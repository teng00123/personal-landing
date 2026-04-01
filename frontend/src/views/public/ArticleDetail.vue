<template>
  <!-- 阅读进度条 -->
  <div class="read-progress" :class="{ done: progressDone }" :style="{ width: readProgress + '%' }"></div>

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
const readProgress  = ref(0)
const progressDone  = ref(false)
const activeId      = ref('')
const toc           = ref([])

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

  // 用文章元素本身的范围计算进度，而非整页高度
  const artTop    = el.getBoundingClientRect().top + window.scrollY
  const artHeight = el.offsetHeight
  const scrolled  = window.scrollY + window.innerHeight - artTop
  const pct = artHeight > 0 ? Math.min(100, Math.max(0, (scrolled / artHeight) * 100)) : 0
  readProgress.value = pct

  // 读完：颜色变绿，2s 后淡出
  if (pct >= 100 && !progressDone.value) {
    progressDone.value = true
  }

  // 高亮当前目录项
  const headings = el.querySelectorAll('h1,h2,h3,h4')
  let current = ''
  headings.forEach((h) => {
    if (h.getBoundingClientRect().top <= 120) current = h.id
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
    onScroll() // 初始化高亮 + 进度
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
  transition: width .1s linear, background .4s ease, opacity .6s ease;
  pointer-events: none;
}
.read-progress.done {
  background: linear-gradient(90deg, #10b981, #34d399);
  animation: progress-done 2s ease forwards;
}
@keyframes progress-done {
  0%   { opacity: 1; }
  60%  { opacity: 1; }
  100% { opacity: 0; }
}

/* 布局 */
.art-layout { display: flex; gap: 40px; align-items: flex-start; max-width: 1100px; }
.art-main   { flex: 1; min-width: 0; }

.back-link { color: var(--c-primary); font-size: .875rem; display: inline-block; margin-bottom: 28px; }
.back-link:hover { text-decoration: underline; }

.art-header { margin-bottom: 40px; }
.tag-row    { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.art-title  { font-size: clamp(1.75rem,4vw,2.5rem); font-weight: 800; color: var(--c-text); line-height: 1.25; margin-bottom: 14px; }
.art-meta   { display: flex; gap: 24px; color: var(--c-text-muted); font-size: .875rem; margin-bottom: 22px; flex-wrap: wrap; }
.art-cover  { width: 100%; max-height: 380px; object-fit: cover; border-radius: 12px; margin-top: 8px; display: block; }

.art-nav     { display: flex; justify-content: flex-start; margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--c-border); }
.art-nav-btn { color: var(--c-primary); font-size: .875rem; }
.art-nav-btn:hover { text-decoration: underline; }

/* 目录 */
.toc-sidebar {
  width: 220px; flex-shrink: 0;
  position: sticky; top: 80px;
  max-height: calc(100vh - 100px); overflow-y: auto;
}
.toc-title { font-size: .8rem; font-weight: 700; color: var(--c-primary); letter-spacing: .08em; text-transform: uppercase; margin-bottom: 12px; }
.toc-nav   { display: flex; flex-direction: column; gap: 2px; }
.toc-item  { font-size: .8125rem; color: var(--c-text-muted); text-decoration: none; padding: 4px 8px; border-radius: 5px; transition: all .15s; line-height: 1.5; }
.toc-item:hover  { color: var(--c-text); background: var(--c-bg-card2); }
.toc-item.active { color: var(--c-primary); background: rgba(59,111,212,.08); }
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
