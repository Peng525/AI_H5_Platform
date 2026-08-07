# AI 提示词模板完全参考手册

> 最后更新：2026-08-08  
> 本文档列出项目中**所有**发送给 LLM 的提示词模板，包括 YAML 模板文件和 Python 内联 Prompt。  
> 每个模板标注了：**文件路径、用途、调用位置、变量列表、修改方法**。

---

## 目录

1. [PPT 生成类（5个）](#一ppt-生成类模板)
2. [PPT 编排类（3个，新增）](#二ppt-编排类模板新增)
3. [简历类（5个）](#三简历类模板)
4. [Python 内联 Prompt（2组）](#四python-内联-prompt)
5. [调用关系总图](#五调用关系总图)
6. [如何修改 Prompt](#六如何修改-prompt)

---

## 一、PPT 生成类模板

### 1.1 严格模板生成.yaml ⭐ 当前默认

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/严格模板生成.yaml` |
| **模板 ID** | `strict_ppt_template` |
| **用途** | AI 全量生成 PPT 的**默认 Prompt**。LLM 只输出 6 种模板类型的纯文本内容，图标/排版/配图均由系统自动处理。 |
| **谁调用** | `deck_generation_service.py:845` — `generate_deck_from_ai()` |
| **触发条件** | `body.strict_template_mode == True`（API 层 `projects.py:268` 强制设为 True） |
| **LLM 角色** | system + user |
| **LLM 输出** | JSON `{title, slides: [{template_type, title, points/cards/items, image_topic}]}` |
| **模板变量** | |
| | `{{ page_count }}` — 页数 |
| | `{{ topic }}` — 主题内容 |
| | `{{ language }}` — 语言（简体中文/English） |
| | `{{ text_density }}` — 文本密度（简约/精炼/详细/繁琐） |
| | `{{ audience }}` — 目标受众 |
| | `{{ style }}` — 风格描述 |
| | `{{ extra_instructions }}` — 附加说明 |
| | `{{ content_mode }}` — free 或 per_page |
| | `{{ page_contents }}` — 逐页内容数组（仅 per_page 模式） |
| **6 种模板** | `title_page`、`toc`、`points`、`cards`、`image_text_left`、`image_text_right` |
| **设计原则** | AI 最少参与 — 禁止 LLM 输出 icon/variant/image_query/坐标 |
| **渲染引擎** | 前端 `compilePptTemplateSlide.js` + `pptTemplateLayout.js` 坐标常量 |

### 1.2 固定布局生成.yaml（当前不可达）

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/固定布局生成.yaml` |
| **模板 ID** | `fixed_deck` |
| **用途** | 8 种固定布局 ID 的 PPT 生成。支持图表数据和 AI 生图。 |
| **谁调用** | `deck_generation_service.py:845` — `generate_deck_from_ai()` |
| **触发条件** | `body.strict_template_mode == False`（**当前 API 层强制 True，此路径不可达**） |
| **LLM 输出** | JSON `{title, slides: [{layout_id, title, subtitle, headline, visual_intent, image_prompt, points, chart}]}` |
| **8 种布局** | `cover_title`、`toc`、`chapter_divider`、`roadmap_bottom`、`scene_left`、`chart_left`、`key_points`、`closing` |
| **图片方式** | AI 生图（15-60秒/张），而非素材搜索 |
| **渲染引擎** | 前端 `compileFixedDeckSlide.js` |

### 1.3 全量生成.yaml（死代码，从未被调用）

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/全量生成.yaml` |
| **模板 ID** | `full_deck` |
| **用途** | 旧版 9 种语义模板的 PPT 生成。支持 modules 数组和选择性配图。 |
| **状态** | ❌ **死代码** — 在 `generate_deck_from_ai()` 中从未被引用，只在管理端模板列表展示 |
| **LLM 输出** | JSON `{title, theme, slides: [{template, modules, image_intent, image_prompt}]}` |
| **9 种模板** | `cover`、`section`、`split_lr`、`grid_2x2`、`cards_row`、`stat_hero`、`steps`、`quote`、`closing` |
| **图片方式** | 可选 AI 生图（cover_bg / scene / roadmap） |
| **渲染引擎** | 前端 `compileStructuredSlide.js` 中的 9 个 Builder 函数 |

### 1.4 单页改写.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/单页改写.yaml` |
| **模板 ID** | `single_page` |
| **用途** | 根据用户指示编辑/重写单张幻灯片内容 |
| **谁调用** | `deck_generation_service.py:1101` — `generate_single_slide_into_project()` |
| **触发条件** | 用户在结果页点击「AI 生成卡片」，对单页进行改写 |
| **特殊点** | 单页生成**始终使用固定布局生成.yaml**（不是严格模板），即使项目本身是严格模板模式 |

### 1.5 PPT 生成模板选择逻辑总结

```
用户点击「生成」
  ↓
前端 AiGenerateReview.vue → strict_template_mode: true
  ↓
API projects.py:268 → 强制 strict_template_mode = True
  ↓
deck_generation_service.py:845
  ├─ True  → 严格模板生成.yaml  ← 当前唯一活动路径
  └─ False → 固定布局生成.yaml  ← API 层阻断，不可达
  ↓
（全量生成.yaml 从未被 generate_deck_from_ai 引用 → 死代码）

单页改写 → 始终使用 固定布局生成.yaml（1101行）
```

---

## 二、PPT 编排类模板（新增）

### 2.1 orchestrate_strategist.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/orchestrate_strategist.yaml` |
| **模板 ID** | `orchestrate_strategist` |
| **用途** | **Phase 1 — 规划师**：根据主题规划 PPT 结构，输出每页的模板类型、标题和核心要点 |
| **谁调用** | `deck_orchestrator.py` — `_strategist_phase()` |
| **LLM 输出** | JSON `{title, theme, pages: [{page_num, template_type, title, key_points[], image_topic}]}` |
| **变量** | `{{ page_count }}` `{{ topic }}` `{{ language }}` `{{ style }}` `{{ audience }}` `{{ extra_instructions }}` |

### 2.2 orchestrate_executor.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/orchestrate_executor.yaml` |
| **模板 ID** | `orchestrate_executor` |
| **用途** | **Phase 2 — 执行者**：根据单页规划生成 1280×720 SVG 幻灯片 |
| **谁调用** | `deck_orchestrator.py` — `_executor_phase_serial()` / `_executor_phase_batch()` |
| **LLM 输出** | ` ```svg <svg>...</svg> ``` ` — 单页 SVG 代码 |
| **变量** | `{{ page_num }}` `{{ total_pages }}` `{{ template_type }}` `{{ page_title }}` `{{ subtitle }}` `{{ author }}` `{{ date }}` `{{ key_points }}` `{{ image_topic }}` `{{ deck_title }}` `{{ style }}` |
| **设计规范** | 1280×720、深蓝主色、禁止外部图片、字体统一 |

### 2.3 orchestrate_designer.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/orchestrate_designer.yaml` |
| **模板 ID** | `orchestrate_designer` |
| **用途** | **Phase 3 — UI 设计师**：审查所有 SVG，统一配色和视觉风格 |
| **谁调用** | `deck_orchestrator.py` — `_designer_phase()` |
| **LLM 输出** | JSON `{palette: {primary, accent, ...}, style_notes, slides: [{page_num, svg, changes}]}` |
| **变量** | `{{ slide_count }}` `{{ slides: [{page_num, template_type, svg}] }}` |

### 2.4 编排调用流程

```
POST /api/v1/项目/ai-生成-orchestrated
  → deck_orchestrator.orchestrate_deck_generation()
    → Phase 1: render_template("orchestrate_strategist.yaml")
    → Phase 2: render_template("orchestrate_executor.yaml") × N页
    → Phase 3: render_template("orchestrate_designer.yaml")
    → Phase 4: SVG → canvas_elements (策略A：背景图+文字叠加)
```

---

## 三、简历类模板

> 所有简历模板通过 `backend/app/services/resume/resume_service.py` 调用，使用 `render_template()` 加载。

### 3.1 resume_parse.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/resume_parse.yaml` |
| **调用位置** | `resume_service.py:213` — `_parse_structured()` |
| **用途** | 将用户原始简历文本解析为结构化 JSON |
| **变量** | `{{ source_text }}` |
| **LLM 输出** | 结构化简历 JSON（basics/experience/education/skills） |

### 3.2 resume_diagnose.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/resume_diagnose.yaml` |
| **调用位置** | `resume_service.py:225` — `_diagnose()` |
| **用途** | 根据简历结构化数据和用户目标，诊断简历问题 |
| **变量** | `{{ structured_json }}` `{{ user_prompt }}` |
| **LLM 输出** | 自由文本诊断报告 |

### 3.3 resume_generate.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/resume_generate.yaml` |
| **调用位置** | `resume_service.py:241` — `_generate_resume()` |
| **用途** | 根据诊断结果生成改进后的简历 |
| **变量** | `{{ structured_json }}` `{{ diagnosis }}` `{{ user_prompt }}` `{{ industry_snippet }}` |
| **LLM 输出** | 改进后的结构化简历 JSON |

### 3.4 resume_advice.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/resume_advice.yaml` |
| **调用位置** | `resume_service.py:261` — `_sidecar_from_llm()` |
| **用途** | 生成简历改进建议和下一步行动 |
| **变量** | `{{ structured_json }}` `{{ diagnosis }}` |
| **LLM 输出** | JSON `{advice: {...}, next_steps: [...]}` |

### 3.5 resume_optimize.yaml

| 项目 | 内容 |
|------|------|
| **文件** | `backend/templates/resume_optimize.yaml` |
| **调用位置** | `resume_service.py:402` — `optimize_resume()` |
| **用途** | 完整的简历优化流程（解析→诊断→生成→建议）中的一步 |
| **变量** | `{{ structured_json }}` `{{ user_prompt }}` |
| **LLM 输出** | 优化后的结构化简历 JSON |

---

## 四、Python 内联 Prompt

> 这些 Prompt 不是 YAML 模板，而是写在 Python 代码中的字符串拼接。

### 4.1 PPT-Master Worker — Strategist

| 项目 | 内容 |
|------|------|
| **文件** | `backend/app/services/ppt_master_worker/prompts.py:22-34` |
| **函数** | `build_strategist_system(language)` |
| **用途** | PPT-Master Worker 的规划阶段 System Prompt |
| **结构** | Python 字符串拼接 + 从 `ppt-master-main/skills/ppt-master/references/strategist.md` 读取参考文档 |
| **LLM 输出** | JSON `{pages: [{file, layout_file, title, brief}]}` |

### 4.2 PPT-Master Worker — Strategist User

| 项目 | 内容 |
|------|------|
| **文件** | `backend/app/services/ppt_master_worker/prompts.py:37-53` |
| **函数** | `build_strategist_user(topic, page_count, language, layout_files, extra_content)` |
| **用途** | PPT-Master Worker 的规划阶段 User Prompt |
| **结构** | 纯字符串拼接，包含 topic/page_count/language/layouts |

### 4.3 PPT-Master Worker — Executor

| 项目 | 内容 |
|------|------|
| **文件** | `backend/app/services/ppt_master_worker/prompts.py:57-67` |
| **函数** | `build_executor_system()` |
| **用途** | PPT-Master Worker 的执行阶段 System Prompt |
| **结构** | Python 字符串 + 从 `ppt-master-main/skills/ppt-master/references/executor-base.md` 和 `shared-standards.md` 读取 |

### 4.4 PPT-Master Worker — Executor User

| 项目 | 内容 |
|------|------|
| **文件** | `backend/app/services/ppt_master_worker/prompts.py:70-94` |
| **函数** | `build_executor_user(page_index, total_pages, page_title, page_brief, topic, language, layout_svg, spec_lock)` |
| **用途** | PPT-Master Worker 的执行阶段 User Prompt |
| **结构** | 字符串拼接 + 截断的布局 SVG 参考 |

### 4.5 PPT-Master Worker 调用路径

```
POST /api/v1/项目/ai-生成-premium
  → scheduler.py → orchestrator.py
    → strategist.py:72-85
      messages = [
        {"role": "system", "content": build_strategist_system(language)},
        {"role": "user", "content": build_strategist_user(...)}
      ]
    → executor.py:67-83 (逐页)
      messages = [
        {"role": "system", "content": build_executor_system()},
        {"role": "user", "content": build_executor_user(...)}
      ]
```

---

## 五、调用关系总图

```
┌─────────────────────────────────────────────────────────────┐
│                     PPT 生成相关                              │
├─────────────────────────────────────────────────────────────┤
│ POST /api/v1/项目/ai-生成                                    │
│   → generate_deck_from_ai()                                 │
│     → render_template("严格模板生成.yaml")     ← 当前默认     │
│     → render_template("固定布局生成.yaml")     ← API层阻断     │
│     → (全量生成.yaml)                         ← 死代码       │
│                                                             │
│ POST /api/v1/项目/ai-生成-orchestrated         ← 新增        │
│   → orchestrate_deck_generation()                            │
│     → render_template("orchestrate_strategist.yaml")         │
│     → render_template("orchestrate_executor.yaml") × N       │
│     → render_template("orchestrate_designer.yaml")           │
│                                                             │
│ POST /api/v1/项目/ai-生成-premium                            │
│   → ppt_master_worker                                       │
│     → build_strategist_system() + build_strategist_user()    │
│     → build_executor_system() + build_executor_user()        │
│                                                             │
│ POST /api/v1/项目/{id}/页面/ai-生成                           │
│   → generate_single_slide_into_project()                     │
│     → render_template("固定布局生成.yaml")     ← 单页强制    │
├─────────────────────────────────────────────────────────────┤
│                     简历相关                                  │
├─────────────────────────────────────────────────────────────┤
│ resume_service.py                                           │
│   → _parse_structured()    → render_template("resume_parse.yaml")    │
│   → _diagnose()            → render_template("resume_diagnose.yaml")  │
│   → _generate_resume()     → render_template("resume_generate.yaml") │
│   → _sidecar_from_llm()    → render_template("resume_advice.yaml")   │
│   → optimize_resume()      → render_template("resume_optimize.yaml") │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、如何修改 Prompt

### 方式 A：修改 YAML 模板（推荐）

**适用**：严格模板生成、固定布局生成、编排生成、简历功能

1. 找到文件：`backend/templates/<模板名>.yaml`
2. 修改 `system:` 或 `user:` 字段
3. 使用 Jinja2 语法 `{{ variable }}` 引用变量
4. 重启后端服务生效

**示例**：修改严格模板的配色约束
```yaml
# backend/templates/严格模板生成.yaml
system: |
  你是专业的商务汇报内容架构师。
  # 在这里添加新的约束
  配色以深蓝 #003366 为主色调。
  ...
```

### 方式 B：修改变量传递

**适用**：调整传给 Prompt 的变量值

1. 找到调用位置（如 `deck_generation_service.py:832-842`）
2. 修改 `variables` 字典
3. 重启后端服务生效

**示例**：增加一个新的变量
```python
# deck_generation_service.py:832
variables = {
    "page_count": body.page_count,
    "topic": _build_topic(body),
    "my_new_var": "新增的内容",  # ← 新增
    ...
}
```
然后在 YAML 中使用 `{{ my_new_var }}`。

### 方式 C：修改 Python 内联 Prompt

**适用**：PPT-Master Worker 的 Strategist/Executor Prompt

1. 找到文件：`backend/app/services/ppt_master_worker/prompts.py`
2. 修改对应的 `build_*` 函数
3. 同时可修改 `ppt-master-main/skills/ppt-master/references/` 下的 `.md` 参考文件

### 方式 D：通过管理端 UI 在线编辑

**适用**：管理端 → 文稿提示词管理（`/admin/prompts`）

- 可视化编辑 system 和 user Prompt
- 支持 YAML 格式
- 保存后立即生效

---

## 附录：快速查找表

| 我想改... | 去这个文件 | 修改位置 |
|-----------|-----------|----------|
| PPT生成的内容质量/格式 | `backend/templates/严格模板生成.yaml` | `system:` 字段 |
| PPT生成的页数/语言/风格 | `backend/app/services/deck_generation_service.py:832` | `variables` 字典 |
| PPT生成的模板选择逻辑 | `backend/app/services/deck_generation_service.py:845` | `prompt_template = ` 行 |
| 编排-规划师的输出格式 | `backend/templates/orchestrate_strategist.yaml` | `system:` 字段 |
| 编排-执行者的SVG设计规范 | `backend/templates/orchestrate_executor.yaml` | `system:` 字段 |
| 编排-设计师的审查标准 | `backend/templates/orchestrate_designer.yaml` | `system:` 字段 |
| PPT-Master Worker的Plan Prompt | `backend/app/services/ppt_master_worker/prompts.py:22` | `build_strategist_system()` |
| PPT-Master Worker的Generate Prompt | `backend/app/services/ppt_master_worker/prompts.py:57` | `build_executor_system()` |
| PPT-Master Worker的参考文档 | `ppt-master-main/skills/ppt-master/references/` | `strategist.md`, `executor-base.md`, `shared-standards.md` |
| 简历解析的Prompt | `backend/templates/resume_parse.yaml` | `system:` 字段 |
| 简历诊断的Prompt | `backend/templates/resume_diagnose.yaml` | `system:` 字段 |
| 简历生成的Prompt | `backend/templates/resume_generate.yaml` | `system:` 字段 |
| 简历建议的Prompt | `backend/templates/resume_advice.yaml` | `system:` 字段 |
| 简历优化的Prompt | `backend/templates/resume_optimize.yaml` | `system:` 字段 |
| 单页改写的Prompt | `backend/templates/固定布局生成.yaml` | `system:` 字段（单页复用固定布局模板） |
| 管理端在线编辑 | 浏览器打开 `/admin/prompts` | 所有 YAML 模板的 UI 编辑器 |
