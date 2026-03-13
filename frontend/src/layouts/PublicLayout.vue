<template>
  <div class="pub-layout">

    <!-- ── 顶部导航 ──────────────────────────────────── -->
    <header class="nav">
      <div class="container nav__inner">

        <router-link to="/" class="nav__logo">
          <span v-if="profile?.full_name">{{ profile.full_name }}</span>
          <span v-else>Portfolio</span>
        </router-link>

        <!-- Desktop links -->
        <nav class="nav__links">
          <router-link to="/">首页</router-link>
          <router-link to="/articles">文章</router-link>
          <router-link to="/projects">项目</router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin" class="nav__admin">后台</router-link>
          <router-link v-else to="/login" class="nav__admin">登录</router-link>
        </nav>

        <!-- Mobile hamburger -->
        <button class="nav__burger" @click="menuOpen = !menuOpen" aria-label="菜单">
          <span></span><span></span><span></span>
        </button>
      </div>

      <!-- Mobile dropdown -->
      <transition name="slide-down">
        <nav v-if="menuOpen" class="nav__mobile" @click="menuOpen = false">
          <router-link to="/">首页</router-link>
          <router-link to="/articles">文章</router-link>
          <router-link to="/projects">项目</router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin">后台</router-link>
          <router-link v-else to="/login">登录</router-link>
        </nav>
      </transition>
    </header>

    <!-- ── 主内容 ─────────────────────────────────────── -->
    <main class="pub-main">
      <router-view />
    </main>

    <!-- ── 页脚 ───────────────────────────────────────── -->
    <footer class="pub-footer">
      <div class="container footer-inner">
        <span>© {{ year }}<span v-if="profile?.full_name"> · {{ profile.full_name }}</span></span>
        <span class="footer-links">
          <a v-if="profile?.github_url"   :href="profile.github_url"   target="_blank">GitHub</a>
          <a v-if="profile?.linkedin_url" :href="profile.linkedin_url" target="_blank">LinkedIn</a>
          <a v-if="profile?.website_url"  :href="profile.website_url"  target="_blank">网站</a>
        </span>
        <span>Built with ❤️ &amp; Vue 3</span>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { profileApi } from '@/api/endpoints.js'
import { useAuthStore } from '@/store/auth.js'

const auth     = useAuthStore()
const profile  = ref(null)
const menuOpen = ref(false)
const year     = computed(() => new Date().getFullYear())

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch {}
})
</script>

<style scoped>
.pub-layout { min-height: 100vh; display: flex; flex-direction: column; }
.pub-main   { flex: 1; }

/* Nav */
.nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(15,23,42,.9);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid #1e293b;
}
.nav__inner {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
}
.nav__logo {
  font-size: 1.125rem; font-weight: 800;
  background: linear-gradient(135deg,#60a5fa,#a78bfa);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-decoration: none; white-space: nowrap;
}
.nav__links { display: flex; gap: 28px; align-items: center; }
.nav__links a {
  color: #94a3b8; font-size: .9375rem; font-weight: 500;
  text-decoration: none; transition: color .2s;
}
.nav__links a:hover,
.nav__links a.router-link-active { color: #e2e8f0; }
.nav__admin {
  padding: 5px 16px !important;
  background: rgba(59,130,246,.1);
  color: #60a5fa !important;
  border: 1px solid rgba(59,130,246,.25);
  border-radius: 7px;
}
.nav__admin:hover { background: rgba(59,130,246,.22) !important; }

/* Hamburger */
.nav__burger {
  display: none; flex-direction: column; justify-content: center;
  gap: 5px; background: none; border: none; cursor: pointer; padding: 8px;
}
.nav__burger span {
  display: block; width: 22px; height: 2px;
  background: #94a3b8; border-radius: 2px; transition: background .2s;
}
.nav__burger:hover span { background: #e2e8f0; }

/* Mobile nav */
.nav__mobile {
  display: flex; flex-direction: column;
  padding: 8px 16px 16px;
  border-top: 1px solid #1e293b;
}
.nav__mobile a {
  padding: 11px 12px; color: #94a3b8; text-decoration: none;
  font-size: .9375rem; font-weight: 500; border-radius: 8px;
  transition: all .15s;
}
.nav__mobile a:hover,
.nav__mobile a.router-link-active { background: #1e293b; color: #e2e8f0; }

.slide-down-enter-active, .slide-down-leave-active { transition: all .2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* Footer */
.pub-footer {
  border-top: 1px solid #1e293b;
  padding: 24px 0;
  font-size: .875rem; color: #475569;
}
.footer-inner {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
.footer-links { display: flex; gap: 20px; }
.footer-links a { color: #64748b; text-decoration: none; }
.footer-links a:hover { color: #94a3b8; }

@media (max-width: 640px) {
  .nav__links  { display: none; }
  .nav__burger { display: flex; }
}
</style>
