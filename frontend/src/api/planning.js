import request from './request'

const AI_REQUEST_TIMEOUT = 300000
const YEARLY_PLAN_TIMEOUT = 600000

export const askPlanningAI = (userId, question) => {
  return request.post('/api/planning/chat', {
    user_id: userId,
    question
  }, {
    timeout: AI_REQUEST_TIMEOUT
  })
}

export const generateYearlyPlanning = (userId, selectedPath) => {
  return request.post('/api/planning/yearly-plan', {
    user_id: userId,
    selected_path: selectedPath
  }, {
    timeout: YEARLY_PLAN_TIMEOUT
  })
}
