# 微信个人收款码（推荐放这里）

请将 `wechat-pay-qr.png` 放在本目录。

- 此目录不会被 `npm run build` 清空
- Docker 可通过 compose 挂载：`./backend/pay_assets:/app/backend/pay_assets`

也可放到 `backend/static/wechat-pay-qr.png`，或在 `.env` 设置公网 URL：

```
WECHAT_PERSONAL_QR_URL=https://你的图床/wechat-pay-qr.png
```
