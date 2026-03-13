import axios from 'axios'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30_000,
})

// 注入 Token
http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// 统一错误处理
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!location.pathname.startsWith('/login')) {
        location.href = '/login'
      }
    }
    return Promise.reject(err.response?.data ?? err)
  }
)

export default http
