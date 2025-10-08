export enum GameMode {
  RANKED = 'ranked',
  CASUAL = 'casual',
  PRACTICE = 'practice',
  TOURNAMENT = 'tournament',
  FRIENDLY = 'friendly'
}

export enum MatchStatus {
  WAITING = 'waiting',
  MATCHING = 'matching',
  MATCHED = 'matched',
  GAME_STARTED = 'game_started',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired'
}

export interface MatchRequest {
  queue_id: string
  user_id: number
  username: string
  mode: GameMode
  deck_id: number
  deck_name: string
  rating: number
  preferences: Record<string, any>
  status: MatchStatus
  created_at: number
}

export interface Match {
  match_id: string
  player1_id: number
  player2_id: number
  player1_username: string
  player2_username: string
  mode: GameMode
  deck1_id: number
  deck2_id: number
  created_at: number
  status: MatchStatus
}

export interface QueueStatus {
  mode: GameMode
  queue_length: number
  average_wait_time: number
  active_matches: number
}

export interface UserMatchStatus {
  in_queue: boolean
  in_match: boolean
  mode?: GameMode
  wait_time?: number
  status?: MatchStatus
  deck_id?: number
  match_id?: string
}

export interface MatchPreferences {
  max_wait_time?: number
  rating_tolerance?: number
  prefer_same_region?: boolean
  avoid_recent_players?: boolean
  deck_type_preference?: string
}

export interface WebSocketMessage {
  type: string
  timestamp?: number
  data?: any
}

export interface MatchFoundMessage extends WebSocketMessage {
  type: 'match_found'
  match: Match
  time_to_match: number
}

export interface MatchCancelledMessage extends WebSocketMessage {
  type: 'match_cancelled'
  reason: string
}

export interface QueueUpdateMessage extends WebSocketMessage {
  type: 'queue_update'
  queue_length: number
  estimated_wait_time: number
}

export interface StatusUpdateMessage extends WebSocketMessage {
  type: 'status_update'
  status: UserMatchStatus
}

export interface LeaderboardEntry {
  rank: number
  user_id: number
  username: string
  rating: number
  wins: number
  losses: number
  win_rate: number
  streak: number
}

export interface LeaderboardResponse {
  mode: GameMode
  season: string
  entries: LeaderboardEntry[]
  user_rank?: number
}

export interface MatchHistoryItem {
  match_id: string
  opponent_username: string
  mode: GameMode
  result: 'win' | 'loss' | 'draw'
  duration: number
  rating_change: number
  played_at: string
}

export interface MatchHistoryResponse {
  matches: MatchHistoryItem[]
  total: number
  limit: number
  offset: number
}

export interface SpectateRequest {
  match_id: string
}

export interface SpectateResponse {
  success: boolean
  match_id?: string
  spectator_token?: string
  message?: string
}

export interface SeasonInfo {
  season_id: string
  name: string
  start_date: string
  end_date?: string
  is_active: boolean
  rewards: Record<string, any>
}

export interface TournamentInfo {
  tournament_id: string
  name: string
  mode: GameMode
  max_participants: number
  current_participants: number
  start_time: string
  status: 'registration' | 'ongoing' | 'completed'
  entry_fee?: number
  prize_pool?: number
}

export interface TournamentRegistration {
  tournament_id: string
  deck_id: number
}