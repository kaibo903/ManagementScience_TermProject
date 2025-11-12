/**
 * Vue Router 路由配置
 * 定義應用程式的所有路由
 */
import { createRouter, createWebHistory } from 'vue-router'
import ProjectManagement from '../views/ProjectManagement.vue'
import BiddingOptimization from '../views/BiddingOptimization.vue'
import ResultAnalysis from '../views/ResultAnalysis.vue'

const routes = [
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/projects',
    name: 'ProjectManagement',
    component: ProjectManagement,
    meta: { title: '專案管理' }
  },
  {
    path: '/optimization',
    name: 'BiddingOptimization',
    component: BiddingOptimization,
    meta: { title: '投標優化' }
  },
  {
    path: '/results/:resultId?',
    name: 'ResultAnalysis',
    component: ResultAnalysis,
    meta: { title: '結果分析' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守衛：設定頁面標題
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 營造廠決策分析平台` : '營造廠決策分析平台'
  next()
})

export default router

