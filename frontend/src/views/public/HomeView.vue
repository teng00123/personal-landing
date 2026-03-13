<template>
  <div>

    <!-- ══ HERO ════════════════════════════════════════════ -->
    <section class="hero">
      <div class="container hero__wrap fade-in-up">

        <!-- 头像 -->
        <div class="hero__avatar-box">
          <img
            :src="profile?.avatar_url || 'https://api.dicebear.com/8.x/bottts/svg?seed=portfolio'"
            alt="avatar"
            class="hero__avatar"
          />
          <div class="hero__avatar-ring"></div>
        </div>

        <!-- 信息 -->
        <div class="hero__info">
          <span class="hero__badge">✅ Open to Work</span>
          <h1 class="hero__name">{{ profile?.full_name || 'Your Name' }}</h1>
          <p class="hero__title">{{ profile?.title || 'Full Stack Engineer' }}</p>
          <p class="hero__bio text-muted">{{ profile?.bio }}</p>

          <div class="hero__meta">
            <span v-if="profile?.location">📍 {{ profile.location }}</span>
            <span v-if="profile?.email_public">✉️ {{ profile.email_public }}</span>
          </div>

          <div class="hero__actions">
            <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" class="btn btn--ghost">
              GitHub ↗
            </a>
            <a v-if="profile?.linkedin_url" :href="profile.linkedin_url" target="_blank" class="btn btn--ghost">
              LinkedIn ↗
            </a>
            <router-link to="/articles" class="btn btn--primary">文章</router-link>
            <router-link to="/projects" class="btn btn--primary">项目</router-link>
          </div>
        </div>

      </div>
    </section>

    <!-- ══ 工作经历 ══════════════════════════════════════════ -->
    <section class="section" v-if="experience.length">
      <div class="container">
        <h2 class="section-title">工作经历</h2>
        <div class="timeline">
          <div
            v-for="(exp, i) in experience"
            :key="i"
            class="timeline__item fade-in-up"
            :style="{ animationDelay: `${i * 0.08}s` }"
          >
            <div class="timeline__dot"></div>
            <div class="card timeline__card">
              <div class="exp__head">
                <div>
                  <h3 class="exp__role">{{ exp.title }}</h3>
                  <p class="exp__company">
                    {{ exp.company }}
                    <span class="badge" style="margin-left:6px">{{ exp.type || 'Full-time' }}</span>
                  </p>
                </div>
                <span class="exp__date text-muted">
                  {{ exp.start }} — {{ exp.end || '至今' }}
                </span>
              </div>
              <p class="text-muted mt-2">{{ exp.description }}</p>
              <div class="tag-row mt-2" v-if="exp.skills">
                <el-tag
                  v-for="s in exp.skills.split(',')"
                  :key="s" size="small" type="info"
                >{{ s.trim() }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 技能 ══════════════════════════════════════════════ -->
    <section class="section skills-bg" v-if="skills.length">
      <div class="container">
        <h2 class="section-title">技能栈</h2>
        <div class="skills-grid">
          <div
            v-for="(grp, i) in skills"
            :key="i"
            class="card"
            :style="{ animationDelay: `${i * 0.07}s` }"
          >
            <p class="skill-cat">{{ grp.category }}</p>
            <div v-for="(sk, j) in grp.items" :key="j" class="skill-item">
              <div class="skill-label">
                <span>{{ sk.name }}</span>
                <span class="text-muted" style="font-size:.8rem">{{ sk.level }}%</span>
              </div>
              <div class="skill-bar">
                <div class="skill-fill" :style="{ width: sk.level + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 教育背景 ══════════════════════════════════════════ -->
    <section class="section" v-if="education.length">
      <div class="container">
        <h2 class="section-title">教育背景</h2>
        <div class="edu-grid">
          <div v-for="(edu, i) in education" :key="i" class="card edu-card">
            <div class="edu-icon">🎓</div>
            <div>
              <h3 style="color:#f1f5f9;font-size:1.05rem">{{ edu.school }}</h3>
              <p class="text-muted">{{ edu.degree }} · {{ edu.major }}</p>
              <p class="text-muted" style="font-size:.8rem;margin-top:4px">
                {{ edu.start }} — {{ edu.end || '至今' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ 最新文章（预览） ══════════════════════════════════ -->
    <section class="section" v-if="latestArticles.length">
      <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:40px">
          <h2 class="section-title" style="margin-bottom:0">最新文章</h2>
          <router-link to="/articles" style="color:#60a5fa;font-size:.9rem">查看全部 →</router-link>
        </div>
        <div class="art-grid">
          <router-link
            v-for="a in latestArticles"
            :key="a.id"
            :to="`/articles/${a.slug}`"
            class="card art-card"
          >
            <div class="art-tag-row">
              <el-tag v-for="t in parseTags(a.tags)" :key="t" size="small">{{ t }}</el-tag>
            </div>
            <h3 class="art-title">{{ a.title }}</h3>
            <p class="art-sum text-muted">{{ a.summary }}</p>
            <div class="art-foot">
              <span>{{ fmtDate(a.published_at) }}</span>
              <span>👁 {{ a.view_count }}</span>
            </div>
          </router-link>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { profileApi, articlesApi } from '@/api/endpoints.js'
import dayjs from 'dayjs'

const profile        = ref(null)
const latestArticles = ref([])

const resume      = computed(() => { try { return JSON.parse(profile.value?.resume_data || '{}') } catch { return {} } })
const experience  = computed(() => resume.value.experience  || [])
const skills      = computed(() => resume.value.skills      || [])
const education   = computed(() => resume.value.education   || [])

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY-MM-DD') : ''

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch {}
  try {
    const res = await articlesApi.list({ page: 1, page_size: 3 })
    latestArticles.value = res.items ?? []
  } catch {}
})
</script>

<style scoped>
/* ── Hero ──────────────────────────────────────────────── */
.hero {
  min-height: 90vh; display: flex; align-items: center;
  background:
    radial-gradient(ellipse at 18% 55%, rgba(59,130,246,.18) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 20%, rgba(139,92,246,.12) 0%, transparent 55%);
  padding: 80px 0;
}
.hero__wrap { display: flex; align-items: center; gap: 64px; }
.hero__avatar-box { position: relative; flex-shrink: 0; }
.hero__avatar {
  width: 200px; height: 200px; border-radius: 50%;
  object-fit: cover; position: relative; z-index: 1;
}
.hero__avatar-ring {
  position: absolute; inset: -6px; border-radius: 50%;
  border: 2px solid transparent;
  background: linear-gradient(135deg,#3b82f6,#8b5cf6) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out; mask-composite: exclude;
}
.hero__badge {
  display: inline-block; padding: 4px 14px; border-radius: 20px;
  background: rgba(16,185,129,.13); color: #10b981;
  border: 1px solid rgba(16,185,129,.3);
  font-size: .8125rem; font-weight: 600; margin-bottom: 14px;
}
.hero__name  { font-size: clamp(2rem,5vw,3.25rem); font-weight: 800; line-height: 1.1; color: #f1f5f9; }
.hero__title { font-size: 1.125rem; color: #60a5fa; font-weight: 600; margin: 8px 0; }
.hero__bio   { max-width: 520px; margin: 10px 0; }
.hero__meta  { display: flex; gap: 20px; font-size: .875rem; color: #64748b; margin: 12px 0; }
.hero__actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }

.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 20px; border-radius: 8px;
  font-size: .875rem; font-weight: 600;
  text-decoration: none; transition: all .2s; cursor: pointer; border: none;
}
.btn--ghost   { border: 1px solid #334155; color: #94a3b8; }
.btn--ghost:hover  { border-color: #60a5fa; color: #60a5fa; }
.btn--primary { background: var(--c-primary); color: #fff; }
.btn--primary:hover { background: var(--c-primary-d); }

/* ── Timeline ──────────────────────────────────────────── */
.timeline { position: relative; padding-left: 28px; }
.timeline::before {
  content: ''; position: absolute; left: 8px; top: 0; bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
}
.timeline__item  { position: relative; margin-bottom: 28px; }
.timeline__dot   {
  position: absolute; left: -24px; top: 20px;
  width: 12px; height: 12px; border-radius: 50%;
  background: #3b82f6; border: 3px solid #0f172a;
  box-shadow: 0 0 10px rgba(59,130,246,.6);
}
.timeline__card  { margin-left: 4px; }
.exp__head       { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; }
.exp__role       { font-size: 1rem; font-weight: 700; color: #f1f5f9; }
.exp__company    { display: flex; align-items: center; font-size: .875rem; color: #94a3b8; margin-top: 4px; }
.exp__date       { font-size: .8125rem; white-space: nowrap; }
.tag-row         { display: flex; flex-wrap: wrap; gap: 6px; }

/* ── Skills ────────────────────────────────────────────── */
.skills-bg   { background: rgba(30,41,59,.3); }
.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 20px; }
.skill-cat   { font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #60a5fa; margin-bottom: 14px; }
.skill-item  { margin-bottom: 10px; }
.skill-label { display: flex; justify-content: space-between; font-size: .875rem; margin-bottom: 5px; }
.skill-bar   { height: 5px; background: #1e293b; border-radius: 3px; overflow: hidden; }
.skill-fill  { height: 100%; background: linear-gradient(90deg,#3b82f6,#8b5cf6); border-radius: 3px; }

/* ── Education ─────────────────────────────────────────── */
.edu-grid  { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 20px; }
.edu-card  { display: flex; align-items: flex-start; gap: 14px; }
.edu-icon  { font-size: 1.75rem; line-height: 1; }

/* ── Latest Articles ───────────────────────────────────── */
.art-grid    { display: grid; grid-template-columns: repeat(auto-fill,minmax(300px,1fr)); gap: 24px; }
.art-card    { display: flex; flex-direction: column; gap: 10px; text-decoration: none; color: inherit; }
.art-tag-row { display: flex; gap: 6px; flex-wrap: wrap; }
.art-title   { font-size: 1rem; font-weight: 700; color: #f1f5f9; line-height: 1.4; }
.art-sum     { font-size: .875rem; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.art-foot    { display: flex; justify-content: space-between; font-size: .8125rem; color: #64748b; padding-top: 8px; border-top: 1px solid #1e293b; }
</style>
