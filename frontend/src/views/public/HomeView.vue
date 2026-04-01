<template>
  <div>

    <!-- ══ HERO ════════════════════════════════════════════ -->
    <section class="hero">
      <!-- 背景 blobs -->
      <div class="hero-blob hero-blob--1"></div>
      <div class="hero-blob hero-blob--2"></div>
      <div class="hero-blob hero-blob--3"></div>
      <!-- 网格线装饰 -->
      <div class="hero-grid"></div>

      <div class="container hero__wrap fade-in-up">

        <!-- 头像 -->
        <div class="hero__avatar-box">
          <div class="avatar-outer-ring"></div>
          <div class="avatar-inner-ring"></div>
          <!-- 动态粒子轨道 -->
          <div class="avatar-orbit">
            <span class="orbit-dot orbit-dot--1"></span>
            <span class="orbit-dot orbit-dot--2"></span>
            <span class="orbit-dot orbit-dot--3"></span>
          </div>
          <img
            :src="profile?.avatar_url || 'https://api.dicebear.com/9.x/bottts-neutral/svg?seed=openclaw&backgroundColor=b6e3f4,c0aede,d1d4f9&backgroundType=gradientLinear'"
            alt="avatar"
            class="hero__avatar"
          />
          <!-- 在线状态 -->
          <div class="avatar-status">
            <span class="status-dot"></span>
            <span class="status-ping"></span>
          </div>
        </div>

        <!-- 信息 -->
        <div class="hero__info">
          <div class="hero__badge-wrap">
            <span class="hero__badge">
              <span class="badge-dot"></span>
              Open to Work
            </span>
          </div>

          <h1 class="hero__name">
            <span class="name-line">{{ profile?.full_name || 'Your Name' }}</span>
          </h1>

          <p class="hero__title">
            <span class="title-gradient">{{ profile?.title || 'Full Stack Engineer' }}</span>
          </p>

          <p class="hero__bio text-muted">{{ profile?.bio }}</p>

          <div class="hero__meta">
            <span v-if="profile?.location" class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="meta-icon">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              {{ profile.location }}
            </span>
            <span v-if="profile?.email_public" class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="meta-icon">
                <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              {{ profile.email_public }}
            </span>
          </div>

          <div class="hero__actions">
            <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" class="btn btn--outline">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
              </svg>
              GitHub
            </a>
            <a v-if="profile?.linkedin_url" :href="profile.linkedin_url" target="_blank" class="btn btn--outline">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
              </svg>
              LinkedIn
            </a>
            <a v-if="profile?.csdn_url" :href="profile.csdn_url" target="_blank" class="btn btn--outline btn--csdn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
              </svg>
              CSDN
            </a>
            <router-link to="/articles" class="btn btn--primary">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
              </svg>
              文章
            </router-link>
            <router-link to="/projects" class="btn btn--gradient">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/>
              </svg>
              项目
            </router-link>
          </div>

          <!-- 统计数字（装饰性） -->
          <div class="hero__stats">
            <div class="stat-item">
              <span class="stat-num">∞</span>
              <span class="stat-label">热情</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">24/7</span>
              <span class="stat-label">专注</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">100%</span>
              <span class="stat-label">全力</span>
            </div>
          </div>
        </div>

      </div>

      <!-- 向下滚动指示器 -->
      <div class="scroll-indicator">
        <div class="scroll-mouse">
          <div class="scroll-wheel"></div>
        </div>
        <span>向下滚动</span>
      </div>
    </section>

    <!-- ══ 工作经历 ══════════════════════════════════════════ -->
    <section class="section section--experience" v-if="experience.length">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">工作经历</h2>
          <div class="section-line"></div>
        </div>
        <div class="timeline">
          <div
            v-for="(exp, i) in experience"
            :key="i"
            class="timeline__item fade-in-up"
            :style="{ animationDelay: `${i * 0.1}s` }"
          >
            <div class="timeline__connector">
              <div class="timeline__dot">
                <div class="timeline__dot-inner"></div>
                <div class="timeline__dot-ping"></div>
              </div>
              <div class="timeline__line" v-if="i < experience.length - 1"></div>
            </div>
            <div class="card timeline__card">
              <div class="card-shine"></div>
              <div class="exp__head">
                <div class="exp__info">
                  <h3 class="exp__role">{{ exp.title }}</h3>
                  <p class="exp__company">
                    <span class="company-dot"></span>
                    {{ exp.company }}
                    <span class="badge" style="margin-left:8px">{{ exp.type || 'Full-time' }}</span>
                  </p>
                </div>
                <span class="exp__date">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style="opacity:.5;flex-shrink:0">
                    <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
                  </svg>
                  {{ exp.start }} — {{ exp.end || '至今' }}
                </span>
              </div>
              <p class="text-muted mt-2 exp__desc">{{ exp.description }}</p>
              <div class="tag-row mt-2" v-if="exp.skills">
                <span
                  v-for="s in exp.skills.split(',')"
                  :key="s"
                  class="skill-tag"
                >{{ s.trim() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 技能 ══════════════════════════════════════════════ -->
    <section class="section section--skills" v-if="skills.length">
      <div class="skills-bg-layer"></div>
      <div class="container" style="position:relative;z-index:1">
        <div class="section-header">
          <h2 class="section-title">技能栈</h2>
          <div class="section-line"></div>
        </div>
        <div class="skills-grid">
          <div
            v-for="(grp, i) in skills"
            :key="i"
            class="card skill-card fade-in-up"
            :style="{ animationDelay: `${i * 0.08}s` }"
          >
            <div class="card-shine"></div>
            <div class="skill-card__header">
              <div class="skill-cat-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                </svg>
              </div>
              <p class="skill-cat">{{ grp.category }}</p>
            </div>
            <div v-for="(sk, j) in grp.items" :key="j" class="skill-item">
              <div class="skill-label">
                <span class="skill-name">{{ sk.name }}</span>
                <span class="skill-pct">{{ sk.level }}%</span>
              </div>
              <div class="skill-bar">
                <div
                  class="skill-fill"
                  :style="{ width: skillsAnimated ? sk.level + '%' : '0%' }"
                  :data-level="sk.level"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 教育背景 ══════════════════════════════════════════ -->
    <section class="section" v-if="education.length">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">教育背景</h2>
          <div class="section-line"></div>
        </div>
        <div class="edu-grid">
          <div
            v-for="(edu, i) in education"
            :key="i"
            class="card edu-card fade-in-up"
            :style="{ animationDelay: `${i * 0.1}s` }"
          >
            <div class="card-shine"></div>
            <div class="edu-icon-wrap">
              <div class="edu-icon-bg"></div>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="url(#eduGrad)" class="edu-icon-svg">
                <defs>
                  <linearGradient id="eduGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#5b8dee"/>
                    <stop offset="100%" stop-color="#a78bfa"/>
                  </linearGradient>
                </defs>
                <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
              </svg>
            </div>
            <div class="edu-content">
              <h3 class="edu-school">{{ edu.school }}</h3>
              <p class="edu-degree text-muted">{{ edu.degree }} · {{ edu.major }}</p>
              <p class="edu-date text-muted">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" style="opacity:.5;vertical-align:middle;margin-right:4px">
                  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
                </svg>
                {{ edu.start }} — {{ edu.end || '至今' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 最新文章（预览） ══════════════════════════════════ -->
    <section class="section section--articles" v-if="latestArticles.length">
      <div class="articles-bg-layer"></div>
      <div class="container" style="position:relative;z-index:1">
        <div class="section-header-row">
          <div>
            <h2 class="section-title" style="margin-bottom:0">最新文章</h2>
            <div class="section-line" style="margin-top:10px"></div>
          </div>
          <router-link to="/articles" class="view-all-btn">
            查看全部
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </router-link>
        </div>
        <div class="art-grid">
          <router-link
            v-for="(a, i) in latestArticles"
            :key="a.id"
            :to="`/articles/${a.slug}`"
            class="art-card fade-in-up"
            :style="{ animationDelay: `${i * 0.1}s` }"
          >
            <div class="art-card__glow"></div>
            <div class="art-card__inner">
              <div class="art-tag-row">
                <span v-for="t in parseTags(a.tags)" :key="t" class="art-tag">{{ t }}</span>
              </div>
              <h3 class="art-title">{{ a.title }}</h3>
              <p class="art-sum text-muted">{{ a.summary }}</p>
              <div class="art-foot">
                <span class="art-date">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style="opacity:.5">
                    <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
                  </svg>
                  {{ fmtDate(a.published_at) }}
                </span>
                <span class="art-views">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style="opacity:.5">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                  </svg>
                  {{ a.view_count }}
                </span>
              </div>
            </div>
            <div class="art-card__arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
              </svg>
            </div>
          </router-link>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { profileApi, articlesApi } from '@/api/endpoints.js'
import dayjs from 'dayjs'

const profile        = ref(null)
const latestArticles = ref([])
const skillsAnimated = ref(false)

const resume      = computed(() => { try { return JSON.parse(profile.value?.resume_data || '{}') } catch { return {} } })
const experience  = computed(() => resume.value.experience  || [])
const skills      = computed(() => resume.value.skills      || [])
const education   = computed(() => resume.value.education   || [])

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY-MM-DD') : ''

function initSkillsObserver() {
  const section = document.querySelector('.section--skills')
  if (!section) return
  const io = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      skillsAnimated.value = true
      io.disconnect()
    }
  }, { threshold: 0.15 })
  io.observe(section)
}

function initScrollReveal() {
  const targets = document.querySelectorAll('.timeline-item, .edu-card, .article-preview-card')
  if (!targets.length) return
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('sr-visible')
        io.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })
  targets.forEach(el => {
    el.classList.add('sr-hidden')
    io.observe(el)
  })
}

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch {}
  try {
    const res = await articlesApi.list({ page: 1, page_size: 3 })
    latestArticles.value = res.items ?? []
  } catch {}
  await nextTick()
  initSkillsObserver()
  initScrollReveal()
})
</script>

<style scoped>
/* ══ HERO ════════════════════════════════════════════════ */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 100px 0 80px;
}

/* Blob 背景 */
.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: .55;
  pointer-events: none;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}
.hero-blob--1 {
  width: 600px; height: 600px;
  top: -150px; left: -100px;
  background: radial-gradient(circle, rgba(91,141,238,.5) 0%, transparent 70%);
  animation: blobMove1 18s infinite;
}
.hero-blob--2 {
  width: 500px; height: 500px;
  bottom: -100px; right: -50px;
  background: radial-gradient(circle, rgba(167,139,250,.45) 0%, transparent 70%);
  animation: blobMove2 22s infinite;
}
.hero-blob--3 {
  width: 350px; height: 350px;
  top: 40%; left: 40%;
  background: radial-gradient(circle, rgba(244,114,182,.3) 0%, transparent 70%);
  animation: blobMove3 15s infinite;
}

/* 网格装饰 */
.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(91,141,238,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91,141,238,.05) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
  pointer-events: none;
}

.hero__wrap {
  display: flex;
  align-items: center;
  gap: 80px;
  position: relative;
  z-index: 2;
}

/* 头像区域 */
.hero__avatar-box {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 6s ease-in-out infinite;
}
/* 流光外圈：conic-gradient 旋转 */
.avatar-outer-ring {
  position: absolute;
  inset: -18px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(91,141,238,0) 0%,
    rgba(91,141,238,.8) 20%,
    rgba(167,139,250,.8) 45%,
    rgba(244,114,182,.8) 65%,
    rgba(91,141,238,0) 100%
  );
  animation: ringRotate 4s linear infinite;
  mask-image: radial-gradient(circle, transparent 87px, black 88px);
  -webkit-mask-image: radial-gradient(circle, transparent 87px, black 88px);
}
.avatar-inner-ring {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid transparent;
  background:
    linear-gradient(var(--c-bg), var(--c-bg)) padding-box,
    linear-gradient(135deg, #5b8dee, #a78bfa, #f472b6) border-box;
  box-shadow:
    0 0 20px rgba(91,141,238,.4),
    0 0 50px rgba(167,139,250,.2),
    inset 0 0 20px rgba(91,141,238,.05);
  animation: glowPulse 3s ease-in-out infinite;
}

/* 粒子轨道 */
.avatar-orbit {
  position: absolute;
  inset: -32px;
  border-radius: 50%;
  animation: ringRotate 8s linear infinite reverse;
  pointer-events: none;
}
.orbit-dot {
  position: absolute;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}
.orbit-dot--1 {
  width: 8px; height: 8px;
  top: 50%; left: 0;
  transform: translateY(-50%);
  background: #5b8dee;
  color: #5b8dee;
  animation: orbitPulse 2s ease-in-out infinite;
}
.orbit-dot--2 {
  width: 6px; height: 6px;
  bottom: 14%; right: 8%;
  background: #a78bfa;
  color: #a78bfa;
  animation: orbitPulse 2.5s ease-in-out infinite .6s;
}
.orbit-dot--3 {
  width: 5px; height: 5px;
  top: 12%; right: 10%;
  background: #f472b6;
  color: #f472b6;
  animation: orbitPulse 2s ease-in-out infinite 1.2s;
}

.hero__avatar {
  width: 200px; height: 200px;
  border-radius: 50%;
  object-fit: cover;
  position: relative;
  z-index: 1;
  box-shadow: 0 20px 60px rgba(0,0,0,.35);
  animation: avatarGlow 4s ease-in-out infinite;
  transition: transform .3s ease !important;
}
.hero__avatar-box:hover .hero__avatar {
  transform: scale(1.05);
}
.avatar-status {
  position: absolute;
  bottom: 8px; right: 8px;
  z-index: 2;
}
.status-dot {
  display: block;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #34d399;
  border: 3px solid var(--c-bg);
}
.status-ping {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(52,211,153,.4);
  animation: dotPing 2s cubic-bezier(0,0,.2,1) infinite;
}

/* Hero 文字 */
.hero__info { flex: 1; min-width: 0; }

.hero__badge-wrap { margin-bottom: 20px; }
.hero__badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 16px;
  border-radius: 24px;
  background: rgba(52,211,153,.1);
  color: #34d399;
  border: 1px solid rgba(52,211,153,.25);
  font-size: .8125rem; font-weight: 600;
  letter-spacing: .04em;
  box-shadow: 0 0 20px rgba(52,211,153,.12);
}
.badge-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
  animation: pulse 2s ease-in-out infinite;
}

.hero__name {
  font-size: clamp(2.25rem, 5.5vw, 3.5rem);
  font-weight: 900;
  line-height: 1.08;
  color: var(--c-text);
  letter-spacing: -0.03em;
  margin-bottom: 12px;
}
.name-line {
  display: inline;
  background: linear-gradient(135deg, #e8eeff 0%, #b0c4f8 50%, #c4a8ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
[data-theme="light"] .name-line {
  background: linear-gradient(135deg, #1a2150 0%, #3b6fd4 60%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero__title {
  margin-bottom: 16px;
}
.title-gradient {
  font-size: 1.2rem;
  font-weight: 600;
  background: linear-gradient(135deg, #5b8dee, #a78bfa, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: shimmer 4s linear infinite;
}

.hero__bio {
  max-width: 520px;
  line-height: 1.8;
  font-size: .95rem;
  margin-bottom: 20px;
}

.hero__meta {
  display: flex; gap: 20px; flex-wrap: wrap;
  margin-bottom: 28px;
}
.meta-item {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: .875rem;
  color: var(--c-text-muted);
  padding: 5px 12px;
  border-radius: 8px;
  background: rgba(91,141,238,.07);
  border: 1px solid rgba(91,141,238,.12);
}
.meta-icon { color: var(--c-primary); flex-shrink: 0; }

/* 按钮 */
.hero__actions { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 32px; }

.btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 10px 22px; border-radius: 10px;
  font-size: .875rem; font-weight: 600;
  text-decoration: none; cursor: pointer; border: none;
  transition: all .25s cubic-bezier(.4,0,.2,1) !important;
  position: relative; overflow: hidden;
}
.btn--outline {
  border: 1px solid var(--c-border-bright);
  color: var(--c-text-muted);
  background: rgba(91,141,238,.05);
}
.btn--outline:hover {
  border-color: rgba(91,141,238,.5);
  color: var(--c-primary);
  background: rgba(91,141,238,.1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,238,.2);
}
.btn--primary {
  background: rgba(91,141,238,.15);
  color: var(--c-primary);
  border: 1px solid rgba(91,141,238,.3);
}
.btn--primary:hover {
  background: rgba(91,141,238,.25);
  border-color: rgba(91,141,238,.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91,141,238,.25);
}
.btn--gradient {
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  color: #fff;
  border: none;
  box-shadow: 0 4px 18px rgba(91,141,238,.35);
}
.btn--gradient::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #7aadff, #c4a8ff);
  opacity: 0;
  transition: opacity .25s !important;
}
.btn--gradient:hover::before { opacity: 1; }
.btn--gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(91,141,238,.45);
}
.btn--gradient > * { position: relative; z-index: 1; }
.btn--csdn {
  border-color: rgba(252, 100, 30, 0.35) !important;
  color: #fc641e !important;
  background: rgba(252, 100, 30, 0.06) !important;
}
.btn--csdn:hover {
  border-color: rgba(252, 100, 30, 0.6) !important;
  background: rgba(252, 100, 30, 0.14) !important;
  box-shadow: 0 6px 20px rgba(252, 100, 30, 0.2) !important;
}

/* 统计 */
.hero__stats {
  display: flex; align-items: center; gap: 0;
  padding: 14px 20px;
  border-radius: 14px;
  background: rgba(91,141,238,.06);
  border: 1px solid rgba(91,141,238,.12);
  width: fit-content;
  backdrop-filter: blur(8px);
}
.stat-item { text-align: center; padding: 0 20px; }
.stat-num {
  display: block;
  font-size: 1.2rem; font-weight: 800;
  background: var(--grad-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.stat-label { font-size: .75rem; color: var(--c-text-muted); font-weight: 500; margin-top: 2px; display: block; }
.stat-divider { width: 1px; height: 32px; background: var(--c-border); flex-shrink: 0; }

/* 滚动指示器 */
.scroll-indicator {
  position: absolute;
  bottom: 30px; left: 50%;
  transform: translateX(-50%);
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  color: var(--c-text-muted);
  font-size: .75rem;
  letter-spacing: .06em;
  animation: float 3s ease-in-out infinite;
  z-index: 2;
  opacity: .6;
}
.scroll-mouse {
  width: 22px; height: 36px;
  border: 2px solid var(--c-text-muted);
  border-radius: 11px;
  display: flex; justify-content: center; padding-top: 5px;
}
.scroll-wheel {
  width: 3px; height: 7px;
  background: var(--c-primary);
  border-radius: 2px;
  animation: fadeInUp 1.5s ease-in-out infinite;
}

/* ══ 通用 section header ══════════════════════════════════ */
.section-header { margin-bottom: 48px; }
.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 48px;
}
.section-line {
  width: 52px; height: 3px;
  background: var(--grad-primary);
  border-radius: 2px;
  margin-top: 10px;
  box-shadow: 0 0 10px var(--c-glow-blue);
}
.view-all-btn {
  display: inline-flex; align-items: center; gap: 5px;
  color: var(--c-primary);
  font-size: .875rem; font-weight: 600;
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid rgba(91,141,238,.25);
  transition: all .2s !important;
}
.view-all-btn:hover {
  background: rgba(91,141,238,.1);
  border-color: rgba(91,141,238,.4);
  transform: translateX(3px);
}

/* ══ 工作经历 Timeline ════════════════════════════════════ */
.section--experience { background: var(--c-bg); }

.timeline { display: flex; flex-direction: column; gap: 0; }
.timeline__item { display: flex; gap: 20px; align-items: flex-start; }

.timeline__connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 22px;
}
.timeline__dot {
  position: relative;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5b8dee, #a78bfa);
  box-shadow: 0 0 0 4px rgba(91,141,238,.15), 0 0 16px rgba(91,141,238,.4);
  flex-shrink: 0;
  z-index: 1;
}
.timeline__dot-inner {
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: var(--c-bg);
}
.timeline__dot-ping {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(91,141,238,.5);
  animation: dotPing 3s ease-in-out infinite;
}
.timeline__line {
  width: 2px;
  flex: 1;
  min-height: 28px;
  background: linear-gradient(to bottom, rgba(91,141,238,.4), rgba(167,139,250,.2));
  margin: 4px 0;
}

.timeline__card {
  flex: 1;
  margin-bottom: 24px;
  position: relative;
}
.card-shine {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(91,141,238,.4), transparent);
  border-radius: inherit;
}

.exp__head { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; }
.exp__info { flex: 1; }
.exp__role { font-size: 1.05rem; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.exp__company {
  display: flex; align-items: center;
  font-size: .875rem; color: var(--c-text-muted);
}
.company-dot {
  display: inline-block;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--grad-primary);
  margin-right: 8px; flex-shrink: 0;
}
.exp__date {
  display: flex; align-items: center; gap: 5px;
  font-size: .8rem; color: var(--c-text-muted);
  background: rgba(91,141,238,.07);
  border: 1px solid rgba(91,141,238,.12);
  padding: 4px 10px; border-radius: 7px;
  white-space: nowrap; flex-shrink: 0;
}
.exp__desc { font-size: .9rem; line-height: 1.7; }
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
.skill-tag {
  display: inline-block;
  padding: 3px 10px; border-radius: 6px;
  font-size: .75rem; font-weight: 600;
  background: rgba(91,141,238,.1);
  color: var(--c-primary);
  border: 1px solid rgba(91,141,238,.2);
  transition: all .2s !important;
}
.skill-tag:hover {
  background: rgba(91,141,238,.2);
  border-color: rgba(91,141,238,.4);
}

/* ══ 技能栈 ══════════════════════════════════════════════ */
.section--skills { position: relative; padding: 100px 0; }
.skills-bg-layer {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(91,141,238,.06) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 50%, rgba(167,139,250,.06) 0%, transparent 60%);
  pointer-events: none;
}
.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px,1fr)); gap: 20px; }

.skill-card { position: relative; }
.skill-card__header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 18px;
}
.skill-cat-icon {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 7px;
  background: linear-gradient(135deg, rgba(91,141,238,.2), rgba(167,139,250,.2));
  border: 1px solid rgba(91,141,238,.25);
  color: var(--c-primary);
  flex-shrink: 0;
}
.skill-cat {
  font-size: .78rem; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase;
  background: var(--grad-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.skill-item { margin-bottom: 14px; }
.skill-label {
  display: flex; justify-content: space-between;
  font-size: .875rem; margin-bottom: 7px;
  align-items: center;
}
.skill-name { font-weight: 500; color: var(--c-text); }
.skill-pct {
  font-size: .75rem; font-weight: 700;
  background: var(--grad-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.skill-bar {
  height: 6px;
  background: rgba(91,141,238,.1);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(91,141,238,.1);
}
.skill-fill {
  height: 100%;
  background: linear-gradient(90deg, #5b8dee, #a78bfa, #f472b6);
  background-size: 200% 100%;
  border-radius: 4px;
  transition: width 0.9s cubic-bezier(.4,0,.2,1);
  animation: shimmer 3s linear infinite;
  box-shadow: 0 0 8px rgba(91,141,238,.4);
}

/* ══ Scroll reveal ══════════════════════════════════════ */
.sr-hidden {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.sr-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ══ 教育背景 ══════════════════════════════════════════════ */
.edu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 20px; }
.edu-card { display: flex; align-items: flex-start; gap: 16px; position: relative; }
.edu-icon-wrap {
  position: relative; flex-shrink: 0;
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
}
.edu-icon-bg {
  position: absolute; inset: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(91,141,238,.15), rgba(167,139,250,.15));
  border: 1px solid rgba(91,141,238,.2);
}
.edu-icon-svg { position: relative; z-index: 1; }
.edu-content { flex: 1; min-width: 0; }
.edu-school { font-size: 1rem; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.edu-degree { font-size: .875rem; margin-bottom: 4px; }
.edu-date { font-size: .8rem; display: flex; align-items: center; }

/* ══ 文章预览 ══════════════════════════════════════════════ */
.section--articles { position: relative; padding: 100px 0; }
.articles-bg-layer {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 70% 30%, rgba(167,139,250,.05) 0%, transparent 55%),
    radial-gradient(ellipse at 20% 70%, rgba(244,114,182,.04) 0%, transparent 55%);
  pointer-events: none;
}

.art-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px,1fr)); gap: 22px; }

.art-card {
  position: relative;
  display: flex; flex-direction: column;
  text-decoration: none; color: inherit;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: transform var(--t), box-shadow var(--t), border-color var(--t) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.art-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.04) 0%, transparent 60%);
  pointer-events: none;
}
.art-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 20px 50px rgba(0,0,0,.4), 0 0 0 1px rgba(91,141,238,.25);
  border-color: rgba(91,141,238,.3);
}
.art-card__glow {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--grad-hero);
  opacity: 0;
  transition: opacity .3s !important;
}
.art-card:hover .art-card__glow { opacity: 1; }
.art-card__inner {
  flex: 1; display: flex; flex-direction: column; gap: 10px;
  padding: 24px;
}
.art-card__arrow {
  position: absolute;
  top: 18px; right: 18px;
  width: 28px; height: 28px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(91,141,238,.08);
  color: var(--c-primary);
  opacity: 0;
  transform: translateX(-6px);
  transition: all .25s !important;
}
.art-card:hover .art-card__arrow { opacity: 1; transform: translateX(0); }

.art-tag-row { display: flex; gap: 5px; flex-wrap: wrap; }
.art-tag {
  display: inline-block;
  padding: 2px 9px; border-radius: 6px;
  font-size: .71rem; font-weight: 600;
  background: rgba(167,139,250,.12);
  color: var(--c-accent);
  border: 1px solid rgba(167,139,250,.2);
  letter-spacing: .03em;
}
.art-title {
  font-size: 1.02rem; font-weight: 700;
  color: var(--c-text); line-height: 1.45;
}
.art-sum {
  font-size: .875rem; flex: 1;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  line-height: 1.6;
}
.art-foot {
  display: flex; justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--c-border);
  margin-top: auto;
}
.art-date, .art-views {
  display: flex; align-items: center; gap: 5px;
  font-size: .8125rem; color: var(--c-text-muted);
}

/* ══ Responsive ══════════════════════════════════════════ */
@media (max-width: 900px) {
  .hero__wrap { flex-direction: column; gap: 40px; text-align: center; padding: 40px 0 0; }
  .hero__bio { margin: 0 auto 20px; }
  .hero__actions { justify-content: center; }
  .hero__meta { justify-content: center; }
  .hero__stats { margin: 0 auto; }
  .hero__avatar-box { animation: none; }
  .scroll-indicator { display: none; }
  .hero-blob--1 { width: 350px; height: 350px; }
  .hero-blob--2 { width: 300px; height: 300px; }
  .hero-blob--3 { display: none; }
}

@media (max-width: 600px) {
  .hero { padding: 90px 0 60px; min-height: auto; }
  .hero__avatar { width: 150px; height: 150px; }
  .hero__name { font-size: 2rem; }
  .hero__stats { flex-wrap: wrap; gap: 12px; padding: 12px 16px; }
  .stat-divider { display: none; }
  .section-header-row { flex-direction: column; align-items: flex-start; gap: 12px; }
  .timeline__item { gap: 12px; }
  .timeline__connector { display: none; }
}
</style>
