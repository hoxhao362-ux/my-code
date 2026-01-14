import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 创建并使用 Pinia
const pinia = createPinia()
app.use(pinia)

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')
