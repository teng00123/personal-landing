import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30_000,
})

// ── 请求拦截：注入 Token ──────────────────────────────────
http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── 响应拦截：统一错误处理 ────────────────────────────────
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status  = err.response?.status
    const data    = err.response?.data

    // 提取错误信息（FastAPI 标准 detail 字段）
    let message = '请求失败'
    if (typeof data?.detail === 'string') {
      message = data.detail
    } else if (Array.isArray(data?.detail)) {
      // Pydantic 校验错误，取第一条
      message = data.detail[0]?.msg ?? '参数错误'
    } else if (typeof data === 'string') {
      message = data
    }

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!location.pathname.startsWith('/login')) {
        ElMessage.error('登录已过期，请重新登录')
        location.href = '/login'
      }
    } else if (status === 403) {
      ElMessage.error('权限不足')
    } else if (status === 422) {
      ElMessage.error(`参数错误：${message}`)
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    }

    // 抛出结构化错误，方便调用方使用 e?.detail
    return Promise.reject({ detail: message, status, raw: data })
  }
)

export default http
