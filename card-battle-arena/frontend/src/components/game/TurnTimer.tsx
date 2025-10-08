import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'

interface TurnTimerProps {
  isActive: boolean
  timeLeft: number
  currentPlayer?: number
  turnNumber?: number
  className?: string
}

export const TurnTimer: React.FC<TurnTimerProps> = ({
  isActive,
  timeLeft,
  currentPlayer = 1,
  turnNumber = 1,
  className,
}) => {
  const [displayTime, setDisplayTime] = useState(timeLeft)
  const [isWarning, setIsWarning] = useState(false)
  const [isDanger, setIsDanger] = useState(false)

  useEffect(() => {
    setDisplayTime(timeLeft)
    setIsWarning(timeLeft <= 30 && timeLeft > 10)
    setIsDanger(timeLeft <= 10)
  }, [timeLeft])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const timerVariants = {
    active: {
      scale: 1,
      opacity: 1,
      transition: { duration: 0.3 }
    },
    inactive: {
      scale: 0.9,
      opacity: 0.6,
      transition: { duration: 0.3 }
    },
    warning: {
      scale: [1, 1.05, 1],
      transition: { repeat: Infinity, duration: 1 }
    },
    danger: {
      scale: [1, 1.1, 1],
      transition: { repeat: Infinity, duration: 0.5 }
    }
  }

  const progressVariants = {
    full: { width: '100%' },
    warning: { width: '33%', backgroundColor: '#f59e0b' },
    danger: { width: '10%', backgroundColor: '#ef4444' }
  }

  const getProgressState = () => {
    if (isDanger) return 'danger'
    if (isWarning) return 'warning'
    return 'full'
  }

  return (
    <motion.div
      className={cn(
        'flex flex-col items-center space-y-2 bg-gray-800 rounded-lg p-4 min-w-[120px]',
        className
      )}
      animate={isActive ? (isDanger ? 'danger' : isWarning ? 'warning' : 'active') : 'inactive'}
      variants={timerVariants}
    >
      {/* 回合数指示器 */}
      <div className="text-center">
        <div className="text-xs text-gray-400">
          第 {turnNumber} 回合
        </div>
        <div className="text-sm text-gray-300">
          玩家 {currentPlayer}
        </div>
      </div>

      {/* 计时器显示 */}
      <div className="relative w-20 h-20">
        {/* 背景圆环 */}
        <svg className="absolute inset-0 w-full h-full transform -rotate-90">
          <circle
            cx="40"
            cy="40"
            r="36"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-700"
          />
          {/* 进度圆环 */}
          <motion.circle
            cx="40"
            cy="40"
            r="36"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 36}`}
            strokeDashoffset={`${2 * Math.PI * 36 * (1 - displayTime / 90)}`}
            className={cn(
              'transition-colors duration-300',
              isDanger ? 'text-red-500' :
              isWarning ? 'text-yellow-500' :
              isActive ? 'text-green-500' : 'text-gray-500'
            )}
            strokeLinecap="round"
          />
        </svg>

        {/* 时间文本 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className={cn(
              'text-lg font-bold tabular-nums',
              isDanger ? 'text-red-400' :
              isWarning ? 'text-yellow-400' :
              isActive ? 'text-green-400' : 'text-gray-400'
            )}
            animate={isDanger ? { scale: [1, 1.2, 1] } : undefined}
            transition={isDanger ? { repeat: Infinity, duration: 0.5 } : undefined}
          >
            {formatTime(displayTime)}
          </motion.span>
        </div>
      </div>

      {/* 状态指示器 */}
      <AnimatePresence>
        {isActive && (
          <motion.div
            className="flex items-center space-x-1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <motion.div
              className="w-2 h-2 bg-green-500 rounded-full"
              animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            />
            <span className="text-xs text-green-400">
              你的回合
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 警告消息 */}
      <AnimatePresence>
        {isDanger && (
          <motion.div
            className="text-xs text-red-400 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            时间即将耗尽！
          </motion.div>
        )}
      </AnimatePresence>

      {/* 底部进度条 */}
      <div className="w-full h-1 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full transition-all duration-1000 ease-linear"
          variants={progressVariants}
          animate={getProgressState()}
        />
      </div>

      {/* 快捷操作按钮 */}
      {isActive && (
        <motion.div
          className="flex space-x-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <button
            className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
            onClick={() => {
              // 触发结束回合动作
              window.dispatchEvent(new CustomEvent('endTurn'))
            }}
          >
            结束回合
          </button>
        </motion.div>
      )}
    </motion.div>
  )
}

export default TurnTimer