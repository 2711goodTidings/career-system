<template>
  <div class="profile-page">
    <button class="back-btn" @click="goHome">BACK HOME</button>

    <div class="story-container" ref="storyContainerRef">
      <!-- 第一屏 -->
      <section class="story-section hero-section">
        <div class="hero-card">
          <div class="hero-top">
            <div class="hero-date">2/0/2/6 / CAREER PLAN</div>
            <div class="hero-note">
              {{ form.bio || '填写你的个人简介' }}
            </div>
          </div>

          <div class="hero-center">
            <div class="hero-image-target" ref="heroImageTargetRef"></div>

            <h1
              class="hero-title"
              :style="{
                opacity: heroTitleOpacity,
                transform: `translate(-50%, calc(-20% + ${heroProgress * -24}px))`
              }"
            >
              PROFILE REPORT
            </h1>
          </div>

          <div class="hero-summary" :style="{ opacity: 1 - heroProgress * 1.2 }">
            <p><strong>姓名：</strong>{{ form.username || '未填写' }}</p>
            <p><strong>学校：</strong>{{ form.school || '未填写' }}</p>
            <p><strong>专业：</strong>{{ form.major || '未填写' }}</p>
          </div>
        </div>

        <div class="scroll-tip" :style="{ opacity: 1 - heroProgress * 1.4 }">
          SCROLL TO EDIT
        </div>
      </section>

      <!-- 第二屏 -->
      <section class="story-section edit-section">
        <div class="edit-stage">
          <div class="edit-left">
            <div class="edit-image-frame">
              <p class="left-top-text">MY PROFILE</p>
              <div class="edit-image-target" ref="editImageTargetRef">
                <label class="change-avatar-btn">
                  更换头像
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleAvatarChange"
                    class="hidden-input"
                  />
                </label>
              </div>
            </div>
          </div>

          <div
            class="edit-right refined-edit-right"
            :style="{
              opacity: editContentOpacity,
              transform: `translateY(${(1 - section2Progress) * 30}px)`
            }"
          >
            <div class="edit-header refined-header">
              <h2>EDIT YOUR PROFILE</h2>
            </div>

            <form class="profile-form refined-form" @submit.prevent="handleSubmit">
              <div class="form-block refined-block">
                <div class="block-content">
                  <h3>Basic Information</h3>

                  <div class="form-grid refined-grid">
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
                      <input
                        v-model="form.phone"
                        type="text"
                        maxlength="11"
                        placeholder="请输入11位手机号"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-block refined-block">
                <div class="block-content">
                  <h3>Education & Contact</h3>

                  <div class="form-grid refined-grid">
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
                      <input
                        v-model="form.email"
                        type="email"
                        placeholder="请输入邮箱"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-block refined-block">
                <div class="block-content">
                  <h3>Personal Description</h3>

                  <div class="form-grid one-col refined-grid">
                    <div class="form-item full">
                      <label>个人简介</label>
                      <textarea
                        v-model="form.bio"
                        rows="5"
                        placeholder="请输入你的兴趣、能力特点、职业倾向等"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-actions refined-actions">
                <div class="completion-box refined-completion">
                  <span>PROFILE COMPLETION</span>
                  <strong>{{ profileCompletion }}%</strong>
                </div>
                <button type="submit" class="save-btn refined-save-btn" :disabled="isSaving">
                  {{ isSaving ? 'SAVING...' : 'SAVE PROFILE' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>
    </div>

    <!-- 共享图片层 -->
    <div
      v-if="sharedImageVisible"
      class="shared-image-layer"
      :style="sharedImageStyle"
    >
      <img
        :src="avatarPreview || defaultAvatar"
        alt="avatar"
        class="shared-image"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const userStore = useUserStore()

const API_BASE = 'http://127.0.0.1:8000'
const defaultAvatar =
  'https://cdn.jsdelivr.net/gh/evjdent/SuperTinyIcons/images/svg/user.svg'

const storyContainerRef = ref(null)
const heroImageTargetRef = ref(null)
const editImageTargetRef = ref(null)

const avatarPreview = ref('')
const heroProgress = ref(0)
const section2Progress = ref(0)

const sharedImageStyle = ref({})
const sharedImageVisible = ref(true)
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
  bio: ''
})

const clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, v))

const updateScene = () => {
  const container = storyContainerRef.value
  const heroTarget = heroImageTargetRef.value
  const editTarget = editImageTargetRef.value
  if (!container || !heroTarget || !editTarget) return

  const scrollTop = container.scrollTop
  const vh = container.clientHeight || 1

  heroProgress.value = clamp(scrollTop / vh)
  section2Progress.value = clamp((scrollTop - vh * 0.15) / (vh * 0.85))

  const start = heroTarget.getBoundingClientRect()
  const end = editTarget.getBoundingClientRect()

  const t = heroProgress.value
  const lerp = (a, b, p) => a + (b - a) * p

  const left = lerp(start.left, end.left, t)
  const top = lerp(start.top, end.top, t)
  const width = lerp(start.width, end.width, t)
  const height = lerp(start.height, end.height, t)
  const shadowBlur = lerp(8, 22, t)

  sharedImageStyle.value = {
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
    height: `${height}px`,
    borderRadius: '0px',
    boxShadow: `0 12px ${shadowBlur}px rgba(0,0,0,0.12)`,
    opacity: scrollTop > vh * 1.25 ? 0 : 1
  }

  sharedImageVisible.value = scrollTop <= vh * 1.28
}

const heroTitleOpacity = computed(() => 1 - heroProgress.value * 1.05)
const editContentOpacity = computed(() => 0.2 + section2Progress.value * 0.8)

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
    form.bio
  ]
  const filled = fields.filter((item) => String(item).trim() !== '').length
  return Math.round((filled / fields.length) * 100)
})

const validatePhone = (phone) => /^1\d{10}$/.test(phone)
const validateEmail = (email) =>
  /^[A-Za-z0-9._%+-]+@(163\.com|qq\.com|gmail\.com)$/.test(email)

const goHome = () => {
  router.push('/')
}

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
    bio: form.bio || null
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

    if (data.avatar) {
      avatarPreview.value = `${API_BASE}${data.avatar}`
    }

    requestAnimationFrame(() => {
      updateScene()
    })
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
  } finally {
    requestAnimationFrame(() => {
      updateScene()
    })
  }
}

onMounted(() => {
  updateScene()
  loadProfile()

  const container = storyContainerRef.value
  container?.addEventListener('scroll', updateScene, { passive: true })
  window.addEventListener('resize', updateScene)
})

onBeforeUnmount(() => {
  const container = storyContainerRef.value
  container?.removeEventListener('scroll', updateScene)
  window.removeEventListener('resize', updateScene)
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.profile-page {
  height: 100vh;
  background: #1f5d95;
  font-family: "Times New Roman", "Georgia", "PingFang SC", "Microsoft YaHei", serif;
  color: #1f5d95;
  overflow: hidden;
  position: relative;
}

.story-container {
  height: 100vh;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}

.story-container::-webkit-scrollbar {
  width: 8px;
}

.story-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.28);
}

.story-section {
  min-height: 100vh;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  position: relative;
}

.back-btn {
  position: fixed;
  top: 22px;
  right: 22px;
  z-index: 60;
  border: none;
  background: rgba(255, 255, 255, 0.92);
  color: #1f5d95;
  padding: 12px 18px;
  font-size: 12px;
  letter-spacing: 2px;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

/* 第一屏 */
.hero-section {
  padding: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1f5d95;
}

.hero-card {
  width: min(1040px, 100%);
  min-height: 620px;
  background: #f5f5f3;
  position: relative;
  padding: 26px 42px 60px;
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.28) inset;
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.hero-date {
  font-size: 18px;
  letter-spacing: 6px;
  color: #1f5d95;
}

.hero-note {
  width: 230px;
  text-align: left;
  font-size: 18px;
  line-height: 1.2;
  color: #1f5d95;
  word-break: break-word;
}

.hero-center {
  position: relative;
  height: 430px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-image-target {
  width: 250px;
  height: 310px;
  position: relative;
  z-index: 1;
}

.hero-title {
  position: absolute;
  left: 50%;
  top: 50%;
  margin: 0;
  font-size: 76px;
  letter-spacing: 8px;
  font-weight: 500;
  color: #1f5d95;
  z-index: 3;
  white-space: nowrap;
}

.hero-dots {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 4px;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(31, 93, 149, 0.45);
}

.dot.active {
  background: #6f9ac1;
}

.hero-summary {
  position: absolute;
  right: 42px;
  bottom: 34px;
  text-align: right;
  font-size: 15px;
  line-height: 1.7;
  color: #1f5d95;
}

.hero-summary p {
  margin: 0;
}

.scroll-tip {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: #1f5d95;
  font-size: 12px;
  letter-spacing: 5px;
}

/* 第二屏 */
.edit-section {
  min-height: 100vh;
  background: #f5f5f3;
  display: flex;
  align-items: center;
  padding: 32px 38px;
}

.edit-stage {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 400px minmax(0, 760px);
  justify-content: center;
  gap: 34px;
}

.edit-left {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.edit-image-frame {
  position: relative;
  width: 360px;
  background: #7fa3c4;
  padding: 20px 26px 12px;
  min-height: 550px;
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.08);
}

.left-top-text {
  margin: 0 0 14px;
  color: #f5f5f3;
  font-size: 16px;
}

.edit-image-target {
  width: 100%;
  height: 440px;
  position: relative;
}

.edit-image-target .change-avatar-btn {
  position: absolute;
  bottom: -42px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: transparent;
  color: #1f5d95;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  z-index: 10;
}

.edit-image-target .change-avatar-btn:hover {
  text-decoration: underline;
}

.left-vertical-text {
  position: absolute;
  right: 8px;
  bottom: 28px;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  color: #f5f5f3;
  font-size: 14px;
  letter-spacing: 1px;
  margin: 0;
}

.edit-right {
  transition: 0.2s linear;
}

.refined-edit-right {
  padding: 18px 12px 12px 0;
  max-width: 760px;
}

.refined-header {
  margin-bottom: 22px;
}

.edit-tag {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 3px;
  color: #7fa3c4;
}

.refined-header h2 {
  margin: 0;
  font-size: 52px;
  line-height: 1.02;
  font-weight: 500;
  letter-spacing: 1px;
  color: #1f5d95;
}

.refined-form {
  width: 100%;
}

.form-block {
  margin-bottom: 22px;
}

.block-content h3 {
  margin: 0 0 14px 0;
  font-size: 14px;
  font-weight: 600;
  color: #3d5a7a;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(170px, 1fr));
}

.refined-grid {
  gap: 14px 16px;
}

.form-grid.one-col {
  grid-template-columns: 1fr;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-item.full {
  grid-column: 1 / -1;
}

.form-item label {
  margin-bottom: 6px;
  font-size: 12px;
  color: #5d84a8;
  letter-spacing: 0.5px;
}

.hero-image-target {
  position: relative;
}

.hidden-input {
  display: none;
}

.form-item input,
.form-item select,
.form-item textarea {
  width: 100%;
  border: none;
  border-bottom: 1px solid rgba(79, 122, 162, 0.28);
  background: transparent;
  padding: 10px 2px 9px;
  font-size: 14px;
  color: #2a5e90;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  border-radius: 0;
}

.form-item input:focus,
.form-item select:focus,
.form-item textarea:focus {
  border-bottom-color: #4f7aa2;
  box-shadow: 0 8px 12px -12px rgba(79, 122, 162, 0.45);
}

.form-item textarea {
  min-height: 92px;
  resize: vertical;
  padding-top: 10px;
}

.form-actions {
  margin-top: 4px;
  padding-left: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.completion-box {
  gap: 10px;
  font-size: 12px;
  color: #5d84a8;
  display: flex;
  align-items: center;
}

.completion-box strong {
  font-size: 18px;
  font-weight: 500;
  color: #1f5d95;
}

.save-btn {
  background: #1f5d95;
  color: #f5f5f3;
  padding: 11px 18px;
  font-size: 11px;
  letter-spacing: 2px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  box-shadow: none;
}

.save-btn:hover {
  background: #6f9ac1;
  color: #fff;
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 共享图片 */
.shared-image-layer {
  position: fixed;
  z-index: 40;
  overflow: hidden;
  pointer-events: none;
  transition: opacity 0.18s linear;
}

.shared-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* responsive */
@media (max-width: 1100px) {
  .edit-stage {
    grid-template-columns: 1fr;
  }

  .edit-left {
    justify-content: flex-start;
  }

  .edit-image-frame {
    width: min(420px, 100%);
    min-height: auto;
  }

  .edit-image-target {
    height: 420px;
  }

  .refined-edit-right {
    max-width: none;
    padding: 8px 0 0;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 16px;
  }

  .hero-card {
    padding: 18px 20px 28px;
    min-height: 540px;
  }

  .hero-date,
  .hero-note {
    font-size: 14px;
  }

  .hero-note {
    width: 150px;
  }

  .hero-center {
    height: 340px;
  }

  .hero-image-target {
    width: 180px;
    height: 230px;
  }

  .hero-title {
    font-size: 38px;
    letter-spacing: 4px;
  }

  .hero-summary {
    position: static;
    margin-top: 18px;
    text-align: center;
  }

  .scroll-tip {
    letter-spacing: 3px;
  }

  .edit-section {
    padding: 18px 16px 28px;
    gap: 22px;
  }

  .edit-image-frame {
    padding: 18px 18px 20px;
  }

  .edit-image-target {
    height: 320px;
  }

  .left-vertical-text {
    display: none;
  }

  .refined-header h2 {
    font-size: 38px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    padding-left: 0;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .back-btn {
    top: 14px;
    right: 14px;
    padding: 10px 14px;
  }
}
</style>