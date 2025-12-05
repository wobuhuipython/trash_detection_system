import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 获取所有分类
export const getCategories = () => api.get('/categories')

// 获取分类详情
export const getCategoryDetail = (name) => api.get(`/category/${name}`)

// 搜索垃圾
export const searchGarbage = (keyword) => api.get('/search', { params: { keyword } })

// 获取知识列表
export const getKnowledge = (category = '') => api.get('/knowledge', { params: { category } })

// 获取知识详情
export const getKnowledgeDetail = (id) => api.get(`/knowledge/${id}`)

// 获取环保资讯
export const getNews = (category = '') => api.get('/news', { params: { category } })

// 获取资讯详情
export const getNewsDetail = (id) => api.get(`/news/${id}`)

// 获取统计数据
export const getStats = () => api.get('/stats')

export default api
