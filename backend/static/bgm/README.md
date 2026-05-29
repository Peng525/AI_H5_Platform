# 背景音乐

请将 MP3 文件放在本目录（`backend/static/bgm/`）。后端通过 `/static/bgm/文件名.mp3` 提供访问，编辑器「动效 → 背景音乐」从 `GET /api/v1/bgm/曲目` 拉取列表。

## 快速安装测试曲

```powershell
cd "E:\cursor projects\类ppt 小程序\develop"
.\scripts\install-bgm.ps1
```

脚本会生成标准文件名，例如：

- `happier-sakura-girl.mp3`
- `demo-loop.mp3`

也可手动将任意 MP3 复制到本目录，刷新页面后即可在编辑器曲库中看到（文件名即显示名，空格与连字符会转为可读标题）。

> MP3 文件不提交 Git（见 `.gitignore`），每台环境需自行放置。

## 编辑器用法

1. 打开项目 → **工具箱 → 动效**
2. 点击 **「启用背景音乐」** 文本按钮
3. 在曲目列表中点选一首
4. 画布右上角 **旋转唱片** 可静音/继续播放；预览与分享页右上角同样有此控件

## 可选元数据

若需自定义曲目标题与描述，可编辑 `backend/data/bgm_catalog.json`；未收录的 MP3 仍会自动出现在列表中。

## 模板 settings_json 示例

```json
{
  "bgm": {
    "enabled": true,
    "trackId": "happier-sakura-girl",
    "url": "/static/bgm/happier-sakura-girl.mp3",
    "loop": true,
    "volume": 0.35
  }
}
```

`enabled: false` 时预览与分享页不播放音乐。
