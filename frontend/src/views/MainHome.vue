<script setup>
import { ref, computed } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const router = useRouter()

// 处理投稿按钮点击事件
const goToSubmit = () => {
  if (user.value) {
    // 已登录用户直接跳转到投稿系统的投稿页面
    router.push('/admin/author-submit')
  } else {
    // 未登录用户跳转到第二层登录页面
    router.push('/submission/login')
  }
}

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 从userStore获取公告数据
const announcements = computed(() => userStore.announcements)

// 近期投稿列表（取前4条）
const recentJournals = computed(() => {
  return userStore.journals.slice(0, 4)
})

// 最近浏览量最高的四篇作品
const topViewedJournals = computed(() => {
  return [...userStore.journals]
    .sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
    .slice(0, 4)
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
      :logout="userStore.logout"
    />

    <!-- Main Content -->
    <main class="main-content">
      <!-- Platform Stats -->
      <section class="stats-section">
        <h2 class="section-title">Platform Statistics</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalJournals }}</h3>
              <p class="stat-label">Total Submissions</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.pendingReviews }}</h3>
              <p class="stat-label">Pending Reviews</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalUsers }}</h3>
              <p class="stat-label">Registered Users</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.recentSubmissions }}</h3>
              <p class="stat-label">Recent Submissions</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Announcements -->
      <section class="announcements-section">
        <h2 class="section-title">Announcements</h2>
        <div class="announcements-list">
          <div 
            v-for="announcement in announcements" 
            :key="announcement.id" 
            class="announcement-item"
          >
            <div class="announcement-header">
              <h3 class="announcement-title">{{ announcement.title }}</h3>
              <span class="announcement-date">{{ announcement.date }}</span>
            </div>
            <p class="announcement-content">{{ announcement.content }}</p>
          </div>
        </div>
      </section>

      <!-- Recent Submissions -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">Recent Submissions</h2>
          <button 
            class="submit-btn"
            @click="goToSubmit"
          >
            Submit your paper
          </button>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">Author: {{ journal.author }} | Date: {{ journal.date || journal.submissionDate }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase().replace(' ', '-')">
              {{ journal.status }}
            </div>
          </div>
        </div>
      </section>

      <!-- Top Viewed -->
      <section class="top-journals-section">
        <div class="section-header">
          <h2 class="section-title">Popular Articles</h2>
          <p class="section-subtitle">Top 4 most viewed articles</p>
        </div>
        <div class="journals-grid">
          <div 
            v-for="journal in topViewedJournals" 
            :key="journal.id" 
            class="top-journal-item"
          >
            <div class="top-journal-info">
              <h3 class="top-journal-title">{{ journal.title }}</h3>
              <p class="top-journal-meta">Author: {{ journal.author }} | Module: {{ journal.module }}</p>
              <p class="top-journal-meta">Date: {{ journal.date || journal.submissionDate }} | Views: {{ journal.viewCount || 0 }}</p>
            </div>
            <div class="top-journal-status" :class="journal.status.toLowerCase().replace(' ', '-')">
              {{ journal.status }}
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #2c3e50;
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

/* 近期投稿 */
.journals-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.submit-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
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

.journal-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  min-width: 80px;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.审稿中 {
  background: #3498db;
  color: white;
}

.journal-status.未通过 {
  background: #e74c3c;
  color: white;
}

/* 平台公告样式 */
.announcements-section {
  margin-bottom: 2rem;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.announcement-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #f39c12;
  transition: all 0.3s ease;
}

.announcement-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.announcement-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.announcement-date {
  font-size: 0.9rem;
  color: #7f8c8d;
  background: #f8f9fa;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
}

.announcement-content {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

/* 热门作品样式 */
.top-journals-section {
  margin-bottom: 2rem;
}

.section-subtitle {
  font-size: 1rem;
  color: #7f8c8d;
  margin: 0.5rem 0 1.5rem 0;
  font-weight: 400;
}

.journals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.top-journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.top-journal-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.top-journal-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  line-height: 1.4;
  transition: color 0.3s ease;
  cursor: pointer;
}

.top-journal-title:hover {
  color: #3498db;
}

.top-journal-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0;
  line-height: 1.5;
}

.top-journal-status {
  align-self: flex-start;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
}

.top-journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.top-journal-status.审稿中 {
  background: #3498db;
  color: white;
}

.top-journal-status.未通过 {
  background: #e74c3c;
  color: white;
}

/* 页脚 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .journals-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  /* 目录响应式调整 */
  .journal-directory-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .journal-directory-actions {
    align-items: stretch;
  }
}
</style>