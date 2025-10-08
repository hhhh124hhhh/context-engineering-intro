import apiClient from './apiClient'
import { Deck, CreateDeckRequest, UpdateDeckRequest, DeckAnalysis } from '@types/deck'

class DeckService {
  // 获取用户的卡组列表
  async getDecks(): Promise<Deck[]> {
    const response = await apiClient.get<Deck[]>('/decks')
    return response
  }

  // 获取单个卡组
  async getDeck(deckId: number): Promise<Deck> {
    const response = await apiClient.get<Deck>(`/decks/${deckId}`)
    return response
  }

  // 创建卡组
  async createDeck(deckData: CreateDeckRequest): Promise<Deck> {
    const response = await apiClient.post<Deck>('/decks', deckData)
    return response
  }

  // 更新卡组
  async updateDeck(deckId: number, deckData: UpdateDeckRequest): Promise<Deck> {
    const response = await apiClient.put<Deck>(`/decks/${deckId}`, deckData)
    return response
  }

  // 删除卡组
  async deleteDeck(deckId: number): Promise<void> {
    await apiClient.delete(`/decks/${deckId}`)
  }

  // 复制卡组
  async duplicateDeck(deckId: number, newName: string): Promise<Deck> {
    const response = await apiClient.post<Deck>(`/decks/${deckId}/duplicate`, {
      name: newName
    })
    return response
  }

  // 分析卡组
  async analyzeDeck(deckId: number): Promise<DeckAnalysis> {
    const response = await apiClient.get<DeckAnalysis>(`/decks/${deckId}/analyze`)
    return response
  }

  // 导入卡组
  async importDeck(importData: any): Promise<Deck> {
    const response = await apiClient.post<Deck>('/decks/import', importData)
    return response
  }

  // 导出卡组
  async exportDeck(deckId: number, format: 'json' | 'text' = 'json'): Promise<any> {
    const response = await apiClient.get(`/decks/${deckId}/export`, {
      params: { format }
    })
    return response
  }

  // 获取卡组统计
  async getDeckStats(deckId: number): Promise<any> {
    const response = await apiClient.get(`/decks/${deckId}/stats`)
    return response
  }

  // 验证卡组
  async validateDeck(deckData: CreateDeckRequest): Promise<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }> {
    const response = await apiClient.post('/decks/validate', deckData)
    return response
  }
}

export const deckService = new DeckService()
export default deckService