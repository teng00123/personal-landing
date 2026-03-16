/**
 * WebSocket 通知客户端 — Iteration 5
 * 自动重连、心跳保活、事件分发
 */
import { ref, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'

export function useWebSocket(channel = 'system') {
  const connected = ref(false)
  const messages  = ref([])
  let ws = null
  let pingTimer = null
  let reconnectTimer = null
  let retries = 0

  function connect() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${proto}://${location.host}/api/v1/ws/notifications?channel=${channel}`

    ws = new WebSocket(url)

    ws.onopen = () => {
      connected.value = true
      retries = 0
      // 每 20s 发 ping
      pingTimer = setInterval(() => ws?.readyState === 1 && ws.send('ping'), 20000)
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'pong' || data.type === 'heartbeat' || data.type === 'connected') return

        messages.value.unshift({ ...data, ts: Date.now() })
        if (messages.value.length > 50) messages.value.pop()

        // 系统消息弹出通知
        if (data.type === 'system') {
          ElNotification({
            title: data.level === 'error' ? '错误' : data.level === 'warning' ? '警告' : '通知',
            message: data.message,
            type: data.level === 'error' ? 'error' : data.level === 'warning' ? 'warning' : 'info',
            duration: 5000,
          })
        }
        // 部署通知
        if (data.type === 'deploy_update' && data.status === 'success') {
          ElNotification({ title: '部署成功 🎉', message: data.message, type: 'success', duration: 6000 })
        }
        if (data.type === 'deploy_update' && data.status === 'failed') {
          ElNotification({ title: '部署失败', message: data.message, type: 'error', duration: 8000 })
        }
      } catch {}
    }

    ws.onclose = () => {
      connected.value = false
      clearInterval(pingTimer)
      // 指数退避重连（最多 30s）
      const delay = Math.min(1000 * 2 ** retries, 30000)
      retries++
      reconnectTimer = setTimeout(connect, delay)
    }

    ws.onerror = () => ws?.close()
  }

  function disconnect() {
    clearInterval(pingTimer)
    clearTimeout(reconnectTimer)
    ws?.close()
  }

  onUnmounted(disconnect)

  return { connect, disconnect, connected, messages }
}
