"""提示词模板引擎（兼容层）。"""
from app.services.prompt_template_service import list_templates, render_template

__all__ = ["list_templates", "render_template"]
