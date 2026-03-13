<template>
  <div class="section" style="padding-top:48px">
    <div class="container" style="max-width:860px">

      <!-- 返回 -->
      <router-link to="/articles" class="back-link">← 返回文章列表</router-link>

      <!-- 骨架屏 -->
      <el-skeleton v-if="loading" :rows="12" animated style="margin-top:24px" />

      <!-- 404 -->
      <el-result v-else-if="!article" icon="404" title="文章不存在">
        <template #extra>
          <router-link to="/articles"><el-button>返回列表</el-button></router-link>
        </template>
      </el-result>

      <!-- 正文 -->
      <template v-else>
        <div class="art-header fade-in-up">
          <div class="tag-row">
            <el-tag v-for="t in parseTags(article.tags)" :key="t">{{ t }}</el-tag>
          </div>
          <h1 class="art-title">{{ article.title }}</h1>
          <div class="art-meta">
            <span>📅 {{ fmtDate(article.published_at) }}</span>
            <span>👁 {{ article.view_count }} 阅读</span>
          </div>
          <img v-if="article.cover_image" :src="article.cover_image" class="art-cover" />
        </div>

        <!-- Markdown 渲染 -->
        <article class="md-body fade-in-up" v-html="html"></article>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { articlesApi } from '@/api/endpoints.js'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import DOMPurify from 'dompurify'
import dayjs from 'dayjs'

const route   = useRoute()
const article = ref(null)
const loading = ref(true)

// 配置 marked
marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    const l = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language: l }).value
  },
}))
marked.use({ gfm: true, breaks: true })

const html = computed(() => {
  if (!article.value) return ''
  return DOMPurify.sanitize(marked.parse(article.value.content))
})

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY年MM月DD日') : ''

onMounted(async () => {
  try {
    article.value = await articlesApi.getBySlug(route.params.slug)
  } catch {
    article.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.back-link { color: #60a5fa; font-size: .875rem; display: inline-block; margin-bottom: 28px; }
.back-link:hover { text-decoration: underline; }
.art-header { margin-bottom: 44px; }
.tag-row    { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.art-title  { font-size: clamp(1.75rem,4vw,2.5rem); font-weight: 800; color: #f1f5f9; line-height: 1.25; margin-bottom: 14px; }
.art-meta   { display: flex; gap: 24px; color: #64748b; font-size: .875rem; margin-bottom: 22px; }
.art-cover  { width: 100%; max-height: 380px; object-fit: cover; border-radius: 10px; }
</style>
