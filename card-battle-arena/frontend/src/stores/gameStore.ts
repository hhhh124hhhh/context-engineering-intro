import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { GameState, GamePlayer, Card } from '@types/game'
import { gameService } from '@services/gameService'

interface GameStore {
  // 游戏状态
  currentGame: GameState | null
  playerHand: Card[]
  battlefield: Card[]
  opponentHand: Card[]
  opponentBattlefield: Card[]
  selectedCard: Card | null
  validTargets: string[]

  // 游戏状态
  isMyTurn: boolean
  turnTime: number
  gamePhase: 'waiting' | 'playing' | 'ended'
  winner: 'player' | 'opponent' | null
  canPlayCards: boolean

  // 连接状态
  isConnected: boolean
  reconnecting: boolean
  error: string | null

  // 动画状态
  playingAnimation: boolean
  lastPlayedCard: Card | null
  damageAnimation: {
    target: string
    damage: number
  } | null

  // 操作
  connectToGame: (gameId: string) => Promise<void>
  disconnect: () => void
  playCard: (cardId: string, targetId?: string) => Promise<void>
  attack: (attackerId: string, targetId: string) => Promise<void>
  endTurn: () => Promise<void>
  concede: () => Promise<void>

  // 状态更新
  updateGameState: (gameState: GameState) => void
  selectCard: (card: Card | null) => void
  clearSelection: () => void
  setError: (error: string | null) => void
  clearError: () => void

  // 动画控制
  startAnimation: (type: string, data?: any) => void
  endAnimation: () => void
}

export const useGameStore = create<GameStore>()(
  subscribeWithSelector((set, get) => ({
    // 初始状态
    currentGame: null,
    playerHand: [],
    battlefield: [],
    opponentHand: [],
    opponentBattlefield: [],
    selectedCard: null,
    validTargets: [],

    isMyTurn: false,
    turnTime: 90,
    gamePhase: 'waiting',
    winner: null,
    canPlayCards: false,

    isConnected: false,
    reconnecting: false,
    error: null,

    playingAnimation: false,
    lastPlayedCard: null,
    damageAnimation: null,

    // 连接到游戏
    connectToGame: async (gameId: string) => {
      try {
        set({ reconnecting: true, error: null })

        await gameService.connectToGame(gameId)

        set({
          isConnected: true,
          reconnecting: false,
          error: null
        })
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '连接游戏失败'
        set({
          error: errorMessage,
          isConnected: false,
          reconnecting: false
        })
        throw error
      }
    },

    // 断开连接
    disconnect: () => {
      gameService.disconnect()
      set({
        isConnected: false,
        currentGame: null,
        playerHand: [],
        battlefield: [],
        opponentHand: [],
        opponentBattlefield: [],
        error: null
      })
    },

    // 出牌
    playCard: async (cardId: string, targetId?: string) => {
      try {
        const { currentGame, isMyTurn, canPlayCards } = get()

        if (!currentGame || !isMyTurn || !canPlayCards) {
          throw new Error('当前不能出牌')
        }

        set({ playingAnimation: true })

        await gameService.playCard(currentGame.id, cardId, targetId)

        // 动画会在WebSocket消息中处理
      } catch (error) {
        set({
          playingAnimation: false,
          error: error instanceof Error ? error.message : '出牌失败'
        })
        throw error
      }
    },

    // 攻击
    attack: async (attackerId: string, targetId: string) => {
      try {
        const { currentGame, isMyTurn } = get()

        if (!currentGame || !isMyTurn) {
          throw new Error('当前不能攻击')
        }

        set({ playingAnimation: true })

        await gameService.attack(currentGame.id, attackerId, targetId)

        // 动画会在WebSocket消息中处理
      } catch (error) {
        set({
          playingAnimation: false,
          error: error instanceof Error ? error.message : '攻击失败'
        })
        throw error
      }
    },

    // 结束回合
    endTurn: async () => {
      try {
        const { currentGame, isMyTurn } = get()

        if (!currentGame || !isMyTurn) {
          throw new Error('当前不能结束回合')
        }

        await gameService.endTurn(currentGame.id)

        set({ canPlayCards: false })
      } catch (error) {
        set({ error: error instanceof Error ? error.message : '结束回合失败' })
        throw error
      }
    },

    // 认输
    concede: async () => {
      try {
        const { currentGame } = get()

        if (!currentGame) {
          throw new Error('没有进行中的游戏')
        }

        await gameService.concede(currentGame.id)
      } catch (error) {
        set({ error: error instanceof Error ? error.message : '认输失败' })
        throw error
      }
    },

    // 更新游戏状态
    updateGameState: (gameState: GameState) => {
      const { user } = useAuthStore.getState()

      if (!user) return

      // 确定当前玩家和对手
      const player = gameState.players.find(p => p.id === user.id)
      const opponent = gameState.players.find(p => p.id !== user.id)

      if (!player || !opponent) return

      set({
        currentGame: gameState,
        playerHand: player.hand,
        battlefield: player.battlefield,
        opponentHand: opponent.hand,
        opponentBattlefield: opponent.battlefield,
        isMyTurn: gameState.current_player_id === user.id,
        turnTime: gameState.turn_time_limit || 90,
        gamePhase: gameState.status === 'playing' ? 'playing' : gameState.status === 'ended' ? 'ended' : 'waiting',
        winner: gameState.winner_id === user.id ? 'player' : gameState.winner_id === opponent.id ? 'opponent' : null,
        canPlayCards: gameState.current_player_id === user.id && gameState.status === 'playing'
      })
    },

    // 选择卡牌
    selectCard: (card: Card | null) => {
      set({
        selectedCard: card,
        validTargets: card ? getValidTargets(card) : []
      })
    },

    // 清除选择
    clearSelection: () => {
      set({
        selectedCard: null,
        validTargets: []
      })
    },

    // 设置错误
    setError: (error: string | null) => {
      set({ error })
    },

    // 清除错误
    clearError: () => {
      set({ error: null })
    },

    // 开始动画
    startAnimation: (type: string, data?: any) => {
      switch (type) {
        case 'playCard':
          set({
            playingAnimation: true,
            lastPlayedCard: data?.card || null
          })
          break
        case 'damage':
          set({
            damageAnimation: {
              target: data?.target || '',
              damage: data?.damage || 0
            }
          })
          break
        default:
          set({ playingAnimation: true })
      }
    },

    // 结束动画
    endAnimation: () => {
      set({
        playingAnimation: false,
        lastPlayedCard: null,
        damageAnimation: null
      })
    }
  })
))

// 获取有效攻击目标
function getValidTargets(card: Card): string[] {
  const { battlefield, opponentBattlefield } = useGameStore.getState()
  const targets: string[] = []

  if (card.type === 'spell') {
    // 法术可以攻击英雄和随从
    targets.push('opponent_hero')
    opponentBattlefield.forEach(minion => {
      targets.push(minion.id)
    })
  } else if (card.type === 'minion' && card.attack > 0) {
    // 随从可以攻击英雄和敌方随从
    if (card.canAttack) {
      targets.push('opponent_hero')
      opponentBattlefield.forEach(minion => {
        targets.push(minion.id)
      })
    }
  }

  return targets
}

// WebSocket消息处理
export const handleWebSocketMessage = (message: any) => {
  const store = useGameStore.getState()

  switch (message.type) {
    case 'game_update':
      if (message.data.gameState) {
        store.updateGameState(message.data.gameState)
      }
      break

    case 'card_played':
      store.startAnimation('playCard', { card: message.data.card })
      setTimeout(() => store.endAnimation(), 500)
      break

    case 'damage_dealt':
      store.startAnimation('damage', {
        target: message.data.target,
        damage: message.data.damage
      })
      setTimeout(() => store.endAnimation(), 300)
      break

    case 'turn_start':
      // 回合开始时更新状态
      if (message.data.gameState) {
        store.updateGameState(message.data.gameState)
      }
      break

    case 'turn_end':
      store.set({ canPlayCards: false })
      break

    case 'game_over':
      if (message.data.gameState) {
        store.updateGameState(message.data.gameState)
      }
      break

    case 'error':
      store.setError(message.data.message)
      break
  }
}