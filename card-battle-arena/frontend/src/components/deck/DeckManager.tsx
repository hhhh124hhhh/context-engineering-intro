import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Button } from '@/components/ui/Button'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import { DeckEditor } from './DeckEditor'
import type { Deck, CardClass } from '@/types/card'

interface DeckManagerProps {
  onSelectDeck?: (deck: Deck) => void
  className?: string
}

export const DeckManager: React.FC<DeckManagerProps> = ({
  onSelectDeck,
  className,
}) => {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(true)
  const [showEditor, setShowEditor] = useState(false)
  const [editingDeck, setEditingDeck] = useState<Deck | undefined>()
  const [filter, setFilter] = useState<CardClass | 'all'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'winRate' | 'gamesPlayed' | 'createdAt'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [deletingDeck, setDeletingDeck] = useState<number | null>(null)

  useEffect(() => {
    loadDecks()
  }, [])

  const loadDecks = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/decks')
      const data = await response.json()
      setDecks(data)
    } catch (error) {
      console.error('Failed to load decks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateDeck = () => {
    setEditingDeck(undefined)
    setShowEditor(true)
  }

  const handleEditDeck = (deck: Deck) => {
    setEditingDeck(deck)
    setShowEditor(true)
  }

  const handleSaveDeck = async (deckData: Partial<Deck>) => {
    try {
      const url = deckData.id ? `/api/decks/${deckData.id}` : '/api/decks'
      const method = deckData.id ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deckData),
      })

      if (response.ok) {
        setShowEditor(false)
        loadDecks()
      } else {
        throw new Error('Failed to save deck')
      }
    } catch (error) {
      console.error('Failed to save deck:', error)
      throw error
    }
  }

  const handleDeleteDeck = async (deckId: number) => {
    if (!confirm('确定要删除这个卡组吗？此操作无法撤销。')) {
      return
    }

    try {
      setDeletingDeck(deckId)
      const response = await fetch(`/api/decks/${deckId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setDecks(prev => prev.filter(deck => deck.id !== deckId))
      } else {
        throw new Error('Failed to delete deck')
      }
    } catch (error) {
      console.error('Failed to delete deck:', error)
      alert('删除失败，请重试')
    } finally {
      setDeletingDeck(null)
    }
  }

  const handleCopyDeck = async (deck: Deck) => {
    try {
      const response = await fetch(`/api/decks/${deck.id}/copy`, {
        method: 'POST',
      })

      if (response.ok) {
        loadDecks()
      } else {
        throw new Error('Failed to copy deck')
      }
    } catch (error) {
      console.error('Failed to copy deck:', error)
      alert('复制失败，请重试')
    }
  }

  const getClassIcon = (cardClass: CardClass) => {
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
    return icons[cardClass] || '❓'
  }

  const getClassName = (cardClass: CardClass) => {
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
    return names[cardClass] || '未知'
  }

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 60) return 'text-green-400'
    if (winRate >= 50) return 'text-blue-400'
    if (winRate >= 40) return 'text-yellow-400'
    return 'text-red-400'
  }

  const filteredAndSortedDecks = decks
    .filter(deck => filter === 'all' || deck.cardClass === filter)
    .sort((a, b) => {
      let aValue: any = a[sortBy]
      let bValue: any = b[sortBy]

      if (sortBy === 'createdAt') {
        aValue = new Date(aValue).getTime()
        bValue = new Date(bValue).getTime()
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

  if (loading) {
    return <LoadingScreen message="加载卡组列表..." />
  }

  if (showEditor) {
    return (
      <DeckEditor
        deck={editingDeck}
        onSave={handleSaveDeck}
        onCancel={() => setShowEditor(false)}
      />
    )
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
      className={cn('min-h-screen bg-gray-900 text-white p-6', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 顶部工具栏 */}
      <motion.div
        className="mb-6"
        variants={itemVariants}
      >
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold">卡组管理</h1>
          <Button onClick={handleCreateDeck}>
            创建新卡组
          </Button>
        </div>

        {/* 筛选和排序 */}
        <div className="flex items-center space-x-4">
          {/* 职业筛选 */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as CardClass | 'all')}
            className="bg-gray-800 text-white px-4 py-2 rounded border border-gray-700 focus:border-blue-500 focus:outline-none"
          >
            <option value="all">所有职业</option>
            <option value="warrior">战士</option>
            <option value="mage">法师</option>
            <option value="hunter">猎人</option>
            <option value="rogue">潜行者</option>
            <option value="priest">牧师</option>
            <option value="warlock">术士</option>
            <option value="shaman">萨满</option>
            <option value="paladin">圣骑士</option>
            <option value="druid">德鲁伊</option>
          </select>

          {/* 排序 */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-')
              setSortBy(field as any)
              setSortOrder(order as any)
            }}
            className="bg-gray-800 text-white px-4 py-2 rounded border border-gray-700 focus:border-blue-500 focus:outline-none"
          >
            <option value="name-asc">名称升序</option>
            <option value="name-desc">名称降序</option>
            <option value="winRate-desc">胜率降序</option>
            <option value="winRate-asc">胜率升序</option>
            <option value="gamesPlayed-desc">场次降序</option>
            <option value="gamesPlayed-asc">场次升序</option>
            <option value="createdAt-desc">创建时间降序</option>
            <option value="createdAt-asc">创建时间升序</option>
          </select>

          <div className="text-gray-400">
            共 {filteredAndSortedDecks.length} 个卡组
          </div>
        </div>
      </motion.div>

      {/* 卡组网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <AnimatePresence>
          {filteredAndSortedDecks.map((deck) => (
            <motion.div
              key={deck.id}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
              variants={itemVariants}
              layout
              exit={{ scale: 0.8, opacity: 0 }}
              whileHover={{ y: -4 }}
            >
              {/* 卡组头部 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                    <span className="text-xl">
                      {getClassIcon(deck.cardClass)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">
                      {deck.name}
                    </h3>
                    <div className="text-sm text-gray-400">
                      {getClassName(deck.cardClass)}
                    </div>
                  </div>
                </div>

                {/* 收藏按钮 */}
                <button
                  className={`p-1 ${deck.isFavorite ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'}`}
                  onClick={async () => {
                    try {
                      await fetch(`/api/decks/${deck.id}/favorite`, {
                        method: 'POST',
                      })
                      loadDecks()
                    } catch (error) {
                      console.error('Failed to toggle favorite:', error)
                    }
                  }}
                >
                  <svg className="w-5 h-5" fill={deck.isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                </button>
              </div>

              {/* 卡组描述 */}
              {deck.description && (
                <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                  {deck.description}
                </p>
              )}

              {/* 卡组统计 */}
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">卡牌数量:</span>
                  <span className="text-white">
                    {deck.cards.reduce((sum, card) => sum + card.quantity, 0)}张
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">使用次数:</span>
                  <span className="text-white">{deck.gamesPlayed}场</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">胜率:</span>
                  <span className={getWinRateColor(deck.winRate)}>
                    {deck.winRate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">连胜:</span>
                  <span className="text-orange-400">{deck.gamesWon - deck.gamesLost}</span>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex space-x-2">
                {onSelectDeck && (
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={() => onSelectDeck(deck)}
                  >
                    使用
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleEditDeck(deck)}
                >
                  编辑
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyDeck(deck)}
                >
                  复制
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDeleteDeck(deck.id)}
                  disabled={deletingDeck === deck.id}
                  className="text-red-400 hover:text-red-300"
                >
                  {deletingDeck === deck.id ? '删除中...' : '删除'}
                </Button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 空状态 */}
      {filteredAndSortedDecks.length === 0 && (
        <motion.div
          className="text-center py-16"
          variants={itemVariants}
        >
          <div className="text-gray-500 mb-4">
            {filter === 'all' ? '你还没有创建任何卡组' : `没有找到${getClassName(filter)}职业的卡组`}
          </div>
          <Button onClick={handleCreateDeck}>
            创建第一个卡组
          </Button>
        </motion.div>
      )}
    </motion.div>
  )
}

export default DeckManager