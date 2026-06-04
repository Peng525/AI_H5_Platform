import CoverSlide from './templates/CoverSlide.vue'
import SectionSlide from './templates/SectionSlide.vue'
import Grid2x2Slide from './templates/Grid2x2Slide.vue'
import CardsRowSlide from './templates/CardsRowSlide.vue'
import SplitLrSlide from './templates/SplitLrSlide.vue'
import StatHeroSlide from './templates/StatHeroSlide.vue'
import StepsSlide from './templates/StepsSlide.vue'
import QuoteSlide from './templates/QuoteSlide.vue'
import ClosingSlide from './templates/ClosingSlide.vue'

export const SLIDE_TEMPLATE_REGISTRY = {
  cover: CoverSlide,
  section: SectionSlide,
  grid_2x2: Grid2x2Slide,
  cards_row: CardsRowSlide,
  split_lr: SplitLrSlide,
  stat_hero: StatHeroSlide,
  steps: StepsSlide,
  quote: QuoteSlide,
  closing: ClosingSlide,
}

export function getSlideTemplateComponent(template) {
  return SLIDE_TEMPLATE_REGISTRY[template] || SectionSlide
}
