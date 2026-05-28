import { computed, ref } from 'vue'

const TOKEN_KEY = 'ai_h5_token'
const USER_KEY = 'ai_h5_user'

const user = ref(loadUser())

function loadUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value?.token)
  const isAdmin = computed(() => !!user.value?.is_admin)

  function setSession(data) {
    user.value = data
    localStorage.setItem(TOKEN_KEY, data.token)
    localStorage.setItem(USER_KEY, JSON.stringify(data))
  }

  function logout() {
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function updateUser(patch) {
    if (!user.value) return
    user.value = { ...user.value, ...patch }
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
  }

  function authHeaders() {
    const t = localStorage.getItem(TOKEN_KEY)
    return t ? { Authorization: `Bearer ${t}` } : {}
  }

  async function refreshProfile() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return null
    try {
      const res = await fetch('/api/v1/认证/我', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return null
      const me = await res.json()
      updateUser({
        user_id: me.user_id,
        username: me.username,
        tier: me.tier,
        is_admin: me.is_admin,
      })
      return me
    } catch {
      return null
    }
  }

  return { user, isLoggedIn, isAdmin, setSession, logout, updateUser, authHeaders, refreshProfile }
}
