import request from './request'

export const askPlanningAI = (userId, question) => {
  return request.post('/api/planning/chat', {
    user_id: userId,
    question
  })
}

export const generateYearlyPlanning = (userId, selectedPath) => {
  return request.post('/api/planning/yearly-plan', {
    user_id: userId,
    selected_path: selectedPath
  }, {
    timeout: 180000
  })
}
