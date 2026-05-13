import request from './request'

export const askPlanningAI = (userId, question) => {
  return request.post('/api/planning/chat', {
    user_id: userId,
    question
  })
}
