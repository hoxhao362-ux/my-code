<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

// 待审核稿件
const pendingJournals = computed(() => {
  return userStore.pendingJournals
})

// 已审核稿件
const reviewedJournals = computed(() => {
  return userStore.journals.filter(journal => journal.status !== '审稿中')
})
</script>

<template>
  <div class="reviewer-dashboard-container">
    <!-- 导航栏 -->
    <!-- 导航栏会在布局组件中统一处理 -->

    <!-- 审核员后台内容 -->
    <main class="dashboard-content">
      <div class="dashboard-header">
        <h1 class="dashboard-title">审核员后台</h1>
        <div class="user-info">
          <span class="welcome-message">欢迎，{{ userStore.user?.username }}</span>
        </div>
      </div>

      <!-- 审核员统计信息 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingJournals.length }}</h3>
              <p class="stat-label">待审核稿件</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ reviewedJournals.filter(j => j.status === '已通过').length }}</h3>
              <p class="stat-label">已通过</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">❌</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ reviewedJournals.filter(j => j.status === '未通过').length }}</h3>
              <p class="stat-label">未通过</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ reviewedJournals.length }}</h3>
              <p class="stat-label">总审核数</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 待审核稿件列表 -->
      <section class="pending-journals-section">
        <div class="section-header">
          <h2 class="section-title">待审核稿件</h2>
          <a href="/reviewer/pending" class="view-all-link">查看全部</a>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in pendingJournals.slice(0, 5)" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
            </div>
            <div class="journal-actions">
              <button class="btn btn-review">开始审核</button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 样式可以根据需要自定义 */
</style>