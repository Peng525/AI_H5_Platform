"""项目辅助函数。"""
from nanoid import generate


def new_public_id() -> str:
    return generate(size=21)


def new_share_slug() -> str:
    return new_public_id()
