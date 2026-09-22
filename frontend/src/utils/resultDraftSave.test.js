import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { createApp, h, nextTick } from 'vue'
import AiGenerateResult from '../views/create/AiGenerateResult.vue'

const ui = vi.hoisted(() => ({ save: vi.fn(), success: vi.fn(), get: vi.fn(), download: vi.fn(), copy: vi.fn(), update: vi.fn(), canvas: null }))
vi.mock('../api/client', () => ({ api: { saveSlideCanvas: ui.save, getProject: ui.get, updateProject: ui.update } }))
vi.mock('vue-router', () => ({ useRoute: () => ({ params: { publicId: 'g1' } }), useRouter: () => ({ replace: vi.fn(), push: vi.fn() }) }))
vi.mock('../composables/useQuota.js', () => ({ useQuota: () => ({ refreshQuota: vi.fn() }) }))
vi.mock('../composables/useToast.js', () => ({ useToast: () => ({ success: ui.success }) }))
vi.mock('../composables/useEvaluationBundle.js', () => ({ downloadEvaluationBundle: ui.download, copyEvaluationBundleMarkdown: ui.copy }))
vi.mock('../components/CanvasElement.vue', () => ({ default: { render: () => null } }))
vi.mock('../components/EditorCanvasToolbar.vue', () => ({ default: { render: () => null } }))
vi.mock('../components/dialogue/DialoguePreviewCanvas.vue', () => ({ default: { render: () => null } }))
vi.mock('../slide-templates/SlideTemplateRenderer.vue', () => ({ default: { render: () => h('div', 'OLD STRUCTURED CONTENT') } }))
vi.mock('../components/create/ResultPageHeader.vue', () => ({ default: {
  props: ['title'], emits: ['update:title', 'save-title'],
  render() { return h('input', { 'data-test': 'title', value: this.title,
    onInput: e => this.$emit('update:title', e.target.value), onBlur: () => this.$emit('save-title') }) },
} }))
vi.mock('../components/DeckEditorWorkspace.vue', async () => {
  const { ref, onMounted, h } = await import('vue')
  return { default: {
    emits: ['project-loaded'],
    setup(_, { emit, expose }) {
      const current = ref({ id: 1, is_manually_edited: false, canvas_elements: [{ id: 't', type: 'text', content: 'Original', x: 72 }] })
      const elements = ref([{ id: 't', type: 'text', content: 'Keep my edit', x: 110 }])
      ui.canvas = { elements,
        updateElement(id, patch) { Object.assign(elements.value.find(e => e.id === id), patch) },
        flushCanvasSave() { return ui.save('g1', 1, elements.value, true) },
      }
      const project = { public_id: 'g1', title: 'G1', settings: {}, slides: [current.value] }
      expose({ flushCanvasSave: ui.canvas.flushCanvasSave, project })
      onMounted(() => emit('project-loaded', project))
      return () => h('div', ui.canvas.elements.value[0]?.content)
    },
  } }
})

let mounted = []
function mount(component, props) {
  const el = document.createElement('div')
  document.body.append(el)
  const app = createApp(component, props)
  app.mount(el)
  mounted.push({ app, el })
  return el
}
beforeEach(() => { localStorage.clear(); vi.useFakeTimers(); ui.save.mockReset(); ui.success.mockClear(); ui.get.mockClear(); ui.download.mockClear(); ui.copy.mockClear(); ui.update.mockReset().mockResolvedValue({title: 'G1'}); ui.get.mockReset().mockResolvedValue({public_id: 'g1', title: 'G1', slides: [], settings: {}}) })
afterEach(() => { mounted.forEach(({ app, el }) => { app.unmount(); el.remove() }); mounted = []; vi.clearAllTimers(); vi.useRealTimers() })

it('actual result-page Save shows failure without success/export and keeps the current canvas', async () => {
  ui.save.mockRejectedValue(new Error('G1 SAVE FAILED'))
  const el = mount(AiGenerateResult)
  await nextTick()
  el.querySelector('footer button').click()
  await vi.advanceTimersByTimeAsync(0)
  await nextTick()
  expect(el.textContent).toContain('G1 SAVE FAILED')
  expect(ui.success).not.toHaveBeenCalled()
  expect(ui.get).not.toHaveBeenCalled()
  expect(ui.download).not.toHaveBeenCalled()
  expect(ui.canvas.elements.value[0]).toMatchObject({ content: 'Keep my edit', x: 110 })
})


it('draft save waits for the server, blocks duplicate clicks and has no export side effects', async () => {
  let finish
  ui.save.mockImplementation(() => new Promise(resolve => { finish = resolve }))
  const el = mount(AiGenerateResult)
  await nextTick()
  const button = el.querySelector('footer button')
  expect(button.textContent).toContain('保存为草稿')
  button.click(); button.click()
  await vi.advanceTimersByTimeAsync(0)
  expect(button.disabled).toBe(true)
  expect(button.textContent).toContain('保存中…')
  expect(ui.save).toHaveBeenCalledTimes(1)
  expect(ui.success).not.toHaveBeenCalled()
  finish({})
  await vi.advanceTimersByTimeAsync(0)
  expect(ui.update).toHaveBeenCalledWith('g1', {title: 'G1'})
  expect(ui.save.mock.calls[0].slice(0, 2)).toEqual(['g1', 1])
  expect(ui.save.mock.calls[0][2][0]).toMatchObject({content: 'Keep my edit', x: 110})
  expect(ui.save.mock.calls[0][3]).toBe(true)
  expect(ui.success).toHaveBeenCalledWith('已保存为草稿，可在工作台继续编辑')
  expect(ui.download).not.toHaveBeenCalled()
  expect(ui.copy).not.toHaveBeenCalled()
  expect(button.disabled).toBe(false)
  expect(ui.canvas.elements.value[0].content).toBe('Keep my edit')
})

it('failed title save preserves edits and can be retried', async () => {
  ui.update.mockRejectedValueOnce(new Error('TITLE FAILED')).mockResolvedValue({title: 'G1'})
  ui.save.mockResolvedValue({})
  const el = mount(AiGenerateResult)
  await nextTick()
  el.querySelector('footer button').click()
  await vi.advanceTimersByTimeAsync(0)
  expect(el.textContent).toContain('TITLE FAILED')
  expect(ui.success).not.toHaveBeenCalled()
  expect(ui.canvas.elements.value[0].content).toBe('Keep my edit')
  el.querySelector('footer button').click()
  await vi.advanceTimersByTimeAsync(0)
  expect(ui.success).toHaveBeenCalledTimes(1)
  expect(el.textContent).not.toContain('TITLE FAILED')
})

it('a stale GET cannot replace edits made during saving', async () => {
  let finish
  ui.save.mockResolvedValue({})
  ui.get.mockImplementation(() => new Promise(resolve => { finish = resolve }))
  const el = mount(AiGenerateResult)
  await nextTick()
  el.querySelector('footer button').click()
  await vi.advanceTimersByTimeAsync(0)
  ui.canvas.updateElement('t', {content: 'Newer live edit', x: 120})
  finish({public_id: 'g1', title: 'G1', settings: {}, slides: []})
  await vi.advanceTimersByTimeAsync(0)
  expect(ui.canvas.elements.value[0]).toMatchObject({content: 'Newer live edit', x: 120})
})

it('an in-flight automatic title save finishes before the explicit latest title save', async () => {
  let finishOld
  ui.update.mockImplementationOnce(() => new Promise(resolve => { finishOld = resolve }))
    .mockResolvedValue({title: 'Latest title'})
  ui.save.mockResolvedValue({})
  const el = mount(AiGenerateResult)
  await nextTick()
  const input = el.querySelector('[data-test="title"]')
  input.value = 'Old title'; input.dispatchEvent(new Event('input')); input.dispatchEvent(new Event('blur'))
  await vi.advanceTimersByTimeAsync(400)
  expect(ui.update).toHaveBeenCalledTimes(1)
  input.value = 'Latest title'; input.dispatchEvent(new Event('input')); input.dispatchEvent(new Event('blur'))
  el.querySelector('footer button').click()
  await vi.advanceTimersByTimeAsync(0)
  expect(ui.update).toHaveBeenCalledTimes(1)
  expect(ui.success).not.toHaveBeenCalled()
  finishOld({title: 'Old title'})
  await vi.advanceTimersByTimeAsync(0)
  expect(ui.update.mock.calls.map(call => call[1].title)).toEqual(['Old title', 'Latest title'])
  expect(ui.success).toHaveBeenCalledTimes(1)
})
