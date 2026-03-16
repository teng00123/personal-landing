<template>
  <div class="theme-switcher" :title="labelMap[themeStore.mode]">
    <button
      v-for="item in options"
      :key="item.value"
      :class="['theme-btn', { active: themeStore.mode === item.value }]"
      @click="themeStore.setMode(item.value)"
      :aria-label="item.label"
    >
      <span class="theme-icon">{{ item.icon }}</span>
    </button>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/store/theme.js'

const themeStore = useThemeStore()

const options = [
  { value: 'light', icon: '☀️', label: '浅色模式' },
  { value: 'auto',  icon: '🌗', label: '跟随系统' },
  { value: 'dark',  icon: '🌙', label: '深色模式' },
]

const labelMap = { light: '浅色', auto: '跟随系统', dark: '深色' }
</script>

<style scoped>
.theme-switcher {
  display: flex;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: 20px;
  padding: 2px;
  gap: 2px;
}
.theme-btn {
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 16px;
  padding: 4px 8px;
  transition: background .18s;
  line-height: 1;
}
.theme-btn:hover   { background: var(--c-bg-card2); }
.theme-btn.active  { background: var(--c-primary); }
.theme-icon { font-size: 14px; }
</style>
