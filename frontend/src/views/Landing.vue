<template>
  <div class="page">
    <!-- HERO -->
    <section class="section hero-section" ref="heroRef">
      <div class="hero-glow hero-glow-1"></div>

      <!-- 竖线 -->
      <div class="hero-line line-1"></div>
      <div class="hero-line line-2"></div>

      <!-- 像素点层 -->
      <canvas ref="canvasRef" class="particle-canvas"></canvas>

      <!-- 右上角小导航 -->
      <div class="top-nav left-nav">
        <span>ABOUT</span>
        <span>SERVICES</span>
        <span>PROJECTS</span>
        <span>CLIENTS</span>
      </div>

      <div class="top-nav right-nav">
        <span>CULTURE & CAREERS</span>
        <span>BLOG</span>
        <span>CONTACT</span>
      </div>

      <!-- 右中说明 -->
      <div class="hero-side-text">
        Answering all of<br />
        your career needs.
      </div>

      <!-- 主标题 -->
      <div class="hero-content">
        <p class="hero-tag">SMART CAREER PLANNING SYSTEM</p>

        <h1 class="hero-title">
          <span class="title-line title-line-1">大学生智能</span>
          <span class="title-line title-line-2">职业规划</span>
        </h1>
      </div>
    </section>

    <!-- 简介 + 横条过渡 -->
    <section class="intro-section" ref="introRef">

      <div class="strip-container">
        <div class="strip strip-1" :style="{ width: strip1Width }"></div>
        <div class="strip strip-2" :style="{ width: strip2Width }"></div>
        <div class="strip strip-3" :style="{ width: strip3Width }"></div>
        <div class="intro-text">
          我们的智能职业规划平台致力于为大学生提供个性化的职业路径推荐。<br />
          基于先进的数据分析与人工智能，系统不仅帮助用户识别潜在发展方向，<br />
          还能够结合兴趣、能力、学习表现与职业需求进行综合评估，<br />
          生成更具针对性的成长建议与发展路径参考。
        </div>
      </div>
    </section>

    <!-- 登录区 -->
    <section class="section login-section" ref="loginRef">
      <div class="login-left">
        <h2>登录系统</h2>
        <p>登录后解锁功能区与 AI 规划区</p>
      </div>

      <div class="login-right">
        <div class="login-form">
          <input type="text" placeholder="Username" />
          <input type="password" placeholder="Password" />
          <button class="login-btn" @click="handleLogin">LOGIN</button>
        </div>
      </div>
    </section>

    <!-- 功能区 -->
    <section class="section function-section">
      <div v-if="!userStore.isLogin" class="lock-mask">
        <div class="lock-box">
          <h3>请先登录</h3>
          <p>登录后自动解锁功能区</p>
        </div>
      </div>

      <h2>功能区</h2>

      <div class="card-list">
        <div class="card">个人信息</div>
        <div class="card">能力评估</div>
        <div class="card">职业推荐</div>
        <div class="card">成长规划</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, nextTick } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const canvasRef = ref(null)
const heroRef = ref(null)
const introRef = ref(null)
const loginRef = ref(null)

const handleLogin = async () => {
  userStore.login()
  await nextTick()
  document.querySelector('.function-section')?.scrollIntoView({
    behavior: 'smooth'
  })
}

/* =========================
   像素点效果
========================= */
let ctx = null
let canvas = null
let dots = []
let rafId = null

const mouse = {
  x: -9999,
  y: -9999,
  active: false
}

const GAP = 14
const BASE_SIZE = 0.7
const MAX_SIZE = 3.2
const RADIUS = 150

const initCanvas = () => {
  canvas = canvasRef.value
  const hero = heroRef.value
  if (!canvas || !hero) return

  const dpr = Math.min(window.devicePixelRatio || 1, 1.5)
  const width = hero.clientWidth
  const height = hero.clientHeight

  canvas.width = width * dpr
  canvas.height = height * dpr
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  dots = []
  for (let y = 10; y < height; y += GAP) {
    for (let x = 10; x < width; x += GAP) {
      dots.push({ x, y })
    }
  }

  drawDots()
}

const drawDots = () => {
  if (!ctx || !canvas || !heroRef.value) return

  const width = heroRef.value.clientWidth
  const height = heroRef.value.clientHeight
  ctx.clearRect(0, 0, width, height)

  for (const d of dots) {
    const dx = mouse.x - d.x
    const dy = mouse.y - d.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    let size = BASE_SIZE
    let alpha = 0.1

    if (mouse.active && dist < RADIUS) {
      const force = 1 - dist / RADIUS
      size = BASE_SIZE + force * MAX_SIZE
      alpha = 0.1 + force * 0.42
    }

    ctx.beginPath()
    ctx.arc(d.x, d.y, size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255,255,255,${alpha})`
    ctx.fill()
  }
}

const requestDraw = () => {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(drawDots)
}

const handleMouseMove = (e) => {
  if (!heroRef.value) return
  const rect = heroRef.value.getBoundingClientRect()
  mouse.x = e.clientX - rect.left
  mouse.y = e.clientY - rect.top
  mouse.active = true
  requestDraw()
}

const handleMouseLeave = () => {
  mouse.active = false
  mouse.x = -9999
  mouse.y = -9999
  requestDraw()
}

const handleResize = () => {
  initCanvas()
  handleScroll()
}

/* =========================
   横条滚动驱动
========================= */
const stripProgress = ref(0)

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const handleScroll = () => {
  if (!introRef.value || !loginRef.value) return

  const introTop = introRef.value.offsetTop
  const loginTop = loginRef.value.offsetTop

  // 让动画在从简介区往登录区滚动过程中逐步发生
  const scrollAnchor = window.scrollY + window.innerHeight * 0.35
  const totalDistance = loginTop - introTop

  let progress = (scrollAnchor - introTop) / totalDistance
  progress = clamp(progress, 0, 1)

  stripProgress.value = progress
}

/* 三条分别到不同终点，且跟滚动实时绑定 */
const strip1Width = computed(() => `${100 - 50 * stripProgress.value}%`) // 100 -> 50
const strip2Width = computed(() => `${100 - 34 * stripProgress.value}%`) // 100 -> 66
const strip3Width = computed(() => `${100 - 17 * stripProgress.value}%`) // 100 -> 83

onMounted(() => {
  initCanvas()
  handleScroll()

  heroRef.value?.addEventListener('mousemove', handleMouseMove)
  heroRef.value?.addEventListener('mouseleave', handleMouseLeave)

  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  if (rafId) cancelAnimationFrame(rafId)

  heroRef.value?.removeEventListener('mousemove', handleMouseMove)
  heroRef.value?.removeEventListener('mouseleave', handleMouseLeave)

  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.page {
  width: 100%;
  min-height: 100vh;
  background: #d9d6d1;
}

.section {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.hero-section {
  min-height: 100vh;
  background: #94b38a;
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}

.hero-glow-1 {
  width: 420px;
  height: 420px;
  right: 18%;
  top: 18%;
  background: rgba(255, 255, 255, 0.045);
}

.hero-line {
  position: absolute;
  background: rgba(255, 255, 255, 0.22);
  z-index: 2;
}

.line-1 {
  left: 51.5%;
  top: 0;
  width: 2px;
  height: 60%;
}

.line-2 {
  left: 77%;
  top: 0;
  width: 1px;
  height: 40%;
}

.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.top-nav {
  position: absolute;
  z-index: 3;
  top: 36px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 13px;
  letter-spacing: 0.8px;
  line-height: 1.2;
}

.left-nav {
  left: 53%;
}

.right-nav {
  left: 78.5%;
}

.hero-side-text {
  position: absolute;
  z-index: 3;
  right: 10%;
  top: 42%;
  color: rgba(255, 255, 255, 0.96);
  font-size: 28px;
  line-height: 1.08;
  font-weight: 500;
  text-align: left;
}

.hero-content {
  position: absolute;
  z-index: 3;
  left: 44px;
  bottom: 58px;
  color: white;
  max-width: 980px;
}

.hero-tag {
  font-size: 12px;
  letter-spacing: 2.4px;
  margin-bottom: 18px;
  margin-left: 40px;
  opacity: 0.9;
}

.hero-title {
  margin: 20px 30px 60px;
  font-weight: 700;
  color: white;
  display: flex;
  flex-direction: column;
}

.title-line {
  display: block;
  font-size: clamp(78px, 10vw, 150px);
  line-height: 0.9;
  letter-spacing: -4px;
}

.title-line-1 {
  margin-bottom: 40px;
}

/* 简介区 */
.intro-section {
  position: relative;
  background: #d9d6d1;
}

.intro-text {
  position: absolute;
  top: 50%;
  right: 0;

  width: 40%;              /* 👈 关键：右半边 */
  transform: translateY(-50%);

  color: white;
  font-family: "Noto Serif SC", serif;

  font-size: 20px;
  line-height: 1.8;

  padding: 0 0px;
  z-index: 5;
}

/* 横条过渡区 */
.strip-container {
  position: relative;
  width: 100%;
  height: 450px;
  background: #d9d6d1;
  overflow: hidden;
}

.strip {
  position: absolute;
  right: 0;
  height: 150px;
  width: 100%;
  background: var(--color-primary);
  transition: width 0.08s linear;
}

.strip-1 {
  bottom: 0;
}

.strip-2 {
  bottom: 150px;
}

.strip-3 {
  bottom: 300px;
}

.login-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 40px;
  padding: 80px 60px;
  background: #d9d6d1;
}

.login-left h2,
.function-section h2 {
  font-size: 56px;
  color: var(--color-primary);
  margin-bottom: 16px;
}

.login-left p {
  color: var(--color-primary);
  font-size: 18px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 420px;
}

.login-form input {
  padding: 16px 12px;
  border: none;
  border-bottom: 1px solid var(--color-primary);
  outline: none;
  background: transparent;
  color: var(--color-primary);
  font-size: 16px;
}

.login-btn {
  padding: 14px 26px;
  border: none;
  background: var(--color-primary);
  color: white;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
}

.function-section {
  padding: 80px 60px;
  background: #d9d6d1;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
  margin-top: 34px;
}

.card {
  min-height: 180px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(60, 78, 56, 0.3);
  color: var(--color-primary);
  font-size: 28px;
}

.lock-mask {
  position: absolute;
  inset: 0;
  z-index: 5;
  background: rgba(20, 20, 20, 0.28);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.lock-box {
  padding: 34px 44px;
  background: rgba(255, 255, 255, 0.88);
  text-align: center;
  color: var(--color-primary);
}

@media (max-width: 1024px) {
  .hero-side-text,
  .top-nav {
    display: none;
  }

  .line-2 {
    display: none;
  }

  .line-1 {
    left: 82%;
    height: 50%;
  }

  .hero-content {
    left: 28px;
    right: 28px;
    bottom: 42px;
  }

  .hero-subtitle-dark {
    font-size: 28px;
    padding: 42px 32px 40px;
  }

  .login-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .title-line {
    letter-spacing: -2px;
  }

  .title-line-1 {
    margin-bottom: 16px;
  }

  .hero-subtitle-dark {
    font-size: 22px;
    line-height: 1.7;
    padding: 32px 20px;
  }

  .strip-container {
    height: 270px;
  }

  .strip {
    height: 90px;
  }

  .strip-2 {
    bottom: 90px;
  }

  .strip-3 {
    bottom: 180px;
  }

  .login-section,
  .function-section {
    padding: 60px 24px;
  }

  .card-list {
    grid-template-columns: 1fr;
  }
}
</style>