<template>
  <div class="page">
    <!-- 1. 首页展示区 -->
    <section class="section hero-section">
      <h1 class="hero-title">大学生智能职业规划系统</h1>
      <p class="hero-desc">首页展示区</p>
    </section>

    <!-- 2. 登录区 -->
    <section class="section login-section">
      <h2>登录区</h2>
      <p>这里后面会换成真正的登录表单</p>
      <button @click="handleLogin">模拟登录</button>
    </section>

    <!-- 3. 功能区：登录后才显示 -->
    <section v-if="userStore.isLogin" class="section function-section">
      <h2>功能区</h2>
      <div class="card-list">
        <div class="card">功能 1</div>
        <div class="card">功能 2</div>
        <div class="card">功能 3</div>
        <div class="card">功能 4</div>
      </div>
    </section>

    <!-- 4. AI规划展示区：登录后才显示 -->
    <section v-if="userStore.isLogin" class="section ai-section">
      <h2>大模型规划展示区</h2>
      <p>这里后面放 AI 规划内容</p>
    </section>
  </div>
</template>

<script setup>
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const handleLogin = () => {
  userStore.login()
}
</script>

<style scoped>
.page {
  width: 100%;
  min-height: 100vh;
  background: #d9d8d1;
}

.section {
  min-height: 100vh;
  padding: 60px 40px;
  border-bottom: 1px solid #bfc2d3;
}

.hero-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-title {
  font-size: 64px;
  color: #2338c4;
  margin-bottom: 20px;
}

.hero-desc {
  font-size: 20px;
  color: #2338c4;
}

.login-section h2,
.function-section h2,
.ai-section h2 {
  color: #2338c4;
  margin-bottom: 20px;
}

button {
  padding: 12px 24px;
  border: none;
  background: #2338c4;
  color: white;
  cursor: pointer;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 30px;
}

.card {
  background: white;
  min-height: 140px;
  padding: 20px;
  border: 1px solid #c8ccdf;
  font-size: 22px;
  color: #2338c4;
}
</style>