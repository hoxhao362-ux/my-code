<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { useI18n } from '../../composables/useI18n'

const { t } = useI18n()
const router = useRouter()
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
  
  if (role === 'editor') {
    return list
  }
  return list
})

// 统计信息
const totalJournals = computed(() => filteredJournals.value.length)
const pendingJournals = computed(() => filteredJournals.value.filter(j => 
  j.status === 'Pending' || 
  j.status === 'Under Review' || 
  j.status === '待审核' || 
  j.status === '审稿中' ||
  j.status === 'pending_initial_review' ||
  j.status === 'initial_review_passed' ||
  j.status === 'under_peer_review' ||
  j.status === 'review_completed' ||
  j.status === 'final_decision_pending'
).length)
const totalUsers = computed(() => 2345) // Mock
const recentSubmissions = computed(() => 45) // Mock

// New Stats for Reviewer Management
const pendingRecommendations = computed(() => {
  return (userStore.recommendedReviewers || []).filter(r => r.status === 'pending').length
})

const pendingOppositions = computed(() => {
  return (userStore.opposedReviewers || []).filter(r => r.status === 'pending').length
})

// Navigation Helpers
const navigateTo = (path) => {
  // If embedded (in portal), we might need to emit event or just push. 
  // Since Navigation component handles 'navigate' event in portal, 
  // but here we are inside Dashboard which is a child.
  // The simplest way for portal to catch this is if we use the same route mechanism.
  // The portal watches route changes.
  router.push(path)
}

// Helper for status display
const getStatusLabel = (status) => {
  if (status === 'Published' || status === '已发表' || status === 'accepted') return 'Accepted'
  if (status === 'Pending' || status === '待审核' || status === 'pending_initial_review') return 'Pending'
  if (status === 'initial_review_passed') return 'Screening Passed'
  if (status === 'Under Review' || status === '审稿中' || status === 'under_peer_review') return 'Under Review'
  if (status === 'review_completed') return 'Review Completed'
  if (status === 'final_decision_pending') return 'Decision Pending'
  if (status === 'Rejected' || status === '已拒稿' || status === 'rejected' || status === 'initial_review_rejected') return 'Rejected'
  if (status === 'revision_required') return 'Revision Required'
  return status
}

const getStatusClass = (status) => {
  if (status === 'Published' || status === '已发表' || status === 'accepted') return 'published'
  if (status === 'Pending' || status === '待审核' || status === 'pending_initial_review') return 'pending'
  if (status === 'initial_review_passed') return 'pending'
  if (status === 'Under Review' || status === '审稿中' || status === 'under_peer_review') return 'pending' // pending color (yellow)
  if (status === 'review_completed') return 'pending'
  if (status === 'final_decision_pending') return 'pending'
  if (status === 'Rejected' || status === '已拒稿' || status === 'rejected' || status === 'initial_review_rejected') return 'rejected'
  if (status === 'revision_required') return 'pending'
  return ''
}
</script>

<template>
  <div class="admin-dashboard-container">
    <!-- 导航栏 -->
    <Navigation 
      v-if="!embedded"
      :user="user"
      :current-page="'admin-dashboard'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 管理员后台内容 -->
    <main class="dashboard-content" :class="{ 'embedded-content': embedded }">
      <div class="dashboard-header">
        <h1 class="dashboard-title">{{ dashboardTitle }}</h1>
        <div class="user-info">
          <span class="welcome-message">{{ t('dashboard.welcome', { name: user?.username }) }}</span>
        </div>
      </div>

      <!-- 平台统计信息 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ totalJournals }}</h3>
              <p class="stat-label">Total Manuscripts</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingJournals }}</h3>
              <p class="stat-label">Pending Reviews</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ totalUsers }}</h3>
              <p class="stat-label">Registered Users</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ recentSubmissions }}</h3>
              <p class="stat-label">Recent Submissions</p>
            </div>
          </div>
          
          <!-- New Widgets for Reviewer Management -->
          <div class="stat-card action-card" @click="navigateTo('/editor/audit/recommended-reviewers')">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingRecommendations }}</h3>
              <p class="stat-label">Writer Recommendations</p>
              <span class="action-hint">Pending Approval</span>
            </div>
          </div>
          
          <div class="stat-card action-card" @click="navigateTo('/editor/audit/opposed-reviewers')">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingOppositions }}</h3>
              <p class="stat-label">Avoidance Requests</p>
              <span class="action-hint">Pending Review</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">Recent Manuscripts</h2>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in filteredJournals.slice(0, 5)" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
              <p class="journal-meta">Writer: {{ journal.writer || journal.author }} | Date: {{ journal.date || journal.submissionDate }}</p>
            </div>
            <div class="journal-status" :class="getStatusClass(journal.status)">
              {{ getStatusLabel(journal.status) }}
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer" v-if="!embedded">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
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

.dashboard-content.embedded-content {
  margin-top: 0;
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease;
}

.stat-card.action-card {
  cursor: pointer;
  border-left: 3px solid #3498db;
}

.stat-card.action-card:hover {
  background-color: #f8fbfe;
}

.stat-card:hover {
  background-color: #f9f9f9;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0.25rem 0 0 0;
  font-size: 0.85rem;
}

.action-hint {
  display: inline-block;
  margin-top: 0.3rem;
  font-size: 0.7rem;
  color: #e67e22;
  background: #fff3e0;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
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

.journal-status.published {
  background: #2ecc71;
  color: white;
}

.journal-status.pending {
  background: #f1c40f;
  color: white;
}

.journal-status.rejected {
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