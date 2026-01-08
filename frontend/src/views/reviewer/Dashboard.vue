<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

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
    <Navigation 
      :user="userStore.user"
      :current-page="'reviewer-dashboard'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

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
/* 审核员后台样式 */
.reviewer-dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 主内容 */
.dashboard-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

/* 仪表盘头部 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-message {
  font-size: 1.1rem;
  color: #34495e;
  font-weight: 500;
}

/* 统计部分 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

/* 待审核稿件部分 */
.pending-journals-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.view-all-link {
  color: #3498db;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.view-all-link:hover {
  color: #2980b9;
  text-decoration: underline;
}

.journals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.journal-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.journal-meta {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
}

.journal-actions {
  display: flex;
  gap: 0.5rem;
}

/* 按钮样式 */
.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-review {
  background: #3498db;
  color: white;
}

.btn-review:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .dashboard-title {
    font-size: 1.6rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .journal-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .journal-actions {
    align-self: flex-end;
  }
}
</style>