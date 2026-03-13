<template>
  <div class="admin-wrap">

    <!-- ── 移动端遮罩 ──────────────────────────────────── -->
    <div v-if="sideOpen" class="aside-mask" @click="sideOpen = false"></div>

    <!-- ── 侧边栏 ─────────────────────────────────────── -->
    <aside class="aside" :class="{ open: sideOpen }">
      <div class="aside__logo">
        <span>⚡ 后台管理</span>
        <el-icon class="aside__close" @click="sideOpen = false"><Close /></el-icon>
      </div>

      <nav class="aside-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="aside-nav__item"
          :class="{ active: route.path.startsWith(item.to) }"
          @click="sideOpen = false"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="aside-footer">
        <button class="aside-nav__item" @click="router.push('/')">
          <el-icon><House /></el-icon><span>查看主页</span>
        </button>
        <button class="aside-nav__item aside-nav__item--danger" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon><span>退出登录</span>
        </button>
      </div>
    </aside>

    <!-- ── 主区域 ─────────────────────────────────────── -->
    <div class="admin-body">

      <!-- 顶栏 -->
      <header class="admin-topbar">
        <button class="topbar__menu" @click="sideOpen = true">
          <el-icon :size="20"><Menu /></el-icon>
        </button>
        <div class="topbar__breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item to="/admin/dashboard">后台</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentNav">{{ currentNav.label }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar__right">
          <el-tag size="small" type="success">{{ auth.user?.username }}</el-tag>
        </div>
      </header>

      <!-- 内容 -->
      <main class="admin-main">
        <router-view />
      </main>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, User, Document, Monitor,
  House, SwitchButton, Close, Menu,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth.js'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const sideOpen = ref(false)

const navItems = [
  { to: '/admin/dashboard', label: '概览',     icon: 'DataAnalysis' },
  { to: '/admin/profile',   label: '个人资料', icon: 'User' },
  { to: '/admin/articles',  label: '文章管理', icon: 'Document' },
  { to: '/admin/projects',  label: '项目管理', icon: 'Monitor' },
]

const currentNav = computed(() =>
  navItems.find(n => route.path.startsWith(n.to))
)

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.admin-wrap { display: flex; min-height: 100vh; background: #0f172a; }

/* ── 侧边栏 ──────────────────────────────────────────── */
.aside {
  width: 220px; flex-shrink: 0;
  background: #0a1120;
  border-right: 1px solid #1e293b;
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; height: 100vh; z-index: 200;
  transition: transform .25s ease;
}
.aside__logo {
  height: 64px; padding: 0 20px;
  display: flex; align-items: center; justify-content: space-between;
  font-size: .9375rem; font-weight: 700; color: #60a5fa;
  border-bottom: 1px solid #1e293b; flex-shrink: 0;
}
.aside__close { cursor: pointer; color: #64748b; display: none; }
.aside__close:hover { color: #e2e8f0; }

.aside-nav { flex: 1; padding: 12px 10px; overflow-y: auto; }
.aside-footer { padding: 12px 10px; border-top: 1px solid #1e293b; }

.aside-nav__item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 9px 12px; border-radius: 8px;
  font-size: .9rem; font-weight: 500; color: #94a3b8;
  text-decoration: none; transition: all .15s;
  background: none; border: none; cursor: pointer;
  margin-bottom: 2px;
}
.aside-nav__item:hover  { background: #1e293b; color: #e2e8f0; }
.aside-nav__item.active { background: rgba(59,130,246,.12); color: #60a5fa; }
.aside-nav__item--danger:hover { background: rgba(239,68,68,.08); color: #f87171; }

.aside-mask {
  display: none;
  position: fixed; inset: 0; background: rgba(0,0,0,.5);
  z-index: 190; backdrop-filter: blur(2px);
}

/* ── 主区域 ──────────────────────────────────────────── */
.admin-body { flex: 1; margin-left: 220px; display: flex; flex-direction: column; min-width: 0; }

.admin-topbar {
  height: 56px; background: #0a1120;
  border-bottom: 1px solid #1e293b;
  display: flex; align-items: center; padding: 0 24px; gap: 16px;
  position: sticky; top: 0; z-index: 100;
}
.topbar__menu    { display: none; background: none; border: none; cursor: pointer; color: #94a3b8; padding: 4px; }
.topbar__menu:hover { color: #e2e8f0; }
.topbar__breadcrumb { flex: 1; }
.topbar__right  { display: flex; align-items: center; gap: 12px; }

.admin-main { flex: 1; padding: 28px 32px; overflow-x: hidden; }

/* ── 移动端响应式 ─────────────────────────────────────── */
@media (max-width: 768px) {
  .aside          { transform: translateX(-100%); }
  .aside.open     { transform: translateX(0); }
  .aside__close   { display: block; }
  .aside-mask     { display: block; }
  .admin-body     { margin-left: 0; }
  .topbar__menu   { display: block; }
  .admin-main     { padding: 16px; }
}
</style>
