<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 统计信息
const totalJournals = computed(() => userStore.journals.length)
const pendingJournals = computed(() => userStore.pendingJournals.length)
const totalUsers = computed(() => 2345) // 模拟数据
const recentSubmissions = computed(() => 45) // 模拟数据
</script>

<template>
  <div class="admin-dashboard-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-dashboard'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 管理员后台内容 -->
    <main class="dashboard-content">
      <div class="dashboard-header">
        <h1 class="dashboard-title">管理员后台</h1>
        <div class="user-info">
          <span class="welcome-message">欢迎，{{ user?.username }}</span>
        </div>
      </div>

      <!-- 平台统计信息 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalJournals }}</h3>
              <p class="stat-label">总投稿量</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingJournals }}</h3>
              <p class="stat-label">待审核稿件</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalUsers }}</h3>
              <p class="stat-label">注册用户</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ recentSubmissions }}</h3>
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
            v-for="journal in userStore.journals.slice(0, 5)" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
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
/* 样式可以从原组件复制或修改 */
</style>