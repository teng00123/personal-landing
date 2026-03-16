<template>
  <div class="ai-assistant">
    <div class="ai-header">
      <span>🤖 {{ $t('ai.title') }}</span>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </div>

    <!-- Tab 切换 -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 生成文章 -->
    <div v-show="activeTab === 'generate'" class="tab-body">
      <div class="field">
        <label>{{ $t('ai.topic') }}</label>
        <input v-model="genForm.topic" :placeholder="$t('ai.topic_placeholder')" />
      </div>
      <div class="field">
        <label>{{ $t('ai.outline') }} ({{ $t('common.optional') }})</label>
        <textarea v-model="genForm.outline" rows="3" :placeholder="$t('ai.outline_placeholder')" />
      </div>
      <div class="field row">
        <div>
          <label>{{ $t('ai.length') }}</label>
          <select v-model="genForm.length">
            <option value="short">{{ $t('ai.length_short') }}</option>
            <option value="medium">{{ $t('ai.length_medium') }}</option>
            <option value="long">{{ $t('ai.length_long') }}</option>
          </select>
        </div>
        <div>
          <label>{{ $t('ai.style') }}</label>
          <select v-model="genForm.style">
            <option value="technical">{{ $t('ai.style_technical') }}</option>
            <option value="casual">{{ $t('ai.style_casual') }}</option>
            <option value="academic">{{ $t('ai.style_academic') }}</option>
          </select>
        </div>
      </div>
      <button class="btn btn-primary" :disabled="loading.generate" @click="generateArticle">
        {{ loading.generate ? $t('ai.generating') : $t('ai.generate') }}
      </button>
      <div class="result-box" v-if="results.generate">
        <div class="result-actions">
          <button class="btn btn-sm" @click="copyResult(results.generate)">{{ $t('ai.copy') }}</button>
          <button class="btn btn-sm btn-primary" @click="$emit('insert', results.generate)">
            {{ $t('ai.insert_editor') }}
          </button>
        </div>
        <pre>{{ results.generate }}</pre>
      </div>
    </div>

    <!-- 内容优化 -->
    <div v-show="activeTab === 'optimize'" class="tab-body">
      <div class="field">
        <label>{{ $t('ai.content_to_optimize') }}</label>
        <textarea v-model="optForm.content" rows="5" :placeholder="$t('ai.paste_content')" />
      </div>
      <div class="field">
        <label>{{ $t('ai.optimize_goal') }}</label>
        <select v-model="optForm.goal">
          <option value="clarity">{{ $t('ai.goal_clarity') }}</option>
          <option value="seo">{{ $t('ai.goal_seo') }}</option>
          <option value="engagement">{{ $t('ai.goal_engagement') }}</option>
        </select>
      </div>
      <button class="btn btn-primary" :disabled="loading.optimize" @click="optimizeContent">
        {{ loading.optimize ? $t('ai.optimizing') : $t('ai.optimize') }}
      </button>
      <div class="result-box" v-if="results.optimize">
        <button class="btn btn-sm" @click="copyResult(results.optimize)">{{ $t('ai.copy') }}</button>
        <pre>{{ results.optimize }}</pre>
      </div>
    </div>

    <!-- 语法检查 -->
    <div v-show="activeTab === 'grammar'" class="tab-body">
      <div class="field">
        <label>{{ $t('ai.text_to_check') }}</label>
        <textarea v-model="gramForm.content" rows="5" :placeholder="$t('ai.paste_content')" />
      </div>
      <div class="field">
        <label>{{ $t('ai.language') }}</label>
        <select v-model="gramForm.lang">
          <option value="zh">{{ $t('ai.lang_zh') }}</option>
          <option value="en">{{ $t('ai.lang_en') }}</option>
        </select>
      </div>
      <button class="btn btn-primary" :disabled="loading.grammar" @click="checkGrammar">
        {{ loading.grammar ? $t('ai.checking') : $t('ai.check_grammar') }}
      </button>
      <div class="result-box" v-if="results.grammar">
        <div class="score-badge" :class="scoreClass(results.grammar.score)">
          {{ $t('ai.score') }}: {{ results.grammar.score ?? 'N/A' }}
        </div>
        <div v-if="results.grammar.issues?.length" class="issues-list">
          <div v-for="(issue, i) in results.grammar.issues" :key="i" class="issue-item">
            <span class="issue-pos">{{ issue.pos }}</span>
            <span class="issue-text">{{ issue.issue }}</span>
            <span class="issue-fix">→ {{ issue.fix }}</span>
          </div>
        </div>
        <div v-else class="no-issues">✅ {{ $t('ai.no_issues') }}</div>
      </div>
    </div>

    <!-- 摘要生成 -->
    <div v-show="activeTab === 'analyze'" class="tab-body">
      <div class="field">
        <label>{{ $t('ai.content_to_analyze') }}</label>
        <textarea v-model="analyzeForm.content" rows="5" :placeholder="$t('ai.paste_content')" />
      </div>
      <div class="action-row">
        <button class="btn" :disabled="loading.summary" @click="generateSummary">
          {{ loading.summary ? '...' : $t('ai.gen_summary') }}
        </button>
        <button class="btn" :disabled="loading.keywords" @click="extractKeywords">
          {{ loading.keywords ? '...' : $t('ai.extract_keywords') }}
        </button>
        <button class="btn" :disabled="loading.sentiment" @click="analyzeSentiment">
          {{ loading.sentiment ? '...' : $t('ai.analyze_sentiment') }}
        </button>
      </div>
      <div class="result-box" v-if="results.summary">
        <strong>{{ $t('ai.summary') }}:</strong>
        <p>{{ results.summary }}</p>
      </div>
      <div class="result-box" v-if="results.keywords?.length">
        <strong>{{ $t('ai.keywords') }}:</strong>
        <div class="keyword-tags">
          <span v-for="kw in results.keywords" :key="kw.word" class="keyword-tag">
            {{ kw.word }} <small>({{ (kw.weight * 100).toFixed(0) }}%)</small>
          </span>
        </div>
      </div>
      <div class="result-box" v-if="results.sentiment">
        <strong>{{ $t('ai.sentiment') }}:</strong>
        <span :class="['sentiment-badge', results.sentiment.sentiment]">
          {{ results.sentiment.sentiment }} ({{ results.sentiment.score?.toFixed(2) }})
        </span>
        <p class="sentiment-reason">{{ results.sentiment.reason }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
defineEmits(['close', 'insert'])

const activeTab = ref('generate')
const tabs = computed(() => [
  { id: 'generate', label: t('ai.tab_generate') },
  { id: 'optimize', label: t('ai.tab_optimize') },
  { id: 'grammar',  label: t('ai.tab_grammar') },
  { id: 'analyze',  label: t('ai.tab_analyze') },
])

const genForm     = ref({ topic: '', outline: '', length: 'medium', style: 'technical' })
const optForm     = ref({ content: '', goal: 'clarity' })
const gramForm    = ref({ content: '', lang: 'zh' })
const analyzeForm = ref({ content: '' })

const loading = ref({ generate: false, optimize: false, grammar: false, summary: false, keywords: false, sentiment: false })
const results = ref({ generate: null, optimize: null, grammar: null, summary: null, keywords: null, sentiment: null })

async function callAI(path, body, loadingKey, resultKey, extract = (d) => d) {
  loading.value[loadingKey] = true
  try {
    const res = await fetch(`/api/v1/ai/${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    results.value[resultKey] = extract(data)
  } catch (e) {
    ElMessage.error(t('ai.request_failed'))
  } finally {
    loading.value[loadingKey] = false
  }
}

const generateArticle = () => callAI('write/generate', genForm.value, 'generate', 'generate', d => d.content)
const optimizeContent  = () => callAI('write/optimize', optForm.value, 'optimize', 'optimize', d => d.suggestions)
const checkGrammar     = () => callAI('write/grammar', gramForm.value, 'grammar', 'grammar')
const generateSummary  = () => callAI('analyze/summary', analyzeForm.value, 'summary', 'summary', d => d.summary)
const extractKeywords  = () => callAI('analyze/keywords', analyzeForm.value, 'keywords', 'keywords', d => d.keywords)
const analyzeSentiment = () => callAI('analyze/sentiment', analyzeForm.value, 'sentiment', 'sentiment')

async function copyResult(text) {
  await navigator.clipboard.writeText(text)
  ElMessage.success(t('ai.copied'))
}

function scoreClass(score) {
  if (score === null || score === undefined) return 'score-unknown'
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-ok'
  return 'score-bad'
}
</script>

<style scoped>
.ai-assistant {
  width: 380px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,.15);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--primary);
  color: #fff;
  font-weight: 600;
}
.close-btn { background: none; border: none; color: #fff; cursor: pointer; font-size: 16px; }

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  background: var(--bg-tertiary);
}
.tab {
  flex: 1;
  padding: 8px 4px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }

.tab-body {
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 12px; color: var(--text-secondary); }
.field input, .field textarea, .field select {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}
.field.row { flex-direction: row; gap: 12px; }
.field.row > div { flex: 1; display: flex; flex-direction: column; gap: 4px; }

.btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 13px;
  transition: opacity 0.2s;
  align-self: flex-start;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.btn-sm { padding: 3px 8px; font-size: 12px; }

.action-row { display: flex; gap: 6px; flex-wrap: wrap; }

.result-box {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px;
  font-size: 13px;
}
.result-box pre { white-space: pre-wrap; margin: 0; max-height: 200px; overflow-y: auto; }
.result-actions { display: flex; gap: 6px; margin-bottom: 8px; }

.score-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
.score-good { background: #d4edda; color: #155724; }
.score-ok   { background: #fff3cd; color: #856404; }
.score-bad  { background: #f8d7da; color: #721c24; }
.score-unknown { background: var(--bg-tertiary); }

.issues-list { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
.issue-item { font-size: 12px; display: flex; gap: 6px; flex-wrap: wrap; }
.issue-pos  { font-weight: 600; color: var(--primary); }
.issue-text { color: var(--text-secondary); }
.issue-fix  { color: #28a745; }
.no-issues  { color: #28a745; font-size: 13px; }

.keyword-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.keyword-tag {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 12px;
}

.sentiment-badge { padding: 2px 8px; border-radius: 10px; font-size: 12px; }
.positive { background: #d4edda; color: #155724; }
.neutral  { background: #e2e3e5; color: #383d41; }
.negative { background: #f8d7da; color: #721c24; }
.sentiment-reason { font-size: 12px; color: var(--text-secondary); margin: 4px 0 0; }
</style>
