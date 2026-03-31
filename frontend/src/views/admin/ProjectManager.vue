<template>
  <div>
    <div class="page-head">
      <h2 class="page-h2">🚀 项目管理</h2>
      <div class="head-actions">
        <el-input v-model="searchQ" placeholder="搜索项目名..." clearable style="width:200px"
          @keyup.enter="loadList" @clear="loadList">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" :icon="Plus" @click="openForm(null)">添加项目</el-button>
      </div>
    </div>

    <!-- 项目卡片 grid -->
    <div v-loading="loading" class="proj-grid">
      <div v-for="p in projects" :key="p.id" class="proj-card card">

        <!-- 封面 -->
        <div class="proj-cover-wrap">
          <img v-if="p.cover_image" :src="p.cover_image" class="proj-cover" />
          <div v-else class="proj-cover-ph">{{ p.name[0]?.toUpperCase() }}</div>
        </div>

        <!-- 内容 -->
        <div class="proj-body">
          <h3 class="proj-name">{{ p.name }}</h3>
          <p class="proj-desc text-muted">{{ p.description || '暂无描述' }}</p>

          <div class="tag-row">
            <el-tag v-for="t in parseTags(p.tech_stack || p.tags)" :key="t" size="small" type="info">{{ t }}</el-tag>
          </div>

          <div class="proj-meta">
            <span v-if="p.github_url">
              🔗 <a :href="p.github_url" target="_blank" class="deploy-link">{{ p.github_url }}</a>
            </span>
            <span v-if="p.framework" class="fw-badge">{{ p.framework }}</span>
          </div>
        </div>

        <!-- 操作 -->
        <div class="proj-actions">
          <el-button size="small" type="primary" :icon="DocumentCopy" @click="fetchReadme(p)">查看 README</el-button>
          <el-button size="small" :icon="Link" @click="window.open(p.github_url, '_blank')" :disabled="!p.github_url">在 GitHub 打开</el-button>
          <el-button size="small" :icon="Edit" @click="openForm(p)">编辑</el-button>
          <el-button size="small" type="danger" :icon="Delete" @click="removeProject(p)">删除</el-button>
        </div>

      </div>
    </div>

    <el-empty v-if="!loading && !projects.length" description="暂无项目，点击「添加项目」开始" style="padding:80px 0" />

    <!-- 分页 -->
    <div class="pager" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
        background layout="prev,pager,next,total" @current-change="loadList" />
    </div>

    <!-- ── 新建/编辑 Dialog ─────────────────────────────── -->
    <el-dialog v-model="formVisible" :title="formId ? '编辑项目' : '添加项目'"
      width="560px" :close-on-click-modal="false">
      <el-form :model="form" label-position="top" style="padding:0 4px">
        <el-form-item label="项目名称 *">
          <el-input v-model="form.name" placeholder="My Awesome Project" />
        </el-form-item>
        <el-form-item label="GitHub URL *">
          <el-input v-model="form.github_url" placeholder="https://github.com/user/repo" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="技术标签（逗号分隔）">
          <el-input v-model="form.tech_stack" placeholder="Vue, FastAPI, Docker" />
        </el-form-item>
        <el-form-item label="显示在主页">
          <el-switch v-model="form.is_published" active-text="是" inactive-text="否" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProject">
          {{ formId ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ── README 预览 Dialog ──────────────────────────── -->
    <el-dialog v-model="readmeVisible" :title="`README — ${readmeProject?.name}`" width="760px" :close-on-click-modal="false">
      <!-- 顶部操作栏 -->
      <div class="readme-toolbar">
        <span class="readme-repo-url" v-if="readmeProject?.github_url">
          <el-icon><Link /></el-icon>
          <a :href="readmeProject.github_url" target="_blank" class="deploy-link">{{ readmeProject.github_url }}</a>
        </span>
        <el-button size="small" type="primary" :icon="TopRight" @click="openGithub">
          前往 GitHub
        </el-button>
      </div>

      <!-- 内容区 -->
      <div class="readme-body">
        <div v-if="readmeLoading" class="readme-loading">
          <el-icon class="is-loading" size="32"><Loading /></el-icon>
          <span>正在拉取 README...</span>
        </div>
        <div v-else-if="readmeError" class="readme-error">
          <el-icon size="24"><Warning /></el-icon>
          <span>{{ readmeError }}</span>
        </div>
        <div v-else class="md-body" v-html="renderedReadme" />
      </div>

      <template #footer>
        <el-button @click="readmeVisible = false">关闭</el-button>
        <el-button type="primary" :icon="TopRight" @click="openGithub">
          前往 GitHub
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, DocumentCopy, Edit, Delete, Link, TopRight, Loading, Warning,
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { projectsApi } from '@/api/endpoints.js'

// marked 配置
marked.setOptions({ breaks: true, gfm: true })

// ── List ──────────────────────────────────────────────────
const projects = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const loading  = ref(false)
const searchQ  = ref('')

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)

async function loadList() {
  loading.value = true
  try {
    const res = await projectsApi.adminList({ page: page.value, page_size: pageSize, q: searchQ.value || undefined })
    projects.value = res.items ?? []
    total.value    = res.total
  } finally { loading.value = false }
}

// ── Form ──────────────────────────────────────────────────
const formVisible = ref(false)
const formId      = ref(null)
const saving      = ref(false)
const form        = ref({ name:'', github_url:'', description:'', tech_stack:'', is_published:true })

function openForm(p) {
  formId.value = p?.id ?? null
  if (p) {
    form.value = {
      name: p.name, github_url: p.github_url, description: p.description ?? '',
      tech_stack: p.tech_stack ?? '', is_published: p.is_published,
    }
  } else {
    form.value = { name:'', github_url:'', description:'', tech_stack:'', is_published:true }
  }
  formVisible.value = true
}

async function saveProject() {
  if (!form.value.name.trim()) { ElMessage.warning('请填写项目名称'); return }
  if (!form.value.github_url.trim()) { ElMessage.warning('请填写 GitHub URL'); return }
  saving.value = true
  try {
    if (formId.value) {
      await projectsApi.update(formId.value, form.value)
      ElMessage.success('已保存')
    } else {
      await projectsApi.create(form.value)
      ElMessage.success('项目已创建')
    }
    formVisible.value = false
    loadList()
  } catch (e) {
    ElMessage.error(e?.detail || '操作失败')
  } finally { saving.value = false }
}

// ── Delete ────────────────────────────────────────────────
async function removeProject(p) {
  try {
    await ElMessageBox.confirm(`确认删除「${p.name}」？`, '删除确认', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await projectsApi.remove(p.id)
    ElMessage.success('已删除')
    loadList()
  } catch {}
}

// ── README ────────────────────────────────────────────────
const readmeVisible = ref(false)
const readmeProject = ref(null)
const readmeContent = ref('')
const readmeError   = ref('')
const readmeLoading = ref(false)

const renderedReadme = computed(() => {
  if (!readmeContent.value) return ''
  return marked.parse(readmeContent.value)
})

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

// 初始加载
loadList()
</script>

<style scoped>
.page-head    { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px; }
.page-h2      { font-size:1.375rem; font-weight:700; color:#f1f5f9; }
.head-actions { display:flex; gap:10px; align-items:center; }

/* 卡片 grid */
.proj-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; }
.proj-card { display:flex; flex-direction:column; gap:12px; padding:0; overflow:hidden; }

/* 封面 */
.proj-cover-wrap { position:relative; }
.proj-cover    { width:100%; height:160px; object-fit:cover; }
.proj-cover-ph {
  width:100%; height:120px; background:linear-gradient(135deg,#1e293b,#334155);
  display:flex; align-items:center; justify-content:center;
  font-size:3rem; font-weight:800; color:rgba(59,130,246,.3);
}

/* 内容 */
.proj-body  { padding:0 16px; display:flex; flex-direction:column; gap:8px; flex:1; }
.proj-name  { font-size:.9375rem; font-weight:700; color:#f1f5f9; }
.proj-desc  { font-size:.8125rem; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.tag-row    { display:flex; gap:5px; flex-wrap:wrap; }
.proj-meta  { display:flex; align-items:center; gap:8px; font-size:.8125rem; color:#64748b; flex-wrap:wrap; }
.deploy-link { color:#60a5fa; word-break:break-all; }
.deploy-link:hover { text-decoration:underline; }
.fw-badge { padding:2px 8px; border-radius:4px; background:rgba(139,92,246,.15); color:#a78bfa; font-size:.75rem; }

/* 操作 */
.proj-actions { padding:12px 16px; border-top:1px solid #1e293b; display:flex; flex-wrap:wrap; gap:6px; }

.pager { display:flex; justify-content:flex-end; margin-top:20px; }

/* README 弹窗 */
.readme-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 0 12px; border-bottom: 1px solid #1e293b; gap: 12px; flex-wrap: wrap;
}
.readme-repo-url {
  display: flex; align-items: center; gap: 6px;
  font-size: .8125rem; color: #64748b; min-width: 0; flex: 1;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.readme-body {
  margin-top: 12px;
  max-height: 62vh;
  overflow-y: auto;
  border-radius: 8px;
}
.readme-loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 12px; padding: 60px 0;
  color: #94a3b8; font-size: .9rem;
}
.readme-error {
  display: flex; align-items: center; gap: 8px;
  padding: 24px; color: #ef4444; font-size: .875rem;
  background: rgba(239,68,68,.08); border-radius: 8px;
}

/* Markdown 渲染样式 */
.md-body {
  padding: 16px 20px;
  background: #0d1117;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.75;
}
.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3),
.md-body :deep(h4) {
  color: #f1f5f9; font-weight: 700; margin: 1.2em 0 .5em;
  padding-bottom: .3em; border-bottom: 1px solid #1e293b;
}
.md-body :deep(h1) { font-size: 1.5rem; }
.md-body :deep(h2) { font-size: 1.25rem; }
.md-body :deep(h3) { font-size: 1.05rem; border-bottom: none; }
.md-body :deep(p)  { margin: .6em 0; }
.md-body :deep(a)  { color: #60a5fa; text-decoration: none; }
.md-body :deep(a:hover) { text-decoration: underline; }
.md-body :deep(code) {
  background: #1e293b; color: #93c5fd;
  padding: 2px 6px; border-radius: 4px; font-size: .85em;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.md-body :deep(pre) {
  background: #1e293b; border-radius: 8px;
  padding: 14px 16px; overflow-x: auto; margin: .8em 0;
}
.md-body :deep(pre code) { background: none; padding: 0; color: #e2e8f0; }
.md-body :deep(blockquote) {
  border-left: 3px solid #3b82f6; margin: .8em 0;
  padding: 4px 16px; color: #94a3b8; background: rgba(59,130,246,.06);
}
.md-body :deep(table) { width: 100%; border-collapse: collapse; margin: .8em 0; }
.md-body :deep(th),
.md-body :deep(td) {
  border: 1px solid #1e293b; padding: 6px 12px; text-align: left;
}
.md-body :deep(th) { background: #1e293b; color: #f1f5f9; font-weight: 600; }
.md-body :deep(ul),
.md-body :deep(ol) { padding-left: 1.5em; margin: .5em 0; }
.md-body :deep(li) { margin: .25em 0; }
.md-body :deep(hr) { border: none; border-top: 1px solid #1e293b; margin: 1em 0; }
.md-body :deep(img) { max-width: 100%; border-radius: 6px; }
</style>
