<template>
  <div class="profile-page">
    <div class="profile-wrap">
      <!-- 左侧头像海报区 -->
      <section class="poster-panel">
        <div class="stripe-group">
          <span v-for="i in 6" :key="i" class="stripe"></span>
        </div>

        <div class="poster poster-back">
          <div class="poster-text top">PERSONAL</div>
        </div>

        <div class="poster poster-middle">
          <div class="poster-text center">PROFILE</div>
        </div>

        <div class="poster poster-front">
          <div class="avatar-box">
            <img
              v-if="avatarPreview || profile.avatar"
              :src="avatarPreview || avatarUrl"
              alt="avatar"
              class="avatar-img"
            />
            <div v-else class="avatar-placeholder">
              <span>头像</span>
            </div>
          </div>

          <div class="poster-footer">
            <p class="poster-name">{{ profile.real_name || "未填写姓名" }}</p>
            <p class="poster-major">
              {{ profile.school || "未填写学校" }} {{ profile.major ? `· ${profile.major}` : "" }}
            </p>

            <label class="upload-btn">
              选择头像
              <input type="file" accept="image/*" @change="handleFileChange" hidden />
            </label>

            <button class="save-avatar-btn" @click="uploadAvatar" :disabled="!selectedFile || loading">
              上传头像
            </button>
          </div>
        </div>
      </section>

      <!-- 右侧表单区 -->
      <section class="info-panel">
        <div class="panel-header">
          <div>
            <p class="sub-title">SMART CAREER PLANNING</p>
            <h1>个人信息</h1>
          </div>
          <div class="status-text">
            {{ hasProfile ? "资料已存在" : "首次填写资料" }}
          </div>
        </div>

        <div class="form-grid">
          <div class="form-item">
            <label>真实姓名</label>
            <input v-model="profile.real_name" type="text" placeholder="请输入姓名" />
          </div>

          <div class="form-item">
            <label>性别</label>
            <select v-model="profile.gender">
              <option value="">请选择</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="保密">保密</option>
            </select>
          </div>

          <div class="form-item">
            <label>学校</label>
            <input v-model="profile.school" type="text" placeholder="请输入学校" />
          </div>

          <div class="form-item">
            <label>专业</label>
            <input v-model="profile.major" type="text" placeholder="请输入专业" />
          </div>

          <div class="form-item">
            <label>年级</label>
            <input v-model="profile.grade" type="text" placeholder="如：大三 / 2023级" />
          </div>

          <div class="form-item">
            <label>年龄</label>
            <input v-model.number="profile.age" type="number" placeholder="请输入年龄" />
          </div>

          <div class="form-item">
            <label>电话</label>
            <input
              v-model="profile.phone"
              type="text"
              maxlength="11"
              placeholder="请输入11位手机号"
            />
            <span v-if="phoneError" class="field-error">{{ phoneError }}</span>
          </div>

          <div class="form-item">
            <label>邮箱</label>
            <input
              v-model="profile.email"
              type="email"
              placeholder="请输入邮箱"
            />
            <span v-if="emailError" class="field-error">{{ emailError }}</span>
          </div>

          <div class="form-item form-item-full">
            <label>个人简介</label>
            <textarea
              v-model="profile.bio"
              rows="6"
              placeholder="介绍一下你的兴趣、方向或目前的职业规划想法"
            ></textarea>
          </div>
        </div>

        <div class="action-row">
          <button class="primary-btn" @click="saveProfile" :disabled="loading">
            {{ loading ? "处理中..." : hasProfile ? "保存修改" : "创建资料" }}
          </button>

          <button class="secondary-btn" @click="fetchProfile" :disabled="loading">
            重新获取
          </button>
        </div>

        <p class="message" v-if="message">{{ message }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import axios from "axios"

// 这里先临时写死测试 user_id
// 后面和队友联调后再改成从登录状态中读取
const userId = 1

const baseURL = "http://127.0.0.1:8000"

const loading = ref(false)
const hasProfile = ref(false)
const message = ref("")

const selectedFile = ref(null)
const avatarPreview = ref("")

const profile = reactive({
  real_name: "",
  gender: "",
  school: "",
  major: "",
  grade: "",
  age: null,
  phone: "",
  email: "",
  bio: "",
  avatar: ""
})

const avatarUrl = computed(() => {
  if (!profile.avatar) return ""
  return `${baseURL}${profile.avatar}`
})

const phoneError = computed(() => {
  if (!profile.phone) return ""
  return /^1\d{10}$/.test(profile.phone) ? "" : "电话必须为11位数字"
})

const emailError = computed(() => {
  if (!profile.email) return ""
  return /@(163\.com|qq\.com|gmail\.com)$/.test(profile.email)
    ? ""
    : "邮箱需以 @163.com、@qq.com 或 @gmail.com 结尾"
})

const validateForm = () => {
  if (profile.phone && phoneError.value) {
    message.value = phoneError.value
    return false
  }

  if (profile.email && emailError.value) {
    message.value = emailError.value
    return false
  }

  return true
}

// 获取个人信息
const fetchProfile = async () => {
  loading.value = true
  message.value = ""

  try {
    const res = await axios.get(`${baseURL}/profile/${userId}`)
    const data = res.data

    profile.real_name = data.real_name || ""
    profile.gender = data.gender || ""
    profile.school = data.school || ""
    profile.major = data.major || ""
    profile.grade = data.grade || ""
    profile.age = data.age ?? null
    profile.phone = data.phone || ""
    profile.email = data.email || ""
    profile.bio = data.bio || ""
    profile.avatar = data.avatar || ""

    hasProfile.value = true
    message.value = "个人信息获取成功"
  } catch (error) {
    if (error.response && error.response.status === 404) {
      hasProfile.value = false
      message.value = "当前用户还没有个人资料，请先填写并创建"
    } else {
      console.error(error)
      message.value = "获取个人信息失败"
    }
  } finally {
    loading.value = false
  }
}

// 创建或修改个人信息
const saveProfile = async () => {
  if (!validateForm()) return

  loading.value = true
  message.value = ""

  const payload = {
    user_id: userId,
    real_name: profile.real_name,
    gender: profile.gender,
    school: profile.school,
    major: profile.major,
    grade: profile.grade,
    age: profile.age,
    phone: profile.phone,
    email: profile.email,
    bio: profile.bio
  }

  try {
    if (!hasProfile.value) {
      await axios.post(`${baseURL}/profile`, payload)
      hasProfile.value = true
      message.value = "个人信息创建成功"
    } else {
      await axios.put(`${baseURL}/profile/${userId}`, {
        real_name: profile.real_name,
        gender: profile.gender,
        school: profile.school,
        major: profile.major,
        grade: profile.grade,
        age: profile.age,
        phone: profile.phone,
        email: profile.email,
        bio: profile.bio
      })
      message.value = "个人信息修改成功"
    }

    await fetchProfile()
  } catch (error) {
    console.error(error)
    message.value = "保存失败，请检查后端是否正常运行"
  } finally {
    loading.value = false
  }
}

// 选择头像文件
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  selectedFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

// 上传头像
const uploadAvatar = async () => {
  if (!selectedFile.value) {
    message.value = "请先选择头像图片"
    return
  }

  if (!hasProfile.value) {
    message.value = "请先创建个人资料，再上传头像"
    return
  }

  loading.value = true
  message.value = ""

  try {
    const formData = new FormData()
    formData.append("file", selectedFile.value)

    const res = await axios.post(`${baseURL}/upload-avatar/${userId}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    })

    profile.avatar = res.data.avatar_url
    message.value = "头像上传成功"
    selectedFile.value = null
  } catch (error) {
    console.error(error)
    message.value = "头像上传失败"
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 48px;
  background: #d9d6d1;
  color: #35568a;
}

.profile-wrap {
  max-width: 1380px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 430px minmax(0, 1fr);
  gap: 52px;
  align-items: start;
}

.poster-panel {
  position: relative;
  min-height: 760px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster {
  position: absolute;
  width: 300px;
  height: 430px;
  border: 5px solid #c84f45;
  background: rgba(240, 229, 208, 0.95);
  box-shadow: 0 12px 30px rgba(53, 86, 138, 0.08);
}

.poster-back {
  top: 30px;
  left: 40px;
  z-index: 1;
}

.poster-middle {
  top: 120px;
  left: 100px;
  z-index: 2;
}

.poster-front {
  top: 200px;
  left: 55px;
  z-index: 3;
  background: #cdb087;
  padding: 26px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.poster-text {
  color: #c84f45;
  font-family: "Georgia", "Times New Roman", serif;
  letter-spacing: 3px;
  text-align: center;
}

.poster-text.top {
  margin-top: 24px;
  font-size: 2.5rem;
}

.poster-text.center {
  margin-top: 96px;
  font-size: 2.35rem;
}

.avatar-box {
  width: 100%;
  height: 250px;
  border: 5px solid #c84f45;
  background: #efe7d5;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #9a7b57;
  font-size: 1.3rem;
  letter-spacing: 2px;
}

.poster-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.poster-name {
  margin: 0;
  font-size: 1.25rem;
  color: #35568a;
  font-weight: 700;
}

.poster-major {
  margin: 0 0 6px 0;
  color: #6f7f95;
  font-size: 0.95rem;
  line-height: 1.5;
}

.upload-btn,
.save-avatar-btn {
  border: none;
  cursor: pointer;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 0.92rem;
  transition: all 0.25s ease;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #35568a;
  color: #fff;
}

.save-avatar-btn {
  background: #c84f45;
  color: #fff;
}

.upload-btn:hover,
.save-avatar-btn:hover,
.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-2px);
  opacity: 0.92;
}

.save-avatar-btn:disabled,
.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.stripe-group {
  position: absolute;
  inset: 0;
  z-index: 0;
  display: flex;
  justify-content: center;
  gap: 18px;
}

.stripe {
  width: 14px;
  height: 100%;
  background: rgba(53, 86, 138, 0.55);
}

.info-panel {
  background: rgba(255, 255, 255, 0.34);
  border: 1px solid rgba(53, 86, 138, 0.12);
  border-radius: 24px;
  padding: 34px 34px 28px;
  box-shadow: 0 10px 35px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(2px);
  min-width: 0;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.sub-title {
  margin: 0 0 8px 0;
  color: #7b8da8;
  letter-spacing: 2px;
  font-size: 0.82rem;
}

.panel-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #35568a;
}

.status-text {
  padding: 8px 14px;
  border-radius: 14px;
  background: rgba(53, 86, 138, 0.1);
  color: #35568a;
  font-size: 0.92rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: 18px;
  row-gap: 18px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.form-item-full {
  grid-column: 1 / -1;
}

.form-item label {
  font-size: 0.95rem;
  color: #4e6487;
  font-weight: 600;
}

.form-item input,
.form-item select,
.form-item textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(53, 86, 138, 0.18);
  background: rgba(255, 255, 255, 0.75);
  border-radius: 10px;
  padding: 13px 14px;
  font-size: 0.96rem;
  color: #35568a;
  outline: none;
  transition: 0.2s ease;
}

.form-item input:focus,
.form-item select:focus,
.form-item textarea:focus {
  border-color: #35568a;
  box-shadow: 0 0 0 3px rgba(53, 86, 138, 0.08);
}

.form-item textarea {
  resize: vertical;
  min-height: 150px;
}

.field-error {
  color: #c84f45;
  font-size: 0.84rem;
  margin-top: -2px;
}

.action-row {
  margin-top: 28px;
  display: flex;
  gap: 14px;
}

.primary-btn,
.secondary-btn {
  border: none;
  cursor: pointer;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 0.96rem;
  transition: all 0.25s ease;
}

.primary-btn {
  background: #35568a;
  color: #fff;
}

.secondary-btn {
  background: #c84f45;
  color: #fff;
}

.message {
  margin-top: 18px;
  color: #35568a;
  font-size: 0.95rem;
}

@media (max-width: 1100px) {
  .profile-wrap {
    grid-template-columns: 1fr;
  }

  .poster-panel {
    min-height: 720px;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 24px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .poster-panel {
    transform: scale(0.9);
    transform-origin: top center;
  }
}
</style>