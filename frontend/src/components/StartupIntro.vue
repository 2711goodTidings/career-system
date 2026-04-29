<template>
  <div class="intro-overlay" :class="{ fadeout: isFadeout }">
    <div class="scene">
      <div class="intro-text">
        Choose Your Career Clearly
      </div>
      <!-- 3D 骰子 -->
      <div
        class="dice-3d"
        :class="{
          drop: started,
          settle: settled,
          showSix: showSix,
          hide3d: toFlat
        }"
      >
        <div class="face front six"></div>
        <div class="face back one"></div>
        <div class="face right three"></div>
        <div class="face left four"></div>
        <div class="face top two"></div>
        <div class="face bottom five"></div>
      </div>

      <!-- 地面阴影 -->
      <div
        class="ground-shadow"
        :class="{
          shadowIn: settled,
          shadowOut: moveCorner
        }"
      ></div>

      <!-- 最终平面 logo -->
      <img
      :src="diceLogo"
      alt="Career Planner Logo"
      class="logo-flat"
      :class="{
        show: toFlat,
        moveCorner: moveCorner
      }"
/>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import diceLogo from '../assets/dice-logo.png'

const emit = defineEmits(['finish'])

const started = ref(false)
const settled = ref(false)
const showSix = ref(false)
const toFlat = ref(false)
const moveCorner = ref(false)
const isFadeout = ref(false)

onMounted(() => {
  // 开始掉落
  setTimeout(() => {
    started.value = true
  }, 50)

  // 落地回弹
  setTimeout(() => {
    settled.value = true
  }, 1000)

  // 转成正面 6 点
  setTimeout(() => {
    showSix.value = true
  }, 1450)

  // 3D -> 平面 logo
  setTimeout(() => {
    toFlat.value = true
  }, 1900)

  // 平面 logo 移动到左上角
  setTimeout(() => {
    moveCorner.value = true
  }, 2250)

  // 背景淡出
  setTimeout(() => {
    isFadeout.value = true
  }, 2850)

  // 通知父组件移除启动层
  setTimeout(() => {
    emit('finish')
  }, 3450)
})
</script>

<style scoped>
.intro-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.18), transparent 34%),
    #93A4C1;
  opacity: 1;
  transition: opacity 0.7s ease;
  overflow: hidden;
}

.intro-overlay.fadeout {
  opacity: 0;
  pointer-events: none;
}

.scene {
  position: relative;
  width: 260px;
  height: 260px;
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 1400px;
}
/* =====================
   动画标题
===================== */
.intro-text {
  position: absolute;
  top: -60px;   /* 在骰子上方 */
  left: 50%;
  transform: translateX(-50%);

  color: rgba(255,255,255,0.9);

  font-size: 30px;
  letter-spacing: 3px;
  font-weight: 500;

  opacity: 0;
  animation: textFadeIn 1.2s ease forwards;

  white-space: nowrap;
}
@keyframes textFadeIn {
  0% {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  100% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
/* =========================
   3D 骰子
========================= */
.dice-3d {
  position: absolute;
  width: 130px;
  height: 130px;
  transform-style: preserve-3d;
  transform: translateY(-340px) rotateX(220deg) rotateY(160deg) rotateZ(-18deg);
  opacity: 1;
}

.drop {
  animation: diceDrop 1s cubic-bezier(.22,.92,.24,1) forwards;
}

.settle {
  animation: diceSettle 0.38s ease-out forwards;
}

.face-six {
  transition: transform 0.55s ease;
  transform: translateY(0) rotateX(0deg) rotateY(0deg) rotateZ(0deg);
}

.hide3d {
  opacity: 0;
  transition: opacity 0.28s ease;
}

.face {
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, #ffffff, #f2f3ee);
  border-radius: 30px;
  box-shadow:
    0 20px 48px rgba(0, 0, 0, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.95),
    inset 0 -8px 14px rgba(60, 78, 56, 0.06);
}

.front  { transform: translateZ(65px); }
.back   { transform: rotateY(180deg) translateZ(65px); }
.right  { transform: rotateY(90deg) translateZ(65px); }
.left   { transform: rotateY(-90deg) translateZ(65px); }
.top    { transform: rotateX(90deg) translateZ(65px); }
.bottom { transform: rotateX(-90deg) translateZ(65px); }

/* 黑点 */
.face::before {
  content: "";
  position: absolute;
  width: 15px;
  height: 15px;
  background: #131313;
  border-radius: 50%;
}

/* 1 */
.one::before {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 2 */
.two::before {
  top: 24px;
  left: 24px;
  box-shadow: 49px 49px #131313;
}

/* 3 */
.three::before {
  top: 24px;
  left: 24px;
  box-shadow:
    24.5px 24.5px #131313,
    49px 49px #131313;
}

/* 4 */
.four::before {
  top: 24px;
  left: 24px;
  box-shadow:
    49px 0 #131313,
    0 49px #131313,
    49px 49px #131313;
}

/* 5 */
.five::before {
  top: 24px;
  left: 24px;
  box-shadow:
    49px 0 #131313,
    0 49px #131313,
    49px 49px #131313,
    24.5px 24.5px #131313;
}

/* 6 */
.six::before {
  top: 21px;
  left: 28px;
  box-shadow:
    57px 0 #131313,
    0 35px #131313,
    57px 35px #131313,
    0 70px #131313,
    57px 70px #131313;
}

/* =========================
   阴影
========================= */
.ground-shadow {
  position: absolute;
  left: 50%;
  bottom: 42px;
  width: 118px;
  height: 22px;
  transform: translateX(-50%) scale(0.55);
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.28);
  filter: blur(14px);
  opacity: 0;
}

.shadowIn {
  animation: shadowIn 0.4s ease forwards;
}

.shadowOut {
  animation: shadowOut 0.5s ease forwards;
}

/* =========================
   平面 logo
========================= */
.logo-flat {
  position: absolute;
  width: 300px;
  height: 300px;
  object-fit: contain;
  opacity: 0;
  transform: scale(0.92);
  transition:
    opacity 0.32s ease,
    transform 0.32s ease;
  filter: drop-shadow(0 12px 28px rgba(0, 0, 0, 0.18));
}

.logo-flat.show {
  opacity: 1;
  transform: scale(1);
}

.logo-flat.moveCorner {
  transform: translate(calc(80px - 50vw), calc(58px - 50vh)) scale(0.2);
  transition: transform 0.85s cubic-bezier(.72,.06,.2,.98), opacity 0.45s ease;
}

@media (max-width: 768px) {
  .logo-flat.moveCorner {
    transform: translate(calc(62px - 50vw), calc(46px - 50vh)) scale(0.2);
  }
}



/* 平面 logo 上的六点 */
.logo-flat span {
  position: absolute;
  width: 14px;
  height: 14px;
  background: #1e1e1e;
  border-radius: 50%;
}

.logo-flat span:nth-child(1) { top: 18px; left: 24px; }
.logo-flat span:nth-child(2) { top: 18px; right: 24px; }
.logo-flat span:nth-child(3) { top: 49px; left: 24px; }
.logo-flat span:nth-child(4) { top: 49px; right: 24px; }
.logo-flat span:nth-child(5) { bottom: 18px; left: 24px; }
.logo-flat span:nth-child(6) { bottom: 18px; right: 24px; }

/* =========================
   动画
========================= */
@keyframes diceDrop {
  0% {
    transform: translateY(-340px) rotateX(220deg) rotateY(160deg) rotateZ(-18deg);
  }
  72% {
    transform: translateY(12px) rotateX(20deg) rotateY(28deg) rotateZ(2deg);
  }
  100% {
    transform: translateY(0) rotateX(10deg) rotateY(16deg) rotateZ(0deg);
  }
}

@keyframes diceSettle {
  0% {
    transform: translateY(0) rotateX(10deg) rotateY(16deg) rotateZ(0deg) scaleY(1);
  }
  46% {
    transform: translateY(9px) rotateX(8deg) rotateY(12deg) rotateZ(0deg) scaleY(0.91) scaleX(1.03);
  }
  100% {
    transform: translateY(0) rotateX(10deg) rotateY(16deg) rotateZ(0deg) scaleY(1) scaleX(1);
  }
}

@keyframes shadowIn {
  0% {
    opacity: 0;
    transform: translateX(-50%) scale(0.55);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
}

@keyframes shadowOut {
  0% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) scale(0.5);
  }
}
</style>
