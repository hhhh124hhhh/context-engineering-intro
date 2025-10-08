import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'

interface PublicRouteProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export const PublicRoute: React.FC<PublicRouteProps> = ({
  children,
  fallback
}) => {
  const { isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  // 显示加载屏幕
  if (isLoading) {
    return <LoadingScreen />
  }

  // 如果已认证，重定向到指定页面或首页
  if (isAuthenticated) {
    // 检查是否有重定向参数
    const urlParams = new URLSearchParams(location.search)
    const redirectPath = urlParams.get('redirect')

    if (redirectPath) {
      return <Navigate to={redirectPath} replace />
    }

    return <Navigate to="/home" replace />
  }

  // 显示公开内容
  return <>{children}</>
}

export default PublicRoute