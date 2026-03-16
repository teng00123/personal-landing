<template>
  <!-- 搜索触发按钮 -->
  <button class="search-trigger" @click="openModal" :aria-label="$t('search.placeholder')">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <span class="search-hint">{{ $t('search.placeholder') }}</span>
    <kbd>⌘K</kbd>
  </button>

  <!-- 搜索弹窗 -->
  <Teleport to="body">
    <Transition name="search-modal">
      <div v-if="open" class="search-overlay" @click.self="close">
        <div class="search-box">
          <!-- 输入框 -->
          <div class="search-input-wrap">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              class="search-input"
              :placeholder="$t('search.placeholder')"
              @input="onInput"
              @keydown.esc="close"
              @keydown.enter="doSearch"
            />
            <button v-if="query" class="search-clear" @click="query = ''; results = null">✕</button>
          </div>

          <!-- 建议列表 -->
          <ul v-if="suggestions.length && !results" class="search-suggestions">
            <li
              v-for="s in suggestions"
              :key="s"
              class="suggest-item"
              @click="query = s; doSearch()"
            >
              <span class="suggest-icon">🔍</span> {{ s }}
            </li>
          </ul>

          <!-- 搜索结果 -->
          <div v-if="results" class="search-results">
            <div v-if="results.total === 0" class="search-empty">
              {{ $t('search.no_results') }}
            </div>
            <template v-else>
              <!-- 文章结果 -->
              <div v-if="results.articles.length" class="result-group">
                <div class="result-group-title">📝 {{ $t('nav.articles') }}</div>
                <router-link
                  v-for="a in results.articles"
                  :key="a.id"
                  :to="`/articles/${a.slug}`"
                  class="result-item"
                  @click="close"
                >
                  <span class="result-title" v-html="highlight(a.title)"></span>
                  <span v-if="a.summary" class="result-desc">{{ a.summary }}</span>
                </router-link>
              </div>
              <!-- 项目结果 -->
              <div v-if="results.projects.length" class="result-group">
                <div class="result-group-title">🚀 {{ $t('nav.projects') }}</div>
                <router-link
                  v-for="p in results.projects"
                  :key="p.id"
                  to="/projects"
                  class="result-item"
                  @click="close"
                >
                  <span class="result-title" v-html="highlight(p.name)"></span>
                  <span v-if="p.description" class="result-desc">{{ p.description }}</span>
                </router-link>
              </div>
            </template>
          </div>

          <!-- 热门搜索 -->
          <div v-if="!query && hotKeywords.length" class="search-hot">
            <div class="result-group-title">🔥 热门搜索</div>
            <div class="hot-tags">
              <button
                v-for="kw in hotKeywords"
                :key="kw.word"
                class="hot-tag"
                @click="query = kw.word; doSearch()"
              >{{ kw.word }}</button>
            </div>
          </div>

          <div class="search-footer">
            <span><kbd>Enter</kbd> 搜索</span>
            <span><kbd>Esc</kbd> 关闭</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import http from '@/api/http.js'

const open         = ref(false)
const query        = ref('')
const results      = ref(null)
const suggestions  = ref([])
const hotKeywords  = ref([])
const inputRef     = ref(null)
let suggestTimer   = null

// 打开弹窗时统一 focus input
watch(open, (val) => {
  if (val) nextTick(() => inputRef.value?.focus())
})

function openModal() {
  open.value = true
}

async function loadHot() {
  try {
    const data = await http.get('/search/hot')
    hotKeywords.value = data.keywords || []
  } catch {}
}

function close() {
  open.value  = false
  query.value = ''
  results.value = null
  suggestions.value = []
}

async function doSearch() {
  if (!query.value.trim()) return
  try {
    results.value = await http.get(`/search?q=${encodeURIComponent(query.value)}&limit=8`)
    suggestions.value = []
  } catch {}
}

function onInput() {
  results.value = null
  clearTimeout(suggestTimer)
  if (!query.value.trim()) { suggestions.value = []; return }
  suggestTimer = setTimeout(async () => {
    try {
      const data = await http.get(`/search/suggest?q=${encodeURIComponent(query.value)}`)
      suggestions.value = data.suggestions || []
    } catch {}
  }, 280)
}

function highlight(text) {
  if (!query.value) return text
  const re = new RegExp(`(${query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(re, '<mark>$1</mark>')
}

// 键盘快捷键 ⌘K / Ctrl+K
function onKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    open.value = !open.value
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  loadHot()
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* 触发按钮 */
.search-trigger {
  display: flex; align-items: center; gap: 8px;
  background: var(--c-bg-card); border: 1px solid var(--c-border);
  color: var(--c-text-muted); border-radius: 8px;
  padding: 6px 12px; cursor: pointer; font-size: .875rem;
  transition: all .15s; white-space: nowrap;
}
.search-trigger:hover { border-color: var(--c-primary); color: var(--c-text); }
.search-hint { flex: 1; text-align: left; }
kbd {
  background: var(--c-bg-card2); border: 1px solid var(--c-border);
  border-radius: 4px; padding: 1px 5px; font-size: .75rem; font-family: inherit;
}

/* 遮罩 */
.search-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(0,0,0,.6); backdrop-filter: blur(4px);
  display: flex; align-items: flex-start; justify-content: center;
  padding-top: 12vh;
}

/* 弹窗 */
.search-box {
  width: min(680px, 94vw);
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

/* 输入行 */
.search-input-wrap {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px; border-bottom: 1px solid var(--c-border);
}
.search-icon { color: var(--c-text-muted); flex-shrink: 0; }
.search-input {
  flex: 1; background: none; border: none; outline: none;
  color: var(--c-text); font-size: 1rem;
}
.search-input::placeholder { color: var(--c-text-muted); }
.search-clear {
  background: none; border: none; color: var(--c-text-muted);
  cursor: pointer; padding: 2px 6px; border-radius: 4px; font-size: .875rem;
}
.search-clear:hover { color: var(--c-text); }

/* 建议 */
.search-suggestions { list-style: none; max-height: 280px; overflow-y: auto; }
.suggest-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; cursor: pointer;
  color: var(--c-text-muted); font-size: .9375rem;
  transition: background .12s;
}
.suggest-item:hover { background: var(--c-bg-card2); color: var(--c-text); }

/* 结果 */
.search-results { max-height: 420px; overflow-y: auto; padding: 8px 0; }
.search-empty   { text-align: center; padding: 32px 0; color: var(--c-text-muted); }
.result-group   { margin-bottom: 4px; }
.result-group-title {
  padding: 6px 16px 4px; font-size: .75rem;
  color: var(--c-text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: .05em;
}
.result-item {
  display: flex; flex-direction: column; gap: 2px;
  padding: 9px 16px; text-decoration: none;
  transition: background .12s; cursor: pointer;
}
.result-item:hover { background: var(--c-bg-card2); }
.result-title { color: var(--c-text); font-size: .9375rem; font-weight: 500; }
.result-title :deep(mark) {
  background: rgba(59,130,246,.25); color: var(--c-primary);
  border-radius: 2px; padding: 0 2px;
}
.result-desc  { color: var(--c-text-muted); font-size: .8125rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 热门搜索 */
.search-hot { padding: 12px 16px; }
.hot-tags   { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.hot-tag {
  background: var(--c-bg-card2); border: 1px solid var(--c-border);
  color: var(--c-text-muted); border-radius: 16px;
  padding: 4px 12px; font-size: .8125rem; cursor: pointer;
  transition: all .12s;
}
.hot-tag:hover { border-color: var(--c-primary); color: var(--c-primary); }

/* 底栏 */
.search-footer {
  padding: 8px 16px; border-top: 1px solid var(--c-border);
  display: flex; gap: 16px; font-size: .75rem; color: var(--c-text-muted);
}

/* 动画 */
.search-modal-enter-active, .search-modal-leave-active { transition: all .2s ease; }
.search-modal-enter-from, .search-modal-leave-to { opacity: 0; }
.search-modal-enter-from .search-box, .search-modal-leave-to .search-box {
  transform: scale(.96) translateY(-8px);
}
</style>
