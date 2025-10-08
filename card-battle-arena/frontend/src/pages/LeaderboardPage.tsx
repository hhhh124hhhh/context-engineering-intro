import React, { useEffect, useState } from 'react'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  TrophyIcon,
  StarIcon,
  UserGroupIcon,
  ChartBarIcon,
  SparklesIcon,
  UserIcon
} from '@heroicons/react/24/outline'

interface LeaderboardPlayer {
  rank: number
  id: string
  username: string
  rating: number
  rankTier: string
  wins: number
  losses: number
  winRate: number
  trend: 'up' | 'down' | 'stable'
  avatar?: string
}

export const LeaderboardPage: React.FC = () => {
  const { addNotification } = useUIStore()

  const [selectedTab, setSelectedTab] = useState<'global' | 'friends' | 'weekly'>('global')
  const [leaderboard, setLeaderboard] = useState<LeaderboardPlayer[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        // 这里应该调用API获取排行榜数据
        // 暂时使用模拟数据
        const mockLeaderboard: LeaderboardPlayer[] = [
          {
            rank: 1,
            id: '1',
            username: 'DragonMaster',
            rating: 2845,
            rankTier: 'grandmaster',
            wins: 234,
            losses: 45,
            winRate: 83.9,
            trend: 'up'
          },
          {
            rank: 2,
            id: '2',
            username: 'NinjaWarrior',
            rating: 2768,
            rankTier: 'grandmaster',
            wins: 198,
            losses: 52,
            winRate: 79.2,
            trend: 'stable'
          },
          {
            rank: 3,
            id: '3',
            username: 'MageKing',
            rating: 2690,
            rankTier: 'master',
            wins: 167,
            losses: 48,
            winRate: 77.7,
            trend: 'down'
          },
          {
            rank: 4,
            id: '4',
            username: 'CardHunter',
            rating: 2654,
            rankTier: 'master',
            wins: 189,
            losses: 67,
            winRate: 73.8,
            trend: 'up'
          },
          {
            rank: 5,
            id: '5',
            username: 'StormCaller',
            rating: 2623,
            rankTier: 'master',
            wins: 156,
            losses: 59,
            winRate: 72.6,
            trend: 'stable'
          },
          {
            rank: 6,
            id: '6',
            username: 'ShadowNinja',
            rating: 2598,
            rankTier: 'diamond',
            wins: 145,
            losses: 62,
            winRate: 70.1,
            trend: 'up'
          },
          {
            rank: 7,
            id: '7',
            username: 'FireMage',
            rating: 2576,
            rankTier: 'diamond',
            wins: 178,
            losses: 84,
            winRate: 67.9,
            trend: 'down'
          },
          {
            rank: 8,
            id: '8',
            username: 'IceQueen',
            rating: 2543,
            rankTier: 'diamond',
            wins: 134,
            losses: 71,
            winRate: 65.4,
            trend: 'stable'
          }
        ]

        setLeaderboard(mockLeaderboard)
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error)
        addNotification('error', '获取排行榜数据失败')
      } finally {
        setIsLoading(false)
      }
    }

    fetchLeaderboard()
  }, [addNotification])

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <StarIcon className="h-6 w-6 text-yellow-400" />
      case 2:
        return <TrophyIcon className="h-6 w-6 text-gray-300" />
      case 3:
        return <SparklesIcon className="h-6 w-6 text-orange-400" />
      default:
        return <span className="text-lg font-bold text-gray-400">#{rank}</span>
    }
  }

  const getRankTierColor = (tier: string) => {
    switch (tier) {
      case 'grandmaster':
        return 'text-red-600 bg-red-900/20'
      case 'master':
        return 'text-red-400 bg-red-900/20'
      case 'diamond':
        return 'text-purple-400 bg-purple-900/20'
      case 'platinum':
        return 'text-cyan-400 bg-cyan-900/20'
      case 'gold':
        return 'text-yellow-400 bg-yellow-900/20'
      case 'silver':
        return 'text-gray-300 bg-gray-700/20'
      case 'bronze':
        return 'text-orange-400 bg-orange-900/20'
      default:
        return 'text-gray-400 bg-gray-700/20'
    }
  }

  const getRankTierText = (tier: string) => {
    switch (tier) {
      case 'grandmaster':
        return '宗师'
      case 'master':
        return '大师'
      case 'diamond':
        return '钻石'
      case 'platinum':
        return '铂金'
      case 'gold':
        return '黄金'
      case 'silver':
        return '白银'
      case 'bronze':
        return '青铜'
      default:
        return '未知'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <span className="text-green-400">↑</span>
      case 'down':
        return <span className="text-red-400">↓</span>
      default:
        return <span className="text-gray-400">—</span>
    }
  }

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">排行榜</h1>
          <p className="text-gray-400">
            查看全球顶尖玩家的排名和战绩
          </p>
        </div>

        {/* 排行榜选项卡 */}
        <div className="flex space-x-1 mb-8 bg-gray-800 rounded-lg p-1 border border-gray-700">
          <Button
            onClick={() => setSelectedTab('global')}
            className={`flex-1 ${
              selectedTab === 'global'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
            variant="ghost"
          >
            <TrophyIcon className="h-5 w-5 mr-2" />
            全球排行榜
          </Button>
          <Button
            onClick={() => setSelectedTab('friends')}
            className={`flex-1 ${
              selectedTab === 'friends'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
            variant="ghost"
          >
            <UserGroupIcon className="h-5 w-5 mr-2" />
            好友排行
          </Button>
          <Button
            onClick={() => setSelectedTab('weekly')}
            className={`flex-1 ${
              selectedTab === 'weekly'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
            variant="ghost"
          >
            <ChartBarIcon className="h-5 w-5 mr-2" />
            本周排行
          </Button>
        </div>

        {isLoading ? (
          <div className="animate-pulse space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="bg-gray-800 rounded-lg p-4 h-20"></div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            {leaderboard.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700 border-b border-gray-600">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        排名
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        玩家
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        段位
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        积分
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        胜/负
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        胜率
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                        趋势
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {leaderboard.map((player) => (
                      <tr key={player.id} className="hover:bg-gray-750 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center justify-center">
                            {getRankIcon(player.rank)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white text-sm font-medium">
                                {player.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <span className="text-white font-medium">
                              {player.username}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRankTierColor(player.rankTier)}`}>
                            {getRankTierText(player.rankTier)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-white font-medium">
                            {player.rating}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-gray-300 text-sm">
                            {player.wins}/{player.losses}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${
                            player.winRate >= 70 ? 'text-green-400' :
                            player.winRate >= 60 ? 'text-yellow-400' :
                            'text-gray-400'
                          }`}>
                            {player.winRate}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center justify-center">
                            {getTrendIcon(player.trend)}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <TrophyIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 text-lg">
                  {selectedTab === 'friends' ? '添加好友查看好友排行榜' :
                   selectedTab === 'weekly' ? '本周排行数据暂未生成' :
                   '暂无排行榜数据'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* 排行榜说明 */}
        <div className="mt-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">排行榜说明</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-white font-medium mb-2">段位系统</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• 宗师：2700+ 积分</li>
                <li>• 大师：2400-2699 积分</li>
                <li>• 钻石：2100-2399 积分</li>
                <li>• 铂金：1800-2099 积分</li>
                <li>• 黄金：1500-1799 积分</li>
                <li>• 白银：1200-1499 积分</li>
                <li>• 青铜：0-1199 积分</li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-medium mb-2">排名规则</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• 排名根据积分排序</li>
                <li>• 积分相同时按胜率排序</li>
                <li>• 胜率相同按总场次排序</li>
                <li>• 每天凌晨2点更新排名</li>
                <li>• 赛季结束时发放奖励</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default LeaderboardPage