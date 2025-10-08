import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import App from './App'
import './index.css'

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5分钟
      cacheTime: 10 * 60 * 1000, // 10分钟
    },
    mutations: {
      retry: 1,
    },
  },
})

// 移除加载屏幕
const removeLoadingScreen = () => {
  const loadingScreen = document.getElementById('loading-screen')
  if (loadingScreen) {
    loadingScreen.style.opacity = '0'
    setTimeout(() => {
      if (loadingScreen.parentNode) {
        loadingScreen.remove()
      }
    }, 300)
  }
}

// 强制移除加载屏幕（超时处理）
const forceRemoveLoadingScreen = () => {
  const loadingScreen = document.getElementById('loading-screen')
  if (loadingScreen) {
    loadingScreen.remove()
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)

// 立即开始移除加载屏幕的倒计时
const startLoadingScreenRemoval = () => {
  // 如果加载已经完成，立即移除
  if (document.readyState === 'complete') {
    removeLoadingScreen()
    return
  }

  // 等待页面加载完成
  window.addEventListener('load', () => {
    removeLoadingScreen()
  })

  // 设置超时强制移除
  setTimeout(() => {
    forceRemoveLoadingScreen()
  }, 2000) // 2秒后强制移除
}

// 开始加载屏幕移除流程
startLoadingScreenRemoval()