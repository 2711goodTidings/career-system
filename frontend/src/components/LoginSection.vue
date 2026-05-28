<template>
  <section class="login-section">
    <div class="login-wrapper">
      <aside class="feature-panel">
        <p class="panel-kicker">SMART CAREER PLANNING</p>
        <h2>让计算机专业的成长路径，有据可循。</h2>
        <p class="panel-desc">
          从个人资料、综合能力到计算机能力画像，系统会把你的课程基础、项目经历、技术兴趣和目标路径串联起来，生成更清晰的方向匹配与年度规划。
        </p>

        <div class="feature-list">
          <article v-for="item in featureItems" :key="item.title" class="feature-line">
            <span>{{ item.index }}</span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </article>
        </div>
      </aside>

      <div class="section-divider" aria-hidden="true"></div>

      <div class="auth-panel">
        <template v-if="!userStore.isLogin">
          <div class="auth-tabs" role="tablist" aria-label="账号操作">
            <button
              type="button"
              class="auth-tab"
              :class="{ active: activeMode === 'login' }"
              @click="activeMode = 'login'"
            >
              登录
            </button>
            <button
              type="button"
              class="auth-tab"
              :class="{ active: activeMode === 'register' }"
              @click="activeMode = 'register'"
            >
              注册
            </button>
          </div>

          <form v-if="activeMode === 'login'" class="auth-form" @submit.prevent="handleLogin">
            <label class="line-input">
              <span>用户名</span>
              <input v-model="loginForm.username" type="text" placeholder="请输入用户名" />
            </label>

            <label class="line-input">
              <span>密码</span>
              <input v-model="loginForm.password" type="password" placeholder="请输入密码" />
            </label>

            <div class="tip" :class="tipClass" v-if="tipText">
              {{ tipText }}
            </div>

            <button class="submit-btn login-submit-btn" type="submit" :disabled="loading">
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </form>

          <form v-else class="auth-form" @submit.prevent="handleRegister">
            <label class="line-input">
              <span>用户名</span>
              <input v-model="regForm.username" type="text" placeholder="请输入用户名" />
            </label>

            <label class="line-input">
              <span>密码</span>
              <input v-model="regForm.password" type="password" placeholder="请输入密码" />
            </label>

            <div class="tip" :class="regTipClass" v-if="regTipText">
              {{ regTipText }}
            </div>

            <button class="submit-btn" type="submit" :disabled="loading">
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </form>
        </template>

        <div class="welcome-panel" v-else>
          <img
            class="welcome-avatar"
            :src="displayAvatar"
            alt="avatar"
            @error="handleAvatarError"
          />
          <p class="welcome-kicker">WELCOME BACK</p>
          <h2>欢迎回来，{{ userStore.username }}</h2>
          <button class="logout-btn" type="button" @click="handleLogout">
            退出登录
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { useUserStore } from '../stores/user'
import axios from '../utils/axios'

const API_BASE = 'http://127.0.0.1:8000'
const defaultAvatar =
  'https://cdn.jsdelivr.net/gh/evjdent/SuperTinyIcons/images/svg/user.svg'

const userStore = useUserStore()
const loading = ref(false)
const activeMode = ref('login')
const profileAvatar = ref('')

const loginForm = reactive({ username: '', password: '' })
const tipText = ref('')
const tipClass = ref('')

const regForm = reactive({ username: '', password: '' })
const regTipText = ref('')
const regTipClass = ref('')

const featureItems = [
  {
    index: '01',
    title: '学生画像',
    desc: '整理年级、专业方向、成绩英语、城市偏好和目标倾向。'
  },
  {
    index: '02',
    title: '双维评估',
    desc: '同时评估综合能力与编程、算法、工程实践等计算机能力。'
  },
  {
    index: '03',
    title: '方向匹配',
    desc: '匹配后端、前端、AI、数据、安全、测试等技术方向。'
  },
  {
    index: '04',
    title: '年度规划',
    desc: '结合推荐路径生成剩余大学阶段的学习、项目和求职安排。'
  }
]

const normalizeAvatarUrl = (avatar) => {
  if (!avatar) return ''
  if (/^(https?:|data:|blob:)/.test(avatar)) return avatar
  return `${API_BASE}${avatar.startsWith('/') ? '' : '/'}${avatar}`
}

const displayAvatar = computed(() => {
  return profileAvatar.value || normalizeAvatarUrl(userStore.avatar) || defaultAvatar
})

const loadProfileAvatar = async (userId = userStore.userId) => {
  const id = Number(userId)
  if (!Number.isFinite(id) || id <= 0) return

  try {
    const res = await fetch(`${API_BASE}/profile/${id}`)
    if (res.status === 404) return
    if (!res.ok) return

    const data = await res.json()
    const avatar = normalizeAvatarUrl(data.avatar || data.avatar_url)
    if (avatar) {
      profileAvatar.value = avatar
      userStore.setAvatar?.(avatar)
    }
  } catch (error) {
    console.warn('加载头像失败', error)
  }
}

const handleAvatarError = (event) => {
  if (event.target.src !== defaultAvatar) {
    event.target.src = defaultAvatar
  }
}

const emit = defineEmits(['login-success'])

const handleLogout = () => {
  userStore.logout()
  profileAvatar.value = ''
  loginForm.username = ''
  loginForm.password = ''
  regForm.username = ''
  regForm.password = ''
  tipText.value = ''
  tipClass.value = ''
  regTipText.value = ''
  regTipClass.value = ''
  activeMode.value = 'login'
}

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

    const avatar = normalizeAvatarUrl(res.data.avatar || res.data.avatar_url)

    userStore.login({
      userId: res.data.user_id,
      username: res.data.username,
      avatar
    })

    profileAvatar.value = avatar
    loadProfileAvatar(res.data.user_id)
    emit('login-success')
  } catch (err) {
    tipText.value = err.response?.data?.detail || '登录失败'
    tipClass.value = 'error'
  } finally {
    loading.value = false
  }
}

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
    setTimeout(() => {
      activeMode.value = 'login'
    }, 900)
  } catch (err) {
    regTipText.value = err.response?.data?.detail || '注册失败'
    regTipClass.value = 'error'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (userStore.isLogin) {
    loadProfileAvatar()
  }
})
</script>

<style scoped>
.login-section {
  position: relative;
  width: 100%;
  min-height: 100vh;
  padding: 72px 20px 72px 224px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background: #E7E8E4;
  color: #3f4f5c;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
}

.login-wrapper {
  width: min(1320px, 100%);
  min-height: 720px;
  display: grid;
  grid-template-columns: minmax(0, 4fr) 1px minmax(0, 6fr);
  gap: clamp(34px, 4vw, 56px);
  align-items: stretch;
}

.feature-panel,
.auth-panel {
  min-width: 0;
}

.feature-panel {
  grid-column: 1;
  padding: 10px 0 0;
  display: flex;
  flex-direction: column;
  text-align: left;
}

.panel-kicker {
  margin: 0 0 16px;
  color: rgba(35, 55, 76, 0.66);
  font-size: 12px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.2em;
}

.feature-panel h2 {
  width: min(540px, 100%);
  margin: 0;
  color: #24384c;
  font-size: clamp(36px, 4vw, 60px);
  font-weight: 600;
  line-height: 1.06;
  letter-spacing: 0;
}

.panel-desc {
  width: min(560px, 100%);
  margin: 26px 0 50px;
  color: rgba(36, 56, 76, 0.82);
  font-size: 17px;
  line-height: 1.82;
}

.feature-list {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.feature-line {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(36, 56, 76, 0.16);
}

.feature-line > span {
  color: rgba(36, 56, 76, 0.42);
  font-size: 14px;
  letter-spacing: 0.14em;
  line-height: 1.6;
  text-align: left;
}

.feature-line h3 {
  margin: 0 0 6px;
  color: #24384c;
  font-size: 21px;
  font-weight: 600;
  line-height: 1.18;
}

.feature-line p {
  margin: 0;
  color: rgba(36, 56, 76, 0.76);
  font-size: 15px;
  line-height: 1.68;
}

.section-divider {
  position: absolute;
  left: var(--main-divider-left, clamp(0px, 49%, 763px));
  top: 72px;
  bottom: 0;
  width: 1px;
  background: rgba(63, 79, 92, 0.55);
}

.auth-panel {
  grid-column: 3;
  padding: 36px 0 0 10px;
  display: flex;
  flex-direction: column;
  transform: translateY(48px);
}

.auth-tabs {
  display: flex;
  align-items: flex-end;
  gap: 32px;
  margin-bottom: 86px;
}

.auth-tab {
  padding: 0 0 14px;
  border: 0;
  border-bottom: 1px solid transparent;
  background: transparent;
  color: rgba(63, 79, 92, 0.24);
  font: inherit;
  font-size: clamp(28px, 3.4vw, 42px);
  line-height: 1;
  font-weight: 500;
  cursor: pointer;
}

.auth-tab.active {
  color: #3f4f5c;
  border-bottom-color: rgba(63, 79, 92, 0.65);
}

.auth-form {
  width: 100%;
  flex: 1;
  padding-top: 26px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.line-input {
  display: grid;
  gap: 14px;
}

.line-input span {
  color: #3f4f5c;
  font-size: 14px;
  line-height: 1;
}

.line-input input {
  width: 100%;
  padding: 0 0 14px;
  border: 0;
  border-bottom: 1px solid rgba(63, 79, 92, 0.75);
  background: transparent;
  color: #3f4f5c;
  border-radius: 0;
  outline: none;
  font: inherit;
  font-size: 24px;
  line-height: 1.1;
}

.line-input input::placeholder {
  color: rgba(63, 79, 92, 0.52);
}

.tip {
  width: fit-content;
  max-width: 100%;
  padding: 8px 0;
  font-size: 14px;
  line-height: 1.4;
}

.tip.success {
  color: #1f7a56;
}

.tip.error {
  color: #b4334a;
}

.submit-btn {
  width: 118px;
  height: 46px;
  margin-top: auto;
  margin-bottom: 0;
  align-self: flex-end;
  justify-self: end;
  transform: translate(80px, -40px);
  border: 0;
  background: #3f4f5c;
  color: #ffffff;
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
}

.submit-btn:hover:not(:disabled) {
  background: #34424d;
}

.submit-btn:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.welcome-panel {
  flex: 1;
  min-height: 100%;
  padding-top: 92px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  color: #3f4f5c;
}

.welcome-avatar {
  width: 300px;
  height: 300px;
  border-radius: 0;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(63, 79, 92, 0.22);
  box-shadow: 0 14px 30px rgba(63, 79, 92, 0.12);
}

.welcome-kicker {
  margin: 34px 0 14px;
  color: rgba(63, 79, 92, 0.58);
  font-size: 15px;
  letter-spacing: 0.16em;
}

.welcome-panel h2 {
  margin: 0;
  font-size: clamp(30px, 3.6vw, 46px);
  font-weight: 500;
  line-height: 1.12;
}

.logout-btn {
  width: 118px;
  height: 46px;
  margin-top: 48px;
  align-self: flex-end;
  transform: translate(80px, 90px);
  border: 1px solid rgba(63, 79, 92, 0.68);
  background: transparent;
  color: #3f4f5c;
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
}

.logout-btn:hover {
  background: #3f4f5c;
  color: #ffffff;
}

@media (max-width: 1080px) {
  .login-wrapper {
    grid-template-columns: 1fr;
    gap: 34px;
  }

  .section-divider {
    position: static;
    width: 100%;
    height: 1px;
  }

  .feature-panel,
  .auth-panel {
    grid-column: auto;
  }

  .auth-panel {
    padding: 0;
    transform: none;
  }

  .auth-tabs {
    margin-bottom: 68px;
  }
}

@media (max-width: 680px) {
  .login-section {
    padding: 64px 18px;
  }

  .login-wrapper {
    min-height: auto;
  }

  .feature-panel h2 {
    font-size: 36px;
  }

  .panel-desc {
    margin: 22px 0 30px;
    font-size: 17px;
  }

  .feature-list {
    gap: 14px;
  }

  .auth-tabs {
    gap: 20px;
    margin-bottom: 38px;
  }

  .auth-tab {
    font-size: 30px;
  }

  .auth-form {
    padding-top: 14px;
    gap: 24px;
  }

  .line-input input {
    font-size: 21px;
  }

  .submit-btn {
    width: 100%;
    height: 52px;
    margin-bottom: 0;
    align-self: stretch;
    justify-self: stretch;
    transform: none;
  }

  .welcome-panel {
    padding-top: 28px;
  }

  .welcome-avatar {
    width: min(220px, 100%);
    height: auto;
    aspect-ratio: 1;
  }

  .welcome-panel h2 {
    font-size: 30px;
  }

  .logout-btn {
    width: 100%;
    height: 52px;
    margin-top: 34px;
    align-self: stretch;
    transform: none;
  }
}
</style>
