import { computed, onMounted, ref } from 'vue'
import { api } from '../api/client'
import { useAuth } from './useAuth'

export function useQuota() {
  const { user, refreshProfile } = useAuth()
  const quota = ref({ remaining: 5, total: 5 })
  const quotaFailed = ref(false)

  const tierLabel = computed(() => (user.value?.tier === 'pro' ? '专业版' : '免费版'))
  const quotaText = computed(() =>
    quotaFailed.value ? '—' : `${quota.value.remaining}/${quota.value.total}`
  )

  async function refreshQuota() {
    try {
      const q = await api.getQuota()
      quota.value = { remaining: q.quota_remaining, total: q.quota_total }
      quotaFailed.value = false
    } catch {
      quotaFailed.value = true
    }
  }

  onMounted(async () => {
    if (!user.value?.username) {
      await refreshProfile()
    }
    await refreshQuota()
  })

  return { quota, quotaFailed, tierLabel, quotaText, refreshQuota }
}
