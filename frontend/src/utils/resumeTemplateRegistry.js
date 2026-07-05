import TemplateClassic from '../components/resume/templates/TemplateClassic.vue'
import TemplateSimple from '../components/resume/templates/TemplateSimple.vue'
import TemplateMulti from '../components/resume/templates/TemplateMulti.vue'
import TemplateModern from '../components/resume/templates/TemplateModern.vue'
import TemplateBusiness from '../components/resume/templates/TemplateBusiness.vue'
import TemplateMagazine from '../components/resume/templates/TemplateMagazine.vue'
import TemplateTech from '../components/resume/templates/TemplateTech.vue'

const ALIASES = { 'classic-blue': 'template1' }

export function normalizeTemplateId(id) {
  if (!id) return 'template1'
  return ALIASES[id] || id
}

const REGISTRY = {
  template1: TemplateClassic,
  template2: TemplateSimple,
  template3: TemplateMulti,
  template4: TemplateModern,
  template5: TemplateBusiness,
  template6: TemplateMagazine,
  template7: TemplateTech,
}

export function resolveTemplateComponent(templateId) {
  const id = normalizeTemplateId(templateId)
  return REGISTRY[id] || TemplateClassic
}

export const TEMPLATE_OPTIONS = [
  { id: 'template1', title: '经典双栏' },
  { id: 'template2', title: '简易一页' },
  { id: 'template3', title: '多页分区' },
  { id: 'template4', title: '现代简洁' },
  { id: 'template5', title: '商务侧栏' },
  { id: 'template6', title: '杂志感' },
  { id: 'template7', title: '技术极客' },
]
