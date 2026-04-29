import axios from 'axios'

const request = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token') || localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 不自动跳转
request.interceptors.response.use(
    response => {
        return response
    },
    error => {
        // 只返回错误，不进行页面跳转
        console.error('API错误:', error.response?.status, error.response?.data)
        return Promise.reject(error)
    }
)

export default request