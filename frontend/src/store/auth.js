import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/endpoints.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user  = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin    = computed(() => !!user.value?.is_admin)

  /**
   * login() returns:
   *   { access_token, user }          → login complete
   *   { mfa_required: true, mfa_token } → MFA challenge, caller must show TOTP input
   */
  async function login(username, password) {
    const data = await authApi.login({ username, password })

    // MFA challenge (HTTP 202 → axios resolves normally)
    if (data?.mfa_required) {
      return data  // { mfa_required: true, mfa_token }
    }

    _setSession(data)
    return data
  }

  async function loginMfa(mfaToken, code) {
    const data = await authApi.loginMfa({ mfa_token: mfaToken, code })
    _setSession(data)
    return data
  }

  function _setSession(data) {
    token.value = data.access_token
    user.value  = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user',  JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, isAdmin, login, loginMfa, logout }
})
