import React, { useState } from 'react'
import { Button } from '@components/ui/Button'
import { ErrorBoundary } from '@components/ui/ErrorBoundary'
import {
  Cog6ToothIcon,
  BellIcon,
  SpeakerWaveIcon,
  EyeIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', name: '通用', icon: Cog6ToothIcon },
    { id: 'notifications', name: '通知', icon: BellIcon },
    { id: 'audio', name: '音频', icon: SpeakerWaveIcon },
    { id: 'appearance', name: '外观', icon: EyeIcon },
    { id: 'language', name: '语言', icon: GlobeAltIcon },
    { id: 'privacy', name: '隐私', icon: ShieldCheckIcon },
    { id: 'about', name: '关于', icon: InformationCircleIcon }
  ]

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">设置</h1>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* 侧边栏 */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                      ${activeTab === tab.id
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* 设置内容 */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              {activeTab === 'general' && (
                <div>
                  <h2 className="text-xl font-semibold text-white mb-4">通用设置</h2>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">自动登录</p>
                        <p className="text-gray-400 text-sm">登录时自动保存凭据</p>
                      </div>
                      <input type="checkbox" className="toggle" defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">显示在线状态</p>
                        <p className="text-gray-400 text-sm">让其他玩家看到您在线</p>
                      </div>
                      <input type="checkbox" className="toggle" defaultChecked />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'about' && (
                <div>
                  <h2 className="text-xl font-semibold text-white mb-4">关于</h2>
                  <div className="space-y-4">
                    <div>
                      <p className="text-white font-medium">卡牌对战竞技场</p>
                      <p className="text-gray-400 text-sm">版本 1.0.0</p>
                    </div>
                    <div>
                      <p className="text-white font-medium">开发者</p>
                      <p className="text-gray-400 text-sm">Card Battle Arena Team</p>
                    </div>
                    <div className="pt-4">
                      <Button variant="outline">
                        <DocumentTextIcon className="h-4 w-4 mr-2" />
                        查看用户协议
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab !== 'general' && activeTab !== 'about' && (
                <div className="text-center py-8">
                  <Cog6ToothIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">此设置页面正在开发中</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default SettingsPage