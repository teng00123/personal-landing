import http from './http.js'

// ── Auth ────────────────────────────────────────────────
export const authApi = {
  login: (data) => http.post('/auth/login', data),
  me:    ()     => http.get('/auth/me'),
}

// ── Profile ─────────────────────────────────────────────
export const profileApi = {
  get:    ()     => http.get('/profile'),
  update: (data) => http.put('/profile', data),
}

// ── Articles ─────────────────────────────────────────────
export const articlesApi = {
  list:       (p)    => http.get('/articles',       { params: p }),
  getBySlug:  (slug) => http.get(`/articles/slug/${slug}`),
  adminList:  (p)    => http.get('/articles/admin', { params: p }),
  getById:    (id)   => http.get(`/articles/${id}`),
  create:     (d)    => http.post('/articles', d),
  update:     (id,d) => http.put(`/articles/${id}`, d),
  remove:     (id)   => http.delete(`/articles/${id}`),
}

// ── Projects ─────────────────────────────────────────────
export const projectsApi = {
  list:      (p)    => http.get('/projects',          { params: p }),
  getPublic: (id)   => http.get(`/projects/public/${id}`),
  adminList: (p)    => http.get('/projects/admin',    { params: p }),
  getById:   (id)   => http.get(`/projects/${id}`),
  create:    (d)    => http.post('/projects', d),
  update:    (id,d) => http.put(`/projects/${id}`, d),
  remove:    (id)   => http.delete(`/projects/${id}`),
}
