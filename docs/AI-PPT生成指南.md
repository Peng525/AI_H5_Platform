# AI PPT 生成指南（最终版）

> **文档版本**：2026-05 · **状态**：当前有效（Last）  
> **适用对象**：在本机用 Cursor + PPT Master 生成可编辑 `.pptx`，并可选导入本 H5 平台  
> **说明**：本文档为 **唯一入口**；方案详表与横评细则见文末「文档索引」，旧内容已合并于此，无需在多篇文档间跳转找步骤。

---

## 1. 我们要做什么

| 目标 | 做法 |
|------|------|
| 生成 **可编辑 PowerPoint**（非截图） | [PPT Master](https://atomgit.com/hugohe3/ppt-master) + Cursor Agent |
| **对比不同大模型** 谁更适合做 PPT | [`ppt-master-benchmark/`](./ppt-master-benchmark/) 五模型横评 |
| 发布为 **移动端 H5 演示** | H5 管理端 `/admin/templates` → **从 PPT 导入** |

**不在本指南范围**：H5 平台内「一键 AI 生成文稿」（后端 `chat_completion` 尚未接用户端）；若将来要做，与本文 Cursor 工作流 **并行不冲突**。

---

## 2. 推荐技术栈（定稿）

### 2.1 主工作流

```
Cursor（Agent 宿主）
    + PPT Master Skill（SVG → 原生 .pptx）
    + 大模型（文案 / 版式 / Executor）
    + 配图（Phase 1 Web 搜图 → Phase 2 gpt-image-2）
         ↓
exports/*.pptx
         ↓（可选）
H5 平台「从 PPT 导入」→ 模板库 → 用户端演示
```

### 2.2 模型分工（两阶段）

| 阶段 | 目的 | 模型 | 配图 |
|------|------|------|------|
| **Phase 1 横评** | 选性价比最高的推理模型 | 5 模型轮换（见 §4） | **仅 Web/Pexels**，禁止 AI 生图 |
| **Phase 2 视觉** | 在胜出模型上加视觉层 | Phase 1 Top 1–2 | **gpt-image-2**（medium，16:9） |

### 2.3 视觉层策略（gpt-image-2 + DeepSeek）

- **DeepSeek / 任意模型**：负责 Strategist、Executor、**SVG 文字与简单版式**
- **gpt-image-2**：负责 **背景 / 主视觉 / 插画**（位图嵌入，损耗小）
- **不要**把整页文字画进 gpt-image-2 大图（不可编辑）
- **推荐结构**：gpt-image-2 出底图 + 模型在 SVG 上排标题与要点

官方满血参考：**Opus + gpt-image-2**；成本栈：**DeepSeek V4 Pro + Pexels/Web 图**。

---

## 3. 环境准备（一次性）

### 3.1 安装 PPT Master

1. Python 3.10+（安装时勾选 **Add to PATH**）
2. 克隆到 **独立目录**（勿与 H5 项目混根目录）：  
   `git clone https://atomgit.com/hugohe3/ppt-master.git`
   或从 [AtomGit](https://atomgit.com/hugohe3/ppt-master) 下载 ZIP 解压到 `develop/ppt-master-main`
3. `python -m pip install -r requirements.txt`
4. Cursor **Open Folder** → 打开 `develop/ppt-master-main` 根目录
5. `npx skills add hugohe3/ppt-master`

详见：[PPT Master Windows 安装](https://atomgit.com/hugohe3/ppt-master/blob/main/docs/zh/windows-installation.md)

一键安装（已有 `ppt-master-main` 时）：`.\develop\scripts\setup_ppt_master.ps1`

### 3.2 配置 `develop/.env`

**中转模型**（Gemini / Claude / GPT 横评共用）——与 H5 平台已有配置相同：

```env
LLM_RELAY_BASE_URL=https://你的中转地址/v1
LLM_RELAY_API_KEY=你的推理令牌
```

**DeepSeek 官方直连**（仅 Cursor / ppt-master，与 `LLM_RELAY_*` 分离）：

```env
base_url=https://api.deepseek.com/v1
api_key=sk-你的DeepSeek密钥
model=deepseek-v4-pro
```

**Phase 2 配图**（可选，与 H5 生图一致）：

```env
LLM_IMAGE_MODEL_FREE=gpt-image-2
LLM_IMAGE_MODEL_PRO=gpt-image-2
```

完整说明：[`ppt-master-benchmark/benchmark.env.example`](./ppt-master-benchmark/benchmark.env.example)

### 3.3 DeepSeek Agent 稳定性

V4 Pro 在 Cursor **多轮工具调用** 可能报 `reasoning_content` 400。处理：本地 [deepseek-cursor-proxy](https://github.com/yxlao/deepseek-cursor-proxy)，Cursor Base URL 改为 `http://127.0.0.1:9000/v1`。

### 3.4 Smoke test（首次，在 Cursor Agent 中执行）

1. **Open Folder** → `develop/ppt-master-main`（非 H5 的 `develop` 根）
2. **Settings → Models**：运行 `python develop/scripts/print_cursor_profile.py`，将 Base URL / API Key / Model 填入当前 `active_profile`
3. **Verify** 通过后，**新开 Agent**，粘贴：

```
请按 PPT Master 工作流（Read skills/ppt-master/SKILL.md）生成 3 页 16:9 测试 deck。
主题：PPT Master 环境验收
风格：简约商务、浅色背景
Executor：General
配图：仅 Web 搜图（Phase 1，禁止 AI 生图）
导出到 exports/，完成后告知 .pptx 路径。
```

横评 8 页话术：`develop/docs/ppt-master-benchmark/prompt-调研类.md` 等（在 `ppt-master-main` 中打开 Cursor 时路径为 `../docs/ppt-master-benchmark/`）。

---

## 4. 多模型横评（当前最后一版）

### 4.1 切换模型的唯一变量

编辑 [`ppt-master-benchmark/model-profiles.yaml`](./ppt-master-benchmark/model-profiles.yaml)：

```yaml
active_profile: deepseek-v4-pro   # 改成下表五选一
benchmark_phase: 1                # 1=只比模型  2=+ gpt-image-2
```

再按 [`benchmark-runbook.md`](./ppt-master-benchmark/benchmark-runbook.md) 同步 **Cursor Settings → Models**（Base URL / API Key / Model 名），**新开 Agent 会话**。

### 4.2 五个横评模型

| active_profile | Cursor Model | Base URL / Key |
|----------------|--------------|----------------|
| `gemini-3-pro` | `gemini-3.1-pro-preview` | `LLM_RELAY_*` |
| `claude-opus-4-8` | `claude-opus-4-8` | `LLM_RELAY_*` |
| `claude-opus-4-7` | `claude-opus-4-7` | `LLM_RELAY_*` |
| `gpt-5-5` | `gpt-5.5` | `LLM_RELAY_*` |
| `deepseek-v4-pro` | `model` | `base_url` / `api_key` |

Verify 失败时只改 yaml 内 `model_id`（如 `gpt-5.5-chat`），**不改** profile 键名。

### 4.3 Phase 1 执行顺序

1. `deepseek-v4-pro`
2. `gemini-3-pro`
3. `gpt-5-5`
4. `claude-opus-4-7`
5. `claude-opus-4-8`

每个 profile：**调研 → 报告 → 学术** 各跑一遍（各 **8 页**，独立 Agent 会话）。

| 类型 | 复制来源 |
|------|----------|
| 调研类 | [`prompt-调研类.md`](./ppt-master-benchmark/prompt-调研类.md) |
| 报告类 | [`prompt-报告类.md`](./ppt-master-benchmark/prompt-报告类.md) |
| 学术类 | [`prompt-学术类.md`](./ppt-master-benchmark/prompt-学术类.md) |

评分：[`evaluation-rubric.md`](./ppt-master-benchmark/evaluation-rubric.md)  
记录：[`results-template.md`](./ppt-master-benchmark/results-template.md) → 存 [`results/`](./ppt-master-benchmark/results/)

### 4.4 Phase 2

对 Phase 1 **总分/性价比前 2 名**：

- `benchmark_phase: 2`
- ppt-master `.env`：`IMAGE_BACKEND=openai` + gpt-image-2
- 建议至少重跑 **报告类**；可选三类全跑

---

## 5. 日常生成（非横评）

横评结束后，固定 `active_profile` 为胜出模型，Agent 话术示例：

```
请按 PPT Master 工作流生成 12 页 16:9 演示文稿。
主题：（你的主题）
Executor：Consultant_Top（报告）/ Consultant（调研）/ General（学术）
配图：（Web 搜图 或 gpt-image-2）
导出到 exports/。
```

项目目录建议：`projects/你的项目名-{日期}/`

---

## 6. 导入 H5 平台

1. 打开 `http://localhost:8080/admin/templates`（或你的部署地址）
2. **从 PPT 导入** 或 编辑已有模板 → **从 PPT 导入**
3. 上传 `exports/` 中的 `.pptx`
4. **编辑** → 可视化编辑器（与用户端相同）→ **保存为预设**

后端：`pptx_template_parser.py` → `h5_template_service`（已实现，无需改代码）。

---

## 7. 方案选型速查（摘要）

完整对比见 [`AI-PPT生成方案对比.md`](./AI-PPT生成方案对比.md)（**附录，非入口**）。

| 你的需求 | 首选 |
|----------|------|
| 本指南默认路径（可编辑 pptx + 横评） | **Cursor + PPT Master + 五模型横评** |
| 对外终稿、版式最稳 | PPT Master + **Opus** + gpt-image-2 |
| 预算紧、内部草稿 | PPT Master + **DeepSeek V4 Pro** + Web 图 |
| 设计感/杂志风/动效视频 | Open Design + Opus + HyperFrames（MP4） |
| 真 Excel 图表、审计 QA | Codex + ppt-polished-deck |
| 最快出稿、少折腾 | Gamma / Pi（SaaS） |

**12 页 deck 粗算**：DeepSeek 约 $0.5–3；Opus 约 $5–15；PPT Master 生成约 **10–20 分钟**（逐页串行）。

---

## 8. 文档索引与版本关系

| 文档 | 角色 | 何时阅读 |
|------|------|----------|
| **本文 `AI-PPT生成指南.md`** | **最终版入口（Last）** | 始终从这里开始 |
| [`ppt-master-benchmark/`](./ppt-master-benchmark/) | 横评实操包（yaml、话术、评分） | Phase 1/2 横评时 |
| [`AI-PPT生成方案对比.md`](./AI-PPT生成方案对比.md) | 多方案详表、成本、SaaS 对照 | 选型论证、对外说明 |
| [`develop/.env.example`](../.env.example) | H5 + DeepSeek 环境变量模板 | 首次配置 |
| [`develop/README.md`](../README.md) | H5 平台功能与 admin 模板说明 | 导入与产品上下文 |

**已合并、勿重复维护的内容**：Cursor+DeepSeek 落地步骤、五模型映射、三类 8 页话术规范、两阶段评测流程——均以 **本文 + ppt-master-benchmark/** 为准。

---

## 9. 检查清单

### 首次搭建

- [ ] ppt-master 安装 + Skill
- [ ] `develop/.env`：`LLM_RELAY_*` + `base_url` / `api_key` / `model`
- [ ] Cursor Verify 当前 profile 成功
- [ ] 3 页 Hello World 测试 deck 可打开

### 完成 Phase 1 横评

- [ ] 5 profile × 3 类 = 15 次 run 均有记录
- [ ] [`results/`](./ppt-master-benchmark/results/) 汇总表填满
- [ ] 确定 Top 1–2 进入 Phase 2

### 定稿上线

- [ ] Phase 2（可选）视觉验收
- [ ] 满意 `.pptx` 导入 H5 管理端
- [ ] 模板「已上架」或按需编辑

---

## 10. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05 | **最终版**：合并方案对比、DeepSeek 落地、五模型横评、三类模板、H5 导入为单一入口 |
