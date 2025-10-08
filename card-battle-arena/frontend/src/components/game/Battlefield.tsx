import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Card } from '@/components/ui/Card'
import type { CardInstance } from '@/types/game'

interface BattlefieldProps {
  cards: CardInstance[] | any[]
  isOpponent?: boolean
  onCardClick?: (cardId: string, target?: string) => void
  disabled?: boolean
  className?: string
}

export const Battlefield: React.FC<BattlefieldProps> = ({
  cards,
  isOpponent = false,
  onCardClick,
  disabled = false,
  className,
}) => {
  const [selectedCard, setSelectedCard] = useState<string | null>(null)
  const [hoveredCard, setHoveredCard] = useState<string | null>(null)

  const handleCardClick = (card: CardInstance | any, targetId?: string) => {
    if (disabled || !onCardClick) return

    if (selectedCard === card.instanceId) {
      setSelectedCard(null)
    } else {
      setSelectedCard(card.instanceId)
      onCardClick(card.instanceId, targetId)
    }
  }

  const getCardPosition = (index: number, total: number) => {
    const maxCards = 7 // 战场最大随从数
    const spacing = Math.min(100, 600 / Math.max(total, 1))
    const totalWidth = spacing * (total - 1)
    const startX = -totalWidth / 2

    return {
      x: startX + index * spacing,
      y: 0
    }
  }

  const cardVariants = {
    initial: {
      y: isOpponent ? -50 : 50,
      opacity: 0,
      scale: 0.8,
    },
    animate: {
      y: 0,
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 20,
        delay: 0.1
      }
    },
    hover: {
      y: isOpponent ? -10 : -15,
      scale: 1.1,
      transition: { duration: 0.2 }
    },
    selected: {
      y: isOpponent ? -20 : -25,
      scale: 1.15,
      transition: { duration: 0.2 }
    },
    attack: {
      x: 100,
      transition: { duration: 0.3 }
    },
    damage: {
      x: [-5, 5, -5, 5, 0],
      transition: { duration: 0.3 }
    },
    destroy: {
      opacity: 0,
      scale: 0,
      rotate: 180,
      transition: { duration: 0.5 }
    }
  }

  const renderCardEffect = (card: CardInstance | any) => {
    if (!card.enchantments || card.enchantments.length === 0) return null

    return (
      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
        {card.enchantments.slice(0, 3).map((enchantment: any, index: number) => (
          <div
            key={enchantment.id}
            className="w-4 h-4 bg-purple-600 rounded-full border border-purple-400 flex items-center justify-center"
            title={enchantment.description}
          >
            <span className="text-xs text-white">
              {enchantment.attackBuff > 0 ? '+' : ''}
              {enchantment.attackBuff}
            </span>
          </div>
        ))}
      </div>
    )
  }

  const renderAttackIndicator = (card: CardInstance | any) => {
    if (!card.attackCount || card.attackCount >= 1) return null
    if (card.summoningSickness) return null

    return (
      <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-500 rounded-full border-2 border-white flex items-center justify-center">
        <span className="text-xs font-bold text-white">!</span>
      </div>
    )
  }

  const renderHealthBar = (card: CardInstance | any) => {
    const maxHealth = card.card.defense || 0
    const currentHealth = card.currentDefense || 0
    const healthPercentage = (currentHealth / maxHealth) * 100

    return (
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700 rounded-b">
        <div
          className={cn(
            'h-full rounded-b transition-all duration-300',
            healthPercentage > 66 ? 'bg-green-500' :
            healthPercentage > 33 ? 'bg-yellow-500' : 'bg-red-500'
          )}
          style={{ width: `${healthPercentage}%` }}
        />
      </div>
    )
  }

  return (
    <div className={cn('relative flex justify-center items-center', className)}>
      <div className="relative" style={{ height: '140px', width: '100%', minWidth: '300px' }}>
        <AnimatePresence>
          {cards.map((card, index) => {
            const position = getCardPosition(index, cards.length)
            const isHovered = hoveredCard === card.instanceId
            const isSelected = selectedCard === card.instanceId
            const canClick = !disabled && onCardClick
            const canAttack = !card.summoningSickness && card.attackCount < 1

            return (
              <motion.div
                key={card.instanceId}
                className="absolute"
                style={{
                  left: '50%',
                  bottom: isOpponent ? '0' : 'auto',
                  top: isOpponent ? 'auto' : '0',
                  zIndex: isSelected ? 20 : isHovered ? 10 : cards.length - index,
                  transform: `translateX(-50%)`,
                }}
                initial="initial"
                animate="animate"
                exit="destroy"
                whileHover={canClick ? "hover" : undefined}
                variants={cardVariants}
                onClick={() => handleCardClick(card)}
                onMouseEnter={() => setHoveredCard(card.instanceId)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div
                  className="relative"
                  style={{
                    transform: `translateX(${position.x}px) translateY(${position.y}px)`,
                  }}
                >
                  <Card
                    card={card.card}
                    currentAttack={card.currentAttack}
                    currentDefense={card.currentDefense}
                    currentCost={card.currentCost}
                    isDormant={card.isDormant}
                    isSilenced={card.isSilenced}
                    isFrozen={card.isFrozen}
                    canPlay={false}
                    size="normal"
                    showCost={false}
                    showStats
                  />

                  {/* 选中指示器 */}
                  {isSelected && (
                    <motion.div
                      className="absolute inset-0 border-2 border-yellow-400 rounded-lg pointer-events-none"
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                    />
                  )}

                  {/* 攻击指示器 */}
                  {canAttack && !disabled && (
                    <motion.div
                      className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full border-2 border-white flex items-center justify-center"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1, rotate: [0, -10, 10, 0] }}
                      transition={{ repeat: Infinity, duration: 2 }}
                    >
                      <span className="text-xs font-bold text-white">⚔️</span>
                    </motion.div>
                  )}

                  {/* 冰冻效果 */}
                  {card.isFrozen && (
                    <div className="absolute inset-0 bg-blue-400 bg-opacity-30 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">❄️</span>
                    </div>
                  )}

                  {/* 沉默效果 */}
                  {card.isSilenced && (
                    <div className="absolute inset-0 bg-gray-400 bg-opacity-20 rounded-lg" />
                  )}

                  {/* 卡牌效果 */}
                  {renderCardEffect(card)}

                  {/* 生命值条 */}
                  {card.card.cardType === 'minion' && renderHealthBar(card)}
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* 空战场状态 */}
        {cards.length === 0 && (
          <motion.div
            className="flex items-center justify-center h-full w-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p className="text-gray-500 text-sm">
              {isOpponent ? '对手战场为空' : '你的战场为空'}
            </p>
          </motion.div>
        )}

        {/* 战场位置指示器 */}
        {!disabled && cards.length < 7 && !isOpponent && (
          <div className="absolute bottom-0 right-0 text-xs text-gray-400">
            {cards.length}/7
          </div>
        )}
      </div>
    </div>
  )
}

export default Battlefield