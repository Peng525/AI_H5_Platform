# Stitch 原型与实现对照

原型项目：https://stitch.withgoogle.com/projects/11380331898068582338

| Stitch 页面 | 路由 | 状态 |
|-------------|------|------|
| 登录/注册 + 拼图验证 | `/login` | ✅ 滑块拼图 |
| 探索模板 + 工具箱 + AI 面板 | `/templates` | ✅ |
| 我的项目工作台 | `/dashboard` | ✅ |
| 三栏编辑器 + 可视化拖拽 | `/editor/:id` | ✅ localStorage 持久化 |
| AI 面板（通道/配额/立即生成） | 编辑器右侧 `AiPanel` | ✅ |
| AI 创建向导（分步） | `/create` | ✅ |
| 套餐升级 + 扫码支付 | `/upgrade` | ⚠️ 演示/mock（可模拟开通 Pro） |
| 发布成功 + 链接/二维码 | `/publish/:id` | ✅ 真实 QR |
| H5 全屏预览（手机框切换） | `/preview/:id` | ✅ |
| 分享页 | `/s/:slug` | ✅ |
| 系统设置 | `/settings` | ✅ |
| 全局导航 + 登出 | `AppShell` | ✅ |

## 设计规范

- 主色 `#005daa`、背景 `#fcf9f8`（见 `_proto_web/.../DESIGN.md`）
- 字体 Inter + Material Symbols
- 免费档：Gemini 3.1 Flash；升级档：Gemini 3 Pro

## 待后端对接（二期）

- 微信/支付宝支付回调（PAY-02）
- 微信登录（ACC-01）
- 画布元素云端持久化（当前仅存浏览器 localStorage）
- JWT 用户项目隔离
