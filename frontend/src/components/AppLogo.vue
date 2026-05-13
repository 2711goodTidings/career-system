<template>
  <RouterLink class="app-logo" to="/" aria-label="返回首页">
    <img :src="diceLogo" alt="Career Planner Logo" class="app-logo__mark" />
    <span class="app-logo__text">SMART CAREER PLANNING</span>
  </RouterLink>
</template>

<script setup>
import diceLogo from '../assets/dice-logo.png'
</script>

<style scoped>
.app-logo {
  position: fixed;
  top: 28px;
  left: 34px;
  z-index: 120;
  width: 310px;
  height: 60px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: rgba(255, 255, 255, 0.92);
  text-decoration: none;
  background: rgba(147, 164, 193, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    0 6px 20px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
}

.app-logo__mark {
  width: 60px;
  height: 60px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.2));
}

.app-logo__text {
  color: inherit;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 2.2px;
  line-height: 1.35;
  white-space: nowrap;
}

.app-logo:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.9);
  outline-offset: 4px;
}

@media (max-width: 768px) {
  .app-logo {
    top: 14px;
    left: 14px;
    width: 230px;
    height: 48px;
    padding: 8px 12px;
    gap: 12px;
  }

  .app-logo__mark {
    width: 48px;
    height: 48px;
  }

  .app-logo__text {
    font-size: 10px;
    letter-spacing: 1.5px;
  }
}

@media (max-width: 480px) {
  .app-logo {
    width: 58px;
    padding: 5px;
    justify-content: center;
  }

  .app-logo__text {
    display: none;
  }
}
</style>
