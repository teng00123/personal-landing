<template>
  <div class="splash" :class="{ 'splash--out': leaving }">

    <!-- 背景 blobs -->
    <div class="sp-blob sp-blob--1"></div>
    <div class="sp-blob sp-blob--2"></div>
    <div class="sp-blob sp-blob--3"></div>
    <!-- 网格 -->
    <div class="sp-grid"></div>

    <!-- 粒子 -->
    <div class="sp-particles">
      <span v-for="i in 18" :key="i" class="sp-particle" :style="particleStyle(i)"></span>
    </div>

    <!-- 主体内容 -->
    <div class="sp-content">

      <!-- Logo 头像 -->
      <div class="sp-avatar-wrap" :class="{ 'sp-avatar-wrap--in': show }">
        <div class="sp-ring sp-ring--outer"></div>
        <div class="sp-ring sp-ring--inner"></div>
        <div class="sp-orbit">
          <span class="sp-dot sp-dot--1"></span>
          <span class="sp-dot sp-dot--2"></span>
          <span class="sp-dot sp-dot--3"></span>
        </div>
        <img
          :src="avatarUrl"
          alt="avatar"
          class="sp-avatar"
        />
      </div>

      <!-- 文字 -->
      <div class="sp-text" :class="{ 'sp-text--in': show }">
        <h1 class="sp-name">{{ name }}</h1>
        <p class="sp-tagline">{{ tagline }}</p>
      </div>

      <!-- 进度条 -->
      <div class="sp-bar-wrap" :class="{ 'sp-bar-wrap--in': show }">
        <div class="sp-bar">
          <div class="sp-bar__fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="sp-bar__label">{{ Math.round(progress) }}%</span>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { profileApi } from '@/api/endpoints.js'

const router   = useRouter()
const show     = ref(false)
const leaving  = ref(false)
const progress = ref(0)
const profile  = ref(null)

const avatarUrl = computed(() =>
  profile.value?.avatar_url ||
  'https://api.dicebear.com/9.x/bottts-neutral/svg?seed=openclaw&backgroundColor=b6e3f4,c0aede,d1d4f9&backgroundType=gradientLinear'
)
const name     = computed(() => profile.value?.full_name || 'Portfolio')
const tagline  = computed(() => profile.value?.title     || 'Welcome')

// 随机粒子样式
function particleStyle(i) {
  const angle  = (i / 18) * 360
  const r      = 38 + (i % 5) * 9   // 38%~74% 半径
  const size   = 3 + (i % 4)
  const delay  = (i * 0.15).toFixed(2)
  const dur    = (2.5 + (i % 3) * 0.7).toFixed(1)
  const x      = 50 + r * Math.cos(angle * Math.PI / 180)
  const y      = 50 + r * Math.sin(angle * Math.PI / 180)
  return {
    left:             `${x}%`,
    top:              `${y}%`,
    width:            `${size}px`,
    height:           `${size}px`,
    animationDelay:   `${delay}s`,
    animationDuration:`${dur}s`,
    opacity:          0.4 + (i % 5) * 0.1,
  }
}

onMounted(async () => {
  // 拉取头像/名字（非阻塞，失败也没关系）
  try { profile.value = await profileApi.get() } catch {}

  // 触发入场动画
  requestAnimationFrame(() => { show.value = true })

  // 进度条动画（约 1.8s 从 0 到 100）
  const TOTAL    = 1800   // ms
  const STEP     = 16
  let   elapsed  = 0
  const timer = setInterval(() => {
    elapsed  += STEP
    // ease-out 曲线
    progress.value = 100 * (1 - Math.pow(1 - elapsed / TOTAL, 2))
    if (elapsed >= TOTAL) {
      progress.value = 100
      clearInterval(timer)
      // 稍作停顿后离场
      setTimeout(() => {
        leaving.value = true
        setTimeout(() => router.replace('/'), 500)
      }, 300)
    }
  }, STEP)
})
</script>

<style scoped>
/* ── 整体容器 ──────────────────────────────────────────── */
.splash {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: var(--c-bg);
  overflow: hidden;
  transition: opacity .5s ease, transform .5s ease;
}
.splash--out {
  opacity: 0;
  transform: scale(1.04);
  pointer-events: none;
}

/* ── 背景 blobs ────────────────────────────────────────── */
.sp-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  pointer-events: none;
}
.sp-blob--1 {
  width: 700px; height: 700px;
  top: -200px; left: -150px;
  background: radial-gradient(circle, rgba(91,141,238,.45) 0%, transparent 70%);
  animation: blobMove1 18s ease-in-out infinite;
}
.sp-blob--2 {
  width: 600px; height: 600px;
  bottom: -150px; right: -100px;
  background: radial-gradient(circle, rgba(167,139,250,.4) 0%, transparent 70%);
  animation: blobMove2 22s ease-in-out infinite;
}
.sp-blob--3 {
  width: 400px; height: 400px;
  top: 45%; left: 45%;
  background: radial-gradient(circle, rgba(244,114,182,.3) 0%, transparent 70%);
  animation: blobMove3 15s ease-in-out infinite;
}

/* ── 网格 ──────────────────────────────────────────────── */
.sp-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(91,141,238,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91,141,238,.05) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
  pointer-events: none;
}

/* ── 粒子 ──────────────────────────────────────────────── */
.sp-particles { position: absolute; inset: 0; pointer-events: none; }
.sp-particle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, #5b8dee, #a78bfa, #f472b6);
  animation: particleFloat var(--dur, 3s) ease-in-out infinite alternate;
  transform: translate(-50%, -50%);
}
@keyframes particleFloat {
  0%   { transform: translate(-50%, -50%) scale(1);   }
  100% { transform: translate(-50%, -60%) scale(1.4); }
}

/* ── 主体内容 ──────────────────────────────────────────── */
.sp-content {
  position: relative; z-index: 2;
  display: flex; flex-direction: column; align-items: center;
  gap: 32px;
}

/* ── 头像区 ────────────────────────────────────────────── */
.sp-avatar-wrap {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transform: scale(.7) translateY(20px);
  transition: opacity .6s cubic-bezier(.34,1.56,.64,1), transform .6s cubic-bezier(.34,1.56,.64,1);
}
.sp-avatar-wrap--in {
  opacity: 1; transform: scale(1) translateY(0);
}

/* 流光外圈 */
.sp-ring {
  position: absolute; border-radius: 50%;
}
.sp-ring--outer {
  inset: -22px;
  background: conic-gradient(
    from 0deg,
    rgba(91,141,238,0)   0%,
    rgba(91,141,238,.9)  20%,
    rgba(167,139,250,.9) 45%,
    rgba(244,114,182,.9) 65%,
    rgba(91,141,238,0)   100%
  );
  animation: splashRing 3s linear infinite;
  mask-image: radial-gradient(circle, transparent 107px, black 108px);
  -webkit-mask-image: radial-gradient(circle, transparent 107px, black 108px);
}
.sp-ring--inner {
  inset: -10px;
  border: 2px solid transparent;
  background:
    linear-gradient(var(--c-bg), var(--c-bg)) padding-box,
    linear-gradient(135deg, #5b8dee, #a78bfa, #f472b6) border-box;
  box-shadow: 0 0 30px rgba(91,141,238,.5), 0 0 60px rgba(167,139,250,.25);
  animation: glowPulse 2.5s ease-in-out infinite;
}

/* 轨道粒子 */
.sp-orbit {
  position: absolute; inset: -36px; border-radius: 50%;
  animation: splashRing 6s linear infinite reverse;
  pointer-events: none;
}
.sp-dot {
  position: absolute; border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
}
.sp-dot--1 { width:9px;height:9px; top:50%;left:0; transform:translateY(-50%); background:#5b8dee;color:#5b8dee; animation:orbitPulse 2s ease-in-out infinite; }
.sp-dot--2 { width:7px;height:7px; bottom:12%;right:7%; background:#a78bfa;color:#a78bfa; animation:orbitPulse 2.5s ease-in-out infinite .5s; }
.sp-dot--3 { width:6px;height:6px; top:10%;right:9%; background:#f472b6;color:#f472b6; animation:orbitPulse 2s ease-in-out infinite 1s; }

.sp-avatar {
  width: 130px; height: 130px;
  border-radius: 50%; object-fit: cover;
  position: relative; z-index: 1;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
  animation: avatarGlow 3s ease-in-out infinite;
}

/* ── 文字 ──────────────────────────────────────────────── */
.sp-text {
  text-align: center;
  opacity: 0; transform: translateY(24px);
  transition: opacity .6s ease .25s, transform .6s ease .25s;
}
.sp-text--in { opacity: 1; transform: translateY(0); }

.sp-name {
  font-size: clamp(1.8rem, 5vw, 2.8rem);
  font-weight: 900;
  letter-spacing: -.03em;
  background: var(--grad-hero);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
  margin-bottom: 8px;
}
.sp-tagline {
  font-size: 1rem; font-weight: 500;
  color: var(--c-text-muted);
  letter-spacing: .04em;
}

/* ── 进度条 ────────────────────────────────────────────── */
.sp-bar-wrap {
  display: flex; align-items: center; gap: 12px;
  opacity: 0; transform: translateY(16px);
  transition: opacity .5s ease .4s, transform .5s ease .4s;
}
.sp-bar-wrap--in { opacity: 1; transform: translateY(0); }

.sp-bar {
  width: 220px; height: 4px;
  border-radius: 4px;
  background: rgba(91,141,238,.15);
  border: 1px solid rgba(91,141,238,.12);
  overflow: hidden;
}
.sp-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, #5b8dee, #a78bfa, #f472b6);
  background-size: 200% 100%;
  border-radius: 4px;
  transition: width .06s linear;
  animation: shimmer 1.5s linear infinite;
  box-shadow: 0 0 8px rgba(91,141,238,.5);
}
.sp-bar__label {
  font-size: .78rem; font-weight: 700;
  color: var(--c-text-muted);
  min-width: 36px; text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ── Keyframes (补充，不在 global.css 的) ──────────────── */
@keyframes splashRing { to { transform: rotate(360deg); } }
</style>
