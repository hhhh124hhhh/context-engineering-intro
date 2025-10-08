import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { User } from '@types/auth'
import { authService } from '@services/authService'
import { getErrorMessage } from '@utils/errorFilter'

interface AuthState {
  // 状态
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // 操作
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  clearError: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // 登录
      login: async (username: string, password: string) => {
        try {
          set({ isLoading: true, error: null })

          const response = await authService.login(username, password)

          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })

          // 设置token到API客户端
          authService.setToken(response.access_token)
        } catch (error) {
          const errorMessage = getErrorMessage(error)
          console.error('登录失败:', error)
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            user: null,
            token: null
          })
          throw error
        }
      },

      // 注册
      register: async (username: string, email: string, password: string) => {
        try {
          set({ isLoading: true, error: null })

          const response = await authService.register(username, email, password)

          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })

          // 设置token到API客户端
          authService.setToken(response.access_token)
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '注册失败'
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            user: null,
            token: null
          })
          throw error
        }
      },

      // 登出
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
          isLoading: false
        })

        // 清除API客户端token
        authService.clearToken()
      },

      // 刷新token
      refreshToken: async () => {
        try {
          const { token } = get()
          if (!token) return

          const response = await authService.refreshToken()

          set({
            token: response.access_token,
            user: response.user
          })

          // 更新API客户端token
          authService.setToken(response.access_token)
        } catch (error) {
          console.error('认证存储刷新token失败:', error)
          // 刷新失败，直接登出
          get().logout()
          throw error
        }
      },

      // 清除错误
      clearError: () => {
        set({ error: null })
      },

      // 设置加载状态
      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化必要的字段
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// 自动检查token有效性
let refreshTimer: NodeJS.Timeout | null = null

export const startTokenRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }

  refreshTimer = setInterval(() => {
    const { isAuthenticated, refreshToken } = useAuthStore.getState()
    if (isAuthenticated) {
      refreshToken().catch(() => {
        // 刷新失败时，store会自动处理登出
      })
    }
  }, 25 * 60 * 1000) // 每25分钟刷新一次
}

export const stopTokenRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 应用启动时检查认证状态
export const initializeAuth = async () => {
  const { token, refreshToken } = useAuthStore.getState()

  if (token) {
    try {
      authService.setToken(token)
      startTokenRefresh()

      // 验证token有效性
      const user = await authService.getCurrentUser()
      useAuthStore.getState().setLoading(false)

      if (user) {
        useAuthStore.setState({
          user,
          isAuthenticated: true
        })
      } else {
        useAuthStore.getState().logout()
      }
    } catch (error) {
      console.error('Token验证失败:', error)
      useAuthStore.getState().logout()
    }
  } else {
    useAuthStore.getState().setLoading(false)
  }
}