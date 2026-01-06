<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 作者的投稿历史
const userJournals = computed(() => userStore.userJournals)
</script>

<template>
  <div class="author-dashboard-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'author-dashboard'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 作者后台内容 -->
    <main class="dashboard-content">
      <div class="dashboard-header">
        <h1 class="dashboard-title">作者后台</h1>
        <div class="user-info">
          <span class="welcome-message">欢迎，{{ user?.username }}</span>
        </div>
      </div>

      <!-- 作者统计信息 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ userJournals.length }}</h3>
              <p class="stat-label">总投稿数</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ userJournals.filter(j => j.status === '审稿中').length }}</h3>
              <p class="stat-label">待审核</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ userJournals.filter(j => j.status === '已通过').length }}</h3>
              <p class="stat-label">已通过</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">❌</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ userJournals.filter(j => j.status === '未通过').length }}</h3>
              <p class="stat-label">未通过</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">近期投稿</h2>
          <button class="submit-btn">+ 新投稿</button>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in userJournals.slice(0, 5)" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
              <p class="journal-meta">投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
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