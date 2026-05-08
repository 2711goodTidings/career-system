<template>
  <section class="login-section">
    <div class="login-wrapper">
      <aside class="feature-panel">
        <p class="panel-kicker">SMART CAREER SYSTEM</p>
        <h2>把职业规划这件事，拆成几步慢慢做清楚。</h2>
        <p class="panel-desc">
          系统会先理解你的基本信息，再通过能力评估建立画像，随后生成职业推荐，并接入大模型整理成长路径。
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

            <button class="submit-btn" type="submit" :disabled="loading">
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
    title: '个人信息',
    desc: '整理专业背景、兴趣偏好、已有技能和职业目标。'
  },
  {
    index: '02',
    title: '能力评估',
    desc: '从逻辑、创新、沟通、学习等维度生成能力画像。'
  },
  {
    index: '03',
    title: '职业推荐',
    desc: '结合个人资料和能力结果，匹配更适合的发展方向。'
  },
  {
    index: '04',
    title: '成长规划',
    desc: '接入大模型规划成长路径，拆解阶段目标和补强任务。'
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
  margin: 0 0 18px;
  color: rgba(63, 79, 92, 0.62);
  font-size: 13px;
  letter-spacing: 0.18em;
}

.feature-panel h2 {
  width: min(500px, 100%);
  margin: 0;
  color: #3f4f5c;
  font-size: clamp(34px, 4vw, 56px);
  font-weight: 500;
  line-height: 1.08;
  letter-spacing: 0;
}

.panel-desc {
  width: min(520px, 100%);
  margin: 24px 0 48px;
  color: #3f4f5c;
  font-size: 18px;
  line-height: 1.78;
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
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(63, 79, 92, 0.18);
}

.feature-line > span {
  color: rgba(63, 79, 92, 0.48);
  font-size: 14px;
  letter-spacing: 0.14em;
  line-height: 1.6;
  text-align: left;
}

.feature-line h3 {
  margin: 0 0 6px;
  color: #3f4f5c;
  font-size: 22px;
  font-weight: 500;
  line-height: 1.18;
}

.feature-line p {
  margin: 0;
  color: #3f4f5c;
  font-size: 15px;
  line-height: 1.7;
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
  margin-bottom: 64px;
  align-self: start;
  justify-self: start;
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
}
</style>
