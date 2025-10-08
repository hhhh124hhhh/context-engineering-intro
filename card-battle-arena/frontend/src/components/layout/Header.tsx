import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'
import {
  HomeIcon,
  UserGroupIcon,
  DocumentTextIcon,
  UserIcon,
  LoginIcon,
  LogoutIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface HeaderProps {
  user?: any
  isAuthenticated?: boolean
  onMobileMenuToggle?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  user,
  isAuthenticated,
  onMobileMenuToggle
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { logout } = useAuthStore()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const navItems = [
    { name: '首页', path: '/home', icon: HomeIcon },
    { name: '大厅', path: '/lobby', icon: UserGroupIcon },
    { name: '卡组', path: '/deck', icon: DocumentTextIcon },
    { name: '资料', path: '/profile', icon: UserIcon },
  ]

  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo和移动端菜单 */}
          <div className="flex items-center">
            {/* 移动端菜单按钮 */}
            <button
              onClick={onMobileMenuToggle}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
            >
              {isAuthenticated ? (
                <Bars3Icon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>

            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">CB</span>
              </div>
              <span className="text-white font-bold text-xl hidden sm:block">
                卡牌竞技场
              </span>
            </Link>

            {/* 桌面端侧边栏切换 */}
            {isAuthenticated && (
              <button
                onClick={toggleSidebar}
                className="hidden lg:block p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
            )}
          </div>

          {/* 桌面端导航 */}
          {isAuthenticated ? (
            <nav className="hidden lg:flex items-center space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium
                    ${isActive(item.path)
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  `}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              ))}
            </nav>
          ) : (
            <nav className="hidden lg:flex items-center space-x-8">
              <Link
                to="/login"
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200"
              >
                <LoginIcon className="h-5 w-5" />
                <span>登录</span>
              </Link>
              <Link
                to="/register"
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200"
              >
                <UserIcon className="h-5 w-5" />
                <span>注册</span>
              </Link>
            </nav>
          )}

          {/* 用户信息 */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <>
                {/* 用户头像和菜单 */}
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {user.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="hidden sm:block">
                      <p className="text-sm font-medium text-white">{user.username}</p>
                      <p className="text-xs text-gray-400">等级 {user.rating}</p>
                    </div>
                  </div>
                </div>

                {/* 登出按钮 */}
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200"
                >
                  <LogoutIcon className="h-5 w-5" />
                  <span className="hidden sm:block">登出</span>
                </button>
              </>
            ) : (
              // 未登录状态
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700 transition-colors duration-200"
                >
                  <LoginIcon className="h-4 w-4" />
                  <span>登录</span>
                </Link>
                <Link
                  to="/register"
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-800 transition-colors duration-200"
                >
                  <UserIcon className="h-4 w-4" />
                  <span>注册</span>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* 移动端导航菜单 */}
        {isAuthenticated && (
          <div className="lg:hidden border-t border-gray-700">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    // 移动端点击菜单项后关闭菜单
                    if (onMobileMenuToggle) {
                      onMobileMenuToggle()
                    }
                  }}
                  className={`
                    flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium
                    ${isActive(item.path)
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  `}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header