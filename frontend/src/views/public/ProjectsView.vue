<template>
  <div class="page section">
    <div class="container">
      <h1 class="section-title fade-in-up">项目展示</h1>
      <p class="text-muted fade-in-up" style="margin-bottom:48px;font-size:1.05rem">
        GitHub 项目 · 自动部署 · 实时访问
        <el-tag type="info" size="small" style="margin-left:8px">自动部署将在迭代三实现</el-tag>
      </p>

      <div v-loading="loading" class="proj-grid">
        <div v-for="p in projects" :key="p.id" class="card proj-card fade-in-up">

          <!-- 状态 -->
          <div class="proj-status">
            <span class="dot" :class="p.deploy_status"></span>
            <span class="status-txt" :class="p.deploy_status">{{ statusLabel(p.deploy_status) }}</span>
            <span class="stars" v-if="p.stars">⭐ {{ p.stars }}</span>
          </div>

          <!-- 封面 / 占位 -->
          <img v-if="p.cover_image" :src="p.cover_image" class="proj-cover" />
          <div v-else class="proj-placeholder">{{ p.name[0].toUpperCase() }}</div>

          <h3 class="proj-name">{{ p.name }}</h3>
          <p class="proj-desc text-muted">{{ p.description }}</p>

          <div class="tag-row" v-if="p.tech_stack || p.tags">
            <el-tag v-for="t in parseTags(p.tech_stack || p.tags)" :key="t" size="small" type="info">{{ t }}</el-tag>
          </div>

          <!-- 操作 -->
          <div class="proj-actions">
            <a :href="p.github_url" target="_blank" class="btn btn--ghost">GitHub ↗</a>
            <a v-if="p.deploy_status === 'running' && p.deploy_url" :href="p.deploy_url" target="_blank" class="btn btn--live">
              🚀 访问
            </a>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && !projects.length" description="暂无项目" style="padding:80px 0" />

      <div class="pager" v-if="total > pageSize">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
          background layout="prev,pager,next" @current-change="load" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { projectsApi } from '@/api/endpoints.js'

const projects = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const loading  = ref(false)

const parseTags   = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const statusLabel = (s) => ({ pending:'待部署', deploying:'部署中', running:'运行中', failed:'失败', stopped:'已停止' }[s] ?? s)

async function load() {
  loading.value = true
  try {
    const res = await projectsApi.list({ page: page.value, page_size: pageSize })
    projects.value = res.items ?? []
    total.value    = res.total
  } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page      { padding-top: 60px; }
.proj-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(300px,1fr)); gap: 24px; }
.proj-card { display: flex; flex-direction: column; gap: 12px; }

.proj-status { display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #475569; }
.dot.running { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,.6); animation: pulse 2s infinite; }
.dot.deploying { background: #f59e0b; animation: pulse 1s infinite; }
.dot.failed   { background: #ef4444; }
.status-txt { font-size: .75rem; color: #64748b; }
.status-txt.running   { color: #10b981; }
.status-txt.deploying { color: #f59e0b; }
.status-txt.failed    { color: #ef4444; }
.stars { margin-left: auto; font-size: .8125rem; color: #f59e0b; }

.proj-cover {
  width: 100%; height: 150px; object-fit: cover; border-radius: 8px;
}
.proj-placeholder {
  width: 100%; height: 100px; border-radius: 8px;
  background: linear-gradient(135deg,#1e293b,#334155);
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem; font-weight: 800; color: rgba(59,130,246,.35);
}
.proj-name { font-size: 1rem; font-weight: 700; color: #f1f5f9; }
.proj-desc { font-size: .875rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.tag-row   { display: flex; gap: 6px; flex-wrap: wrap; }
.proj-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: auto; }

.btn       { display: inline-flex; align-items: center; gap: 5px; padding: 7px 14px; border-radius: 8px; font-size: .8125rem; font-weight: 600; text-decoration: none; transition: all .2s; }
.btn--ghost { border: 1px solid #334155; color: #94a3b8; }
.btn--ghost:hover { border-color: #60a5fa; color: #60a5fa; }
.btn--live  { background: linear-gradient(135deg,#10b981,#059669); color: white; }

.pager { display: flex; justify-content: center; margin-top: 48px; }
</style>
