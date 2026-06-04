# PPT Master 多模型横评套件

> **上级文档**：[AI-PPT生成指南.md](../AI-PPT生成指南.md)（最终版入口）  
> 本目录为横评 **实操包**：切换模型、三类 8 页话术、评分与记录。

在 Cursor + PPT Master 工作流下，对比 **5 个模型** 在调研 / 报告 / 学术三类 8 页 deck 上的输出差异。

## 快速开始

**PPT Master 安装路径（本仓库）**：`develop/ppt-master-main`（[AtomGit](https://atomgit.com/hugohe3/ppt-master) ZIP 或 `git clone https://atomgit.com/hugohe3/ppt-master.git`）

1. 阅读 [../AI-PPT生成指南.md](../AI-PPT生成指南.md) §3–§4
2. 配置 [`../../.env`](../../.env)（见 [`benchmark.env.example`](./benchmark.env.example)）
3. 改 [`model-profiles.yaml`](./model-profiles.yaml) 的 `active_profile`
4. 按 [`benchmark-runbook.md`](./benchmark-runbook.md) 同步 Cursor Settings
5. 新开 Agent，复制 [`prompt-调研类.md`](./prompt-调研类.md) / [`prompt-报告类.md`](./prompt-报告类.md) / [`prompt-学术类.md`](./prompt-学术类.md)

## 横评模型

| active_profile | 凭证 |
|----------------|------|
| `gemini-3-pro` | `LLM_RELAY_*` |
| `claude-opus-4-8` | `LLM_RELAY_*` |
| `claude-opus-4-7` | `LLM_RELAY_*` |
| `gpt-5-5` | `LLM_RELAY_*` |
| `deepseek-v4-pro` | `base_url` / `api_key` / `model` |

## 两阶段

- **Phase 1**：Web 搜图，5 模型 × 3 类
- **Phase 2**：Top 1–2 模型 + gpt-image-2

## 文件索引

| 文件 | 说明 |
|------|------|
| [`model-profiles.yaml`](./model-profiles.yaml) | 切换模型 |
| [`benchmark-runbook.md`](./benchmark-runbook.md) | 操作手册 |
| [`evaluation-rubric.md`](./evaluation-rubric.md) | 评分标准 |
| [`results-template.md`](./results-template.md) | 单次记录表 |
| [`results/`](./results/) | 实测结果目录 |

方案详表见 [AI-PPT生成方案对比.md](../AI-PPT生成方案对比.md)。
