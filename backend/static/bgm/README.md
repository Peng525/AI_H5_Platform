# 背景音乐

## 第一版测试曲（Happier – Sakura Girl）

可直接把 MP3 放进本目录（任意文件名），然后运行：

```powershell
cd "E:\cursor projects\类ppt 小程序\develop"
.\scripts\install-bgm.ps1
```

脚本会生成模板使用的标准文件名：

- `happier-sakura-girl.mp3`
- `demo-loop.mp3`（兼容旧 URL）

也可手动复制并重命名为 `happier-sakura-girl.mp3`。

> MP3 文件不提交 Git（见 `.gitignore`），每台开发机需本地安装一次。
