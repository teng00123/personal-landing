<template>
  <div class="page section">
    <div class="container">
      <h1 class="section-title fade-in-up">项目展示</h1>
      <p class="text-muted fade-in-up" style="margin-bottom:48px;font-size:1.05rem">
        GitHub 开源项目 · 持续更新
      </p>

      <div v-loading="loading" class="proj-grid">
        <div
          v-for="p in projects"
          :key="p.id"
          class="card proj-card fade-in-up"
          :style="{ animationDelay: `${projects.indexOf(p) * 0.06}s` }"
        >
          <!-- 封面 / 占位 -->
          <img v-if="p.cover_image" :src="p.cover_image" class="proj-cover" />
          <div v-else class="proj-placeholder">{{ p.name[0]?.toUpperCase() }}</div>

          <h3 class="proj-name">{{ p.name }}</h3>
          <p class="proj-desc text-muted">{{ p.description }}</p>

          <div class="tag-row" v-if="p.tech_stack || p.tags">
            <el-tag v-for="t in parseTags(p.tech_stack || p.tags)" :key="t" size="small" type="info">{{ t }}</el-tag>
          </div>

          <!-- stars / forks -->
          <div class="stats-row" v-if="p.stars || p.forks">
            <span class="stars" v-if="p.stars">⭐ {{ p.stars }}</span>
            <span class="forks" v-if="p.forks">🍴 {{ p.forks }}</span>
          </div>

          <!-- 框架标识 -->
          <div v-if="p.framework" class="fw-row">
            <span class="fw-badge">{{ fwLabel(p.framework) }}</span>
          </div>

          <!-- 操作按钮 -->
          <div class="proj-actions">
            <a :href="p.github_url" target="_blank" class="btn btn--ghost">GitHub ↗</a>
            <a
              v-if="p.github_url"
              :href="p.github_url"
              target="_blank"
              class="btn btn--live"
            >查看 GitHub</a>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && !projects.length" description="暂无项目" style="padding:80px 0" />

      <div class="pager" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page" :page-size="pageSize" :total="total"
          background layout="prev,pager,next" @current-change="load"
        />
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

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fwLabel   = (f) => ({ 'vue-react':'Vue/React', nextjs:'Next.js', nodejs:'Node.js', fastapi:'FastAPI', flask:'Flask', django:'Django', static:'静态', docker:'Docker' }[f] ?? f)

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
.proj-card { display: flex; flex-direction: column; gap: 12px; overflow: hidden; padding: 0; }

/* 封面 */
.proj-cover { width:100%; height:150px; object-fit:cover; }
.proj-placeholder {
  width:100%; height:110px;
  background:linear-gradient(135deg,#1e293b,#334155);
  display:flex; align-items:center; justify-content:center;
  font-size:2.75rem; font-weight:800; color:rgba(59,130,246,.25);
}

/* 内容区 padding */
.proj-name   { font-size:.9375rem; font-weight:700; color:#f1f5f9; padding: 0 16px; }
.proj-desc   { font-size:.8125rem; padding:0 16px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.tag-row     { display:flex; gap:6px; flex-wrap:wrap; padding:0 16px; }
.stats-row   { display:flex; align-items:center; gap:10px; padding:0 16px; }
.fw-row      { padding:0 16px; }

.stars { font-size:.8125rem; color:#f59e0b; }
.forks { font-size:.8125rem; color:#64748b; }

.fw-badge { padding:2px 8px; border-radius:4px; background:rgba(139,92,246,.12); color:#a78bfa; font-size:.75rem; }

.proj-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:auto; padding:12px 16px; border-top:1px solid #1e293b; }
.btn { display:inline-flex; align-items:center; gap:5px; padding:6px 14px; border-radius:8px; font-size:.8125rem; font-weight:600; text-decoration:none; transition:all .2s; }
.btn--ghost   { border:1px solid #334155; color:#94a3b8; }
.btn--ghost:hover { border-color:#60a5fa; color:#60a5fa; }
.btn--live    { background:linear-gradient(135deg,#3b82f6,#2563eb); color:white; }
.btn--live:hover { opacity:.9; }

.pager { display:flex; justify-content:center; margin-top:48px; }
</style>
