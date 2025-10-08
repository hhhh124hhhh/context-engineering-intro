import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { apiClient } from '@services/apiClient'

interface GameMode {
  id: string
  name: string
  description: string
  playerCount: string
  avgWaitTime: string
  isRecommended?: boolean
}

interface OnlinePlayer {
  id: string
  username: string
  rating: number
  status: 'online' | 'ingame' | 'waiting'
  avatar?: string
}

interface MatchStatus {
  status: 'idle' | 'searching' | 'found' | 'cancelled'
  queuePosition?: number
  estimatedWaitTime?: number
  found?: boolean
}

interface LobbyStore {
  // 游戏模式
  gameModes: GameMode[]
  loadingModes: boolean
  modesError: string | null

  // 在线玩家
  onlinePlayers: OnlinePlayer[]
  loadingPlayers: boolean
  playersError: string | null

  // 匹配状态
  matchStatus: MatchStatus | null
  searching: boolean

  // 操作
  getGameModes: () => Promise<GameMode[]>
  getOnlinePlayers: () => Promise<OnlinePlayer[]>
  findMatch: (mode: string) => Promise<void>
  cancelMatchmaking: () => Promise<void>
  setMatchStatus: (status: MatchStatus) => void
}

export const useLobbyStore = create<LobbyStore>()(
  subscribeWithSelector((set, get) => ({
    // 初始状态
    gameModes: [],
    loadingModes: false,
    modesError: null,

    onlinePlayers: [],
    loadingPlayers: false,
    playersError: null,

    matchStatus: null,
    searching: false,

    // 获取游戏模式
    getGameModes: async () => {
      set({ loadingModes: true, modesError: null })
      try {
        // 由于后端缺少相关API，先返回模拟数据
        const modes: GameMode[] = [
          {
            id: 'ranked',
            name: '天梯对战',
            description: '天梯排位赛，影响您的段位和排名',
            playerCount: '1v1',
            avgWaitTime: '约2分钟',
            isRecommended: true
          },
          {
            id: 'casual',
            name: '休闲对战',
            description: '轻松的对战，不影响天梯排名',
            playerCount: '1v1',
            avgWaitTime: '约1分钟'
          },
          {
            id: 'practice',
            name: '练习模式',
            description: '与AI对战，熟悉卡牌和策略',
            playerCount: '1v0',
            avgWaitTime: '立即开始'
          }
        ]

        set({ gameModes: modes, loadingModes: false })
        return modes
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '获取游戏模式失败'
        set({ modesError: errorMessage, loadingModes: false })
        throw error
      }
    },

    // 获取在线玩家
    getOnlinePlayers: async () => {
      set({ loadingPlayers: true, playersError: null })
      try {
        // 由于后端缺少相关API，先返回模拟数据
        const players: OnlinePlayer[] = [
          { id: '1', username: 'DragonMaster', rating: 2345, status: 'online' },
          { id: '2', username: 'NinjaWarrior', rating: 2189, status: 'ingame' },
          { id: '3', username: 'MageKing', rating: 1987, status: 'waiting' },
          { id: '4', username: 'CardHunter', rating: 2100, status: 'online' },
          { id: '5', username: 'StormCaller', rating: 2234, status: 'online' }
        ]

        set({ onlinePlayers: players, loadingPlayers: false })
        return players
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '获取在线玩家失败'
        set({ playersError: errorMessage, loadingPlayers: false })
        throw error
      }
    },

    // 开始匹配
    findMatch: async (mode: string) => {
      set({ searching: true })
      try {
        // 由于后端缺少相关API，先模拟匹配过程
        set({ 
          matchStatus: { 
            status: 'searching',
            queuePosition: 1,
            estimatedWaitTime: 30
          } 
        })

        // 模拟匹配过程
        setTimeout(() => {
          set({ 
            matchStatus: { 
              status: 'found',
              found: true
            } 
          })
        }, 3000)
      } catch (error) {
        set({ searching: false })
        throw error
      }
    },

    // 取消匹配
    cancelMatchmaking: async () => {
      set({ 
        searching: false,
        matchStatus: { 
          status: 'cancelled'
        } 
      })
    },

    // 设置匹配状态
    setMatchStatus: (status: MatchStatus) => {
      set({ matchStatus: status })
    }
  }))
)