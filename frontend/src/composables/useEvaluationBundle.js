import { loadDraft } from './useAiCreateDraft.js'

const RUBRIC_HINT =
  '请按 evaluation-rubric Phase1 维度 1–6 对本演示进行人工打分（内容准确性、结构逻辑、视觉可读性、受众适配、语言质量、完整性）。'

export function buildEvaluationBundle(project, draftOverride = null) {
  const draft = draftOverride || loadDraft()
  const meta = project.generation_meta || {}
  return {
    project_public_id: project.public_id,
    title: project.title,
    model: meta.model || '',
    channel: meta.channel || '',
    duration_ms: meta.duration_ms ?? null,
    generated_at: new Date().toISOString(),
    generation_params: {
      topic: draft.topic || '',
      page_count: draft.pageCount ?? project.slides?.length ?? 0,
      audience: draft.audience || '',
      tone: draft.tone || '',
      text_density: draft.textDensity || '',
      language: draft.language || '',
      content_mode: draft.contentMode || 'free',
      viewport_mode: draft.viewportMode || 'auto',
      background_preset: draft.background || '',
      extra_instructions: draft.extraInstructions || '',
    },
    slides: (project.slides || []).map((s, i) => ({
      index: i + 1,
      layout: s.layout,
      title: s.title,
      subtitle: s.subtitle,
      bullets: s.bullets || [],
      speaker_notes: s.speaker_notes || '',
    })),
    evaluation_hint: RUBRIC_HINT,
  }
}

export function downloadEvaluationBundle(project, draftOverride = null) {
  const bundle = buildEvaluationBundle(project, draftOverride)
  const date = new Date().toISOString().slice(0, 10)
  const filename = `evaluation-${project.public_id}-${date}.json`
  const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  return bundle
}

export function evaluationBundleMarkdown(project, draftOverride = null) {
  const b = buildEvaluationBundle(project, draftOverride)
  const lines = [
    `# 演示评估包 · ${b.title || '无标题'}`,
    '',
    `- 项目标识: ${b.project_public_id}`,
    `- 模型: ${b.model || '—'}`,
    `- 耗时: ${b.duration_ms != null ? `${(b.duration_ms / 1000).toFixed(1)}s` : '—'}`,
    `- 生成时间: ${b.generated_at}`,
    '',
    '## 生成参数',
    '',
    `- 主题: ${b.generation_params.topic}`,
    `- 页数: ${b.generation_params.page_count}`,
    `- 受众: ${b.generation_params.audience}`,
    `- 语气: ${b.generation_params.tone}`,
    `- 文本量: ${b.generation_params.text_density}`,
    `- 语言: ${b.generation_params.language}`,
    `- 分页模式: ${b.generation_params.content_mode}`,
    '',
    '## 逐页内容',
    '',
  ]
  for (const s of b.slides) {
    lines.push(`### 第 ${s.index} 页 · ${s.title || '（无标题）'}`)
    if (s.subtitle) lines.push(`副标题: ${s.subtitle}`)
    if (s.bullets?.length) {
      lines.push('要点:')
      for (const bullet of s.bullets) lines.push(`- ${bullet}`)
    }
    if (s.speaker_notes) lines.push(`备注: ${s.speaker_notes}`)
    lines.push('')
  }
  lines.push('---', '', b.evaluation_hint)
  return lines.join('\n')
}

export async function copyEvaluationBundleMarkdown(project, draftOverride = null) {
  const md = evaluationBundleMarkdown(project, draftOverride)
  await navigator.clipboard.writeText(md)
  return md
}
