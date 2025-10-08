import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'

interface GameLogEntry {
  id: string
  type: 'play' | 'attack' | 'spell' | 'death' | 'turn' | 'system'
  message: string
  timestamp: number
  player?: string
  card?: {
    name: string
    cost?: number
    attack?: number
    defense?: number
  }
  target?: {
    name: string
    type: 'player' | 'minion'
  }
  damage?: number
  healing?: number
}

interface GameLogProps {
  logs: GameLogEntry[] | any[]
  maxEntries?: number
  className?: string
}

export const GameLog: React.FC<GameLogProps> = ({
  logs,
  maxEntries = 50,
  className,
}) => {
  const [expandedLogs, setExpandedLogs] = useState<Set<string>>(new Set())
  const [autoScroll, setAutoScroll] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const logContainerRef = useRef<HTMLDivElement>(null)

  // 转换日志数据格式
  const formattedLogs = logs.map((log, index) => {
    if (typeof log === 'string') {
      return {
        id: `log-${index}`,
        type: 'system' as const,
        message: log,
        timestamp: Date.now(),
      }
    }
    return {
      id: log.id || `log-${index}`,
      type: log.type || 'system',
      message: log.message || log.description || '',
      timestamp: log.timestamp || Date.now(),
      player: log.player,
      card: log.card,
      target: log.target,
      damage: log.damage,
      healing: log.healing,
    }
  })

  const filteredLogs = formattedLogs
    .filter(log => filter === 'all' || log.type === filter)
    .slice(-maxEntries)

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      const container = logContainerRef.current
      container.scrollTop = container.scrollHeight
    }
  }, [filteredLogs, autoScroll])

  const toggleExpand = (logId: string) => {
    setExpandedLogs(prev => {
      const newSet = new Set(prev)
      if (newSet.has(logId)) {
        newSet.delete(logId)
      } else {
        newSet.add(logId)
      }
      return newSet
    })
  }

  const getLogIcon = (type: string) => {
    const icons = {
      play: '🎴',
      attack: '⚔️',
      spell: '✨',
      death: '💀',
      turn: '🔄',
      system: 'ℹ️',
    }
    return icons[type as keyof typeof icons] || '📝'
  }

  const getLogColor = (type: string) => {
    const colors = {
      play: 'text-blue-400',
      attack: 'text-red-400',
      spell: 'text-purple-400',
      death: 'text-gray-400',
      turn: 'text-green-400',
      system: 'text-gray-300',
    }
    return colors[type as keyof typeof colors] || 'text-gray-300'
  }

  const formatMessage = (log: GameLogEntry) => {
    let message = log.message

    if (log.card) {
      message = message.replace(
        '{card}',
        `<span class="font-medium text-yellow-400">${log.card.name}</span>`
      )
    }

    if (log.player) {
      message = message.replace(
        '{player}',
        `<span class="font-medium text-cyan-400">${log.player}</span>`
      )
    }

    if (log.target) {
      message = message.replace(
        '{target}',
        `<span class="font-medium text-orange-400">${log.target.name}</span>`
      )
    }

    if (log.damage) {
      message += ` <span class="text-red-400">-${log.damage}</span>`
    }

    if (log.healing) {
      message += ` <span class="text-green-400">+${log.healing}</span>`
    }

    return message
  }

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  return (
    <motion.div
      className={cn(
        'bg-gray-900 bg-opacity-90 rounded-lg p-4 space-y-3',
        'border border-gray-700',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* 日志标题和控制 */}
      <div className="flex items-center justify-between">
        <h3 className="text-white font-medium">游戏日志</h3>
        <div className="flex items-center space-x-2">
          {/* 过滤器 */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-800 text-white text-xs px-2 py-1 rounded border border-gray-600"
          >
            <option value="all">全部</option>
            <option value="play">出牌</option>
            <option value="attack">攻击</option>
            <option value="spell">法术</option>
            <option value="death">死亡</option>
            <option value="turn">回合</option>
            <option value="system">系统</option>
          </select>

          {/* 自动滚动 */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={cn(
              'text-xs px-2 py-1 rounded transition-colors',
              autoScroll
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300'
            )}
          >
            {autoScroll ? '自动' : '手动'}
          </button>

          {/* 清空日志 */}
          <button
            onClick={() => setExpandedLogs(new Set())}
            className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors"
          >
            清空
          </button>
        </div>
      </div>

      {/* 日志内容 */}
      <div
        ref={logContainerRef}
        className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar"
        onMouseEnter={() => setAutoScroll(false)}
        onMouseLeave={() => setAutoScroll(true)}
      >
        <AnimatePresence>
          {filteredLogs.length === 0 ? (
            <motion.div
              className="text-center text-gray-500 text-sm py-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              暂无日志记录
            </motion.div>
          ) : (
            filteredLogs.map((log, index) => (
              <motion.div
                key={log.id}
                className={cn(
                  'flex items-start space-x-2 p-2 rounded hover:bg-gray-800 transition-colors',
                  'text-sm'
                )}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
              >
                {/* 图标 */}
                <div className={cn('text-lg', getLogColor(log.type))}>
                  {getLogIcon(log.type)}
                </div>

                {/* 消息内容 */}
                <div className="flex-1 min-w-0">
                  <div
                    className={cn(
                      'text-gray-300',
                      expandedLogs.has(log.id) ? '' : 'line-clamp-1'
                    )}
                    dangerouslySetInnerHTML={{ __html: formatMessage(log) }}
                  />

                  {/* 时间戳 */}
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTimestamp(log.timestamp)}
                    {log.player && (
                      <span className="ml-2 text-cyan-400">{log.player}</span>
                    )}
                  </div>

                  {/* 详细信息 */}
                  {expandedLogs.has(log.id) && (
                    <motion.div
                      className="mt-2 p-2 bg-gray-800 rounded text-xs space-y-1"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      {log.card && (
                        <div className="text-gray-400">
                          卡牌: {log.card.name}
                          {log.card.cost && ` (${log.card.cost}法力)`}
                          {log.card.attack && log.card.defense &&
                            ` [${log.card.attack}/${log.card.defense}]`
                          }
                        </div>
                      )}
                      {log.target && (
                        <div className="text-gray-400">
                          目标: {log.target.name} ({log.target.type})
                        </div>
                      )}
                      {log.damage && (
                        <div className="text-red-400">伤害: {log.damage}</div>
                      )}
                      {log.healing && (
                        <div className="text-green-400">治疗: {log.healing}</div>
                      )}
                    </motion.div>
                  )}
                </div>

                {/* 展开/收起按钮 */}
                {log.card || log.target || log.damage || log.healing ? (
                  <button
                    onClick={() => toggleExpand(log.id)}
                    className="text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    {expandedLogs.has(log.id) ? '收起' : '展开'}
                  </button>
                ) : null}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* 日志统计 */}
      <div className="flex items-center justify-between text-xs text-gray-500 border-t border-gray-700 pt-2">
        <div>
          显示 {filteredLogs.length} / {formattedLogs.length} 条记录
        </div>
        <div>
          过滤: {filter === 'all' ? '全部' : filter}
        </div>
      </div>
    </motion.div>
  )
}

export default GameLog