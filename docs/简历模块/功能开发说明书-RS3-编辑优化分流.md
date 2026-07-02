# 简历模块 — 功能开发说明书 RS3（编辑 / 优化分流 + 上传交互）

> **事实源**：[`需求清单-RS3-编辑优化分流.md`](./需求清单-RS3-编辑优化分流.md) · **任务卡**：[`任务拆解/R7-编辑优化分流.md`](./任务拆解/R7-编辑优化分流.md)

---

## 1. 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| 生成入口 | `/create/generate?tab=resume-edit` | 视觉模板选择 |
| 生成入口 | `/create/generate?tab=resume-optimize` | 上传 + 提示词 + 生成 |
| 工作台（编辑） | `/create/generate/resume/:publicId?mode=edit` | 两栏 |
| 工作台（优化） | `/create/generate/resume/:publicId?mode=optimize` | 三栏（缺省） |
| 简历列表 | `/dashboard/resumes` | 卡片链至 `mode=optimize` |

**Tab 兼容**：`?tab=resume` → 前端重定向为 `?tab=resume-optimize`。

---

## 2. 生成页组件结构

```
AiGenerateStart.vue
├── typeTabs: deck | image | resume-edit | resume-optimize
├── [resume-edit]
│   └── ResumeTemplatePicker  @select → createFromVisualTemplate()
└── [resume-optimize]
    ├── ResumeOptimizeForm.vue          ← 新建，封装上传+提示词+生成
    │   ├── ResumeAttachmentChip.vue    ← 左上角文件名 + 更换 + 移除
    │   ├── GenerateTopicInput          ← 提示词
    │   └── [生成] 按钮
    └── ResumeTemplatePicker（可选）     ← 提示词模板，空态且无附件时显示
```

### 2.1 上传交互（RS3-25 ~ RS3-30）

**现状问题**：`ResumeFileUpload.vue` 为大块虚线区，选中文件后按钮文案变为文件名，整块区域仍占主视觉，用户感知为「上传功能被占用」。

**目标结构**：

| 状态 | UI |
|------|-----|
| 无文件 | 提示词卡片上方或角标行显示轻量「上传简历」按钮 / 小虚线条 |
| 已选文件 | 提示词卡片**内顶部**一行：`ResumeAttachmentChip`（图标 + 文件名 truncate + 「更换」+ ×） |
| 更换 | 触发隐藏 `<input type="file">`，选中新文件替换 `pendingResumeFile` / 清空旧 `fileId` |
| 移除 | 清空附件状态；若提示词也为空 → 显示提示词模板区 |

**数据流（与现 `goResumeGenerate` 一致）**：

```javascript
// useResumeDraft 扩展
{
  tab: 'resume-optimize',
  prompt: '',
  fileId: null,
  fileName: '',
  pendingFile: null,  // 仅内存，不入 localStorage
  selectedPromptTemplateId: '',
}
```

生成时：优先上传 `pendingFile` → 得 `fileId` → `createResume` + `generateResume`。

---

## 3. 工作台组件结构

```
AiResumeWorkspace.vue
├── header（标题 / 保存 / 导出）
└── grid（由 mode + chatCollapsed 决定列）
    ├── ResumeChatAside.vue          ← 新建：包裹 ResumeChatPanel + 收起按钮
    ├── ResumeEditorPanel.vue        ← 复用 V2，无改动
    └── ResumeAdviceSidebar.vue    ← v-if="mode === 'optimize'"
```

**mode 解析**：

```javascript
const mode = computed(() =>
  route.query.mode === 'edit' ? 'edit' : 'optimize'
)
```

**网格 class**：

| 条件 | class |
|------|-------|
| optimize | `lg:grid-cols-[320px_1fr_280px]` |
| edit + 展开 | `lg:grid-cols-[320px_1fr]` |
| edit + 收起 | `lg:grid-cols-1`（ChatAside 绝对定位或 width:0） |

---

## 4. API 变更

### POST `/api/v1/resume`

```json
{
  "title": "我的简历",
  "template_id": "classic-blue",
  "prompt": null,
  "file_id": null
}
```

| 场景 | 行为 |
|------|------|
| 仅 `template_id` | 创建 profile + 首版 `structured` 空占位 + `compile_visual_document`；**无 LLM、无配额** |
| `prompt` / `file_id`（优化 Tab） | 与 V1 相同；随后前端调 `generate` 扣配额 |

`CreateResumeBody` 增加：

```python
template_id: str | None = None
```

### 其余接口

`generate` / `optimize` / `PUT` / `export` / `templates` **不变**。

---

## 5. 后端 `create_profile` 逻辑

```text
if body.template_id and not body.prompt and not body.file_id:
    structured = normalize_structured({})
    visual = compile_visual_document(structured, {"template_id": body.template_id})
    write_version(..., structured, visual_document=visual)
    return profile  # 不写 GenerationLog
else:
    # 现有 V1 逻辑
```

`template_id` 校验：必须在 `RESUME_TEMPLATES` / 已知 visual 模板注册表中。

---

## 6. 复用清单

| 能力 | 路径 | RS3 用法 |
|------|------|----------|
| 视觉模板选择 | `ResumeTemplatePicker.vue` | 编辑 Tab：跳转；优化 Tab：填 prompt（可选） |
| 提示词输入 | `GenerateTopicInput.vue` | 优化 Tab 内嵌 |
| 模板卡片样式 | `PromptTemplateCard.vue` | 不变 |
| 工作台编辑 | `ResumeEditorPanel.vue` + classic-blue 系列 | 不变 |
| AI 聊天 | `ResumeChatPanel.vue` | 包一层 Aside 支持收起 |
| 草稿 | `useResumeDraft.js` | 扩展字段 |
| 编译 | `visual_compiler.py` | 编辑创建时 compile |

**新建组件**：

- `ResumeOptimizeForm.vue` — 优化 Tab 主表单
- `ResumeAttachmentChip.vue` — 附件角标行
- `ResumeChatAside.vue` — 可收起左栏

**弱化 / 替换**：

- `ResumeFileUpload.vue` — 拆为轻量触发器 + `ResumeAttachmentChip`；或保留为子组件仅负责 file input + 校验

---

## 7. 与参考线框对照

原 P1 线框（Tab = 简历生成）：

```
[上传大块区]
[提示词]
[模板A B C]  ← 空态且未上传
[生成]
```

RS3 后：

**编辑 Tab**

```
[模板A classic-blue] [模板B …]  → 点击进 mode=edit 工作台
```

**优化 Tab**

```
[提示词卡片]
  ├─ 附件角标行（有文件时）
  └─ 多行提示词
[提示词模板]  ← 仅无输入且无附件
[生成]
```
