<template>
  <div class="page">
    <!-- HERO -->
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
          <span class="title-line title-line-1">计算机专业智能</span>
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

        <div class="intro-copy">
          <p class="intro-kicker">COMPUTER SCIENCE · CAREER PATH</p>
          <p class="intro-lead">不只是推荐职业，</p>
          <h2>
            先看清<span>计算机能力</span><br />
            再规划<span>成长路径</span>
          </h2>
          <p class="intro-desc">
            系统会结合个人资料、综合能力评估与计算机能力画像，<br />
            匹配后端、前端、AI、数据、安全等技术方向，<br />
            再生成大学剩余阶段的年度计划与补强任务。
          </p>
        </div>
      </div>
    </section>

    <!-- 鐧诲綍鍖?-->
    <div ref="loginRef">
      <LoginSection
          @login-success="handleLoginSuccess"
      />
    </div>

    <!-- 鏈櫥褰曟彁绀哄尯 -->
    <section v-if="!userStore.isLogin" class="unlock-section">
      <div class="unlock-box">
        <p class="unlock-kicker">LOCKED MODULES</p>
        <p class="unlock-desc">登录后可使用个人信息、能力评估、职业规划与成长规划功能。</p>

        <div class="unlock-actions">
          <button class="login-btn" @click="scrollToLogin">去登录</button>
        </div>
      </div>
    </section>

    <!-- 鍔熻兘鍖猴細鍙湁鐧诲綍鍚庢墠鏄剧ず -->
    <section id="functions" v-if="userStore.isLogin" class="function-section" ref="functionRef">
      <div class="function-sticky">
        <div class="function-layout">
          <div class="function-left">
            <p class="function-kicker">功能模块</p>
            <h2 class="function-title">每一步都有方向</h2>
            <p class="function-desc">
              完善个人信息，评估核心能力，发现适合的职业方向，并生成清晰的成长规划。
            </p>

            <div class="function-hint">
              <span class="hint-dot"></span>
              <span>{{ cardsExpanded ? '点击卡片进入页面' : '点击展开功能卡片' }}</span>
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
import { computed, nextTick, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import LoginSection from '../components/LoginSection.vue'

const userStore = useUserStore()
const route = useRoute()
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

const scrollToFunctions = async () => {
  if (route.hash !== '#functions' || !userStore.isLogin) return

  cardsExpanded.value = true
  await nextTick()
  functionRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

const goFunctionPage = (item) => {
  if (!cardsExpanded.value) {
    cardsExpanded.value = true
    return
  }

  router.push(item.path)
}

/* =========================
   绮掑瓙鏁堟灉
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
   宸ュ叿
========================= */
const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

/* =========================
   绠€浠嬫í鏉℃粴鍔?
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
// 鐧诲綍鎴愬姛锛氳В閿佸姛鑳藉尯 + 鑷姩灞曞紑 + 鑷姩婊氬姩
const handleLoginSuccess = () => {
  cardsExpanded.value = false
}

// 鈥斺€斺€斺€斺€斺€斺€斺€斺€斺€?鍒锋柊鑷姩鍏抽棴鍗＄墖 鈥斺€斺€斺€斺€斺€斺€斺€斺€斺€?
onMounted(() => {
  cardsExpanded.value = false
  scrollToFunctions()
})

watch(
  () => [route.hash, userStore.isLogin],
  () => {
    scrollToFunctions()
  }
)

/* =========================
   鍔熻兘鍗＄墖鏁版嵁
========================= */
const functionCards = [
  {
    title: '个人信息',
    en: 'PROFILE',
    desc: '沉淀年级、专业、兴趣、技能与目标偏好。',
    path: '/profile'
  },
  {
    title: '能力评估',
    en: 'ABILITY',
    desc: '双维评估综合素质与计算机能力，形成能力画像。',
    path: '/assessment'
  },
  {
    title: '职业规划',
    en: 'CAREER',
    desc: '匹配就业、考研、考公、留学路径与职业方向。',
    path: '/career'
  },
  {
    title: '成长规划',
    en: 'PLANNING',
    desc: '生成年度学习、项目、材料与补强任务。',
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

.page {
  --main-divider-left: clamp(0px, 49%, 763px);
  width: 100%;
  min-height: 100vh;
  background: #E7E8E4;
}

.section {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

/* HERO */
.hero-section {
  min-height: 100vh;
  background:
    linear-gradient(rgba(147, 164, 193, 0.58), rgba(147, 164, 193, 0.58)),
    url('../public/images/head.jpg') center center / cover no-repeat;
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
  bottom: 98px;
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
  font-size: clamp(66px, 8vw, 124px);
  line-height: 0.9;
  letter-spacing: -4px;
  white-space: nowrap;
}

.title-line-1 {
  margin-bottom: 40px;
}

/* 绠€浠嬪尯 */
.intro-section {
  position: relative;
  background: #E7E8E4;
}

.intro-copy {
  position: absolute;
  top: 50%;
  right: clamp(28px, 6vw, 96px);
  width: min(520px, 42%);
  transform: translateY(-50%);
  color: #ffffff;
  z-index: 5;
}

.intro-kicker {
  margin: 0 0 22px;
  font-size: 11px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.22em;
  color: rgba(255, 255, 255, 0.68);
}

.intro-lead {
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.78);
  font-size: clamp(17px, 1.45vw, 22px);
  line-height: 1.2;
  font-weight: 400;
}

.intro-copy h2 {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  font-size: clamp(30px, 3.25vw, 48px);
  line-height: 1.12;
  font-weight: 600;
  letter-spacing: 0;
  color: #ffffff;
}

.intro-copy h2 span {
  font-size: 1.06em;
  font-weight: 700;
}

.intro-desc {
  max-width: 560px;
  margin: 22px 0 0;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.82;
  color: rgba(255, 255, 255, 0.82);
}

.strip-container {
  position: relative;
  width: 100%;
  height: 450px;
  background: #E7E8E4;
  overflow: hidden;
}

.strip {
  position: absolute;
  right: 0;
  height: 150px;
  width: 100%;
  background: #8D97A7;
  transition: width 0.08s linear;
}

.strip-1 { bottom: 0; }
.strip-2 { bottom: 150px; }
.strip-3 { bottom: 300px; }


.login-actions {
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



/* 鏈櫥褰曟彁绀哄尯 */
.unlock-section {
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: #E7E8E4;
}

.unlock-box {
  width: 100%;
  min-height: 86px;
  padding: 18px 34px;
  border: none;
  background: #93A4C1;
  box-shadow: none;
  backdrop-filter: none;
  display: grid;
  grid-template-columns: 1fr auto minmax(320px, 620px) 1fr auto;
  justify-content: stretch;
  align-items: center;
  gap: 18px;
}

.unlock-kicker {
  grid-column: 2;
  font-size: 12px;
  letter-spacing: 2.4px;
  color: rgba(255, 255, 255, 0.78);
  margin: 0;
  white-space: nowrap;
}

.unlock-desc {
  grid-column: 3;
  max-width: none;
  font-size: 16px;
  line-height: 1.5;
  color: white;
  margin: 0;
}

.unlock-actions {
  margin-top: 0;
  grid-column: 5;
}

/* 鍔熻兘鍖?*/
.function-section {
  position: relative;
  height: 100vh;
  min-height: 860px;
  background: #E7E8E4;
  overflow: hidden;
}

.function-section::before {
  content: "";
  position: absolute;
  top: 76px;
  left: 60px;
  right: 60px;
  height: 1px;
  background: rgba(63, 79, 92, 0.72);
  z-index: 2;
}

.function-section::after {
  content: "";
  position: absolute;
  left: var(--main-divider-left);
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(63, 79, 92, 0.72);
  z-index: 2;
}

.function-sticky {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 60px;
}

.function-sticky::before {
  content: "";
  position: absolute;
  left: 66%;
  top: 76px;
  bottom: 0;
  width: 1px;
  background: rgba(63, 79, 92, 0.56);
  z-index: 1;
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
  padding-left: 72px;
  padding-right: 0;
}

.function-kicker {
  font-size: 12px;
  letter-spacing: 2.4px;
  color: rgba(63, 79, 92, 0.72);
  margin-bottom: 18px;
}

.function-title {
  font-size: clamp(56px, 6.4vw, 104px);
  line-height: 1;
  letter-spacing: 0;
  font-weight: 600;
  color: #3f4f5c;
  margin: 0 0 28px;
  max-width: 520px;
}

.function-desc {
  max-width: 430px;
  font-size: 18px;
  line-height: 1.65;
  color: #3f4f5c;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  text-transform: none;
  margin: 0;
}

.function-hint {
  margin-top: 36px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(63, 79, 92, 0.68);
  font-size: 12px;
  letter-spacing: 1px;
  text-transform: none;
}

.hint-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3f4f5c;
  box-shadow: 0 0 0 6px rgba(63, 79, 92, 0.1);
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

.fan-stage::after {
  content: "";
  position: absolute;
  background: rgba(53, 86, 138, 0.55);
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
  color: #3f4f5c;
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
  max-width: 90%;
  font-size: 14px;
  line-height: 1.55;
  color: #3f4f5c;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  text-transform: none;
}

.fan-card-bottom {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: rgba(63, 79, 92, 0.72);
  font-size: 12px;
  letter-spacing: 1.6px;
  text-transform: uppercase;
}

.fan-card-tag {
  opacity: 0.82;
}

.fan-card-open {
  color: #3f4f5c;
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
    padding-left: 28px;
    padding-right: 0;
  }

  .function-title {
    max-width: 760px;
  }

  .function-desc {
    max-width: 760px;
    font-size: 16px;
    line-height: 1.6;
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
    bottom: 82px;
  }

  .intro-copy {
    width: 48%;
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
    font-size: clamp(48px, 10vw, 78px);
    letter-spacing: 0;
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
  .hero-title {
    margin: 18px 0 56px;
  }

  .title-line {
    font-size: clamp(34px, 10.5vw, 54px);
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

  .intro-copy {
    right: 18px;
    width: min(70%, 360px);
  }

  .intro-kicker {
    margin-bottom: 10px;
    font-size: 10px;
  }

  .intro-lead {
    margin-bottom: 8px;
    font-size: 14px;
  }

  .intro-copy h2 {
    font-size: clamp(23px, 6.4vw, 32px);
  }

  .intro-desc {
    margin-top: 14px;
    font-size: 11px;
    line-height: 1.65;
  }

  .unlock-box {
    grid-template-columns: 1fr;
    align-items: start;
    gap: 10px;
  }

  .unlock-kicker,
  .unlock-desc,
  .unlock-actions {
    grid-column: auto;
  }

  .unlock-actions {
    width: 100%;
  }

  .unlock-actions .login-btn {
    width: 100%;
  }

  .function-sticky {
    padding: 0 18px;
  }

  .function-section::before {
    left: 18px;
    right: 18px;
    top: 62px;
    height: 1px;
  }

  .function-section::after {
    left: 34%;
    top: 62px;
    bottom: 0;
    width: 1px;
  }

  .function-sticky::before {
    left: 70%;
    top: 62px;
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




