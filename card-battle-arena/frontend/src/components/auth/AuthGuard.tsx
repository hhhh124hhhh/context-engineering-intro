import React, { createContext, useContext, useEffect, useState } from 'react'
import { useAuthStore } from '@stores/authStore'

interface AuthGuardContextType {
  isReady: boolean
  refreshAuth: () => Promise<void>
}

const AuthGuardContext = createContext<AuthGuardContextType>({
  isReady: false,
  refreshAuth: async () => {}
})

interface AuthGuardProps {
  children: React.ReactNode
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const [isReady, setIsReady] = useState(false)
  const { isAuthenticated, isLoading, token } = useAuthStore()

  // 刷新认证状态
  const refreshAuth = async () => {
    try {
      setIsReady(false)

      // 如果有token，尝试验证其有效性
      if (token) {
        // 这里可以调用API验证token有效性
        // 暂时直接认为有效
        setIsReady(true)
      } else {
        setIsReady(true)
      }
    } catch (error) {
      console.error('认证状态刷新失败:', error)
      setIsReady(true)
    }
  }

  useEffect(() => {
    // 应用启动时初始化认证状态
    const initializeAuth = async () => {
      try {
        const { initializeAuth } = await import('@stores/authStore')
        await initializeAuth()
        setIsReady(true)
      } catch (error) {
        console.error('认证初始化失败:', error)
        setIsReady(true)
      }
    }

    initializeAuth()
  }, [])

  // 监听token变化
  useEffect(() => {
    if (token) {
      // Token存在，设置自动刷新
      const { startTokenRefresh } = require('@stores/authStore')
      startTokenRefresh()
    }
  }, [token])

  // 监听认证状态变化
  useEffect(() => {
    if (isAuthenticated && token) {
      // 已认证且有token，可以正常访问
      console.log('用户已认证')
    } else if (!isLoading) {
      // 未认证且不在加载中
      console.log('用户未认证')
    }
  }, [isAuthenticated, isLoading, token])

  // 页面可见性变化时刷新认证状态
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        refreshAuth()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  // 网络状态变化时刷新认证状态
  useEffect(() => {
    const handleOnline = () => {
      console.log('网络已连接，刷新认证状态')
      refreshAuth()
    }

    const handleOffline = () => {
      console.log('网络已断开')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const contextValue: AuthGuardContextType = {
    isReady,
    refreshAuth
  }

  return (
    <AuthGuardContext.Provider value={contextValue}>
      {children}
    </AuthGuardContext.Provider>
  )
}

// Hook to use auth guard context
export const useAuthGuard = () => {
  const context = useContext(AuthGuardContext)
  if (!context) {
    throw new Error('useAuthGuard must be used within AuthGuard')
  }
  return context
}

export default AuthGuard