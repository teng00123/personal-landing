<template>
  <div>
    <h2 class="page-h2">📊 概览</h2>

    <div class="stats-grid">
      <div class="stat-card card" v-for="s in stats" :key="s.label">
        <div class="stat-icon">{{ s.icon }}</div>
        <div class="stat-num">{{ s.value }}</div>
        <div class="stat-label text-muted">{{ s.label }}</div>
      </div>
    </div>

    <div class="quick-grid">
      <router-link to="/admin/profile"  class="card quick-card">
        <div class="quick-icon">🧑</div>
        <div class="quick-title">编辑个人资料</div>
        <div class="quick-desc text-muted">修改简历、技能、工作经历</div>
      </router-link>
      <router-link to="/admin/articles" class="card quick-card">
        <div class="quick-icon">📝</div>
        <div class="quick-title">管理文章</div>
        <div class="quick-desc text-muted">上传 .md / 在线编辑 / 发布管理</div>
      </router-link>
      <router-link to="/admin/projects" class="card quick-card">
        <div class="quick-icon">🚀</div>
        <div class="quick-title">管理项目</div>
        <div class="quick-desc text-muted">迭代三：GitHub 自动部署</div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { articlesApi, projectsApi } from '@/api/endpoints.js'

const stats = ref([
  { icon: '📝', label: '文章总数',   value: '—' },
  { icon: '✅', label: '已发布',     value: '—' },
  { icon: '🚀', label: '项目总数',   value: '—' },
  { icon: '👁',  label: '总阅读量',   value: '—' },
])

onMounted(async () => {
  try {
    const [ar, arAll, pr] = await Promise.all([
      articlesApi.adminList({ page: 1, page_size: 1 }),
      articlesApi.adminList({ page: 1, page_size: 100, published: true }),
      projectsApi.adminList({ page: 1, page_size: 100 }),
    ])
    stats.value[0].value = ar.total
    stats.value[1].value = arAll.total
    stats.value[2].value = pr.total
    // 总阅读量
    const allArt = await articlesApi.adminList({ page: 1, page_size: 100 })
    stats.value[3].value = (allArt.items ?? []).reduce((s, a) => s + (a.view_count || 0), 0)
  } catch { /* ignore */ }
})
</script>

<style scoped>
.page-h2    { font-size: 1.375rem; font-weight: 700; color: #f1f5f9; margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 24px; }
.stat-card  { text-align: center; padding: 24px; }
.stat-icon  { font-size: 1.75rem; margin-bottom: 6px; }
.stat-num   { font-size: 1.875rem; font-weight: 800; color: #60a5fa; }
.stat-label { font-size: .8125rem; margin-top: 4px; }
.quick-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.quick-card { text-decoration: none; color: inherit; cursor: pointer; }
.quick-icon  { font-size: 1.75rem; margin-bottom: 8px; }
.quick-title { font-size: .9375rem; font-weight: 700; color: #f1f5f9; margin-bottom: 4px; }
.quick-desc  { font-size: .8125rem; }
</style>
