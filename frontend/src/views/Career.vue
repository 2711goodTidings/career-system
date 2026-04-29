<template>
  <div class="career-page" :style="{ backgroundImage: `url(${careerBackground})` }">
    <FeaturePageNav current="career" />

    <main class="career-shell">
      <section class="cover">
        <h1>职业规划与推荐报告</h1>
      </section>

      <section v-if="error" class="notice danger">
        <strong>提示</strong>
        <p>{{ error }}</p>
      </section>

      <section v-if="!userStore.isLogin" class="notice">
        <strong>请先登录</strong>
        <p>登录后，系统会结合你的个人信息、兴趣技能和职业目标生成规划与推荐。</p>
      </section>

      <section v-else-if="loading" class="notice">
        <strong>正在生成</strong>
        <p>系统正在计算职业路径、能力画像和推荐职业，请稍候。</p>
      </section>

      <template v-else-if="recommendation">
        <section class="overview">
          <article class="overview-block primary">
            <div class="ticket-stub">
              <span>路径结论</span>
              <strong>{{ pathResult.recommend_path || '--' }}</strong>
            </div>
            <span class="ticket-notch" aria-hidden="true"></span>
            <div class="ticket-main">
              <p>{{ pathResult.analysis_text || '暂无路径分析。' }}</p>
            </div>
          </article>

          <article class="overview-block">
            <span>推荐职业</span>
            <strong>{{ careerList.length }}</strong>
            <p>已生成 {{ careerList.length }} 个候选方向。</p>
          </article>

          <article class="overview-block">
            <span>最高匹配</span>
            <strong>{{ formatScore(topCareer?.match_score) }}</strong>
            <p>{{ topCareer?.career_name || '暂无最高匹配职业' }}</p>
          </article>
        </section>

        <section class="score-sheet">
          <div class="section-head">
            <span>01</span>
            <h2>路径评分</h2>
          </div>

          <div class="score-table">
            <div v-for="item in pathScoreList" :key="item.key" class="score-row">
              <span>{{ item.label }}</span>
              <div class="score-track">
                <div class="score-fill" :style="{ width: `${clampScore(item.value)}%` }"></div>
              </div>
              <strong>{{ formatScore(item.value) }}</strong>
            </div>
          </div>
        </section>

        <section class="career-layout">
          <article class="ability-sheet">
            <div class="section-head">
              <span>02</span>
              <h2>能力画像</h2>
            </div>

            <div class="ability-radar-wrap">
              <svg class="ability-radar" viewBox="0 0 360 360" role="img" aria-label="能力画像雷达图">
                <g class="radar-grid">
                  <polygon
                    v-for="level in radarLevels"
                    :key="level"
                    :points="radarGridPoints(level)"
                  />
                  <line
                    v-for="axis in radarAxis"
                    :key="axis.key"
                    x1="180"
                    y1="180"
                    :x2="axis.x"
                    :y2="axis.y"
                  />
                </g>

                <polygon class="radar-area" :points="radarPolygon" />
                <polyline class="radar-line" :points="radarPolygon" />

                <g class="radar-dots">
                  <circle
                    v-for="point in radarPoints"
                    :key="point.key"
                    :cx="point.x"
                    :cy="point.y"
                    r="4"
                  />
                </g>

                <g class="radar-labels">
                  <text
                    v-for="axis in radarAxis"
                    :key="axis.key"
                    :x="axis.labelX"
                    :y="axis.labelY"
                    text-anchor="middle"
                    dominant-baseline="middle"
                  >
                    {{ axis.label }}
                  </text>
                </g>
              </svg>

              <div class="ability-list">
                <div v-for="item in abilityList" :key="item.key" class="ability-row">
                  <span>{{ item.label }}</span>
                  <strong>{{ formatScore(item.value) }}</strong>
                </div>
              </div>
            </div>
          </article>

          <article class="advice-sheet">
            <div class="section-head">
              <span>03</span>
              <h2>发展建议</h2>
            </div>

            <div v-if="adviceItems.length" class="advice-list">
              <div v-for="(item, index) in adviceItems" :key="item" class="advice-item">
                <span>{{ index + 1 }}</span>
                <p>{{ item }}</p>
              </div>
            </div>
            <p v-else class="empty-text">暂无建议，请先生成职业推荐结果。</p>
          </article>
        </section>

        <section class="recommend-sheet">
          <div class="section-head recommend-head">
            <span>04</span>
            <div>
              <h2>推荐职业</h2>
              <p>鼠标悬停可预览详情，点击卡片可固定展开。</p>
            </div>
          </div>

          <div class="career-list">
            <article
              v-for="(item, index) in careerList"
              :key="item.career_id"
              class="career-item"
              :class="{ expanded: isCardExpanded(item.career_id) }"
              @mouseenter="setHover(item.career_id)"
              @mouseleave="clearHover"
              @click="toggleCard(item.career_id)"
            >
              <div class="career-number">{{ String(index + 1).padStart(2, '0') }}</div>

              <div class="career-main">
                <div class="career-meta">
                  <span>{{ item.category || '职业方向' }}</span>
                  <span>{{ item.industry || '行业待补充' }}</span>
                </div>

                <h3>{{ item.career_name || '未命名职业' }}</h3>

                <div class="career-facts">
                  <span>匹配度 {{ formatScore(item.match_score) }}</span>
                  <span>路径 {{ item.recommend_path || '--' }}</span>
                  <span>薪资 {{ formatSalary(item.avg_salary) }}</span>
                </div>

                <div class="career-detail">
                  <p>{{ item.description || '暂无职业描述。' }}</p>

                  <div class="detail-grid">
                    <div>
                      <span>学历要求</span>
                      <strong>{{ item.education_require || '--' }}</strong>
                    </div>
                    <div>
                      <span>成长潜力</span>
                      <strong>{{ item.growth_potential || '--' }}</strong>
                    </div>
                  </div>

                  <div v-if="item.reasons?.length" class="detail-block">
                    <h4>推荐理由</h4>
                    <div class="tag-list">
                      <span v-for="reason in item.reasons" :key="reason">{{ reason }}</span>
                    </div>
                  </div>

                  <div v-if="item.gap_skills?.length" class="detail-block">
                    <h4>建议补强</h4>
                    <div class="tag-list">
                      <span v-for="skill in item.gap_skills" :key="skill">{{ skill }}</span>
                    </div>
                  </div>

                  <div class="detail-block">
                    <h4>适配技能</h4>
                    <p>{{ item.suitable_skills || item.skill_require || '暂无技能说明。' }}</p>
                  </div>

                  <div class="detail-block">
                    <h4>工作内容</h4>
                    <p>{{ item.work_content || '暂无工作内容说明。' }}</p>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </section>
      </template>

      <section v-else class="notice">
        <strong>暂无结果</strong>
        <p>完善个人信息后点击“重新生成”，系统会生成路径评分、能力画像与推荐职业。</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import FeaturePageNav from '../components/FeaturePageNav.vue'
import { getCareerRecommendation } from '../api/career'
import careerBackground from '../assets/career_background.jpg'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const loading = ref(false)
const error = ref('')
const recommendation = ref(null)
const hoveredId = ref(null)
const fixedOpenId = ref(null)

const pathResult = computed(() => recommendation.value?.path_result || {})
const careerList = computed(() => recommendation.value?.career_list || [])
const adviceItems = computed(() => recommendation.value?.advice_list || [])
const topCareer = computed(() => careerList.value[0] || null)

const pathScoreList = computed(() => [
  { key: 'job_score', label: '就业路径', value: Number(pathResult.value.job_score || 0) },
  { key: 'graduate_score', label: '考研路径', value: Number(pathResult.value.graduate_score || 0) },
  { key: 'civil_service_score', label: '考公路径', value: Number(pathResult.value.civil_service_score || 0) },
  { key: 'abroad_score', label: '留学路径', value: Number(pathResult.value.abroad_score || 0) }
])

const abilityList = computed(() => {
  const ability = recommendation.value?.ability_snapshot || {}
  return [
    { key: 'logic', label: '逻辑思维', value: ability.logic },
    { key: 'innovation', label: '创新能力', value: ability.innovation },
    { key: 'communication', label: '沟通协作', value: ability.communication },
    { key: 'learning', label: '学习能力', value: ability.learning },
    { key: 'pressure', label: '抗压能力', value: ability.pressure },
    { key: 'leadership', label: '领导力', value: ability.leadership }
  ]
})

const radarLevels = [0.2, 0.4, 0.6, 0.8, 1]
const radarCenter = 180
const radarRadius = 112

function radarPoint(index, total, ratio, radiusOffset = 0) {
  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / total
  const radius = radarRadius * ratio + radiusOffset
  return {
    x: radarCenter + Math.cos(angle) * radius,
    y: radarCenter + Math.sin(angle) * radius
  }
}

function radarGridPoints(level) {
  return abilityList.value
    .map((_, index) => {
      const point = radarPoint(index, abilityList.value.length, level)
      return `${point.x},${point.y}`
    })
    .join(' ')
}

const radarPoints = computed(() =>
  abilityList.value.map((item, index) => {
    const point = radarPoint(index, abilityList.value.length, clampScore(item.value) / 100)
    return {
      ...item,
      ...point
    }
  })
)

const radarAxis = computed(() =>
  abilityList.value.map((item, index) => {
    const axisPoint = radarPoint(index, abilityList.value.length, 1)
    const labelPoint = radarPoint(index, abilityList.value.length, 1, 34)
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

function clampScore(value) {
  const score = Number(value || 0)
  return Math.min(100, Math.max(0, score))
}

function formatScore(value) {
  const score = Number(value)
  return Number.isFinite(score) ? score.toFixed(1) : '--'
}

function formatSalary(value) {
  if (value === null || value === undefined || value === '') return '面议'
  return `${value} / 月`
}

function isCardExpanded(id) {
  return fixedOpenId.value === id || (!fixedOpenId.value && hoveredId.value === id)
}

function setHover(id) {
  if (!fixedOpenId.value) hoveredId.value = id
}

function clearHover() {
  if (!fixedOpenId.value) hoveredId.value = null
}

function toggleCard(id) {
  fixedOpenId.value = fixedOpenId.value === id ? null : id
  hoveredId.value = null
}

async function loadRecommendation() {
  if (!userStore.isLogin || !userStore.userId) {
    error.value = '请先登录后再使用职业规划与推荐功能。'
    recommendation.value = null
    return
  }

  loading.value = true
  error.value = ''
  fixedOpenId.value = null
  hoveredId.value = null

  try {
    recommendation.value = await getCareerRecommendation(userStore.userId)
  } catch (err) {
    error.value = err.message || '获取职业规划与推荐失败。'
    recommendation.value = null
  } finally {
    loading.value = false
  }
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

.career-page {
  min-height: 100vh;
  background-color: #E7E8E4;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: #3f4f5c;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif;
  padding: 34px 34px 34px 176px;
}

.career-shell {
  width: min(1320px, 100%);
  margin: 0 auto;
  padding-top: 72px;
}

.notice,
.overview-block,
.score-sheet,
.ability-sheet,
.advice-sheet,
.recommend-sheet {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(53, 86, 138, 0.18);
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
  clip-path: polygon(
    12px 0,
    calc(100% - 12px) 0,
    100% 12px,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    12px 100%,
    0 calc(100% - 12px),
    0 12px
  );
}

.cover {
  position: fixed;
  left: 118px;
  top: 112px;
  z-index: 30;
  padding: 0;
  margin: 0;
  pointer-events: none;
}

.cover h1 {
  margin: 0;
  color: #ffffff;
  font-family: "SimSun", "Songti SC", "STSong", serif;
  font-size: clamp(54px, 6vw, 96px);
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0.08em;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  white-space: normal;
}

.overview-block span,
.career-meta span,
.detail-grid span {
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.notice p,
.overview-block p,
.recommend-head p,
.career-detail p,
.advice-item p,
.empty-text {
  margin: 0;
  color: #8D97A7;
  font-size: 15px;
  line-height: 1.85;
}

button {
  font-family: inherit;
}

.notice {
  padding: 30px 34px;
  margin-bottom: 24px;
  border-left: 8px solid #8D97A7;
}

.notice strong {
  display: block;
  margin-bottom: 8px;
  color: #3f4f5c;
  font-size: 28px;
  font-weight: 500;
}

.notice.danger {
  border-left-color: #a54a4a;
}

.overview {
  display: grid;
  grid-template-columns: 1.25fr 0.75fr 0.85fr;
  gap: 18px;
  margin-bottom: 24px;
}

.overview-block {
  min-height: 220px;
  padding: 26px;
  position: relative;
  overflow: hidden;
}

.overview-block.primary {
  display: grid;
  grid-template-columns: 112px 1px minmax(0, 1fr);
  gap: 0;
  align-items: stretch;
  padding: 0;
  overflow: visible;
  background: transparent;
  border: none;
  box-shadow: none;
  backdrop-filter: none;
  clip-path: none;
}

.ticket-stub {
  min-height: 220px;
  padding: 26px 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(53, 86, 138, 0.18);
  border-right: none;
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
  clip-path: polygon(
    12px 0,
    calc(100% - 12px) 0,
    100% 12px,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    12px 100%,
    0 calc(100% - 12px),
    0 12px
  );
}

.ticket-stub span {
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.ticket-stub strong {
  margin: 0;
  color: #3f4f5c;
  font-size: 34px;
  font-weight: 500;
  line-height: 1;
}

.ticket-main {
  min-width: 0;
  min-height: 220px;
  padding: 30px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(53, 86, 138, 0.18);
  border-left: none;
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
  clip-path: polygon(
    12px 0,
    calc(100% - 12px) 0,
    100% 12px,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    12px 100%,
    0 calc(100% - 12px),
    0 12px
  );
}

.ticket-notch {
  align-self: stretch;
  width: 1px;
  min-height: 220px;
  border-left: 1px dashed rgba(53, 86, 138, 0.36);
  pointer-events: none;
  position: relative;
  z-index: 3;
}

.overview-block strong {
  display: block;
  margin: 14px 0;
  color: #3f4f5c;
  font-size: 38px;
  font-weight: 500;
  line-height: 1.1;
}

.overview-block .ticket-stub strong {
  margin: 0;
  font-size: 34px;
  line-height: 1;
}

.score-sheet,
.ability-sheet,
.advice-sheet,
.recommend-sheet {
  padding: 30px;
  margin-bottom: 24px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  position: relative;
}

.section-head::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: rgba(63, 79, 92, 0.72);
}

.section-head > span {
  color: #8D97A7;
  font-size: 20px;
  letter-spacing: 2px;
}

.section-head h2 {
  margin: 0;
  color: #3f4f5c;
  font-size: 44px;
  line-height: 1;
  font-weight: 500;
}

.score-table,
.ability-list {
  border-top: none;
}

.score-row {
  display: grid;
  grid-template-columns: 120px 1fr 72px;
  gap: 18px;
  align-items: center;
  min-height: 64px;
}

.score-row span,
.ability-row span {
  color: #8D97A7;
  font-size: 15px;
}

.score-track {
  height: 10px;
  background: rgba(127, 163, 196, 0.25);
}

.score-fill {
  height: 100%;
  background: #3f4f5c;
}

.score-row strong,
.ability-row strong {
  color: #3f4f5c;
  font-size: 22px;
  font-weight: 500;
  text-align: right;
}

.career-layout {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 24px;
}

.ability-radar-wrap {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) 190px;
  gap: 22px;
  align-items: center;
}

.ability-radar {
  width: 100%;
  min-height: 320px;
  display: block;
}

.radar-grid polygon {
  fill: none;
  stroke: rgba(31, 93, 149, 0.22);
  stroke-width: 1;
}

.radar-grid line {
  stroke: rgba(31, 93, 149, 0.18);
  stroke-width: 1;
}

.radar-area {
  fill: rgba(31, 93, 149, 0.22);
  stroke: none;
}

.radar-line {
  fill: none;
  stroke: #3f4f5c;
  stroke-width: 2;
}

.radar-dots circle {
  fill: #3f4f5c;
  stroke: rgba(255, 255, 255, 0.86);
  stroke-width: 2;
}

.radar-labels text {
  fill: #8D97A7;
  font-size: 12px;
  letter-spacing: 0;
}

.ability-row {
  display: grid;
  grid-template-columns: 1fr 70px;
  align-items: center;
  min-height: 52px;
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
}

.advice-item span {
  color: #3f4f5c;
  font-size: 28px;
  line-height: 1;
}

.recommend-head {
  justify-content: space-between;
}

.career-list {
  border-top: none;
}

.career-item {
  display: grid;
  grid-template-columns: 86px 1fr;
  gap: 22px;
  padding: 28px 0;
  cursor: pointer;
}

.career-number {
  color: #8D97A7;
  font-size: 48px;
  line-height: 1;
}

.career-meta,
.career-facts,
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
}

.career-main h3 {
  margin: 12px 0 14px;
  color: #3f4f5c;
  font-size: 42px;
  font-weight: 500;
  line-height: 1.08;
}

.career-facts span {
  color: #8D97A7;
  font-size: 14px;
}

.career-detail {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.32s ease, opacity 0.18s ease, margin-top 0.32s ease;
}

.career-item.expanded .career-detail {
  max-height: 1200px;
  opacity: 1;
  margin-top: 22px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0;
}

.detail-grid div {
  padding: 16px;
  background: rgba(255, 255, 255, 0.42);
}

.detail-grid strong {
  display: block;
  margin-top: 8px;
  color: #3f4f5c;
  font-size: 18px;
  font-weight: 500;
}

.detail-block {
  margin-top: 18px;
}

.detail-block h4 {
  margin: 0 0 10px;
  color: #3f4f5c;
  font-size: 16px;
  font-weight: 500;
}

.tag-list span {
  padding: 7px 10px;
  color: #3f4f5c;
  background: rgba(127, 163, 196, 0.22);
  font-size: 13px;
}

@media (max-width: 1024px) {
  .overview,
  .career-layout {
    grid-template-columns: 1fr;
  }

  .ability-radar-wrap {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .career-page {
    padding: 18px 14px 28px 96px;
  }

  .career-shell {
    padding-top: 64px;
  }

  .cover {
    left: 58px;
    top: 86px;
  }

  .score-sheet,
  .ability-sheet,
  .advice-sheet,
  .recommend-sheet,
  .notice,
  .overview-block {
    padding: 20px;
  }

  .overview-block.primary {
    grid-template-columns: 88px 1px minmax(0, 1fr);
    padding: 0;
  }

  .ticket-stub {
    min-height: 190px;
    padding: 20px 12px;
  }

  .overview-block .ticket-stub strong {
    font-size: 28px;
  }

  .ticket-main {
    padding: 24px 20px 24px 0;
  }

  .cover h1 {
    font-size: 42px;
  }

  .section-head h2 {
    font-size: 34px;
  }

  .ability-radar {
    min-height: 280px;
  }

  .score-row {
    grid-template-columns: 1fr 58px;
  }

  .score-track {
    grid-column: 1 / -1;
    grid-row: 2;
  }

  .career-item {
    grid-template-columns: 1fr;
  }

  .career-main h3 {
    font-size: 32px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

}
</style>
