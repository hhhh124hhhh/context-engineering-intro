import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  // 侧边栏状态
  sidebarOpen: boolean

  // 模态框状态
  modal: {
    type: 'card-details' | 'deck-editor' | 'settings' | null
    data: any
  } | null

  // 通知状态
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    duration?: number
  }>

  // 主题设置
  theme: 'light' | 'dark' | 'auto'

  // 语言设置
  language: 'zh' | 'en'

  // 加载状态
  globalLoading: boolean
  loadingMessage: string

  // 页面状态
  currentPage: string
  previousPage: string

  // 操作
  toggleSidebar: () => void
  openModal: (type: string, data?: any) => void
  closeModal: () => void
  addNotification: (type: string, message: string, duration?: number) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
  setTheme: (theme: 'light' | 'dark' | 'auto') => void
  setLanguage: (language: 'zh' | 'en') => void
  setGlobalLoading: (loading: boolean, message?: string) => void
  setCurrentPage: (page: string) => void
  goBack: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // 初始状态
      sidebarOpen: true,
      modal: null,
      notifications: [],
      theme: 'dark',
      language: 'zh',
      globalLoading: false,
      loadingMessage: '',
      currentPage: '/home',
      previousPage: '',

      // 切换侧边栏
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }))
      },

      // 打开模态框
      openModal: (type: string, data?: any) => {
        set({
          modal: { type: type as any, data }
        })
      },

      // 关闭模态框
      closeModal: () => {
        set({ modal: null })
      },

      // 添加通知
      addNotification: (type: string, message: string, duration = 5000) => {
        const id = Date.now().toString()
        const notification = {
          id,
          type: type as any,
          message,
          duration
        }

        set((state) => ({
          notifications: [...state.notifications, notification]
        }))

        // 自动移除通知
        if (duration > 0) {
          setTimeout(() => {
            get().removeNotification(id)
          }, duration)
        }
      },

      // 移除通知
      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }))
      },

      // 清除所有通知
      clearNotifications: () => {
        set({ notifications: [] })
      },

      // 设置主题
      setTheme: (theme: 'light' | 'dark' | 'auto') => {
        set({ theme })
        // 应用主题到document
        document.documentElement.classList.remove('light', 'dark')
        if (theme === 'auto') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
          document.documentElement.classList.add(prefersDark ? 'dark' : 'light')
        } else {
          document.documentElement.classList.add(theme)
        }
      },

      // 设置语言
      setLanguage: (language: 'zh' | 'en') => {
        set({ language })
        document.documentElement.lang = language
      },

      // 设置全局加载状态
      setGlobalLoading: (loading: boolean, message = '') => {
        set({
          globalLoading: loading,
          loadingMessage: message
        })
      },

      // 设置当前页面
      setCurrentPage: (page: string) => {
        set((state) => ({
          currentPage: page,
          previousPage: state.currentPage
        }))
      },

      // 返回上一页
      goBack: () => {
        set((state) => ({
          currentPage: state.previousPage,
          previousPage: ''
        }))
      }
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        theme: state.theme,
        language: state.language
      })
    }
  )
)

// 初始化主题
const initializeTheme = () => {
  const { theme } = useUIStore.getState()

  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.classList.add(prefersDark ? 'dark' : 'light')
  } else {
    document.documentElement.classList.add(theme)
  }

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (useUIStore.getState().theme === 'auto') {
      document.documentElement.classList.remove('light', 'dark')
      document.documentElement.classList.add(e.matches ? 'dark' : 'light')
    }
  })
}

// 应用启动时初始化
if (typeof window !== 'undefined') {
  initializeTheme()
}