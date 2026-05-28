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

  return { user, isLoggedIn, setSession, logout, updateUser, authHeaders }
}
