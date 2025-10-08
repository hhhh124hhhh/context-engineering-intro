import axios, { AxiosInstance, AxiosResponse } from 'axios'

class ApiClient {
  private instance: AxiosInstance
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.instance = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加token到请求头
        const token = localStorage.getItem('auth-storage')
        if (token) {
          try {
            const authData = JSON.parse(token)
            if (authData.state?.token) {
              config.headers.Authorization = `Bearer ${authData.state.token}`
            }
          } catch (error) {
            console.error('解析认证数据失败:', error)
          }
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      async (error) => {
        const originalRequest = error.config

        // Token过期处理
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            // 尝试刷新token
            const refreshResponse = await this.refreshToken()
            const newToken = refreshResponse.data.access_token

            // 更新本地存储的token
            const token = localStorage.getItem('auth-storage')
            if (token) {
              const authData = JSON.parse(token)
              authData.state.token = newToken
              localStorage.setItem('auth-storage', JSON.stringify(authData))
            }

            // 重试原请求
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return this.instance(originalRequest)
          } catch (refreshError) {
            // 刷新失败，清除认证信息
            localStorage.removeItem('auth-storage')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private async refreshToken() {
    const token = localStorage.getItem('auth-storage')
    if (!token) {
      throw new Error('No refresh token available')
    }

    const authData = JSON.parse(token)
    if (!authData.state?.token) {
      throw new Error('No access token available')
    }

    // 这里应该调用刷新token的API
    // 暂时返回一个mock响应
    return {
      data: {
        access_token: authData.state.token,
        refresh_token: 'mock_refresh_token'
      }
    }
  }

  // 公共方法
  async get<T>(url: string, params?: any): Promise<T> {
    try {
      console.log(`📡 GET请求: ${this.baseURL}${url}`, { params })
      const response = await this.instance.get(url, { params })
      console.log(`✅ GET响应: ${url}`, { status: response.status, hasData: !!response.data })
      return response.data
    } catch (error) {
      console.error(`❌ GET请求失败: ${url}`, error)
      throw error
    }
  }

  async post<T>(url: string, data?: any): Promise<T> {
    try {
      console.log(`📤 POST请求: ${this.baseURL}${url}`, { data })
      const response = await this.instance.post(url, data)
      console.log(`✅ POST响应: ${url}`, { status: response.status, hasData: !!response.data })
      return response.data
    } catch (error) {
      console.error(`❌ POST请求失败: ${url}`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      throw error
    }
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.instance.put(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.instance.delete(url)
    return response.data
  }

  // 设置token
  setToken(token: string) {
    this.instance.defaults.headers.Authorization = `Bearer ${token}`
  }

  // 清除token
  clearToken() {
    delete this.instance.defaults.headers.Authorization
  }
}

// 创建API客户端实例
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const apiClient = new ApiClient(baseURL)

export default apiClient