<template>
  <div class="playground-page">
    <div class="pg-hero">
      <h1 class="pg-title">
        <span class="pg-title-icon">⚡</span>
        代码运行器
      </h1>
      <p class="pg-desc">在线运行 Python / Node.js / Bash / Go，支持代码分享与 AI 分析</p>
    </div>
    <div class="pg-content">
      <CodePlayground
        :initial-language="lang"
        :snippet-id="snippetId"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import CodePlayground from '@/components/CodePlayground.vue'

const route     = useRoute()
const lang      = computed(() => route.query.lang || 'python')
const snippetId = computed(() => route.query.snippet || null)
</script>

<style scoped>
.playground-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}

.pg-hero {
  margin-bottom: 24px;
}

.pg-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0 0 8px;
  background: linear-gradient(135deg, #7aadff, #c4a8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.pg-title-icon {
  -webkit-text-fill-color: initial;
  font-size: 1.5rem;
}

.pg-desc {
  margin: 0;
  font-size: .9375rem;
  color: var(--c-text-muted);
}

.pg-content {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}
</style>
