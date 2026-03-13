<template>
  <div class="pub-layout">

    <!-- ── 顶部导航 ──────────────────────────── -->
    <header class="nav">
      <div class="container nav__inner">
        <!-- Logo -->
        <router-link to="/" class="nav__logo">
          <span v-if="profile">{{ profile.full_name }}</span>
          <span v-else>Portfolio</span>
        </router-link>

        <!-- Links -->
        <nav class="nav__links">
          <router-link to="/">首页</router-link>
          <router-link to="/articles">文章</router-link>
          <router-link to="/projects">项目</router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin" class="nav__admin">
            后台
          </router-link>
          <router-link v-else to="/login" class="nav__admin">
            登录
          </router-link>
        </nav>
      </div>
    </header>

    <!-- ── 主内容 ─────────────────────────────── -->
    <main class="pub-main">
      <router-view />
    </main>

    <!-- ── 页脚 ───────────────────────────────── -->
    <footer class="pub-footer">
      <div class="container">
        © {{ year }}
        <span v-if="profile"> · {{ profile.full_name }}</span>
        · Built with ❤️ &amp; Vue 3
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { profileApi } from '@/api/endpoints.js'
import { useAuthStore } from '@/store/auth.js'

const auth    = useAuthStore()
const profile = ref(null)
const year    = computed(() => new Date().getFullYear())

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch { /* ignore */ }
})
</script>

<style scoped>
.pub-layout { min-height: 100vh; display: flex; flex-direction: column; }
.pub-main   { flex: 1; }

/* Nav */
.nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(15,23,42,.88);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid #1e293b;
}
.nav__inner {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
}
.nav__logo {
  font-size: 1.15rem; font-weight: 800;
  background: linear-gradient(135deg,#60a5fa,#a78bfa);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-decoration: none;
}
.nav__links { display: flex; gap: 28px; align-items: center; }
.nav__links a {
  color: #94a3b8; font-size: .9375rem; font-weight: 500;
  text-decoration: none; transition: color .2s;
}
.nav__links a:hover,
.nav__links a.router-link-active { color: #e2e8f0; }
.nav__admin {
  padding: 6px 16px;
  background: rgba(59,130,246,.12);
  color: #60a5fa !important;
  border: 1px solid rgba(59,130,246,.28);
  border-radius: 8px;
}
.nav__admin:hover { background: rgba(59,130,246,.25) !important; }

/* Footer */
.pub-footer {
  border-top: 1px solid #1e293b;
  padding: 20px 0; text-align: center;
  font-size: .875rem; color: #475569;
}
</style>
