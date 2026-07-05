import { api } from '../api/client'
import { IMAGE_PROMPT_TEMPLATES } from '../constants/imagePromptTemplates'
import { usePromptTemplates } from './usePromptTemplates.js'

export function useImagePromptTemplates() {
  return usePromptTemplates(() => api.listImagePromptTemplates(), IMAGE_PROMPT_TEMPLATES)
}
