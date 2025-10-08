/**
 * 错误过滤工具
 * 用于过滤浏览器扩展等非关键错误
 */

// 需要过滤的错误关键词
const FILTERED_ERRORS = [
  'runtime.lastError',
  'Could not establish connection',
  'Receiving end does not exist',
  'message port closed',
  'utils.js',
  'extensionState.js',
  'heuristicsRedefinitions.js',
  'ERR_FILE_NOT_FOUND',
  'chrome-extension://',
  'moz-extension://',
  'safari-extension://'
]

/**
 * 判断是否为需要过滤的错误
 */
export function shouldFilterError(error: any): boolean {
  if (!error) return false

  const errorString = String(error).toLowerCase()
  return FILTERED_ERRORS.some(keyword =>
    errorString.includes(keyword.toLowerCase())
  )
}

/**
 * 过滤控制台错误输出
 */
export function createFilteredConsole() {
  const originalError = console.error
  const originalWarn = console.warn

  console.error = (...args: any[]) => {
    const message = args.join(' ')
    if (!shouldFilterError(message)) {
      originalError.apply(console, args)
    }
  }

  console.warn = (...args: any[]) => {
    const message = args.join(' ')
    if (!shouldFilterError(message)) {
      originalWarn.apply(console, args)
    }
  }

  // 恢复原始函数的清理方法
  return () => {
    console.error = originalError
    console.warn = originalWarn
  }
}

/**
 * 获取用户友好的错误消息
 */
export function getErrorMessage(error: any): string {
  if (!error) return '未知错误'

  // 如果是HTTP响应错误
  if (error.response) {
    const status = error.response.status
    const data = error.response.data

    switch (status) {
      case 400:
        return data?.detail || '请求参数错误'
      case 401:
        return '用户名/邮箱或密码错误'
      case 403:
        return data?.detail || '账户已被禁用或封禁'
      case 422:
        return data?.detail || '请求数据格式错误'
      case 429:
        return '请求过于频繁，请稍后重试'
      case 500:
        return '服务器内部错误，请稍后重试'
      default:
        return data?.detail || `请求失败 (${status})`
    }
  }

  // 如果是网络错误
  if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
    return '网络连接失败，请检查网络设置'
  }

  // 如果是超时错误
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return '请求超时，请稍后重试'
  }

  // 其他错误
  return error.message || '操作失败，请稍后重试'
}

/**
 * 创建增强的错误边界处理函数
 */
export function createErrorHandler(errorHandler?: (error: Error, errorInfo: any) => void) {
  return (error: Error, errorInfo: any) => {
    // 过滤掉扩展错误
    if (shouldFilterError(error)) {
      console.warn('过滤非关键错误:', error)
      return
    }

    console.error('应用错误:', error, errorInfo)

    if (errorHandler) {
      errorHandler(error, errorInfo)
    }
  }
}