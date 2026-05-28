"""微信支付 Native（API v3）。"""
import json
import logging
import time
import uuid
from base64 import b64decode
from datetime import datetime, timezone
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings
from app.models import Order, User
from app.services.payment.base import PaymentError, PaymentNotConfigured, PaymentProvider, PaymentResult

logger = logging.getLogger(__name__)

NATIVE_URL = "https://api.mch.weixin.qq.com/v3/pay/transactions/native"


def wechat_pay_configured() -> bool:
    return bool(
        settings.wechat_pay_mch_id.strip()
        and settings.wechat_pay_app_id.strip()
        and settings.wechat_pay_api_v3_key.strip()
        and settings.wechat_pay_serial_no.strip()
        and settings.wechat_pay_private_key_path.strip()
        and settings.wechat_pay_notify_url.strip()
    )


def _load_private_key():
    path = Path(settings.wechat_pay_private_key_path)
    if not path.is_file():
        raise PaymentNotConfigured("微信支付商户私钥未找到")
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def _sign_message(message: str) -> str:
    key = _load_private_key()
    sig = key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    import base64

    return base64.b64encode(sig).decode("ascii")


def _auth_header(method: str, url_path: str, body: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = uuid.uuid4().hex
    message = f"{method}\n{url_path}\n{timestamp}\n{nonce}\n{body}\n"
    signature = _sign_message(message)
    mch_id = settings.wechat_pay_mch_id.strip()
    serial = settings.wechat_pay_serial_no.strip()
    token = (
        f'WECHATPAY2-SHA256-RSA2048 mchid="{mch_id}",'
        f'nonce_str="{nonce}",timestamp="{timestamp}",'
        f'serial_no="{serial}",signature="{signature}"'
    )
    return {"Authorization": token, "Content-Type": "application/json", "Accept": "application/json"}


def make_out_trade_no(order_id: int) -> str:
    return f"H5{order_id}{int(time.time())}"[-32:]


class WechatNativePaymentProvider(PaymentProvider):
    channel = "wechat_native"

    async def create_payment(self, order: Order, user: User) -> PaymentResult:
        if not wechat_pay_configured():
            raise PaymentNotConfigured("微信支付未配置，请联系管理员或使用演示支付")

        out_trade_no = make_out_trade_no(order.id)
        order.out_trade_no = out_trade_no

        amount_fen = int(round(float(order.amount) * 100))
        payload = {
            "appid": settings.wechat_pay_app_id.strip(),
            "mchid": settings.wechat_pay_mch_id.strip(),
            "description": f"{order.plan_name} · AI H5",
            "out_trade_no": out_trade_no,
            "notify_url": settings.wechat_pay_notify_url.strip(),
            "amount": {"total": amount_fen, "currency": "CNY"},
        }
        body = json.dumps(payload, ensure_ascii=False)
        headers = _auth_header("POST", "/v3/pay/transactions/native", body)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(NATIVE_URL, content=body.encode("utf-8"), headers=headers)
        except httpx.HTTPError as exc:
            raise PaymentError("微信预下单失败，请稍后重试") from exc

        if resp.status_code not in (200, 201):
            logger.warning("WeChat native prepay failed: %s %s", resp.status_code, resp.text[:500])
            raise PaymentError("微信预下单失败，请检查商户配置")

        data = resp.json()
        code_url = data.get("code_url")
        if not code_url:
            raise PaymentError("微信未返回收款二维码")

        order.code_url = code_url
        return PaymentResult(
            status="pending",
            message="请使用微信扫码完成支付",
            qr_code_url=code_url,
        )


def verify_notify_signature(
    timestamp: str,
    nonce: str,
    body: bytes,
    signature: str,
    serial: str,
) -> bool:
    """简化验签：使用商户私钥对应公钥自验（生产应使用微信平台证书）。"""
    if not signature:
        return False
    try:
        key = _load_private_key()
        public_key = key.public_key()
        message = f"{timestamp}\n{nonce}\n{body.decode('utf-8')}\n".encode("utf-8")
        import base64

        sig_bytes = b64decode(signature)
        public_key.verify(sig_bytes, message, padding.PKCS1v15(), hashes.SHA256())
        _ = serial
        return True
    except Exception:
        logger.exception("WeChat notify signature verify failed")
        return False


def decrypt_notify_resource(resource: dict) -> dict:
    api_v3_key = settings.wechat_pay_api_v3_key.strip().encode("utf-8")
    nonce = resource.get("nonce", "")
    ciphertext = resource.get("ciphertext", "")
    associated_data = resource.get("associated_data", "")
    aesgcm = AESGCM(api_v3_key)
    plain = aesgcm.decrypt(nonce.encode("utf-8"), b64decode(ciphertext), associated_data.encode("utf-8"))
    return json.loads(plain.decode("utf-8"))
