<template>
  <div id="app">
    <LanguageSwitcher />
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta.transition || 'page-fade'" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import { useThemeStore } from './store/theme.js'
import { useRouter, useRoute } from 'vue-router'
import { onMounted } from 'vue'

// 初始化主题
useThemeStore()

const router = useRouter()
const route  = useRoute()

onMounted(() => {
  // 仅在访问根路径且本次会话尚未看过欢迎页时跳转
  const seen = sessionStorage.getItem('splash_seen')
  if (!seen && (route.path === '/' || route.path === '')) {
    sessionStorage.setItem('splash_seen', '1')
    router.replace('/splash')
  }
})
</script>

<style>
#app {
  font-family: 'Inter', 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── 页面淡入淡出 ──────────────────────────────────────── */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity .22s ease, transform .22s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── 侧滑（左→右）────────────────────────────────────── */
.slide-enter-active,
.slide-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.slide-enter-from { opacity: 0; transform: translateX(16px); }
.slide-leave-to   { opacity: 0; transform: translateX(-16px); }

/* ── Loading spinner ──────────────────────────────────── */
.page-loading {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: var(--c-bg);
}
.page-loading::after {
  content: '';
  width: 36px; height: 36px;
  border: 3px solid var(--c-border);
  border-top-color: var(--c-primary);
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Skeleton 占位 ────────────────────────────────────── */
.skeleton {
  background: linear-gradient(90deg, var(--c-bg-card) 25%, var(--c-bg-card2) 50%, var(--c-bg-card) 75%);
  background-size: 200% 100%;
  animation: skeleton-wave 1.4s ease infinite;
  border-radius: 6px;
}
@keyframes skeleton-wave {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
