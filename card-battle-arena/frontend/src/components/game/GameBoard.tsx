import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useGameState } from '@/hooks/useGameState'
import { useSocket } from '@/hooks/useSocket'
import { cn } from '@/utils/classnames'
import { Hand } from './Hand'
import { Battlefield } from './Battlefield'
import { TurnTimer } from './TurnTimer'
import { PlayerInfo } from './PlayerInfo'
import { GameLog } from './GameLog'
import { MenuBar } from './MenuBar'
import { Card, CardBack } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { LoadingScreen } from '@/components/ui/LoadingScreen'
import type { CardInstance } from '@/types/game'

interface GameBoardProps {
  gameId: string
  playerId: string
  onLeaveGame?: () => void
  onConcede?: () => void
}

export const GameBoard: React.FC<GameBoardProps> = ({
  gameId,
  playerId,
  onLeaveGame,
  onConcede,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isSpectator, setIsSpectator] = useState(false)
  const [showGameLog, setShowGameLog] = useState(false)

  const { gameState, isLoading, playCard, endTurn, concede } = useGameState(gameId)
  const socket = useSocket()

  const currentPlayer = gameState?.currentPlayer
  const opponent = gameState?.opponent
  const isMyTurn = currentPlayer?.user_id === playerId

  const handleCardPlay = useCallback(async (cardId: string, target?: string) => {
    if (!isMyTurn) return

    try {
      await playCard(cardId, target)
    } catch (error) {
      console.error('Failed to play card:', error)
    }
  }, [isMyTurn, playCard])

  const handleEndTurn = useCallback(async () => {
    if (!isMyTurn) return

    try {
      await endTurn()
    } catch (error) {
      console.error('Failed to end turn:', error)
    }
  }, [isMyTurn, endTurn])

  const handleConcede = useCallback(async () => {
    try {
      await concede()
      onConcede?.()
    } catch (error) {
      console.error('Failed to concede:', error)
    }
  }, [concede, onConcede])

  const handleLeaveGame = useCallback(() => {
    socket.emit('leave_game', { game_id: gameId })
    onLeaveGame?.()
  }, [gameId, socket, onLeaveGame])

  // 渲染玩家手牌
  const renderPlayerHand = (player: any, isOpponent = false) => {
    const hand = player?.hand || []
    const maxCards = 10
    const displayCards = isOpponent ? Math.min(hand.length, 10) : hand

    return (
      <div className={cn('relative', isOpponent && 'scale-y-100')}>
        <Hand
          cards={displayCards}
          isOpponent={isOpponent}
          maxCards={maxCards}
          onCardPlay={isOpponent ? undefined : handleCardPlay}
          disabled={!isMyTurn && !isOpponent}
        />

        {/* 对手手牌遮罩效果 */}
        {isOpponent && hand.length > 10 && (
          <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/90 to-transparent pointer-events-none" />
        )}

        {/* 对手手牌提示 */}
        {isOpponent && hand.length > 10 && (
          <div className="absolute -top-2 right-2 bg-gray-800 text-white text-xs px-2 py-1 rounded">
            +{hand.length - 10}
          </div>
        )}
      </div>
    )
  }

  // 渲染战场
  const renderBattlefield = (player: any, isOpponent = false) => {
    const battlefield = player?.battlefield || []

    return (
      <Battlefield
        cards={battlefield}
        isOpponent={isOpponent}
        onCardClick={handleCardPlay}
        disabled={!isMyTurn && !isOpponent}
      />
    )
  }

  // 渲染英雄状态
  const renderHeroState = (player: any, isOpponent = false) => {
    return (
      <div className="flex flex-col items-center space-y-2">
        {/* 英雄头像 */}
        <div className="relative">
          <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center border-2 border-gray-600">
            <div className="text-2xl">
              {player?.card_class === 'warrior' && '⚔️'}
              {player?.card_class === 'mage' && '🧙‍♂️'}
              {player?.card_class === 'hunter' && '🏹'}
              {player?.card_class === 'rogue' && '🗡️'}
              {player?.card_class === 'priest' && '✝️'}
              {player?.card_class === 'warlock' && '🔮'}
              {player?.card_class === 'shaman' && '⚡'}
              {player?.card_class === 'paladin' && '⚔️'}
              {player?. card_class === 'druid' && '🌿'}
              {player?.card_class === 'neutral' && '🎯'}
            </div>
          </div>

          {/* 武器 */}
          {player?.weapon && (
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center border border-orange-500">
              <span className="text-xs text-white">⚔️</span>
            </div>
          )}
        </div>

        {/* 生命值和护甲 */}
        <div className="flex flex-col items-center space-y-1">
          <div className="flex items-center space-x-2">
            <div className="text-blue-400 font-bold text-lg">
              {player?.armor || 0}
            </div>
            <div className="text-white font-bold text-xl">
              {player?.health || 0}
            </div>
          </div>
          <div className="text-xs text-gray-400">
            HP: {player?.effective_health || 0}
          </div>
        </div>

        {/* 法力值 */}
        <div className="flex items-center space-x-2">
          <div className="text-purple-400 font-bold">
            {player?.mana || 0}
          </div>
          <div className="text-gray-400 text-sm">
            / {player?.max_mana || 0}
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return <LoadingScreen message="加载游戏..." />
  }

  if (!gameState) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">游戏未找到</h1>
          <Button onClick={handleLeaveGame}>返回大厅</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* 游戏背景 */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-black opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-indigo-900/20" />
      </div>

      {/* 顶部菜单栏 */}
      <MenuBar
        isOpen={isMenuOpen}
        onToggle={() => setIsMenuOpen(!isMenuOpen)}
        onConcede={handleConcede}
        onLeave={handleLeaveGame}
        onToggleSpectator={() => setIsSpectator(!isSpectator)}
        onToggleLog={() => setShowGameLog(!showGameLog)}
        isSpectator={isSpectator}
        canConcede={currentPlayer?.user_id === playerId}
      />

      {/* 游戏主界面 */}
      <div className="flex h-full">
        {/* 左侧 - 对手区域 */}
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          {renderHeroState(opponent, true)}
          {renderBattlefield(opponent, true)}
          {renderPlayerHand(opponent, true)}
        </div>

        {/* 中间 - 分隔线 */}
        <div className="flex flex-col items-center justify-center">
          <div className="h-1/2 w-px bg-gradient-to-b from-primary-400 to-primary-600" />

          {/* 回合指示器 */}
          <div className="my-4">
            <TurnTimer
              isActive={isMyTurn}
              timeLeft={gameState?.turn_time_limit || 90}
              currentPlayer={gameState?.current_player_number}
              turnNumber={gameState?.turn_number}
            />
          </div>

          <div className="h-1/2 w-px bg-gradient-to-t from-primary-600 to-primary-400" />
        </div>

        {/* 右侧 - 玩家区域 */}
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          {renderPlayerHand(currentPlayer, false)}
          {renderBattlefield(currentPlayer, false)}
          {renderHeroState(currentPlayer, false)}
        </div>
      </div>

      {/* 玩家标记 */}
      {isSpectator && (
        <div className="absolute top-4 right-4 bg-yellow-600 text-white px-3 py-1 rounded-lg text-sm font-medium">
          观战模式
        </div>
      )}

      {/* 游戏日志 */}
      {showGameLog && (
        <div className="absolute bottom-4 left-4 right-4">
          <GameLog logs={gameState?.action_history || []} />
        </div>
      )}

      {/* 游戏结束覆盖层 */}
      <AnimatePresence>
        {gameState?.is_game_over && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-800 rounded-xl p-8 text-center max-w-md"
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                游戏结束！
              </h2>

              <div className="mb-6">
                {gameState.winner?.user_id === playerId ? (
                  <>
                    <div className="text-6xl mb-2">🎉</div>
                    <p className="text-xl text-green-400">你赢了！</p>
                  </>
                ) : (
                  <>
                    <div className="text-6xl mb-2">😔</div>
                    <p className="text-xl text-red-400">你输了</p>
                  </>
                )}
              </div>

              <div className="flex space-x-4 justify-center">
                <Button onClick={handleLeaveGame}>
                  返回大厅
                </Button>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  再来一局
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default GameBoard