"""人机验证抽象层。"""
from abc import ABC, abstractmethod


class CaptchaError(Exception):
    pass


class CaptchaProvider(ABC):
    @abstractmethod
    async def verify_ticket(self, ticket: str, randstr: str, user_ip: str) -> bool:
        raise NotImplementedError
