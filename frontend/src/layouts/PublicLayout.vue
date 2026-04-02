<template>
  <div class="pub-layout">

    <!-- ── 顶部导航 ──────────────────────────────────── -->
    <header class="nav" :class="{ 'nav--scrolled': scrolled }">
      <div class="container nav__inner">

        <router-link to="/" class="nav__logo">
          <span class="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#logoGrad)"/>
              <path d="M2 17l10 5 10-5" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round"/>
              <path d="M2 12l10 5 10-5" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" opacity=".6"/>
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#5b8dee"/>
                  <stop offset="100%" stop-color="#a78bfa"/>
                </linearGradient>
              </defs>
            </svg>
          </span>
          <span class="logo-text">
            <span v-if="profile?.full_name">{{ profile.full_name }}</span>
            <span v-else>Portfolio</span>
          </span>
        </router-link>

        <!-- Desktop links -->
        <nav class="nav__links">
          <router-link to="/" class="nav__link">
            <span>{{ $t('nav.home') }}</span>
          </router-link>
          <router-link to="/articles" class="nav__link">
            <span>{{ $t('nav.articles') }}</span>
          </router-link>
          <router-link to="/projects" class="nav__link">
            <span>{{ $t('nav.projects') }}</span>
          </router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin" class="nav__admin-btn">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="opacity:.8">
              <path d="M12 2a5 5 0 1 0 0 10A5 5 0 0 0 12 2zm0 12c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z"/>
            </svg>
            后台
          </router-link>
          <router-link v-else to="/login" class="nav__admin-btn">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="opacity:.8">
              <path d="M11 7L9.6 8.4l2.6 2.6H2v2h10.2l-2.6 2.6L11 17l5-5-5-5zm9 12h-8v2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-8v2h8v14z"/>
            </svg>
            登录
          </router-link>
        </nav>

        <!-- 工具栏 -->
        <div class="nav__tools">
          <SearchModal />
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>

        <!-- Mobile hamburger -->
        <button
          class="nav__burger"
          @click="menuOpen = !menuOpen"
          :class="{ 'nav__burger--open': menuOpen }"
          aria-label="菜单"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <!-- Mobile dropdown -->
      <transition name="slide-down">
        <nav v-if="menuOpen" class="nav__mobile" @click="menuOpen = false">
          <router-link to="/" class="nav__mobile-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".7"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            {{ $t('nav.home') }}
          </router-link>
          <router-link to="/articles" class="nav__mobile-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".7"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            {{ $t('nav.articles') }}
          </router-link>
          <router-link to="/projects" class="nav__mobile-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".7"><path d="M20 6h-2.18c.07-.44.18-.88.18-1.36 0-2.55-2.08-4.64-4.64-4.64-1.37 0-2.58.58-3.44 1.51L9 3.5 8.08 2.51C7.22 1.58 6.01 1 4.64 1 2.09 1 0 3.09 0 5.64c0 .48.11.92.18 1.36H0v2h20V6z"/></svg>
            {{ $t('nav.projects') }}
          </router-link>
          <router-link v-if="auth.isLoggedIn" to="/admin" class="nav__mobile-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".7"><path d="M12 2a5 5 0 1 0 0 10A5 5 0 0 0 12 2zm0 12c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z"/></svg>
            后台
          </router-link>
          <router-link v-else to="/login" class="nav__mobile-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".7"><path d="M11 7L9.6 8.4l2.6 2.6H2v2h10.2l-2.6 2.6L11 17l5-5-5-5zm9 12h-8v2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-8v2h8v14z"/></svg>
            登录
          </router-link>
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

    <!-- ── AI 助手悬浮入口 ──────────────────────────── -->
    <!-- 悬浮按钮 -->
    <transition name="fab-pop">
      <div class="ai-fab-wrap">
        <!-- Tooltip 气泡 -->
        <transition name="tooltip-fade">
          <div class="ai-tooltip" v-if="showTooltip">
            <span>🤖 AI 助手已就绪，点击了解更多！</span>
            <button class="tooltip-close" @click.stop="dismissTooltip">✕</button>
          </div>
        </transition>
        <button class="ai-fab" @click="openAI" aria-label="打开 AI 助手引导">
          <span class="ai-fab-glow"></span>
          <svg class="ai-fab-icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
            <circle cx="9" cy="14" r="1" fill="currentColor" stroke="none"/>
            <circle cx="15" cy="14" r="1" fill="currentColor" stroke="none"/>
          </svg>
          <span class="ai-fab-label">AI 助手</span>
          <span class="ai-fab-dot" v-if="showTooltip"></span>
        </button>
      </div>
    </transition>

    <!-- AI 助手引导弹窗 -->
    <transition name="modal-fade">
      <div class="ai-modal-overlay" v-if="aiOpen" @click.self="aiOpen = false">
        <transition name="modal-pop">
          <div class="ai-modal" v-if="aiOpen">
            <button class="ai-modal-close" @click="aiOpen = false">✕</button>

            <!-- 头部 -->
            <div class="ai-modal-header">
              <div class="ai-modal-avatar">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
                  <circle cx="9" cy="14" r="1" fill="white" stroke="none"/>
                  <circle cx="15" cy="14" r="1" fill="white" stroke="none"/>
                </svg>
              </div>
              <div>
                <h2 class="ai-modal-title">✨ AI 助手</h2>
                <p class="ai-modal-subtitle">你的智能写作伙伴，随时待命</p>
              </div>
            </div>

            <!-- 功能列表 -->
            <div class="ai-modal-features">
              <div class="ai-feature-item">
                <span class="ai-feature-icon">📝</span>
                <div>
                  <strong>文章生成</strong>
                  <p>输入主题，一键生成高质量文章草稿</p>
                </div>
              </div>
              <div class="ai-feature-item">
                <span class="ai-feature-icon">🔧</span>
                <div>
                  <strong>内容优化</strong>
                  <p>润色文字，提升清晰度与可读性</p>
                </div>
              </div>
              <div class="ai-feature-item">
                <span class="ai-feature-icon">✅</span>
                <div>
                  <strong>语法检查</strong>
                  <p>智能检测语法问题，给出修改建议</p>
                </div>
              </div>
              <div class="ai-feature-item">
                <span class="ai-feature-icon">🔍</span>
                <div>
                  <strong>内容分析</strong>
                  <p>自动提取关键词、摘要与情感倾向</p>
                </div>
              </div>
            </div>

            <!-- CTA -->
            <div class="ai-modal-actions">
              <router-link to="/login" class="ai-modal-btn-primary" @click="aiOpen = false">
                立即使用 AI 助手 →
              </router-link>
              <button class="ai-modal-btn-secondary" @click="aiOpen = false">稍后再说</button>
            </div>
          </div>
        </transition>
      </div>
    </transition>

    <!-- ── 页脚 ───────────────────────────────────────── -->
    <footer class="pub-footer">
      <div class="footer-glow"></div>
      <div class="container footer-inner">
        <div class="footer-brand">
          <div class="footer-logo">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#footerGrad)"/>
              <path d="M2 17l10 5 10-5" stroke="url(#footerGrad)" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="footerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#5b8dee"/>
                  <stop offset="100%" stop-color="#a78bfa"/>
                </linearGradient>
              </defs>
            </svg>
            <span v-if="profile?.full_name">{{ profile.full_name }}</span>
            <span v-else>Portfolio</span>
          </div>
          <p class="footer-copy">© {{ year }} · Built with ❤️ &amp; Vue 3</p>
        </div>

        <div class="footer-social">
          <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" class="social-link" aria-label="GitHub">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
            </svg>
            GitHub
          </a>
          <a v-if="profile?.linkedin_url" :href="profile.linkedin_url" target="_blank" class="social-link" aria-label="LinkedIn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
            </svg>
            LinkedIn
          </a>
          <a v-if="profile?.website_url" :href="profile.website_url" target="_blank" class="social-link" aria-label="网站">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16.36 14c.08-.66.14-1.32.14-2 0-.68-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2m-5.15 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56M14.34 14H9.66c-.1-.66-.16-1.32-.16-2 0-.68.06-1.35.16-2h4.68c.09.65.16 1.32.16 2 0 .68-.07 1.34-.16 2M12 19.96c-.83-1.2-1.5-2.53-1.91-3.96h3.82c-.41 1.43-1.08 2.76-1.91 3.96M8 8H5.08A7.923 7.923 0 0 1 9.4 4.44C8.8 5.55 8.35 6.75 8 8m-2.92 8H8c.35 1.25.8 2.45 1.4 3.56A8.008 8.008 0 0 1 5.08 16m-.82-2C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2 0 .68.06 1.34.14 2M12 4.03c.83 1.2 1.5 2.54 1.91 3.97h-3.82c.41-1.43 1.08-2.77 1.91-3.97M18.92 8h-2.95a15.65 15.65 0 0 0-1.38-3.56c1.84.63 3.37 1.9 4.33 3.56M12 2C6.47 2 2 6.5 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2z"/>
            </svg>
            网站
          </a>
        </div>
      </div>
    </footer>

    <!-- 访客 AI 对话浮窗 -->
    <VisitorChat />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { profileApi } from '@/api/endpoints.js'
import { useAuthStore } from '@/store/auth.js'
import SearchModal from '@/components/SearchModal.vue'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const auth     = useAuthStore()
const profile  = ref(null)
const menuOpen = ref(false)
const scrolled = ref(false)
const year     = computed(() => new Date().getFullYear())

// AI 助手状态
const aiOpen       = ref(false)
const showTooltip  = ref(false)
const TOOLTIP_KEY  = 'ai_tooltip_dismissed'

function openAI() {
  aiOpen.value = true
  showTooltip.value = false
}

function dismissTooltip() {
  showTooltip.value = false
  localStorage.setItem(TOOLTIP_KEY, '1')
}

const handleScroll = () => { scrolled.value = window.scrollY > 20 }

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch {}
  window.addEventListener('scroll', handleScroll, { passive: true })

  // 首次访问或未永久关闭时，延迟 2s 展示 tooltip
  if (!localStorage.getItem(TOOLTIP_KEY)) {
    setTimeout(() => { showTooltip.value = true }, 2000)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.pub-layout { min-height: 100vh; display: flex; flex-direction: column; }
.pub-main   { flex: 1; }

/* ── Nav ────────────────────────────────────────────────── */
.nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(6, 11, 24, 0.55);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border-bottom: 1px solid rgba(99, 130, 200, 0.1);
  transition: background .3s ease, box-shadow .3s ease, border-color .3s ease !important;
}
.nav--scrolled {
  background: rgba(6, 11, 24, 0.82) !important;
  border-bottom-color: rgba(99, 130, 200, 0.2) !important;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}
[data-theme="light"] .nav {
  background: rgba(240, 244, 255, 0.72) !important;
  border-bottom-color: rgba(100, 130, 220, 0.15) !important;
}
[data-theme="light"] .nav--scrolled {
  background: rgba(240, 244, 255, 0.92) !important;
  box-shadow: 0 4px 30px rgba(60, 80, 180, 0.1);
}

.nav__inner {
  display: flex; align-items: center; justify-content: space-between;
  height: 68px; gap: 16px;
}

/* Logo */
.nav__logo {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none; white-space: nowrap; flex-shrink: 0;
}
.logo-icon {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, rgba(91,141,238,.18), rgba(167,139,250,.18));
  border: 1px solid rgba(91,141,238,.3);
  transition: all .3s ease !important;
}
.nav__logo:hover .logo-icon {
  background: linear-gradient(135deg, rgba(91,141,238,.28), rgba(167,139,250,.28));
  box-shadow: 0 0 16px rgba(91,141,238,.3);
}
.logo-text {
  font-size: 1.05rem; font-weight: 800;
  background: linear-gradient(135deg, #7aadff, #c4a8ff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Nav links */
.nav__links {
  display: flex; gap: 4px; align-items: center;
}
.nav__link {
  position: relative; padding: 6px 14px;
  color: var(--c-text-muted); font-size: .9375rem; font-weight: 500;
  text-decoration: none; border-radius: 8px;
  transition: color .2s, background .2s !important;
}
.nav__link:hover,
.nav__link.router-link-active {
  color: var(--c-text);
  background: rgba(91, 141, 238, 0.1);
}
.nav__link::after {
  content: '';
  position: absolute; bottom: 3px; left: 50%; right: 50%;
  height: 2px;
  background: var(--grad-primary);
  border-radius: 2px;
  transition: left .25s ease, right .25s ease !important;
}
.nav__link.router-link-active::after,
.nav__link:hover::after {
  left: 18%; right: 18%;
}

.nav__admin-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 16px;
  background: rgba(91,141,238,.1);
  color: var(--c-primary) !important;
  border: 1px solid rgba(91,141,238,.25);
  border-radius: 9px;
  font-size: .875rem; font-weight: 600;
  text-decoration: none;
  transition: all .2s ease !important;
}
.nav__admin-btn:hover {
  background: rgba(91,141,238,.2) !important;
  border-color: rgba(91,141,238,.45) !important;
  box-shadow: 0 0 14px rgba(91,141,238,.2);
  transform: translateY(-1px);
}

/* 工具栏 */
.nav__tools { display: flex; align-items: center; gap: 8px; margin-left: auto; }

/* Hamburger */
.nav__burger {
  display: none; flex-direction: column; justify-content: center;
  gap: 5px; background: none; border: none; cursor: pointer;
  padding: 8px; border-radius: 8px;
  transition: background .2s !important;
}
.nav__burger:hover { background: rgba(91,141,238,.1); }
.nav__burger span {
  display: block; width: 22px; height: 2px;
  background: var(--c-text-muted); border-radius: 2px;
  transition: all .3s cubic-bezier(.4,0,.2,1) !important;
  transform-origin: center;
}
.nav__burger--open span:nth-child(1) { transform: translateY(7px) rotate(45deg); background: var(--c-primary); }
.nav__burger--open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
.nav__burger--open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); background: var(--c-primary); }

/* Mobile nav */
.nav__mobile {
  display: flex; flex-direction: column; gap: 2px;
  padding: 10px 14px 16px;
  border-top: 1px solid rgba(99, 130, 200, 0.15);
  background: rgba(6, 11, 24, 0.92);
  backdrop-filter: blur(20px);
}
[data-theme="light"] .nav__mobile {
  background: rgba(240, 244, 255, 0.96) !important;
}
.nav__mobile-link {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; color: var(--c-text-muted); text-decoration: none;
  font-size: .9375rem; font-weight: 500; border-radius: 10px;
  transition: all .18s !important;
}
.nav__mobile-link:hover,
.nav__mobile-link.router-link-active {
  background: rgba(91, 141, 238, 0.12);
  color: var(--c-text);
}
.mobile-tools {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px 4px;
  margin-top: 4px;
  border-top: 1px solid rgba(99, 130, 200, 0.1);
}

.slide-down-enter-active, .slide-down-leave-active { transition: all .25s cubic-bezier(.4,0,.2,1) !important; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }

/* ── Footer ─────────────────────────────────────────────── */
.pub-footer {
  position: relative;
  border-top: 1px solid rgba(99, 130, 200, 0.12);
  padding: 32px 0;
  background: rgba(6, 11, 24, 0.6);
  backdrop-filter: blur(10px);
  overflow: hidden;
}
[data-theme="light"] .pub-footer {
  background: rgba(240, 244, 255, 0.7) !important;
}
.footer-glow {
  position: absolute;
  top: -60px; left: 50%; transform: translateX(-50%);
  width: 600px; height: 120px;
  background: radial-gradient(ellipse, rgba(91,141,238,.08) 0%, transparent 70%);
  pointer-events: none;
}
.footer-inner {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 20px;
}
.footer-brand { display: flex; flex-direction: column; gap: 4px; }
.footer-logo {
  display: flex; align-items: center; gap: 8px;
  font-size: .95rem; font-weight: 700;
  background: linear-gradient(135deg, #7aadff, #c4a8ff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.footer-copy { font-size: .8125rem; color: var(--c-text-muted); }

.footer-social { display: flex; gap: 10px; flex-wrap: wrap; }
.social-link {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 14px;
  border-radius: 10px;
  border: 1px solid var(--c-border);
  color: var(--c-text-muted);
  font-size: .8125rem; font-weight: 500;
  text-decoration: none;
  transition: all .22s ease !important;
}
.social-link:hover {
  color: var(--c-primary);
  border-color: rgba(91,141,238,.35);
  background: rgba(91,141,238,.08);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(91,141,238,.15);
}

@media (max-width: 768px) {
  .nav__links  { display: none; }
  .nav__burger { display: flex; }
  .nav__tools  { gap: 4px; }
  .footer-inner { flex-direction: column; align-items: flex-start; gap: 16px; }
}

/* ── AI 悬浮入口 ──────────────────────────────────────── */
.ai-fab-wrap {
  position: fixed;
  bottom: 32px;
  right: 28px;
  z-index: 200;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.ai-fab {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 22px 14px 18px;
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  color: #fff;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: .9375rem;
  font-weight: 700;
  box-shadow: 0 6px 24px rgba(91, 141, 238, 0.5), 0 2px 8px rgba(0,0,0,.15);
  transition: transform .2s ease, box-shadow .2s ease;
  white-space: nowrap;
  letter-spacing: .02em;
}
.ai-fab:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 12px 36px rgba(91, 141, 238, 0.6), 0 4px 12px rgba(0,0,0,.2);
}

/* 光晕动画 */
.ai-fab-glow {
  position: absolute;
  inset: -2px;
  border-radius: 50px;
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  opacity: .4;
  filter: blur(10px);
  animation: glow-pulse 2.5s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}
@keyframes glow-pulse {
  0%, 100% { opacity: .3; transform: scale(1); }
  50%       { opacity: .6; transform: scale(1.06); }
}

.ai-fab-icon { flex-shrink: 0; }
.ai-fab-label { letter-spacing: .04em; }

/* 红点提示 */
.ai-fab-dot {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 9px;
  height: 9px;
  background: #ff4d4f;
  border-radius: 50%;
  border: 2px solid #fff;
  animation: dot-pulse 1.8s ease-in-out infinite;
}
@keyframes dot-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.35); opacity: .7; }
}

/* Tooltip 气泡 */
.ai-tooltip {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--bg-secondary, #1a2035);
  border: 1px solid rgba(91, 141, 238, 0.3);
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
  font-size: .8125rem;
  color: var(--c-text, #e0e6f0);
  max-width: 240px;
  line-height: 1.45;
}
[data-theme="light"] .ai-tooltip {
  background: #fff;
  border-color: rgba(91, 141, 238, 0.25);
  color: #1a2035;
  box-shadow: 0 6px 24px rgba(60, 80, 180, 0.12);
}
.ai-tooltip::after {
  content: '';
  position: absolute;
  bottom: -7px;
  right: 24px;
  width: 12px;
  height: 12px;
  background: var(--bg-secondary, #1a2035);
  border-right: 1px solid rgba(91, 141, 238, 0.3);
  border-bottom: 1px solid rgba(91, 141, 238, 0.3);
  transform: rotate(45deg);
}
[data-theme="light"] .ai-tooltip::after { background: #fff; }
.tooltip-close {
  background: none; border: none;
  color: var(--c-text-muted, #8899b0);
  cursor: pointer; font-size: 12px;
  padding: 0; flex-shrink: 0; line-height: 1;
  transition: color .15s;
}
.tooltip-close:hover { color: var(--c-text, #e0e6f0); }

/* ── AI 引导弹窗 ──────────────────────────────────────── */
.ai-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ai-modal {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: var(--bg-secondary, #151d30);
  border: 1px solid rgba(91, 141, 238, 0.25);
  border-radius: 20px;
  padding: 32px 28px 28px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,.04);
  overflow: hidden;
}
[data-theme="light"] .ai-modal {
  background: #fff;
  border-color: rgba(91, 141, 238, 0.2);
  box-shadow: 0 24px 64px rgba(60, 80, 180, 0.15);
}
.ai-modal::before {
  content: '';
  position: absolute;
  top: -60px; left: 50%; transform: translateX(-50%);
  width: 300px; height: 160px;
  background: radial-gradient(ellipse, rgba(91,141,238,.18) 0%, transparent 70%);
  pointer-events: none;
}

.ai-modal-close {
  position: absolute;
  top: 14px; right: 16px;
  background: none; border: none;
  color: var(--c-text-muted, #8899b0);
  cursor: pointer; font-size: 16px;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
  transition: background .15s, color .15s;
}
.ai-modal-close:hover {
  background: rgba(91,141,238,.1);
  color: var(--c-text, #e0e6f0);
}

.ai-modal-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.ai-modal-avatar {
  flex-shrink: 0;
  width: 60px; height: 60px;
  border-radius: 16px;
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(91,141,238,.4);
}
.ai-modal-title {
  font-size: 1.3rem;
  font-weight: 800;
  margin: 0 0 4px;
  background: linear-gradient(135deg, #7aadff, #c4a8ff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.ai-modal-subtitle {
  font-size: .875rem;
  color: var(--c-text-muted, #8899b0);
  margin: 0;
}

.ai-modal-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 28px;
}
.ai-feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 12px 14px;
  background: rgba(91, 141, 238, 0.06);
  border: 1px solid rgba(91, 141, 238, 0.12);
  border-radius: 12px;
  transition: background .2s;
}
.ai-feature-item:hover { background: rgba(91, 141, 238, 0.1); }
[data-theme="light"] .ai-feature-item {
  background: rgba(91, 141, 238, 0.05);
  border-color: rgba(91, 141, 238, 0.15);
}
.ai-feature-icon { font-size: 1.25rem; flex-shrink: 0; margin-top: 1px; }
.ai-feature-item strong {
  display: block;
  font-size: .9rem; font-weight: 700;
  color: var(--c-text, #e0e6f0);
  margin-bottom: 3px;
}
[data-theme="light"] .ai-feature-item strong { color: #1a2035; }
.ai-feature-item p {
  margin: 0;
  font-size: .8125rem;
  color: var(--c-text-muted, #8899b0);
  line-height: 1.5;
}

.ai-modal-actions { display: flex; gap: 10px; }
.ai-modal-btn-primary {
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  color: #fff;
  border-radius: 12px;
  font-size: .9rem; font-weight: 700;
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(91,141,238,.4);
  transition: transform .2s, box-shadow .2s;
}
.ai-modal-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(91,141,238,.5);
}
.ai-modal-btn-secondary {
  padding: 12px 18px;
  background: none;
  border: 1px solid var(--c-border, rgba(99,130,200,.2));
  color: var(--c-text-muted, #8899b0);
  border-radius: 12px;
  font-size: .875rem;
  cursor: pointer;
  transition: background .2s, color .2s, border-color .2s;
  white-space: nowrap;
}
.ai-modal-btn-secondary:hover {
  background: rgba(91,141,238,.08);
  color: var(--c-text, #e0e6f0);
  border-color: rgba(91,141,238,.3);
}

/* ── 动画 ────────────────────────────────────────────── */
.fab-pop-enter-active    { transition: all .35s cubic-bezier(.34,1.56,.64,1); }
.fab-pop-leave-active    { transition: all .2s ease; }
.fab-pop-enter-from,
.fab-pop-leave-to        { opacity: 0; transform: scale(.7) translateY(16px); }

.tooltip-fade-enter-active { transition: all .25s ease; }
.tooltip-fade-leave-active { transition: all .18s ease; }
.tooltip-fade-enter-from,
.tooltip-fade-leave-to     { opacity: 0; transform: translateY(8px); }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity .25s ease; }
.modal-fade-enter-from, .modal-fade-leave-to       { opacity: 0; }

.modal-pop-enter-active { transition: all .35s cubic-bezier(.34,1.56,.64,1); }
.modal-pop-leave-active { transition: all .2s ease; }
.modal-pop-enter-from,
.modal-pop-leave-to     { opacity: 0; transform: scale(.88) translateY(24px); }

@media (max-width: 480px) {
  .ai-fab-wrap { right: 16px; bottom: 20px; }
  .ai-fab-label { display: none; }
  .ai-fab { padding: 14px; border-radius: 50%; }
  .ai-modal { padding: 24px 18px 20px; }
  .ai-modal-actions { flex-direction: column; }
}
</style>
