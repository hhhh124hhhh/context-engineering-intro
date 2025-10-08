// 测试修复的文件
import React from 'react'

// 测试Heroicons导入
import { StarIcon, TrophyIcon, SpeakerWaveIcon } from '@heroicons/react/24/outline'

console.log('✅ Heroicons 导入测试通过:', { StarIcon, TrophyIcon, SpeakerWaveIcon })

// 测试组件渲染
const TestComponent = () => {
  return (
    <div style={{ padding: '20px', background: '#1f2937', color: 'white', minHeight: '100vh' }}>
      <h1>测试页面</h1>
      <p>如果你能看到这个页面，说明基本功能正常</p>
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        <StarIcon style={{ width: '24px', height: '24px', color: 'yellow' }} />
        <TrophyIcon style={{ width: '24px', height: '24px', color: 'gray' }} />
        <SpeakerWaveIcon style={{ width: '24px', height: '24px', color: 'blue' }} />
      </div>
    </div>
  )
}

export default TestComponent