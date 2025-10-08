import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Button } from '@/components/ui/Button'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import { useWebSocket } from '@/hooks/useWebSocket'
import type { GameMode, Deck, UserMatchStatusResponse } from '@/types/matchmaking'

interface MatchLobbyProps {
  userDecks: Deck[]
  onMatchFound: (matchId: string) => void
  onSpectateMatch: (matchId: string) => void
  className?: string
}

export const MatchLobby: React.FC<MatchLobbyProps> = ({
  userDecks,
  onMatchFound,
  onSpectateMatch,
  className,
}) => {
  const [selectedMode, setSelectedMode] = useState<GameMode>('ranked')
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null)
  const [matchStatus, setMatchStatus] = useState<UserMatchStatusResponse | null>(null)
  const [queueStatus, setQueueStatus] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [searchTime, setSearchTime] = useState(0)
  const [error, setError] = useState('')
  const [showPreferences, setShowPreferences] = useState(false)

  const ws = useWebSocket('/api/matchmaking/ws')

  // WebSocket消息处理
  useEffect(() => {
    if (!ws) return

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        switch (message.type) {
          case 'match_found':
            handleMatchFound(message)
            break
          case 'match_cancelled':
            handleMatchCancelled(message)
            break
          case 'queue_update':
            setQueueStatus(message)
            break
          case 'status_update':
            setMatchStatus(message.data)
            break
          case 'pong':
            // 心跳响应
            break
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
  }, [ws])

  // 定时发送心跳
  useEffect(() => {
    if (!ws || !isSearching) return

    const interval = setInterval(() => {
      ws.send(JSON.stringify({ type: 'ping' }))
    }, 30000) // 每30秒发送一次心跳

    return () => clearInterval(interval)
  }, [ws, isSearching])

  // 更新搜索时间
  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isSearching && matchStatus?.wait_time) {
      interval = setInterval(() => {
        setSearchTime(Math.floor(matchStatus.wait_time))
      }, 1000)
    }

    return () => clearInterval(interval)
  }, [isSearching, matchStatus])

  // 获取初始状态
  useEffect(() => {
    fetchMatchStatus()
    fetchQueueStatus()
  }, [])

  const fetchMatchStatus = async () => {
    try {
      const response = await fetch('/api/matchmaking/status')
      const status = await response.json()
      setMatchStatus(status)

      if (status.in_queue) {
        setIsSearching(true)
        setSelectedMode(status.mode)
      }
    } catch (error) {
      console.error('Failed to fetch match status:', error)
    }
  }

  const fetchQueueStatus = async () => {
    try {
      const response = await fetch('/api/matchmaking/queues/status')
      const status = await response.json()
      setQueueStatus(status)
    } catch (error) {
      console.error('Failed to fetch queue status:', error)
    }
  }

  const handleStartMatching = async () => {
    if (!selectedDeck) {
      setError('请选择一个卡组')
      return
    }

    setError('')
    setIsSearching(true)

    try {
      const response = await fetch('/api/matchmaking/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode: selectedMode,
          deck_id: selectedDeck,
          preferences: {
            max_wait_time: 300,
            rating_tolerance: 200
          }
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start matchmaking')
      }

      const result = await response.json()
      setMatchStatus(result)
    } catch (error) {
      console.error('Failed to start matchmaking:', error)
      setError('开始匹配失败，请重试')
      setIsSearching(false)
    }
  }

  const handleCancelMatching = async () => {
    try {
      await fetch('/api/matchmaking/request', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: selectedMode }),
      })

      setIsSearching(false)
      setSearchTime(0)
      await fetchMatchStatus()
    } catch (error) {
      console.error('Failed to cancel matchmaking:', error)
    }
  }

  const handleMatchFound = (message: any) => {
    setIsSearching(false)
    setSearchTime(0)
    onMatchFound(message.match.match_id)
  }

  const handleMatchCancelled = (message: any) => {
    setIsSearching(false)
    setSearchTime(0)
    setError(message.reason || '匹配已取消')
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getModeLabel = (mode: GameMode) => {
    const labels = {
      ranked: '天梯',
      casual: '休闲',
      practice: '练习',
      tournament: '锦标赛',
      friendly: '友谊赛'
    }
    return labels[mode] || mode
  }

  const getModeColor = (mode: GameMode) => {
    const colors = {
      ranked: 'bg-orange-600',
      casual: 'bg-blue-600',
      practice: 'bg-green-600',
      tournament: 'bg-purple-600',
      friendly: 'bg-pink-600'
    }
    return colors[mode] || 'bg-gray-600'
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 20
      }
    }
  }

  if (isSearching && matchStatus) {
    return (
      <motion.div
        className={cn('min-h-screen bg-gray-900 text-white flex items-center justify-center', className)}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          className="text-center space-y-8 max-w-md"
          variants={itemVariants}
        >
          {/* 搜索动画 */}
          <div className="relative w-32 h-32 mx-auto">
            <motion.div
              className="absolute inset-0 border-4 border-blue-500 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
            <motion.div
              className="absolute inset-2 border-4 border-purple-500 rounded-full"
              animate={{ rotate: -360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
            />
            <motion.div
              className="absolute inset-4 border-4 border-pink-500 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />

            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-2xl font-bold">
                {Math.floor(searchTime % 60)}s
              </div>
            </div>
          </div>

          {/* 搜索状态 */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">
              正在搜索对手...
            </h2>

            <div className="flex items-center justify-center space-x-4 text-sm text-gray-400">
              <span>模式: {getModeLabel(selectedMode)}</span>
              <span>等待时间: {formatTime(Math.floor(searchTime))}</span>
            </div>

            {/* 队列信息 */}
            {queueStatus && queueStatus[selectedMode] && (
              <div className="bg-gray-800 rounded-lg p-4 space-y-2">
                <div className="text-sm text-gray-400">
                  当前队列: {queueStatus[selectedMode].queue_length} 人
                </div>
                <div className="text-sm text-gray-400">
                  平均等待: {formatTime(Math.floor(queueStatus[selectedMode].average_wait_time))}
                </div>
              </div>
            )}

            {/* 取消按钮 */}
            <Button
              variant="outline"
              onClick={handleCancelMatching}
              className="mt-4"
            >
              取消匹配
            </Button>
          </div>
        </motion.div>
      </motion.div>
    )
  }

  return (
    <motion.div
      className={cn('min-h-screen bg-gray-900 text-white p-6', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 顶部标题 */}
      <motion.div
        className="text-center mb-8"
        variants={itemVariants}
      >
        <h1 className="text-4xl font-bold mb-2">对战大厅</h1>
        <p className="text-gray-400">选择游戏模式和卡组，开始匹配对战</p>
      </motion.div>

      {/* 错误信息 */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="bg-red-900 bg-opacity-50 border border-red-600 rounded-lg p-4 mb-6 text-red-300"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {/* 游戏模式选择 */}
        <motion.div
          className="bg-gray-800 rounded-lg p-6"
          variants={itemVariants}
        >
          <h2 className="text-xl font-semibold mb-4">游戏模式</h2>
          <div className="space-y-3">
            {(['ranked', 'casual', 'practice', 'tournament', 'friendly'] as GameMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setSelectedMode(mode)}
                className={cn(
                  'w-full p-4 rounded-lg text-left transition-colors',
                  selectedMode === mode
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{getModeLabel(mode)}</div>
                    <div className="text-sm opacity-75">
                      {mode === 'ranked' && '影响段位和积分'}
                      {mode === 'casual' && '轻松休闲对局'}
                      {mode === 'practice' && '与AI对战练习'}
                      {mode === 'tournament' && '官方锦标赛'}
                      {mode === 'friendly' && '与好友切磋'}
                    </div>
                  </div>
                  <div className={cn('w-3 h-3 rounded-full', getModeColor(mode))} />
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* 卡组选择 */}
        <motion.div
          className="bg-gray-800 rounded-lg p-6"
          variants={itemVariants}
        >
          <h2 className="text-xl font-semibold mb-4">选择卡组</h2>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {userDecks.map((deck) => (
              <button
                key={deck.id}
                onClick={() => setSelectedDeck(deck.id)}
                className={cn(
                  'w-full p-3 rounded-lg text-left transition-colors',
                  selectedDeck === deck.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                )}
              >
                <div className="font-medium">{deck.name}</div>
                <div className="text-sm opacity-75">
                  {deck.card_class} • {deck.cards.length}种卡牌
                </div>
                <div className="text-sm opacity-75">
                  胜率: {(deck.win_rate * 100).toFixed(1)}% • {deck.games_played}场
                </div>
              </button>
            ))}
          </div>

          {userDecks.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              你还没有创建任何卡组
            </div>
          )}
        </motion.div>

        {/* 队列状态和开始匹配 */}
        <motion.div
          className="bg-gray-800 rounded-lg p-6"
          variants={itemVariants}
        >
          <h2 className="text-xl font-semibold mb-4">队列状态</h2>

          {queueStatus && (
            <div className="space-y-4 mb-6">
              {(['ranked', 'casual', 'practice'] as GameMode[]).map((mode) => (
                <div key={mode} className="bg-gray-700 rounded p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">{getModeLabel(mode)}</span>
                    <span className="text-white font-medium">
                      {queueStatus[mode]?.queue_length || 0} 人
                    </span>
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    平均等待: {formatTime(Math.floor(queueStatus[mode]?.average_wait_time || 0))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <Button
            onClick={handleStartMatching}
            disabled={!selectedDeck || !selectedMode}
            className="w-full py-3 text-lg"
          >
            开始匹配
          </Button>

          {/* 匹配偏好设置 */}
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            className="w-full mt-4 text-sm text-gray-400 hover:text-gray-300"
          >
            {showPreferences ? '隐藏' : '显示'}高级设置
          </button>

          <AnimatePresence>
            {showPreferences && (
              <motion.div
                className="mt-4 p-4 bg-gray-700 rounded-lg space-y-3"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <div>
                  <label className="block text-sm text-gray-300 mb-1">
                    最大等待时间
                  </label>
                  <select className="w-full bg-gray-600 text-white px-3 py-2 rounded">
                    <option value="60">1分钟</option>
                    <option value="180">3分钟</option>
                    <option value="300">5分钟</option>
                    <option value="600">10分钟</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-300 mb-1">
                    ELO容忍度
                  </label>
                  <select className="w-full bg-gray-600 text-white px-3 py-2 rounded">
                    <option value="100">严格 (±100)</option>
                    <option value="200">标准 (±200)</option>
                    <option value="400">宽松 (±400)</option>
                    <option value="999">无限制</option>
                  </select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* 观战模式 */}
      <motion.div
        className="mt-8 text-center"
        variants={itemVariants}
      >
        <p className="text-gray-400 mb-4">想要观看高手对战？</p>
        <Button variant="outline" onClick={() => onSpectateMatch('')}>
          进入观战模式
        </Button>
      </motion.div>
    </motion.div>
  )
}

export default MatchLobby