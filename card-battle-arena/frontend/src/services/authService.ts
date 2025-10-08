import apiClient from './apiClient'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@types/auth'

class AuthService {
  private token: string | null = null

  // 登录
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      username,
      password
    })

    this.token = response.access_token
    return response
  }

  // 注册
  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', {
      username,
      email,
      password
    })

    this.token = response.access_token
    return response
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me')
    return response
  }

  // 更新用户信息
  async updateUser(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/users/me', userData)
    return response
  }

  // 刷新token
  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    const response = await apiClient.post<{ access_token: string; refresh_token: string }>('/auth/refresh', {
      refresh_token
    })

    this.token = response.access_token
    return response
  }

  // 登出
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } finally {
      this.token = null
    }
  }

  // 获取用户统计
  async getUserStats(): Promise<any> {
    const response = await apiClient.get('/users/me/stats')
    return response
  }

  // 设置token
  setToken(token: string): void {
    this.token = token
    apiClient.setToken(token)
  }

  // 清除token
  clearToken(): void {
    this.token = null
    apiClient.clearToken()
  }

  // 获取token
  getToken(): string | null {
    return this.token
  }

  // 检查是否已认证
  isAuthenticated(): boolean {
    return !!this.token
  }
}

export const authService = new AuthService()
export default authService