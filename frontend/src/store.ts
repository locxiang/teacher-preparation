import { reactive, computed } from 'vue'
import type { User } from './services/auth'
import { getToken, removeToken } from './services/auth'

export interface AuthState {
  user: User | null
  token: string | null
}

const authState = reactive<AuthState>({
  user: null,
  token: getToken(),
})

export const useAuthStore = () => {
  const isAuthenticated = computed(() => !!authState.token && !!authState.user)

  const setUser = (user: User) => {
    authState.user = user
  }

  const setToken = (token: string) => {
    authState.token = token
  }

  const logout = () => {
    authState.user = null
    authState.token = null
    removeToken()
  }

  return {
    user: computed(() => authState.user),
    token: computed(() => authState.token),
    isAuthenticated,
    setUser,
    setToken,
    logout,
  }
}

export const globalState = reactive({
  count: 0,
})
