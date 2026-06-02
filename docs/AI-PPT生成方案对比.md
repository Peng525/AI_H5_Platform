# AI PPT 生成方案对比

> **文档版本**：2026-05  
> **文档角色**：详细附录（方案详表、成本、SaaS 对照）  
> **入口文档**：请先阅读 **[AI-PPT生成指南.md](./AI-PPT生成指南.md)**（最终版 Last，含落地步骤与横评索引）  
> 适用场景：设计感/现代感演示、报告类、图表对比类、邀请/活动类  
> 关联平台：本 H5 演示平台可通过管理端「从 PPT 导入」接入任意方案产出的 `.pptx`

---

## 1. 文档目的

本文对比当前主流的 **Agent 驱动** 与 **SaaS 驱动** AI 演示文稿生成方案，从以下维度帮助选型：

- **方案架构**与输出物形态
- **生成效果**（设计感、报告、图表、邀请四类需求）
- **生成成本**（单次与月费）
- **生成时间**
- **应用场景**与上手难度
- **与本 H5 平台的衔接方式**

---

## 2. 方案名称澄清

| 常见说法 | 实际组成 | 主要输出 |
|----------|----------|----------|
| **PPT Master + DeepSeek** | [hugohe3/ppt-master](https://atomgit.com/hugohe3/ppt-master) Skill + Cursor/Claude Code Agent + DeepSeek V4 Pro API | 原生可编辑 `.pptx` |
| **PPT Master + Opus + gpt-image-2** | 同上工作流 + Claude Opus + OpenAI 生图 | 原生可编辑 `.pptx`（官方推荐满血组合） |
| **Codex + gpt-image-2** | OpenAI Codex CLI + slides / ppt-polished skill + gpt-image-2 | 原生 `.pptx` + 可选 PNG 渲染 QA |
| **HyperFrames + Opus** | 通常指 [Open Design](https://github.com/nexu-io/open-design) 生态：Opus Agent + [HyperFrames](https://github.com/heygen-com/hyperframes)（HTML→MP4）+ guizang-ppt + gpt-image-2 | HTML 杂志风 deck、PDF、`.mp4` 动效；PPTX 需 Agent 导出 |

> **重要**：HyperFrames 是 **动效视频渲染框架**（HeyGen 开源），擅长动态图表、产品 reveal、kinetic typography，**不是**静态 `.pptx` 生成器。静态 PPT 在 Open Design 中由 guizang-ppt / html-ppt 等 Skill 负责。

---

## 3. 需求维度说明

| 需求类型 | 典型场景 | 关键能力 |
|----------|----------|----------|
| **设计感 / 现代感** | 融资路演、品牌发布、产品 Story | 强视觉方向、杂志排版、定制插画 |
| **报告类** | 年报、复盘、咨询交付 | 章节结构、MBB/商务风、长文可读性 |
| **图表对比类** | 竞品分析、数据叙事、趋势对比 | 真图表或可编辑形状图表、数据准确 |
| **邀请类** | 活动邀请、海报、朋友圈/Story | 多画布比例（1:1、9:16、3:4 等） |

---

## 4. 总览对比表（12 页商务 deck 量级）

| 维度 | PPT Master + Opus + gpt-image-2 | PPT Master + DeepSeek V4 Pro | Open Design + Opus + HyperFrames + gpt-image-2 | Codex CLI + gpt-image-2 | SaaS：Gamma / Beautiful.ai / Pi |
|------|----------------------------------|------------------------------|------------------------------------------------|-------------------------|----------------------------------|
| **方案本质** | 开源 Skill + Agent；SVG→原生形状 .pptx | 同上，换 DeepSeek 模型 | 开源设计工作台 + 多 Skill；HTML/PDF/PPTX/MP4 | OpenAI Agent + PptxGenJS / python-pptx + 渲染 QA | 闭源网页生成器 |
| **输出物** | 原生可编辑 `.pptx`（DrawingML） | 同上 | HTML 杂志风 deck + PDF；HyperFrames 产出 `.mp4`；PPTX 需 Agent 导出 | 原生 `.pptx` + 可选 PNG QA 闭环 | `.pptx` / 在线链接（导出质量参差） |
| **设计感 / 现代感** | ⭐⭐⭐⭐（官方天花板组合） | ⭐⭐⭐（布局精度依赖模型，易溢出/错位） | ⭐⭐⭐⭐⭐（5 套视觉方向 + guizang 杂志风 + 150 设计系统） | ⭐⭐⭐（偏 executive / 结构化） | Gamma ⭐⭐⭐⭐；Pi ⭐⭐⭐⭐；Beautiful.ai ⭐⭐⭐ |
| **报告类** | ⭐⭐⭐⭐⭐（Executor_Consultant_Top，MBB 风） | ⭐⭐⭐⭐（内容 OK，版式需改稿） | ⭐⭐⭐⭐（finance-report skill；偏叙事网页） | ⭐⭐⭐⭐⭐（ppt-polished-deck + Office 图表） | Beautiful.ai ⭐⭐⭐⭐；Gamma ⭐⭐⭐ |
| **图表 / 对比类** | ⭐⭐⭐⭐（SVG 定制图表→形状，非 Excel 绑定） | ⭐⭐⭐ | ⭐⭐⭐⭐（HyperFrames 动态图表→**视频**） | ⭐⭐⭐⭐⭐（原生 Office Chart + Python 图） | ⭐⭐⭐（导出后常需修） |
| **邀请 / 活动 / 社媒** | ⭐⭐⭐⭐⭐（10+ 画布：1:1、9:16、3:4 小红书等） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐（magazine-poster、social-carousel、HyperFrames 短片） | ⭐⭐⭐（需自定义尺寸 preset） | Canva/Gamma ⭐⭐⭐⭐ 快 |
| **生成时间** | **10–20 分钟**（10–15 页，逐页串行） | 15–30 分钟（含重试 / proxy） | **20–45 分钟**（discovery + 多轮 critique） | **15–35 分钟**（含 render QA） | **30 秒–3 分钟** 首稿；导出清理 +10 分钟 |
| **单次成本（估）** | **$5–15** | **$0.5–3** | **$5–20** | **$8–25** | 订阅 $0–12/月；按量约 $1–5/deck |
| **固定月费** | 无（BYOK） | 无（BYOK）+ Cursor 可选 | 无（BYOK） | ChatGPT Pro/Codex ~$20+ | Gamma $8+；Beautiful.ai $12+；Pi ~$7.5 |
| **编辑性** | 形状级可编辑（Office 2016+） | 同上 | HTML 最好；PPTX 依赖导出 skill | 高（python-pptx / PptxGenJS） | Gamma 导出常 flatten |
| **上手难度** | 中 | 中高（+ DeepSeek proxy） | 高 | 中高 | 低 |
| **与 H5 平台衔接** | ✅ 管理端「从 PPT 导入」 | ✅ 同上 | ⚠️ 需先稳定导出 `.pptx` | ✅ 可导入 | ⚠️ 导出后导入 |

---

## 5. 分场景推荐

| 需求 | 首选 | 次选 | 不推荐 |
|------|------|------|--------|
| **设计感 + 现代感**（路演、品牌、融资） | Open Design + Opus + gpt-image-2 | PPT Master + Opus + gpt-image-2 | 纯 DeepSeek（布局风险高） |
| **报告类**（年报、复盘、咨询） | PPT Master + Opus（Consultant_Top） | Codex + ppt-polished-deck-collab | Gamma 直接导出交 Board |
| **图表对比类**（数据叙事、竞品对比） | Codex + ppt-polished（Office 真图表） | PPT Master SVG 图表；动效用 HyperFrames MP4 嵌入 | 仅 Web 卡片式 SaaS |
| **邀请类**（活动、海报、1:1/9:16） | PPT Master 多画布 或 OD social-carousel | Gamma 快速版 | 长报告型 Beautiful.ai |
| **预算极敏感 + 可接受改稿** | **PPT Master + DeepSeek V4 Pro** + Pexels 免费图 | DeepSeek Flash | Opus 全栈 |
| **要最快出稿、少折腾** | Pi / Gamma（SaaS） | — | 本地 Agent 全套 |

### 质量 vs 成本定位（12 页 deck，示意）

```
高质量 ↑
        │     Open Design + Opus + HyperFrames
        │              Codex + gpt-image-2
        │         PPT Master + Opus + image-2
        │    PPT Master + DeepSeek（性价比）
        │  Gamma / Pi（快但模板感）
低成本 ─┴────────────────────────────→ 高成本
```

---

## 6. Agent 方案详解

### 6.1 PPT Master + Claude Opus + gpt-image-2（官方「满血」）

| 项 | 说明 |
|----|------|
| **仓库** | https://atomgit.com/hugohe3/ppt-master |
| **效果** | 官方自述天花板；示例多为 Opus + gpt-image-2；原生形状、页过渡、定制 SVG 图表 |
| **时间** | 10–15 页约 **10–20 min**；≥18 页可能 split 两阶段 |
| **成本** | 工具免费；12 页约 **$5–15**（Opus token + ~12 张 medium 图 ~$0.6） |
| **Executor** | General / Consultant / **Consultant_Top**（MBB 级） |
| **弱项** | 图表非 Excel 数据绑定；复杂表格需人工微调 |

**Opus 定价参考（2026-05）**：输入约 $5/M tokens，输出约 $25/M tokens。

**gpt-image-2 定价参考**：1024×1024 medium 约 **$0.053/张**（OpenAI 官方计算器估算）。

---

### 6.2 PPT Master + DeepSeek V4 Pro（成本栈）

| 项 | 说明 |
|----|------|
| **效果** | 与 6.1 同一工作流；**版式上限由 V4 Pro 决定**（SVG 绝对坐标不如 Opus，易溢出/错位） |
| **时间** | **15–30 min**（Cursor Agent 可能需 deepseek-cursor-proxy；重试增加时间） |
| **成本** | 12 页约 **$0.5–3**（V4 Pro：cache-miss 输入 $0.435/M，输出 $0.87/M；思考 token 可能 2–3×） |
| **配图** | Web 搜图零成本；或 Pexels/Pixabay 免费 API |
| **适合** | 内部草稿、内容优先、可在 PowerPoint 微调 |
| **不适合** | 零容忍错位的对外融资终稿 |

**DeepSeek 配置示例（Cursor）**：

```env
# Cursor Settings → Models
Override OpenAI Base URL: https://api.deepseek.com/v1
Model: deepseek-v4-pro
API Key: sk-...
```

**Agent 稳定性**：V4 Pro 为思考模型，Cursor 多轮工具调用可能报 `reasoning_content must be passed back`。建议本地运行 [deepseek-cursor-proxy](https://github.com/yxlao/deepseek-cursor-proxy)，Base URL 改为 `http://127.0.0.1:9000/v1`。

---

### 6.3 Open Design + HyperFrames + Opus（视觉栈）

| 项 | 说明 |
|----|------|
| **仓库** | https://github.com/nexu-io/open-design |
| **HyperFrames** | https://github.com/heygen-com/hyperframes — HTML+GSAP→MP4 |
| **Deck Skill** | guizang-ppt（杂志风）、html-ppt（36 主题）、simple-deck 等 |
| **效果** | 最接近 Claude Design 开源替代；五维自评；**HyperFrames 擅动态图表视频** |
| **时间** | discovery 表单 ~2 min + 生成 **20–45 min** |
| **成本** | Open Design **Apache 免费**；Opus + gpt-image-2 约 **$5–20/deck** |
| **适合** | 强设计感、现代杂志风、需要配套 **15s MP4** 片段的演示 |
| **弱项** | PPTX 导出链路长于 PPT Master；HyperFrames 单独 **不出 .pptx** |

---

### 6.4 Codex CLI + gpt-image-2（图表 / 报告栈）

| 项 | 说明 |
|----|------|
| **Skill 示例** | [OpenAI slides skill](https://www.piax.org/skills/openai-skills/slides)、[ppt-polished-deck-collab](https://github.com/Sven-LI-sankyuu/presentation-skills) |
| **流程** | brief → deck_narrative → slide_specs → python-pptx / PptxGenJS → LibreOffice 渲染 PNG QA |
| **效果** | **原生 Office 图表**、connector 图、结构 preflight + render review |
| **时间** | **15–35 min**（含 QA 迭代） |
| **成本** | GPT-5.x/Codex API 或 ~$20/mo 订阅 + 图；12 页 **$8–25** 量级 |
| **适合** | 报告 + 真图表 + 可审计 QA 的企业交付 |
| **弱项** | 视觉 wow 通常弱于 Open Design / Opus+PPT Master |

---

## 7. SaaS 方案对照

| 工具 | 生成时间 | 月费（参考） | 效果特点 | 四类需求匹配 |
|------|----------|--------------|----------|--------------|
| **Pi** | 10–15 s 全 deck | ~$7.5/月（年付） | AI-native，声称零编辑可汇报 | 现代感强；图表/报告中等 |
| **Gamma** | <60 s | $8–12/月 | 卡片式 Web 美学 | 现代感好；PPTX 导出需 ~10 min 清理 |
| **Beautiful.ai** | ~90 s | $12–45/月 | Smart Slides 品牌一致 | 报告/商务强；设计感模板化 |
| **Microsoft Copilot** | 2–3 min | M365 捆绑 | 原生 PowerPoint | 企业合规；设计感一般 |

**第三方测速参考（2026-05）**：同一 QBR prompt 下，Pi 约 72 秒完成可汇报 `.pptx`；Gamma/Beautiful.ai 等常需 4–12 分钟导出后清理（来源：AI Journal 六工具横评）。

---

## 8. 成本估算明细（12 页 deck）

### 8.1 模型 Token（粗算）

假设单次生成累计：**输入 ~300K tokens，输出 ~80K tokens**（含 Strategist、逐页 Executor、改稿）。

| 模型 | 输入成本 | 输出成本 | 合计（估） |
|------|----------|----------|------------|
| Claude Opus 4.8 | 300K × $5/M ≈ $1.5 | 80K × $25/M ≈ $2.0 | **$3.5–8**（含重试更高） |
| DeepSeek V4 Pro | 300K × $0.435/M ≈ $0.13 | 80K × $0.87/M ≈ $0.07 | **$0.2–1**（思考模式 2–3×） |
| DeepSeek V4 Flash | 更便宜 | 更便宜 | **<$0.5** |

### 8.2 配图（12 页，每页 1 张 medium）

| 来源 | 单价 | 12 页合计 |
|------|------|-----------|
| gpt-image-2 medium | ~$0.053 | ~**$0.64** |
| Pexels / Pixabay / Web 搜图 | $0 | **$0** |

### 8.3 单次总成本区间

| 方案 | 低 | 高 |
|------|----|----|
| PPT Master + Opus + gpt-image-2 | $5 | $15 |
| PPT Master + DeepSeek V4 Pro + 免费图 | $0.5 | $3 |
| Open Design + Opus + gpt-image-2 | $5 | $20 |
| Codex + gpt-image-2 | $8 | $25 |
| Gamma / Pi 订阅摊销 | $1 | $5 |

> PPT Master FAQ 称：配合 VS Code Copilot 等廉价模型可低至 **~$0.08/deck**，但 SVG 布局质量显著下降。

---

## 9. 生成时间说明

| 方案 | 10–15 页典型耗时 | 瓶颈 |
|------|------------------|------|
| PPT Master 系 | **10–20 min** | 模型输出速度；**故意逐页串行**保风格一致 |
| Open Design | **20–45 min** | discovery 表单 + 多轮 critique |
| Codex + QA | **15–35 min** | render-review 迭代 |
| Gamma / Pi | **30 s–3 min** | 首稿快；专业交付常 +10 min 导出清理 |

PPT Master 在 ≥18 页或素材极厚时可能建议 **split mode**：Phase A 结束后再开新 Chat 输入 `继续生成 projects/xxx` 继续 Phase B。

---

## 10. 与本 H5 演示平台的衔接

本仓库 `develop/` 已实现 **管理端 PPT 导入**，无需改后端即可串联 Agent 工作流：

```
Cursor / Codex / Open Design
        ↓ 生成 .pptx
exports/ 或本机路径
        ↓
H5 平台 /admin/templates →「从 PPT 导入」
        ↓
可视化编辑器（EditorStudio）→「保存为预设」
        ↓
用户端模板库 / 移动端 H5 演示
```

| 步骤 | 路径 |
|------|------|
| 管理端导入 | `/admin/templates` → 从 PPT 导入 |
| 可视化编辑 | `/editor/:id?adminPreset=templateId` |
| 解析后端 | `pptx_template_parser.py` → `h5_template_service` |

**关系总结**：Agent 方案负责 **PowerPoint 设计与导出**；H5 平台负责 **移动端发布与互动编辑**。

---

## 11. 综合推荐：双栈策略

若四类需求（设计感、报告、图表、邀请）都要覆盖，建议 **组合使用**，而非单选：

| 栈 | 组合 | 用途 |
|----|------|------|
| **主栈（对外高质量）** | PPT Master + Opus + gpt-image-2 | 报告 / 对比 / 多格式邀请；`.pptx` 最稳 |
| **成本栈（内部迭代）** | PPT Master + DeepSeek V4 Pro + Pexels | 已有 DeepSeek API；打草稿 |
| **视觉栈（现代 / 动效）** | Open Design + Opus + HyperFrames MP4 | 融资路演、品牌 Story |
| **图表栈（数据绑定）** | Codex + ppt-polished-deck | 年报数据页、竞品对比表 |

---

## 12. 推荐落地步骤（Cursor + PPT Master + DeepSeek）

### 12.1 环境安装

1. Python 3.10+（勾选 Add to PATH）
2. 从 [AtomGit](https://atomgit.com/hugohe3/ppt-master) 下载 ZIP 解压到 `develop/ppt-master-main`，或 `git clone https://atomgit.com/hugohe3/ppt-master.git`
3. `python -m pip install -r requirements.txt`
4. Cursor **Open Folder** 打开 `develop/ppt-master-main` 根目录

### 12.2 Cursor 配置 DeepSeek V4 Pro

| 设置项 | 值 |
|--------|-----|
| OpenAI API Key | DeepSeek `sk-...` |
| Override OpenAI Base URL | `https://api.deepseek.com/v1` |
| 自定义模型 | `deepseek-v4-pro` |

Agent 不稳定时启用 [deepseek-cursor-proxy](https://github.com/yxlao/deepseek-cursor-proxy)。

### 12.3 安装 Skill

```powershell
npx skills add hugohe3/ppt-master
```

### 12.4 配图（可选）

在 `ppt-master/.env` 配置：

- 零配置：Web 搜图（Openverse / Wikimedia）
- 免费图库：`PEXELS_API_KEY` / `PIXABAY_API_KEY`
- AI 生图：`OPENAI_API_KEY` 等（Strategist 阶段选 AI 生成）

### 12.5 标准 Agent 话术示例

```
请按 PPT Master 工作流，用 deepseek-v4-pro 生成 12 页 16:9 演示文稿。
主题：2025 企业财报解读
受众：管理层
风格：简约商务、深蓝主色
Executor：Consultant_Top
图片来源：Pexels 搜图
导出到 exports/，告知文件路径。
```

### 12.6 验收清单

- [ ] `python -c "import pptx; import fitz"` 通过
- [ ] Cursor Verify DeepSeek 成功；Agent 3 页测试无 400
- [ ] `exports/` 出现可编辑 `.pptx`（Office 2016+）
- [ ] （可选）H5 管理端导入成功

### 12.7 对比验证建议

用 **同一主题** 做 3 页小样（封面 + 图表对比 + 邀请 1:1），横向比较：

1. PPT Master + DeepSeek V4 Pro  
2. PPT Master + Opus + gpt-image-2（若有 Opus）  
3. Gamma 或 Pi（SaaS 基准）

记录：耗时、单次费用、版式问题数、是否需 PowerPoint 手工修。

---

## 13. 多模型横评套件

> 操作步骤与 env 配置已合并进 **[AI-PPT生成指南.md](./AI-PPT生成指南.md)** §4。以下为套件文件索引。

本仓库提供 **PPT Master 五模型 A/B 测试** 文档包，路径：

**[`docs/ppt-master-benchmark/`](./ppt-master-benchmark/README.md)**

| 内容 | 文件 |
|------|------|
| 切换模型（改 `active_profile`） | [`model-profiles.yaml`](./ppt-master-benchmark/model-profiles.yaml) |
| 环境变量 | [`benchmark.env.example`](./ppt-master-benchmark/benchmark.env.example) + `develop/.env` 中 `DEEPSEEK_*` |
| 操作手册 | [`benchmark-runbook.md`](./ppt-master-benchmark/benchmark-runbook.md) |
| 8 页话术 | [`prompt-调研类.md`](./ppt-master-benchmark/prompt-调研类.md) / [`报告类`](./ppt-master-benchmark/prompt-报告类.md) / [`学术类`](./ppt-master-benchmark/prompt-学术类.md) |
| 评分与记录 | [`evaluation-rubric.md`](./ppt-master-benchmark/evaluation-rubric.md) / [`results-template.md`](./ppt-master-benchmark/results-template.md) |

**横评模型**：`gemini-3-pro`、`claude-opus-4-8`、`claude-opus-4-7`、`gpt-5-5`、`deepseek-v4-pro`（除 DeepSeek 外复用 `LLM_RELAY_*`）。

**两阶段**：Phase 1 固定 Web 搜图比模型；Phase 2 对 Top 1–2 加 gpt-image-2。

---

## 14. 参考链接

| 资源 | URL |
|------|-----|
| PPT Master | https://atomgit.com/hugohe3/ppt-master |
| PPT Master FAQ | https://atomgit.com/hugohe3/ppt-master/blob/main/docs/faq.md |
| PPT Master Windows 安装 | https://atomgit.com/hugohe3/ppt-master/blob/main/docs/zh/windows-installation.md |
| Open Design | https://github.com/nexu-io/open-design |
| HyperFrames | https://github.com/heygen-com/hyperframes |
| deepseek-cursor-proxy | https://github.com/yxlao/deepseek-cursor-proxy |
| OpenAI slides skill | https://www.piax.org/skills/openai-skills/slides |
| ppt-polished-deck-collab | https://github.com/Sven-LI-sankyuu/presentation-skills |
| DeepSeek 定价 | https://platform.deepseek.com |
| OpenAI 图像定价 | https://developers.openai.com/api/docs/guides/image-generation |
| Claude Opus 4.8 发布 | https://www.anthropic.com/news/claude-opus-4-8 |

---

## 15. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05 | 初版：四类需求对比 + Agent/SaaS 方案 + H5 平台衔接 + DeepSeek 落地步骤 |
| 2026-05 | 新增 `ppt-master-benchmark/` 五模型横评套件与三类 8 页话术 |
| 2026-05 | 新增 **[AI-PPT生成指南.md](./AI-PPT生成指南.md)** 作为最终版统一入口 |
