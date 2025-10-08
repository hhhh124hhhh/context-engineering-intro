export interface Deck {
  id: number
  name: string
  class_name: string
  cards: DeckCard[]
  is_standard: boolean
  created_at: string
  updated_at: string
  user_id: number
  stats: DeckStats
}

export interface DeckCard {
  card_id: string
  count: number
  card: Card
}

export interface DeckStats {
  games_played: number
  wins: number
  losses: number
  win_rate: number
  avg_game_duration: number
}

export interface CreateDeckRequest {
  name: string
  class_name: string
  cards: Array<{
    card_id: string
    count: number
  }>
}

export interface UpdateDeckRequest {
  name?: string
  cards?: Array<{
    card_id: string
    count: number
  }>
}

export interface DeckAnalysis {
  mana_curve: Record<number, number>
  card_types: Record<string, number>
  rarities: Record<string, number>
  synergy_score: number
  power_level: number
  recommendations: string[]
}

export interface DeckImportData {
  name: string
  cards: Array<{
    name: string
    count: number
  }>
}