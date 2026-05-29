# 背景音乐（历史目录）

**曲目列表与编辑器选曲以 [`backend/static/bgm/`](../static/bgm/) 为准。**

若你此前将 MP3 放在本目录，请复制到 `static/bgm/` 后刷新页面，或运行：

```powershell
cd "E:\cursor projects\类ppt 小程序\develop"
.\scripts\install-bgm.ps1
```

本目录仍可作为静态挂载的备用路径，但 `GET /api/v1/bgm/曲目` 仅扫描 `static/bgm/*.mp3`。
