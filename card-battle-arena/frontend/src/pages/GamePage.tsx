import React from 'react'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import { PlayIcon } from '@heroicons/react/24/outline'

export const GamePage: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <PlayIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">游戏界面</h1>
          <p className="text-gray-400 mb-6">
            完整的游戏界面将在Phase 4中集成现有游戏组件时实现
          </p>
          <div className="text-sm text-gray-500">
            <p>当前状态：等待游戏界面集成阶段</p>
            <p className="mt-2">将包含：棋盘、卡牌显示、回合管理、对战界面等</p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default GamePage