import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
  UserIcon,
  EnvelopeIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface RegisterFormData {
  username: string
  email: string
  password: string
  confirmPassword: string
  agreeToTerms: boolean
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading, error, clearError } = useAuthStore()
  const { addNotification } = useUIStore()

  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  })

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 处理表单输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // 表单验证
  const validateForm = () => {
    // 用户名验证
    if (!formData.username.trim()) {
      addNotification('error', '请输入用户名')
      return false
    }

    if (formData.username.length < 3) {
      addNotification('error', '用户名至少需要3个字符')
      return false
    }

    if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      addNotification('error', '用户名只能包含字母、数字和下划线')
      return false
    }

    // 邮箱验证
    if (!formData.email.trim()) {
      addNotification('error', '请输入邮箱地址')
      return false
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      addNotification('error', '请输入有效的邮箱地址')
      return false
    }

    // 密码验证
    if (!formData.password.trim()) {
      addNotification('error', '请输入密码')
      return false
    }

    if (formData.password.length < 6) {
      addNotification('error', '密码至少需要6个字符')
      return false
    }

    // 确认密码验证
    if (formData.password !== formData.confirmPassword) {
      addNotification('error', '两次输入的密码不一致')
      return false
    }

    // 条款验证
    if (!formData.agreeToTerms) {
      addNotification('error', '请同意用户协议和隐私政策')
      return false
    }

    return true
  }

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    clearError()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      await register(
        formData.username,
        formData.email,
        formData.password
      )

      addNotification('success', '注册成功！请登录您的账户')
      navigate('/login', { replace: true })
    } catch (error: any) {
      // 错误已经在store中处理，这里不需要额外处理
    } finally {
      setIsSubmitting(false)
    }
  }

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
              创建账户
            </h1>
            <p className="mt-2 text-sm text-gray-400">
              加入卡牌对战竞技场，开始您的冒险之旅
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-md">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* 注册表单 */}
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
              <p className="mt-1 text-xs text-gray-500">
                只能包含字母、数字和下划线，至少3个字符
              </p>
            </div>

            {/* 邮箱 */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                邮箱地址
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-600 bg-gray-800 text-white rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请输入邮箱地址"
                  autoComplete="email"
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
                  autoComplete="new-password"
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
              <p className="mt-1 text-xs text-gray-500">
                至少需要6个字符
              </p>
            </div>

            {/* 确认密码 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                确认密码
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-10 py-2 border border-gray-600 bg-gray-800 text-white rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="请再次输入密码"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* 条款同意 */}
            <div className="flex items-start">
              <input
                id="agreeToTerms"
                name="agreeToTerms"
                type="checkbox"
                checked={formData.agreeToTerms}
                onChange={handleInputChange}
                className="h-4 w-4 rounded border-gray-600 bg-gray-800 text-primary-600 focus:ring-primary-500 mt-1"
              />
              <label
                htmlFor="agreeToTerms"
                className="ml-2 block text-sm text-gray-300"
              >
                我已阅读并同意{' '}
                <Link
                  to="/terms"
                  className="text-primary-400 hover:text-primary-300 underline"
                >
                  用户协议
                </Link>
                {' '}和{' '}
                <Link
                  to="/privacy"
                  className="text-primary-400 hover:text-primary-300 underline"
                >
                  隐私政策
                </Link>
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
                    <span>注册中...</span>
                  </div>
                ) : (
                  <span>创建账户</span>
                )}
              </Button>
            </div>
          </form>

          {/* 登录链接 */}
          <div className="text-center">
            <p className="text-sm text-gray-400">
              已有账户？{' '}
              <Link
                to="/login"
                className="font-medium text-primary-400 hover:text-primary-300"
              >
                立即登录
              </Link>
            </p>
          </div>

          {/* 快速链接 */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              注册即表示您同意我们的服务条款
            </p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default RegisterPage