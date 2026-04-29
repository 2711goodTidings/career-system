<template>
  <div class="assessment-page">
    <FeaturePageNav current="ability" />

    <div class="container">
      <h1>📊 能力评估</h1>
      <p class="subtitle">请根据您的真实情况回答以下问题，结果将结合您的兴趣和成绩进行个性化分析</p>
      
      <!-- 自动保存提示 -->
      <div v-if="autoSaveMsg" class="auto-save-tip">
        {{ autoSaveMsg }}
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载题目中...</p>
      </div>
      
      <!-- 题目列表 -->
      <div v-else-if="!submitted && questions.length > 0" class="questions-container">
        <div v-for="(q, idx) in questions" :key="q.id" class="question-card">
          <div class="question-header">
            <span class="question-num">{{ idx + 1 }}</span>
            <span class="question-dimension">{{ getDimensionName(q.dimension) }}</span>
          </div>
          <p class="question-text">{{ q.question_text }}</p>
          <div class="options">
            <label v-for="score in 5" :key="score" class="option">
              <input 
                type="radio" 
                :name="`q${q.id}`" 
                :value="score"
                v-model="answers[q.id]"
                @change="saveAnswersToLocal"
              >
              <span>{{ scoreLabels[score] }}</span>
            </label>
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="goToHome" class="btn-home">🏠 返回首页</button>
          <button @click="clearSavedAnswers" class="btn-clear">清除已保存答案</button>
          <button @click="handleSubmit" class="btn-primary" :disabled="!isAllAnswered || submitting">
            {{ submitting ? '提交中...' : '提交评估' }}
          </button>
        </div>
      </div>
      
      <!-- 结果展示 -->
      <div v-else-if="submitted && result" class="result-container">
        <div class="result-card">
          <h2>📈 评估结果</h2>
          <div class="overall-level">
            <span class="level-label">综合等级：</span>
            <span class="level-value" :class="result.overall_level">{{ result.overall_level }}</span>
          </div>
          
          <div class="scores-list">
            <div v-for="(score, dim) in result.scores" :key="dim" class="score-item">
              <span class="dim-name">{{ getDimensionName(dim) }}</span>
              <div class="progress-bar">
                <div class="progress" :style="{ width: score + '%' }"></div>
              </div>
              <span class="score-value">{{ Math.round(score) }}分</span>
            </div>
          </div>
          
          <div class="suggestions">
            <h3>💡 个性化建议</h3>
            <p class="suggestions-text">{{ result.suggestions }}</p>
          </div>
          
          <div class="result-buttons">
            <button @click="goToHome" class="btn-home">🏠 返回首页</button>
            <button @click="resetAssessment" class="btn-secondary">重新评估</button>
          </div>
        </div>
      </div>
      
      <!-- 错误或无题目 -->
      <div v-else-if="!loading && questions.length === 0" class="error-card">
        <p>暂无评估题目，请联系管理员</p>
        <button @click="goToHome" class="btn-home">🏠 返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getQuestions, submitAssessment } from '../api/assessment'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const questions = ref([])
const answers = ref({})
const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const result = ref(null)
const autoSaveMsg = ref('')

// 评分标签
const scoreLabels = {
  1: '非常不符合',
  2: '比较不符合',
  3: '一般',
  4: '比较符合',
  5: '非常符合'
}

// 维度名称映射
const dimensionNames = {
  logic: '逻辑思维',
  innovation: '创新能力',
  communication: '沟通协作',
  learning: '学习能力',
  pressure: '抗压能力',
  leadership: '领导力'
}

const getDimensionName = (dim) => dimensionNames[dim] || dim

const isAllAnswered = computed(() => {
  if (!questions.value.length) return false
  return questions.value.every(q => answers.value[q.id] !== undefined && answers.value[q.id] !== null && answers.value[q.id] !== '')
})

// 返回首页
const goToHome = () => {
  router.push('/')
}

const getUserId = () => {
  if (userStore.userId) {
    return String(userStore.userId)
  }

  let userId = localStorage.getItem('userId')
  if (!userId) {
    userId = 'user_' + Date.now()
    localStorage.setItem('userId', userId)
  }
  return userId
}

const getCurrentUserId = () => {
  const id = Number(userStore.userId)
  return Number.isFinite(id) && id > 0 ? id : null
}

const saveAnswersToLocal = () => {
  const userId = getUserId()
  const key = `assessment_answers_${userId}`
  const toSave = {}
  
  questions.value.forEach(q => {
    if (answers.value[q.id] !== undefined && answers.value[q.id] !== null && answers.value[q.id] !== '') {
      toSave[q.id] = answers.value[q.id]
    }
  })
  
  localStorage.setItem(key, JSON.stringify({
    answers: toSave,
    savedAt: new Date().toISOString()
  }))
  
  autoSaveMsg.value = '✓ 已自动保存'
  setTimeout(() => {
    autoSaveMsg.value = ''
  }, 1500)
}

const loadSavedAnswers = () => {
  const userId = getUserId()
  const key = `assessment_answers_${userId}`
  const saved = localStorage.getItem(key)
  
  if (saved) {
    try {
      const data = JSON.parse(saved)
      if (data.answers && Object.keys(data.answers).length > 0) {
        for (const [qId, score] of Object.entries(data.answers)) {
          answers.value[parseInt(qId)] = score
        }
        autoSaveMsg.value = `✓ 已恢复上次保存的答案`
        setTimeout(() => {
          autoSaveMsg.value = ''
        }, 3000)
        return true
      }
    } catch (e) {
      console.error('加载保存的答案失败', e)
    }
  }
  return false
}

const clearSavedAnswers = () => {
  if (confirm('确定要清除所有已保存的答案吗？此操作不可恢复。')) {
    const userId = getUserId()
    const key = `assessment_answers_${userId}`
    localStorage.removeItem(key)
    
    questions.value.forEach(q => {
      answers.value[q.id] = null
    })
    
    autoSaveMsg.value = '✓ 已清除所有保存的答案'
    setTimeout(() => {
      autoSaveMsg.value = ''
    }, 2000)
  }
}

const loadQuestions = async () => {
  loading.value = true
  try {
    const res = await getQuestions()
    questions.value = res.data
    questions.value.forEach(q => {
      if (answers.value[q.id] === undefined) {
        answers.value[q.id] = null
      }
    })
    loadSavedAnswers()
  } catch (error) {
    console.error('加载题目失败', error)
    alert('加载题目失败，请检查后端是否正常运行')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!isAllAnswered.value) {
    alert('请回答所有问题')
    return
  }
  
  submitting.value = true
  try {
    const res = await submitAssessment(answers.value, getCurrentUserId())
    result.value = res.data
    submitted.value = true
    
    // 提交成功后不清除答案，保持上一轮答案
    // 这样用户可以查看已填写的答案
    autoSaveMsg.value = '✓ 提交成功！答案已保留'
    setTimeout(() => {
      autoSaveMsg.value = ''
    }, 2000)
    
  } catch (error) {
    console.error('提交失败', error)
    let errorMsg = '提交失败，请重试'
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    alert(errorMsg)
  } finally {
    submitting.value = false
  }
}

const resetAssessment = () => {
  submitted.value = false
  result.value = null
  // 不清空答案，保持已填写的答案
  // 如果也想清空答案，取消下面的注释
  // questions.value.forEach(q => {
  //   answers.value[q.id] = null
  // })
  // clearSavedAnswers()
}

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
.assessment-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 2rem 0;
}
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}
h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}
.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}
.auto-save-tip {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #4caf50;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  z-index: 1000;
  animation: fadeOut 2s ease-in-out;
}
@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}
.loading {
  text-align: center;
  padding: 3rem;
}
.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4285f4;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.question-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
}
.question-num {
  background: #4285f4;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.question-dimension {
  color: #666;
  font-size: 14px;
}
.question-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 1rem;
  line-height: 1.5;
}
.options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 14px;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background 0.2s;
}
.option:hover {
  background: #f0f0f0;
}
.option input {
  cursor: pointer;
  width: 18px;
  height: 18px;
}
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}
.result-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 1.5rem;
}
.btn-primary {
  background: #4285f4;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) {
  background: #3367d6;
}
.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.btn-clear {
  background: #ff9800;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-clear:hover {
  background: #f57c00;
}
.btn-home {
  background: #4caf50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-home:hover {
  background: #45a049;
}
.btn-secondary {
  background: #e0e0e0;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}
.btn-secondary:hover {
  background: #ccc;
}
.result-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.overall-level {
  text-align: center;
  margin-bottom: 1.5rem;
}
.level-label {
  font-size: 18px;
}
.level-value {
  font-size: 28px;
  font-weight: bold;
  margin-left: 0.5rem;
}
.level-value.优秀 { color: #f4b400; }
.level-value.良好 { color: #4285f4; }
.level-value.中等 { color: #0f9d58; }
.level-value.待提升 { color: #ea4335; }
.scores-list {
  margin: 1.5rem 0;
}
.score-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.dim-name {
  width: 80px;
  font-size: 14px;
  font-weight: 500;
}
.progress-bar {
  flex: 1;
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
}
.progress {
  height: 100%;
  background: #4285f4;
  border-radius: 5px;
  transition: width 0.3s;
}
.score-value {
  width: 50px;
  font-size: 14px;
  text-align: right;
  font-weight: 500;
}
.suggestions {
  background: #f0f7ff;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1.5rem 0;
}
.suggestions h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #4285f4;
}
.suggestions-text {
  white-space: pre-line;
  line-height: 1.6;
  margin: 0;
}
.error-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  color: #ea4335;
}
</style>
