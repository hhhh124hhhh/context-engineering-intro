import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { LoadingScreen } from '@components/ui/LoadingScreen'

interface ProtectedRouteProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback
}) => {
  const { isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  // 显示加载屏幕
  if (isLoading) {
    return <LoadingScreen />
  }

  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    // 保存当前路径以便登录后重定向
    const currentPath = location.pathname + location.search
    if (currentPath !== '/login' && currentPath !== '/register') {
      return <Navigate to={`/login?redirect=${encodeURIComponent(currentPath)}`} replace />
    }
    return <Navigate to="/login" replace />
  }

  // 显示受保护的内容
  return <>{children}</>
}

export default ProtectedRoute