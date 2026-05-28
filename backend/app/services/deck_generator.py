"""项目辅助函数。"""
import uuid


def new_share_slug() -> str:
    return uuid.uuid4().hex[:12]
