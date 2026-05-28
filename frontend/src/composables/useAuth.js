import { computed, ref } from 'vue'

const TOKEN_KEY = 'ai_h5_token'
const USER_KEY = 'ai_h5_user'
const REMEMBER_KEY = 'ai_h5_remember'

const user = ref(null)
const authReady = ref(false)

function getStoredToken() {
  return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY)
}

function loadUserFromStorage() {
  try {
    const raw =
      sessionStorage.getItem(USER_KEY) ||
      localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function clearSessionStorage() {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}

function clearLocalSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

function clearAllSession() {
  clearSessionStorage()
  clearLocalSession()
}

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value?.token)
  const isAdmin = computed(() => !!user.value?.is_admin)

  function setSession(data, remember = false) {
    user.value = data
    clearAllSession()
    const store = remember ? localStorage : sessionStorage
    store.setItem(TOKEN_KEY, data.token)
    store.setItem(USER_KEY, JSON.stringify(data))
  }

  function logout(options = {}) {
    user.value = null
    clearAllSession()
    if (options.clearRemember) {
      clearRememberCredentials()
    }
  }

  /** 退出并跳转登录页（不触发自动登录） */
  function performLogout(router, keepRemember = true) {
    logout({ clearRemember: !keepRemember })
    router.replace({
      name: 'login',
      query: {
        from: 'logout',
        keep: keepRemember ? '1' : '0',
      },
    })
  }

  function updateUser(patch) {
    if (!user.value) return
    user.value = { ...user.value, ...patch }
    const store = localStorage.getItem(TOKEN_KEY) ? localStorage : sessionStorage
    store.setItem(USER_KEY, JSON.stringify(user.value))
  }

  function authHeaders() {
    const t = getStoredToken()
    return t ? { Authorization: `Bearer ${t}` } : {}
  }

  function getRememberedCredentials() {
    try {
      const raw = localStorage.getItem(REMEMBER_KEY)
      if (!raw) return null
      const data = JSON.parse(raw)
      if (!data?.account || !data?.password) return null
      return data
    } catch {
      return null
    }
  }

  function saveRememberCredentials(account, password) {
    localStorage.setItem(
      REMEMBER_KEY,
      JSON.stringify({ account, password })
    )
  }

  function clearRememberCredentials() {
    localStorage.removeItem(REMEMBER_KEY)
  }

  async function refreshProfile() {
    const token = getStoredToken()
    if (!token) return null
    try {
      const res = await fetch('/api/v1/认证/我', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return null
      const me = await res.json()
      if (!user.value?.token) {
        user.value = { token, ...me, user_id: me.user_id }
      } else {
        updateUser({
          user_id: me.user_id,
          username: me.username,
          tier: me.tier,
          is_admin: me.is_admin,
          quota_remaining: me.quota_remaining,
          quota_total: me.quota_total,
        })
      }
      return me
    } catch {
      return null
    }
  }

  return {
    user,
    authReady,
    isLoggedIn,
    isAdmin,
    setSession,
    logout,
    performLogout,
    updateUser,
    authHeaders,
    refreshProfile,
    getRememberedCredentials,
    saveRememberCredentials,
    clearRememberCredentials,
    getStoredToken,
  }
}

/** 应用启动时校验本地 token，无效则清除 */
export async function initAuth() {
  const { refreshProfile, logout } = useAuth()

  // 清除旧版「未记住密码却写入 localStorage」的登录态
  const remembered = localStorage.getItem(REMEMBER_KEY)
  if (localStorage.getItem(TOKEN_KEY) && !remembered) {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  const token = getStoredToken()
  if (token) {
    const stored = loadUserFromStorage()
    user.value = stored ? { ...stored, token } : { token }
    const me = await refreshProfile()
    if (!me) {
      logout()
    }
  } else {
    user.value = null
  }
  authReady.value = true
}

/** 记住密码时静默登录（无需拼图） */
export async function tryRememberLogin() {
  const { getRememberedCredentials, setSession, refreshProfile } = useAuth()
  const saved = getRememberedCredentials()
  if (!saved) return null

  const res = await fetch('/api/v1/认证/登录', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      account: saved.account,
      password: saved.password,
      remember_login: true,
    }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    return null
  }
  setSession(data, true)
  await refreshProfile()
  return data
}
