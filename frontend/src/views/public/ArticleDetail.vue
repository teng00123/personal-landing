<template>
  <!-- 阅读进度条 -->
  <div class="read-progress" :style="{ width: readProgress + '%' }"></div>

  <div class="section" style="padding-top:48px">
    <div class="container art-layout">

      <!-- ── 正文区 ──────────────────────────────────────── -->
      <div class="art-main">
        <router-link to="/articles" class="back-link">← 返回文章列表</router-link>

        <el-skeleton v-if="loading" :rows="14" animated style="margin-top:24px" />

        <el-result v-else-if="!article" icon="404" title="文章不存在" sub-title="该文章可能已删除或未发布">
          <template #extra>
            <router-link to="/articles"><el-button type="primary">返回列表</el-button></router-link>
          </template>
        </el-result>

        <template v-else>
          <div class="art-header fade-in-up">
            <div class="tag-row">
              <el-tag v-for="t in parseTags(article.tags)" :key="t" size="small">{{ t }}</el-tag>
            </div>
            <h1 class="art-title">{{ article.title }}</h1>
            <div class="art-meta">
              <span>📅 {{ fmtDate(article.published_at) }}</span>
              <span>👁 {{ article.view_count }} 阅读</span>
              <span>⏱ 约 {{ readTime }} 分钟</span>
            </div>
            <img v-if="article.cover_image" :src="article.cover_image" class="art-cover" />
          </div>

          <article ref="articleRef" class="md-body fade-in-up" v-html="html"></article>

          <!-- 上一篇 / 下一篇（预留槽位） -->
          <div class="art-nav">
            <router-link to="/articles" class="art-nav-btn">← 返回列表</router-link>
          </div>
        </template>
      </div>

      <!-- ── 目录侧边栏 ──────────────────────────────────── -->
      <aside class="toc-sidebar" v-if="toc.length > 2">
        <div class="toc-title">📋 目录</div>
        <nav class="toc-nav">
          <a
            v-for="h in toc"
            :key="h.id"
            :href="`#${h.id}`"
            class="toc-item"
            :class="[`toc-h${h.level}`, { active: activeId === h.id }]"
            @click.prevent="scrollTo(h.id)"
          >{{ h.text }}</a>
        </nav>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { articlesApi } from '@/api/endpoints.js'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import DOMPurify from 'dompurify'
import dayjs from 'dayjs'

const route      = useRoute()
const article    = ref(null)
const loading    = ref(true)
const articleRef = ref(null)
const readProgress = ref(0)
const activeId   = ref('')
const toc        = ref([])

// ── Marked 配置 ──────────────────────────────────────────
marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    const l = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language: l }).value
  },
}))

// 自定义 renderer：给标题加锚点 id
const renderer = new marked.Renderer()
renderer.heading = function (text, level) {
  const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fff]+/g, '-').replace(/^-|-$/g, '')
  return `<h${level} id="${id}">${text}</h${level}>`
}
marked.use({ renderer, gfm: true, breaks: true })

// ── 计算属性 ─────────────────────────────────────────────
const html = computed(() => {
  if (!article.value) return ''
  return DOMPurify.sanitize(marked.parse(article.value.content))
})

const readTime = computed(() => {
  const words = (article.value?.content || '').length
  return Math.max(1, Math.ceil(words / 400))
})

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY年MM月DD日') : ''

// ── 阅读进度 ─────────────────────────────────────────────
function onScroll() {
  const el = articleRef.value
  if (!el) return
  const scrollTop  = window.scrollY
  const docHeight  = document.documentElement.scrollHeight - window.innerHeight
  readProgress.value = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0

  // 高亮当前目录项
  const headings = el.querySelectorAll('h1,h2,h3,h4')
  let current = ''
  headings.forEach((h) => {
    if (h.getBoundingClientRect().top <= 100) current = h.id
  })
  activeId.value = current
}

// ── 目录提取 ─────────────────────────────────────────────
function buildToc() {
  const el = articleRef.value
  if (!el) return
  const headings = el.querySelectorAll('h1,h2,h3,h4')
  toc.value = Array.from(headings).map((h) => ({
    id:    h.id,
    text:  h.textContent,
    level: parseInt(h.tagName[1]),
  }))
}

function scrollTo(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// ── 代码块复制按钮 ────────────────────────────────────────
function addCopyButtons() {
  const el = articleRef.value
  if (!el) return
  el.querySelectorAll('pre').forEach((pre) => {
    if (pre.querySelector('.copy-btn')) return
    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.textContent = '复制'
    btn.onclick = async () => {
      const code = pre.querySelector('code')?.textContent || ''
      await navigator.clipboard.writeText(code).catch(() => {})
      btn.textContent = '已复制 ✓'
      setTimeout(() => (btn.textContent = '复制'), 2000)
    }
    pre.style.position = 'relative'
    pre.appendChild(btn)
  })
}

onMounted(async () => {
  try {
    article.value = await articlesApi.getBySlug(route.params.slug)
    await nextTick()
    buildToc()
    addCopyButtons()
  } catch {
    article.value = null
  } finally {
    loading.value = false
  }
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
/* 阅读进度条 */
.read-progress {
  position: fixed; top: 0; left: 0; height: 3px; z-index: 9999;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width .1s linear;
}

/* 布局 */
.art-layout { display: flex; gap: 40px; align-items: flex-start; max-width: 1100px; }
.art-main   { flex: 1; min-width: 0; }

.back-link { color: #60a5fa; font-size: .875rem; display: inline-block; margin-bottom: 28px; }
.back-link:hover { text-decoration: underline; }

.art-header { margin-bottom: 40px; }
.tag-row    { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.art-title  { font-size: clamp(1.75rem,4vw,2.5rem); font-weight: 800; color: #f1f5f9; line-height: 1.25; margin-bottom: 14px; }
.art-meta   { display: flex; gap: 24px; color: #64748b; font-size: .875rem; margin-bottom: 22px; flex-wrap: wrap; }
.art-cover  { width: 100%; max-height: 380px; object-fit: cover; border-radius: 12px; margin-top: 8px; }

.art-nav     { display: flex; justify-content: flex-start; margin-top: 48px; padding-top: 24px; border-top: 1px solid #1e293b; }
.art-nav-btn { color: #60a5fa; font-size: .875rem; }
.art-nav-btn:hover { text-decoration: underline; }

/* 目录 */
.toc-sidebar {
  width: 220px; flex-shrink: 0;
  position: sticky; top: 80px;
  max-height: calc(100vh - 100px); overflow-y: auto;
}
.toc-title { font-size: .8rem; font-weight: 700; color: #60a5fa; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 12px; }
.toc-nav   { display: flex; flex-direction: column; gap: 2px; }
.toc-item  { font-size: .8125rem; color: #64748b; text-decoration: none; padding: 4px 8px; border-radius: 5px; transition: all .15s; line-height: 1.5; }
.toc-item:hover  { color: #e2e8f0; background: #1e293b; }
.toc-item.active { color: #60a5fa; background: rgba(59,130,246,.1); }
.toc-h1 { font-weight: 700; }
.toc-h2 { padding-left: 8px; }
.toc-h3 { padding-left: 20px; font-size: .78rem; }
.toc-h4 { padding-left: 32px; font-size: .75rem; }
</style>

<!-- 代码复制按钮全局样式（不加 scoped 因为是动态插入的） -->
<style>
.md-body pre { position: relative; }
.copy-btn {
  position: absolute; top: 8px; right: 10px;
  padding: 3px 10px; border-radius: 5px; border: none; cursor: pointer;
  font-size: .75rem; font-weight: 600;
  background: rgba(99,102,241,.2); color: #a5b4fc;
  transition: all .2s; opacity: 0;
}
.md-body pre:hover .copy-btn { opacity: 1; }
.copy-btn:hover { background: rgba(99,102,241,.4); color: #fff; }
</style>
