<template>
  <div class="editor-wrap">

    <!-- ── 左栏：编辑区 ──────────────────────────────────── -->
    <div class="editor-left">

      <!-- 基本信息 -->
      <el-form :model="form" label-position="top" class="meta-form">
        <el-row :gutter="12">
          <el-col :span="16">
            <el-form-item label="标题 *">
              <el-input v-model="form.title" placeholder="文章标题" size="large" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="标签（逗号分隔）">
              <el-input v-model="form.tags" placeholder="Vue, Python, DevOps" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="一句话描述..." />
        </el-form-item>

        <el-row :gutter="12" style="align-items:flex-end">
          <!-- 封面图 -->
          <el-col :span="10">
            <el-form-item label="封面图">
              <div class="cover-box">
                <img v-if="form.cover_image" :src="form.cover_image" class="cover-preview" />
                <div v-else class="cover-placeholder">📷 点击上传</div>
                <el-upload
                  :show-file-list="false"
                  accept="image/*"
                  action="#"
                  :auto-upload="false"
                  :on-change="(f) => uploadCover(f.raw)"
                  class="cover-upload"
                >
                  <div class="cover-overlay">更换</div>
                </el-upload>
              </div>
            </el-form-item>
          </el-col>
          <!-- 发布开关 + 操作按钮 -->
          <el-col :span="14">
            <el-form-item label="发布状态">
              <el-switch
                v-model="form.is_published"
                active-text="已发布"
                inactive-text="草稿"
                active-color="#10b981"
              />
            </el-form-item>
            <div class="editor-actions">
              <el-button @click="$emit('cancel')">取消</el-button>
              <el-button type="primary" :loading="saving" @click="save">
                💾 保存
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>

      <!-- Markdown 编辑区 -->
      <div class="md-editor-area">
        <div class="md-toolbar">
          <span class="md-toolbar-title">✏️ Markdown 编辑</span>
          <div class="toolbar-btns">
            <el-button size="small" text @click="insertSnippet('**', '**', '粗体')">B</el-button>
            <el-button size="small" text @click="insertSnippet('*', '*', '斜体')"><i>I</i></el-button>
            <el-button size="small" text @click="insertSnippet('`', '`', '代码')">` `</el-button>
            <el-button size="small" text @click="insertSnippet('\n```\n', '\n```', 'code')">{ }</el-button>
            <el-button size="small" text @click="insertLine('## ')">H2</el-button>
            <el-button size="small" text @click="insertLine('### ')">H3</el-button>
            <el-button size="small" text @click="insertLine('- ')">列表</el-button>
            <el-button size="small" text @click="insertLine('> ')">引用</el-button>
            <el-button size="small" text @click="insertSnippet('[', '](url)', '链接文字')">🔗</el-button>
            <el-button size="small" text @click="insertSnippet('![alt](', ')', 'image-url')">🖼️</el-button>
            <el-divider direction="vertical" />
            <el-upload :show-file-list="false" accept=".md" :before-upload="reimportMd">
              <el-button size="small" text>📂 导入.md</el-button>
            </el-upload>
          </div>
        </div>
        <textarea
          ref="textareaRef"
          v-model="form.content"
          class="md-textarea"
          placeholder="在这里写 Markdown..."
          spellcheck="false"
          @input="onInput"
          @keydown.tab.prevent="insertTab"
        />
      </div>
    </div>

    <!-- ── 右栏：预览区 ──────────────────────────────────── -->
    <div class="editor-right">
      <div class="preview-header">👁 实时预览</div>
      <div class="md-body preview-body" v-html="previewHtml" />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import DOMPurify from 'dompurify'
import { articlesApi } from '@/api/endpoints.js'

const props = defineProps({ articleId: { type: Number, default: null } })
const emit  = defineEmits(['saved', 'cancel'])

// ── Marked 配置 ──────────────────────────────────────────
marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    const l = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language: l }).value
  },
}))
marked.use({ gfm: true, breaks: true })

// ── State ─────────────────────────────────────────────────
const saving      = ref(false)
const textareaRef = ref(null)

const form = ref({
  title: '',
  summary: '',
  content: '',
  tags: '',
  cover_image: '',
  is_published: false,
})

const previewHtml = computed(() => {
  if (!form.value.content) return '<p class="text-muted" style="padding:20px">（预览区域）</p>'
  return DOMPurify.sanitize(marked.parse(form.value.content))
})

// ── 加载已有文章 ──────────────────────────────────────────
onMounted(async () => {
  if (props.articleId) {
    try {
      const a = await articlesApi.getById(props.articleId)
      form.value = {
        title:        a.title        ?? '',
        summary:      a.summary      ?? '',
        content:      a.content      ?? '',
        tags:         a.tags         ?? '',
        cover_image:  a.cover_image  ?? '',
        is_published: a.is_published ?? false,
      }
    } catch { ElMessage.error('加载文章失败') }
  }
})

// ── 保存 ──────────────────────────────────────────────────
async function save() {
  if (!form.value.title.trim()) { ElMessage.warning('请填写标题'); return }
  if (!form.value.content.trim()) { ElMessage.warning('请填写内容'); return }
  saving.value = true
  try {
    const payload = {
      title:        form.value.title,
      summary:      form.value.summary,
      content:      form.value.content,
      tags:         form.value.tags,
      is_published: form.value.is_published,
    }
    if (props.articleId) {
      await articlesApi.update(props.articleId, payload)
    } else {
      await articlesApi.create(payload)
    }
    ElMessage.success('保存成功')
    emit('saved')
  } catch (e) {
    ElMessage.error(e?.detail || '保存失败')
  } finally { saving.value = false }
}

// ── 封面图上传 ────────────────────────────────────────────
async function uploadCover(file) {
  if (!file) return
  if (!props.articleId) {
    ElMessage.info('请先保存文章，再上传封面图')
    return
  }
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await articlesApi.uploadCover(props.articleId, fd)
    form.value.cover_image = res.cover_image
    ElMessage.success('封面已更新')
  } catch { ElMessage.error('封面上传失败') }
}

// ── 重新导入 .md ──────────────────────────────────────────
async function reimportMd(file) {
  const text = await file.text()
  form.value.content = text
  ElMessage.success('已导入')
  return false
}

// ── Markdown 工具栏 ───────────────────────────────────────
function getTextarea() { return textareaRef.value }

function insertSnippet(before, after, placeholder) {
  const el = getTextarea()
  const start = el.selectionStart
  const end   = el.selectionEnd
  const sel   = form.value.content.slice(start, end) || placeholder
  const newText =
    form.value.content.slice(0, start) +
    before + sel + after +
    form.value.content.slice(end)
  form.value.content = newText
  nextTick(() => {
    el.focus()
    el.setSelectionRange(start + before.length, start + before.length + sel.length)
  })
}

function insertLine(prefix) {
  const el = getTextarea()
  const start = el.selectionStart
  const before = form.value.content.slice(0, start)
  const after  = form.value.content.slice(start)
  const lineStart = before.lastIndexOf('\n') + 1
  form.value.content =
    form.value.content.slice(0, lineStart) + prefix + form.value.content.slice(lineStart)
  nextTick(() => { el.focus(); el.setSelectionRange(lineStart + prefix.length, lineStart + prefix.length) })
}

function insertTab(e) {
  const el = getTextarea()
  const start = el.selectionStart
  form.value.content = form.value.content.slice(0, start) + '  ' + form.value.content.slice(start)
  nextTick(() => el.setSelectionRange(start + 2, start + 2))
}

function onInput() { /* 预览通过 computed 自动更新 */ }
</script>

<style scoped>
.editor-wrap {
  display: flex; gap: 0; height: calc(100vh - 80px);
  overflow: hidden;
}

/* ── 左栏 ──────────────────────────────────────────────── */
.editor-left {
  flex: 1; min-width: 0; display: flex; flex-direction: column;
  border-right: 1px solid #1e293b; overflow: hidden;
}
.meta-form   { padding: 16px; border-bottom: 1px solid #1e293b; flex-shrink: 0; }
.editor-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }

/* 封面 */
.cover-box      { position: relative; width: 120px; height: 80px; cursor: pointer; border-radius: 8px; overflow: hidden; background: #1e293b; }
.cover-preview  { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: .8125rem; color: #64748b; }
.cover-upload   { position: absolute; inset: 0; opacity: 0; width: 100%; height: 100%; }
.cover-upload :deep(.el-upload) { width: 100%; height: 100%; display: block; }
.cover-overlay  { width: 100%; height: 100%; }

/* MD 编辑器 */
.md-editor-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.md-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 12px; background: #1e293b; border-bottom: 1px solid #334155;
  flex-shrink: 0; flex-wrap: wrap; gap: 4px;
}
.md-toolbar-title { font-size: .8125rem; color: #60a5fa; font-weight: 600; }
.toolbar-btns { display: flex; align-items: center; gap: 2px; flex-wrap: wrap; }
.md-textarea {
  flex: 1; resize: none; background: #0d1117; color: #e2e8f0;
  border: none; outline: none; padding: 16px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 14px; line-height: 1.7; overflow-y: auto;
}
.md-textarea::placeholder { color: #334155; }

/* ── 右栏 ──────────────────────────────────────────────── */
.editor-right { width: 46%; flex-shrink: 0; display: flex; flex-direction: column; overflow: hidden; }
.preview-header {
  padding: 8px 16px; background: #1e293b; border-bottom: 1px solid #334155;
  font-size: .8125rem; color: #60a5fa; font-weight: 600; flex-shrink: 0;
}
.preview-body { flex: 1; overflow-y: auto; padding: 20px 24px; }
</style>
