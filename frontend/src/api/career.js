const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const message = response.status === 405
      ? '后端还未重启到新版接口，请重启 FastAPI 后端后再重新生成。'
      : data.detail || '请求失败'
    throw new Error(message)
  }

  return data
}

export function getCareerRecommendation(userId, planningInput = null) {
  if (planningInput) {
    return request(`/career/recommendation/${userId}`, {
      method: 'POST',
      body: JSON.stringify(planningInput)
    })
  }

  return request(`/career/recommendation/${userId}`)
}

export function seedDefaultCareers() {
  return request('/career/seed-defaults')
}

export { API_BASE_URL }
