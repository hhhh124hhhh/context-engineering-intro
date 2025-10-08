import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { Footer } from './Footer'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import { LoadingScreen } from '@components/ui/LoadingScreen'

interface LayoutProps {
  children?: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuthStore()
  const { sidebarOpen } = useUIStore()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // 处理移动端菜单
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-900 text-white flex flex-col">
        {/* 顶部导航栏 */}
        <Header
          user={user}
          isAuthenticated={isAuthenticated}
          onMobileMenuToggle={toggleMobileMenu}
        />

        {/* 主内容区域 */}
        <div className="flex flex-1 relative">
          {/* 侧边栏 - 桌面端 */}
          <aside className={`
            hidden lg:block
            w-64 bg-gray-800 border-r border-gray-700
            transition-all duration-300 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          `}>
            <Sidebar />
          </aside>

          {/* 移动端侧边栏 */}
          {isMobileMenuOpen && (
            <div className="fixed inset-0 z-50 lg:hidden">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={closeMobileMenu} />
              <div className="fixed left-0 top-0 h-full w-64 bg-gray-800 border-r border-gray-700">
                <Sidebar />
              </div>
            </div>
          )}

          {/* 主内容 */}
          <main className="flex-1 overflow-y-auto">
            <div className="p-4 lg:p-6">
              {/* 页面内容 */}
              {children || <Outlet />}
            </div>
          </main>
        </div>

        {/* 底部 */}
        <Footer />

        {/* 移动端菜单覆盖层 - 暂时移除，改为使用Header中的汉堡菜单 */}
        {/*
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div
              className="fixed inset-0 bg-black bg-opacity-50"
              onClick={closeMobileMenu}
            />
            <div className="fixed left-0 top-0 h-full w-64 bg-gray-800 border-r border-gray-700">
              <Sidebar />
            </div>
          </div>
        )}
        */}
      </div>
    </ErrorBoundary>
  )
}

export default Layout