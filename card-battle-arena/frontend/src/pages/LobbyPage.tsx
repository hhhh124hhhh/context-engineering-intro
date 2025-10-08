import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useLobbyStore } from '@stores/lobbyStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  UserGroupIcon,
  PlayIcon,
  ClockIcon,
  TrophyIcon,
  StarIcon,
  XMarkIcon,
  SparklesIcon,
  CheckIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

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

export const LobbyPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const {
    findMatch,
    cancelMatchmaking,
    getGameModes,
    getOnlinePlayers
  } = useLobbyStore()
  const { addNotification } = useUIStore()
  
  const [matchStatus, setMatchStatus] = useState<MatchStatus | null>(null)

  const [selectedMode, setSelectedMode] = useState<string>('ranked')
  const [gameModes, setGameModes] = useState<GameMode[]>([])
  const [onlinePlayers, setOnlinePlayers] = useState<OnlinePlayer[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [searchStartTime, setSearchStartTime] = useState<Date | null>(null)
  const [estimatedWaitTime, setEstimatedWaitTime] = useState(0)

  // 获取游戏模式
  useEffect(() => {
    const fetchGameModes = async () => {
      try {
        const modes = await getGameModes()
        setGameModes(modes)
      } catch (error) {
        console.error('Failed to fetch game modes:', error)
        // 使用默认游戏模式
        setGameModes([
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
        ])
      }
    }

    fetchGameModes()
  }, [getGameModes])

  // 获取在线玩家
  useEffect(() => {
    const fetchOnlinePlayers = async () => {
      try {
        const players = await getOnlinePlayers()
        setOnlinePlayers(players)
      } catch (error) {
        console.error('Failed to fetch online players:', error)
        // 使用模拟数据
        setOnlinePlayers([
          { id: '1', username: 'DragonMaster', rating: 2345, status: 'online' },
          { id: '2', username: 'NinjaWarrior', rating: 2189, status: 'ingame' },
          { id: '3', username: 'MageKing', rating: 1987, status: 'waiting' },
          { id: '4', username: 'CardHunter', rating: 2100, status: 'online' },
          { id: '5', username: 'StormCaller', rating: 2234, status: 'online' }
        ])
      }
    }

    fetchOnlinePlayers()

    // 设置定时更新
    const interval = setInterval(fetchOnlinePlayers, 30000) // 每30秒更新一次
    return () => clearInterval(interval)
  }, [getOnlinePlayers])

  // 监听匹配状态变化
  useEffect(() => {
    if (matchStatus?.found) {
      addNotification('success', '匹配成功！正在进入游戏...')
      navigate('/game')
    }

    if (matchStatus?.status === 'searching' && !searchStartTime) {
      setSearchStartTime(new Date())
      setIsSearching(true)
    }

    if (matchStatus?.status === 'idle' && searchStartTime) {
      setSearchStartTime(null)
      setIsSearching(false)
    }
  }, [matchStatus, searchStartTime, navigate, addNotification])

  // 更新等待时间
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isSearching && searchStartTime) {
      interval = setInterval(() => {
        const elapsed = Math.floor((new Date().getTime() - searchStartTime.getTime()) / 1000)
        const minutes = Math.floor(elapsed / 60)
        const seconds = elapsed % 60
        setEstimatedWaitTime(minutes * 60 + seconds)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isSearching, searchStartTime])

  const handleStartMatchmaking = async () => {
    try {
      const mode = gameModes.find(m => m.id === selectedMode)
      if (!mode) {
        addNotification('error', '请选择一个游戏模式')
        return
      }

      await findMatch(selectedMode)
      addNotification('info', `正在为您匹配${mode.name}对手...`)
    } catch (error) {
      console.error('Failed to start matchmaking:', error)
      addNotification('error', '开始匹配失败，请稍后重试')
    }
  }

  const handleCancelMatchmaking = async () => {
    try {
      await cancelMatchmaking()
      addNotification('info', '已取消匹配')
    } catch (error) {
      console.error('Failed to cancel matchmaking:', error)
      addNotification('error', '取消匹配失败')
    }
  }

  const formatWaitTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-400'
      case 'ingame':
        return 'bg-red-400'
      case 'waiting':
        return 'bg-yellow-400'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return '在线'
      case 'ingame':
        return '游戏中'
      case 'waiting':
        return '等待中'
      default:
        return '离线'
    }
  }

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">游戏大厅</h1>
          <p className="text-gray-400">
            选择游戏模式，开始您的卡牌对战之旅
          </p>
        </div>

        {/* 匹配状态 */}
        {isSearching && (
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                <div>
                  <h2 className="text-xl font-semibold text-white">正在匹配中...</h2>
                  <p className="text-primary-100">
                    等待时间：{formatWaitTime(estimatedWaitTime)}
                  </p>
                </div>
              </div>
              <Button
                onClick={handleCancelMatchmaking}
                variant="outline"
                className="bg-red-600 hover:bg-red-700 text-white border-red-500"
              >
                <XMarkIcon className="h-4 w-4 mr-2" />
                取消匹配
              </Button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 游戏模式选择 */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold text-white mb-4">选择游戏模式</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {gameModes.map((mode) => {
                // 根据模式ID选择图标
                let IconComponent;
                switch (mode.id) {
                  case 'ranked':
                    IconComponent = TrophyIcon;
                    break;
                  case 'casual':
                    IconComponent = PlayIcon;
                    break;
                  case 'practice':
                    IconComponent = Cog6ToothIcon;
                    break;
                  default:
                    IconComponent = StarIcon;
                }
                
                return (
                  <div
                    key={mode.id}
                    className={`
                      relative rounded-lg border-2 p-6 cursor-pointer transition-all duration-200
                      ${selectedMode === mode.id
                        ? 'border-primary-500 bg-primary-900/20'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                      }
                    `}
                    onClick={() => !isSearching && setSelectedMode(mode.id)}
                  >
                    {mode.isRecommended && (
                      <span className="absolute top-2 right-2 bg-yellow-500 text-gray-900 text-xs px-2 py-1 rounded-full font-medium">
                        推荐
                      </span>
                    )}

                    <div className="flex items-center space-x-3 mb-3">
                      <IconComponent className="h-8 w-8 text-primary-400" />
                      <h3 className="text-lg font-semibold text-white">
                        {mode.name}
                      </h3>
                    </div>

                    <p className="text-gray-400 text-sm mb-4">
                      {mode.description}
                    </p>

                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <UserGroupIcon className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-400">{mode.playerCount}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <ClockIcon className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-400">{mode.avgWaitTime}</span>
                        </div>
                      </div>

                      {selectedMode === mode.id && (
                        <CheckIcon className="h-5 w-5 text-primary-400" />
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* 开始匹配按钮 */}
            <div className="mt-6">
              <Button
                onClick={handleStartMatchmaking}
                disabled={isSearching || !selectedMode}
                className="w-full lg:w-auto px-8 py-3"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    匹配中...
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-5 w-5 mr-2" />
                    开始匹配
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* 在线玩家列表 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">在线玩家</h2>
              <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                {onlinePlayers.length} 人在线
              </span>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700">
              {onlinePlayers.length > 0 ? (
                <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
                  {onlinePlayers.map((player) => (
                    <div key={player.id} className="p-4 hover:bg-gray-750 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="relative">
                            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                              <span className="text-white text-sm font-medium">
                                {player.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full ${getStatusColor(player.status)}`}></div>
                          </div>
                          <div>
                            <p className="text-white font-medium">{player.username}</p>
                            <p className="text-gray-400 text-sm">
                              等级 {player.rating}
                            </p>
                          </div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          player.status === 'online' ? 'bg-green-900/20 text-green-400' :
                          player.status === 'ingame' ? 'bg-red-900/20 text-red-400' :
                          'bg-yellow-900/20 text-yellow-400'
                        }`}>
                          {getStatusText(player.status)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <UserGroupIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">暂无在线玩家</p>
                </div>
              )}
            </div>

            {/* 快速提示 */}
            <div className="mt-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-medium mb-2">快速提示</h3>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• 天梯对战会影响您的排名</li>
                <li>• 休闲对战不影响排位</li>
                <li>• 练习模式可以与AI对战</li>
                <li>• 确保您的卡组配置完整</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default LobbyPage