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
          <router-link to="/">{{ $t('nav.home') }}</router-link>
          <router-link to="/articles">{{ $t('nav.articles') }}</router-link>
          <router-link to="/projects">{{ $t('nav.projects') }}</router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin" class="nav__admin">后台</router-link>
          <router-link v-else to="/login" class="nav__admin">登录</router-link>
        </nav>

        <!-- 工具栏 -->
        <div class="nav__tools">
          <SearchModal />
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>

        <!-- Mobile hamburger -->
        <button class="nav__burger" @click="menuOpen = !menuOpen" aria-label="菜单">
          <span></span><span></span><span></span>
        </button>
      </div>

      <!-- Mobile dropdown -->
      <transition name="slide-down">
        <nav v-if="menuOpen" class="nav__mobile" @click="menuOpen = false">
          <router-link to="/">{{ $t('nav.home') }}</router-link>
          <router-link to="/articles">{{ $t('nav.articles') }}</router-link>
          <router-link to="/projects">{{ $t('nav.projects') }}</router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin">后台</router-link>
          <router-link v-else to="/login">登录</router-link>
          <div class="mobile-tools">
            <ThemeSwitcher />
            <LanguageSwitcher />
          </div>
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
import SearchModal from '@/components/SearchModal.vue'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

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
  background: rgba(var(--nav-bg-rgb, 15,23,42), .9);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--c-border);
}
[data-theme="light"] .nav { background: rgba(248,250,252,.92); }

.nav__inner {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px; gap: 16px;
}
.nav__logo {
  font-size: 1.125rem; font-weight: 800;
  background: linear-gradient(135deg,#60a5fa,#a78bfa);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-decoration: none; white-space: nowrap;
}
.nav__links { display: flex; gap: 28px; align-items: center; }
.nav__links a {
  color: var(--c-text-muted); font-size: .9375rem; font-weight: 500;
  text-decoration: none; transition: color .2s;
}
.nav__links a:hover,
.nav__links a.router-link-active { color: var(--c-text); }
.nav__admin {
  padding: 5px 16px !important;
  background: rgba(59,130,246,.1);
  color: #60a5fa !important;
  border: 1px solid rgba(59,130,246,.25);
  border-radius: 7px;
}
.nav__admin:hover { background: rgba(59,130,246,.22) !important; }

/* 工具栏 */
.nav__tools { display: flex; align-items: center; gap: 10px; margin-left: auto; }

/* Hamburger */
.nav__burger {
  display: none; flex-direction: column; justify-content: center;
  gap: 5px; background: none; border: none; cursor: pointer; padding: 8px;
}
.nav__burger span {
  display: block; width: 22px; height: 2px;
  background: var(--c-text-muted); border-radius: 2px; transition: background .2s;
}
.nav__burger:hover span { background: var(--c-text); }

/* Mobile nav */
.nav__mobile {
  display: flex; flex-direction: column;
  padding: 8px 16px 16px;
  border-top: 1px solid var(--c-border);
}
.nav__mobile a {
  padding: 11px 12px; color: var(--c-text-muted); text-decoration: none;
  font-size: .9375rem; font-weight: 500; border-radius: 8px;
  transition: all .15s;
}
.nav__mobile a:hover,
.nav__mobile a.router-link-active { background: var(--c-bg-card); color: var(--c-text); }
.mobile-tools { display: flex; align-items: center; gap: 8px; padding: 10px 12px; }

.slide-down-enter-active, .slide-down-leave-active { transition: all .2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* Footer */
.pub-footer {
  border-top: 1px solid var(--c-border);
  padding: 24px 0;
  font-size: .875rem; color: var(--c-text-muted);
}
.footer-inner {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
.footer-links { display: flex; gap: 20px; }
.footer-links a { color: var(--c-text-muted); text-decoration: none; }
.footer-links a:hover { color: var(--c-text); }

@media (max-width: 768px) {
  .nav__links  { display: none; }
  .nav__burger { display: flex; }
  .nav__tools  { gap: 6px; }
  .search-trigger .search-hint { display: none; }
  .search-trigger kbd { display: none; }
}
</style>
