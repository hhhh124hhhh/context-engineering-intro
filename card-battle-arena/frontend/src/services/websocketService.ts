class WebSocketService {
  private connections: Map<string, WebSocket> = new Map()
  private listeners: Map<string, Array<(data: any) => void>> = new Map()
  private reconnectAttempts: Map<string, number> = new Map()
  private maxReconnectAttempts = 5
  private heartbeatInterval: NodeJS.Timeout | null = null

  // 连接到WebSocket
  connect(url: string, userId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(url)

        ws.onopen = () => {
          console.log(`WebSocket连接已建立: ${url}`)
          this.connections.set(url, ws)
          this.reconnectAttempts.delete(url)

          // 发送连接消息
          if (userId) {
            this.sendMessage(url, {
              type: 'connect',
              user_id: userId,
              timestamp: Date.now()
            })
          }

          resolve()
        }

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(url, message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        ws.onclose = (event) => {
          console.log(`WebSocket连接已关闭: ${url}, 代码: ${event.code}`)
          this.connections.delete(url)

          // 如果不是正常关闭，尝试重连
          if (event.code !== 1000) {
            this.attemptReconnect(url)
          }
        }

        ws.onerror = (error) => {
          console.error(`WebSocket连接错误: ${url}`, error)
          reject(error)
        }

      } catch (error) {
        reject(error)
      }
    })
  }

  // 断开连接
  disconnect(url: string): void {
    const ws = this.connections.get(url)
    if (ws) {
      ws.close(1000, '用户主动断开')
      this.connections.delete(url)
      this.reconnectAttempts.delete(url)
    }
  }

  // 发送消息
  sendMessage(url: string, message: any): boolean {
    const ws = this.connections.get(url)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
      return true
    }
    return false
  }

  // 广播消息到所有连接
  broadcast(message: any): void {
    this.connections.forEach((ws, url) => {
      this.sendMessage(url, message)
    })
  }

  // 监听消息
  onMessage(url: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(url)) {
      this.listeners.set(url, [])
    }

    const listeners = this.listeners.get(url)!
    listeners.push(callback)

    // 返回取消监听的函数
    return () => {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  // 处理接收到的消息
  private handleMessage(url: string, message: any): void {
    const listeners = this.listeners.get(url)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('WebSocket消息处理器错误:', error)
        }
      })
    }

    // 触发全局事件
    window.dispatchEvent(new CustomEvent('websocketMessage', {
      detail: { url, message }
    }))
  }

  // 尝试重连
  private attemptReconnect(url: string): void {
    const attempts = this.reconnectAttempts.get(url) || 0

    if (attempts < this.maxReconnectAttempts) {
      this.reconnectAttempts.set(url, attempts + 1)

      const delay = Math.min(1000 * Math.pow(2, attempts), 10000) // 指数退避，最大10秒

      console.log(`尝试重连WebSocket (${attempts + 1}/${this.maxReconnectAttempts}): ${url}`)

      setTimeout(() => {
        this.connect(url).catch(error => {
          console.error('WebSocket重连失败:', error)
        })
      }, delay)
    } else {
      console.error(`WebSocket重连失败，已达到最大重试次数: ${url}`)
      this.reconnectAttempts.delete(url)
    }
  }

  // 开始心跳
  startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
    }

    this.heartbeatInterval = setInterval(() => {
      this.broadcast({
        type: 'ping',
        timestamp: Date.now()
      })
    }, 30000) // 每30秒发送一次心跳
  }

  // 停止心跳
  stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  // 获取连接状态
  isConnected(url: string): boolean {
    const ws = this.connections.get(url)
    return ws !== undefined && ws.readyState === WebSocket.OPEN
  }

  // 获取所有连接状态
  getAllConnections(): { url: string; connected: boolean }[] {
    return Array.from(this.connections.entries()).map(([url, ws]) => ({
      url,
      connected: ws.readyState === WebSocket.OPEN
    }))
  }

  // 清理所有连接
  disconnectAll(): void {
    this.connections.forEach((ws, url) => {
      ws.close(1000, '应用关闭')
    })
    this.connections.clear()
    this.listeners.clear()
    this.reconnectAttempts.clear()
    this.stopHeartbeat()
  }
}

export const websocketService = new WebSocketService()
export default websocketService