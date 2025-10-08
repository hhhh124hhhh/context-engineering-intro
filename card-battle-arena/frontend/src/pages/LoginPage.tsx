import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
  UserIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface LoginFormData {
  username: string
  password: string
  rememberMe: boolean
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading, error, clearError } = useAuthStore()
  const { addNotification } = useUIStore()

  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
    rememberMe: false
  })

  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 获取重定向路径
  const getRedirectPath = () => {
    const params = new URLSearchParams(location.search)
    return params.get('redirect') || '/home'
  }

  // 处理表单输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    clearError()

    // 验证表单
    if (!formData.username.trim()) {
      addNotification('error', '请输入用户名')
      return
    }

    if (!formData.password.trim()) {
      addNotification('error', '请输入密码')
      return
    }

    setIsSubmitting(true)

    try {
      await login(formData.username, formData.password, formData.rememberMe)
      addNotification('success', '登录成功！')

      // 如果设置了记住我，保存用户名
      if (formData.rememberMe) {
        localStorage.setItem('remembered_username', formData.username)
      } else {
        localStorage.removeItem('remembered_username')
      }

      // 重定向到目标页面
      const redirectPath = getRedirectPath()
      navigate(redirectPath, { replace: true })
    } catch (error: any) {
      // 错误已经在store中处理，这里不需要额外处理
      console.error('登录页面错误:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 组件挂载时加载记住的用户名
  useEffect(() => {
    const rememberedUsername = localStorage.getItem('remembered_username')
    if (rememberedUsername) {
      setFormData(prev => ({
        ...prev,
        username: rememberedUsername,
        rememberMe: true
      }))
    }
  }, [])

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
        <div className="max-w-md w-full space-y-8">
          {/* Logo 和标题 */}
          <div className="text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center bg-primary-600 rounded-full mb-4">
              <SparklesIcon className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">
              欢迎回来
            </h1>
            <p className="mt-2 text-sm text-gray-400">
              登录您的卡牌对战竞技场账户
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-md">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* 登录表单 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 用户名 */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                用户名
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <UserIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请输入用户名"
                  autoComplete="username"
                />
              </div>
            </div>

            {/* 密码 */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                密码
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-10 py-2 border border-gray-600 bg-gray-800 text-white rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请输入密码"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* 记住我 */}
            <div className="flex items-center">
              <input
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                checked={formData.rememberMe}
                onChange={handleInputChange}
                className="h-4 w-4 rounded border-gray-600 bg-gray-800 text-primary-600 focus:ring-primary-500"
              />
              <label
                htmlFor="rememberMe"
                className="ml-2 block text-sm text-gray-300"
              >
                记住我的用户名
              </label>
            </div>

            {/* 提交按钮 */}
            <div>
              <Button
                type="submit"
                disabled={isLoading || isSubmitting}
                className="w-full flex justify-center"
              >
                {(isLoading || isSubmitting) ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>登录中...</span>
                  </div>
                ) : (
                  <span>登录</span>
                )}
              </Button>
            </div>
          </form>

          {/* 注册链接 */}
          <div className="text-center">
            <p className="text-sm text-gray-400">
              还没有账户？{' '}
              <Link
                to="/register"
                className="font-medium text-primary-400 hover:text-primary-300"
              >
                立即注册
              </Link>
            </p>
          </div>

          {/* 快速链接 */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              <Link
                to="/forgot-password"
                className="text-gray-400 hover:text-white underline"
              >
                忘记密码？
              </Link>
            </p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default LoginPage