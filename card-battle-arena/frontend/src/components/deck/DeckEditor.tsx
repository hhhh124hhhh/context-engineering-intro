import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import type { Card as CardType, Deck, DeckCard, CardFilter, CardSort } from '@/types/card'

interface DeckEditorProps {
  deck?: Deck
  onSave: (deck: Partial<Deck>) => void
  onCancel: () => void
  className?: string
}

export const DeckEditor: React.FC<DeckEditorProps> = ({
  deck,
  onSave,
  onCancel,
  className,
}) => {
  const [availableCards, setAvailableCards] = useState<CardType[]>([])
  const [filteredCards, setFilteredCards] = useState<CardType[]>([])
  const [selectedCards, setSelectedCards] = useState<DeckCard[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filter, setFilter] = useState<CardFilter>({})
  const [sort, setSort] = useState<CardSort>({ field: 'cost', direction: 'asc' })
  const [deckName, setDeckName] = useState(deck?.name || '')
  const [deckDescription, setDeckDescription] = useState(deck?.description || '')
  const [selectedCardClass, setSelectedCardClass] = useState(deck?.cardClass || 'neutral')

  // 加载可用卡牌
  useEffect(() => {
    const loadCards = async () => {
      try {
        setLoading(true)
        // 模拟API调用
        const response = await fetch('/api/cards')
        const cards = await response.json()
        setAvailableCards(cards)
        setFilteredCards(cards)
      } catch (error) {
        console.error('Failed to load cards:', error)
      } finally {
        setLoading(false)
      }
    }
    loadCards()
  }, [])

  // 初始化选中卡牌
  useEffect(() => {
    if (deck?.cards) {
      setSelectedCards(deck.cards)
    }
  }, [deck])

  // 应用过滤和排序
  useEffect(() => {
    let filtered = availableCards.filter(card => {
      // 职业过滤
      if (selectedCardClass !== 'neutral' &&
          card.cardClass !== selectedCardClass &&
          card.cardClass !== 'neutral') {
        return false
      }

      // 搜索过滤
      if (searchQuery && !card.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }

      // 其他过滤条件
      if (filter.cardType && card.cardType !== filter.cardType) return false
      if (filter.rarity && card.rarity !== filter.rarity) return false
      if (filter.costMin !== undefined && card.cost < filter.costMin) return false
      if (filter.costMax !== undefined && card.cost > filter.costMax) return false

      return true
    })

    // 排序
    filtered.sort((a, b) => {
      const aValue = a[sort.field]
      const bValue = b[sort.field]

      if (aValue < bValue) return sort.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sort.direction === 'asc' ? 1 : -1
      return 0
    })

    setFilteredCards(filtered)
  }, [availableCards, searchQuery, filter, sort, selectedCardClass])

  const addCard = useCallback((card: CardType) => {
    const existingCard = selectedCards.find(c => c.cardId === card.id)
    const currentCount = existingCard ? existingCard.quantity : 0

    // 检查卡牌数量限制
    if (currentCount >= (card.rarity === 'legendary' ? 1 : 2)) {
      return
    }

    // 检查卡组总数量限制
    const totalCards = selectedCards.reduce((sum, c) => sum + c.quantity, 0)
    if (totalCards >= 30) {
      return
    }

    if (existingCard) {
      setSelectedCards(prev => prev.map(c =>
        c.cardId === card.id
          ? { ...c, quantity: c.quantity + 1 }
          : c
      ))
    } else {
      setSelectedCards(prev => [...prev, {
        cardId: card.id,
        quantity: 1,
        position: prev.length,
        card
      }])
    }
  }, [selectedCards])

  const removeCard = useCallback((cardId: number) => {
    setSelectedCards(prev => {
      const existing = prev.find(c => c.cardId === cardId)
      if (existing && existing.quantity > 1) {
        return prev.map(c =>
          c.cardId === cardId
            ? { ...c, quantity: c.quantity - 1 }
            : c
        )
      }
      return prev.filter(c => c.cardId !== cardId)
    })
  }, [])

  const getCardCount = useCallback((cardId: number) => {
    const card = selectedCards.find(c => c.cardId === cardId)
    return card?.quantity || 0
  }, [selectedCards])

  const getTotalCardCount = useCallback(() => {
    return selectedCards.reduce((sum, c) => sum + c.quantity, 0)
  }, [selectedCards])

  const canAddCard = useCallback((card: CardType) => {
    const currentCount = getCardCount(card.id)
    const maxCount = card.rarity === 'legendary' ? 1 : 2
    const totalCards = getTotalCardCount()

    return currentCount < maxCount && totalCards < 30
  }, [getCardCount, getTotalCardCount])

  const handleSave = useCallback(async () => {
    if (!deckName.trim()) {
      alert('请输入卡组名称')
      return
    }

    if (getTotalCardCount() !== 30) {
      alert('卡组必须包含30张卡牌')
      return
    }

    try {
      setSaving(true)
      await onSave({
        id: deck?.id,
        name: deckName.trim(),
        description: deckDescription.trim(),
        cardClass: selectedCardClass,
        cards: selectedCards
      })
    } catch (error) {
      console.error('Failed to save deck:', error)
      alert('保存失败，请重试')
    } finally {
      setSaving(false)
    }
  }, [deckName, deckDescription, selectedCardClass, selectedCards, getTotalCardCount, deck, onSave])

  if (loading) {
    return <LoadingScreen message="加载卡牌数据..." />
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
      className={cn('h-screen bg-gray-900 text-white', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 顶部工具栏 */}
      <motion.div
        className="bg-gray-800 border-b border-gray-700 p-4"
        variants={itemVariants}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={onCancel}>
              返回
            </Button>
            <div>
              <input
                type="text"
                value={deckName}
                onChange={(e) => setDeckName(e.target.value)}
                placeholder="卡组名称"
                className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                maxLength={50}
              />
            </div>
            <div className="text-sm text-gray-400">
              {getTotalCardCount()}/30 张卡牌
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={selectedCardClass}
              onChange={(e) => setSelectedCardClass(e.target.value)}
              className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="neutral">中立</option>
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

            <Button
              onClick={handleSave}
              disabled={saving || getTotalCardCount() !== 30 || !deckName.trim()}
              className="min-w-[100px]"
            >
              {saving ? '保存中...' : '保存卡组'}
            </Button>
          </div>
        </div>

        {/* 卡组描述 */}
        <div className="mt-4">
          <textarea
            value={deckDescription}
            onChange={(e) => setDeckDescription(e.target.value)}
            placeholder="卡组描述（可选）"
            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            rows={2}
            maxLength={200}
          />
        </div>
      </motion.div>

      <div className="flex h-full">
        {/* 左侧：卡牌筛选和列表 */}
        <div className="flex-1 flex flex-col">
          {/* 筛选工具栏 */}
          <motion.div
            className="bg-gray-800 border-b border-gray-700 p-4"
            variants={itemVariants}
          >
            <div className="flex items-center space-x-4">
              {/* 搜索框 */}
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索卡牌名称..."
                className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />

              {/* 费用过滤 */}
              <select
                value={filter.costMin || ''}
                onChange={(e) => setFilter(prev => ({
                  ...prev,
                  costMin: e.target.value ? parseInt(e.target.value) : undefined
                }))}
                className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">最小费用</option>
                {[0, 1, 2, 3, 4, 5, 6, 7].map(cost => (
                  <option key={cost} value={cost}>{cost}费</option>
                ))}
              </select>

              <select
                value={filter.costMax || ''}
                onChange={(e) => setFilter(prev => ({
                  ...prev,
                  costMax: e.target.value ? parseInt(e.target.value) : undefined
                }))}
                className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">最大费用</option>
                {[0, 1, 2, 3, 4, 5, 6, 7].map(cost => (
                  <option key={cost} value={cost}>{cost}费</option>
                ))}
              </select>

              {/* 稀有度过滤 */}
              <select
                value={filter.rarity || ''}
                onChange={(e) => setFilter(prev => ({
                  ...prev,
                  rarity: e.target.value as any
                }))}
                className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">所有稀有度</option>
                <option value="common">普通</option>
                <option value="rare">稀有</option>
                <option value="epic">史诗</option>
                <option value="legendary">传说</option>
              </select>

              {/* 排序 */}
              <select
                value={`${sort.field}-${sort.direction}`}
                onChange={(e) => {
                  const [field, direction] = e.target.value.split('-')
                  setSort({ field: field as any, direction: direction as any })
                }}
                className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="cost-asc">费用升序</option>
                <option value="cost-desc">费用降序</option>
                <option value="name-asc">名称升序</option>
                <option value="name-desc">名称降序</option>
                <option value="attack-asc">攻击升序</option>
                <option value="attack-desc">攻击降序</option>
                <option value="defense-asc">生命升序</option>
                <option value="defense-desc">生命降序</option>
              </select>
            </div>
          </motion.div>

          {/* 卡牌列表 */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <AnimatePresence>
                {filteredCards.map((card) => {
                  const count = getCardCount(card.id)
                  const canAdd = canAddCard(card)

                  return (
                    <motion.div
                      key={card.id}
                      className="relative"
                      variants={itemVariants}
                      layout
                      exit={{ scale: 0.8, opacity: 0 }}
                    >
                      <Card
                        card={card}
                        size="normal"
                        canPlay={canAdd}
                        onClick={() => canAdd && addCard(card)}
                        className={cn(
                          !canAdd && 'opacity-50 cursor-not-allowed'
                        )}
                      />

                      {/* 卡牌数量指示器 */}
                      {count > 0 && (
                        <div className="absolute top-2 right-2 bg-blue-600 text-white text-sm font-bold rounded-full w-6 h-6 flex items-center justify-center">
                          {count}
                        </div>
                      )}

                      {/* 添加按钮 */}
                      {canAdd && (
                        <motion.button
                          className="absolute bottom-2 right-2 bg-green-600 hover:bg-green-700 text-white p-2 rounded-full"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => addCard(card)}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        </motion.button>
                      )}
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>

            {filteredCards.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                没有找到符合条件的卡牌
              </div>
            )}
          </div>
        </div>

        {/* 右侧：当前卡组 */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">当前卡组</h3>

          <div className="space-y-2">
            <AnimatePresence>
              {selectedCards.map((deckCard) => (
                <motion.div
                  key={deckCard.cardId}
                  className="flex items-center space-x-3 bg-gray-700 rounded-lg p-3"
                  variants={itemVariants}
                  exit={{ scale: 0.8, opacity: 0 }}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-white font-medium">
                        {deckCard.card.name}
                      </span>
                      <span className="text-gray-400 text-sm">
                        {deckCard.card.cost}费
                      </span>
                    </div>
                    {deckCard.card.attack !== undefined && deckCard.card.defense !== undefined && (
                      <div className="text-gray-400 text-sm">
                        {deckCard.card.attack}/{deckCard.card.defense}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-white font-bold">
                      {deckCard.quantity}
                    </span>
                    <button
                      onClick={() => removeCard(deckCard.cardId)}
                      className="text-red-400 hover:text-red-300 p-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                      </svg>
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {selectedCards.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              卡组为空，请添加卡牌
            </div>
          )}

          {/* 卡组统计 */}
          <div className="mt-6 pt-4 border-t border-gray-600">
            <h4 className="text-sm font-medium text-gray-300 mb-2">卡组统计</h4>
            <div className="space-y-1 text-sm text-gray-400">
              <div>总卡牌数: {getTotalCardCount()}/30</div>
              <div>不同卡牌: {selectedCards.length}种</div>
              <div>
                平均费用: {selectedCards.length > 0
                  ? (selectedCards.reduce((sum, c) => sum + c.card.cost * c.quantity, 0) / getTotalCardCount()).toFixed(1)
                  : 0}费
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default DeckEditor