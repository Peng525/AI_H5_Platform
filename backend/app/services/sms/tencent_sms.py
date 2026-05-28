"""腾讯云短信发送。"""
import json
import logging

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

from app.config import settings
from app.services.sms.base import SmsError, SmsProvider

logger = logging.getLogger(__name__)


class TencentSmsProvider(SmsProvider):
    async def send_code(self, phone: str, code: str) -> None:
        sid = settings.tencent_secret_id.strip()
        skey = settings.tencent_secret_key.strip()
        app_id = settings.tencent_sms_sdk_app_id.strip()
        sign = settings.tencent_sms_sign_name.strip()
        template_id = settings.tencent_sms_template_id.strip()
        if not all([sid, skey, app_id, sign, template_id]):
            raise SmsError("短信服务未配置")

        try:
            cred = credential.Credential(sid, skey)
            http_profile = HttpProfile()
            http_profile.reqMethod = "POST"
            http_profile.endpoint = "sms.tencentcloudapi.com"
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            client = sms_client.SmsClient(cred, settings.tencent_sms_region, client_profile)

            req = models.SendSmsRequest()
            req.SmsSdkAppId = app_id
            req.SignName = sign
            req.TemplateId = template_id
            req.TemplateParamSet = [code, str(settings.sms_code_ttl_minutes)]
            req.PhoneNumberSet = [f"+86{phone}"]

            resp = client.SendSms(req)
            status = resp.SendStatusSet[0] if resp.SendStatusSet else None
            if not status or status.Code != "Ok":
                code_msg = status.Message if status else "未知错误"
                logger.warning("Tencent SMS failed: %s", code_msg)
                raise SmsError("短信发送失败，请稍后重试")
        except TencentCloudSDKException as exc:
            logger.warning("Tencent SMS SDK error: %s", exc)
            raise SmsError("短信发送失败，请稍后重试") from exc
