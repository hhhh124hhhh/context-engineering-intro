export interface User {
  id: number
  username: string
  email: string
  elo_rating: number
  level: number
  experience: number
  coins: number
  display_name?: string
  avatar_url?: string
  bio?: string
  country?: string
  is_active: boolean
  is_verified: boolean
  is_online: boolean
  games_played: number
  games_won: number
  games_lost: number
  win_streak: number
  best_win_streak: number
  created_at: string
  last_login_at?: string
}

export interface UserStats {
  games_played: number
  games_won: number
  games_lost: number
  win_rate: number
  current_win_streak: number
  best_win_streak: number
  favorite_class?: string
  average_game_duration?: number
  total_play_time: number
}

export interface LoginRequest {
  username_or_email: string
  password: string
  remember_me?: boolean
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