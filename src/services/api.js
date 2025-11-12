/**
 * API 服務層
 * 封裝所有後端 API 請求
 */
import axios from 'axios'

// 建立 axios 實例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 秒超時
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 可以在這裡加入認證 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 統一錯誤處理
    const message = error.response?.data?.detail || error.message || '請求失敗'
    console.error('API 錯誤:', message)
    return Promise.reject(new Error(message))
  }
)

// 專案管理 API
export const projectAPI = {
  // 取得所有專案
  getProjects: () => api.get('/api/projects'),
  
  // 取得單一專案
  getProject: (id) => api.get(`/api/projects/${id}`),
  
  // 建立專案
  createProject: (data) => api.post('/api/projects', data),
  
  // 更新專案
  updateProject: (id, data) => api.put(`/api/projects/${id}`, data),
  
  // 刪除專案
  deleteProject: (id) => api.delete(`/api/projects/${id}`)
}

// 作業活動 API
export const activityAPI = {
  // 取得專案的所有作業
  getActivities: (projectId) => api.get(`/api/projects/${projectId}/activities`),
  
  // 取得單一作業
  getActivity: (id) => api.get(`/api/activities/${id}`),
  
  // 建立作業
  createActivity: (projectId, data) => api.post(`/api/projects/${projectId}/activities`, data),
  
  // 更新作業
  updateActivity: (id, data) => api.put(`/api/activities/${id}`, data),
  
  // 刪除作業
  deleteActivity: (id) => api.delete(`/api/activities/${id}`),
  
  // 取得作業的前置作業
  getPredecessors: (id) => api.get(`/api/activities/${id}/predecessors`)
}

// 優化計算 API
export const optimizationAPI = {
  // 執行優化計算
  optimize: (data) => api.post('/api/optimize', data),
  
  // 取得優化結果
  getResult: (scenarioId) => api.get(`/api/scenarios/${scenarioId}/results`)
}

export default api

