import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Button } from '@/components/ui/Button'

interface MenuBarProps {
  isOpen: boolean
  onToggle: () => void
  onConcede: () => void
  onLeave: () => void
  onToggleSpectator: () => void
  onToggleLog: () => void
  isSpectator: boolean
  canConcede: boolean
  className?: string
}

export const MenuBar: React.FC<MenuBarProps> = ({
  isOpen,
  onToggle,
  onConcede,
  onLeave,
  onToggleSpectator,
  onToggleLog,
  isSpectator,
  canConcede,
  className,
}) => {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [confirmAction, setConfirmAction] = useState<'concede' | 'leave' | null>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        if (showConfirmDialog) {
          setShowConfirmDialog(false)
          setConfirmAction(null)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showConfirmDialog])

  const handleActionClick = (action: 'concede' | 'leave') => {
    setConfirmAction(action)
    setShowConfirmDialog(true)
  }

  const handleConfirmAction = () => {
    if (confirmAction === 'concede') {
      onConcede()
    } else if (confirmAction === 'leave') {
      onLeave()
    }
    setShowConfirmDialog(false)
    setConfirmAction(null)
  }

  const handleCancelAction = () => {
    setShowConfirmDialog(false)
    setConfirmAction(null)
  }

  const menuVariants = {
    open: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    closed: {
      opacity: 0,
      scale: 0.95,
      transition: {
        duration: 0.2,
        ease: "easeIn"
      }
    }
  }

  const menuItemVariants = {
    open: (i: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: i * 0.05,
        duration: 0.2,
        ease: "easeOut"
      }
    }),
    closed: {
      opacity: 0,
      x: -20,
      transition: {
        duration: 0.2,
        ease: "easeIn"
      }
    }
  }

  return (
    <div className={cn('relative', className)}>
      {/* 菜单按钮 */}
      <motion.button
        onClick={onToggle}
        className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <svg
          className="w-6 h-6 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </motion.button>

      {/* 菜单面板 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={menuRef}
            className="absolute top-full right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-xl border border-gray-700 z-50"
            variants={menuVariants}
            initial="closed"
            animate="open"
            exit="closed"
          >
            {/* 菜单标题 */}
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-white font-medium">游戏菜单</h3>
              <p className="text-gray-400 text-sm mt-1">
                {isSpectator ? '观战模式' : '游戏设置'}
              </p>
            </div>

            {/* 菜单项 */}
            <div className="p-2 space-y-1">
              {/* 观战模式切换 */}
              <motion.button
                custom={0}
                variants={menuItemVariants}
                initial="closed"
                animate="open"
                onClick={onToggleSpectator}
                className={cn(
                  'w-full flex items-center space-x-3 p-3 rounded-lg transition-colors',
                  'hover:bg-gray-700 text-left'
                )}
              >
                <span className="text-lg">
                  {isSpectator ? '👁️' : '🎮'}
                </span>
                <div className="flex-1">
                  <div className="text-white text-sm font-medium">
                    {isSpectator ? '退出观战' : '进入观战'}
                  </div>
                  <div className="text-gray-400 text-xs">
                    {isSpectator ? '返回玩家视角' : '以观战者身份观看'}
                  </div>
                </div>
              </motion.button>

              {/* 游戏日志切换 */}
              <motion.button
                custom={1}
                variants={menuItemVariants}
                initial="closed"
                animate="open"
                onClick={onToggleLog}
                className="w-full flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-700 text-left"
              >
                <span className="text-lg">📜</span>
                <div className="flex-1">
                  <div className="text-white text-sm font-medium">
                    游戏日志
                  </div>
                  <div className="text-gray-400 text-xs">
                    查看详细的游戏记录
                  </div>
                </div>
              </motion.button>

              {/* 游戏设置 */}
              <motion.button
                custom={2}
                variants={menuItemVariants}
                initial="closed"
                animate="open"
                className="w-full flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-700 text-left"
              >
                <span className="text-lg">⚙️</span>
                <div className="flex-1">
                  <div className="text-white text-sm font-medium">
                    游戏设置
                  </div>
                  <div className="text-gray-400 text-xs">
                    音效、画质等选项
                  </div>
                </div>
              </motion.button>

              {/* 帮助 */}
              <motion.button
                custom={3}
                variants={menuItemVariants}
                initial="closed"
                animate="open"
                className="w-full flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-700 text-left"
              >
                <span className="text-lg">❓</span>
                <div className="flex-1">
                  <div className="text-white text-sm font-medium">
                    游戏帮助
                  </div>
                  <div className="text-gray-400 text-xs">
                    查看游戏规则和快捷键
                  </div>
                </div>
              </motion.button>

              {/* 分隔线 */}
              <div className="border-t border-gray-700 my-2" />

              {/* 认输按钮 */}
              {!isSpectator && canConcede && (
                <motion.button
                  custom={4}
                  variants={menuItemVariants}
                  initial="closed"
                  animate="open"
                  onClick={() => handleActionClick('concede')}
                  className="w-full flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-red-600 text-left"
                >
                  <span className="text-lg">🏳️</span>
                  <div className="flex-1">
                    <div className="text-white text-sm font-medium">
                      认输
                    </div>
                    <div className="text-gray-400 text-xs">
                      放弃本局游戏
                    </div>
                  </div>
                </motion.button>
              )}

              {/* 离开游戏 */}
              <motion.button
                custom={5}
                variants={menuItemVariants}
                initial="closed"
                animate="open"
                onClick={() => handleActionClick('leave')}
                className="w-full flex items-center space-x-3 p-3 rounded-lg transition-colors hover:bg-gray-600 text-left"
              >
                <span className="text-lg">🚪</span>
                <div className="flex-1">
                  <div className="text-white text-sm font-medium">
                    离开游戏
                  </div>
                  <div className="text-gray-400 text-xs">
                    返回游戏大厅
                  </div>
                </div>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 确认对话框 */}
      <AnimatePresence>
        {showConfirmDialog && (
          <motion.div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-gray-800 rounded-lg p-6 max-w-sm mx-4 border border-gray-700"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-center">
                <div className="text-3xl mb-4">
                  {confirmAction === 'concede' ? '🏳️' : '🚪'}
                </div>

                <h3 className="text-xl font-bold text-white mb-2">
                  {confirmAction === 'concede' ? '确认认输？' : '确认离开游戏？'}
                </h3>

                <p className="text-gray-400 mb-6">
                  {confirmAction === 'concede'
                    ? '认输后本局游戏将结束，对手获得胜利。'
                    : '离开游戏后将返回大厅，当前游戏进度将丢失。'
                  }
                </p>

                <div className="flex space-x-3">
                  <Button
                    variant="outline"
                    onClick={handleCancelAction}
                    className="flex-1"
                  >
                    取消
                  </Button>
                  <Button
                    onClick={handleConfirmAction}
                    className={cn(
                      'flex-1',
                      confirmAction === 'concede'
                        ? 'bg-red-600 hover:bg-red-700'
                        : 'bg-gray-600 hover:bg-gray-700'
                    )}
                  >
                    {confirmAction === 'concede' ? '认输' : '离开'}
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default MenuBar