export interface User {
  id: number
  username: string
  email: string
  rating: number
  avatar?: string
  is_online: boolean
  last_login: string
  created_at: string
  stats: UserStats
}

export interface UserStats {
  games_played: number
  wins: number
  losses: number
  draws: number
  win_rate: number
  current_streak: number
  best_streak: number
  favorite_class: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  user: User
}