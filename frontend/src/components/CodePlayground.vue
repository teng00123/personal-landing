<template>
  <div class="playground-container">
    <!-- 头部工具栏 -->
    <div class="playground-header">
      <div class="left">
        <select v-model="selectedLang" class="lang-select">
          <option v-for="lang in languages" :key="lang.id" :value="lang.id">
            {{ lang.name }}
          </option>
        </select>
        <span v-if="snippetId" class="snippet-badge">
          📎 {{ $t('playground.shared_snippet') }}
        </span>
      </div>
      <div class="right">
        <button class="btn btn-secondary" @click="copyCode" :title="$t('playground.copy')">
          📋
        </button>
        <button class="btn btn-secondary" @click="shareSnippet" :title="$t('playground.share')">
          🔗
        </button>
        <button
          class="btn btn-primary run-btn"
          :disabled="running"
          @click="runCode"
        >
          <span v-if="running">⏳ {{ $t('playground.running') }}</span>
          <span v-else>▶ {{ $t('playground.run') }}</span>
        </button>
      </div>
    </div>

    <!-- Monaco 编辑器区 -->
    <div class="editor-wrapper" ref="editorContainer" />

    <!-- 输入区（stdin） -->
    <div class="stdin-area">
      <label>{{ $t('playground.stdin') }}</label>
      <textarea v-model="stdin" :placeholder="$t('playground.stdin_placeholder')" rows="2" />
    </div>

    <!-- 输出区 -->
    <div class="output-area" :class="{ error: result?.exit_code !== 0 && result !== null }">
      <div class="output-header">
        <span>{{ $t('playground.output') }}</span>
        <span v-if="result" class="meta">
          Exit: {{ result.exit_code }} | {{ result.duration_ms }}ms
        </span>
      </div>
      <pre class="output-content" v-if="result">{{ result.stdout || result.stderr || $t('playground.no_output') }}</pre>
      <pre class="output-content error-text" v-if="result?.stderr && result.exit_code !== 0">{{ result.stderr }}</pre>
      <div class="output-placeholder" v-else-if="!result">
        {{ $t('playground.run_hint') }}
      </div>
    </div>

    <!-- AI 代码分析（可展开） -->
    <div class="ai-panel" v-if="aiSuggestions">
      <div class="ai-header" @click="showAI = !showAI">
        🤖 AI {{ $t('playground.ai_suggestions') }}
        <span class="toggle">{{ showAI ? '▲' : '▼' }}</span>
      </div>
      <div class="ai-body" v-show="showAI">
        <pre>{{ aiSuggestions }}</pre>
        <button class="btn btn-sm btn-secondary" @click="analyzeWithAI">
          🔄 {{ $t('playground.re_analyze') }}
        </button>
      </div>
    </div>
    <button v-else class="btn btn-sm ai-analyze-btn" @click="analyzeWithAI" :disabled="analyzingAI">
      🤖 {{ analyzingAI ? $t('playground.analyzing') : $t('playground.ai_analyze') }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const props = defineProps({
  initialCode:     { type: String, default: '' },
  initialLanguage: { type: String, default: 'python' },
  snippetId:       { type: String, default: null },
})

const editorContainer = ref(null)
const selectedLang    = ref(props.initialLanguage)
const stdin           = ref('')
const running         = ref(false)
const result          = ref(null)
const languages       = ref([])
const aiSuggestions   = ref(null)
const showAI          = ref(true)
const analyzingAI     = ref(false)

let monacoEditor = null

// ── 初始化 Monaco ─────────────────────────────────────────
onMounted(async () => {
  // 动态加载 Monaco（避免 SSR 问题）
  try {
    const monaco = await import('monaco-editor')
    monacoEditor = monaco.editor.create(editorContainer.value, {
      value:              props.initialCode || getDefaultCode(selectedLang.value),
      language:           monacoLang(selectedLang.value),
      theme:              document.documentElement.dataset.theme === 'dark' ? 'vs-dark' : 'vs',
      fontSize:           14,
      lineNumbers:        'on',
      minimap:            { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout:    true,
      tabSize:            4,
      wordWrap:           'on',
    })

    // 主题跟随
    const observer = new MutationObserver(() => {
      monaco.editor.setTheme(
        document.documentElement.dataset.theme === 'dark' ? 'vs-dark' : 'vs'
      )
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  } catch (e) {
    console.warn('Monaco editor not available, using textarea fallback', e)
  }

  // 加载语言列表
  try {
    const res = await fetch('/api/v1/sandbox/languages')
    const data = await res.json()
    languages.value = data.languages
  } catch {
    languages.value = [
      { id: 'python', name: 'Python 3' },
      { id: 'javascript', name: 'Node.js' },
    ]
  }

  // 加载分享片段
  if (props.snippetId) {
    loadSnippet(props.snippetId)
  }
})

onBeforeUnmount(() => {
  monacoEditor?.dispose()
})

// ── 语言切换 ──────────────────────────────────────────────
watch(selectedLang, (lang) => {
  if (monacoEditor) {
    const monaco = window.monaco
    if (monaco) {
      const model = monacoEditor.getModel()
      monaco.editor.setModelLanguage(model, monacoLang(lang))
      monacoEditor.setValue(getDefaultCode(lang))
    }
  }
  result.value = null
  aiSuggestions.value = null
})

// ── 执行代码 ──────────────────────────────────────────────
async function runCode() {
  const code = monacoEditor ? monacoEditor.getValue() : ''
  if (!code.trim()) {
    ElMessage.warning(t('playground.empty_code'))
    return
  }
  running.value = true
  result.value  = null
  try {
    const res = await fetch('/api/v1/sandbox/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: selectedLang.value, code, stdin: stdin.value || null }),
    })
    result.value = await res.json()
    if (result.value.exit_code !== 0) {
      ElMessage.error(t('playground.run_error'))
    }
  } catch (e) {
    ElMessage.error(t('playground.network_error'))
  } finally {
    running.value = false
  }
}

// ── 复制代码 ──────────────────────────────────────────────
async function copyCode() {
  const code = monacoEditor ? monacoEditor.getValue() : ''
  await navigator.clipboard.writeText(code)
  ElMessage.success(t('playground.copied'))
}

// ── 分享片段 ──────────────────────────────────────────────
async function shareSnippet() {
  const code = monacoEditor ? monacoEditor.getValue() : ''
  try {
    const res = await fetch('/api/v1/sandbox/snippets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: selectedLang.value, code, title: 'Shared Snippet' }),
    })
    const data = await res.json()
    const url = `${window.location.origin}${data.share_url}`
    await navigator.clipboard.writeText(url)
    ElMessage.success(t('playground.share_copied'))
  } catch {
    ElMessage.error(t('playground.share_failed'))
  }
}

// ── 加载片段 ──────────────────────────────────────────────
async function loadSnippet(id) {
  try {
    const res  = await fetch(`/api/v1/sandbox/snippets/${id}`)
    const data = await res.json()
    selectedLang.value = data.language
    monacoEditor?.setValue(data.code)
  } catch {
    ElMessage.error(t('playground.snippet_not_found'))
  }
}

// ── AI 分析 ───────────────────────────────────────────────
async function analyzeWithAI() {
  const code = monacoEditor ? monacoEditor.getValue() : ''
  if (!code.trim()) return
  analyzingAI.value = true
  try {
    const res = await fetch('/api/v1/ai/write/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: code, goal: 'clarity' }),
    })
    const data = await res.json()
    aiSuggestions.value = data.suggestions
    showAI.value = true
  } catch {
    ElMessage.warning(t('playground.ai_unavailable'))
  } finally {
    analyzingAI.value = false
  }
}

// ── 工具函数 ──────────────────────────────────────────────
function monacoLang(lang) {
  return { javascript: 'javascript', python: 'python', bash: 'shell', go: 'go' }[lang] || lang
}

function getDefaultCode(lang) {
  const defaults = {
    python:     'print("Hello, World!")',
    javascript: 'console.log("Hello, World!")',
    bash:       'echo "Hello, World!"',
    go: `package main\nimport "fmt"\nfunc main() {\n\tfmt.Println("Hello, World!")\n}`,
  }
  return defaults[lang] || ''
}
</script>

<style scoped>
.playground-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.playground-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border);
}

.left, .right { display: flex; gap: 8px; align-items: center; }

.lang-select {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 13px;
}

.editor-wrapper {
  height: 300px;
  min-height: 200px;
}

.stdin-area {
  padding: 6px 12px;
}
.stdin-area label {
  font-size: 12px;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 4px;
}
.stdin-area textarea {
  width: 100%;
  resize: vertical;
  font-family: monospace;
  font-size: 13px;
  padding: 6px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.output-area {
  margin: 0 8px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.output-area.error { border-color: #f56c6c; }

.output-header {
  display: flex;
  justify-content: space-between;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  font-size: 12px;
  color: var(--text-secondary);
}
.output-content {
  margin: 0;
  padding: 10px;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  background: var(--bg-primary);
  color: var(--text-primary);
}
.error-text { color: #f56c6c; }
.output-placeholder {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
}

.ai-panel {
  margin: 0 8px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
}
.ai-header {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  cursor: pointer;
  background: var(--bg-tertiary);
  font-size: 13px;
  font-weight: 500;
}
.ai-body pre {
  padding: 10px;
  font-size: 13px;
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
}

.ai-analyze-btn {
  margin: 0 8px 8px;
  align-self: flex-start;
}

.snippet-badge {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 10px;
}

.btn {
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: opacity 0.2s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); }
.btn-sm { padding: 3px 8px; font-size: 12px; }
.run-btn { min-width: 80px; }
</style>
