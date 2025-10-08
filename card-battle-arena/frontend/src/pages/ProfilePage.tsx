import React, { useEffect, useState } from 'react'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  UserIcon,
  EnvelopeIcon,
  TrophyIcon,
  ChartBarIcon,
  PencilIcon,
  ShieldCheckIcon,
  StarIcon,
  FireIcon,
  CalendarIcon,
  Cog6ToothIcon,
  CameraIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface UserProfile {
  id: string
  username: string
  email: string
  avatar?: string
  rating: number
  rank: string
  level: number
  experience: number
  totalGames: number
  wins: number
  losses: number
  winRate: number
  winStreak: number
  bestWinStreak: number
  achievements: Achievement[]
  joinDate: string
  lastLoginDate: string
}

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  unlockedAt: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

const RANK_COLORS = {
  bronze: 'text-orange-400',
  silver: 'text-gray-300',
  gold: 'text-yellow-400',
  platinum: 'text-cyan-400',
  diamond: 'text-purple-400',
  master: 'text-red-400',
  grandmaster: 'text-red-600'
}

const ACHIEVEMENT_COLORS = {
  common: 'border-gray-500 bg-gray-800',
  rare: 'border-blue-500 bg-blue-900/20',
  epic: 'border-purple-500 bg-purple-900/20',
  legendary: 'border-yellow-500 bg-yellow-900/20'
}

export const ProfilePage: React.FC = () => {
  const { user, updateProfile } = useAuthStore()
  const { addNotification } = useUIStore()

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    username: '',
    email: '',
    avatar: ''
  })
  const [isLoading, setIsLoading] = useState(true)

  // 获取用户详细信息
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // 这里应该调用API获取用户详细信息
        // 暂时使用模拟数据
        const mockProfile: UserProfile = {
          id: user?.id || '1',
          username: user?.username || 'Player',
          email: 'player@example.com',
          avatar: user?.avatar,
          rating: user?.rating || 1500,
          rank: 'gold',
          level: 42,
          experience: 6850,
          totalGames: 156,
          wins: 102,
          losses: 54,
          winRate: 65.4,
          winStreak: 3,
          bestWinStreak: 8,
          achievements: [
            {
              id: '1',
              name: '初次胜利',
              description: '赢得您的第一场对战',
              icon: '🏆',
              unlockedAt: '2024-01-10',
              rarity: 'common'
            },
            {
              id: '2',
              name: '连胜达人',
              description: '连续赢得5场对战',
              icon: '🔥',
              unlockedAt: '2024-01-12',
              rarity: 'rare'
            },
            {
              id: '3',
              name: '卡牌收藏家',
              description: '收集100张不同的卡牌',
              icon: '📚',
              unlockedAt: '2024-01-15',
              rarity: 'epic'
            },
            {
              id: '4',
              name: '竞技场大师',
              description: '达到钻石段位',
              icon: '💎',
              unlockedAt: '2024-01-18',
              rarity: 'legendary'
            }
          ],
          joinDate: '2024-01-01',
          lastLoginDate: '2024-01-20'
        }

        setProfile(mockProfile)
        setEditForm({
          username: mockProfile.username,
          email: mockProfile.email,
          avatar: mockProfile.avatar || ''
        })
      } catch (error) {
        console.error('Failed to fetch profile:', error)
        addNotification('error', '获取用户信息失败')
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfile()
  }, [user, addNotification])

  const handleUpdateProfile = async () => {
    try {
      await updateProfile(editForm)
      setIsEditing(false)
      addNotification('success', '个人资料更新成功')

      // 更新本地profile状态
      if (profile) {
        setProfile({
          ...profile,
          username: editForm.username,
          email: editForm.email,
          avatar: editForm.avatar
        })
      }
    } catch (error) {
      console.error('Failed to update profile:', error)
      addNotification('error', '更新个人资料失败')
    }
  }

  const getRankColor = (rank: string) => {
    return RANK_COLORS[rank as keyof typeof RANK_COLORS] || 'text-gray-400'
  }

  const getAchievementColor = (rarity: string) => {
    return ACHIEVEMENT_COLORS[rarity as keyof typeof ACHIEVEMENT_COLORS] || ACHIEVEMENT_COLORS.common
  }

  const getLevelProgress = (experience: number) => {
    const expPerLevel = 1000
    const currentLevelExp = experience % expPerLevel
    const progress = (currentLevelExp / expPerLevel) * 100
    return progress
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-700 rounded w-1/3 mb-8"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 h-96 bg-gray-800 rounded-lg"></div>
            <div className="lg:col-span-2 h-96 bg-gray-800 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <UserIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">无法加载用户信息</p>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">个人资料</h1>
          {!isEditing && (
            <Button
              onClick={() => setIsEditing(true)}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <PencilIcon className="h-4 w-4" />
              <span>编辑资料</span>
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 左侧：基本信息 */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              {/* 头像 */}
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="w-24 h-24 bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    {profile.avatar ? (
                      <img
                        src={profile.avatar}
                        alt="Avatar"
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <span className="text-white text-3xl font-bold">
                        {profile.username.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  {isEditing && (
                    <button className="absolute bottom-4 right-0 bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-full">
                      <CameraIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <h2 className="text-xl font-semibold text-white mb-2">
                  {profile.username}
                </h2>
                <p className={`text-sm font-medium ${getRankColor(profile.rank)}`}>
                  {profile.rank === 'bronze' ? '青铜' :
                   profile.rank === 'silver' ? '白银' :
                   profile.rank === 'gold' ? '黄金' :
                   profile.rank === 'platinum' ? '铂金' :
                   profile.rank === 'diamond' ? '钻石' :
                   profile.rank === 'master' ? '大师' : '宗师'} 段位
                </p>
              </div>

              {/* 基本信息 */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <TrophyIcon className="h-5 w-5 text-yellow-400" />
                  <div>
                    <p className="text-sm text-gray-400">等级</p>
                    <p className="text-white font-medium">Lv.{profile.level}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <StarIcon className="h-5 w-5 text-primary-400" />
                  <div>
                    <p className="text-sm text-gray-400">积分</p>
                    <p className="text-white font-medium">{profile.rating}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-400">邮箱</p>
                    <p className="text-white font-medium text-sm">{profile.email}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <CalendarIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-400">注册时间</p>
                    <p className="text-white font-medium text-sm">{profile.joinDate}</p>
                  </div>
                </div>
              </div>

              {/* 等级进度条 */}
              <div className="mt-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">等级进度</span>
                  <span className="text-white">{profile.experience}/1000</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${getLevelProgress(profile.experience)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧：统计和成就 */}
          <div className="lg:col-span-2 space-y-8">
            {/* 游戏统计 */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">游戏统计</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">{profile.totalGames}</p>
                  <p className="text-sm text-gray-400">总场次</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">{profile.wins}</p>
                  <p className="text-sm text-gray-400">胜利</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-400">{profile.losses}</p>
                  <p className="text-sm text-gray-400">失败</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary-400">{profile.winRate}%</p>
                  <p className="text-sm text-gray-400">胜率</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-2 gap-4 mt-4">
                <div className="text-center bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-center space-x-2">
                    <FireIcon className="h-5 w-5 text-orange-400" />
                    <p className="text-xl font-bold text-white">{profile.winStreak}</p>
                  </div>
                  <p className="text-sm text-gray-400">当前连胜</p>
                </div>
                <div className="text-center bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-center space-x-2">
                    <SparklesIcon className="h-5 w-5 text-yellow-400" />
                    <p className="text-xl font-bold text-white">{profile.bestWinStreak}</p>
                  </div>
                  <p className="text-sm text-gray-400">最佳连胜</p>
                </div>
              </div>
            </div>

            {/* 成就系统 */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">成就</h3>
                <span className="bg-primary-600 text-white text-xs px-2 py-1 rounded-full">
                  {profile.achievements.length} 个成就
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className={`border rounded-lg p-4 ${getAchievementColor(achievement.rarity)}`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">{achievement.icon}</div>
                      <div className="flex-1">
                        <h4 className="text-white font-medium">{achievement.name}</h4>
                        <p className="text-gray-400 text-sm mt-1">{achievement.description}</p>
                        <p className="text-gray-500 text-xs mt-2">{achievement.unlockedAt}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {profile.achievements.length === 0 && (
                <div className="text-center py-8">
                  <TrophyIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">还没有解锁任何成就</p>
                  <p className="text-gray-500 text-sm mt-1">
                    完成特定任务来解锁成就
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 编辑资料模态框 */}
        {isEditing && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsEditing(false)} />
              <div className="relative bg-gray-800 rounded-lg p-6 max-w-md w-full border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">编辑个人资料</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      用户名
                    </label>
                    <input
                      type="text"
                      value={editForm.username}
                      onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      邮箱地址
                    </label>
                    <input
                      type="email"
                      value={editForm.email}
                      onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      头像URL（可选）
                    </label>
                    <input
                      type="url"
                      value={editForm.avatar}
                      onChange={(e) => setEditForm({ ...editForm, avatar: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="https://example.com/avatar.jpg"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <Button
                    onClick={() => setIsEditing(false)}
                    variant="outline"
                  >
                    取消
                  </Button>
                  <Button onClick={handleUpdateProfile}>
                    保存更改
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  )
}

export default ProfilePage