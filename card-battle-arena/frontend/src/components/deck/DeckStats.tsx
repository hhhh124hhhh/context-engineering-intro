import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/classnames'
import type { Deck, CardType, CardRarity } from '@/types/card'

interface DeckStatsProps {
  deck: Deck
  className?: string
}

export const DeckStats: React.FC<DeckStatsProps> = ({
  deck,
  className,
}) => {
  const stats = useMemo(() => {
    const totalCards = deck.cards.reduce((sum, card) => sum + card.quantity, 0)
    const totalCost = deck.cards.reduce((sum, card) => sum + card.card.cost * card.quantity, 0)
    const averageCost = totalCost / totalCards

    // 按费用分组统计
    const costDistribution = Array.from({ length: 8 }, (_, i) => ({
      cost: i,
      count: deck.cards
        .filter(card => card.card.cost === i)
        .reduce((sum, card) => sum + card.quantity, 0)
    }))

    // 按卡牌类型统计
    const typeDistribution = deck.cards.reduce((acc, card) => {
      const type = card.card.cardType
      acc[type] = (acc[type] || 0) + card.quantity
      return acc
    }, {} as Record<CardType, number>)

    // 按稀有度统计
    const rarityDistribution = deck.cards.reduce((acc, card) => {
      const rarity = card.card.rarity
      acc[rarity] = (acc[rarity] || 0) + card.quantity
      return acc
    }, {} as Record<CardRarity, number>)

    // 法力曲线
    const manaCurve = costDistribution.map(item => ({
      cost: item.cost,
      count: item.count,
      percentage: (item.count / totalCards) * 100
    }))

    return {
      totalCards,
      averageCost: parseFloat(averageCost.toFixed(1)),
      costDistribution,
      typeDistribution,
      rarityDistribution,
      manaCurve
    }
  }, [deck])

  const getTypeLabel = (type: CardType) => {
    const labels = {
      minion: '随从',
      spell: '法术',
      weapon: '武器',
      hero_power: '英雄技能'
    }
    return labels[type] || type
  }

  const getRarityLabel = (rarity: CardRarity) => {
    const labels = {
      common: '普通',
      rare: '稀有',
      epic: '史诗',
      legendary: '传说'
    }
    return labels[rarity] || rarity
  }

  const getRarityColor = (rarity: CardRarity) => {
    const colors = {
      common: 'bg-gray-600',
      rare: 'bg-blue-600',
      epic: 'bg-purple-600',
      legendary: 'bg-orange-600'
    }
    return colors[rarity] || 'bg-gray-600'
  }

  const getMaxPercentage = () => {
    return Math.max(...stats.manaCurve.map(item => item.percentage))
  }

  const getTypeColor = (type: CardType) => {
    const colors = {
      minion: 'bg-blue-500',
      spell: 'bg-purple-500',
      weapon: 'bg-orange-500',
      hero_power: 'bg-green-500'
    }
    return colors[type] || 'bg-gray-500'
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

  return (
    <motion.div
      className={cn('bg-gray-800 rounded-lg p-6 space-y-6', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <h2 className="text-xl font-bold text-white mb-4">卡组统计分析</h2>

      {/* 基础统计 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">基础信息</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-700 rounded p-3">
            <div className="text-2xl font-bold text-white">{stats.totalCards}</div>
            <div className="text-sm text-gray-400">总卡牌数</div>
          </div>
          <div className="bg-gray-700 rounded p-3">
            <div className="text-2xl font-bold text-white">{stats.averageCost}</div>
            <div className="text-sm text-gray-400">平均费用</div>
          </div>
          <div className="bg-gray-700 rounded p-3">
            <div className="text-2xl font-bold text-white">{deck.cards.length}</div>
            <div className="text-sm text-gray-400">不同卡牌</div>
          </div>
          <div className="bg-gray-700 rounded p-3">
            <div className="text-2xl font-bold text-white">{deck.winRate.toFixed(1)}%</div>
            <div className="text-sm text-gray-400">胜率</div>
          </div>
        </div>
      </motion.div>

      {/* 法力曲线 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">法力曲线</h3>
        <div className="bg-gray-700 rounded p-4">
          <div className="space-y-2">
            {stats.manaCurve.map((item) => (
              <div key={item.cost} className="flex items-center">
                <div className="w-8 text-center text-white font-medium">
                  {item.cost}
                </div>
                <div className="flex-1 mx-2">
                  <div className="bg-gray-600 rounded-full h-6 relative overflow-hidden">
                    <motion.div
                      className="bg-blue-500 h-full rounded-full flex items-center justify-center text-xs text-white font-medium"
                      initial={{ width: 0 }}
                      animate={{ width: `${(item.percentage / getMaxPercentage()) * 100}%` }}
                      transition={{ duration: 0.8, delay: 0.2 }}
                    >
                      {item.count > 0 && `${item.count}张`}
                    </motion.div>
                  </div>
                </div>
                <div className="w-12 text-right text-gray-400 text-sm">
                  {item.percentage.toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* 卡牌类型分布 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">卡牌类型分布</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(stats.typeDistribution).map(([type, count]) => (
            <div key={type} className="bg-gray-700 rounded p-3">
              <div className="flex items-center space-x-2">
                <div className={cn('w-3 h-3 rounded-full', getTypeColor(type as CardType))} />
                <span className="text-white font-medium">{getTypeLabel(type as CardType)}</span>
              </div>
              <div className="text-lg font-bold text-white mt-1">{count}</div>
              <div className="text-xs text-gray-400">
                {((count / stats.totalCards) * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* 稀有度分布 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">稀有度分布</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(stats.rarityDistribution).map(([rarity, count]) => (
            <div key={rarity} className="bg-gray-700 rounded p-3">
              <div className="flex items-center space-x-2">
                <div className={cn('w-3 h-3 rounded-full', getRarityColor(rarity as CardRarity))} />
                <span className="text-white font-medium">{getRarityLabel(rarity as CardRarity)}</span>
              </div>
              <div className="text-lg font-bold text-white mt-1">{count}</div>
              <div className="text-xs text-gray-400">
                {((count / stats.totalCards) * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* 费用段分析 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">费用段分析</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700 rounded p-4">
            <h4 className="text-white font-medium mb-2">前期 (1-3费)</h4>
            <div className="text-2xl font-bold text-green-400">
              {stats.costDistribution.slice(1, 4).reduce((sum, item) => sum + item.count, 0)}张
            </div>
            <div className="text-sm text-gray-400">
              占比 {((stats.costDistribution.slice(1, 4).reduce((sum, item) => sum + item.count, 0) / stats.totalCards) * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-gray-700 rounded p-4">
            <h4 className="text-white font-medium mb-2">中期 (4-6费)</h4>
            <div className="text-2xl font-bold text-yellow-400">
              {stats.costDistribution.slice(4, 7).reduce((sum, item) => sum + item.count, 0)}张
            </div>
            <div className="text-sm text-gray-400">
              占比 {((stats.costDistribution.slice(4, 7).reduce((sum, item) => sum + item.count, 0) / stats.totalCards) * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-gray-700 rounded p-4">
            <h4 className="text-white font-medium mb-2">后期 (7+费)</h4>
            <div className="text-2xl font-bold text-red-400">
              {stats.costDistribution.slice(7).reduce((sum, item) => sum + item.count, 0)}张
            </div>
            <div className="text-sm text-gray-400">
              占比 {((stats.costDistribution.slice(7).reduce((sum, item) => sum + item.count, 0) / stats.totalCards) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </motion.div>

      {/* 使用建议 */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-3">使用建议</h3>
        <div className="bg-gray-700 rounded p-4 space-y-2">
          {stats.averageCost < 3 && (
            <div className="text-green-400 text-sm">
              • 这是一个快攻卡组，前期卡牌充足
            </div>
          )}
          {stats.averageCost >= 3 && stats.averageCost <= 5 && (
            <div className="text-blue-400 text-sm">
              • 这是一个中速卡组，节奏均衡
            </div>
          )}
          {stats.averageCost > 5 && (
            <div className="text-purple-400 text-sm">
              • 这是一个控制卡组，后期强大
            </div>
          )}
          {stats.costDistribution[1].count + stats.costDistribution[2].count < 8 && (
            <div className="text-yellow-400 text-sm">
              • 建议增加更多低费卡牌来改善前期曲线
            </div>
          )}
          {stats.costDistribution[0].count > 10 && (
            <div className="text-orange-400 text-sm">
              • 1费卡牌较多，注意避免手牌拥堵
            </div>
          )}
          {Object.values(stats.rarityDistribution).filter((_, index) =>
            ['legendary'].includes(Object.keys(stats.rarityDistribution)[index])
          ).reduce((sum, count) => sum + count, 0) > 5 && (
            <div className="text-yellow-400 text-sm">
              • 传说卡牌较多，稳定性可能受影响
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default DeckStats