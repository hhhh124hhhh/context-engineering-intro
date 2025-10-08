import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  UserGroupIcon,
  DocumentTextIcon,
  UserIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  TrophyIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline'
import { useUIStore } from '@stores/uiStore'

export const Sidebar: React.FC = () => {
  const location = useLocation()
  const { sidebarOpen } = useUIStore()

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const navigationItems = [
    {
      name: '主页',
      path: '/home',
      icon: HomeIcon,
      description: '游戏首页'
    },
    {
      name: '游戏大厅',
      path: '/lobby',
      icon: UserGroupIcon,
      description: '开始对战'
    },
    {
      name: '卡组管理',
      path: '/deck',
      icon: DocumentTextIcon,
      description: '管理卡组'
    },
    {
      name: '个人资料',
      path: '/profile',
      icon: UserIcon,
      description: '个人信息'
    },
  ]

  const secondaryItems = [
    {
      name: '排行榜',
      path: '/leaderboard',
      icon: TrophyIcon,
      description: '查看排名'
    },
    {
      name: '游戏统计',
      path: '/stats',
      icon: ChartBarIcon,
      description: '查看统计'
    },
    {
      name: '消息中心',
      path: '/messages',
      icon: ChatBubbleLeftRightIcon,
      description: '查看消息'
    },
    {
      name: '设置',
      path: '/settings',
      icon: Cog6ToothIcon,
      description: '系统设置'
    }
  ]

  return (
    <div className="flex flex-col h-full">
      {/* 主要导航 */}
      <nav className="flex-1 px-4 py-6">
        <ul className="space-y-2">
          {navigationItems.map((item) => (
            <li key={item.name}>
              <Link
                to={item.path}
                className={`
                  group flex items-center px-3 py-2 text-sm font-medium rounded-md
                  ${isActive(item.path)
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }
                  transition-colors duration-200
                `}
              >
                <item.icon
                  className={`
                    h-6 w-6 flex-shrink-0
                    ${isActive(item.path)
                      ? 'text-primary-200'
                      : 'text-gray-400 group-hover:text-gray-300'
                    }
                  `}
                />
                <span className="ml-3">{item.name}</span>
              </Link>
            </li>
          ))}
        </ul>

        {/* 分隔线 */}
        <div className="border-t border-gray-700 my-4" />

        {/* 次要导航 */}
        <div className="px-3">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            更多功能
          </h3>
          <ul className="space-y-1">
            {secondaryItems.map((item) => (
              <li key={item.name}>
                <Link
                  to={item.path}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md
                    ${isActive(item.path)
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                    }
                    transition-colors duration-200
                  `}
                >
                  <item.icon
                    className={`
                      h-5 w-5 flex-shrink-0
                      ${isActive(item.path)
                        ? 'text-gray-300'
                        : 'text-gray-500 group-hover:text-gray-400'
                      }
                    `}
                  />
                  <span className="ml-3">{item.name}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* 底部信息 */}
      <div className="flex-shrink-0 border-t border-gray-700 p-4">
        <div className="text-xs text-gray-400 text-center">
          <p>卡牌对战竞技场</p>
          <p>版本 1.0.0</p>
          <p className="mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-green-400 bg-green-900/20">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
              <span className="ml-1">在线</span>
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar