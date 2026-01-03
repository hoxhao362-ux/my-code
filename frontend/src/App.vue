<script setup>
import { ref, computed } from 'vue'

// 导入所有组件
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Home from './components/Home.vue'
import Submit from './components/Submit.vue'
import Review from './components/Review.vue'
import Profile from './components/Profile.vue'
import JournalDetail from './components/JournalDetail.vue'

// 应用状态管理
const currentPage = ref('login') // 当前页面
const user = ref(JSON.parse(localStorage.getItem('user')) || null) // 当前用户
const journalId = ref(null) // 当前查看的稿件ID

// 页面导航方法
const navigateTo = (page, id = null) => {
  currentPage.value = page
  if (id) {
    journalId.value = id
  }
}

// 登录方法
const login = (userData) => {
  user.value = userData
  localStorage.setItem('user', JSON.stringify(userData))
  navigateTo('home')
}

// 登出方法
const logout = () => {
  user.value = null
  localStorage.removeItem('user')
  navigateTo('login')
}

// 计算当前应该显示的组件
const CurrentComponent = computed(() => {
  switch (currentPage.value) {
    case 'login': return Login
    case 'register': return Register
    case 'home': return Home
    case 'submit': return Submit
    case 'review': return Review
    case 'profile': return Profile
    case 'journal': return JournalDetail
    default: return Login
  }
})

// 提供给子组件使用的方法和状态
const appContext = computed(() => {
  return {
    user: user.value,
    currentPage: currentPage.value,
    journalId: journalId.value,
    navigateTo,
    login,
    logout
  }
})
</script>

<template>
  <div class="app-container">
    <!-- 使用动态组件渲染当前页面 -->
    <component 
      :is="CurrentComponent" 
      v-bind="appContext"
    />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  line-height: 1.6;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>