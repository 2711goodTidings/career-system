<template>
  <div class="page">
    <!-- HERO -->
    <div class="brand-bar">
      <img :src="diceLogo" class="brand-logo" />
      <div class="brand-text">
        SMART CAREER PLANNING
      </div>
    </div>

    <section class="section hero-section" ref="heroRef">
      <div class="hero-glow hero-glow-1"></div>

      <div class="hero-line line-1"></div>
      <div class="hero-line line-2"></div>

      <canvas ref="canvasRef" class="particle-canvas"></canvas>

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

      <div class="hero-side-text">
        Answering all of<br />
        your career needs.
      </div>

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
    <div ref="loginRef">
      <LoginSection
          @login-success="handleLoginSuccess"
      />
    </div>

    <!-- 未登录提示区 -->
    <section v-if="!userStore.isLogin" class="unlock-section">
      <div class="unlock-box">
        <p class="unlock-kicker">LOCKED MODULES</p>
        <h2 class="unlock-title">Login to unlock more features</h2>
        <p class="unlock-desc">
          After signing in, you can access your profile, ability evaluation,
          career recommendation, and intelligent planning modules.
        </p>

        <div class="unlock-actions">
          <button class="login-btn" @click="scrollToLogin">GO TO LOGIN</button>
        </div>
      </div>
    </section>

    <!-- 功能区：只有登录后才显示 -->
    <section v-if="userStore.isLogin" class="function-section" ref="functionRef">
      <div class="function-sticky">
        <div class="function-layout">
          <div class="function-left">
            <p class="function-kicker">FUNCTIONS</p>
            <h2 class="function-title">Here at every step</h2>
            <p class="function-desc">
              Build your profile, evaluate your abilities, discover suitable careers,
              and generate an intelligent growth roadmap within one integrated system.
            </p>

            <div class="function-hint">
              <span class="hint-dot"></span>
              <span>{{ cardsExpanded ? 'Click a card to enter' : 'Click to expand cards' }}</span>
            </div>
          </div>

          <div class="function-right">
            <div
              class="fan-stage"
              :class="{ expanded: cardsExpanded }"
              @click="handleStageClick"
            >
              <div
                v-for="(item, index) in functionCards"
                :key="item.title"
                class="fan-card"
                :class="[
                  `fan-card-${index + 1}`,
                  { expanded: cardsExpanded }
                ]"
                :style="fanCardStyle(index)"
                @click.stop="goFunctionPage(item)"
              >
                <div class="fan-card-inner">
                  <div class="fan-card-top">
                    <span class="fan-card-title">{{ item.title }}</span>
                    <span class="fan-card-index">0{{ index + 1 }}</span>
                  </div>

                  <div class="fan-card-line"></div>

                  <p class="fan-card-text">
                    {{ item.desc }}
                  </p>

                  <div class="fan-card-bottom">
                    <span class="fan-card-tag">{{ item.en }}</span>
                    <span class="fan-card-open">VIEW</span>
                  </div>
                </div>
              </div>

              <div class="fan-stage-center-glow"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import diceLogo from '../assets/dice-logo.png'
import LoginSection from '../components/LoginSection.vue'

const userStore = useUserStore()
const router = useRouter()

const canvasRef = ref(null)
const heroRef = ref(null)
const introRef = ref(null)
const loginRef = ref(null)
const functionRef = ref(null)

const cardsExpanded = ref(false)

const resetCardsExpanded = () => {
  cardsExpanded.value = false
}
const scrollToLogin = () => {
  loginRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

const handleStageClick = () => {
  if (!cardsExpanded.value) {
    cardsExpanded.value = true
  }
}

const goFunctionPage = (item) => {
  if (!cardsExpanded.value) {
    cardsExpanded.value = true
    return
  }

  router.push(item.path)
}

/* =========================
   粒子效果
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
const BASE_SIZE = 0.1
const MAX_SIZE = 3.6
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

    let size = BASE_SIZE + 0.8
    let alpha = 0.24

    if (mouse.active && dist < RADIUS) {
      const force = 1 - dist / RADIUS
      size = BASE_SIZE + force * MAX_SIZE
      alpha = 0.24 + force * 0.38
    }

    ctx.beginPath()
    ctx.arc(d.x, d.y, size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(227,159,159,${alpha})`
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

/* =========================
   工具
========================= */
const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

/* =========================
   简介横条滚动
========================= */
const stripProgress = ref(0)

const handleIntroProgress = () => {
  if (!introRef.value || !loginRef.value) return

  const introTop = introRef.value.offsetTop
  const loginTop = loginRef.value.offsetTop
  const scrollAnchor = window.scrollY + window.innerHeight * 0.35
  const totalDistance = loginTop - introTop

  let progress = (scrollAnchor - introTop) / totalDistance
  progress = clamp(progress, 0, 1)

  stripProgress.value = progress
}

const strip1Width = computed(() => `${100 - 50 * stripProgress.value}%`)
const strip2Width = computed(() => `${100 - 34 * stripProgress.value}%`)
const strip3Width = computed(() => `${100 - 17 * stripProgress.value}%`)
// 登录成功：解锁功能区 + 自动展开 + 自动滚动
const handleLoginSuccess = () => {
  setTimeout(() => {
    // 滚动到功能区
    functionRef.value?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
    // 自动展开卡片
    cardsExpanded.value = true
  }, 500)
}

// —————————— 刷新自动关闭卡片 ——————————
onMounted(() => {
  cardsExpanded.value = false
})

/* =========================
   功能卡片数据
========================= */
const functionCards = [
  {
    title: '个人信息',
    en: 'PROFILE',
    desc: 'Manage your personal background, major, interests and key skill profile.',
    path: '/profile'
  },
  {
    title: '能力评估',
    en: 'ABILITY',
    desc: 'Evaluate core abilities from learning performance and multiple competence dimensions.',
    path: '/ability'
  },
  {
    title: '职业推荐',
    en: 'CAREER',
    desc: 'Match suitable career directions based on your profile, strengths and assessment results.',
    path: '/career'
  },
  {
    title: '成长规划',
    en: 'PLANNING',
    desc: 'Generate an intelligent roadmap for skills, goals and long-term development planning.',
    path: '/planning'
  }
]

const collapsedStates = [
  { x: 42, y: 40, r: -10, z: 4, o: 1 },
  { x: 56, y: 54, r: -3, z: 3, o: 1 },
  { x: 72, y: 70, r: 4, z: 2, o: 1 },
  { x: 92, y: 92, r: 10, z: 1, o: 1 }
]

const expandedStates = [
  { x: 10, y: 0, r: 0, z: 4, o: 1 },
  { x: 55, y: 200, r: 0, z: 3, o: 1 },
  { x: 100, y: 400, r: 0, z: 2, o: 1 },
  { x: 145, y: 600, r: 0, z: 1, o: 1 }
]

const fanCardStyle = (index) => {
  const state = cardsExpanded.value ? expandedStates[index] : collapsedStates[index]

  return {
    transform: `translate(${state.x}px, ${state.y}px) rotate(${state.r}deg)`,
    zIndex: state.z,
    opacity: state.o,
    transitionDelay: `${index * 70}ms`
  }
}

const handleScroll = () => {
  handleIntroProgress()
}

const handleResize = () => {
  initCanvas()
  handleScroll()
}

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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.brand-bar {
  position: absolute;
  top: 28px;
  left: 34px;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #35568a;
  backdrop-filter: blur(8px);
  border-radius: 0;
  height: 40px;
  width: 300px;
  box-shadow:
    0 6px 20px rgba(0,0,0,0.15),
    inset 0 1px 0 rgba(255,255,255,0.08);
}

.brand-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.2));
}

.brand-text {
  color: rgba(255,255,255,0.92);
  font-size: 12px;
  letter-spacing: 2.2px;
  font-weight: 500;
  white-space: nowrap;
}

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

/* HERO */
.hero-section {
  min-height: 100vh;
  background: #8b9bc1;
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
  width: 40%;
  transform: translateY(-50%);
  color: white;
  font-family: "Noto Serif SC", serif;
  font-size: 20px;
  line-height: 1.8;
  padding: 0;
  z-index: 5;
}

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
  background: #8b9bc1;
  transition: width 0.08s linear;
}

.strip-1 { bottom: 0; }
.strip-2 { bottom: 150px; }
.strip-3 { bottom: 300px; }


.login-actions,
.unlock-actions {
  display: flex;
  gap: 14px;
  margin-top: 8px;
}

.login-btn {
  padding: 14px 26px;
  border: none;
  background: #35568a;
  color: white;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(53, 86, 138, 0.18);
}



/* 未登录提示区 */
.unlock-section {
  min-height: 62vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 24px 120px;
  background: #d9d6d1;
}

.unlock-box {
  width: min(920px, 100%);
  padding: 54px 56px;
  border: 1px solid rgba(53, 86, 138, 0.18);
  background: rgba(255,255,255,0.62);
  box-shadow: 0 18px 40px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(6px);
}

.unlock-kicker {
  font-size: 12px;
  letter-spacing: 2.4px;
  color: rgba(53, 86, 138, 0.72);
  margin-bottom: 18px;
}

.unlock-title {
  font-size: clamp(34px, 5vw, 72px);
  line-height: 0.95;
  letter-spacing: -2px;
  color: #2336c1;
  margin-bottom: 24px;
}

.unlock-desc {
  max-width: 650px;
  font-size: 18px;
  line-height: 1.7;
  color: #35568a;
}

/* 功能区 */
.function-section {
  position: relative;
  height: 100vh;
  min-height: 860px;
  background: #d9d6d1;
  overflow: hidden;
}

.function-sticky {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 60px;
}

.function-layout {
  width: 100%;
  display: grid;
  grid-template-columns: 0.94fr 1.18fr;
  align-items: center;
  gap: 40px;
}

.function-left {
  position: relative;
  padding-right: 24px;
}

.function-kicker {
  font-size: 12px;
  letter-spacing: 2.4px;
  color: rgba(53, 86, 138, 0.72);
  margin-bottom: 18px;
}

.function-title {
  font-size: clamp(80px, 10vw, 152px);
  line-height: 0.9;
  letter-spacing: -5px;
  font-weight: 600;
  color: #2336c1;
  margin: 0 0 44px;
  max-width: 520px;
}

.function-desc {
  max-width: 360px;
  font-size: 22px;
  line-height: 1.25;
  color: #35568a;
  font-family: "Courier New", monospace;
  text-transform: uppercase;
  margin: 0;
}

.function-hint {
  margin-top: 36px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(53, 86, 138, 0.62);
  font-size: 12px;
  letter-spacing: 1.8px;
  text-transform: uppercase;
}

.hint-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2336c1;
  box-shadow: 0 0 0 6px rgba(35, 54, 193, 0.08);
}

.function-right {
  position: relative;
  height: 760px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fan-stage {
  position: relative;
  width: 760px;
  height: 660px;
  cursor: pointer;
}

.fan-stage::before,
.fan-stage::after {
  content: "";
  position: absolute;
  background: rgba(53, 86, 138, 0.55);
}

.fan-stage::before {
  left: 52%;
  top: -30px;
  width: 1px;
  height: 112%;
}

.fan-stage::after {
  left: 6%;
  bottom: 0;
  width: 1px;
  height: 34%;
  opacity: 0.7;
}

.fan-stage-center-glow {
  position: absolute;
  right: 150px;
  top: 110px;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139,155,193,0.12) 0%, rgba(139,155,193,0) 72%);
  pointer-events: none;
}

.fan-card {
  position: absolute;
  left: 0;
  top: 0;
  width: 600px;
  height: 190px;
  background: rgba(255,255,255,0.74);
  border: 1px solid rgba(53, 86, 138, 0.18);
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
  will-change: transform;
  transition:
    transform 0.95s cubic-bezier(.22,.98,.24,1),
    box-shadow 0.35s ease,
    border-color 0.35s ease;
}

.fan-card:hover {
  box-shadow: 0 20px 38px rgba(53, 86, 138, 0.16);
  border-color: rgba(35, 54, 193, 0.28);
}

.fan-card-inner {
  width: 100%;
  height: 100%;
  padding: 14px 22px 12px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 10px;
}

.fan-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  color: #2336c1;
}

.fan-card-title {
  flex: 1;
  min-width: 0;
  font-size: 28px;
  line-height: 1.05;
  font-weight: 400;
  letter-spacing: -0.5px;
}

.fan-card-index {
  flex: 0 0 auto;
  margin: 0;
  font-size: 26px;
  line-height: 1;
  font-weight: 400;
  padding-left: 8px;
}

.fan-card-line {
  width: 100%;
  height: 1px;
  background: rgba(53, 86, 138, 0.45);
  margin-top: 0;
  margin-bottom: 2px;
}

.fan-card-text {
  margin: 0;
  max-width: 86%;
  font-size: 14px;
  line-height: 1.45;
  color: #4c63c9;
  font-family: "Courier New", monospace;
  text-transform: uppercase;
}

.fan-card-bottom {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: rgba(53, 86, 138, 0.72);
  font-size: 12px;
  letter-spacing: 1.6px;
  text-transform: uppercase;
}

.fan-card-tag {
  opacity: 0.82;
}

.fan-card-open {
  color: #2336c1;
}

@media (max-width: 1320px) {
  .function-sticky {
    padding: 0 24px;
  }

  .function-layout {
    grid-template-columns: 1fr;
    gap: 28px;
    align-items: start;
  }

  .function-left {
    padding-right: 0;
  }

  .function-title {
    max-width: 760px;
  }

  .function-desc {
    max-width: 760px;
    font-size: 18px;
    line-height: 1.5;
  }

  .function-right {
    justify-content: flex-start;
    height: 700px;
  }

  .fan-stage {
    width: 100%;
    max-width: 760px;
  }
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

  .intro-text {
    width: 48%;
    font-size: 18px;
  }

  .unlock-box {
    padding: 40px 28px;
  }

  .function-section {
    height: auto;
    min-height: 980px;
    padding: 80px 0;
  }

  .function-title {
    font-size: clamp(56px, 12vw, 92px);
    letter-spacing: -2px;
  }

  .function-right {
    height: 620px;
  }

  .fan-stage {
    height: 560px;
  }

  .fan-card {
    width: min(100%, 560px);
    height: 200px;
  }

  .fan-card-title {
    font-size: 24px;
  }

  .fan-card-index {
    font-size: 22px;
  }

  .fan-card-text {
    font-size: 13px;
    max-width: 88%;
  }
}

@media (max-width: 768px) {
  .brand-bar {
    left: 16px;
    top: 16px;
    width: 252px;
  }

  .title-line {
    letter-spacing: -2px;
  }

  .title-line-1 {
    margin-bottom: 16px;
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

  .intro-text {
    width: 52%;
    font-size: 14px;
    line-height: 1.8;
    padding-right: 12px;
  }

  .unlock-actions {
    flex-direction: column;
  }

  .function-sticky {
    padding: 0 18px;
  }

  .function-right {
    height: 520px;
  }

  .fan-stage {
    height: 500px;
  }

  .fan-card {
    width: calc(100% - 24px);
    height: 124px;
  }

  .fan-card-inner {
    padding: 14px 16px;
  }

  .fan-card-title {
    font-size: 20px;
  }

  .fan-card-index {
    font-size: 18px;
  }

  .fan-card-text {
    font-size: 12px;
    line-height: 1.4;
    max-width: 100%;
  }
}
</style>