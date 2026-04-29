<template>
  <div class="planning-page">
    <FeaturePageNav current="planning" />

    <main class="planning-shell">
      <section class="cover">
        <div class="cover-index">CAREER / PLAN / 2026</div>
        <div class="cover-main">
          <div>
            <p class="kicker">大学生智能职业规划系统</p>
            <h1>职业成长规划书</h1>
          </div>

          <div class="cover-side">
            <span>当前路径</span>
            <strong>{{ pathResult.recommend_path || '待生成' }}</strong>
            <p>{{ coverDescription }}</p>
          </div>
        </div>

        <div class="cover-actions">
          <button class="text-btn" @click="goProfile">完善个人信息</button>
          <button class="text-btn" @click="goCareer">查看职业推荐</button>
          <button class="solid-btn" @click="loadRecommendation" :disabled="loading">
            {{ loading ? '正在生成...' : '生成规划' }}
          </button>
        </div>
      </section>

      <section v-if="error" class="notice danger">
        <strong>提示</strong>
        <p>{{ error }}</p>
      </section>

      <section v-if="!userStore.isLogin" class="notice">
        <strong>请先登录</strong>
        <p>登录后，系统会结合你的个人信息、职业倾向和推荐结果生成成长规划。</p>
      </section>

      <section v-else-if="loading" class="notice">
        <strong>正在生成规划</strong>
        <p>系统正在整理推荐路径、技能差距和阶段任务，请稍候。</p>
      </section>

      <template v-else-if="recommendation">
        <section class="overview">
          <article class="overview-block primary">
            <span>推荐路径</span>
            <strong>{{ pathResult.recommend_path || '--' }}</strong>
            <p>{{ pathResult.analysis_text || '暂无路径分析。' }}</p>
          </article>

          <article class="overview-block">
            <span>首选职业</span>
            <strong>{{ topCareer?.career_name || '--' }}</strong>
            <p>匹配度 {{ formatScore(topCareer?.match_score) }} 分</p>
          </article>

          <article class="overview-block">
            <span>优先补强</span>
            <strong>{{ skillGaps[0] || '待明确' }}</strong>
            <p>{{ skillGaps.length ? `共识别 ${skillGaps.length} 个技能补强点` : '推荐结果中暂无技能差距。' }}</p>
          </article>
        </section>

        <section class="roadmap">
          <div class="section-head">
            <span>01</span>
            <h2>阶段路线</h2>
          </div>

          <div class="timeline">
            <article v-for="stage in roadmapStages" :key="stage.title" class="timeline-item">
              <div class="timeline-mark">{{ stage.index }}</div>
              <div class="timeline-content">
                <span>{{ stage.period }}</span>
                <h3>{{ stage.title }}</h3>
                <p>{{ stage.desc }}</p>
                <ol>
                  <li v-for="task in stage.tasks" :key="task">{{ task }}</li>
                </ol>
              </div>
            </article>
          </div>
        </section>

        <section class="planning-grid">
          <article class="sheet">
            <div class="section-head">
              <span>02</span>
              <h2>技能清单</h2>
            </div>

            <div v-if="skillGaps.length" class="skill-table">
              <div v-for="(skill, index) in skillGaps" :key="skill" class="skill-row">
                <span>{{ String(index + 1).padStart(2, '0') }}</span>
                <strong>{{ skill }}</strong>
                <em>{{ index < 3 ? '优先' : '储备' }}</em>
              </div>
            </div>
            <p v-else class="empty-text">暂无明确技能短板，可以先根据目标职业补充项目经验。</p>
          </article>

          <article class="sheet">
            <div class="section-head">
              <span>03</span>
              <h2>行动建议</h2>
            </div>

            <div v-if="adviceList.length" class="advice-list">
              <div v-for="(item, index) in adviceList" :key="item" class="advice-item">
                <span>{{ index + 1 }}</span>
                <p>{{ item }}</p>
              </div>
            </div>
            <p v-else class="empty-text">暂无建议，请先生成职业推荐结果。</p>
          </article>
        </section>
      </template>

      <section v-else class="notice">
        <strong>暂无规划</strong>
        <p>完善个人信息后点击“生成规划”，系统会自动生成阶段路线、技能清单和行动建议。</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import { getCareerRecommendation } from '../api/career'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const error = ref('')
const recommendation = ref(null)

const pathResult = computed(() => recommendation.value?.path_result || {})
const careerList = computed(() => recommendation.value?.career_list || [])
const topCareer = computed(() => careerList.value[0] || null)
const adviceList = computed(() => recommendation.value?.advice_list || [])

const skillGaps = computed(() => {
  const result = []
  careerList.value.forEach((career) => {
    ;(career.gap_skills || []).forEach((skill) => {
      if (skill && !result.includes(skill)) result.push(skill)
    })
  })
  return result.slice(0, 8)
})

const coverDescription = computed(() => {
  if (!userStore.isLogin) return '登录后即可生成专属职业成长路线。'
  if (loading.value) return '系统正在整理你的规划档案。'
  if (!recommendation.value) return '完善资料后生成一份可执行的成长规划。'
  return '规划已根据职业推荐结果生成，可继续完善资料后刷新。'
})

const roadmapStages = computed(() => {
  const pathName = pathResult.value.recommend_path || '目标方向'
  const careerName = topCareer.value?.career_name || '目标职业'
  const skills = skillGaps.value

  return [
    {
      index: 'A',
      period: '第 1 阶段 / 1-2 周',
      title: '定位与校准',
      desc: `把“${pathName}”从模糊倾向变成清晰目标，先完成资料、方向和衡量标准的校准。`,
      tasks: [
        '补全个人简介、兴趣方向、已有技能和职业目标',
        `阅读并确认“${careerName}”的岗位或升学要求`,
        skills[0] ? `优先梳理 ${skills[0]} 的学习路径` : '选择一个核心技能作为本阶段主线'
      ]
    },
    {
      index: 'B',
      period: '第 2 阶段 / 3-6 周',
      title: '能力补强',
      desc: '围绕推荐结果补齐短板，用可见产出替代泛泛学习。',
      tasks: [
        skills[1] ? `完成一个包含 ${skills[1]} 的小型练习` : '完成一个小型项目或专题练习',
        '每周记录一次学习结果、问题和下一步改进',
        '把练习成果整理成可展示的项目说明'
      ]
    },
    {
      index: 'C',
      period: '第 3 阶段 / 7-12 周',
      title: '成果打磨',
      desc: '把能力沉淀到简历、作品集、申请材料或面试表达中。',
      tasks: [
        skills[2] ? `继续补强 ${skills[2]} 并加入作品材料` : '补充一项进阶能力并形成证明材料',
        '整理简历、项目文档或升学申请材料',
        '更新个人信息并重新生成职业推荐，检查方向是否变化'
      ]
    }
  ]
})

function formatScore(value) {
  const score = Number(value)
  return Number.isFinite(score) ? score.toFixed(1) : '--'
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
  } catch (err) {
    error.value = err.message || '生成职业规划失败。'
    recommendation.value = null
  } finally {
    loading.value = false
  }
}

function goProfile() {
  router.push('/profile')
}

function goCareer() {
  router.push('/career')
}

onMounted(() => {
  if (userStore.isLogin && userStore.userId) {
    loadRecommendation()
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.planning-page {
  min-height: 100vh;
  background: #1f5d95;
  color: #1f5d95;
  font-family: "Times New Roman", "Georgia", "PingFang SC", "Microsoft YaHei", serif;
  padding: 34px;
}

.planning-shell {
  width: min(1280px, 100%);
  margin: 0 auto;
}

.cover,
.notice,
.overview-block,
.roadmap,
.sheet {
  background: #f5f5f3;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.cover {
  min-height: 520px;
  padding: 28px 42px 38px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-bottom: 26px;
}

.cover-index {
  color: #1f5d95;
  font-size: 18px;
  letter-spacing: 6px;
}

.cover-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 34px;
  align-items: end;
}

.kicker {
  margin: 0 0 16px;
  color: #5d84a8;
  font-size: 13px;
  letter-spacing: 2px;
}

.cover h1 {
  margin: 0;
  max-width: 760px;
  color: #1f5d95;
  font-size: clamp(68px, 10vw, 132px);
  font-weight: 500;
  line-height: 0.92;
  letter-spacing: 0;
}

.cover-side {
  border-left: 1px solid rgba(31, 93, 149, 0.35);
  padding-left: 24px;
}

.cover-side span,
.overview-block span,
.skill-row span,
.skill-row em {
  color: #5d84a8;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.cover-side strong {
  display: block;
  margin: 14px 0;
  color: #1f5d95;
  font-size: 42px;
  font-weight: 500;
  line-height: 1.05;
}

.cover-side p,
.notice p,
.overview-block p,
.timeline-content p,
.advice-item p,
.empty-text {
  margin: 0;
  color: #3d5a7a;
  font-size: 15px;
  line-height: 1.85;
}

.cover-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 18px;
  border-top: 1px solid rgba(31, 93, 149, 0.18);
  padding-top: 22px;
}

button {
  font-family: inherit;
}

.text-btn,
.solid-btn {
  border: none;
  cursor: pointer;
  padding: 11px 4px;
  font-size: 13px;
  letter-spacing: 1px;
}

.text-btn {
  background: transparent;
  color: #1f5d95;
  border-bottom: 1px solid rgba(31, 93, 149, 0.45);
}

.solid-btn {
  background: #1f5d95;
  color: #f5f5f3;
  padding: 12px 22px;
}

.solid-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.notice {
  padding: 30px 34px;
  margin-bottom: 24px;
  border-left: 8px solid #7fa3c4;
}

.notice strong {
  display: block;
  margin-bottom: 8px;
  color: #1f5d95;
  font-size: 28px;
  font-weight: 500;
}

.notice.danger {
  border-left-color: #a54a4a;
}

.overview {
  display: grid;
  grid-template-columns: 1.2fr 0.9fr 0.9fr;
  gap: 18px;
  margin-bottom: 24px;
}

.overview-block {
  min-height: 220px;
  padding: 26px;
  border-top: 8px solid rgba(127, 163, 196, 0.65);
}

.overview-block.primary {
  border-top-color: #1f5d95;
}

.overview-block strong {
  display: block;
  margin: 14px 0;
  color: #1f5d95;
  font-size: 38px;
  font-weight: 500;
  line-height: 1.1;
}

.roadmap,
.sheet {
  padding: 30px;
  margin-bottom: 24px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
}

.section-head > span {
  color: #7fa3c4;
  font-size: 20px;
  letter-spacing: 2px;
}

.section-head h2 {
  margin: 0;
  color: #1f5d95;
  font-size: 44px;
  line-height: 1;
  font-weight: 500;
}

.timeline {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid rgba(31, 93, 149, 0.35);
  border-left: 1px solid rgba(31, 93, 149, 0.35);
}

.timeline-item {
  min-height: 420px;
  display: grid;
  grid-template-rows: 90px 1fr;
  border-right: 1px solid rgba(31, 93, 149, 0.35);
  border-bottom: 1px solid rgba(31, 93, 149, 0.35);
  background: #ffffff;
}

.timeline-mark {
  display: flex;
  align-items: center;
  padding: 0 22px;
  border-bottom: 1px solid rgba(31, 93, 149, 0.18);
  color: #1f5d95;
  font-size: 46px;
  line-height: 1;
}

.timeline-content {
  padding: 24px 22px 28px;
}

.timeline-content span {
  color: #5d84a8;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.timeline-content h3 {
  margin: 16px 0 12px;
  color: #1f5d95;
  font-size: 34px;
  font-weight: 500;
  line-height: 1.08;
}

.timeline-content ol {
  margin: 20px 0 0;
  padding-left: 20px;
  color: #3d5a7a;
  line-height: 1.8;
}

.timeline-content li + li {
  margin-top: 8px;
}

.planning-grid {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 24px;
}

.skill-table {
  border-top: 1px solid rgba(31, 93, 149, 0.26);
}

.skill-row {
  display: grid;
  grid-template-columns: 52px 1fr 54px;
  align-items: center;
  min-height: 58px;
  border-bottom: 1px solid rgba(31, 93, 149, 0.18);
}

.skill-row strong {
  color: #1f5d95;
  font-size: 20px;
  font-weight: 500;
}

.skill-row em {
  font-style: normal;
  text-align: right;
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.advice-item {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(31, 93, 149, 0.18);
}

.advice-item span {
  color: #1f5d95;
  font-size: 28px;
  line-height: 1;
}

@media (max-width: 1024px) {
  .cover-main,
  .overview,
  .timeline,
  .planning-grid {
    grid-template-columns: 1fr;
  }

  .cover-side {
    border-left: none;
    border-top: 1px solid rgba(31, 93, 149, 0.35);
    padding: 22px 0 0;
  }

  .timeline-item {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .planning-page {
    padding: 18px 14px 28px;
  }

  .cover,
  .roadmap,
  .sheet,
  .notice,
  .overview-block {
    padding: 20px;
  }

  .cover {
    min-height: 500px;
  }

  .cover-index {
    font-size: 13px;
    letter-spacing: 3px;
  }

  .cover h1 {
    font-size: clamp(52px, 18vw, 78px);
  }

  .cover-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .text-btn,
  .solid-btn {
    width: 100%;
    text-align: center;
  }

  .section-head h2 {
    font-size: 34px;
  }

}
</style>
