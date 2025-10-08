import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/classnames'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg' | 'xl'
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  border?: boolean
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  glass?: boolean
}

interface GameCardProps {
  id: number
  name: string
  cost: number
  attack?: number
  defense?: number
  description?: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  type: 'minion' | 'spell' | 'weapon' | 'hero_power'
  mechanics?: string[]
  image?: string
  onClick?: () => void
  selected?: boolean
  disabled?: boolean
  className?: string
  showStats?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = true,
  padding = 'md',
  shadow = 'md',
  border = true,
  rounded = 'lg',
  glass = false,
  ...props
}) => {
  const baseClasses = 'relative transition-all duration-200'

  const paddingClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  }

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  }

  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full',
  }

  const glassClasses = glass
    ? 'bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20'
    : 'bg-gray-800'

  return (
    <div
      className={cn(
        baseClasses,
        paddingClasses[padding],
        shadowClasses[shadow],
        roundedClasses[rounded],
        glassClasses,
        border && 'border border-gray-700',
        hover && 'hover:shadow-xl hover:scale-105',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export const GameCard: React.FC<GameCardProps> = ({
  id,
  name,
  cost,
  attack,
  defense,
  description,
  rarity,
  type,
  mechanics = [],
  image,
  onClick,
  selected = false,
  disabled = false,
  className,
  showStats = true,
}) => {
  const rarityColors = {
    common: 'border-gray-500',
    rare: 'border-blue-500',
    epic: 'border-purple-500',
    legendary: 'border-yellow-500',
  }

  const rarityBackgrounds = {
    common: 'bg-gradient-to-br from-gray-700 to-gray-800',
    rare: 'bg-gradient-to-br from-blue-800 to-blue-900',
    epic: 'bg-gradient-to-br from-purple-800 to-purple-900',
    legendary: 'bg-gradient-to-br from-yellow-800 to-yellow-900',
  }

  const cardVariants = {
    initial: { scale: 1, rotateY: 0 },
    hover: !disabled
      ? { scale: 1.05, rotateY: 5, transition: { duration: 0.2 } }
      : {},
    tap: { scale: 0.95 },
    selected: { scale: 1.05, rotateY: 10 },
  }

  return (
    <motion.div
      className={cn(
        'relative w-32 h-44 rounded-lg cursor-pointer overflow-hidden',
        rarityBackgrounds[rarity],
        rarityColors[rarity],
        selected && 'ring-4 ring-primary-500 ring-opacity-50',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      variants={cardVariants}
      initial="initial"
      animate={selected ? 'selected' : 'initial'}
      whileHover="hover"
      whileTap="tap"
      onClick={!disabled ? onClick : undefined}
      style={{
        transformStyle: 'preserve-3d',
      }}
    >
      {/* 卡牌背景 */}
      <div className="absolute inset-0 bg-black bg-opacity-20" />

      {/* 卡牌顶部 - 费用 */}
      <div className="absolute top-2 left-2 bg-blue-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
        {cost}
      </div>

      {/* 卡牌类型图标 */}
      <div className="absolute top-2 right-2 w-4 h-4">
        {type === 'minion' && (
          <div className="w-full h-full bg-green-600 rounded-sm" />
        )}
        {type === 'spell' && (
          <div className="w-full h-full bg-purple-600 rounded-full" />
        )}
        {type === 'weapon' && (
          <div className="w-full h-full bg-orange-600 rounded-sm" />
        )}
      </div>

      {/* 卡牌图片区域 */}
      <div className="flex items-center justify-center h-24">
        {image ? (
          <img
            src={image}
            alt={name}
            className="w-20 h-20 object-cover rounded"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        ) : (
          <div className="w-20 h-20 bg-gray-700 rounded flex items-center justify-center">
            <span className="text-2xl">🎴</span>
          </div>
        )}
      </div>

      {/* 卡牌名称 */}
      <div className="absolute bottom-2 left-2 right-2">
        <h3 className="text-white text-xs font-bold text-center truncate">
          {name}
        </h3>
      </div>

      {/* 攻击力和生命值（随从和武器） */}
      {showStats && (type === 'minion' || type === 'weapon') && (
        <>
          <div className="absolute bottom-8 left-2 bg-red-600 text-white text-xs font-bold rounded w-5 h-5 flex items-center justify-center">
            {attack || 0}
          </div>
          <div className="absolute bottom-8 right-2 bg-blue-600 text-white text-xs font-bold rounded w-5 h-5 flex items-center justify-center">
            {defense || 0}
          </div>
        </>
      )}

      {/* 机制标记 */}
      {mechanics.length > 0 && (
        <div className="absolute top-8 left-2 flex gap-1">
          {mechanics.slice(0, 3).map((mechanic, index) => (
            <div
              key={index}
              className="w-4 h-4 bg-yellow-600 rounded-full flex items-center justify-center"
              title={mechanic}
            >
              <span className="text-xs text-white">★</span>
            </div>
          ))}
          {mechanics.length > 3 && (
            <div className="w-4 h-4 bg-gray-600 rounded-full flex items-center justify-center">
              <span className="text-xs text-white">+</span>
            </div>
          )}
        </div>
      )}

      {/* 传说卡牌的闪光效果 */}
      {rarity === 'legendary' && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-t from-transparent via-yellow-500 to-transparent opacity-20 animate-pulse" />
        </div>
      )}

      {/* 精英卡牌的动画效果 */}
      {(rarity === 'epic' || rarity === 'legendary') && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-br from-transparent via-purple-500 to-transparent opacity-10 animate-pulse" />
        </div>
      )}
    </motion.div>
  )
}

export const CardBack: React.FC<{
  onClick?: () => void
  disabled?: boolean
  className?: string
}> = ({ onClick, disabled = false, className }) => {
  return (
    <motion.div
      className={cn(
        'relative w-32 h-44 rounded-lg cursor-pointer overflow-hidden',
        'bg-gradient-to-br from-purple-800 via-blue-800 to-purple-900',
        'border-2 border-gray-600',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      onClick={!disabled ? onClick : undefined}
      whileHover={!disabled ? { scale: 1.05 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
    >
      {/* 卡背图案 */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-24 h-24 border-2 border-gray-500 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-1">🎴</div>
            <div className="text-xs text-gray-300">卡牌</div>
          </div>
        </div>
      </div>

      {/* 装饰性光效 */}
      <div className="absolute inset-0 bg-gradient-to-t from-transparent via-white to-transparent opacity-10" />
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-500 to-transparent opacity-5" />
    </motion.div>
  )
}

export default Card