# 背景音乐（推荐放这里）

`frontend` 构建会清空 `backend/static/`，因此 **请把 MP3 放在本目录**（`backend/media/bgm/`），后端仍通过 `/static/bgm/xxx.mp3` 提供访问。

## 曲目目录

元数据见 [`backend/data/bgm_catalog.json`](../data/bgm_catalog.json)。编辑器「动效 → 背景音乐」会从 `GET /api/v1/bgm/曲目` 拉取列表；**音乐可选可不选**（关闭开关即不播放）。

| 文件名 | 说明 |
|--------|------|
| `happier-sakura-girl.mp3` | 樱花少女（轻快），微信故事模板默认 |
| `demo-loop.mp3` | 演示循环曲（install 脚本会一并生成） |
| `calm-minimal.mp3` | 简约商务（可选，自行放入） |
| `warm-story.mp3` | 温暖叙事（可选，自行放入） |

安装脚本：`develop/scripts/install-bgm.ps1`（会写入本目录与 `static/bgm/` 两份）

## 模板 settings_json 示例

```json
{
  "bgm": {
    "enabled": false,
    "trackId": "",
    "url": "",
    "loop": true,
    "volume": 0.35
  }
}
```

启用时填写 `trackId` + `url`；`enabled: false` 时分享页不播放。
