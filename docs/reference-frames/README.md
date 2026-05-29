# 参考帧说明（对齐 MP4 模板）

开发环境无法直接解码 `模板/模板.mp4`、`模板2.mp4`、`演示.mp4`。验收时请本地截帧放入本目录，用于对照配色与间距。

## 建议截帧

| 来源视频 | 建议帧数 | 关注点 |
|----------|----------|--------|
| `模板.mp4` | 3～5 | 封面排版、对话页气泡色、页间过渡 |
| `模板2.mp4` | 3～5 | 进阶版配色、对话密度 |
| `演示.mp4` | 3～5 | 预览/分享整体体验、BGM 提示、逐句点击 |
| 易企秀 5P8N3mJ7 | 3～5 | 叙事纵向滑动、暖色排版（见 `eqxiu-volunteer-story.md`） |

## 文件命名

```
reference-frames/
  template-a-cover.png
  template-a-chat.png
  template-b-cover.png
  demo-preview-full.png
  eqxiu-volunteer-cover.png
  eqxiu-volunteer-hook.png
```

规范文档：

- [zjy-style-guide.md](./zjy-style-guide.md)
- [eqxiu-volunteer-story.md](./eqxiu-volunteer-story.md)

重新生成模板 JSON：`node scripts/generate-h5-templates.mjs`

## 当前实现对照

- 微信对话：左右气泡（左白 / 右 `#95EC69`）、圆角头像、点击逐句
- 滚动：旗舰模板默认 **纵向滚动**（`scrollEffect: vertical`）
- BGM：`/static/bgm/happier-sakura-girl.mp3`（文件放 `backend/static/bgm/`，见 README 与 `scripts/install-bgm.ps1`）

录屏验收：编辑器预览与 `/s/:slug` 分享页应与 `演示.mp4` 体验一致。
