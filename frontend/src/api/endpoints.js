import http from './http.js'

// ── Auth ────────────────────────────────────────────────
export const authApi = {
  login:    (data) => http.post('/auth/login', data),
  loginMfa: (data) => http.post('/auth/login/mfa', data),
  me:    ()     => http.get('/auth/me'),
}

// ── Profile ─────────────────────────────────────────────
export const profileApi = {
  get:    ()     => http.get('/profile'),
  update: (data) => http.put('/profile', data),
}

// ── Articles ─────────────────────────────────────────────
export const articlesApi = {
  // 公开
  list:        (p)       => http.get('/articles',              { params: p }),
  getBySlug:   (slug)    => http.get(`/articles/slug/${slug}`),
  // 管理员
  adminList:   (p)       => http.get('/articles/admin',        { params: p }),
  getById:     (id)      => http.get(`/articles/${id}`),
  create:      (d)       => http.post('/articles', d),
  update:      (id, d)   => http.put(`/articles/${id}`, d),
  remove:      (id)      => http.delete(`/articles/${id}`),
  // 迭代二
  uploadMd:    (fd)      => http.post('/articles/upload-md', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  importCsdn:  (url)     => http.post('/articles/import-csdn', { url }),
  uploadCover: (id, fd)  => http.post(`/articles/${id}/cover`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

// ── Projects ─────────────────────────────────────────────
export const projectsApi = {
  // 公开
  list:        (p)      => http.get('/projects',          { params: p }),
  getPublic:   (id)     => http.get(`/projects/public/${id}`),
  // 管理员 CRUD
  adminList:   (p)      => http.get('/projects/admin',    { params: p }),
  getById:     (id)     => http.get(`/projects/${id}`),
  create:      (d)      => http.post('/projects', d),
  update:      (id, d)  => http.put(`/projects/${id}`, d),
  remove:      (id)     => http.delete(`/projects/${id}`),
  uploadCover: (id, fd) => http.post(`/projects/${id}/cover`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  // GitHub README
  readme:      (id)     => http.get(`/projects/${id}/readme`),
}
