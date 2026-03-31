<template>
  <div class="splash" :class="{ 'splash--out': leaving }">

    <!-- ── 深度背景层 ─────────────────────────────────── -->
    <!-- 点阵背景 -->
    <div class="sp-dots"></div>
    <!-- 流光扫描线 -->
    <div class="sp-scanline"></div>
    <!-- Blob 光晕 -->
    <div class="sp-blob sp-blob--1"></div>
    <div class="sp-blob sp-blob--2"></div>
    <div class="sp-blob sp-blob--3"></div>
    <!-- 光束 -->
    <div class="sp-beam sp-beam--1"></div>
    <div class="sp-beam sp-beam--2"></div>

    <!-- ── 浮动粒子 ────────────────────────────────────── -->
    <div class="sp-particles" aria-hidden="true">
      <span v-for="i in 24" :key="i" class="sp-particle" :style="particleStyle(i)"></span>
    </div>

    <!-- ── 主体 ──────────────────────────────────────── -->
    <div class="sp-stage">

      <!-- 头像区 -->
      <div class="sp-avatar-wrap" :class="{ 'sp-avatar-wrap--in': show }">
        <!-- 最外层慢旋光晕 -->
        <div class="sp-halo"></div>
        <!-- 流光外圈（快） -->
        <div class="sp-ring sp-ring--fast"></div>
        <!-- 流光外圈（慢，反向） -->
        <div class="sp-ring sp-ring--slow"></div>
        <!-- 玻璃底座 -->
        <div class="sp-avatar-glass"></div>
        <!-- 轨道粒子 -->
        <div class="sp-orbit sp-orbit--1">
          <span class="sp-orb sp-orb--blue"></span>
        </div>
        <div class="sp-orbit sp-orbit--2">
          <span class="sp-orb sp-orb--purple"></span>
        </div>
        <div class="sp-orbit sp-orbit--3">
          <span class="sp-orb sp-orb--pink"></span>
        </div>
        <img :src="avatarUrl" alt="avatar" class="sp-avatar" />
      </div>

      <!-- 文字区 -->
      <div class="sp-copy">

        <!-- HELLO 徽章 -->
        <div class="sp-badge" :class="{ 'sp-badge--in': show }">
          <span class="sp-badge__dot"></span>
          HELLO WORLD
        </div>

        <!-- 名字 -->
        <h1 class="sp-name" :class="{ 'sp-name--in': show }">
          <span class="sp-name__inner">{{ name }}</span>
        </h1>

        <!-- 职位 -->
        <p class="sp-role" :class="{ 'sp-role--in': show }">{{ tagline }}</p>

        <!-- 打字机欢迎词 -->
        <div class="sp-typewriter" :class="{ 'sp-typewriter--in': typedStarted }">
          <span class="sp-typed">{{ typedText }}</span>
          <span class="sp-cursor" :class="{ 'sp-cursor--blink': cursorBlink }"></span>
        </div>

      </div>

    </div>

    <!-- ── 底部全宽进度条 ─────────────────────────────── -->
    <div class="sp-loader" :class="{ 'sp-loader--in': show }">
      <div class="sp-loader__track">
        <div class="sp-loader__fill" :style="{ width: progress + '%' }">
          <div class="sp-loader__glow"></div>
        </div>
      </div>
      <div class="sp-loader__info">
        <span class="sp-loader__pct">{{ Math.round(progress) }}<em>%</em></span>
        <span class="sp-loader__hint">Loading...</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { profileApi } from '@/api/endpoints.js'

const router       = useRouter()
const show         = ref(false)
const leaving      = ref(false)
const progress     = ref(0)
const profile      = ref(null)
const typedText    = ref('')
const cursorBlink  = ref(false)
const typedStarted = ref(false)

const WELCOME = '欢迎来到我的个人主页 ✦'

const avatarUrl = computed(() =>
  profile.value?.avatar_url ||
  'https://api.dicebear.com/9.x/bottts-neutral/svg?seed=openclaw&backgroundColor=b6e3f4,c0aede,d1d4f9&backgroundType=gradientLinear'
)
const name    = computed(() => profile.value?.full_name || 'Portfolio')
const tagline = computed(() => profile.value?.title     || 'Full Stack Engineer')

/* 粒子分布：分散在画面各处，大小/速度随机 */
function particleStyle(i) {
  const seed  = i * 137.508          // 黄金角散布
  const x     = (seed * 3.7)  % 100
  const y     = (seed * 6.13) % 100
  const size  = 2 + (i % 5)
  const delay = ((i * 0.23) % 3).toFixed(2)
  const dur   = (3 + (i % 4) * 0.8).toFixed(1)
  const hue   = [210, 270, 320][i % 3]  // 蓝/紫/粉
  return {
    left:              `${x}%`,
    top:               `${y}%`,
    width:             `${size}px`,
    height:            `${size}px`,
    animationDelay:    `${delay}s`,
    animationDuration: `${dur}s`,
    background:        `hsl(${hue},80%,65%)`,
    boxShadow:         `0 0 ${size * 2}px hsl(${hue},80%,65%)`,
  }
}

function startTypewriter(delay = 600) {
  setTimeout(() => {
    typedStarted.value = true
    let idx = 0
    const t = setInterval(() => {
      typedText.value = WELCOME.slice(0, ++idx)
      if (idx >= WELCOME.length) { clearInterval(t); cursorBlink.value = true }
    }, 75)
  }, delay)
}

onMounted(async () => {
  try { profile.value = await profileApi.get() } catch {}
  requestAnimationFrame(() => { show.value = true })
  startTypewriter(700)

  const TOTAL = 1900, STEP = 16
  let elapsed = 0
  const t = setInterval(() => {
    elapsed += STEP
    progress.value = 100 * (1 - Math.pow(1 - elapsed / TOTAL, 2.2))
    if (elapsed >= TOTAL) {
      progress.value = 100
      clearInterval(t)
      setTimeout(() => {
        leaving.value = true
        setTimeout(() => router.replace('/'), 600)
      }, 280)
    }
  }, STEP)
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════
   容器
═══════════════════════════════════════════════════════ */
.splash {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: var(--c-bg);
  overflow: hidden;
  transition: opacity .6s cubic-bezier(.4,0,.2,1),
              transform .6s cubic-bezier(.4,0,.2,1),
              filter .6s ease;
}
.splash--out {
  opacity: 0;
  transform: translateY(-6%) scale(1.03);
  filter: blur(6px);
  pointer-events: none;
}

/* ═══════════════════════════════════════════════════════
   点阵背景
═══════════════════════════════════════════════════════ */
.sp-dots {
  position: absolute; inset: 0;
  background-image: radial-gradient(circle, rgba(91,141,238,.22) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 20%, transparent 100%);
  pointer-events: none;
  animation: dotsShift 20s linear infinite;
}
@keyframes dotsShift {
  0%   { background-position: 0 0; }
  100% { background-position: 32px 32px; }
}

/* ═══════════════════════════════════════════════════════
   扫描线
═══════════════════════════════════════════════════════ */
.sp-scanline {
  position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(91,141,238,.018) 2px,
    rgba(91,141,238,.018) 4px
  );
  animation: scanMove 8s linear infinite;
}
@keyframes scanMove {
  0%   { background-position: 0 0; }
  100% { background-position: 0 200px; }
}

/* ═══════════════════════════════════════════════════════
   Blob 光晕
═══════════════════════════════════════════════════════ */
.sp-blob {
  position: absolute; border-radius: 50%;
  filter: blur(100px); pointer-events: none;
}
.sp-blob--1 {
  width: 800px; height: 800px; top: -220px; left: -180px;
  background: radial-gradient(circle, rgba(91,141,238,.38) 0%, transparent 65%);
  animation: blobMove1 20s ease-in-out infinite;
}
.sp-blob--2 {
  width: 700px; height: 700px; bottom: -180px; right: -120px;
  background: radial-gradient(circle, rgba(167,139,250,.32) 0%, transparent 65%);
  animation: blobMove2 25s ease-in-out infinite;
}
.sp-blob--3 {
  width: 500px; height: 500px; top: 40%; left: 42%;
  background: radial-gradient(circle, rgba(244,114,182,.25) 0%, transparent 65%);
  animation: blobMove3 17s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════════════
   光束
═══════════════════════════════════════════════════════ */
.sp-beam {
  position: absolute; pointer-events: none;
  width: 2px;
  background: linear-gradient(to bottom, transparent, rgba(91,141,238,.5), transparent);
  filter: blur(1px);
  opacity: .5;
}
.sp-beam--1 {
  height: 60vh; top: -10%; left: 30%;
  transform: rotate(-25deg);
  animation: beamFloat 8s ease-in-out infinite;
}
.sp-beam--2 {
  height: 50vh; top: 10%; right: 28%;
  background: linear-gradient(to bottom, transparent, rgba(167,139,250,.4), transparent);
  transform: rotate(20deg);
  animation: beamFloat 11s ease-in-out infinite reverse;
}
@keyframes beamFloat {
  0%,100% { opacity: .3; transform: rotate(-25deg) translateY(0); }
  50%      { opacity: .7; transform: rotate(-25deg) translateY(30px); }
}

/* ═══════════════════════════════════════════════════════
   浮动粒子
═══════════════════════════════════════════════════════ */
.sp-particles { position: absolute; inset: 0; pointer-events: none; }
.sp-particle {
  position: absolute; border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: particleDrift linear infinite alternate;
}
@keyframes particleDrift {
  0%   { transform: translate(-50%,-50%) translateY(0)   scale(1); }
  100% { transform: translate(-50%,-50%) translateY(-18px) scale(1.5); }
}

/* ═══════════════════════════════════════════════════════
   主舞台（水平居中）
═══════════════════════════════════════════════════════ */
.sp-stage {
  position: relative; z-index: 2;
  display: flex; flex-direction: column; align-items: center;
  gap: 36px;
}

/* ═══════════════════════════════════════════════════════
   头像区
═══════════════════════════════════════════════════════ */
.sp-avatar-wrap {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  opacity: 0;
  transform: scale(.65) translateY(30px);
  transition: opacity .7s cubic-bezier(.34,1.56,.64,1),
              transform .7s cubic-bezier(.34,1.56,.64,1);
}
.sp-avatar-wrap--in { opacity: 1; transform: scale(1) translateY(0); }

/* 最外大光晕 */
.sp-halo {
  position: absolute; inset: -50px; border-radius: 50%;
  background: radial-gradient(circle, rgba(91,141,238,.18) 0%, rgba(167,139,250,.1) 40%, transparent 70%);
  animation: haloPulse 4s ease-in-out infinite;
}
@keyframes haloPulse {
  0%,100% { transform: scale(1);   opacity: .6; }
  50%      { transform: scale(1.1); opacity: 1; }
}

/* 流光外圈 快 */
.sp-ring { position: absolute; border-radius: 50%; }
.sp-ring--fast {
  inset: -18px;
  background: conic-gradient(
    from 0deg,
    rgba(91,141,238,0)    0%,
    rgba(91,141,238,1)   18%,
    rgba(167,139,250,.9) 38%,
    rgba(244,114,182,.8) 55%,
    rgba(91,141,238,0)  100%
  );
  mask-image: radial-gradient(circle, transparent 88px, black 89px, black 92px, transparent 93px);
  -webkit-mask-image: radial-gradient(circle, transparent 88px, black 89px, black 92px, transparent 93px);
  animation: splashRing 2.5s linear infinite;
  filter: blur(.5px);
}
/* 流光外圈 慢 反向 */
.sp-ring--slow {
  inset: -28px;
  background: conic-gradient(
    from 180deg,
    rgba(244,114,182,0)   0%,
    rgba(244,114,182,.5) 25%,
    rgba(167,139,250,.4) 50%,
    rgba(244,114,182,0) 100%
  );
  mask-image: radial-gradient(circle, transparent 98px, black 99px, black 101px, transparent 102px);
  -webkit-mask-image: radial-gradient(circle, transparent 98px, black 99px, black 101px, transparent 102px);
  animation: splashRing 5s linear infinite reverse;
  opacity: .7;
}
@keyframes splashRing { to { transform: rotate(360deg); } }

/* 玻璃底座 */
.sp-avatar-glass {
  position: absolute; inset: -6px; border-radius: 50%;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255,255,255,.15);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.2),
              0 0 40px rgba(91,141,238,.2);
}

/* 三条轨道粒子 */
.sp-orbit {
  position: absolute; inset: 0; border-radius: 50%;
  pointer-events: none;
}
.sp-orbit--1 { inset: -38px; animation: splashRing 4s linear infinite; }
.sp-orbit--2 { inset: -50px; animation: splashRing 7s linear infinite reverse; }
.sp-orbit--3 { inset: -30px; animation: splashRing 5.5s linear infinite; transform-origin: center; }

.sp-orb {
  position: absolute; border-radius: 50%;
}
.sp-orb--blue   { width:10px;height:10px; top:50%;left:0; transform:translateY(-50%);
                  background:#5b8dee; box-shadow:0 0 12px #5b8dee,0 0 24px rgba(91,141,238,.5); }
.sp-orb--purple { width:7px;height:7px; top:0;left:50%; transform:translateX(-50%);
                  background:#a78bfa; box-shadow:0 0 10px #a78bfa,0 0 20px rgba(167,139,250,.5); }
.sp-orb--pink   { width:6px;height:6px; bottom:8%;right:6%;
                  background:#f472b6; box-shadow:0 0 8px #f472b6,0 0 16px rgba(244,114,182,.5); }

.sp-avatar {
  width: 140px; height: 140px;
  border-radius: 50%; object-fit: cover;
  position: relative; z-index: 1;
  box-shadow: 0 0 0 3px rgba(255,255,255,.12),
              0 20px 60px rgba(0,0,0,.3),
              0 0 40px rgba(91,141,238,.25);
  animation: avatarGlow 3.5s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════════════
   文字区
═══════════════════════════════════════════════════════ */
.sp-copy {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}

/* HELLO 徽章 */
.sp-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 14px; border-radius: 20px;
  font-size: .72rem; font-weight: 700; letter-spacing: .1em;
  color: #5b8dee;
  background: rgba(91,141,238,.1);
  border: 1px solid rgba(91,141,238,.25);
  box-shadow: 0 0 16px rgba(91,141,238,.12), inset 0 1px 0 rgba(255,255,255,.1);
  opacity: 0; transform: translateY(10px) scale(.9);
  transition: opacity .5s ease .1s, transform .5s cubic-bezier(.34,1.56,.64,1) .1s;
}
.sp-badge--in { opacity: 1; transform: translateY(0) scale(1); }
.sp-badge__dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
  animation: pulse 2s ease-in-out infinite;
}

/* 名字 */
.sp-name {
  font-size: clamp(2rem, 6vw, 3.2rem);
  font-weight: 900; letter-spacing: -.04em; line-height: 1;
  margin: 0;
  opacity: 0; transform: translateY(20px);
  transition: opacity .6s ease .2s, transform .6s cubic-bezier(.34,1.4,.64,1) .2s;
}
.sp-name--in { opacity: 1; transform: translateY(0); }
.sp-name__inner {
  background: var(--grad-hero);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: shimmer 4s linear infinite;
  /* 文字描边光晕 */
  filter: drop-shadow(0 0 20px rgba(91,141,238,.35));
}

/* 职位 */
.sp-role {
  font-size: .95rem; font-weight: 500; letter-spacing: .05em;
  color: var(--c-text-muted); margin: 0;
  opacity: 0; transform: translateY(14px);
  transition: opacity .5s ease .32s, transform .5s ease .32s;
}
.sp-role--in { opacity: 1; transform: translateY(0); }

/* ── 打字机 ──────────────────────────────────────────── */
.sp-typewriter {
  display: flex; align-items: center; gap: 2px;
  min-height: 1.8em; margin-top: 4px;
  opacity: 0; transform: translateY(10px);
  transition: opacity .4s ease, transform .4s ease;
}
.sp-typewriter--in { opacity: 1; transform: translateY(0); }

.sp-typed {
  font-size: 1.08rem; font-weight: 600; letter-spacing: .04em;
  background: linear-gradient(90deg, #5b8dee 0%, #a78bfa 50%, #f472b6 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; background-size: 200% auto;
  animation: shimmer 2.5s linear infinite;
}
.sp-cursor {
  display: inline-block;
  width: 2px; height: 1.1em;
  border-radius: 1px;
  background: var(--c-primary);
  margin-left: 2px;
  vertical-align: middle;
}
.sp-cursor--blink { animation: cursorBlink .75s step-end infinite; }
@keyframes cursorBlink {
  0%,100% { opacity: 1; }
  50%      { opacity: 0; }
}

/* ═══════════════════════════════════════════════════════
   底部进度条
═══════════════════════════════════════════════════════ */
.sp-loader {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 0 0 28px;
  z-index: 3;
  opacity: 0; transform: translateY(12px);
  transition: opacity .5s ease .5s, transform .5s ease .5s;
}
.sp-loader--in { opacity: 1; transform: translateY(0); }

.sp-loader__track {
  width: 100%; height: 2px;
  background: rgba(91,141,238,.1);
  position: relative; overflow: visible;
  margin-bottom: 14px;
}
.sp-loader__fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, #3b6fd4, #7c3aed, #db2777);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
  transition: width .08s linear;
  border-radius: 0 2px 2px 0;
}
.sp-loader__glow {
  position: absolute; right: -1px; top: 50%;
  transform: translateY(-50%);
  width: 20px; height: 20px; border-radius: 50%;
  background: radial-gradient(circle, rgba(124,58,237,.9) 0%, transparent 70%);
  filter: blur(4px);
  animation: glowPulse 1s ease-in-out infinite;
}
.sp-loader__info {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 24px;
}
.sp-loader__pct {
  font-size: 1.1rem; font-weight: 800; letter-spacing: -.02em;
  background: var(--grad-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  font-variant-numeric: tabular-nums;
}
.sp-loader__pct em {
  font-style: normal; font-size: .7em; opacity: .7;
}
.sp-loader__hint {
  font-size: .72rem; font-weight: 600; letter-spacing: .1em;
  color: var(--c-text-muted); text-transform: uppercase;
  animation: pulse 2s ease-in-out infinite;
}
</style>
