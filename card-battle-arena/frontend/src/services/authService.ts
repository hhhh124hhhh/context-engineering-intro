import apiClient from './apiClient'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@types/auth'

class AuthService {
  private token: string | null = null

  // 登录
  async login(usernameOrEmail: string, password: string, rememberMe: boolean = false): Promise<AuthResponse> {
    try {
      console.log('🔐 开始登录流程:', { usernameOrEmail, rememberMe })

      const response = await apiClient.post<AuthResponse>('/auth/login', {
        username_or_email: usernameOrEmail,
        password,
        remember_me: rememberMe
      })

      console.log('✅ 登录响应:', {
        hasAccessToken: !!response.access_token,
        hasRefreshToken: !!response.refresh_token,
        tokenType: response.token_type,
        expiresIn: response.expires_in,
        hasUser: !!response.user
      })

      this.token = response.access_token
      return response
    } catch (error) {
      console.error('❌ 登录失败:', error)
      throw error
    }
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

  // 更新用户信息
  async updateUser(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/users/me', userData)
    return response
  }

  // 刷新token
  async refreshToken(): Promise<AuthResponse> {
    if (!this.token) {
      throw new Error('没有可刷新的token')
    }

    try {
      console.log('🔄 开始刷新token流程')

      const response = await apiClient.post<AuthResponse>('/auth/refresh')

      console.log('✅ 刷新token成功:', {
        hasAccessToken: !!response.access_token,
        hasRefreshToken: !!response.refresh_token
      })

      this.token = response.access_token
      apiClient.setToken(response.access_token)
      return response
    } catch (error) {
      console.error('❌ 刷新token失败:', error)
      throw error
    }
  }

  // 登出
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } finally {
      this.token = null
    }
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await apiClient.get<User>('/users/me')
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
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