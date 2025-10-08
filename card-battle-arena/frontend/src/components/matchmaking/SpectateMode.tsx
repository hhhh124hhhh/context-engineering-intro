import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Button } from '@/components/ui/Button'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import type { GameMode, Match } from '@/types/matchmaking'

interface SpectateModeProps {
  onExitSpectate: () => void
  onJoinSpectate: (matchId: string) => void
  className?: string
}

export const SpectateMode: React.FC<SpectateModeProps> = ({
  onExitSpectate,
  onJoinSpectate,
  className,
}) => {
  const [availableMatches, setAvailableMatches] = useState<Match[]>([])
  const [selectedMode, setSelectedMode] = useState<GameMode>('ranked')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchAvailableMatches()
  }, [selectedMode])

  const fetchAvailableMatches = async () => {
    try {
      setLoading(true)
      setError('')

      // 这里应该调用实际的API获取可观战的比赛
      // 暂时使用模拟数据
      const mockMatches: Match[] = [
        {
          match_id: 'match_1',
          player1_id: 1,
          player2_id: 2,
          player1_username: 'ProPlayer1',
          player2_username: 'MasterDuelist',
          mode: 'ranked',
          deck1_id: 1,
          deck2_id: 2,
          created_at: Date.now() / 1000,
          status: 'game_started'
        },
        {
          match_id: 'match_2',
          player1_id: 3,
          player2_id: 4,
          player1_username: 'CardNinja',
          player2_username: 'StrategicMind',
          mode: 'casual',
          deck1_id: 3,
          deck2_id: 4,
          created_at: Date.now() / 1000,
          status: 'game_started'
        }
      ]

      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000))

      setAvailableMatches(mockMatches.filter(match => match.mode === selectedMode))
    } catch (error) {
      console.error('Failed to fetch available matches:', error)
      setError('获取比赛列表失败')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchAvailableMatches()
  }

  const handleJoinSpectate = (matchId: string) => {
    onJoinSpectate(matchId)
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

  const formatGameTime = (startTime: number) => {
    const elapsed = Math.floor(Date.now() / 1000 - startTime)
    const mins = Math.floor(elapsed / 60)
    const secs = elapsed % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const filteredMatches = availableMatches.filter(match => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      match.player1_username.toLowerCase().includes(query) ||
      match.player2_username.toLowerCase().includes(query)
    )
  })

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

  if (loading) {
    return <LoadingScreen message="加载比赛列表..." />
  }

  return (
    <motion.div
      className={cn('min-h-screen bg-gray-900 text-white p-6', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 顶部标题和控制 */}
      <motion.div
        className="flex items-center justify-between mb-8"
        variants={itemVariants}
      >
        <div>
          <h1 className="text-4xl font-bold mb-2">观战模式</h1>
          <p className="text-gray-400">观看其他玩家的精彩对局</p>
        </div>

        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={onExitSpectate}>
            返回大厅
          </Button>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? '刷新中...' : '刷新列表'}
          </Button>
        </div>
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

      {/* 筛选和搜索 */}
      <motion.div
        className="bg-gray-800 rounded-lg p-6 mb-8"
        variants={itemVariants}
      >
        <div className="flex flex-col md:flex-row gap-4">
          {/* 游戏模式筛选 */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              游戏模式
            </label>
            <div className="flex flex-wrap gap-2">
              {(['ranked', 'casual', 'tournament', 'friendly'] as GameMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setSelectedMode(mode)}
                  className={cn(
                    'px-4 py-2 rounded-lg transition-colors',
                    selectedMode === mode
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  )}
                >
                  {getModeLabel(mode)}
                </button>
              ))}
            </div>
          </div>

          {/* 搜索框 */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              搜索玩家
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="输入玩家名称..."
              className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {/* 统计信息 */}
        <div className="mt-4 flex items-center justify-between text-sm text-gray-400">
          <span>
            找到 {filteredMatches.length} 场比赛
          </span>
          <span>
            当前模式: {getModeLabel(selectedMode)}
          </span>
        </div>
      </motion.div>

      {/* 比赛列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredMatches.map((match) => (
            <motion.div
              key={match.match_id}
              className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-gray-600 transition-colors"
              variants={itemVariants}
              layout
              exit={{ scale: 0.8, opacity: 0 }}
              whileHover={{ y: -4 }}
            >
              {/* 比赛头部 */}
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <div className={cn('px-2 py-1 rounded text-xs text-white', getModeColor(match.mode))}>
                    {getModeLabel(match.mode)}
                  </div>
                  <div className="text-sm text-gray-400">
                    {formatGameTime(match.created_at)}
                  </div>
                </div>

                {/* 对战玩家 */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {match.player1_username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-white font-medium">
                          {match.player1_username}
                        </div>
                        <div className="text-xs text-gray-400">
                          玩家 {match.player1_id}
                        </div>
                      </div>
                    </div>
                    <div className="text-2xl text-gray-500">VS</div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {match.player2_username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-white font-medium">
                          {match.player2_username}
                        </div>
                        <div className="text-xs text-gray-400">
                          玩家 {match.player2_id}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 观战信息 */}
              <div className="p-4 bg-gray-750">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm text-gray-400">
                    观战人数: {Math.floor(Math.random() * 50)} {/* 模拟观战人数 */}
                  </div>
                  <div className="text-xs text-green-400">
                    ● 进行中
                  </div>
                </div>

                <Button
                  onClick={() => handleJoinSpectate(match.match_id)}
                  className="w-full"
                  size="sm"
                >
                  进入观战
                </Button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 空状态 */}
      <AnimatePresence>
        {filteredMatches.length === 0 && !loading && (
          <motion.div
            className="text-center py-16"
            variants={itemVariants}
          >
            <div className="text-gray-500 mb-4">
              {searchQuery ? '没有找到匹配的比赛' : '当前没有可观战的比赛'}
            </div>
            {!searchQuery && (
              <Button variant="outline" onClick={handleRefresh}>
                刷新页面
              </Button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 观战说明 */}
      <motion.div
        className="mt-8 bg-gray-800 rounded-lg p-6"
        variants={itemVariants}
      >
        <h3 className="text-lg font-semibold text-white mb-4">观战说明</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-400">
          <div>
            <h4 className="text-white font-medium mb-2">观战规则</h4>
            <ul className="space-y-1">
              <li>• 观战者无法参与游戏操作</li>
              <li>• 可以看到双方玩家的手牌和操作</li>
              <li>• 观战时聊天功能受限</li>
              <li>• 可以随时退出观战</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-2">注意事项</h4>
            <ul className="space-y-1">
              <li>• 请尊重比赛选手，不要干扰游戏</li>
              <li>• 观战时请保持网络连接稳定</li>
              <li>• 遇到网络问题会自动断开观战</li>
              <li>• 选手可以设置禁止观战</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default SpectateMode