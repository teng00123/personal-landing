/**
 * 主题管理 Store — Iteration 5
 * 支持 dark / light / auto 三种模式
 * auto 模式跟随系统 prefers-color-scheme
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// ThemeMode: 'dark' | 'light' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  const mode = ref(localStorage.getItem('theme') || 'auto')

  // 当前实际主题（auto 下根据系统解析）
  const resolved = ref('dark')

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  function applyTheme() {
    const isDark =
      mode.value === 'dark' ||
      (mode.value === 'auto' && mediaQuery.matches)
    resolved.value = isDark ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', resolved.value)
  }

  function setMode(m) {
    mode.value = m
    localStorage.setItem('theme', m)
    applyTheme()
  }

  // 监听系统主题变化
  mediaQuery.addEventListener('change', applyTheme)

  // 初始化 & mode 变化时应用
  watch(mode, applyTheme, { immediate: true })

  return { mode, resolved, setMode }
})
