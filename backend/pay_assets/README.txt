# 微信个人收款码（推荐放这里）

请将 `wechat-pay-qr.png` 放在本目录。

## 图片要求（避免扫不出）

1. **只保存二维码本体**，不要带「推荐使用微信支付」绿色边框和底部 logo 的整页截图
2. 在微信 → 我 → 服务 → 收付款 → 二维码收款 → **保存收款码**，或截图后裁切只留中间二维码
3. 建议 PNG 边长 ≥ 430px，文件清晰、无压缩模糊
4. 本目录不会被 `npm run build` 清空；Docker 可挂载：`./backend/pay_assets:/app/backend/pay_assets`

也可放到 `backend/static/wechat-pay-qr.png`，或在 `.env` 设置公网 URL：

```
WECHAT_PERSONAL_QR_URL=https://你的图床/wechat-pay-qr.png
```

## 支付说明

个人收款码是**静态图**，扫码后需用户**手动输入应付金额**；管理员在 `/admin` 核对金额后确认开通。
