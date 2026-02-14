<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
<<<<<<< HEAD

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 统计信息
const totalJournals = computed(() => userStore.journals.length)
const pendingJournals = computed(() => userStore.pendingJournals.length)
const totalUsers = computed(() => 2345) // 模拟数据
const recentSubmissions = computed(() => 45) // 模拟数据
=======
import { useI18n } from '../../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

// Dashboard Title based on role
const dashboardTitle = computed(() => {
  const role = user.value?.role
  if (role === 'admin') return 'Editor-in-Chief Dashboard'
  if (role === 'editor') return 'Editor Dashboard'
  if (role === 'associate_editor') return 'Associate Editor Dashboard'
  if (role === 'editorial_assistant') return 'Editorial Assistant Dashboard'
  if (role === 'advisory_editor') return 'Advisory Editor Dashboard'
  return 'Dashboard'
})

// Filtered Journals based on role
const filteredJournals = computed(() => {
  let list = userStore.journals
  const role = user.value?.role
  const username = user.value?.username

  if (role === 'editor') {
    // Mock: Editor sees journals assigned to them (author matches for demo or specific field)
    // For now, return all for demo, or filter by some logic if data supported it
    // Let's filter by a mock property 'assignedTo' if it existed, but userStore.journals is simple.
    // We will just return all for now but label it "Assigned Manuscripts"
    return list
  }
  // AE sees all
  // Advisory sees subset
  return list
})

// 统计信息
const totalJournals = computed(() => filteredJournals.value.length)
const pendingJournals = computed(() => filteredJournals.value.filter(j => j.status === '待审核' || j.status === '审稿中').length)
const totalUsers = computed(() => 2345) // Mock
const recentSubmissions = computed(() => 45) // Mock
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
</script>

<template>
  <div class="admin-dashboard-container">
    <!-- 导航栏 -->
    <Navigation 
<<<<<<< HEAD
=======
      v-if="!embedded"
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
      :user="user"
      :current-page="'admin-dashboard'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 管理员后台内容 -->
<<<<<<< HEAD
    <main class="dashboard-content">
      <div class="dashboard-header">
        <h1 class="dashboard-title">管理员后台</h1>
        <div class="user-info">
          <span class="welcome-message">欢迎，{{ user?.username }}</span>
=======
    <main class="dashboard-content" :class="{ 'embedded-content': embedded }">
      <div class="dashboard-header">
        <h1 class="dashboard-title">{{ dashboardTitle }}</h1>
        <div class="user-info">
          <span class="welcome-message">{{ t('dashboard.welcome', { name: user?.username }) }}</span>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
        </div>
      </div>

      <!-- 平台统计信息 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalJournals }}</h3>
<<<<<<< HEAD
              <p class="stat-label">总投稿量</p>
=======
              <p class="stat-label">Total Manuscripts</p>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingJournals }}</h3>
<<<<<<< HEAD
              <p class="stat-label">待审核稿件</p>
=======
              <p class="stat-label">Pending Reviews</p>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalUsers }}</h3>
<<<<<<< HEAD
              <p class="stat-label">注册用户</p>
=======
              <p class="stat-label">Registered Users</p>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ recentSubmissions }}</h3>
<<<<<<< HEAD
              <p class="stat-label">近期投稿</p>
=======
              <p class="stat-label">Recent Submissions</p>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            </div>
          </div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
<<<<<<< HEAD
          <h2 class="section-title">近期投稿</h2>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in userStore.journals.slice(0, 5)" 
=======
          <h2 class="section-title">Recent Manuscripts</h2>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in filteredJournals.slice(0, 5)" 
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
<<<<<<< HEAD
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase()">
              {{ journal.status }}
=======
              <p class="journal-meta">Author: {{ journal.author }} | Date: {{ journal.date || journal.submissionDate }}</p>
            </div>
            <div class="journal-status" :class="journal.status === '已发表' ? 'published' : journal.status === '待审核' ? 'pending' : 'rejected'">
              {{ journal.status === '已发表' ? 'Published' : journal.status === '待审核' ? 'Pending' : journal.status === '审稿中' ? 'Under Review' : 'Rejected' }}
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
<<<<<<< HEAD
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
=======
    <footer class="footer" v-if="!embedded">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 管理员后台样式 */
.admin-dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 导航栏已在Navigation组件中处理 */

/* 主内容 */
.dashboard-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

<<<<<<< HEAD
=======
.dashboard-content.embedded-content {
  margin-top: 0;
}

>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
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

/* 近期投稿部分 */
.journals-section {
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

<<<<<<< HEAD
.journal-status.已通过 {
=======
.journal-status.published {
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  background: #2ecc71;
  color: white;
}

<<<<<<< HEAD
.journal-status.审稿中 {
  background: #3498db;
  color: white;
}

.journal-status.未通过 {
=======
.journal-status.pending {
  background: #f1c40f;
  color: white;
}

.journal-status.rejected {
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  background: #e74c3c;
  color: white;
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

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
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
  
  .journal-status {
    align-self: flex-end;
  }
}
</style>