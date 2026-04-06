<template>
  <section class="section login-section">
    <div class="login-left">
      <h2>登录系统</h2>
      <p>登录后解锁功能区与 AI 规划区</p>
    </div>

    <div class="login-right">
      <div class="login-form">
        <input type="text" placeholder="Username" />
        <input type="password" placeholder="Password" />

        <div class="login-actions">
          <button class="login-btn" @click="handleLogin">LOGIN</button>
         
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps({
  functionRef: {
    type: Object,
    default: null
  },
  onLoginSuccess: {
    type: Function,
    default: null
  }
})

const userStore = useUserStore()
const handleLogin = async () => {
  userStore.login()

  if (props.onLoginSuccess) {
    props.onLoginSuccess()
  }

  await nextTick()

  props.functionRef?.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}


</script>

<style scoped>
.section {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.login-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 40px;
  padding: 80px 60px;
  background: #d9d6d1;
}

.login-left h2 {
  font-size: 56px;
  color: #35568a;
  margin-bottom: 16px;
}

.login-left p {
  color: #35568a;
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
  border-bottom: 1px solid #35568a;
  outline: none;
  background: transparent;
  color: #35568a;
  font-size: 16px;
}

.login-form input::placeholder {
  color: rgba(53, 86, 138, 0.55);
}

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


@media (max-width: 1024px) {
  .login-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .login-section {
    padding: 60px 24px;
  }

  .login-left h2 {
    font-size: 40px;
  }

  .login-actions {
    flex-direction: column;
  }
}
</style>