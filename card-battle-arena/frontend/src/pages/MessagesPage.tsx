import React from 'react'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

export const MessagesPage: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <ChatBubbleLeftRightIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">消息中心</h1>
          <p className="text-gray-400 mb-6">
            消息系统将在后续版本中实现
          </p>
          <div className="text-sm text-gray-500">
            <p>将包含：好友消息、系统通知、对战邀请等</p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default MessagesPage