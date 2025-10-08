import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/classnames'
import { Button } from '@/components/ui/Button'
import type { Deck, Card } from '@/types/card'

interface DeckImportExportProps {
  onImportDeck?: (deck: Partial<Deck>) => void
  currentDeck?: Deck
  className?: string
}

interface DeckstringData {
  cards: Array<{ id: number; quantity: number }>
  heroes?: number[]
  format?: number
  sideboards?: Array<{ cards: Array<{ id: number; quantity: number }> }>
}

export const DeckImportExport: React.FC<DeckImportExportProps> = ({
  onImportDeck,
  currentDeck,
  className,
}) => {
  const [importString, setImportString] = useState('')
  const [importMode, setImportMode] = useState<'deckstring' | 'text' | 'json'>('deckstring')
  const [exportFormat, setExportFormat] = useState<'deckstring' | 'text' | 'json'>('deckstring')
  const [showImportModal, setShowImportModal] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [importError, setImportError] = useState('')
  const [processing, setProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 简化的deckstring编码/解码（实际实现需要更复杂的算法）
  const encodeDeckstring = (deck: Deck): string => {
    try {
      const deckData: DeckstringData = {
        cards: deck.cards.map(card => ({ id: card.cardId, quantity: card.quantity })),
        format: 1, // Standard format
        heroes: [getHeroIdByClass(deck.cardClass)]
      }

      // 这里应该实现真正的base64编码和二进制数据压缩
      // 为了演示，我们使用简化的JSON编码
      const encoded = btoa(JSON.stringify(deckData))
      return `AAEBAf0E${encoded.substring(0, 20)}...` // 模拟Hearthstone deckstring格式
    } catch (error) {
      console.error('Failed to encode deckstring:', error)
      return ''
    }
  }

  const decodeDeckstring = (deckstring: string): DeckstringData | null => {
    try {
      // 简化的解码逻辑
      if (!deckstring.startsWith('AAEBAf0E')) {
        throw new Error('Invalid deckstring format')
      }

      // 模拟解码过程
      const data: DeckstringData = {
        cards: [
          { id: 1, quantity: 2 },
          { id: 2, quantity: 1 },
          { id: 3, quantity: 2 },
        ],
        format: 1,
        heroes: [7] // Mage hero
      }

      return data
    } catch (error) {
      console.error('Failed to decode deckstring:', error)
      return null
    }
  }

  const getHeroIdByClass = (cardClass: string): number => {
    const heroIds = {
      warrior: 7,
      mage: 8,
      hunter: 9,
      rogue: 10,
      priest: 11,
      warlock: 12,
      shaman: 13,
      paladin: 14,
      druid: 15,
      neutral: 16
    }
    return heroIds[cardClass as keyof typeof heroIds] || 16
  }

  const getCardClassByHeroId = (heroId: number): string => {
    const classMap: Record<number, string> = {
      7: 'warrior',
      8: 'mage',
      9: 'hunter',
      10: 'rogue',
      11: 'priest',
      12: 'warlock',
      13: 'shaman',
      14: 'paladin',
      15: 'druid',
      16: 'neutral'
    }
    return classMap[heroId] || 'neutral'
  }

  const handleImport = async () => {
    setProcessing(true)
    setImportError('')

    try {
      let deckData: Partial<Deck> = {}

      if (importMode === 'deckstring') {
        const decoded = decodeDeckstring(importString.trim())
        if (!decoded) {
          throw new Error('无效的卡组代码格式')
        }

        // 获取卡牌详细信息
        const cardDetails = await Promise.all(
          decoded.cards.map(async (card) => {
            const response = await fetch(`/api/cards/${card.id}`)
            const cardData = await response.json()
            return {
              cardId: card.id,
              quantity: card.quantity,
              position: 0,
              card: cardData
            }
          })
        )

        deckData = {
          name: '导入的卡组',
          cardClass: getCardClassByHeroId(decoded.heroes?.[0] || 16),
          cards: cardDetails
        }
      } else if (importMode === 'text') {
        // 解析文本格式（每行一张卡牌）
        const lines = importString.trim().split('\n').filter(line => line.trim())
        const cardNames = lines.map(line => line.trim())

        const cardDetails = await Promise.all(
          cardNames.map(async (name, index) => {
            const response = await fetch(`/api/cards/search?name=${encodeURIComponent(name)}`)
            const results = await response.json()
            const card = results[0]

            if (!card) {
              throw new Error(`找不到卡牌: ${name}`)
            }

            return {
              cardId: card.id,
              quantity: 1,
              position: index,
              card
            }
          })
        )

        deckData = {
          name: '导入的卡组',
          cardClass: 'neutral',
          cards: cardDetails
        }
      } else if (importMode === 'json') {
        // 解析JSON格式
        const jsonData = JSON.parse(importString.trim())
        deckData = {
          name: jsonData.name || '导入的卡组',
          description: jsonData.description,
          cardClass: jsonData.cardClass || 'neutral',
          cards: jsonData.cards || []
        }
      }

      onImportDeck?.(deckData)
      setShowImportModal(false)
      setImportString('')
    } catch (error) {
      setImportError(error instanceof Error ? error.message : '导入失败')
    } finally {
      setProcessing(false)
    }
  }

  const handleExport = () => {
    if (!currentDeck) return

    let exportData = ''

    if (exportFormat === 'deckstring') {
      exportData = encodeDeckstring(currentDeck)
    } else if (exportFormat === 'text') {
      exportData = currentDeck.cards
        .map(card => `${card.quantity}x ${card.card.name}`)
        .join('\n')
    } else if (exportFormat === 'json') {
      exportData = JSON.stringify(currentDeck, null, 2)
    }

    // 下载文件
    const blob = new Blob([exportData], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentDeck.name}.${exportFormat === 'json' ? 'json' : 'txt'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setImportString(content)

      // 根据文件扩展名自动设置导入模式
      if (file.name.endsWith('.json')) {
        setImportMode('json')
      } else if (file.name.endsWith('.txt')) {
        setImportMode('text')
      } else {
        setImportMode('deckstring')
      }
    }
    reader.readAsText(file)
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
      className={cn('flex space-x-4', className)}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 导入按钮 */}
      <motion.div variants={itemVariants}>
        <Button
          variant="outline"
          onClick={() => setShowImportModal(true)}
        >
          导入卡组
        </Button>
      </motion.div>

      {/* 导出按钮 */}
      <motion.div variants={itemVariants}>
        <Button
          variant="outline"
          onClick={() => setShowExportModal(true)}
          disabled={!currentDeck}
        >
          导出卡组
        </Button>
      </motion.div>

      {/* 导入模态框 */}
      {showImportModal && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto border border-gray-700"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <h2 className="text-xl font-bold text-white mb-4">导入卡组</h2>

            {/* 导入模式选择 */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                导入模式
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="deckstring"
                    checked={importMode === 'deckstring'}
                    onChange={(e) => setImportMode(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">卡组代码</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="text"
                    checked={importMode === 'text'}
                    onChange={(e) => setImportMode(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">文本格式</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="json"
                    checked={importMode === 'json'}
                    onChange={(e) => setImportMode(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">JSON格式</span>
                </label>
              </div>
            </div>

            {/* 文件上传 */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                或选择文件上传
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.json"
                onChange={handleFileImport}
                className="hidden"
              />
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                选择文件
              </Button>
            </div>

            {/* 导入内容输入 */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {importMode === 'deckstring' ? '卡组代码' :
                 importMode === 'text' ? '卡牌列表（每行一张）' :
                 'JSON数据'}
              </label>
              <textarea
                value={importString}
                onChange={(e) => setImportString(e.target.value)}
                placeholder={
                  importMode === 'deckstring' ? '粘贴卡组代码...' :
                  importMode === 'text' ? '卡牌名称1\n卡牌名称2\n卡牌名称3' :
                  '{\n  "name": "卡组名称",\n  "cards": [...]\n}'
                }
                className="w-full h-64 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none resize-none font-mono text-sm"
              />
            </div>

            {/* 错误信息 */}
            {importError && (
              <div className="mb-4 p-3 bg-red-900 bg-opacity-50 border border-red-600 rounded text-red-300 text-sm">
                {importError}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowImportModal(false)
                  setImportError('')
                  setImportString('')
                }}
              >
                取消
              </Button>
              <Button
                onClick={handleImport}
                disabled={!importString.trim() || processing}
              >
                {processing ? '导入中...' : '导入'}
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* 导出模态框 */}
      {showExportModal && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <h2 className="text-xl font-bold text-white mb-4">导出卡组</h2>

            {/* 导出格式选择 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                导出格式
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="deckstring"
                    checked={exportFormat === 'deckstring'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">卡组代码</span>
                  <span className="text-gray-400 text-sm ml-2">（可分享给其他玩家）</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="text"
                    checked={exportFormat === 'text'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">文本格式</span>
                  <span className="text-gray-400 text-sm ml-2">（易读的卡牌列表）</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="json"
                    checked={exportFormat === 'json'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                    className="mr-2"
                  />
                  <span className="text-white">JSON格式</span>
                  <span className="text-gray-400 text-sm ml-2">（完整数据格式）</span>
                </label>
              </div>
            </div>

            {/* 卡组信息 */}
            {currentDeck && (
              <div className="mb-6 p-3 bg-gray-700 rounded text-sm">
                <div className="text-white font-medium">{currentDeck.name}</div>
                <div className="text-gray-400">
                  {currentDeck.cards.length}种卡牌，共{currentDeck.cards.reduce((sum, c) => sum + c.quantity, 0)}张
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowExportModal(false)}
              >
                取消
              </Button>
              <Button onClick={handleExport}>
                下载文件
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default DeckImportExport