import request from './request'

// 获取评估题目
export const getQuestions = () => {
    return request.get('/api/assessment/questions')
}

// 提交评估答案
export const submitAssessment = (answers) => {
    return request.post('/api/assessment/submit', { answers })
}

// 获取评估历史
export const getAssessmentHistory = () => {
    return request.get('/api/assessment/history')
}