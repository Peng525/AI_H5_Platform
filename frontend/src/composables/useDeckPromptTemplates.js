import { api } from '../api/client'
import { DECK_PROMPT_TEMPLATES } from '../constants/deckPromptTemplates'
import { usePromptTemplates } from './usePromptTemplates.js'

export function useDeckPromptTemplates() {
  return usePromptTemplates(() => api.listDeckPromptTemplates(), DECK_PROMPT_TEMPLATES)
}
