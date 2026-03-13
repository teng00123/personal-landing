<template>
  <el-container style="min-height:100vh">

    <!-- ── 侧边栏 ────────────────────────────── -->
    <el-aside width="220px" class="aside">
      <div class="aside__logo">⚡ 后台管理</div>

      <el-menu
        :router="true"
        :default-active="route.path"
        background-color="#0f172a"
        text-color="#94a3b8"
        active-text-color="#60a5fa"
        style="border:none"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>概览
        </el-menu-item>
        <el-menu-item index="/admin/profile">
          <el-icon><User /></el-icon>个人资料
        </el-menu-item>
        <el-menu-item index="/admin/articles">
          <el-icon><Document /></el-icon>文章管理
        </el-menu-item>
        <el-menu-item index="/admin/projects">
          <el-icon><Monitor /></el-icon>项目管理
        </el-menu-item>

        <el-divider style="border-color:#1e293b;margin:8px 0" />

        <el-menu-item @click="router.push('/')">
          <el-icon><House /></el-icon>查看主页
        </el-menu-item>
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>退出登录
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- ── 主区域 ─────────────────────────────── -->
    <el-main class="admin-main">
      <router-view />
    </el-main>

  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth.js'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.aside {
  background: #0f172a;
  border-right: 1px solid #1e293b;
  position: fixed; height: 100vh;
  overflow-y: auto;
}
.aside__logo {
  height: 64px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 700; color: #60a5fa;
  border-bottom: 1px solid #1e293b;
  letter-spacing: .05em;
}
.admin-main {
  margin-left: 220px;
  min-height: 100vh;
  background: #0f172a;
  padding: 32px;
}
</style>
