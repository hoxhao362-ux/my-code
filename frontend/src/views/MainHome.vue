<script setup>
import { ref, computed } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const user = computed(() => userStore.user)

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
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
      :toggle-directory="toggleDirectory"
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

      <!-- 平台公告 -->
      <section class="announcements-section">
        <h2 class="section-title">平台公告</h2>
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

      <!-- 最近浏览量最高的作品 -->
      <section class="top-journals-section">
        <div class="section-header">
          <h2 class="section-title">热门作品</h2>
          <p class="section-subtitle">最近浏览量最高的四篇作品</p>
        </div>
        <div class="journals-grid">
          <div 
            v-for="journal in topViewedJournals" 
            :key="journal.id" 
            class="top-journal-item"
          >
            <div class="top-journal-info">
              <h3 class="top-journal-title">{{ journal.title }}</h3>
              <p class="top-journal-meta">作者：{{ journal.author }} | 模块：{{ journal.module }}</p>
              <p class="top-journal-meta">投稿日期：{{ journal.date }} | 阅读量：{{ journal.viewCount || 0 }}</p>
            </div>
            <div class="top-journal-status" :class="journal.status.toLowerCase()">
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
}
</style>