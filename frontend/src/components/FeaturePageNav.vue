<template>
  <nav class="feature-page-nav" aria-label="功能页面导航">
    <button
      v-for="(item, index) in navItems"
      :key="item.path"
      class="nav-btn"
      :class="{ active: item.key === current }"
      type="button"
      @click="go(item.path)"
    >
      <span class="nav-en">{{ item.en }}</span>
      <span class="nav-cn">{{ item.label }}</span>
    </button>

    <button class="nav-btn" type="button" @click="go('/')">
      <span class="nav-en">HOME</span>
      <span class="nav-cn">返回首页</span>
    </button>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  current: {
    type: String,
    required: true
  }
})

const router = useRouter()

const navItems = [
  { key: 'profile', en: 'PROFILE', label: '个人信息', path: '/profile' },
  { key: 'ability', en: 'ABILITY', label: '能力评估', path: '/ability' },
  { key: 'career', en: 'CAREER', label: '职业规划', path: '/career' },
  { key: 'planning', en: 'PLANNING', label: '成长规划', path: '/planning' }
]

function go(path) {
  router.push(path)
}
</script>

<style scoped>
.feature-page-nav {
  position: fixed;
  top: 22px;
  right: 22px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
}

.nav-btn {
  border: none;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid transparent;
  color: #1f5d95;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  cursor: pointer;
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
}

.nav-btn {
  width: 92px;
  height: 54px;
  padding: 9px 11px;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr;
  gap: 5px;
  align-items: start;
  overflow: hidden;
  text-align: left;
  transition:
    width 0.42s cubic-bezier(.22,.98,.24,1),
    box-shadow 0.25s ease,
    border-color 0.25s ease,
    background 0.25s ease;
}

.nav-btn:hover,
.nav-btn.active:hover {
  width: 132px;
  background: #f5f5f3;
  border-color: transparent;
  box-shadow: 0 20px 38px rgba(53, 86, 138, 0.16);
}

.nav-btn.active {
  background: rgba(245, 245, 243, 0.88);
  border-color: transparent;
}

.nav-en {
  grid-column: 1;
  color: #1f5d95;
  font-size: 12px;
  line-height: 1;
  letter-spacing: 1.4px;
  white-space: nowrap;
}

.nav-cn {
  grid-column: 1 / -1;
  align-self: end;
  color: #1f5d95;
  font-size: 22px;
  line-height: 1.05;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(10px);
  transition: opacity 0.2s ease, transform 0.25s ease;
}

.nav-btn:hover .nav-cn,
.nav-btn.active:hover .nav-cn {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 768px) {
  .feature-page-nav {
    top: 14px;
    right: 14px;
  }

  .nav-btn {
    width: 78px;
    height: 48px;
    padding: 8px 9px;
  }

  .nav-btn:hover,
  .nav-btn.active:hover {
    width: 118px;
  }

  .nav-en {
    font-size: 10px;
  }

  .nav-cn {
    font-size: 18px;
  }
}
</style>
