import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Card, CardBack } from '@/components/ui/Card'
import type { CardInstance } from '@/types/game'

interface HandProps {
  cards: CardInstance[] | any[]
  isOpponent?: boolean
  maxCards?: number
  onCardPlay?: (cardId: string, target?: string) => void
  disabled?: boolean
  className?: string
}

export const Hand: React.FC<HandProps> = ({
  cards,
  isOpponent = false,
  maxCards = 10,
  onCardPlay,
  disabled = false,
  className,
}) => {
  const [selectedCard, setSelectedCard] = useState<string | null>(null)
  const [hoveredCard, setHoveredCard] = useState<string | null>(null)

  const handleCardClick = (card: CardInstance | any) => {
    if (disabled || isOpponent || !onCardPlay) return

    if (selectedCard === card.instanceId) {
      setSelectedCard(null)
    } else {
      setSelectedCard(card.instanceId)
      onCardPlay(card.instanceId)
    }
  }

  const getCardPosition = (index: number, total: number) => {
    if (total <= 1) return { x: 0, y: 0, rotate: 0 }

    const spread = Math.min(total * 15, 120) // 扩散角度
    const angleStep = spread / (total - 1)
    const angle = -spread / 2 + index * angleStep

    // 稍微向上偏移，形成扇形
    const yOffset = Math.abs(angle) * 0.5

    return {
      x: angle * 0.5, // 水平偏移
      y: yOffset,     // 垂直偏移
      rotate: angle,  // 旋转角度
    }
  }

  const cardVariants = {
    initial: {
      y: isOpponent ? -100 : 100,
      opacity: 0,
      scale: 0.8,
      rotate: isOpponent ? 180 : 0
    },
    animate: {
      y: 0,
      opacity: 1,
      scale: 1,
      rotate: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 20,
        delay: 0.1
      }
    },
    hover: {
      y: isOpponent ? -15 : -20,
      scale: 1.1,
      transition: { duration: 0.2 }
    },
    selected: {
      y: isOpponent ? -25 : -30,
      scale: 1.15,
      transition: { duration: 0.2 }
    },
    play: {
      y: isOpponent ? -200 : 200,
      opacity: 0,
      scale: 0.5,
      transition: { duration: 0.5 }
    }
  }

  return (
    <div className={cn('relative flex justify-center items-center', className)}>
      <div className="relative" style={{ height: '120px', width: '100%' }}>
        <AnimatePresence>
          {cards.map((card, index) => {
            const position = getCardPosition(index, cards.length)
            const isHovered = hoveredCard === card.instanceId
            const isSelected = selectedCard === card.instanceId
            const canPlay = !disabled && !isOpponent && onCardPlay

            return (
              <motion.div
                key={card.instanceId}
                className="absolute cursor-pointer"
                style={{
                  left: '50%',
                  bottom: isOpponent ? '0' : 'auto',
                  top: isOpponent ? 'auto' : '0',
                  zIndex: isSelected ? 20 : isHovered ? 10 : cards.length - index,
                  transform: `translateX(-50%)`,
                }}
                initial="initial"
                animate="animate"
                exit="play"
                whileHover={canPlay ? "hover" : undefined}
                variants={cardVariants}
                transformTemplate={({ x, y, rotate }) => `
                  translateX(calc(-50% + ${x}px))
                  translateY(${y}px)
                  rotate(${rotate}deg)
                `}
                onClick={() => handleCardClick(card)}
                onMouseEnter={() => setHoveredCard(card.instanceId)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div
                  className="relative"
                  style={{
                    transform: `
                      translateX(${position.x}px)
                      translateY(${position.y * (isOpponent ? -1 : 1)}px)
                      rotate(${position.rotate * (isOpponent ? -1 : 1)}deg)
                    `,
                    transformOrigin: 'center bottom'
                  }}
                >
                  {isOpponent ? (
                    <CardBack
                      cost={card.card.cost}
                      rarity={card.card.rarity}
                      isGolden={card.isGolden}
                      size="small"
                    />
                  ) : (
                    <Card
                      card={card.card}
                      currentAttack={card.currentAttack}
                      currentDefense={card.currentDefense}
                      currentCost={card.currentCost}
                      isDormant={card.isDormant}
                      isSilenced={card.isSilenced}
                      isFrozen={card.isFrozen}
                      canPlay={canPlay && !disabled}
                      size="small"
                      showCost
                      showStats
                    />
                  )}

                  {/* 选中指示器 */}
                  {isSelected && (
                    <motion.div
                      className="absolute inset-0 border-2 border-yellow-400 rounded-lg pointer-events-none"
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                    />
                  )}

                  {/* 可打出指示器 */}
                  {canPlay && !disabled && (
                    <motion.div
                      className="absolute -top-2 -right-2 w-4 h-4 bg-green-500 rounded-full border-2 border-white"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                    />
                  )}

                  {/* 法力值不足指示器 */}
                  {canPlay && card.currentCost > (card.currentPlayerMana || 0) && (
                    <div className="absolute inset-0 bg-red-900 bg-opacity-30 rounded-lg pointer-events-none" />
                  )}
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* 空手牌状态 */}
        {cards.length === 0 && !isOpponent && (
          <motion.div
            className="flex items-center justify-center h-full w-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p className="text-gray-400 text-sm">
              {disabled ? '等待对手行动...' : '你的手牌为空'}
            </p>
          </motion.div>
        )}
      </div>

      {/* 手牌数量指示器 */}
      {(isOpponent || cards.length > 0) && (
        <div className="absolute bottom-2 left-2 bg-gray-800 bg-opacity-80 text-white text-xs px-2 py-1 rounded">
          {isOpponent ? '对手手牌' : '我的手牌'}: {cards.length}/{maxCards}
        </div>
      )}
    </div>
  )
}

export default Hand