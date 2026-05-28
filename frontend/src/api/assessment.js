import request from './request'

// 获取评估题目
export const getQuestions = (assessmentType = 'tech') => {
    return request.get('/api/assessment/questions', { params: { type: assessmentType } })
}

// 提交评估答案
export const submitAssessment = (answers, userId = null, assessmentType = 'tech') => {
    return request.post('/api/assessment/submit', {
        answers,
        user_id: userId,
        assessment_type: assessmentType
    }, {
        timeout: 300000
    })
}

// 获取评估历史
export const getAssessmentHistory = (userId, assessmentType = null) => {
    const config = assessmentType ? { params: { type: assessmentType } } : undefined
    return request.get(`/api/assessment/history/${userId}`, config)
}
