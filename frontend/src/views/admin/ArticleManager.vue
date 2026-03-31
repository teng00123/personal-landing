<template>
  <div>
    <div class="page-head">
      <h2 class="page-h2">📝 文章管理</h2>
      <div class="head-actions">
        <el-input
          v-model="searchQ"
          placeholder="搜索标题..."
          clearable
          style="width:220px"
          @keyup.enter="loadList"
          @clear="loadList"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterPublished" placeholder="全部状态" clearable style="width:130px" @change="loadList">
          <el-option label="已发布" :value="true" />
          <el-option label="草稿"   :value="false" />
        </el-select>
        <el-upload
          :show-file-list="false"
          accept=".md"
          :before-upload="uploadMd"
        >
          <el-button type="success" :icon="Upload">上传 .md</el-button>
        </el-upload>
        <el-button type="primary" :icon="Plus" @click="openEditor(null)">新建文章</el-button>
        <el-button type="warning" :icon="Link" @click="csdnVisible = true">从 CSDN 导入</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      v-loading="loading"
      :data="articles"
      stripe
      style="width:100%"
      row-key="id"
    >
      <el-table-column prop="id" label="ID" width="60" />

      <el-table-column label="封面" width="72">
        <template #default="{ row }">
          <img v-if="row.cover_image" :src="row.cover_image" class="cover-thumb" />
          <div v-else class="cover-empty">📄</div>
        </template>
      </el-table-column>

      <el-table-column label="标题" min-width="200">
        <template #default="{ row }">
          <span class="article-title">{{ row.title }}</span>
          <div style="font-size:12px;color:#64748b;margin-top:2px">/{{ row.slug }}</div>
        </template>
      </el-table-column>

      <el-table-column label="标签" width="180">
        <template #default="{ row }">
          <el-tag
            v-for="t in parseTags(row.tags)"
            :key="t"
            size="small"
            type="info"
            style="margin:2px"
          >{{ t }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_published"
            active-color="#10b981"
            inactive-color="#475569"
            :loading="row._toggling"
            @change="togglePublish(row)"
          />
        </template>
      </el-table-column>

      <el-table-column label="阅读" width="75" align="center">
        <template #default="{ row }">
          <span style="color:#64748b;font-size:13px">{{ row.view_count }}</span>
        </template>
      </el-table-column>

      <el-table-column label="创建时间" width="160">
        <template #default="{ row }">
          <span style="font-size:13px;color:#64748b">{{ fmtDate(row.created_at) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" text @click="openEditor(row)">编辑</el-button>
          <el-button size="small" type="success" text @click="previewArticle(row)">预览</el-button>
          <el-button size="small" type="danger"  text @click="removeArticle(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pager" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        background
        layout="prev,pager,next,total"
        @current-change="loadList"
      />
    </div>

    <!-- ── 编辑器抽屉 ──────────────────────────────────── -->
    <el-drawer
      v-model="editorVisible"
      :title="editId ? '编辑文章' : '新建文章'"
      size="90%"
      direction="rtl"
      :destroy-on-close="false"
    >
      <ArticleEditor
        v-if="editorVisible"
        :article-id="editId"
        @saved="onSaved"
        @cancel="editorVisible = false"
      />
    </el-drawer>

    <!-- ── CSDN 导入 Dialog ──────────────────────────────── -->
    <el-dialog
      v-model="csdnVisible"
      title="从 CSDN 导入文章"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="csdn-form">
        <p class="csdn-tip">
          粘贴 CSDN 文章链接，系统将自动提取标题、正文、标签并保存为草稿，同时在文末附上原文链接。
        </p>
        <el-input
          v-model="csdnUrl"
          placeholder="https://blog.csdn.net/xxx/article/details/xxx"
          clearable
          :prefix-icon="Link"
          size="large"
        />
        <div v-if="csdnError" class="csdn-error">⚠️ {{ csdnError }}</div>
      </div>
      <template #footer>
        <el-button @click="csdnVisible = false">取消</el-button>
        <el-button type="primary" :loading="csdnLoading" @click="doImportCsdn">导入</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Upload, Link } from '@element-plus/icons-vue'
import { articlesApi } from '@/api/endpoints.js'
import ArticleEditor from './ArticleEditor.vue'
import dayjs from 'dayjs'

const router = useRouter()

const articles        = ref([])
const total           = ref(0)
const page            = ref(1)
const pageSize        = 15
const loading         = ref(false)
const searchQ         = ref('')
const filterPublished = ref(null)
const editorVisible   = ref(false)
const editId          = ref(null)

// CSDN 导入
const csdnVisible = ref(false)
const csdnUrl     = ref('')
const csdnLoading = ref(false)
const csdnError   = ref('')

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '—'

async function loadList() {
  loading.value = true
  try {
    const res = await articlesApi.adminList({
      page: page.value,
      page_size: pageSize,
      q: searchQ.value || undefined,
      published: filterPublished.value ?? undefined,
    })
    articles.value = (res.items ?? []).map(a => ({ ...a, _toggling: false }))
    total.value    = res.total
  } finally { loading.value = false }
}

function openEditor(row) {
  editId.value      = row?.id ?? null
  editorVisible.value = true
}

function onSaved() {
  editorVisible.value = false
  loadList()
}

function previewArticle(row) {
  window.open(`/articles/${row.slug}`, '_blank')
}

async function togglePublish(row) {
  row._toggling = true
  try {
    await articlesApi.update(row.id, { is_published: !row.is_published })
    row.is_published = !row.is_published
    ElMessage.success(row.is_published ? '已发布' : '已转为草稿')
  } catch { ElMessage.error('操作失败') }
  finally { row._toggling = false }
}

async function removeArticle(row) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.title}」？此操作不可恢复。`, '删除确认', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await articlesApi.remove(row.id)
    ElMessage.success('已删除')
    loadList()
  } catch {}
}

async function uploadMd(file) {
  const fd = new FormData()
  fd.append('file', file)
  try {
    const art = await articlesApi.uploadMd(fd)
    ElMessage.success(`"${art.title}" 已导入为草稿`)
    editId.value = art.id
    editorVisible.value = true
    loadList()
  } catch (e) {
    ElMessage.error(e?.detail || '上传失败')
  }
  return false  // 阻止 el-upload 自动上传
}

async function doImportCsdn() {
  csdnError.value = ''
  const url = csdnUrl.value.trim()
  if (!url) { csdnError.value = '请输入 CSDN 文章链接'; return }
  if (!url.includes('csdn.net')) { csdnError.value = '请输入有效的 CSDN 链接（包含 csdn.net）'; return }
  csdnLoading.value = true
  try {
    const art = await articlesApi.importCsdn(url)
    ElMessage.success(`「${art.title}」已导入为草稿，可在编辑器中继续编辑`)
    csdnVisible.value = false
    csdnUrl.value = ''
    editId.value = art.id
    editorVisible.value = true
    loadList()
  } catch (e) {
    csdnError.value = e?.response?.data?.detail || e?.message || '导入失败，请检查链接或稍后重试'
  } finally {
    csdnLoading.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.page-head    { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px; }
.page-h2      { font-size:1.375rem; font-weight:700; color:var(--c-text); }
.head-actions { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.cover-thumb  { width:48px; height:36px; object-fit:cover; border-radius:4px; }
.cover-empty  { width:48px; height:36px; display:flex; align-items:center; justify-content:center; font-size:1.25rem; background:var(--c-bg-card2); border-radius:4px; }
.article-title { font-weight:600; color:var(--c-text); }
.pager        { display:flex; justify-content:flex-end; margin-top:20px; }

/* CSDN 导入弹窗 */
.csdn-form  { display:flex; flex-direction:column; gap:14px; }
.csdn-tip   { font-size:.875rem; color:var(--c-text-muted); line-height:1.6; }
.csdn-error { font-size:.85rem; color:var(--c-danger); background:rgba(220,38,38,.07); padding:8px 12px; border-radius:6px; }
</style>
