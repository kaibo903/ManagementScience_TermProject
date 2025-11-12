import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhTw from 'element-plus/dist/locale/zh-tw.mjs'
import router from './router'
import App from './App.vue'
import './style.css'
import ECharts from 'vue-echarts'

// 建立 Vue 應用程式
const app = createApp(App)

// 註冊 Element Plus
app.use(ElementPlus, {
  locale: zhTw
})

// 註冊所有 Element Plus 圖示
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 註冊 vue-echarts
app.component('v-chart', ECharts)

// 註冊路由
app.use(router)

// 掛載應用程式
app.mount('#app')
