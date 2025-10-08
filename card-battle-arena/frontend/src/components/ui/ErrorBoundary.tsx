import React, { Component, ErrorInfo, ReactNode } from 'react'
import { motion } from 'framer-motion'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      hasError: true,
      error,
      errorInfo,
    })
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center justify-center min-h-screen bg-gray-900"
        >
          <div className="text-center p-8 max-w-md">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, duration: 0.2 }}
              className="w-20 h-20 mx-auto mb-4 text-red-500"
            >
              <svg
                className="w-full h-full"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.607.336 3.236-.336 4.842-.336c1.606 0 3.235-.336 4.842-.336c1.607 0 3.236-.336 4.842-.336c1.607 0 3.235-.336 4.842-.336c1.607 0 3.236-.336 4.842-.336c1.607 0 3.235-.336 4.842-.336"
                />
              </svg>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.2 }}
              className="text-2xl font-bold text-white mb-2"
            >
              出现了错误
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.2 }}
              className="text-gray-400 mb-6"
            >
              很抱歉，应用程序遇到了一个错误。请尝试刷新页面或联系技术支持。
            </motion.p>

            {this.state.error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.2 }}
                className="bg-gray-800 rounded-lg p-4 mb-6 text-left"
              >
                <p className="text-sm font-mono text-red-400 mb-2">
                  错误类型: {this.state.error.name}
                </p>
                <p className="text-sm text-gray-300 break-all">
                  {this.state.error.message}
                </p>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.2 }}
              className="flex space-x-4"
            >
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7, duration: 0.2 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={this.handleReset}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                重新加载
              </motion.button>

              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8, duration: 0.2 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                刷新页面
              </motion.button>
            </motion.div>

            {process.env.NODE_ENV === 'development' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9, duration: 0.2 }}
                className="mt-4"
              >
                <details className="text-left">
                  <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-300">
                    错误详情 (仅开发模式)
                  </summary>
                  <pre className="mt-2 p-2 bg-gray-800 rounded text-xs text-gray-300 overflow-auto max-h-40">
                    {this.state.error && this.state.error.stack}
                    {this.state.errorInfo && (
                      <div className="mt-2 text-gray-400">
                        <p className="font-semibold">Component Stack:</p>
                        <pre className="text-gray-500">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </pre>
                </details>
              </motion.div>
            )}
          </div>
        </motion.div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary