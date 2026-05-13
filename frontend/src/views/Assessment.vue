<template>
  <div class="assessment-page">
    <FeaturePageNav current="ability" />

    <main class="questionnaire-shell">
      <div class="qa-mark">Q&amp;A</div>

      <section class="paper-panel">
        <header class="paper-heading">
          <span>Ability Questionnaire</span>
          <h1>{{ activeConfig.title }}</h1>
        </header>

        <div class="assessment-tabs">
          <button
            v-for="item in assessmentTypes"
            :key="item.key"
            type="button"
            class="tab-btn"
            :class="{ active: assessmentType === item.key }"
            @click="switchAssessmentType(item.key)"
          >
            <span>{{ item.icon }}</span>{{ item.label }}
          </button>
        </div>

        <div class="assessment-intro">
          <p>{{ activeConfig.intro }}</p>
        </div>

        <div class="paper-status">
          <span>{{ answeredCount }}/{{ questions.length || 0 }}</span>
          <span>{{ answerProgress }}%</span>
          <span>{{ submitted ? '已生成' : '填写中' }}</span>
        </div>

        <div v-if="autoSaveMsg" class="auto-save-tip">
          {{ autoSaveMsg }}
        </div>

        <section v-if="loading" class="paper-state">
          <div class="spinner"></div>
          <p>加载题目中...</p>
        </section>

        <section v-else-if="questions.length > 0" class="questionnaire-form">
          <div class="score-legend" aria-label="评分说明">
            <span v-for="score in 5" :key="score">
              <b>{{ score }}</b>{{ scoreLabels[score] }}
            </span>
          </div>

          <div class="question-list">
            <article v-for="(q, idx) in questions" :key="q.id" class="question-row">
              <span class="question-index">{{ idx + 1 }}.</span>

              <div class="question-copy">
                <div class="question-meta">
                  <span>{{ getDimensionName(q.dimension) }}</span>
                  <span>{{ isAnsweredValue(answers[q.id]) ? `${answers[q.id]}/5` : '未作答' }}</span>
                </div>
                <p>{{ q.question_text }}</p>
              </div>

              <div class="circle-options" role="radiogroup" :aria-label="getDimensionName(q.dimension)">
                <label
                  v-for="score in 5"
                  :key="score"
                  class="circle-option"
                  :class="{ selected: Number(answers[q.id]) === score }"
                  :title="scoreLabels[score]"
                >
                  <input
                    type="radio"
                    :name="`q${q.id}`"
                    :value="score"
                    v-model="answers[q.id]"
                    @change="saveAnswersToLocal"
                  >
                  <span>{{ score }}</span>
                </label>
              </div>
            </article>
          </div>

          <div class="paper-actions">
            <button type="button" class="text-btn" @click="clearSavedAnswers">清除答案</button>
            <button
              type="button"
              class="submit-btn"
              :disabled="!isAllAnswered || submitting"
              @click="handleSubmit"
            >
              {{ submitting ? '提交中...' : submitted ? '更新评估' : '提交评估' }}
            </button>
          </div>

          <section v-if="submitted && result" class="result-view">
            <div class="result-heading">
              <span>{{ activeConfig.resultTitle }}</span>
              <strong :class="result.overall_level">{{ result.overall_level }}</strong>
            </div>

            <div class="radar-layout">
              <svg class="radar-chart" viewBox="0 0 360 360" role="img" aria-label="能力评估雷达图">
                <g class="radar-grid">
                  <polygon
                    v-for="level in radarLevels"
                    :key="level"
                    :points="radarGridPoints(level)"
                  />
                  <line
                    v-for="axis in radarAxis"
                    :key="axis.dim"
                    x1="180"
                    y1="180"
                    :x2="axis.x"
                    :y2="axis.y"
                  />
                </g>

                <polygon class="radar-area" :points="radarPolygon" />
                <polygon class="radar-line" :points="radarPolygon" />

                <g class="radar-dots">
                  <circle
                    v-for="point in radarPoints"
                    :key="point.dim"
                    :cx="point.x"
                    :cy="point.y"
                    r="4"
                  />
                </g>

                <g class="radar-labels">
                  <text
                    v-for="axis in radarAxis"
                    :key="axis.dim"
                    :x="axis.labelX"
                    :y="axis.labelY"
                    text-anchor="middle"
                    dominant-baseline="middle"
                  >
                    {{ axis.shortLabel }}
                  </text>
                </g>
              </svg>

              <div class="radar-score-list">
                <div v-for="item in resultScoreList" :key="item.dim" class="radar-score-item">
                  <span>{{ item.label }}</span>
                  <strong>{{ Math.round(item.score) }}</strong>
                </div>
              </div>
            </div>

            <div class="result-suggestion">
              <div class="suggestion-title">
                <span>个性化建议</span>
                <em>{{ suggestionSourceText }}</em>
              </div>
              <small v-if="result.suggestion_error" class="suggestion-error">
                AI 未生成：{{ result.suggestion_error }}
              </small>
              <p>{{ result.suggestions }}</p>
            </div>

            <div class="paper-actions">
              <button type="button" class="text-btn" @click="resetAssessment">收起结果</button>
            </div>
          </section>
        </section>

        <section v-else-if="!loading && questions.length === 0" class="paper-state">
          <p>暂无评估题目，请联系管理员。</p>
        </section>

        <footer class="paper-footer">Ability Questionnaire</footer>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getQuestions, submitAssessment } from '../api/assessment'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const questions = ref([])
const answers = ref({})
const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const result = ref(null)
const autoSaveMsg = ref('')
const assessmentType = ref('tech')

const assessmentTypes = [
  {
    key: 'general',
    icon: 'GEN',
    label: '综合能力评估',
    title: '综合能力评估',
    resultTitle: '综合能力雷达图',
    intro: '这部分评估逻辑思维、创新、沟通协作、学习、抗压和领导力，用于 Career 页面判断学习节奏、表达协作和长期执行状态。'
  },
  {
    key: 'tech',
    icon: 'CS',
    label: '计算机能力评估',
    title: '计算机能力评估',
    resultTitle: '计算机能力雷达图',
    intro: '这部分评估编程、算法、计算机基础、软件工程、前后端、数据库、网络、AI 和运维能力，是 Career 页面职业推荐和能力画像的主要依据。'
  }
]

const activeConfig = computed(() =>
  assessmentTypes.find(item => item.key === assessmentType.value) || assessmentTypes[1]
)

const scoreLabels = {
  1: '非常不符合',
  2: '比较不符合',
  3: '一般',
  4: '比较符合',
  5: '非常符合'
}

const dimensionNames = {
  logic: '逻辑思维',
  innovation: '创新能力',
  communication: '沟通协作',
  learning: '学习能力',
  pressure: '抗压能力',
  leadership: '领导力',
  programming: '编程能力',
  algorithm: '数据结构与算法',
  computer_basic: '计算机基础',
  software_eng: '软件工程',
  backend: '后端开发',
  frontend: '前端开发',
  database: '数据库',
  network: '计算机网络',
  ai_ml: 'AI与机器学习',
  devops: '运维与部署'
}

const dimensionShortNames = {
  logic: '逻辑',
  innovation: '创新',
  communication: '沟通',
  learning: '学习',
  pressure: '抗压',
  leadership: '领导',
  programming: '编程',
  algorithm: '算法',
  computer_basic: '基础',
  software_eng: '工程',
  backend: '后端',
  frontend: '前端',
  database: '数据库',
  network: '网络',
  ai_ml: 'AI',
  devops: '运维'
}

const getDimensionName = (dim) => dimensionNames[dim] || dim
const getDimensionShortName = (dim) => dimensionShortNames[dim] || getDimensionName(dim)

const isAnsweredValue = (value) => value !== undefined && value !== null && value !== ''

const clampScore = (value) => {
  const score = Number(value || 0)
  return Math.min(100, Math.max(0, score))
}

const isAllAnswered = computed(() => {
  if (!questions.value.length) return false
  return questions.value.every(q => isAnsweredValue(answers.value[q.id]))
})

const answeredCount = computed(() =>
  questions.value.filter(q => isAnsweredValue(answers.value[q.id])).length
)

const answerProgress = computed(() => {
  if (!questions.value.length) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})

const resultScoreList = computed(() =>
  Object.entries(result.value?.scores || {}).map(([dim, score]) => ({
    dim,
    label: getDimensionName(dim),
    shortLabel: getDimensionShortName(dim),
    score: clampScore(score)
  }))
)

const suggestionSourceText = computed(() => {
  if (!result.value) return ''
  return result.value.suggestion_source === 'ai' ? 'AI 生成' : '规则建议'
})

const radarLevels = [0.25, 0.5, 0.75, 1]
const radarCenter = 180
const radarRadius = 104

function radarPoint(index, total, ratio, radiusOffset = 0) {
  if (!total) {
    return { x: radarCenter, y: radarCenter }
  }

  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / total
  const radius = radarRadius * ratio + radiusOffset
  return {
    x: radarCenter + Math.cos(angle) * radius,
    y: radarCenter + Math.sin(angle) * radius
  }
}

function radarGridPoints(level) {
  return resultScoreList.value
    .map((_, index) => {
      const point = radarPoint(index, resultScoreList.value.length, level)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

const radarPoints = computed(() =>
  resultScoreList.value.map((item, index) => {
    const point = radarPoint(index, resultScoreList.value.length, item.score / 100)
    return {
      ...item,
      ...point
    }
  })
)

const radarAxis = computed(() =>
  resultScoreList.value.map((item, index) => {
    const axisPoint = radarPoint(index, resultScoreList.value.length, 1)
    const labelPoint = radarPoint(index, resultScoreList.value.length, 1, 32)
    return {
      ...item,
      x: axisPoint.x,
      y: axisPoint.y,
      labelX: labelPoint.x,
      labelY: labelPoint.y
    }
  })
)

const radarPolygon = computed(() =>
  radarPoints.value.map((point) => `${point.x},${point.y}`).join(' ')
)

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
  const key = `assessment_${assessmentType.value}_answers_${userId}`
  const toSave = {}

  questions.value.forEach(q => {
    if (isAnsweredValue(answers.value[q.id])) {
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
  const key = `assessment_${assessmentType.value}_answers_${userId}`
  const saved = localStorage.getItem(key)

  if (saved) {
    try {
      const data = JSON.parse(saved)
      if (data.answers && Object.keys(data.answers).length > 0) {
        for (const [qId, score] of Object.entries(data.answers)) {
          answers.value[parseInt(qId)] = score
        }
        autoSaveMsg.value = '✓ 已恢复上次保存的答案'
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
    const key = `assessment_${assessmentType.value}_answers_${userId}`
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
    const res = await getQuestions(assessmentType.value)
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
    const res = await submitAssessment(answers.value, getCurrentUserId(), assessmentType.value)
    result.value = res.data
    submitted.value = true

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
}

const switchAssessmentType = async (type) => {
  if (type === assessmentType.value) return
  saveAnswersToLocal()
  assessmentType.value = type
  answers.value = {}
  submitted.value = false
  result.value = null
  await loadQuestions()
}

watch(assessmentType, () => {
  submitted.value = false
  result.value = null
})

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.assessment-page {
  min-height: 100vh;
  padding: 0 24px 54px;
  position: relative;
  overflow-x: hidden;
  background-color: #123f91;
  background-image:
    linear-gradient(rgba(18, 63, 145, 0.18), rgba(18, 63, 145, 0.18)),
    url("../assets/assessmentbackgroud.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: #5d5751;
  font-family: "Times New Roman", "Songti SC", "STSong", "SimSun", serif;
}

.questionnaire-shell {
  width: min(720px, calc(100vw - 48px));
  margin: 50vh auto 0;
  position: relative;
  z-index: 1;
}

.qa-mark {
  position: absolute;
  left: -150px;
  top: -88px;
  z-index: 3;
  color: #1f5d95;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(82px, 13vw, 168px);
  font-weight: 400;
  line-height: 0.78;
  letter-spacing: -0.08em;
  pointer-events: none;
}

.paper-panel {
  min-height: 760px;
  padding: 44px 38px 24px;
  position: relative;
  background: #edf0f2;
  box-shadow: 0 28px 72px rgba(16, 32, 68, 0.24);
}

.paper-heading {
  margin-bottom: 14px;
  position: relative;
}

.paper-heading::after {
  content: "";
  position: absolute;
  right: 205px;
  bottom: 10px;
  width: 8px;
  height: 8px;
  border: 2px solid #1f5d95;
  border-radius: 50%;
}

.paper-heading span {
  display: block;
  color: #14110f;
  font-size: clamp(27px, 4vw, 43px);
  line-height: 1;
  letter-spacing: 0.02em;
}

.paper-heading h1 {
  margin: 4px 0 0;
  color: #504c48;
  font-family: "Microsoft JhengHei Light", "Microsoft YaHei UI Light", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: clamp(42px, 7vw, 74px);
  font-weight: 300;
  line-height: 0.9;
  letter-spacing: 0.01em;
  text-align: right;
  transform: scaleY(1.18);
  transform-origin: right bottom;
}

.paper-status {
  margin: 0 0 14px;
  padding: 8px 0 10px;
  display: flex;
  justify-content: flex-end;
  gap: 18px;
  border-top: 1px solid rgba(89, 82, 75, 0.28);
  border-bottom: 1px solid rgba(89, 82, 75, 0.2);
  color: #7c746d;
  font-size: 13px;
  letter-spacing: 0.08em;
}

.assessment-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 18px 0 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(89, 82, 75, 0.16);
}

.tab-btn {
  min-height: 38px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(31, 93, 149, 0.42);
  background: rgba(255, 255, 255, 0.22);
  color: #1f5d95;
  cursor: pointer;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
}

.tab-btn span {
  font-size: 11px;
  letter-spacing: 0.08em;
}

.tab-btn.active {
  background: #1f5d95;
  color: #f4f7fa;
  border-color: #1f5d95;
}

.assessment-intro {
  margin: 12px 0 16px;
  padding: 12px 14px;
  border: 1px solid rgba(31, 93, 149, 0.22);
  background: rgba(255, 255, 255, 0.38);
}

.assessment-intro p {
  margin: 0;
  color: #625b54;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.7;
}

.auto-save-tip {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 90;
  padding: 9px 14px;
  background: rgba(232, 227, 218, 0.94);
  color: #123f91;
  border: 1px solid rgba(18, 63, 145, 0.22);
  font-size: 14px;
  box-shadow: 0 16px 30px rgba(16, 32, 68, 0.22);
}

.paper-state {
  min-height: 360px;
  display: grid;
  place-items: center;
  gap: 18px;
  text-align: center;
  color: #6f6860;
  font-size: 18px;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 2px solid rgba(89, 82, 75, 0.2);
  border-top-color: #1f5d95;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.score-legend {
  margin-bottom: 6px;
  padding-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  color: #79716a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  border-bottom: 1px solid rgba(89, 82, 75, 0.18);
}

.score-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}

.score-legend b {
  width: 17px;
  height: 17px;
  display: inline-grid;
  place-items: center;
  color: #1f5d95;
  border: 1px solid #1f5d95;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 500;
}

.question-list {
  margin-top: 4px;
}

.question-row {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) 158px;
  gap: 8px 14px;
  align-items: start;
  padding: 8px 0;
  border-bottom: 1px solid rgba(89, 82, 75, 0.13);
}

.question-index {
  color: #69625b;
  font-size: 17px;
  line-height: 1.5;
  text-align: right;
}

.question-copy {
  min-width: 0;
}

.question-meta {
  margin-bottom: 1px;
  display: flex;
  gap: 10px;
  color: #9a9188;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 10px;
  line-height: 1.2;
  letter-spacing: 0.08em;
}

.question-copy p {
  margin: 0;
  color: #5c554f;
  font-size: 17px;
  line-height: 1.48;
}

.circle-options {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  padding-top: 4px;
}

.circle-option {
  cursor: pointer;
}

.circle-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.circle-option span {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border: 1.4px solid #79716a;
  border-radius: 50%;
  color: #79716a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  line-height: 1;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;
}

.circle-option:hover span,
.circle-option.selected span {
  color: #f4f7fa;
  background: #1f5d95;
  border-color: #1f5d95;
}

.circle-option:hover span {
  transform: translateY(-1px);
}

.paper-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

button {
  font: inherit;
}

.text-btn {
  padding: 0 0 3px;
  border: 0;
  border-bottom: 1px dashed rgba(89, 82, 75, 0.64);
  background: transparent;
  color: #625b54;
  cursor: pointer;
  font-size: 15px;
}

.submit-btn {
  min-height: 38px;
  padding: 0 22px;
  border: 1px solid #1f5d95;
  background: #1f5d95;
  color: #f4f7fa;
  cursor: pointer;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  letter-spacing: 0.08em;
  transition:
    opacity 0.18s ease,
    transform 0.18s ease,
    background 0.18s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #174a78;
}

.submit-btn:disabled {
  opacity: 0.42;
  cursor: not-allowed;
}

.result-view {
  margin-top: 30px;
  padding-top: 24px;
  border-top: 1px solid rgba(89, 82, 75, 0.2);
}

.result-heading {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 18px;
  align-items: end;
  padding-bottom: 18px;
}

.result-heading span,
.result-suggestion span {
  color: #14110f;
  font-size: 30px;
  line-height: 1;
}

.suggestion-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.suggestion-title em {
  padding: 5px 10px;
  color: #1f5d95;
  border: 1px solid rgba(31, 93, 149, 0.26);
  background: rgba(31, 93, 149, 0.08);
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  font-style: normal;
}

.suggestion-error {
  display: block;
  margin-top: 10px;
  color: #a25a18;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  line-height: 1.6;
}

.result-heading strong {
  color: #1f5d95;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: clamp(34px, 6vw, 62px);
  line-height: 1;
}

.radar-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px;
  gap: 22px;
  align-items: center;
  margin: 12px 0 24px;
}

.radar-chart {
  width: 100%;
  min-height: 300px;
  display: block;
}

.radar-grid polygon {
  fill: none;
  stroke: rgba(89, 82, 75, 0.22);
  stroke-width: 1;
}

.radar-grid line {
  stroke: rgba(89, 82, 75, 0.16);
  stroke-width: 1;
}

.radar-area {
  fill: rgba(31, 93, 149, 0.18);
}

.radar-line {
  fill: none;
  stroke: #1f5d95;
  stroke-width: 2;
}

.radar-dots circle {
  fill: #1f5d95;
  stroke: #edf0f2;
  stroke-width: 2;
}

.radar-labels text {
  fill: #625b54;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 11px;
}

.radar-score-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radar-score-item {
  min-height: 32px;
  display: grid;
  grid-template-columns: 1fr 42px;
  gap: 10px;
  align-items: center;
  color: #625b54;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  border-bottom: 1px solid rgba(89, 82, 75, 0.12);
}

.radar-score-item strong {
  color: #1f5d95;
  font-weight: 600;
  text-align: right;
}

.result-scores {
  margin: 24px 0;
}

.score-row {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) 42px;
  gap: 12px;
  align-items: center;
  min-height: 36px;
  color: #625b54;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
}

.score-track {
  height: 8px;
  background: rgba(89, 82, 75, 0.16);
}

.score-fill {
  height: 100%;
  background: #123f91;
}

.score-row strong {
  text-align: right;
  font-weight: 500;
}

.result-suggestion {
  padding-top: 18px;
  border-top: 1px solid rgba(89, 82, 75, 0.18);
}

.result-suggestion p {
  margin: 14px 0 0;
  color: #625b54;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-line;
}

.paper-footer {
  margin-top: 28px;
  text-align: center;
  color: #26211d;
  font-size: 18px;
  line-height: 1;
}

@media (max-width: 900px) {
  .qa-mark {
    left: -24px;
    top: -76px;
  }

  .question-row {
    grid-template-columns: 32px minmax(0, 1fr);
  }

  .circle-options {
    grid-column: 2;
    justify-content: flex-start;
    padding-top: 0;
  }

  .radar-layout {
    grid-template-columns: 1fr;
  }

  .radar-score-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .assessment-page {
    padding: 0 12px 34px;
  }

  .questionnaire-shell {
    width: 100%;
  }

  .qa-mark {
    left: 2px;
    top: -54px;
    font-size: 78px;
  }

  .paper-panel {
    min-height: auto;
    padding: 34px 18px 22px;
  }

  .paper-heading span {
    font-size: 26px;
  }

  .paper-heading h1 {
    font-size: 42px;
    text-align: left;
  }

  .paper-heading::after {
    right: auto;
    left: 0;
    bottom: -10px;
  }

  .paper-status {
    justify-content: flex-start;
    margin-top: 18px;
  }

  .score-legend {
    gap: 7px 10px;
  }

  .question-row {
    grid-template-columns: 28px minmax(0, 1fr);
    gap: 6px 9px;
    padding: 10px 0;
  }

  .question-copy p {
    font-size: 16px;
  }

  .circle-option span {
    width: 23px;
    height: 23px;
  }

  .result-heading {
    grid-template-columns: 1fr;
  }

  .radar-chart {
    min-height: 250px;
  }

  .radar-score-list {
    grid-template-columns: 1fr;
  }

  .score-row {
    grid-template-columns: 1fr 38px;
  }

  .score-track {
    grid-column: 1 / -1;
    grid-row: 2;
  }

  .paper-actions {
    gap: 12px;
  }
}
</style>
