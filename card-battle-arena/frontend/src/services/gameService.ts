import apiClient from './apiClient'
import { GameState, PlayCardRequest, AttackRequest, CreateGameRequest } from '@types/game'

class GameService {
  private wsConnection: WebSocket | null = null
  private messageHandlers: Map<string, (data: any) => void> = new Map()

  // 创建游戏
  async createGame(deckId: number, gameMode: 'ranked' | 'casual' | 'practice' = 'ranked'): Promise<GameState> {
    const request: CreateGameRequest = {
      deck_id: deckId,
      game_mode: gameMode
    }

    const response = await apiClient.post<GameState>('/games/start', request)
    return response
  }

  // 获取游戏状态
  async getGameState(gameId: string): Promise<GameState> {
    const response = await apiClient.get<GameState>(`/games/${gameId}`)
    return response
  }

  // 出牌
  async playCard(gameId: string, cardId: string, targetId?: string): Promise<void> {
    const request: PlayCardRequest = {
      card_id: cardId,
      target_id: targetId
    }

    await apiClient.post(`/games/${gameId}/play-card`, request)
  }

  // 攻击
  async attack(gameId: string, attackerId: string, targetId: string): Promise<void> {
    const request: AttackRequest = {
      attacker_id: attackerId,
      target_id: targetId
    }

    await apiClient.post(`/games/${gameId}/attack`, request)
  }

  // 结束回合
  async endTurn(gameId: string): Promise<void> {
    await apiClient.post(`/games/${gameId}/end-turn`)
  }

  // 认输
  async concede(gameId: string): Promise<void> {
    await apiClient.post(`/games/${gameId}/concede`)
  }

  // 连接到游戏WebSocket
  connectToGame(gameId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/${gameId}`

      try {
        this.wsConnection = new WebSocket(wsUrl)

        this.wsConnection.onopen = () => {
          console.log('WebSocket连接已建立')
          resolve()
        }

        this.wsConnection.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        this.wsConnection.onclose = () => {
          console.log('WebSocket连接已关闭')
          this.wsConnection = null
        }

        this.wsConnection.onerror = (error) => {
          console.error('WebSocket连接错误:', error)
          reject(error)
        }

        // 心跳机制
        this.startHeartbeat()
      } catch (error) {
        reject(error)
      }
    })
  }

  // 断开WebSocket连接
  disconnect(): void {
    if (this.wsConnection) {
      this.wsConnection.close()
      this.wsConnection = null
    }
    this.stopHeartbeat()
  }

  // 注册消息处理器
  onMessage(type: string, handler: (data: any) => void): void {
    this.messageHandlers.set(type, handler)
  }

  // 移除消息处理器
  offMessage(type: string): void {
    this.messageHandlers.delete(type)
  }

  // 发送消息
  sendMessage(message: any): void {
    if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
      this.wsConnection.send(JSON.stringify(message))
    }
  }

  // 处理接收到的消息
  private handleMessage(message: any): void {
    const { type, data } = message
    const handler = this.messageHandlers.get(type)

    if (handler) {
      handler(data)
    }

    // 触发全局事件
    window.dispatchEvent(new CustomEvent('gameMessage', {
      detail: { type, data }
    }))
  }

  // 心跳机制
  private heartbeatInterval: NodeJS.Timeout | null = null

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.sendMessage({ type: 'ping', timestamp: Date.now() })
    }, 30000) // 每30秒发送一次心跳
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  // 获取连接状态
  isConnected(): boolean {
    return this.wsConnection !== null && this.wsConnection.readyState === WebSocket.OPEN
  }

  // 重新连接
  async reconnect(gameId: string): Promise<void> {
    this.disconnect()
    await this.connectToGame(gameId)
  }
}

export const gameService = new GameService()
export default gameService