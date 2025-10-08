export interface GameState {
  id: string
  status: 'waiting' | 'playing' | 'ended'
  current_player_id: number
  turn: number
  turn_time_limit: number
  players: GamePlayer[]
  winner_id?: number
  created_at: string
  updated_at: string
}

export interface GamePlayer {
  id: number
  username: string
  rating: number
  hero: Hero
  hand: Card[]
  battlefield: Card[]
  deck: Card[]
  graveyard: Card[]
  mana: number
  max_mana: number
  can_play_card: boolean
}

export interface Hero {
  id: string
  name: string
  class_name: string
  health: number
  max_health: number
  armor: number
  attack: number
  image_url: string
}

export interface Card {
  id: string
  name: string
  description: string
  cost: number
  class_name: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  type: 'minion' | 'spell' | 'weapon' | 'hero_power'
  attack: number
  health: number
  image_url: string
  card_text?: string
  mechanics?: string[]
  canAttack?: boolean
  hasTaunt?: boolean
  hasDivineShield?: boolean
  hasStealth?: boolean
  hasWindfury?: boolean
  hasPoison?: boolean
  hasLifesteal?: boolean
  hasSpellDamage?: number
}

export interface GameAction {
  type: 'play_card' | 'attack' | 'end_turn' | 'concede'
  player_id: number
  card_id?: string
  target_id?: string
  attacker_id?: string
  timestamp: string
}

export interface GameEvent {
  id: string
  game_id: string
  type: string
  data: any
  player_id: number
  timestamp: string
}

export interface PlayCardRequest {
  card_id: string
  target_id?: string
}

export interface AttackRequest {
  attacker_id: string
  target_id: string
}

export interface CreateGameRequest {
  deck_id: number
  game_mode?: 'ranked' | 'casual' | 'practice'
}

export interface GameStateResponse {
  game: GameState
  valid_actions: string[]
  turn_time_remaining: number
}