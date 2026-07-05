"""AI 生图提示词模板服务。"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ImagePromptTemplate
from app.services import prompt_template_crud as crud

BUILTIN_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "cat-window-rain",
        "title": "橘猫窗台 · 雨天",
        "description": "温馨室内与雨景街景",
        "fields": [
            {"label": "主体", "value": "一只橘色的短毛猫，坐在木质窗台上"},
            {"label": "环境", "value": "窗外是下雨的街道"},
            {"label": "光线", "value": "柔和的自然光从侧面照入"},
            {"label": "风格", "value": "水彩插画风格，细腻笔触"},
        ],
        "sort_order": 10,
    },
    {
        "id": "business-data-screen",
        "title": "企业数据大屏",
        "description": "科技感汇报封面",
        "fields": [
            {"label": "主体", "value": "2024 企业财报数据可视化大屏标题区"},
            {"label": "环境", "value": "深色科技背景，隐约可见图表与数据流光"},
            {"label": "光线", "value": "屏幕自发光，蓝紫色霓虹点缀"},
            {"label": "风格", "value": "3D 质感，商务专业，简洁大气"},
        ],
        "sort_order": 20,
    },
    {
        "id": "fork-road-choice",
        "title": "路口分岔",
        "description": "决策类 H5 配图",
        "fields": [
            {"label": "主体", "value": "站在路口中央的人物剪影，面前左右两条分岔路"},
            {"label": "环境", "value": "开阔城市道路，远处城市天际线"},
            {"label": "光线", "value": "黄昏暖色侧光，路面有轻微反光"},
            {"label": "风格", "value": "扁平插画，留白充足，适合叠加标题"},
        ],
        "sort_order": 30,
    },
]


class ImagePromptTemplateError(Exception):
    pass


async def list_for_editor(db: AsyncSession) -> list[dict]:
    return await crud.list_enabled(db, ImagePromptTemplate, ImagePromptTemplateError)


async def admin_list(db: AsyncSession) -> list[dict]:
    return await crud.admin_list_all(db, ImagePromptTemplate, ImagePromptTemplateError)


async def get_template(db: AsyncSession, template_id: str) -> dict | None:
    return await crud.get_by_id(db, ImagePromptTemplate, template_id, ImagePromptTemplateError)


async def create_template(db: AsyncSession, data: dict[str, Any]) -> dict:
    return await crud.create_row(db, ImagePromptTemplate, data, ImagePromptTemplateError)


async def update_template(db: AsyncSession, template_id: str, data: dict[str, Any]) -> dict:
    return await crud.update_row(db, ImagePromptTemplate, template_id, data, ImagePromptTemplateError)


async def delete_template(db: AsyncSession, template_id: str) -> None:
    await crud.delete_row(db, ImagePromptTemplate, template_id, ImagePromptTemplateError)


async def seed_builtin_templates(db: AsyncSession) -> None:
    await crud.seed_builtins(db, ImagePromptTemplate, BUILTIN_TEMPLATES)
