# H5 平台对接 — 本地下一步

本目录为 PPT Master（[AtomGit](https://atomgit.com/hugohe3/ppt-master)），与 AI H5 演示平台配合使用。

## 1. Cursor

- **Open Folder** → 本目录（`develop/ppt-master-main`）
- **Settings → Models**：在 H5 的 `develop` 目录运行  
  `python scripts/print_cursor_profile.py`  
  将输出的 Base URL / API Key / Model 同步到 Cursor（勿在聊天中粘贴密钥）

## 2. Smoke test

新开 **Agent**，粘贴 `develop/docs/AI-PPT生成指南.md` §3.4 中的 3 页测试话术。

## 3. 横评（可选）

- 话术副本：`benchmark-prompts/prompt-调研类.md` 等
- 操作手册：`../docs/ppt-master-benchmark/benchmark-runbook.md`
- 切换模型：改 `../docs/ppt-master-benchmark/model-profiles.yaml` 的 `active_profile`

## 4. CLI 自检（可选）

```powershell
python -c "import pptx; import fitz; print('OK')"
python skills/ppt-master/scripts/svg_to_pptx.py --help
```
