"""短信抽象层。"""
from abc import ABC, abstractmethod


class SmsError(Exception):
    pass


class SmsProvider(ABC):
    @abstractmethod
    async def send_code(self, phone: str, code: str) -> None:
        raise NotImplementedError
