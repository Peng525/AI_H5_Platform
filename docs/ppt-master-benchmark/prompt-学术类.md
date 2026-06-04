# 横评话术 — 学术类（8 页）

> 使用前：在 [`model-profiles.yaml`](./model-profiles.yaml) 设置 `active_profile`，按 [`benchmark-runbook.md`](./benchmark-runbook.md) 同步 Cursor Models，**新开 Agent 会话**后整段复制发送。

---

## 复制起点（从这里到文末全部粘贴）

请严格按 **PPT Master** 完整工作流生成演示文稿，不要跳过 Strategist 八项确认。

### 横评元信息

- 类型：**学术类**（研究生开题答辩）
- 页数：**严格 8 页**，16:9，不得增减
- 项目目录：`projects/benchmark-{当前 active_profile}-学术-{YYYYMMDD}/`
- 当前横评 profile：请读取 [`model-profiles.yaml`](./model-profiles.yaml) 中的 `active_profile`
- benchmark_phase：
  - **若为 1**：Strategist 配图策略选 **Web-sourced**（Openverse / Pexels，零 AI 生图）
  - **若为 2**：配图使用 **gpt-image-2**（medium，16:9 内容区），与 Phase 1 同一模型

### Executor 与风格

- Executor：**Executor_General**
- 风格：学术简洁；白底为主、标题深灰 `#1A202C`、链接蓝 `#2B6CB0`
- 语言：简体中文；术语首次出现给英文缩写

### 研究主题（固定，不得更换方向）

**题目**：基于 Transformer 的医学影像三维分割方法研究

**背景要点**：

- 腹部 CT 多器官分割对术前规划重要
- U-Net 系方法在 3D 上下文建模上存在感受野局限

**问题定义**：

- 输入：512×512×D 腹部 CT 体数据
- 输出：肝、脾、胰三类器官 voxel-wise 标签
- 目标：Dice ≥ 0.85（三类平均）

**方法框架（须在方法页出现）**：

1. 预训练 ViT-3D encoder
2. 滑动窗口 patch 128³
3. 边界感知 loss（Dice + Boundary loss）

**实验设计（须在实验页出现）**：

- 数据集：BTCV 子集，30 例 train / 10 例 val
- Baseline：nnU-Net 3D
- 指标：Dice、HD95、参数量、推理时间（秒/体）

**预期贡献（3 条）**：

1. 提出轻量 3D Transformer 分割头，参数量较 baseline 降 18%
2. 边界 loss 降低 HD95 约 12%（相对 baseline）
3. 开源推理脚本与预训练权重

**参考文献（第 8 页必须列出，禁止编造 DOI，使用占位）**：

- [1] Author A et al. TransUNet. MICCAI, 2021. DOI: 待补充
- [2] Author B et al. nnU-Net. Nat Methods, 2021. DOI: 待补充
- [3] Author C et al. Swin UNETR. CVPR, 2022. DOI: 待补充
- [4] Author D et al. BTCV Challenge. 2015. DOI: 待补充
- [5] Author E et al. Boundary loss for segmentation. 2019. DOI: 待补充

格式：GB/T 7714 顺序编码制

### 8 页固定结构

1. **封面**：论文题目 + 答辩人「张某某」+ 导师「李某某 教授」+ 2025-06
2. **研究背景与意义**：临床需求 2 点 + 技术痛点 2 点
3. **文献综述**：CNN vs Transformer 各 2 句；指出现有不足 1 句
4. **问题定义**：输入/输出/指标 Dice≥0.85
5. **方法框架**：ViT-3D + patch + loss 三块示意图（SVG 即可）
6. **实验设计**：BTCV 划分、baseline、指标四列
7. **预期贡献**：上述 3 条
8. **参考文献**：[1]–[5] 占位条目

### 禁止项

- 禁止改为 7 页或 9 页
- **禁止编造真实 DOI 或虚构已发表论文全名**
- 禁止跳过导出脚本
- Phase 1 禁止 AI 生图

### 交付要求

1. 完成导出：`exports/` 下生成可编辑 `.pptx`
2. 回复：**总耗时**、**exports 路径**、**版式问题**
3. 公式可用文字描述，不要求 LaTeX 渲染

当前横评 profile：见 `model-profiles.yaml` 的 `active_profile`；benchmark_phase 见同文件 `benchmark_phase`。请严格 8 页，导出 exports/，并在完成后列出：耗时、是否改页、主要版式问题。

---

## 复制终点
