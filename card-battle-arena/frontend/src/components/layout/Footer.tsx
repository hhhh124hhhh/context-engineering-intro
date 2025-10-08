import React from 'react'
import {
  GlobeAltIcon,
  GithubIcon,
  EnvelopeIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 border-t border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* 关于我们 */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">
              关于游戏
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  游戏介绍
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  开发团队
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  联系我们
                </a>
              </li>
            </ul>
          </div>

          {/* 游戏资源 */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">
              游戏资源
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  卡牌数据库
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  游戏规则
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  新手指南
                </a>
              </li>
            </ul>
          </div>

          {/* 社区 */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">
              社区
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Discord
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Reddit
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  论坛
                </a>
              </li>
            </ul>
          </div>

          {/* 支持 */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">
              支持
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  帮见问题
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  用户协议
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  隐私政策
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* 底部版权信息 */}
        <div className="mt-8 border-t border-gray-700 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <ShieldCheckIcon className="h-4 w-4 text-green-400" />
              <span>安全可靠的卡牌对战平台</span>
            </div>

            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <a
                href="https://github.com/cardbattle/card-battle-arena"
                className="text-gray-400 hover:text-white"
                target="_blank"
                rel="noopener noreferrer"
              >
                <GithubIcon className="h-5 w-5" />
              </a>
              <a
                href="mailto:support@cardbattle.arena"
                className="text-gray-400 hover:text-white"
              >
                <EnvelopeIcon className="h-5 w-5" />
              </a>
              <a
                href="https://cardbattle.arena"
                className="text-gray-400 hover:text-white"
                target="_blank"
                rel="noopener noreferrer"
              >
                <GlobeAltIcon className="h-5 w-5" />
              </a>
            </div>

            <p className="text-xs text-gray-400 mt-4 md:mt-0">
              © 2024 卡牌对战竞技场. 保留所有权利.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer