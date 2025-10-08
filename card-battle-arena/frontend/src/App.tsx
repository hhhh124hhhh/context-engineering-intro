import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { initializeAuth } from '@/stores/authStore'
import { HomePage } from '@/pages/HomePage'
import { LobbyPage } from '@/pages/LobbyPage'
import { GamePage } from '@/pages/GamePage'
import { DeckPage } from '@/pages/DeckPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { LeaderboardPage } from '@/pages/LeaderboardPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { MessagesPage } from '@/pages/MessagesPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { PublicRoute } from '@/components/auth/PublicRoute'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { createFilteredConsole } from '@/utils/errorFilter'

function App() {
  const { isAuthenticated, isLoading } = useAuthStore()

  // 初始化错误过滤
  useEffect(() => {
    const restoreConsole = createFilteredConsole()
    return restoreConsole
  }, [])

  // 初始化认证状态
  useEffect(() => {
    console.log('🚀 应用启动，开始初始化认证状态')
    initializeAuth()
  }, [])

  // 显示加载屏幕（但限制最大时间）
  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-900 text-white">
        <Routes>
          {/* 公开路由 */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />

          {/* 受保护的路由 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/home" replace />} />
            <Route path="home" element={<HomePage />} />
            <Route path="lobby" element={<LobbyPage />} />
            <Route path="game/:gameId" element={<GamePage />} />
            <Route path="deck" element={<DeckPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="leaderboard" element={<LeaderboardPage />} />
            <Route path="stats" element={<LeaderboardPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* 404页面 */}
          <Route
            path="*"
            element={
              <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                  <h1 className="text-6xl font-bold text-gray-400 mb-4">404</h1>
                  <p className="text-xl text-gray-500 mb-8">页面未找到</p>
                  <a
                    href="/home"
                    className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    返回首页
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </ErrorBoundary>
  )
}

export default App