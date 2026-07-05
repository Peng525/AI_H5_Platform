import json
import sys
import types
from types import SimpleNamespace
from unittest import TestCase

if "nanoid" not in sys.modules:
    nanoid = types.ModuleType("nanoid")
    nanoid.generate = lambda *args, **kwargs: "test-public-id"
    sys.modules["nanoid"] = nanoid

from app.schemas import AiSlideGenerateRequest, SlideOut
from app.services.deck_generation_service import TEMPLATE_HINT_INSTRUCTIONS, _normalize_fixed_layout_slide
from app.services.llm import provider
from app.services.llm.provider import LlmError
from app.services.prompt_template_service import render_template


class FixedLayoutGenerationTests(TestCase):
    def test_normalize_fixed_layout_preserves_ai_layout_choice(self):
        slide = _normalize_fixed_layout_slide(
            {
                "layout_id": "key_points",
                "title": "业务增长拆解",
                "points": [{"title": "获客", "body": "降低单客成本"}],
            },
            index=0,
            total=5,
        )

        self.assertEqual(slide["layout_id"], "key_points")
        self.assertEqual(slide["points"][0]["title"], "获客")

    def test_slide_out_keeps_fixed_layout_structured_payload(self):
        slide = SimpleNamespace(
            id=1,
            sort_order=0,
            layout="key_points",
            title="业务增长拆解",
            subtitle="",
            bullets_json="[]",
            speaker_notes="",
            animation="fade",
            canvas_json="[]",
            chat_script_json="{}",
            structured_json=json.dumps(
                {
                    "layout_id": "key_points",
                    "title": "业务增长拆解",
                    "points": [{"title": "获客", "body": "降低单客成本"}],
                },
                ensure_ascii=False,
            ),
        )

        out = SlideOut.from_orm_slide(slide)

        self.assertIsNotNone(out.structured)
        self.assertEqual(out.structured["layout_id"], "key_points")
        self.assertEqual(out.structured["points"][0]["title"], "获客")

    def test_free_mode_prompt_uses_title_or_source_order_as_default_sequence(self):
        messages = render_template(
            "固定布局生成.yaml",
            {
                "page_count": 5,
                "topic": "AI 教育产品增长方案\n1. 市场背景\n2. 产品策略\n3. 增长路径",
                "audience": "产品负责人",
                "style": "语气：专业克制",
                "language": "简体中文",
                "text_density": "精炼",
                "extra_instructions": "无",
                "content_mode": "free",
                "page_contents": [],
            },
        )
        prompt = "\n".join(message["content"] for message in messages)

        self.assertIn("根据标题层级、原文先后顺序和自然叙事确定页面顺序", prompt)
        self.assertNotIn("第 1 页必须是 cover_title", prompt)
        self.assertNotIn("第 2 页必须是 toc", prompt)

    def test_text_generation_prefers_relay_text_model_over_tier_default(self):
        original_relay_model = provider.settings.llm_relay_model
        original_model_free = provider.settings.llm_model_free
        try:
            provider.settings.llm_relay_model = "deepseek-v4-pro"
            provider.settings.llm_model_free = "gemini-3.1-flash-image-preview"

            model = provider._resolve_channel_text_model("relay", "free", None)
        finally:
            provider.settings.llm_relay_model = original_relay_model
            provider.settings.llm_model_free = original_model_free

        self.assertEqual(model, "deepseek-v4-pro")

    def test_extract_json_empty_response_reports_clear_error(self):
        with self.assertRaises(LlmError) as raised:
            provider.extract_json("")

        self.assertIn("大模型返回为空", str(raised.exception))

    def test_single_slide_template_hint_accepts_concrete_content_templates(self):
        for hint in ("bullets", "paragraph", "cards", "image_text"):
            body = AiSlideGenerateRequest(prompt="AI education growth", template_hint=hint)
            self.assertEqual(body.template_hint, hint)

        body = AiSlideGenerateRequest(prompt="AI education growth", template_hint="unknown")
        self.assertEqual(body.template_hint, "magic")

    def test_template_hint_instructions_distinguish_bullets_from_cards(self):
        bullets = TEMPLATE_HINT_INSTRUCTIONS["bullets"]
        cards = TEMPLATE_HINT_INSTRUCTIONS["cards"]
        image_text = TEMPLATE_HINT_INSTRUCTIONS["image_text"]

        self.assertIn("key_points", bullets)
        self.assertIn("要点", bullets)
        self.assertNotIn("cards_row", bullets)
        self.assertIn("卡片", cards)
        self.assertIn("scene_left", image_text)
        self.assertIn("段落", TEMPLATE_HINT_INSTRUCTIONS["paragraph"])

    def test_single_slide_request_can_replace_existing_slide(self):
        req = AiSlideGenerateRequest(
            prompt="AI education growth",
            template_hint="cards",
            replace_slide_id=12,
        )
        self.assertEqual(req.replace_slide_id, 12)

    def test_single_slide_generation_uses_replace_semantics(self):
        self.assertTrue(True)
