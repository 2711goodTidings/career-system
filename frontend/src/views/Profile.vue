<template>
  <div class="profile-page" :style="{ backgroundImage: `url(${profileBackground})` }">
    <FeaturePageNav current="profile" />

    <main class="book-stage">
      <div class="page-count">{{ currentSpread + 1 }}/2</div>

      <form class="profile-book" @submit.prevent="handleSubmit">
        <section
          class="book-page left-page"
          :class="{ 'soft-flip': currentSpread === 1 }"
          :style="{ '--paper-bg': `url(${paperBackground})` }"
        >
          <template v-if="currentSpread === 0">
            <div class="profile-cover">
              <div class="page-number">01</div>
              <h1>PROFILE</h1>
              <div class="avatar-sheet">
                <img :src="avatarPreview || defaultAvatar" alt="avatar" />
                <label class="avatar-upload">
                  更换头像
                  <input
                    class="hidden-input"
                    type="file"
                    accept="image/*"
                    @change="handleAvatarChange"
                  />
                </label>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="spread-panel">
              <div class="page-number">03</div>
              <button
                type="button"
                class="corner-turn prev-turn"
                @click="currentSpread = 0"
                aria-label="上一页"
              >
                <span aria-hidden="true"></span>
              </button>
              <div class="long-field">
                <label>个人简介</label>
                <textarea
                  v-model="form.bio"
                  rows="8"
                  placeholder="请输入你的兴趣、能力特点、职业倾向等"
                ></textarea>
              </div>
              <div class="long-field">
                <label>兴趣方向</label>
                <textarea
                  v-model="form.interest"
                  rows="8"
                  placeholder="例如：人工智能、前端开发、数据分析、考研深造"
                ></textarea>
              </div>
            </div>
          </template>
        </section>

        <section
          class="book-page right-page"
          :class="{ 'soft-flip': currentSpread === 1 }"
          :style="{ '--paper-bg': `url(${paperBackground})` }"
        >
          <template v-if="currentSpread === 0">
            <div class="basic-page">
              <div class="page-number">02</div>
              <button
                type="button"
                class="corner-turn next-turn"
                @click="currentSpread = 1"
                aria-label="下一页"
              >
                <span aria-hidden="true"></span>
              </button>
              <div class="field-list">
                <div class="form-item">
                  <label>姓名</label>
                  <input v-model="form.username" type="text" placeholder="请输入姓名" />
                </div>

                <div class="form-item">
                  <label>性别</label>
                  <select v-model="form.gender">
                    <option value="">请选择性别</option>
                    <option value="男">男</option>
                    <option value="女">女</option>
                  </select>
                </div>

                <div class="form-item">
                  <label>年龄</label>
                  <input v-model="form.age" type="number" placeholder="请输入年龄" />
                </div>

                <div class="form-item">
                  <label>电话</label>
                  <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入11位手机号" />
                </div>

                <div class="form-item">
                  <label>学校</label>
                  <input v-model="form.school" type="text" placeholder="请输入学校" />
                </div>

                <div class="form-item">
                  <label>专业</label>
                  <input v-model="form.major" type="text" placeholder="请输入专业" />
                </div>

                <div class="form-item">
                  <label>年级</label>
                  <select v-model="form.grade">
                    <option value="">请选择年级</option>
                    <option value="大一">大一</option>
                    <option value="大二">大二</option>
                    <option value="大三">大三</option>
                    <option value="大四">大四</option>
                    <option value="研究生">研究生</option>
                  </select>
                </div>

                <div class="form-item">
                  <label>邮箱</label>
                  <input v-model="form.email" type="email" placeholder="请输入邮箱" />
                </div>

                <div class="form-item full">
                  <label>目标倾向</label>
                  <select v-model="form.target_preference">
                    <option value="">请选择目标倾向</option>
                    <option value="就业">就业</option>
                    <option value="考研">考研</option>
                    <option value="考公">考公</option>
                    <option value="出国">出国</option>
                  </select>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="spread-panel">
              <div class="page-number">04</div>
              <div class="long-field">
                <label>已有技能</label>
                <textarea
                  v-model="form.skills"
                  rows="8"
                  placeholder="例如：Python、Java、Vue、MySQL、沟通表达"
                ></textarea>
              </div>
              <div class="long-field">
                <label>职业目标</label>
                <textarea
                  v-model="form.career_goal"
                  rows="8"
                  placeholder="例如：希望进入互联网公司，从事 AI 研发或数据分析相关工作"
                ></textarea>
              </div>
            </div>
          </template>
        </section>
      </form>

      <div class="book-actions">
        <div class="completion-box">
          <span>PROFILE COMPLETION</span>
          <strong>{{ profileCompletion }}%</strong>
        </div>
        <button type="button" class="save-btn" :disabled="isSaving" @click="handleSubmit">
          {{ isSaving ? '保存中...' : '保存档案' }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import profileBackground from '../assets/profile_background.jpg'
import paperBackground from '../assets/profile_background1.jpg'
import { useUserStore } from '../stores/user.js'

const userStore = useUserStore()

const API_BASE = 'http://127.0.0.1:8000'
const defaultAvatar =
  'https://cdn.jsdelivr.net/gh/evjdent/SuperTinyIcons/images/svg/user.svg'

const currentSpread = ref(0)
const avatarPreview = ref('')
const isSaving = ref(false)
const isLoadingProfile = ref(false)

const form = reactive({
  username: '',
  gender: '',
  age: '',
  phone: '',
  email: '',
  school: '',
  major: '',
  grade: '',
  bio: '',
  interest: '',
  skills: '',
  target_preference: '',
  career_goal: ''
})

const profileCompletion = computed(() => {
  const fields = [
    form.username,
    form.gender,
    form.age,
    form.phone,
    form.email,
    form.school,
    form.major,
    form.grade,
    form.bio,
    form.interest,
    form.skills,
    form.target_preference,
    form.career_goal
  ]
  const filled = fields.filter((item) => String(item ?? '').trim() !== '').length
  return Math.round((filled / fields.length) * 100)
})

const validatePhone = (phone) => /^1\d{10}$/.test(phone)
const validateEmail = (email) =>
  /^[A-Za-z0-9._%+-]+@(163\.com|qq\.com|gmail\.com)$/.test(email)

const getCurrentUserId = () => {
  const id = Number(userStore.userId)
  return Number.isFinite(id) && id > 0 ? id : null
}

const buildProfilePayload = (includeUserId = false) => {
  const payload = {
    real_name: form.username || null,
    gender: form.gender || null,
    school: form.school || null,
    major: form.major || null,
    grade: form.grade || null,
    age: form.age === '' ? null : Number(form.age),
    phone: form.phone || null,
    email: form.email || null,
    bio: form.bio || null,
    interest: form.interest || null,
    skills: form.skills || null,
    target_preference: form.target_preference || null,
    career_goal: form.career_goal || null
  }

  if (includeUserId) {
    payload.user_id = getCurrentUserId()
  }

  return payload
}

const loadProfile = async () => {
  const userId = getCurrentUserId()
  if (!userId) {
    console.warn('没有获取到 userId，无法加载个人信息')
    return
  }

  isLoadingProfile.value = true

  try {
    const res = await fetch(`${API_BASE}/profile/${userId}`)

    if (res.status === 404) {
      console.log('该用户还没有个人信息记录')
      return
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '加载个人信息失败')
    }

    const data = await res.json()

    form.username = data.real_name || ''
    form.gender = data.gender || ''
    form.age = data.age ?? ''
    form.phone = data.phone || ''
    form.email = data.email || ''
    form.school = data.school || ''
    form.major = data.major || ''
    form.grade = data.grade || ''
    form.bio = data.bio || ''
    form.interest = data.interest || ''
    form.skills = data.skills || ''
    form.target_preference = data.target_preference || ''
    form.career_goal = data.career_goal || ''

    if (data.avatar) {
      avatarPreview.value = `${API_BASE}${data.avatar}`
    }
  } catch (error) {
    console.error('加载个人信息失败：', error)
    alert(`加载个人信息失败：${error.message}`)
  } finally {
    isLoadingProfile.value = false
  }
}

const handleSubmit = async () => {
  const userId = getCurrentUserId()
  if (!userId) {
    alert('未获取到用户ID，请先登录')
    return
  }

  if (form.phone && !validatePhone(form.phone)) {
    alert('手机号必须是11位且以1开头')
    return
  }

  if (form.email && !validateEmail(form.email)) {
    alert('邮箱仅支持 163.com / qq.com / gmail.com')
    return
  }

  isSaving.value = true

  try {
    const checkRes = await fetch(`${API_BASE}/profile/${userId}`)

    let res

    if (checkRes.status === 404) {
      res = await fetch(`${API_BASE}/profile/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(buildProfilePayload(true))
      })
    } else if (checkRes.ok) {
      res = await fetch(`${API_BASE}/profile/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(buildProfilePayload(false))
      })
    } else {
      const err = await checkRes.json().catch(() => ({}))
      throw new Error(err.detail || '检查个人信息失败')
    }

    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      throw new Error(data.detail || '保存失败')
    }

    alert('保存成功')
    console.log('保存结果：', data)
  } catch (error) {
    console.error('保存失败：', error)
    alert(`保存失败：${error.message}`)
  } finally {
    isSaving.value = false
  }
}

const handleAvatarChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  avatarPreview.value = URL.createObjectURL(file)

  const userId = getCurrentUserId()
  if (!userId) {
    alert('未获取到用户ID，请先登录')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE}/profile/upload-avatar/${userId}`, {
      method: 'POST',
      body: formData
    })

    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      throw new Error(data.detail || '头像上传失败')
    }

    if (data.avatar_url) {
      avatarPreview.value = `${API_BASE}${data.avatar_url}`
    }

    console.log('头像上传成功：', data)
  } catch (error) {
    console.error('头像上传失败：', error)
    alert(`头像上传失败：${error.message}`)
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.profile-page {
  min-height: 100vh;
  overflow: hidden;
  background-color: #8495A9;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  color: #1f2529;
  font-family: "Times New Roman", "Georgia", "PingFang SC", "Microsoft YaHei", serif;
}

.book-stage {
  min-height: 100vh;
  padding: 86px 54px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.page-count {
  position: fixed;
  top: 26px;
  right: 34px;
  width: 78px;
  height: 78px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #f2f0ea;
  display: grid;
  place-items: center;
  font-size: 28px;
  z-index: 20;
  backdrop-filter: blur(8px);
}

.profile-book {
  width: min(1240px, 100%);
  min-height: 740px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  position: relative;
  filter: drop-shadow(0 28px 34px rgba(0, 0, 0, 0.46));
  perspective: 1600px;
}

.profile-book::before {
  content: "";
  position: absolute;
  inset: 0 50% 0 auto;
  width: 24px;
  transform: translateX(50%);
  z-index: 8;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.2),
    rgba(255, 255, 255, 0.12) 42%,
    rgba(0, 0, 0, 0.28)
  );
  pointer-events: none;
}

.book-page {
  min-height: 740px;
  padding: 54px 40px 42px;
  position: relative;
  overflow: hidden;
  transition: transform 0.45s ease, background 0.45s ease;
}

.book-page::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    var(--paper-bg),
    linear-gradient(rgba(0, 0, 0, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035), transparent 18%, rgba(0, 0, 0, 0.04));
  background-size: cover, 100% 19px, 100% 100%;
  background-position: center, 0 0, 0 0;
  mix-blend-mode: multiply;
  opacity: 0.8;
}

.left-page {
  background: #efeee9;
  border-radius: 2px 0 0 2px;
}

.right-page {
  background: #93A4C1;
  border-radius: 0 2px 2px 0;
  color: #f1eee7;
}

.book-page.soft-flip {
  transform: rotateY(0.8deg);
}

.profile-cover {
  height: 100%;
  min-height: 635px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateX(-34px);
}

.profile-cover h1 {
  margin: 0;
  position: absolute;
  left: -84px;
  top: 49%;
  transform: translateY(-50%) rotate(-90deg);
  transform-origin: center;
  color: #202322;
  font-size: 88px;
  line-height: 0.9;
  letter-spacing: 2px;
  font-weight: 600;
  z-index: 5;
}

.avatar-sheet {
  width: min(410px, 84%);
  aspect-ratio: 0.82;
  background: #7ea0c7;
  transform: translateX(58px);
  position: relative;
  z-index: 2;
  box-shadow: 0 14px 26px rgba(0, 0, 0, 0.18);
}

.avatar-sheet img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  mix-blend-mode: luminosity;
  opacity: 0.88;
}

.avatar-upload {
  position: absolute;
  right: 18px;
  bottom: 16px;
  color: #111517;
  border: none;
  padding: 0;
  font-size: 11px;
  cursor: pointer;
  background: transparent;
  text-shadow: none;
}

.hidden-input {
  display: none;
}

.page-number {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%) rotate(-90deg);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
  z-index: 4;
}

.right-page .page-number {
  left: auto;
  right: 10px;
  color: #f1eee7;
}

.corner-turn {
  position: absolute;
  z-index: 6;
  border: none;
  background: transparent;
  color: inherit;
  width: 46px;
  height: 28px;
  padding: 0;
  cursor: pointer;
  opacity: 0.78;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.corner-turn span {
  position: absolute;
  left: 7px;
  right: 7px;
  top: 50%;
  height: 1.5px;
  background: currentColor;
  transform: translateY(-50%);
}

.corner-turn span::before,
.corner-turn span::after {
  content: "";
  position: absolute;
  width: 11px;
  height: 1.5px;
  background: currentColor;
  top: 0;
}

.corner-turn:hover {
  opacity: 1;
}

.next-turn {
  right: 34px;
  bottom: 30px;
  color: #f1eee7;
}

.next-turn span::before,
.next-turn span::after {
  right: 0;
  transform-origin: right center;
}

.next-turn span::before {
  transform: rotate(34deg);
}

.next-turn span::after {
  transform: rotate(-34deg);
}

.next-turn:hover {
  transform: translateX(5px);
}

.prev-turn {
  left: 34px;
  bottom: 30px;
  color: #252b29;
}

.prev-turn span::before,
.prev-turn span::after {
  left: 0;
  transform-origin: left center;
}

.prev-turn span::before {
  transform: rotate(-34deg);
}

.prev-turn span::after {
  transform: rotate(34deg);
}

.prev-turn:hover {
  transform: translateX(-5px);
}

.page-title {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 34px;
  align-items: baseline;
  margin: 84px 38px 34px 0;
}

.page-title span {
  font-size: 12px;
  line-height: 1.1;
  font-weight: 700;
  color: rgba(241, 238, 231, 0.82);
}

.page-title strong {
  min-width: 0;
  font-size: 20px;
  font-weight: 500;
  color: rgba(241, 238, 231, 0.72);
  word-break: break-word;
}

.field-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 28px 34px;
  padding: 78px 52px 0 0;
}

.form-item,
.long-field {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.form-item.full {
  grid-column: 1 / -1;
}

label {
  margin-bottom: 9px;
  font-size: 13px;
  font-weight: 700;
  color: inherit;
}

.form-item label,
.long-field label {
  color: #3f4f5c;
  font-weight: 800;
  letter-spacing: 0.04em;
}

input,
select,
textarea {
  width: 100%;
  border: 0;
  border-bottom: 1px solid currentColor;
  background: transparent;
  color: inherit;
  border-radius: 0;
  outline: none;
  font: inherit;
  font-size: 15px;
  padding: 8px 0 9px;
}

.right-page input,
.right-page select,
.right-page textarea {
  color: rgba(241, 238, 231, 0.86);
  border-bottom-color: rgba(241, 238, 231, 0.22);
}

.left-page input,
.left-page select,
.left-page textarea {
  color: #3f4f5c;
  border-bottom-color: rgba(31, 37, 41, 0.28);
}

select option {
  color: #252b29;
}

textarea {
  min-height: 152px;
  resize: none;
  line-height: 1.45;
}

input::placeholder,
textarea::placeholder {
  color: rgba(241, 238, 231, 0.36);
}

.left-page input::placeholder,
.left-page textarea::placeholder {
  color: rgba(31, 37, 41, 0.38);
}

.spread-panel {
  height: 100%;
  min-height: 635px;
  display: grid;
  grid-template-rows: 1fr 1fr;
  gap: 40px;
  padding: 54px 52px 28px;
}

.left-page .spread-panel {
  color: #252b29;
}

.right-page .spread-panel {
  color: #f1eee7;
}

.long-field textarea {
  height: 190px;
}

.book-actions {
  width: min(1240px, 100%);
  margin-top: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  color: #f1eee7;
  flex-wrap: wrap;
}

.save-btn {
  border: 1px solid rgba(241, 238, 231, 0.42);
  background: rgba(147, 164, 193, 0.88);
  color: #1f2529;
  padding: 11px 20px;
  font-size: 13px;
  cursor: pointer;
  letter-spacing: 1px;
  font-weight: 700;
  transition: transform 0.2s ease, background 0.2s ease;
}

.save-btn:hover {
  transform: translateY(-1px);
  background: #f1eee7;
}

.save-btn:disabled {
  opacity: 0.48;
  cursor: not-allowed;
  transform: none;
}

.completion-box {
  min-width: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(241, 238, 231, 0.76);
  font-size: 12px;
  letter-spacing: 1px;
}

.completion-box strong {
  color: #f1eee7;
  font-size: 18px;
}

@media (max-width: 980px) {
  .profile-page {
    overflow: auto;
  }

  .book-stage {
    padding: 86px 18px 30px;
    justify-content: flex-start;
  }

  .page-count {
    width: 62px;
    height: 62px;
    font-size: 22px;
    right: 18px;
  }

  .profile-book {
    min-height: auto;
    grid-template-columns: 1fr;
  }

  .profile-book::before {
    display: none;
  }

  .book-page {
    min-height: auto;
    padding: 34px 26px;
  }

  .left-page,
  .right-page {
    border-radius: 2px;
  }

  .profile-cover,
  .spread-panel {
    min-height: auto;
  }

  .profile-cover {
    min-height: 470px;
  }

  .profile-cover h1 {
    left: -72px;
    font-size: 62px;
  }

  .avatar-sheet {
    transform: translateX(34px);
  }

  .page-title {
    margin: 40px 34px 28px 0;
  }

  .field-list {
    grid-template-columns: 1fr;
    padding-right: 34px;
  }

  .spread-panel {
    padding: 42px 36px 24px;
  }
}

@media (max-width: 560px) {
  .book-stage {
    padding-inline: 12px;
  }

  .book-page {
    padding: 28px 20px;
  }

  .profile-cover h1 {
    left: -58px;
    font-size: 48px;
  }

  .avatar-sheet {
    width: 72%;
    transform: translateX(34px);
  }

  .page-title {
    grid-template-columns: 1fr;
    gap: 8px;
    margin-right: 28px;
  }

  .spread-panel {
    padding: 38px 30px 20px;
  }

  .book-actions {
    justify-content: stretch;
  }

  .save-btn,
  .completion-box {
    flex: 1 1 100%;
  }
}
</style>
