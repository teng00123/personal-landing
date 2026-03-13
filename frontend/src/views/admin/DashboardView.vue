<template>
  <div>
    <h2 class="page-h2">📊 概览</h2>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card" v-for="s in stats" :key="s.label">
        <div class="stat-icon">{{ s.icon }}</div>
        <div class="stat-num">{{ s.value }}</div>
        <div class="stat-label text-muted">{{ s.label }}</div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-grid">
      <router-link to="/admin/profile"  class="card quick-card">
        <div class="quick-icon">🧑</div>
        <div class="quick-title">编辑个人资料</div>
        <div class="quick-desc text-muted">修改简历、技能、工作经历</div>
      </router-link>
      <router-link to="/admin/articles" class="card quick-card">
        <div class="quick-icon">📝</div>
        <div class="quick-title">管理文章</div>
        <div class="quick-desc text-muted">迭代二实现：上传 Markdown 文章</div>
      </router-link>
      <router-link to="/admin/projects" class="card quick-card">
        <div class="quick-icon">🚀</div>
        <div class="quick-title">管理项目</div>
        <div class="quick-desc text-muted">迭代三实现：GitHub 自动部署</div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { articlesApi, projectsApi } from '@/api/endpoints.js'

const stats = ref([
  { icon: '📝', label: '文章总数',   value: '—' },
  { icon: '🚀', label: '项目总数',   value: '—' },
  { icon: '👁',  label: '总阅读量',   value: '—' },
  { icon: '✅', label: '运行中项目', value: '—' },
])

onMounted(async () => {
  try {
    const [ar, pr] = await Promise.all([
      articlesApi.adminList({ page: 1, page_size: 1 }),
      projectsApi.adminList({ page: 1, page_size: 100 }),
    ])
    stats.value[0].value = ar.total
    stats.value[1].value = pr.total
    stats.value[2].value = pr.items.reduce((s, _) => s, 0)  // 迭代二填充
    stats.value[3].value = pr.items.filter(p => p.deploy_status === 'running').length
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
