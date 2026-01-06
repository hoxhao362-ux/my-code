<script setup>
import { ref, computed } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 近期投稿列表（取前4条）
const recentJournals = computed(() => {
  return userStore.journals.slice(0, 4)
})

// 搜索相关状态
const searchKeyword = ref('')
const searchStatus = ref('all')
const searchModule = ref('all')
const searchResults = ref([])
const showSearchResults = ref(false)
</script>

<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'home'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 首页内容 -->
    <main class="main-content">
      <!-- 平台统计 -->
      <section class="stats-section">
        <h2 class="section-title">平台统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalJournals }}</h3>
              <p class="stat-label">总投稿量</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.pendingReviews }}</h3>
              <p class="stat-label">待审核稿件</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalUsers }}</h3>
              <p class="stat-label">注册用户</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.recentSubmissions }}</h3>
              <p class="stat-label">近期投稿</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">近期投稿</h2>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase()">
              {{ journal.status }}
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 样式可以从原 Home.vue 组件复制 */
</style>