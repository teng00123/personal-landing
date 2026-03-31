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
    <el-dialog v-model="readmeVisible" :title="`README — ${readmeProject?.name}`" width="720px">
      <div v-if="readmeLoading" style="text-align:center;padding:40px">加载中...</div>
      <div v-else-if="readmeError" style="color:#ef4444;padding:20px">{{ readmeError }}</div>
      <pre v-else style="white-space:pre-wrap;word-break:break-all;font-size:13px;line-height:1.7;max-height:60vh;overflow-y:auto;background:#0d1117;padding:16px;border-radius:8px;color:#e2e8f0">{{ readmeContent }}</pre>
      <template #footer>
        <el-button @click="readmeVisible = false">关闭</el-button>
        <el-button type="primary" @click="window.open(readmeProject?.github_url, '_blank')">在 GitHub 打开</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, RefreshRight,
  DocumentCopy, Edit, Delete, Link,
} from '@element-plus/icons-vue'
import { projectsApi } from '@/api/endpoints.js'

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

async function fetchReadme(p) {
  readmeProject.value = p
  readmeContent.value = ''
  readmeError.value = ''
  readmeLoading.value = true
  readmeVisible.value = true
  try {
    const res = await projectsApi.readme(p.id)
    if (res.readme) {
      readmeContent.value = res.readme
    } else {
      readmeError.value = res.error || '未找到 README'
    }
  } catch (e) {
    readmeError.value = '加载失败'
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
</style>
