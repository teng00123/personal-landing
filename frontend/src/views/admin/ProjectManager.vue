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
          <div class="proj-status-badge" :class="p.deploy_status">
            <span class="dot" :class="p.deploy_status"></span>
            {{ statusLabel(p.deploy_status) }}
          </div>
        </div>

        <!-- 内容 -->
        <div class="proj-body">
          <h3 class="proj-name">{{ p.name }}</h3>
          <p class="proj-desc text-muted">{{ p.description || '暂无描述' }}</p>

          <div class="tag-row">
            <el-tag v-for="t in parseTags(p.tech_stack || p.tags)" :key="t" size="small" type="info">{{ t }}</el-tag>
          </div>

          <div class="proj-meta">
            <span v-if="p.deploy_url">
              🔗 <a :href="p.deploy_url" target="_blank" class="deploy-link">{{ p.deploy_url }}</a>
            </span>
            <span v-if="p.framework" class="fw-badge">{{ p.framework }}</span>
          </div>
        </div>

        <!-- 操作 -->
        <div class="proj-actions">
          <el-button size="small" type="success" :icon="VideoPlay"
            :disabled="p.deploy_status === 'deploying'"
            @click="doDeploy(p)">
            {{ p.deploy_status === 'deploying' ? '部署中...' : '部署' }}
          </el-button>
          <el-button size="small" type="warning" :icon="RefreshRight"
            :disabled="p.deploy_status === 'deploying'"
            @click="doRedeploy(p)">重部署</el-button>
          <el-button size="small" type="info" :icon="VideoPause"
            :disabled="p.deploy_status !== 'running'"
            @click="doStop(p)">停止</el-button>
          <el-button size="small" :icon="DocumentCopy" @click="openLogs(p)">日志</el-button>
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
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="部署分支">
              <el-input v-model="form.deploy_branch" placeholder="main" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="技术标签（逗号分隔）">
              <el-input v-model="form.tech_stack" placeholder="Vue, FastAPI, Docker" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="自定义启动命令（可选，留空则自动识别）">
          <el-input v-model="form.deploy_command" placeholder="node server.js --port {PORT}" />
        </el-form-item>
        <el-form-item label="显示在主页">
          <el-switch v-model="form.is_published" active-text="是" inactive-text="否" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProject">
          {{ formId ? '保存' : '创建并部署' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ── 日志 Drawer ──────────────────────────────────── -->
    <el-drawer v-model="logsVisible" :title="`部署日志 — ${logsProject?.name}`"
      size="55%" direction="rtl" @close="stopLogPolling">
      <div class="log-toolbar">
        <el-tag :type="logStatusType" size="small">{{ statusLabel(logsProject?.deploy_status) }}</el-tag>
        <span v-if="logsProject?.deploy_url" style="margin-left:12px;font-size:13px">
          🔗 <a :href="logsProject.deploy_url" target="_blank" class="deploy-link">{{ logsProject.deploy_url }}</a>
        </span>
        <el-button size="small" style="margin-left:auto" :icon="RefreshRight" @click="fetchLogs(true)">刷新</el-button>
      </div>
      <div class="log-body" ref="logBodyRef">
        <pre class="log-pre">{{ logContent || '（暂无日志）' }}</pre>
      </div>
    </el-drawer>

  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, VideoPlay, VideoPause, RefreshRight,
  DocumentCopy, Edit, Delete,
} from '@element-plus/icons-vue'
import { projectsApi } from '@/api/endpoints.js'

// ── List ──────────────────────────────────────────────────
const projects = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const loading  = ref(false)
const searchQ  = ref('')

const parseTags   = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const statusLabel = (s) => ({ pending:'待部署', deploying:'部署中', running:'运行中', failed:'失败', stopped:'已停止' }[s] ?? s)

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
const form        = ref({ name:'', github_url:'', description:'', deploy_branch:'main', tech_stack:'', deploy_command:'', is_published:true })

function openForm(p) {
  formId.value = p?.id ?? null
  if (p) {
    form.value = {
      name: p.name, github_url: p.github_url, description: p.description ?? '',
      deploy_branch: p.deploy_branch ?? 'main', tech_stack: p.tech_stack ?? '',
      deploy_command: p.deploy_command ?? '', is_published: p.is_published,
    }
  } else {
    form.value = { name:'', github_url:'', description:'', deploy_branch:'main', tech_stack:'', deploy_command:'', is_published:true }
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
      ElMessage.success('项目已创建，自动开始部署')
    }
    formVisible.value = false
    loadList()
  } catch (e) {
    ElMessage.error(e?.detail || '操作失败')
  } finally { saving.value = false }
}

// ── Deploy actions ────────────────────────────────────────
async function doDeploy(p) {
  try {
    await projectsApi.deploy(p.id)
    ElMessage.success('部署已触发')
    startAutoRefresh()
    loadList()
  } catch (e) { ElMessage.error(e?.detail || '触发失败') }
}

async function doRedeploy(p) {
  try {
    await ElMessageBox.confirm(`重新部署「${p.name}」？将先停止再重新 clone & 构建。`, '确认重部署', {
      type: 'warning', confirmButtonText: '重部署', cancelButtonText: '取消',
    })
    await projectsApi.redeploy(p.id)
    ElMessage.success('重部署已触发')
    startAutoRefresh()
    loadList()
  } catch {}
}

async function doStop(p) {
  try {
    await projectsApi.stop(p.id)
    ElMessage.success('已停止')
    loadList()
  } catch (e) { ElMessage.error(e?.detail || '停止失败') }
}

async function removeProject(p) {
  try {
    await ElMessageBox.confirm(`确认删除「${p.name}」？进程将被停止。`, '删除确认', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await projectsApi.remove(p.id)
    ElMessage.success('已删除')
    loadList()
  } catch {}
}

// ── 自动刷新（部署中时轮询） ──────────────────────────────
let refreshTimer = null
function startAutoRefresh() {
  if (refreshTimer) return
  refreshTimer = setInterval(async () => {
    await loadList()
    const deploying = projects.value.some(p => p.deploy_status === 'deploying')
    if (!deploying) stopAutoRefresh()
  }, 3000)
}
function stopAutoRefresh() {
  clearInterval(refreshTimer)
  refreshTimer = null
}

// ── Logs ──────────────────────────────────────────────────
const logsVisible  = ref(false)
const logsProject  = ref(null)
const logContent   = ref('')
const logBodyRef   = ref(null)
let logOffset      = 0
let logTimer       = null

const logStatusType = computed(() => ({
  running:'success', deploying:'warning', failed:'danger', stopped:'info', pending:'info',
}[logsProject.value?.deploy_status] ?? 'info'))

async function openLogs(p) {
  logsProject.value = p
  logContent.value  = ''
  logOffset         = 0
  logsVisible.value = true
  await fetchLogs(true)
  // 轮询（部署中时每 2s 刷新）
  logTimer = setInterval(() => {
    if (['deploying'].includes(logsProject.value?.deploy_status)) fetchLogs(false)
    else stopLogPolling()
  }, 2000)
}

async function fetchLogs(reset = false) {
  if (!logsProject.value) return
  if (reset) { logContent.value = ''; logOffset = 0 }
  try {
    const res = await projectsApi.logs(logsProject.value.id, logOffset)
    if (res.log) {
      logContent.value += res.log
      logOffset = res.total_length
    }
    // 同步状态
    logsProject.value = { ...logsProject.value, deploy_status: res.status, deploy_url: res.deploy_url }
    // 滚动到底部
    await nextTick()
    if (logBodyRef.value) logBodyRef.value.scrollTop = logBodyRef.value.scrollHeight
  } catch {}
}

function stopLogPolling() {
  clearInterval(logTimer)
  logTimer = null
}

onUnmounted(() => {
  stopAutoRefresh()
  stopLogPolling()
})

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
.proj-status-badge {
  position:absolute; top:10px; right:10px;
  display:flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:20px; font-size:.75rem; font-weight:600;
  background:rgba(15,23,42,.75); backdrop-filter:blur(4px);
  color:#94a3b8;
}
.proj-status-badge.running   { color:#10b981; }
.proj-status-badge.deploying { color:#f59e0b; }
.proj-status-badge.failed    { color:#ef4444; }
.dot { width:7px; height:7px; border-radius:50%; background:currentColor; }
.dot.running   { animation: pulse 2s infinite; }
.dot.deploying { animation: pulse 1s infinite; }

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

/* 日志 */
.log-toolbar { display:flex; align-items:center; padding:0 0 12px; border-bottom:1px solid #1e293b; flex-wrap:wrap; gap:8px; }
.log-body    { margin-top:12px; background:#0d1117; border-radius:8px; height:calc(100vh - 180px); overflow-y:auto; }
.log-pre     { padding:16px; font-family:'JetBrains Mono','Fira Code',monospace; font-size:12.5px; line-height:1.7; color:#e2e8f0; white-space:pre-wrap; word-break:break-all; margin:0; }
</style>
