<template>
  <div class="planning-page">
    <FeaturePageNav current="planning" />

    <main class="planning-shell">
      <section class="plan-card">
        <header class="plan-header">
          <div class="header-titles">
            <span class="kicker-text">CAREER DOSSIER</span>
            <h1>职业成长规划书</h1>
            <p class="subtitle">面向计算机专业学生的路径判断、能力补强与阶段行动整理。</p>
          </div>

          <div class="plan-stamp">
            <label for="planning-path">CURRENT PATH // 当前路径</label>
            <div class="select-wrapper">
              <select id="planning-path" v-model="selectedPath" :disabled="!userStore.isLogin" @change="onPathChange">
                <option v-for="path in pathOptions" :key="path.value" :value="path.value">
                  {{ path.label }}
                </option>
              </select>
            </div>
            <p class="stamp-desc">{{ coverDescription }}</p>
          </div>
        </header>

        <div v-if="error" class="plan-state danger">
          <strong>[ ERROR ]</strong>
          <p>{{ error }}</p>
        </div>

        <div v-if="!userStore.isLogin" class="plan-state">
          <strong>AUTHORIZATION REQUIRED</strong>
          <p>请先登录。系统将结合个人资料、能力评估和职业推荐结果为您生成专属档案。</p>
        </div>

        <div v-else-if="loading" class="plan-state">
          <div class="loading-block"></div>
          <strong>COMPILING DOSSIER...</strong>
          <p>正在汇总推荐路径、技能短板和阶段任务，请稍候。</p>
        </div>

        <div v-else-if="recommendation" class="plan-content">
          <section class="yearly-plan">
            <div class="yearly-head">
              <span class="kicker-text">YEARLY ROADMAP</span>
              <h2>年度规划</h2>
              <p>依据个人资料、能力评估、职业推荐和当前路径侧重生成。</p>
              <button
                v-if="yearlyPlan && !yearlyPlanLoading && !yearlyPlanError"
                class="sharp-btn-outline export-plan-btn"
                type="button"
                @click="exportYearlyPlanPdf"
              >
                导出 PDF
              </button>
            </div>

            <div v-if="yearlyPlanLoading" class="yearly-loading">
              <div class="loading-block"></div>
              <p>正在整理每学年的目标、任务和产出...</p>
            </div>

            <p v-else-if="yearlyPlanError" class="yearly-error">{{ yearlyPlanError }}</p>

            <article v-else class="yearly-paper">
              <template v-if="yearlyPlan">
                <p
                  v-for="(line, index) in formattedYearlyPlanLines"
                  :key="`${index}_${line.text}`"
                  class="yearly-line"
                  :class="{
                    'yearly-line-heading': line.isHeading,
                    'yearly-line-blank': line.isBlank
                  }"
                >
                  <template v-for="(part, partIndex) in line.parts" :key="partIndex">
                    <strong v-if="part.bold">{{ part.text }}</strong>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </p>
              </template>
              <template v-else>暂未形成年度规划。</template>
            </article>
          </section>

          <footer class="plan-footer">
            GENERATED AT / {{ generatedAtText }}
          </footer>
        </div>

        <div v-else class="plan-state empty">
          <strong>NO DATA</strong>
          <p>完善个人信息并完成能力评估后，系统会自动整理大学剩余学年的年度安排。</p>
        </div>
      </section>

      <section class="consultation-panel">
        <div class="panel-inner">
          <div class="section-head">
            <div>
              <span class="kicker-text">PLANNING INQUIRY</span>
              <h2>规划问答</h2>
            </div>
            <button
              v-if="userStore.isLogin"
              class="clear-chat-btn"
              type="button"
              :disabled="aiLoading || !chatMessages.length"
              @click="clearChatHistory"
            >
              清空历史
            </button>
          </div>

          <section v-if="!userStore.isLogin" class="notice consultation-notice">
            <strong>需要权限</strong>
            <p>登录后可以结合你的资料、测评结果和推荐路径进行深度咨询。</p>
          </section>

          <template v-else>
            <div class="quick-questions">
              <button
                v-for="item in quickQuestions"
                :key="item"
                class="sharp-btn-outline"
                type="button"
                @click="sendQuestion(item)"
                :disabled="aiLoading"
              >
                {{ item }}
              </button>
            </div>

            <div ref="chatDossierRef" class="chat-dossier">
              <div v-if="!chatMessages.length" class="empty-text">
                [ 记录为空 ] 可以继续追问就业、考研、项目、算法、简历或具体技术方向。
              </div>
              <article
                v-for="message in chatMessages"
                :key="message.id"
                class="dossier-entry"
                :class="message.role"
              >
                <div class="entry-role">{{ message.role === 'user' ? 'Q.' : 'A.' }}</div>
                <div class="entry-body">
                  <p>{{ message.content }}</p>

                </div>
              </article>
            </div>

            <p v-if="aiError" class="consultation-error">{{ aiError }}</p>

            <div class="chat-input-matrix">
              <textarea
                v-model="aiQuestion"
                rows="3"
                placeholder="在此输入需要探讨的问题..."
                :disabled="aiLoading"
              ></textarea>
              <button class="sharp-btn-solid" type="button" @click="sendQuestion()" :disabled="aiLoading">
                {{ aiLoading ? 'PROCESSING' : 'SUBMIT' }}
              </button>
            </div>
          </template>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
// [你的原生 script 内容完全保持不变，不要做任何删减]
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import { getCareerRecommendation } from '../api/career'
import { askPlanningAI, generateYearlyPlanning } from '../api/planning'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const loading = ref(false)
const error = ref('')
const recommendation = ref(null)
const aiLoading = ref(false)
const aiQuestion = ref('')
const aiError = ref('')
const chatMessages = ref([])
const chatDossierRef = ref(null)
const selectedPath = ref('就业')
const selectedPathTouched = ref(false)
const yearlyPlan = ref('')
const yearlyPlanLoading = ref(false)
const yearlyPlanError = ref('')
const generatedAt = ref('')
let yearlyPlanRequestId = 0

const pathOptions = [
  { value: '就业', label: '就业' },
  { value: '考研', label: '考研' },
  { value: '考公', label: '考公 / 事业单位' },
  { value: '留学', label: '留学' }
]

const quickQuestions = [
  '我适合就业还是考研？',
  '我想做后端，接下来三个月怎么准备？',
  '我的项目经历应该怎么补？',
  '算法薄弱还能找开发岗吗？'
]

const pathResult = computed(() => recommendation.value?.path_result || {})

const activePathLabel = computed(() => {
  return selectedPath.value || pathResult.value.recommend_path || pathOptions[0].value
})

const generatedAtText = computed(() => generatedAt.value || new Date().toLocaleString())

const formattedYearlyPlanLines = computed(() => {
  return String(yearlyPlan.value || '')
    .split('\n')
    .map(line => formatYearlyPlanLine(line))
})

const coverDescription = computed(() => {
  if (!userStore.isLogin) return '登录后即可生成专属职业成长路线。'
  if (loading.value) return '正在整理你的规划档案。'
  if (!recommendation.value) return '完善资料后生成一份可执行的成长规划。'
  return '规划已根据职业推荐结果生成，可继续完善资料后刷新。'
})

function toPlainText(text) {
  return String(text || '')
    .replace(/\*\*/g, '')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/^\s*[-*]\s+/gm, '')
    .replace(/`{1,3}/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function isYearlyHeading(line) {
  const text = String(line || '').trim()
  return /^(?:[一二三四五六七八九十]+[、.．]\s*)?(?:大一|大二|大三|大四|研一|研二|当前学年|本学年|剩余学年|毕业前).{0,12}(?:年度规划|阶段规划|规划|计划|安排)$/.test(text)
}

function formatYearlyPlanLine(line) {
  const text = String(line || '')
  const isBlank = !text.trim()
  const isHeading = isYearlyHeading(text)
  const targetKeyword = '年度目标'
  const keywordIndex = text.indexOf(targetKeyword)

  if (keywordIndex === -1) {
    return {
      text,
      isBlank,
      isHeading,
      parts: [{ text, bold: false }]
    }
  }

  return {
    text,
    isBlank,
    isHeading,
    parts: [
      { text: text.slice(0, keywordIndex), bold: false },
      { text: targetKeyword, bold: true },
      { text: text.slice(keywordIndex + targetKeyword.length), bold: false }
    ].filter(part => part.text)
  }
}

function trimYearlyPlanIntro(text) {
  const plain = toPlainText(text)
  const headingMatch = plain.match(/(?:^|\n)\s*[一二三四五六七八九十]+[、.．]\s*(大一|大二|大三|大四|研一|研二|当前学年|本学年|剩余学年|毕业前|年度|阶段)/)
  if (headingMatch?.index !== undefined) {
    return plain.slice(headingMatch.index).trim()
  }

  const introPrefixes = [
    '学生信息',
    '学校：',
    '学校:',
    '年级：',
    '年级:',
    '专业：',
    '专业:',
    '本次规划路径',
    '本次规划路线',
    '路径说明',
    '规划说明',
    '当前判断'
  ]
  const lines = plain.split('\n')
  while (lines.length) {
    const line = lines[0].trim()
    if (!line || introPrefixes.some(prefix => line.startsWith(prefix))) {
      lines.shift()
    } else {
      break
    }
  }
  return lines.join('\n').trim()
}

function formatGeneratedAt(value) {
  if (!value) return new Date().toLocaleString()
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString()
}

function scrollChatToBottom() {
  nextTick(() => {
    const el = chatDossierRef.value
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

async function loadRecommendation() {
  if (!userStore.isLogin || !userStore.userId) {
    error.value = '请先登录后再生成职业规划。'
    recommendation.value = null
    return
  }

  loading.value = true
  error.value = ''

  try {
    recommendation.value = await getCareerRecommendation(userStore.userId)
    const recommendedPath = recommendation.value?.path_result?.recommend_path
    if (!selectedPathTouched.value && recommendedPath) {
      selectedPath.value = recommendedPath
    }
  } catch (err) {
    error.value = err.message || '生成职业规划失败。'
    recommendation.value = null
    return
  } finally {
    loading.value = false
  }

  await loadYearlyPlan()
}

async function loadYearlyPlan() {
  if (!userStore.isLogin || !userStore.userId) return

  const requestId = ++yearlyPlanRequestId
  const pathLabel = activePathLabel.value
  yearlyPlanLoading.value = true
  yearlyPlanError.value = ''

  try {
    const response = await generateYearlyPlanning(userStore.userId, pathLabel)
    if (requestId !== yearlyPlanRequestId) return

    const data = response.data || response
    if (data.success) {
      yearlyPlan.value = trimYearlyPlanIntro(data.answer) || '暂未形成年度规划。'
      generatedAt.value = formatGeneratedAt(data.created_at)
    } else {
      yearlyPlan.value = ''
      yearlyPlanError.value = data.error || '年度规划暂时无法生成，请稍后重试。'
    }
  } catch (err) {
    if (requestId !== yearlyPlanRequestId) return

    yearlyPlan.value = ''
    yearlyPlanError.value = err.response?.data?.detail || err.message || '年度规划请求失败，请稍后重试。'
  } finally {
    if (requestId === yearlyPlanRequestId) {
      yearlyPlanLoading.value = false
    }
  }
}

function onPathChange() {
  selectedPathTouched.value = true
  if (recommendation.value && userStore.isLogin && userStore.userId) {
    loadYearlyPlan()
  }
}

function getChatStorageKey() {
  return `planning_ai_chat_${userStore.userId}`
}

function loadChatMessages() {
  if (!userStore.userId) {
    chatMessages.value = []
    return
  }

  try {
    const saved = localStorage.getItem(getChatStorageKey())
    chatMessages.value = saved
      ? JSON.parse(saved).map(message => ({
          ...message,
          content: message.role === 'assistant' ? toPlainText(message.content) : message.content
        }))
      : []
    scrollChatToBottom()
  } catch (err) {
    chatMessages.value = []
  }
}

function saveChatMessages() {
  if (!userStore.userId) return
  localStorage.setItem(getChatStorageKey(), JSON.stringify(chatMessages.value.slice(-30)))
}

function clearChatHistory() {
  if (!userStore.userId || aiLoading.value || !chatMessages.value.length) return

  const confirmed = window.confirm('确定清空当前账号的规划问答历史吗？')
  if (!confirmed) return

  chatMessages.value = []
  aiError.value = ''
  localStorage.removeItem(getChatStorageKey())
}

function appendChatMessage(role, content, meta = '') {
  chatMessages.value.push({
    id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
    role,
    content,
    meta
  })
  saveChatMessages()
  scrollChatToBottom()
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderFormattedPlanHtml(text) {
  return String(text || '')
    .split('\n')
    .map(line => formatYearlyPlanLine(line))
    .map(line => {
      const content = line.parts
        .map(part => (part.bold ? `<strong>${escapeHtml(part.text)}</strong>` : escapeHtml(part.text)))
        .join('')
      const className = [
        'plan-line',
        line.isHeading ? 'plan-heading' : '',
        line.isBlank ? 'plan-blank' : ''
      ].filter(Boolean).join(' ')
      return `<p class="${className}">${content || '&nbsp;'}</p>`
    })
    .join('')
}

function exportYearlyPlanPdf() {
  if (!yearlyPlan.value) return

  const title = 'SmartCareerPlanning 职业成长规划书'
  const path = activePathLabel.value || '未选择'
  const generated = generatedAtText.value
  const planHtml = renderFormattedPlanHtml(yearlyPlan.value)
  const printWindow = window.open('', '_blank', 'width=900,height=720')

  if (!printWindow) {
    yearlyPlanError.value = '浏览器阻止了导出窗口，请允许弹出窗口后重试。'
    return
  }

  printWindow.document.write(`
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(title)}</title>
        <style>
          @page { size: A4; margin: 22mm 18mm; }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            color: #263d4f;
            font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
            background: #ffffff;
          }
          .cover {
            padding-bottom: 18px;
            margin-bottom: 26px;
            border-bottom: 3px solid #263d4f;
          }
          .kicker {
            margin: 0 0 10px;
            color: #496274;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
          }
          h1 {
            margin: 0;
            font-family: "SimSun", "Microsoft YaHei", serif;
            font-size: 28px;
            font-weight: 700;
            line-height: 1.3;
          }
          .meta {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 18px;
            margin-top: 18px;
            padding-top: 12px;
            border-top: 1px solid #a9b8c3;
            color: #496274;
            font-size: 12px;
          }
          .plan {
            white-space: pre-wrap;
            color: #30485a;
            font-size: 13.5px;
            line-height: 1.9;
          }
          .plan-line {
            margin: 0;
            white-space: pre-wrap;
          }
          .plan-heading {
            margin-top: 22px;
            margin-bottom: 14px;
            color: #263d4f;
            font-size: 19px;
            font-weight: 800;
            line-height: 1.45;
          }
          .plan-heading:first-child {
            margin-top: 0;
          }
          .plan-blank {
            min-height: 10px;
          }
          strong {
            color: #263d4f;
            font-weight: 800;
          }
        </style>
      </head>
      <body>
        <section class="cover">
          <p class="kicker">SMART CAREER PLANNING SYSTEM</p>
          <h1>${escapeHtml(title)}</h1>
          <div class="meta">
            <span>当前路径：${escapeHtml(path)}</span>
            <span>生成时间：${escapeHtml(generated)}</span>
          </div>
        </section>
        <main class="plan">${planHtml}</main>
      </body>
    </html>
  `)
  printWindow.document.close()
  printWindow.focus()

  setTimeout(() => {
    printWindow.print()
  }, 250)
}

async function sendQuestion(presetQuestion = '') {
  if (!userStore.isLogin || !userStore.userId) {
    aiError.value = '请先登录后再使用规划咨询。'
    return
  }

  const question = (presetQuestion || aiQuestion.value).trim()
  if (!question) {
    aiError.value = '请输入要咨询的问题。'
    return
  }

  aiLoading.value = true
  aiError.value = ''
  appendChatMessage('user', question)
  aiQuestion.value = ''

  try {
    const response = await askPlanningAI(userStore.userId, question)
    const data = response.data || response
    if (data.success) {
      appendChatMessage('assistant', toPlainText(data.answer) || '暂未形成回复。')
    } else {
      const message = data.error || '规划咨询暂时不可用，请稍后重试。'
      aiError.value = message
      appendChatMessage('assistant', message)
    }
  } catch (err) {
    const message = err.response?.data?.detail || err.message || '规划咨询请求失败，请稍后重试。'
    aiError.value = message
    appendChatMessage('assistant', message)
  } finally {
    aiLoading.value = false
  }
}

onMounted(() => {
  if (userStore.isLogin && userStore.userId) {
    loadRecommendation()
    loadChatMessages()
  }
})

watch(
  () => userStore.userId,
  () => {
    loadChatMessages()
  }
)

watch(
  () => chatMessages.value.length,
  () => {
    scrollChatToBottom()
  }
)
</script>

<style scoped>
/* 
 * 核心重构理念：
 * 1. 彻底去除所有 border-radius (圆角边框)
 * 2. 采用 Editorial / 档案风格，利用纯色、细线、锐利对比 
 * 3. 移除常见的对话气泡，改用 Q/A 访谈笔录的纯文本排版
 * 4. 动画用闪烁光标/方块替代常规加载圈
 */

* {
  box-sizing: border-box;
}

.planning-page {
  min-height: 100vh;
  background:
    linear-gradient(rgba(48, 72, 90, 0.42), rgba(38, 61, 79, 0.5)),
    url('../assets/planning_background.jpg') center / cover fixed;
  color: #263d4f;
  font-family: "Times New Roman", "Georgia", "PingFang SC", "Microsoft YaHei", serif;
  padding: 40px;
}

.planning-shell {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* ================= 通用文本样式 ================= */
.kicker-text {
  display: block;
  color: #496274;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* ================= 档案主卡片 ================= */
.plan-card {
  background: rgba(232, 239, 243, 0.93);
  border: 1px solid #8fa0ad;
  /* 取消模糊和轻柔阴影，改为硬朗的线条感 */
  box-shadow: 8px 8px 0px rgba(38, 61, 79, 0.32);
  margin-top: 60px;
}

.plan-header {
  padding: 48px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 48px;
  align-items: stretch;
  border-bottom: 2px solid #263d4f;
}

.header-titles h1 {
  margin: 16px 0;
  color: #263d4f;
  font-size: clamp(48px, 6vw, 84px);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  color: #41586a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.6;
}

.plan-stamp {
  padding-left: 32px;
  border-left: 1px solid #8fa0ad;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.plan-stamp label {
  color: #496274;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  letter-spacing: 1.5px;
  margin-bottom: 12px;
}

.select-wrapper {
  position: relative;
}

.plan-stamp select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #263d4f;
  background: transparent;
  color: #263d4f;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  font-weight: 500;
  outline: none;
  border-radius: 0;
  appearance: none;
  cursor: pointer;
}

.select-wrapper::after {
  content: '▼';
  font-size: 10px;
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #263d4f;
}

.stamp-desc {
  margin-top: 16px;
  color: #496274;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  line-height: 1.6;
}

/* ================= 状态区域 ================= */
.plan-state {
  padding: 80px 48px;
  text-align: center;
  border-bottom: 1px solid #8fa0ad;
}

.plan-state strong {
  display: block;
  margin-bottom: 12px;
  color: #263d4f;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 24px;
  letter-spacing: 2px;
}

.plan-state p {
  margin: 0;
  color: #41586a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.plan-state.danger strong,
.plan-state.danger p,
.consultation-error,
.yearly-error {
  color: #b91c1c;
}

/* 用闪烁的方块代替圆形的 Spinner，削弱 AI 味，增加终端/打字机感 */
.loading-block {
  width: 16px;
  height: 24px;
  background: #263d4f;
  margin: 0 auto 20px;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ================= 年度规划内容 ================= */
.plan-content {
  padding: 48px;
}

.yearly-plan {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 48px;
}

.yearly-head {
  position: sticky;
  top: 40px;
  align-self: start;
}

.yearly-head h2 {
  margin: 16px 0;
  color: #263d4f;
  font-size: 36px;
  font-weight: 600;
  line-height: 1.1;
}

.yearly-head p {
  color: #41586a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

.export-plan-btn {
  display: block;
  width: fit-content;
  margin: 18px 0 0 0;
}

.yearly-loading {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

.yearly-paper {
  min-height: 400px;
  padding: 32px;
  background: rgba(221, 231, 237, 0.88);
  border: 1px solid #a9b8c3;
  border-top: 4px solid #263d4f;
  color: #30485a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  line-height: 2;
}

.yearly-line {
  min-height: 1em;
  margin: 0;
  white-space: pre-wrap;
}

.yearly-line + .yearly-line {
  margin-top: 2px;
}

.yearly-line-heading {
  margin-top: 28px;
  margin-bottom: 18px;
  color: #263d4f;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.45;
}

.yearly-line-heading:first-child {
  margin-top: 0;
}

.yearly-line-blank {
  min-height: 12px;
  margin-top: 0;
}

.yearly-line strong {
  color: #263d4f;
  font-weight: 800;
}

.plan-footer {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid #a9b8c3;
  text-align: right;
  color: #9ca3af;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  letter-spacing: 1px;
}

/* ================= 问答模块 (无气泡纪实风格) ================= */
.consultation-panel {
  background: rgba(232, 239, 243, 0.93);
  border: 1px solid #8fa0ad;
  box-shadow: 8px 8px 0px rgba(38, 61, 79, 0.32);
}

.panel-inner {
  padding: 48px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.section-head h2 {
  margin: 12px 0 32px;
  color: #263d4f;
  font-size: 32px;
  font-weight: 600;
}

.clear-chat-btn {
  margin-top: 4px;
  padding: 8px 14px;
  border: 1px solid #8fa0ad;
  background: transparent;
  color: #30485a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.2s ease;
}

.clear-chat-btn:hover:not(:disabled) {
  border-color: #263d4f;
  background: #263d4f;
  color: #ffffff;
}

.clear-chat-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.notice {
  padding: 24px;
  border: 1px solid #263d4f;
  border-left: 6px solid #263d4f;
  background: rgba(221, 231, 237, 0.88);
}

.notice strong {
  display: block;
  font-size: 18px;
  margin-bottom: 8px;
}

/* 快捷问题按钮 */
.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
}

.sharp-btn-outline {
  padding: 10px 16px;
  border: 1px solid #8fa0ad;
  background: transparent;
  color: #30485a;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  cursor: pointer;
  border-radius: 0; /* 绝对无圆角 */
  transition: all 0.2s ease;
}

.sharp-btn-outline:hover:not(:disabled) {
  border-color: #263d4f;
  background: #263d4f;
  color: #ffffff;
}

/* 聊天记录 - 访谈记录流排版 */
.chat-dossier {
  display: flex;
  flex-direction: column;
  border-top: 1px solid #263d4f;
  border-bottom: 1px solid #263d4f;
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
  background: rgba(232, 239, 243, 0.78);
}

.empty-text {
  padding: 32px 0;
  color: #9ca3af;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
}

.dossier-entry {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  padding: 24px 0;
  border-bottom: 1px solid #a9b8c3;
}

.dossier-entry:last-child {
  border-bottom: none;
}

.entry-role {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #263d4f;
}

.dossier-entry.assistant .entry-role {
  color: #496274; /* AI 的前缀稍微浅一点，拉开层次 */
}

.entry-body p {
  margin: 0;
  color: #263d4f;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.dossier-entry.assistant .entry-body p {
  color: #30485a;
}

.entry-body small {
  display: block;
  margin-top: 12px;
  color: #9ca3af;
  font-size: 12px;
}

/* 输入框区域 - 矩阵式无缝衔接设计 */
.chat-input-matrix {
  margin-top: 32px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  border: 1px solid #263d4f;
  background: rgba(232, 239, 243, 0.93);
}

.chat-input-matrix textarea {
  width: 100%;
  resize: none;
  border: none;
  min-height: 20px;
  padding: 2px 10px;
  color: #263d4f;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  line-height: 1.35;
  outline: none;
  background: transparent;
}

.sharp-btn-solid {
  width: 100%;
  height: 100%;
  min-height: 20px;
  border: none;
  border-left: 1px solid #263d4f;
  background: #263d4f;
  color: #ffffff;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  cursor: pointer;
  border-radius: 0;
}

.sharp-btn-solid:disabled {
  background: #496274;
  cursor: not-allowed;
}

/* ================= 响应式调整 ================= */
@media (max-width: 1024px) {
  .plan-header {
    grid-template-columns: 1fr;
    gap: 32px;
    padding: 32px;
  }

  .plan-stamp {
    padding-left: 0;
    border-left: none;
    border-top: 1px solid #8fa0ad;
    padding-top: 24px;
  }

  .yearly-plan {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .yearly-head {
    position: static;
  }
}

@media (max-width: 768px) {
  .planning-page {
    padding: 20px;
  }

  .plan-state, .plan-content, .panel-inner {
    padding: 24px;
  }

  .header-titles h1 {
    font-size: clamp(36px, 10vw, 48px);
  }

  .chat-input-matrix {
    grid-template-columns: 1fr;
    grid-template-rows: auto 48px;
  }

  .sharp-btn-solid {
    border-left: none;
    border-top: 1px solid #263d4f;
  }
}
</style>

