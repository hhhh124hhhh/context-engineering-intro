import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/classnames'

interface PlayerInfoProps {
  player: any
  isOpponent?: boolean
  isActive?: boolean
  className?: string
}

export const PlayerInfo: React.FC<PlayerInfoProps> = ({
  player,
  isOpponent = false,
  isActive = false,
  className,
}) => {
  const getClassIcon = (cardClass: string) => {
    const icons = {
      warrior: '⚔️',
      mage: '🧙‍♂️',
      hunter: '🏹',
      rogue: '🗡️',
      priest: '✝️',
      warlock: '🔮',
      shaman: '⚡',
      paladin: '🛡️',
      druid: '🌿',
      neutral: '🎯'
    }
    return icons[cardClass as keyof typeof icons] || '❓'
  }

  const getClassName = (cardClass: string) => {
    const names = {
      warrior: '战士',
      mage: '法师',
      hunter: '猎人',
      rogue: '潜行者',
      priest: '牧师',
      warlock: '术士',
      shaman: '萨满',
      paladin: '圣骑士',
      druid: '德鲁伊',
      neutral: '中立'
    }
    return names[cardClass as keyof typeof names] || '未知'
  }

  const getRankColor = (rank: number) => {
    if (rank >= 25) return 'text-gray-400'
    if (rank >= 20) return 'text-gray-300'
    if (rank >= 15) return 'text-green-400'
    if (rank >= 10) return 'text-blue-400'
    if (rank >= 5) return 'text-purple-400'
    if (rank >= 1) return 'text-orange-400'
    return 'text-yellow-400' // Legend rank
  }

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 60) return 'text-green-400'
    if (winRate >= 50) return 'text-blue-400'
    if (winRate >= 40) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <motion.div
      className={cn(
        'bg-gray-800 rounded-lg p-4 min-w-[200px] space-y-3',
        isActive && 'ring-2 ring-green-500 ring-opacity-50',
        className
      )}
      initial={{ opacity: 0, x: isOpponent ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* 玩家基本信息 */}
      <div className="flex items-center space-x-3">
        {/* 头像 */}
        <div className="relative">
          <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
            <span className="text-xl">
              {getClassIcon(player?.card_class || 'neutral')}
            </span>
          </div>

          {/* 在线状态 */}
          {player?.is_online && (
            <motion.div
              className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-800"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            />
          )}
        </div>

        {/* 玩家名称和等级 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <h3 className="text-white font-medium truncate">
              {player?.username || '未知玩家'}
            </h3>
            {isActive && (
              <motion.div
                className="w-2 h-2 bg-green-500 rounded-full"
                animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            )}
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-gray-400">
              {getClassName(player?.card_class || 'neutral')}
            </span>
            <span className={getRankColor(player?.rank || 25)}>
              Lv.{player?.level || 1}
            </span>
          </div>
        </div>
      </div>

      {/* 战斗统计 */}
      <div className="space-y-2">
        {/* 生命值和护甲 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-blue-400 font-bold">
              {player?.armor || 0}
            </div>
            <div className="text-white font-bold text-lg">
              {player?.health || 0}
            </div>
          </div>
          <div className="text-xs text-gray-400">
            总计: {player?.effective_health || 0}
          </div>
        </div>

        {/* 法力值 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-purple-400 font-bold">
              {player?.mana || 0}
            </div>
            <div className="text-gray-400 text-sm">
              / {player?.max_mana || 0}
            </div>
          </div>
          <div className="text-xs text-gray-400">
            法力值
          </div>
        </div>

        {/* 卡牌数量 */}
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-400">
            手牌: {player?.hand?.length || 0}
          </div>
          <div className="text-gray-400">
            牌库: {player?.deck_count || 0}
          </div>
        </div>
      </div>

      {/* 玩家统计信息 */}
      {player?.stats && (
        <motion.div
          className="border-t border-gray-700 pt-3 space-y-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">胜率:</span>
            <span className={getWinRateColor(player.stats.win_rate || 0)}>
              {(player.stats.win_rate || 0).toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">场次:</span>
            <span className="text-gray-300">
              {player.stats.games_played || 0}
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">连胜:</span>
            <span className="text-orange-400">
              {player.stats.win_streak || 0}
            </span>
          </div>
        </motion.div>
      )}

      {/* 段位信息 */}
      {player?.rank !== undefined && (
        <motion.div
          className="flex items-center justify-between text-xs"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <span className="text-gray-400">段位:</span>
          <span className={getRankColor(player.rank)}>
            {player.rank <= 0 ? '传说' : `${player.rank}段`}
          </span>
        </motion.div>
      )}

      {/* 状态效果 */}
      {player?.status_effects && player.status_effects.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {player.status_effects.slice(0, 3).map((effect: any, index: number) => (
            <div
              key={index}
              className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300"
              title={effect.description}
            >
              {effect.name}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}

export default PlayerInfo