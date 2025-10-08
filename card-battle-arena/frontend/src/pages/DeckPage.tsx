import React, { useEffect, useState } from 'react'
import { useAuthStore } from '@stores/authStore'
import { useDeckStore } from '@stores/deckStore'
import { useUIStore } from '@stores/uiStore'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  DocumentTextIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  SparklesIcon,
  ShieldCheckIcon,
  FireIcon,
  BoltIcon,
  HeartIcon,
  StarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface Card {
  id: string
  name: string
  cost: number
  attack: number
  health: number
  description: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  type: 'minion' | 'spell' | 'weapon'
  faction: string
  image?: string
  count?: number
}

interface Deck {
  id: string
  name: string
  description: string
  cards: Card[]
  cardCount: number
  isCurrent: boolean
  createdAt: string
  winRate?: number
  gamesPlayed?: number
}

const CARD_COLORS = {
  common: 'border-gray-500 bg-gray-800',
  rare: 'border-blue-500 bg-blue-900/20',
  epic: 'border-purple-500 bg-purple-900/20',
  legendary: 'border-yellow-500 bg-yellow-900/20'
}

const RARITY_COLORS = {
  common: 'text-gray-400',
  rare: 'text-blue-400',
  epic: 'text-purple-400',
  legendary: 'text-yellow-400'
}

export const DeckPage: React.FC = () => {
  const { user } = useAuthStore()
  const {
    decks,
    currentDeck,
    availableCards,
    getDecks,
    getDeck,
    createDeck,
    updateDeck,
    deleteDeck,
    setCurrentDeck,
    getAvailableCards
  } = useDeckStore()
  const { addNotification } = useUIStore()

  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null)
  const [isCreatingDeck, setIsCreatingDeck] = useState(false)
  const [isEditingDeck, setIsEditingDeck] = useState(false)
  const [deckName, setDeckName] = useState('')
  const [deckDescription, setDeckDescription] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRarity, setSelectedRarity] = useState<string>('all')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedCost, setSelectedCost] = useState<string>('all')
  const [isCardCollectionOpen, setIsCardCollectionOpen] = useState(false)

  // 获取卡组列表
  useEffect(() => {
    const fetchDecks = async () => {
      try {
        await getDecks()
      } catch (error) {
        console.error('Failed to fetch decks:', error)
        addNotification('error', '获取卡组列表失败')
      }
    }

    fetchDecks()
  }, [getDecks, addNotification])

  // 获取可用卡牌
  useEffect(() => {
    const fetchAvailableCards = async () => {
      try {
        await getAvailableCards()
      } catch (error) {
        console.error('Failed to fetch available cards:', error)
        addNotification('error', '获取卡牌列表失败')
      }
    }

    fetchAvailableCards()
  }, [getAvailableCards, addNotification])

  // 获取选中的卡组详情
  useEffect(() => {
    if (selectedDeck) {
      const fetchDeck = async () => {
        try {
          await getDeck(selectedDeck.id)
        } catch (error) {
          console.error('Failed to fetch deck details:', error)
          addNotification('error', '获取卡组详情失败')
        }
      }

      fetchDeck()
    }
  }, [selectedDeck, getDeck, addNotification])

  const handleCreateDeck = async () => {
    if (!deckName.trim()) {
      addNotification('error', '请输入卡组名称')
      return
    }

    try {
      await createDeck({
        name: deckName,
        description: deckDescription,
        cards: []
      })

      setIsCreatingDeck(false)
      setDeckName('')
      setDeckDescription('')
      addNotification('success', '卡组创建成功')
      await getDecks()
    } catch (error) {
      console.error('Failed to create deck:', error)
      addNotification('error', '创建卡组失败')
    }
  }

  const handleUpdateDeck = async () => {
    if (!selectedDeck || !deckName.trim()) {
      addNotification('error', '请输入卡组名称')
      return
    }

    try {
      await updateDeck(selectedDeck.id, {
        name: deckName,
        description: deckDescription
      })

      setIsEditingDeck(false)
      addNotification('success', '卡组更新成功')
      await getDecks()
    } catch (error) {
      console.error('Failed to update deck:', error)
      addNotification('error', '更新卡组失败')
    }
  }

  const handleDeleteDeck = async (deckId: string) => {
    if (!confirm('确定要删除这个卡组吗？此操作不可恢复。')) {
      return
    }

    try {
      await deleteDeck(deckId)
      addNotification('success', '卡组删除成功')
      await getDecks()

      if (selectedDeck?.id === deckId) {
        setSelectedDeck(null)
      }
    } catch (error) {
      console.error('Failed to delete deck:', error)
      addNotification('error', '删除卡组失败')
    }
  }

  const handleSetCurrentDeck = async (deckId: string) => {
    try {
      await setCurrentDeck(deckId)
      addNotification('success', '当前卡组已设置')
      await getDecks()
    } catch (error) {
      console.error('Failed to set current deck:', error)
      addNotification('error', '设置当前卡组失败')
    }
  }

  const filteredCards = availableCards.filter(card => {
    const matchesSearch = card.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         card.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRarity = selectedRarity === 'all' || card.rarity === selectedRarity
    const matchesType = selectedType === 'all' || card.type === selectedType
    const matchesCost = selectedCost === 'all' || card.cost.toString() === selectedCost

    return matchesSearch && matchesRarity && matchesType && matchesCost
  })

  const getManaIcon = (cost: number) => {
    const icons = []
    for (let i = 0; i < cost; i++) {
      icons.push(<BoltIcon key={i} className="h-3 w-3 text-blue-400" />)
    }
    return icons
  }

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">卡组管理</h1>
          <p className="text-gray-400">
            创建和管理您的卡组，构建最强阵容
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 卡组列表 */}
          <div className="lg:col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">我的卡组</h2>
              <Button
                onClick={() => setIsCreatingDeck(true)}
                className="p-2"
                title="创建新卡组"
              >
                <PlusIcon className="h-5 w-5" />
              </Button>
            </div>

            <div className="space-y-4">
              {decks.map((deck) => (
                <div
                  key={deck.id}
                  className={`
                    rounded-lg border-2 p-4 cursor-pointer transition-all duration-200
                    ${selectedDeck?.id === deck.id
                      ? 'border-primary-500 bg-primary-900/20'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }
                    ${deck.isCurrent ? 'ring-2 ring-green-500' : ''}
                  `}
                  onClick={() => setSelectedDeck(deck)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-white font-medium">{deck.name}</h3>
                      <p className="text-gray-400 text-sm mt-1">{deck.description}</p>
                    </div>
                    {deck.isCurrent && (
                      <ShieldCheckIcon className="h-5 w-5 text-green-400" title="当前卡组" />
                    )}
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">
                      {deck.cardCount} 张卡牌
                    </span>
                    {deck.winRate !== undefined && (
                      <span className="text-green-400">
                        胜率 {deck.winRate}%
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2 mt-3">
                    {!deck.isCurrent && (
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSetCurrentDeck(deck.id)
                        }}
                        variant="outline"
                        className="text-xs px-2 py-1"
                      >
                        设为当前
                      </Button>
                    )}
                    <Button
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedDeck(deck)
                        setIsEditingDeck(true)
                      }}
                      variant="outline"
                      className="text-xs px-2 py-1"
                    >
                      <PencilIcon className="h-3 w-3" />
                    </Button>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteDeck(deck.id)
                      }}
                      variant="outline"
                      className="text-xs px-2 py-1 text-red-400"
                    >
                      <TrashIcon className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}

              {decks.length === 0 && (
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
                  <DocumentTextIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">您还没有创建任何卡组</p>
                  <p className="text-gray-500 text-sm mt-1">
                    点击上方的 + 按钮创建您的第一个卡组
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 卡组详情 */}
          <div className="lg:col-span-2">
            {selectedDeck ? (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-white">
                    {selectedDeck.name}
                  </h2>
                  <Button
                    onClick={() => setIsCardCollectionOpen(true)}
                    className="flex items-center space-x-2"
                  >
                    <PlusIcon className="h-4 w-4" />
                    <span>添加卡牌</span>
                  </Button>
                </div>

                <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                  {/* 卡组统计 */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-white">
                        {selectedDeck.cardCount}
                      </p>
                      <p className="text-sm text-gray-400">总卡牌数</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-400">
                        {Math.round(selectedDeck.cards?.reduce((sum, card) => sum + card.cost, 0) / selectedDeck.cardCount || 0)}
                      </p>
                      <p className="text-sm text-gray-400">平均法力值</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-400">
                        {selectedDeck.cards?.filter(card => card.type === 'minion').length || 0}
                      </p>
                      <p className="text-sm text-gray-400">随从数</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-400">
                        {selectedDeck.cards?.filter(card => card.type === 'spell').length || 0}
                      </p>
                      <p className="text-sm text-gray-400">法术数</p>
                    </div>
                  </div>

                  {/* 卡牌列表 */}
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {selectedDeck.cards?.map((card, index) => (
                      <div
                        key={`${card.id}-${index}`}
                        className={`border rounded-lg p-3 ${CARD_COLORS[card.rarity]}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center space-x-1">
                              {getManaIcon(card.cost)}
                            </div>
                            <div>
                              <p className="text-white font-medium">{card.name}</p>
                              <p className="text-gray-400 text-sm">
                                {card.type === 'minion' ? `${card.attack}/${card.health}` : '法术'}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`text-xs px-2 py-1 rounded ${RARITY_COLORS[card.rarity]}`}>
                              {card.rarity === 'common' ? '普通' :
                               card.rarity === 'rare' ? '稀有' :
                               card.rarity === 'epic' ? '史诗' : '传说'}
                            </span>
                            {card.count && card.count > 1 && (
                              <span className="bg-gray-700 text-white text-xs px-2 py-1 rounded">
                                x{card.count}
                              </span>
                            )}
                          </div>
                        </div>
                        <p className="text-gray-400 text-sm mt-2">
                          {card.description}
                        </p>
                      </div>
                    ))}

                    {(!selectedDeck.cards || selectedDeck.cards.length === 0) && (
                      <div className="text-center py-8">
                        <SparklesIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-400">这个卡组还没有卡牌</p>
                        <p className="text-gray-500 text-sm mt-1">
                          点击"添加卡牌"开始构建您的卡组
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
                <DocumentTextIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  选择一个卡组
                </h3>
                <p className="text-gray-400">
                  从左侧选择一个卡组来查看详情，或者创建一个新的卡组
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 创建卡组模态框 */}
        {isCreatingDeck && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsCreatingDeck(false)} />
              <div className="relative bg-gray-800 rounded-lg p-6 max-w-md w-full border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">创建新卡组</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      卡组名称
                    </label>
                    <input
                      type="text"
                      value={deckName}
                      onChange={(e) => setDeckName(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="输入卡组名称"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      卡组描述（可选）
                    </label>
                    <textarea
                      value={deckDescription}
                      onChange={(e) => setDeckDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={3}
                      placeholder="输入卡组描述"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <Button
                    onClick={() => setIsCreatingDeck(false)}
                    variant="outline"
                  >
                    取消
                  </Button>
                  <Button onClick={handleCreateDeck}>
                    创建
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 编辑卡组模态框 */}
        {isEditingDeck && selectedDeck && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsEditingDeck(false)} />
              <div className="relative bg-gray-800 rounded-lg p-6 max-w-md w-full border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">编辑卡组</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      卡组名称
                    </label>
                    <input
                      type="text"
                      value={deckName || selectedDeck.name}
                      onChange={(e) => setDeckName(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="输入卡组名称"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      卡组描述（可选）
                    </label>
                    <textarea
                      value={deckDescription || selectedDeck.description}
                      onChange={(e) => setDeckDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={3}
                      placeholder="输入卡组描述"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <Button
                    onClick={() => setIsEditingDeck(false)}
                    variant="outline"
                  >
                    取消
                  </Button>
                  <Button onClick={handleUpdateDeck}>
                    保存
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 卡牌收藏模态框 */}
        {isCardCollectionOpen && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsCardCollectionOpen(false)} />
              <div className="relative bg-gray-800 rounded-lg p-6 max-w-4xl w-full border border-gray-700 max-h-[80vh] overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">选择卡牌</h3>
                  <Button
                    onClick={() => setIsCardCollectionOpen(false)}
                    variant="outline"
                    className="p-2"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </Button>
                </div>

                {/* 搜索和筛选 */}
                <div className="space-y-4 mb-6">
                  <div className="relative">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="搜索卡牌..."
                    />
                  </div>

                  <div className="flex items-center space-x-4">
                    <select
                      value={selectedRarity}
                      onChange={(e) => setSelectedRarity(e.target.value)}
                      className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="all">所有稀有度</option>
                      <option value="common">普通</option>
                      <option value="rare">稀有</option>
                      <option value="epic">史诗</option>
                      <option value="legendary">传说</option>
                    </select>

                    <select
                      value={selectedType}
                      onChange={(e) => setSelectedType(e.target.value)}
                      className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="all">所有类型</option>
                      <option value="minion">随从</option>
                      <option value="spell">法术</option>
                      <option value="weapon">武器</option>
                    </select>

                    <select
                      value={selectedCost}
                      onChange={(e) => setSelectedCost(e.target.value)}
                      className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="all">所有法力值</option>
                      <option value="0">0</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                      <option value="5">5</option>
                      <option value="6">6+</option>
                    </select>
                  </div>
                </div>

                {/* 卡牌列表 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto max-h-96">
                  {filteredCards.map((card) => (
                    <div
                      key={card.id}
                      className={`border rounded-lg p-3 cursor-pointer hover:opacity-80 transition-opacity ${CARD_COLORS[card.rarity]}`}
                      onClick={() => {
                        // 这里应该处理添加卡牌到卡组的逻辑
                        addNotification('info', `添加 ${card.name} 到卡组`)
                      }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-1">
                          {getManaIcon(card.cost)}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${RARITY_COLORS[card.rarity]}`}>
                          {card.rarity === 'common' ? '普通' :
                           card.rarity === 'rare' ? '稀有' :
                           card.rarity === 'epic' ? '史诗' : '传说'}
                        </span>
                      </div>
                      <h4 className="text-white font-medium">{card.name}</h4>
                      <p className="text-gray-400 text-sm">
                        {card.type === 'minion' ? `${card.attack}/${card.health}` : '法术'}
                      </p>
                      <p className="text-gray-500 text-xs mt-2">
                        {card.description}
                      </p>
                    </div>
                  ))}

                  {filteredCards.length === 0 && (
                    <div className="col-span-full text-center py-8">
                      <MagnifyingGlassIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                      <p className="text-gray-400">没有找到匹配的卡牌</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  )
}

export default DeckPage