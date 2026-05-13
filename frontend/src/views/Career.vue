<template>
  <div
    class="career-page"
    :style="{
      backgroundImage: `linear-gradient(rgba(34, 74, 132, 0.16), rgba(34, 74, 132, 0.16)), url(${careerBackground})`
    }"
  >
    <FeaturePageNav current="career" />

    <main class="career-shell">
      <section class="cover">
        <span class="cover-label">ANALYSIS REPORT</span>
        <h1>
          <span class="title-primary">计算机专业职业规划</span>
          <span class="title-secondary">与推荐报告</span>
        </h1>
      </section>

      <section v-if="error" class="notice danger">
        <strong>提示</strong>
        <p>{{ error }}</p>
      </section>

      <section v-if="!userStore.isLogin" class="notice">
        <strong>请先登录</strong>
        <p>登录后，系统会按“个人画像 + 计算机能力画像 + 路径选择 + 职业推荐”生成推荐报告。</p>
      </section>

      <section v-if="userStore.isLogin && loading" class="notice">
        <strong>正在生成</strong>
        <p>系统正在整理个人画像、能力评估、方向匹配和岗位建议，请稍候。</p>
      </section>

      <section v-if="userStore.isLogin" class="input-sheet">
        <div class="section-head">
          <span>INPUT</span>
          <div>
            <h2>规划信息补充</h2>
            <p>这些信息需要你自己填写，系统会把它们和个人资料、能力评估一起用于推荐。</p>
          </div>
        </div>

        <div class="input-grid">
          <label>
            <span>学校层次</span>
            <select v-model="planningInput.school_level">
              <option value="">请选择</option>
              <option value="双一流/985/211">双一流/985/211</option>
              <option value="普通本科">普通本科</option>
              <option value="民办/独立学院">民办/独立学院</option>
              <option value="专科">专科</option>
              <option value="研究生">研究生</option>
            </select>
          </label>

          <label>
            <span>GPA（4.0制）</span>
            <input v-model.number="planningInput.gpa_score" type="number" min="0" max="4" step="0.01" placeholder="例如：3.50" />
          </label>

          <label>
            <span>专业排名</span>
            <select v-model="planningInput.rank_level">
              <option value="">请选择</option>
              <option value="前10%">前10%</option>
              <option value="前30%">前30%</option>
              <option value="前50%">前50%</option>
              <option value="50%以后">50%以后</option>
              <option value="不清楚">不清楚</option>
            </select>
          </label>

          <label>
            <span>英语四级</span>
            <input v-model.number="planningInput.cet4_score" type="number" min="0" max="710" step="1" placeholder="0-710，未考填0" />
          </label>

          <label>
            <span>英语六级</span>
            <input v-model.number="planningInput.cet6_score" type="number" min="0" max="710" step="1" placeholder="0-710，未考填0" />
          </label>

          <label>
            <span>雅思/托福</span>
            <input v-model="planningInput.language_test" type="text" placeholder="例如：雅思6.5 / 托福95，没有可空" />
          </label>

          <label>
            <span>期望城市</span>
            <input v-model="planningInput.expected_city" type="text" placeholder="例如：北京、上海、杭州、成都" />
          </label>

          <label>
            <span>经济约束</span>
            <select v-model="planningInput.economic_constraint">
              <option value="">请选择</option>
              <option value="需要尽快就业">需要尽快就业</option>
              <option value="可接受考研">可接受考研</option>
              <option value="可承担留学成本">可承担留学成本</option>
              <option value="希望稳定优先">希望稳定优先</option>
            </select>
          </label>

          <label>
            <span>项目数量</span>
            <select v-model.number="planningInput.project_count">
              <option :value="0">0 个</option>
              <option :value="1">1 个</option>
              <option :value="2">2 个</option>
              <option :value="3">3 个及以上</option>
            </select>
          </label>

          <label>
            <span>项目复杂度</span>
            <select v-model="planningInput.project_complexity">
              <option value="">请选择</option>
              <option value="课程小作业">课程小作业</option>
              <option value="完整 CRUD 项目">完整 CRUD 项目</option>
              <option value="前后端联调项目">前后端联调项目</option>
              <option value="上线/部署项目">上线/部署项目</option>
              <option value="科研/竞赛项目">科研/竞赛项目</option>
            </select>
          </label>

          <label>
            <span>是否部署</span>
            <select v-model="planningInput.has_deployment">
              <option value="">请选择</option>
              <option value="是">是</option>
              <option value="否">否</option>
            </select>
          </label>

          <label>
            <span>实习经历</span>
            <select v-model="planningInput.internship_status">
              <option value="">请选择</option>
              <option value="暂无">暂无</option>
              <option value="校内/实验室经历">校内/实验室经历</option>
              <option value="一段实习">一段实习</option>
              <option value="多段实习">多段实习</option>
            </select>
          </label>

          <label>
            <span>价值偏好</span>
            <select v-model="planningInput.value_preference">
              <option value="">请选择</option>
              <option value="高薪成长">高薪成长</option>
              <option value="稳定优先">稳定优先</option>
              <option value="研究深造">研究深造</option>
              <option value="城市机会">城市机会</option>
              <option value="低压力">低压力</option>
            </select>
          </label>

          <label class="full">
            <span>具体技术兴趣</span>
            <textarea v-model="planningInput.tech_interests" rows="3" placeholder="例如：后端、AI应用、数据分析、网络安全、嵌入式、产品"></textarea>
          </label>

          <label class="full">
            <span>补充说明</span>
            <textarea v-model="planningInput.extra_notes" rows="3" placeholder="例如：不想去一线城市、准备考研但担心数学、想优先找实习"></textarea>
          </label>
        </div>

        <div class="input-actions">
          <button type="button" class="text-btn" @click="resetPlanningInput">清空补充信息</button>
          <button type="button" class="solid-btn" @click="handleRegenerate" :disabled="loading">
            {{ loading ? '生成中...' : '根据补充信息重新生成' }}
          </button>
        </div>

        <div class="scoring-note">
          <strong>评分依据</strong>
          <p>系统会综合三类输入：个人资料用于判断专业、年级、兴趣和目标；能力评估用于判断编程算法、项目工程、计算机基础、调试排错等能力；本页补充信息用于判断 GPA、四六级、城市、项目、实习、经济约束和价值偏好。</p>
        </div>
      </section>

      <template v-if="userStore.isLogin && recommendation">
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

        <section class="profile-sheet">
          <div class="section-head">
            <span>01</span>
            <h2>个人画像</h2>
          </div>

          <div class="profile-grid">
            <article v-for="item in profileSnapshot" :key="item.label" class="profile-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <p>{{ item.detail }}</p>
            </article>
          </div>

          <div class="interest-grid">
            <article v-for="block in interestValues" :key="block.label" class="interest-card">
              <span>{{ block.label }}</span>
              <div v-if="block.items?.length" class="tag-list">
                <span v-for="item in block.items" :key="item">{{ item }}</span>
              </div>
              <p v-else>{{ block.empty }}</p>
            </article>
          </div>

          <div class="planning-input-snapshot">
            <article v-for="item in planningInputSnapshot" :key="item.label" class="input-snapshot-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </article>
          </div>
        </section>

        <section class="score-sheet">
          <div class="section-head">
            <span>02</span>
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

          <div v-if="topPathScoreDetail.length" class="score-detail">
            <h3>{{ pathResult.recommend_path || '推荐路径' }}评分依据</h3>
            <div class="score-detail-grid">
              <div v-for="item in topPathScoreDetail" :key="item.label">
                <span>{{ item.label }}</span>
                <strong>{{ formatScore(item.value) }}</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="career-layout">
          <article class="ability-sheet">
            <div class="section-head">
              <span>03</span>
              <h2>计算机能力画像</h2>
            </div>

            <div v-if="hasAbilityChart" class="ability-radar-wrap">
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
                <polygon class="radar-line" :points="radarPolygon" />

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

              <div class="ability-breakdown">
                <article v-for="item in abilityBreakdown" :key="item.key" class="ability-card">
                  <div>
                    <span>{{ item.label }}</span>
                    <strong>{{ formatScore(item.score) }}</strong>
                    <em>{{ item.level }}</em>
                  </div>
                  <p>{{ item.suggestion }}</p>
                  <div class="tag-list compact">
                    <span v-for="scope in item.covers" :key="scope">{{ scope }}</span>
                  </div>
                </article>
              </div>
            </div>

            <div v-else class="ability-empty">
              <strong>还没有计算机能力评估结果</strong>
              <p>请先到能力评估页面完成“计算机能力评估”。综合能力评估会作为表达、协作和执行力的辅助判断，但不会替代计算机能力画像。</p>
            </div>

            <div class="general-ability-panel" :class="{ muted: !hasGeneralAbility }">
              <div class="general-ability-head">
                <div>
                  <span>综合能力参与评分</span>
                  <strong>{{ hasGeneralAbility ? formatScore(generalAbilityAverage) : '未纳入' }}</strong>
                </div>
                <p>
                  {{ hasGeneralAbility
                    ? '已作为岗位匹配中的辅助权重，影响表达协作、学习节奏、抗压和执行力判断。'
                    : '完成“综合能力评估”后，这部分会进入岗位匹配评分。' }}
                </p>
              </div>

              <div v-if="hasGeneralAbility" class="general-score-grid">
                <div v-for="item in generalAbilityList" :key="item.key" class="general-score-item">
                  <span>{{ item.label }}</span>
                  <strong>{{ formatScore(item.value) }}</strong>
                  <div class="mini-track">
                    <div :style="{ width: `${clampScore(item.value)}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <article class="advice-sheet">
            <div class="section-head">
              <span>04</span>
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
            <span>05</span>
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

                  <div v-if="scoreDetailList(item).length" class="detail-block">
                    <h4>评分明细</h4>
                    <div class="score-chip-list">
                      <span v-for="score in scoreDetailList(item)" :key="score.label">
                        {{ score.label }} {{ formatScore(score.value) }}
                      </span>
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

      <section v-if="userStore.isLogin && !loading && !recommendation" class="notice">
        <strong>暂无结果</strong>
        <p>完善个人信息后点击“重新生成”，系统会生成个人画像、能力画像和方向匹配。</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
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

const defaultPlanningInput = {
  school_level: '',
  gpa_score: '',
  rank_level: '',
  cet4_score: '',
  cet6_score: '',
  language_test: '',
  expected_city: '',
  economic_constraint: '',
  project_count: 0,
  project_complexity: '',
  has_deployment: '',
  internship_status: '',
  value_preference: '',
  tech_interests: '',
  extra_notes: ''
}

const planningInput = reactive({ ...defaultPlanningInput })

const pathResult = computed(() => recommendation.value?.path_result || {})
const careerList = computed(() => recommendation.value?.career_list || [])
const adviceItems = computed(() => recommendation.value?.advice_list || [])
const topCareer = computed(() => careerList.value[0] || null)
const planningReport = computed(() => recommendation.value?.computer_planning || {})
const dataSource = computed(() => recommendation.value?.data_source || {})
const profileSnapshot = computed(() => planningReport.value.profile_snapshot || [])
const planningInputSnapshot = computed(() => planningReport.value.planning_input_snapshot || [])
const interestValues = computed(() => planningReport.value.interest_values || [])
const abilityBreakdown = computed(() => planningReport.value.ability_breakdown || [])
const pathScoreDetail = computed(() => planningReport.value.path_score_detail || {})


const pathScoreList = computed(() => [
  { key: 'job_score', label: '就业路径', value: Number(pathResult.value.job_score || 0) },
  { key: 'graduate_score', label: '考研路径', value: Number(pathResult.value.graduate_score || 0) },
  { key: 'civil_service_score', label: '考公路径', value: Number(pathResult.value.civil_service_score || 0) },
  { key: 'abroad_score', label: '留学路径', value: Number(pathResult.value.abroad_score || 0) }
])

const topPathScoreDetail = computed(() => {
  const pathName = pathResult.value.recommend_path
  const detail = pathScoreDetail.value[pathName] || {}
  const labels = {
    ability: '能力基础',
    interest: '目标意向',
    project: '项目经历',
    academic: '成绩基础',
    english: '英语基础',
    constraint: '现实约束'
  }
  return Object.entries(labels)
    .filter(([key]) => detail[key] !== undefined)
    .map(([key, label]) => ({
      label,
      value: detail[key]
    }))
})

const abilityList = computed(() => {
  const ability = recommendation.value?.ability_snapshot || {}
  const techScores = ability.tech_scores || {}
  const techList = [
    { key: 'programming', label: '编程', value: techScores.programming },
    { key: 'algorithm', label: '算法', value: techScores.algorithm },
    { key: 'computer_basic', label: '基础', value: techScores.computer_basic },
    { key: 'software_eng', label: '工程', value: techScores.software_eng },
    { key: 'backend', label: '后端', value: techScores.backend },
    { key: 'frontend', label: '前端', value: techScores.frontend },
    { key: 'database', label: '数据库', value: techScores.database },
    { key: 'network', label: '网络', value: techScores.network },
    { key: 'ai_ml', label: 'AI', value: techScores.ai_ml },
    { key: 'devops', label: '运维', value: techScores.devops }
  ].filter(item => item.value !== undefined)

  if (techList.length >= 6) return techList
  if (!dataSource.value.has_assessment) return []

  return [
    { key: 'logic', label: '编程算法', value: ability.logic },
    { key: 'innovation', label: '项目工程', value: ability.innovation },
    { key: 'communication', label: '项目表达', value: ability.communication },
    { key: 'learning', label: '计算机基础', value: ability.learning },
    { key: 'pressure', label: '调试排错', value: ability.pressure },
    { key: 'leadership', label: '规划执行', value: ability.leadership }
  ]
})

const hasAbilityChart = computed(() =>
  abilityList.value.length > 0 && abilityBreakdown.value.length > 0
)

const generalAbilityList = computed(() => {
  const scores = recommendation.value?.ability_snapshot?.general_scores || {}
  const items = [
    { key: 'logic', label: '逻辑思维', value: scores.logic },
    { key: 'innovation', label: '创新能力', value: scores.innovation },
    { key: 'communication', label: '沟通协作', value: scores.communication },
    { key: 'learning', label: '学习能力', value: scores.learning },
    { key: 'pressure', label: '抗压能力', value: scores.pressure },
    { key: 'leadership', label: '领导力', value: scores.leadership }
  ]
  return items.filter(item => item.value !== undefined && item.value !== null)
})

const hasGeneralAbility = computed(() =>
  dataSource.value.has_general_assessment && generalAbilityList.value.length > 0
)

const generalAbilityAverage = computed(() => {
  if (!generalAbilityList.value.length) return null
  const total = generalAbilityList.value.reduce((sum, item) => sum + Number(item.value || 0), 0)
  return total / generalAbilityList.value.length
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

function scoreDetailList(item) {
  const detail = item?.score_detail || {}
  const order = ['专业匹配', '技能匹配', '兴趣匹配', '计算机能力', '综合能力', '能力匹配', '补充信息匹配', '路径一致']
  return order
    .filter(label => detail[label] !== undefined)
    .map(label => ({
      label,
      value: detail[label]
    }))
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
    recommendation.value = await getCareerRecommendation(userStore.userId, buildPlanningPayload())
  } catch (err) {
    error.value = err.message || '获取职业规划与推荐失败。'
    recommendation.value = null
  } finally {
    loading.value = false
  }
}

function buildPlanningPayload() {
  const payload = {}
  Object.entries(planningInput).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      payload[key] = value
    }
  })
  return payload
}

function getPlanningInputKey() {
  return `career_planning_input_${userStore.userId || 'guest'}`
}

function savePlanningInput() {
  if (!userStore.userId) return
  localStorage.setItem(getPlanningInputKey(), JSON.stringify(buildPlanningPayload()))
}

function loadPlanningInput() {
  if (!userStore.userId) return
  try {
    const saved = localStorage.getItem(getPlanningInputKey())
    if (!saved) return
    Object.assign(planningInput, defaultPlanningInput, JSON.parse(saved))
  } catch (err) {
    Object.assign(planningInput, defaultPlanningInput)
  }
}

function resetPlanningInput() {
  Object.assign(planningInput, defaultPlanningInput)
  if (userStore.userId) {
    localStorage.removeItem(getPlanningInputKey())
  }
}

function handleRegenerate() {
  savePlanningInput()
  loadRecommendation()
}

onMounted(() => {
  if (userStore.isLogin && userStore.userId) {
    loadPlanningInput()
    loadRecommendation()
  }
})

watch(
  () => ({ ...planningInput }),
  () => savePlanningInput(),
  { deep: true }
)
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
.input-sheet,
.profile-sheet,
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
  top: 180px;
  z-index: 30;
  padding: 0;
  margin: 0;
  pointer-events: none;
}

.cover-label {
  display: block;
  margin: 0 0 16px 4px;
  color: rgba(190, 216, 234, 0.88);
  font-family: "Inter", "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.24em;
  line-height: 1;
  text-shadow: 0 8px 18px rgba(16, 38, 70, 0.28);
}

.cover h1 {
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
  gap: 12px;
  margin: 0;
  color: #e6f3ff;
  font-family: "Inter", "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
  font-size: clamp(48px, 5.4vw, 82px);
  font-weight: 800;
  line-height: 0.98;
  letter-spacing: 0.02em;
  text-shadow: 0 16px 34px rgba(16, 38, 70, 0.42);
  text-rendering: geometricPrecision;
  font-variant-ligatures: common-ligatures;
}

.cover h1 span {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  white-space: nowrap;
}

.title-primary {
  color: #e6f3ff;
  font-weight: 900;
}

.title-secondary {
  color: #9fbfd8;
  font-weight: 650;
}

.overview-block span,
.career-meta span,
.detail-grid span,
.profile-card span,
.interest-card > span {
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.notice p,
.overview-block p,
.section-head p,
.profile-card p,
.interest-card p,
.ability-card p,
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

.input-sheet {
  padding: 30px;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(53, 86, 138, 0.18);
  box-shadow: 0 14px 30px rgba(53, 86, 138, 0.08);
  backdrop-filter: blur(4px);
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.input-grid label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-grid label.full {
  grid-column: span 5;
}

.input-grid label > span {
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.input-grid input,
.input-grid select,
.input-grid textarea {
  width: 100%;
  min-height: 42px;
  border: 1px solid rgba(53, 86, 138, 0.22);
  background: rgba(255, 255, 255, 0.58);
  color: #3f4f5c;
  font: inherit;
  font-size: 14px;
  padding: 10px 12px;
  outline: none;
}

.input-grid textarea {
  resize: vertical;
  line-height: 1.6;
}

.input-actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  flex-wrap: wrap;
}

.scoring-note {
  margin-top: 18px;
  padding: 14px 16px;
  border-left: 4px solid #3f4f5c;
  background: rgba(255, 255, 255, 0.42);
}

.scoring-note strong {
  display: block;
  margin-bottom: 8px;
  color: #3f4f5c;
  font-size: 16px;
  font-weight: 500;
}

.scoring-note p {
  margin: 0;
  color: #8D97A7;
  font-size: 14px;
  line-height: 1.75;
}

.solid-btn {
  border: none;
  background: #3f4f5c;
  color: #ffffff;
  cursor: pointer;
  padding: 11px 18px;
  font-size: 14px;
}

.solid-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
.profile-sheet,
.recommend-sheet {
  padding: 30px;
  margin-bottom: 24px;
}

.profile-grid,
.interest-grid {
  display: grid;
  gap: 16px;
}

.profile-card,
.interest-card,
.ability-card {
  background: rgba(255, 255, 255, 0.46);
  border: 1px solid rgba(53, 86, 138, 0.13);
}

.profile-card,
.interest-card {
  padding: 20px;
}

.profile-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 18px;
}

.profile-card strong {
  display: block;
  margin: 12px 0 10px;
  color: #3f4f5c;
  font-size: 26px;
  font-weight: 500;
  line-height: 1.16;
}

.interest-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.planning-input-snapshot {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.input-snapshot-card {
  min-height: 92px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(53, 86, 138, 0.12);
}

.input-snapshot-card span {
  display: block;
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.input-snapshot-card strong {
  display: block;
  margin-top: 10px;
  color: #3f4f5c;
  font-size: 18px;
  font-weight: 500;
  line-height: 1.25;
}

.ability-breakdown {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 0;
}

.ability-card {
  padding: 16px;
}

.ability-card div:first-child {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.ability-card span,
.ability-card em {
  color: #8D97A7;
  font-size: 12px;
  font-style: normal;
}

.ability-card strong {
  color: #3f4f5c;
  font-size: 20px;
  font-weight: 500;
}

.ability-empty {
  min-height: 220px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(53, 86, 138, 0.14);
}

.ability-empty strong {
  color: #3f4f5c;
  font-size: 24px;
  font-weight: 500;
}

.ability-empty p {
  margin: 0;
  color: #8D97A7;
  font-size: 15px;
  line-height: 1.8;
}

.general-ability-panel {
  margin-top: 22px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(53, 86, 138, 0.14);
}

.general-ability-panel.muted {
  opacity: 0.82;
}

.general-ability-head {
  display: grid;
  grid-template-columns: minmax(180px, 0.34fr) minmax(0, 1fr);
  gap: 18px;
  align-items: center;
}

.general-ability-head span {
  display: block;
  color: #8D97A7;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.general-ability-head strong {
  display: block;
  margin-top: 8px;
  color: #3f4f5c;
  font-size: 32px;
  font-weight: 500;
  line-height: 1;
}

.general-ability-head p {
  margin: 0;
  color: #8D97A7;
  font-size: 14px;
  line-height: 1.8;
}

.general-score-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.general-score-item {
  min-width: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.36);
  border: 1px solid rgba(53, 86, 138, 0.1);
}

.general-score-item span {
  display: block;
  color: #8D97A7;
  font-size: 12px;
}

.general-score-item strong {
  display: block;
  margin: 8px 0 10px;
  color: #3f4f5c;
  font-size: 20px;
  font-weight: 500;
}

.mini-track {
  height: 5px;
  overflow: hidden;
  background: rgba(63, 79, 92, 0.14);
}

.mini-track div {
  height: 100%;
  background: #3f4f5c;
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

.score-table {
  border-top: none;
}

.score-row {
  display: grid;
  grid-template-columns: 120px 1fr 72px;
  gap: 18px;
  align-items: center;
  min-height: 64px;
}

.score-row span {
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

.score-row strong {
  color: #3f4f5c;
  font-size: 22px;
  font-weight: 500;
  text-align: right;
}

.score-detail {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid rgba(63, 79, 92, 0.18);
}

.score-detail h3 {
  margin: 0 0 14px;
  color: #3f4f5c;
  font-size: 20px;
  font-weight: 500;
}

.score-detail-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.score-detail-grid div {
  padding: 12px;
  background: rgba(255, 255, 255, 0.42);
}

.score-detail-grid span,
.score-chip-list span {
  color: #8D97A7;
  font-size: 12px;
}

.score-detail-grid strong {
  display: block;
  margin-top: 8px;
  color: #3f4f5c;
  font-size: 20px;
  font-weight: 500;
}

.career-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
}

.ability-radar-wrap {
  display: grid;
  grid-template-columns: minmax(300px, 0.78fr) minmax(620px, 1.22fr);
  gap: 24px;
  align-items: stretch;
}

.ability-radar {
  width: 100%;
  min-height: 420px;
  display: block;
  align-self: center;
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

.score-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.score-chip-list span {
  padding: 7px 10px;
  color: #3f4f5c;
  background: rgba(255, 255, 255, 0.48);
  border: 1px solid rgba(53, 86, 138, 0.12);
}

.tag-list.compact {
  gap: 8px;
  margin-top: 12px;
}

.tag-list.compact span {
  padding: 5px 8px;
  font-size: 12px;
}

@media (max-width: 1024px) {
  .overview,
  .career-layout,
  .profile-grid,
  .interest-grid,
  .planning-input-snapshot,
  .general-ability-head,
  .general-score-grid,
  .score-detail-grid {
    grid-template-columns: 1fr;
  }

  .ability-breakdown {
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
    top: 138px;
  }

  .score-sheet,
  .ability-sheet,
  .advice-sheet,
  .input-sheet,
  .profile-sheet,
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

  .input-grid {
    grid-template-columns: 1fr;
  }

  .input-grid label.full {
    grid-column: span 1;
  }

  .input-actions {
    justify-content: stretch;
  }

  .input-actions button {
    width: 100%;
  }

  .section-head h2 {
    font-size: 34px;
  }

  .ability-radar {
    min-height: 280px;
  }

  .ability-radar-wrap {
    grid-template-columns: 1fr;
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
