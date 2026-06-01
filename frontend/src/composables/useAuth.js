import { computed, ref } from 'vue'

const TOKEN_KEY = 'ai_h5_token'
const USER_KEY = 'ai_h5_user'
const REMEMBER_KEY = 'ai_h5_remember'

const user = ref(null)
const authReady = ref(false)

function hasRememberCredentials() {
  return !!localStorage.getItem(REMEMBER_KEY)
}

/** 仅内存 token，或「记住密码」时的 localStorage token */
function getStoredToken() {
  if (user.value?.token) return user.value.token
  if (hasRememberCredentials()) {
    return localStorage.getItem(TOKEN_KEY)
  }
  return null
}

function loadPersistedUser() {
  if (!hasRememberCredentials()) return null
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function clearPersistedSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value?.token)
  const isAdmin = computed(() => !!user.value?.is_admin)

  function setSession(data, remember = false) {
    clearPersistedSession()
    user.value = { ...data, token: data.token }
    if (remember) {
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    }
  }

  function logout(options = {}) {
    user.value = null
    clearPersistedSession()
    if (options.clearRemember) {
      clearRememberCredentials()
    }
  }

  function performLogout(router) {
    logout()
    router.replace({
      name: 'login',
      query: { from: 'logout' },
    })
  }

  function updateUser(patch) {
    if (!user.value) return
    user.value = { ...user.value, ...patch }
    if (hasRememberCredentials() && localStorage.getItem(TOKEN_KEY)) {
      localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    }
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
      if (!data?.account) return null
      return { account: data.account }
    } catch {
      return null
    }
  }

  function saveRememberCredentials(account) {
    localStorage.setItem(REMEMBER_KEY, JSON.stringify({ account: account.trim() }))
  }

  function clearRememberCredentials() {
    localStorage.removeItem(REMEMBER_KEY)
    clearPersistedSession()
  }

  function cachedMe() {
    if (!user.value?.username) return null
    return {
      user_id: user.value.user_id,
      username: user.value.username,
      tier: user.value.tier,
      is_admin: user.value.is_admin,
      quota_remaining: user.value.quota_remaining,
      quota_total: user.value.quota_total,
    }
  }

  /** 刷新用户信息；仅 401/无 token 返回 null，网络或服务端异常时保留已有会话 */
  async function refreshProfile() {
    const token = getStoredToken()
    if (!token) return null
    try {
      const res = await fetch('/api/v1/认证/我', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) return null
      if (!res.ok) return cachedMe()
      const me = await res.json()
      user.value = {
        ...user.value,
        token,
        user_id: me.user_id,
        username: me.username,
        tier: me.tier,
        is_admin: me.is_admin,
        quota_remaining: me.quota_remaining,
        quota_total: me.quota_total,
      }
      if (hasRememberCredentials() && localStorage.getItem(TOKEN_KEY)) {
        localStorage.setItem(USER_KEY, JSON.stringify(user.value))
      }
      return me
    } catch {
      return cachedMe()
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
    hasRememberCredentials,
  }
}

/** 启动时：无「记住密码」则不恢复登录；有则校验 token */
export async function initAuth() {
  const { refreshProfile, logout, getRememberedCredentials } = useAuth()

  user.value = null
  const saved = getRememberedCredentials()

  if (!saved) {
    clearPersistedSession()
    authReady.value = true
    return
  }

  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    const stored = loadPersistedUser()
    user.value = stored ? { ...stored, token } : { token }
    const me = await refreshProfile()
    if (!me) logout()
  }

  authReady.value = true
}

/** 记住密码时仅尝试用已存 JWT 恢复会话（不再跳过拼图） */
export async function tryRememberLogin() {
  const { refreshProfile, user } = useAuth()
  const me = await refreshProfile()
  return me ? user.value : null
}
