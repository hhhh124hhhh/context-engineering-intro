import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useGameStore } from '@stores/gameStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  PlayIcon,
  UserGroupIcon,
  DocumentTextIcon,
  TrophyIcon,
  ChartBarIcon,
  SparklesIcon,
  FireIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/react/24/outline'

export const HomePage: React.FC = () => {
  const { user } = useAuthStore()
  const { getGameStats } = useGameStore()
  const { addNotification } = useUIStore()

  const [gameStats, setGameStats] = useState<any>(null)
  const [recentGames, setRecentGames] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // 获取游戏统计数据
  useEffect(() => {
    const fetchGameStats = async () => {
      try {
        const stats = await getGameStats()
        setGameStats(stats)
      } catch (error) {
        console.error('Failed to fetch game stats:', error)
        addNotification('error', '获取游戏统计数据失败')
      } finally {
        setIsLoading(false)
      }
    }

    fetchGameStats()
  }, [getGameStats, addNotification])

  // 模拟最近游戏数据
  useEffect(() => {
    // 这里应该从API获取真实的最近游戏数据
    const mockRecentGames = [
      {
        id: '1',
        opponent: 'Player123',
        result: 'victory',
        duration: '12:34',
        date: '2024-01-15',
        rating: '+15'
      },
      {
        id: '2',
        opponent: 'DragonMaster',
        result: 'defeat',
        duration: '8:56',
        date: '2024-01-15',
        rating: '-12'
      },
      {
        id: '3',
        opponent: 'NinjaWarrior',
        result: 'victory',
        duration: '15:23',
        date: '2024-01-14',
        rating: '+18'
      }
    ]
    setRecentGames(mockRecentGames)
  }, [])

  const quickActions = [
    {
      name: '快速对战',
      description: '立即开始匹配对手',
      icon: PlayIcon,
      href: '/lobby',
      color: 'bg-green-600 hover:bg-green-700',
      primary: true
    },
    {
      name: '卡组管理',
      description: '编辑和管理您的卡组',
      icon: DocumentTextIcon,
      href: '/deck',
      color: 'bg-blue-600 hover:bg-blue-700',
      primary: false
    },
    {
      name: '排行榜',
      description: '查看全球玩家排名',
      icon: TrophyIcon,
      href: '/leaderboard',
      color: 'bg-yellow-600 hover:bg-yellow-700',
      primary: false
    },
    {
      name: '游戏统计',
      description: '查看您的战绩和统计',
      icon: ChartBarIcon,
      href: '/stats',
      color: 'bg-purple-600 hover:bg-purple-700',
      primary: false
    }
  ]

  const gameStatsCards = [
    {
      title: '总胜率',
      value: gameStats?.winRate || '65.2%',
      icon: TrophyIcon,
      color: 'text-green-400',
      bgColor: 'bg-green-900/20'
    },
    {
      title: '当前排名',
      value: `#${gameStats?.rank || '1,234'}`,
      icon: StarIcon,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-900/20'
    },
    {
      title: '总场次',
      value: gameStats?.totalGames || '156',
      icon: PlayIcon,
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/20'
    },
    {
      title: '连胜场次',
      value: gameStats?.winStreak || '3',
      icon: FireIcon,
      color: 'text-red-400',
      bgColor: 'bg-red-900/20'
    }
  ]

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 欢迎横幅 */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                欢迎回来，{user?.username || '玩家'}！
              </h1>
              <p className="text-primary-100 text-lg">
                准备好在卡牌竞技场中取得胜利了吗？
              </p>
            </div>
            <div className="hidden lg:block">
              <SparklesIcon className="h-16 w-16 text-primary-200" />
            </div>
          </div>
        </div>

        {/* 快速操作 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">快速开始</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className={`
                  relative overflow-hidden rounded-lg p-6 transition-all duration-200
                  ${action.primary
                    ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800'
                    : action.color
                  }
                  ${action.primary ? 'ring-2 ring-green-500 ring-offset-2 ring-offset-gray-900' : ''}
                `}
              >
                <div className="flex items-center justify-between mb-3">
                  <action.icon className="h-8 w-8 text-white" />
                  {action.primary && (
                    <span className="bg-white/20 text-white text-xs px-2 py-1 rounded-full">
                      推荐
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">
                  {action.name}
                </h3>
                <p className="text-white/80 text-sm">
                  {action.description}
                </p>
              </Link>
            ))}
          </div>
        </div>

        {/* 游戏统计 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">您的游戏统计</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-gray-800 rounded-lg p-6 animate-pulse">
                  <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-700 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {gameStatsCards.map((stat, index) => (
                <div key={index} className={`${stat.bgColor} rounded-lg p-6 border border-gray-700`}>
                  <div className="flex items-center justify-between mb-3">
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                    <span className={`text-xs font-medium ${stat.color}`}>
                      {stat.title}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 最近游戏 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold text-white mb-4">最近对战</h2>
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              {recentGames.length > 0 ? (
                <div className="divide-y divide-gray-700">
                  {recentGames.map((game) => (
                    <div key={game.id} className="p-4 hover:bg-gray-750 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-2 h-2 rounded-full ${
                            game.result === 'victory' ? 'bg-green-400' : 'bg-red-400'
                          }`}></div>
                          <div>
                            <p className="text-white font-medium">
                              对战 {game.opponent}
                            </p>
                            <div className="flex items-center space-x-2 text-sm text-gray-400">
                              <ClockIcon className="h-3 w-3" />
                              <span>{game.duration}</span>
                              <span>•</span>
                              <span>{game.date}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            game.result === 'victory'
                              ? 'bg-green-900/20 text-green-400'
                              : 'bg-red-900/20 text-red-400'
                          }`}>
                            {game.result === 'victory' ? '胜利' : '失败'}
                          </span>
                          <p className={`text-sm font-medium mt-1 ${
                            game.rating.startsWith('+') ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {game.rating}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <PlayIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">您还没有进行任何对战</p>
                  <p className="text-gray-500 text-sm mt-1">
                    前往游戏大厅开始您的第一场对战吧！
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 系统公告 */}
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">系统公告</h2>
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-yellow-400 mt-2"></div>
                  <div>
                    <p className="text-white font-medium">新卡包上线</p>
                    <p className="text-gray-400 text-sm mt-1">
                      龙之传说卡包现已上线，包含5张全新的传说级卡牌！
                    </p>
                    <p className="text-gray-500 text-xs mt-2">2024-01-15</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400 mt-2"></div>
                  <div>
                    <p className="text-white font-medium">平衡性调整</p>
                    <p className="text-gray-400 text-sm mt-1">
                      部分卡牌效果已进行调整，请查看详细说明。
                    </p>
                    <p className="text-gray-500 text-xs mt-2">2024-01-14</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-400 mt-2"></div>
                  <div>
                    <p className="text-white font-medium">服务器维护</p>
                    <p className="text-gray-400 text-sm mt-1">
                      本周三凌晨2点进行服务器维护，预计1小时。
                    </p>
                    <p className="text-gray-500 text-xs mt-2">2024-01-13</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-700">
                <Link
                  to="/announcements"
                  className="text-primary-400 hover:text-primary-300 text-sm font-medium"
                >
                  查看全部公告 →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default HomePage