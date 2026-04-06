<template>
  <section class="login-section">
    <div class="login-wrapper" v-if="!userStore.isLogin">
      <div class="login-card">
        <div class="card-head">
          <h2>登录账号</h2>
          <p>登录后解锁全部职业规划功能</p>
        </div>

        <div class="input-item">
          <input
            v-model="loginForm.username"
            type="text"
            placeholder="用户名"
          />
        </div>
        <div class="input-item">
          <input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
          />
        </div>

        <div class="tip" :class="tipClass" v-if="tipText">
          {{ tipText }}
        </div>

        <button class="btn-login" @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <button class="btn-reg" @click="showRegModal = true">
          注册新账号
        </button>
      </div>
    </div>

    <div class="logged-info" v-else>
      ✅ 已登录 | 欢迎回来，{{ userStore.username }}
    </div>

    <div class="modal-mask" v-show="showRegModal" @click="showRegModal = false">
      <div class="modal" @click.stop>
        <h3>注册账号</h3>
        <div class="input-item">
          <input v-model="regForm.username" placeholder="用户名" />
        </div>
        <div class="input-item">
          <input v-model="regForm.password" type="password" placeholder="密码" />
        </div>
        <div class="tip" :class="regTipClass" v-if="regTipText">
          {{ regTipText }}
        </div>
        <div class="modal-btns">
          <button @click="showRegModal = false">取消</button>
          <button @click="handleRegister" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '../stores/user'
import axios from '../utils/axios'

const userStore = useUserStore()
const loading = ref(false)
const showRegModal = ref(false)

const loginForm = reactive({ username: '', password: '' })
const tipText = ref('')
const tipClass = ref('')

const regForm = reactive({ username: '', password: '' })
const regTipText = ref('')
const regTipClass = ref('')

const emit = defineEmits(['login-success'])

// 登录
const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    tipText.value = '请输入账号密码'
    tipClass.value = 'error'
    return
  }
  loading.value = true
  tipText.value = ''
  try {
    const res = await axios.post('/auth/login', loginForm)
    tipText.value = '登录成功！'
    tipClass.value = 'success'

    userStore.login({
      userId: res.data.user_id,
      username: res.data.username
    })

    emit('login-success')
  } catch (err) {
    tipText.value = err.response?.data?.detail || '登录失败'
    tipClass.value = 'error'
  } finally {
    loading.value = false
  }
}

// 注册
const handleRegister = async () => {
  if (!regForm.username || !regForm.password) {
    regTipText.value = '请完整填写'
    regTipClass.value = 'error'
    return
  }
  loading.value = true
  regTipText.value = ''
  try {
    await axios.post('/auth/register', regForm)
    regTipText.value = '注册成功！请登录'
    regTipClass.value = 'success'
    setTimeout(() => showRegModal.value = false, 1000)
  } catch (err) {
    regTipText.value = err.response?.data?.detail || '注册失败'
    regTipClass.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-section {
  width: 100%;
  min-height: 100vh;
  background: #d9d6d1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}
.login-wrapper {
  width: 100%;
  max-width: 440px;
}
.login-card {
  background: #ffffff;
  border-radius: 22px;
  padding: 50px 42px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}
.card-head {
  text-align: center;
  margin-bottom: 36px;
}
.card-head h2 {
  font-size: 28px;
  color: #35568a;
  margin-bottom: 8px;
}
.card-head p {
  color: #8b9bc1;
  font-size: 14px;
}
.input-item {
  margin-bottom: 20px;
}
.input-item input {
  width: 100%;
  padding: 15px 18px;
  border: 1px solid #e0e6ed;
  border-radius: 14px;
  font-size: 15px;
  outline: none;
  box-sizing: border-box;
}
.input-item input:focus {
  border-color: #35568a;
}
.tip {
  text-align: center;
  font-size: 13px;
  margin-bottom: 16px;
  padding: 6px;
  border-radius: 6px;
}
.tip.success {
  color: #10b981;
  background: rgba(16, 185, 129, 0.08);
}
.tip.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
}
.btn-login, .btn-reg {
  width: 100%;
  padding: 15px;
  border-radius: 14px;
  font-size: 15px;
  margin-bottom: 12px;
  border: none;
  cursor: pointer;
}
.btn-login {
  background: #35568a;
  color: white;
}
.btn-reg {
  background: transparent;
  color: #35568a;
  border: 1px solid #35568a;
}
.btn-login:disabled {
  opacity: 0.6;
}
.logged-info {
  padding: 20px 40px;
  background: rgba(53, 86, 138, 0.1);
  border-radius: 14px;
  color: #35568a;
  font-size: 15px;
}
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 20px;
  padding: 36px;
}
.modal h3 {
  text-align: center;
  color: #35568a;
  margin-bottom: 24px;
}
.modal-btns {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.modal-btns button {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
}
.modal-btns button:nth-child(2) {
  background: #35568a;
  color: white;
}
</style>