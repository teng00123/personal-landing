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

          <!-- 操作按钮：查看 README + 前往 GitHub -->
          <div class="proj-actions">
            <button class="btn btn--primary" @click="fetchReadme(p)">📄 查看 README</button>
            <a :href="p.github_url" target="_blank" class="btn btn--ghost">GitHub ↗</a>
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

    <!-- ── README 预览 Dialog ──────────────────────────── -->
    <el-dialog
      v-model="readmeVisible"
      :title="`README — ${readmeProject?.name}`"
      width="760px"
      :close-on-click-modal="false"
    >
      <!-- 顶部工具栏：仓库地址 + 前往 GitHub 按钮 -->
      <div class="readme-toolbar">
        <span class="readme-url" v-if="readmeProject?.github_url">
          🔗 <a :href="readmeProject.github_url" target="_blank" class="gh-link">{{ readmeProject.github_url }}</a>
        </span>
        <el-button size="small" type="primary" @click="openGithub">前往 GitHub ↗</el-button>
      </div>

      <!-- 内容区 -->
      <div class="readme-body">
        <div v-if="readmeLoading" class="readme-loading">
          <el-icon class="is-loading" size="32"><Loading /></el-icon>
          <span>正在拉取 README...</span>
        </div>
        <div v-else-if="readmeError" class="readme-error">
          <el-icon size="20"><Warning /></el-icon>
          <span>{{ readmeError }}</span>
        </div>
        <div v-else class="md-body" v-html="renderedReadme" />
      </div>

      <!-- footer：关闭 + 前往 GitHub -->
      <template #footer>
        <el-button @click="readmeVisible = false">关闭</el-button>
        <el-button type="primary" @click="openGithub">前往 GitHub ↗</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Loading, Warning } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { projectsApi } from '@/api/endpoints.js'

marked.setOptions({ breaks: true, gfm: true })

// ── 列表 ──────────────────────────────────────────────────
const projects = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const loading  = ref(false)

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fwLabel   = (f) => ({
  'vue-react': 'Vue/React', nextjs: 'Next.js', nodejs: 'Node.js',
  fastapi: 'FastAPI', flask: 'Flask', django: 'Django', static: '静态', docker: 'Docker',
}[f] ?? f)

async function load() {
  loading.value = true
  try {
    const res = await projectsApi.list({ page: page.value, page_size: pageSize })
    projects.value = res.items ?? []
    total.value    = res.total
  } finally { loading.value = false }
}

// ── README 预览 ───────────────────────────────────────────
const readmeVisible = ref(false)
const readmeProject = ref(null)
const readmeContent = ref('')
const readmeError   = ref('')
const readmeLoading = ref(false)

const renderedReadme = computed(() =>
  readmeContent.value ? marked.parse(readmeContent.value) : ''
)

function openGithub() {
  if (readmeProject.value?.github_url) {
    window.open(readmeProject.value.github_url, '_blank')
  }
}

async function fetchReadme(p) {
  readmeProject.value = p
  readmeContent.value = ''
  readmeError.value   = ''
  readmeLoading.value = true
  readmeVisible.value = true
  try {
    const res = await projectsApi.readme(p.id)
    if (res.readme) {
      readmeContent.value = res.readme
    } else {
      readmeError.value = res.error || '未找到 README'
    }
  } catch {
    readmeError.value = '加载失败，请检查 GitHub URL 是否正确'
  } finally {
    readmeLoading.value = false
  }
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

/* 内容区 */
.proj-name  { font-size:.9375rem; font-weight:700; color:#f1f5f9; padding:0 16px; }
.proj-desc  { font-size:.8125rem; padding:0 16px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.tag-row    { display:flex; gap:6px; flex-wrap:wrap; padding:0 16px; }
.stats-row  { display:flex; align-items:center; gap:10px; padding:0 16px; }
.fw-row     { padding:0 16px; }
.stars      { font-size:.8125rem; color:#f59e0b; }
.forks      { font-size:.8125rem; color:#64748b; }
.fw-badge   { padding:2px 8px; border-radius:4px; background:rgba(139,92,246,.12); color:#a78bfa; font-size:.75rem; }

/* 操作按钮 */
.proj-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:auto; padding:12px 16px; border-top:1px solid #1e293b; }
.btn { display:inline-flex; align-items:center; gap:5px; padding:6px 14px; border-radius:8px; font-size:.8125rem; font-weight:600; text-decoration:none; transition:all .2s; cursor:pointer; border:none; }
.btn--primary { background:linear-gradient(135deg,#3b82f6,#2563eb); color:white; }
.btn--primary:hover { opacity:.88; }
.btn--ghost   { border:1px solid #334155; color:#94a3b8; background:transparent; }
.btn--ghost:hover { border-color:#60a5fa; color:#60a5fa; }

.pager { display:flex; justify-content:center; margin-top:48px; }

/* README 弹窗 */
.readme-toolbar {
  display:flex; align-items:center; justify-content:space-between;
  padding:0 0 12px; border-bottom:1px solid #1e293b; gap:12px; flex-wrap:wrap;
}
.readme-url {
  font-size:.8125rem; color:#64748b;
  display:flex; align-items:center; gap:6px;
  min-width:0; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.gh-link { color:#60a5fa; text-decoration:none; }
.gh-link:hover { text-decoration:underline; }

.readme-body  { margin-top:12px; max-height:62vh; overflow-y:auto; border-radius:8px; }
.readme-loading {
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:12px; padding:60px 0; color:#94a3b8; font-size:.9rem;
}
.readme-error {
  display:flex; align-items:center; gap:8px; padding:20px;
  color:#ef4444; background:rgba(239,68,68,.08); border-radius:8px; font-size:.875rem;
}

/* Markdown 渲染 */
.md-body { padding:16px 20px; background:#0d1117; border-radius:8px; color:#e2e8f0; font-size:14px; line-height:1.75; }
.md-body :deep(h1),.md-body :deep(h2),.md-body :deep(h3),.md-body :deep(h4) { color:#f1f5f9; font-weight:700; margin:1.2em 0 .5em; padding-bottom:.3em; border-bottom:1px solid #1e293b; }
.md-body :deep(h1) { font-size:1.5rem; }
.md-body :deep(h2) { font-size:1.25rem; }
.md-body :deep(h3) { font-size:1.05rem; border-bottom:none; }
.md-body :deep(p)  { margin:.6em 0; }
.md-body :deep(a)  { color:#60a5fa; text-decoration:none; }
.md-body :deep(a:hover) { text-decoration:underline; }
.md-body :deep(code) { background:#1e293b; color:#93c5fd; padding:2px 6px; border-radius:4px; font-size:.85em; font-family:'JetBrains Mono','Fira Code',monospace; }
.md-body :deep(pre) { background:#1e293b; border-radius:8px; padding:14px 16px; overflow-x:auto; margin:.8em 0; }
.md-body :deep(pre code) { background:none; padding:0; color:#e2e8f0; }
.md-body :deep(blockquote) { border-left:3px solid #3b82f6; margin:.8em 0; padding:4px 16px; color:#94a3b8; background:rgba(59,130,246,.06); }
.md-body :deep(table) { width:100%; border-collapse:collapse; margin:.8em 0; }
.md-body :deep(th),.md-body :deep(td) { border:1px solid #1e293b; padding:6px 12px; text-align:left; }
.md-body :deep(th) { background:#1e293b; color:#f1f5f9; font-weight:600; }
.md-body :deep(ul),.md-body :deep(ol) { padding-left:1.5em; margin:.5em 0; }
.md-body :deep(li) { margin:.25em 0; }
.md-body :deep(hr) { border:none; border-top:1px solid #1e293b; margin:1em 0; }
.md-body :deep(img) { max-width:100%; border-radius:6px; }
</style>
