<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { editorApi, adminApi } from '../../utils/api'
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
  if (role === 'admin') return t('dashboard.roles.admin')
  if (role === 'editor') return t('dashboard.roles.editor')
  if (role === 'associate_editor') return t('dashboard.roles.associate_editor')
  if (role === 'ea_ae') return t('dashboard.roles.ea_ae')
  return t('dashboard.roles.default')
})

// 真实看板统计数据
const stats = ref({
  total_manuscripts: 0,
  pending_manuscripts: 0,
  under_review: 0,
  completed_reviews: 0,
  total_users: 0,
  recent_submissions: 0,
  user_roles: {}
})

// 近期投稿列表
const recentJournalsList = ref([])
const isLoading = ref(false)

// 页面加载时拉取后端数据（根据角色调用不同API）
onMounted(async () => {
  try {
    isLoading.value = true
    
    const role = user.value?.role
    
    if (role === 'admin') {
      // 管理员：调用 adminApi.getDashboard
      const dashboardRes = await adminApi.getDashboard()
      const data = dashboardRes.data || dashboardRes
      
      stats.value = {
        total_manuscripts: data.total_journals || data.totalJournals || 0,
        pending_manuscripts: 0,
        under_review: 0,
        completed_reviews: 0,
        total_users: data.total_users || data.totalUsers || 0,
        recent_submissions: 0,
        user_roles: data.user_roles || data.userRoles || {}
      }
      
      recentJournalsList.value = []
    } else {
      // 编辑：调用 editorApi.getDashboard
      const dashboardRes = await editorApi.getDashboard()
      const data = dashboardRes.data?.statistics || dashboardRes.statistics || dashboardRes.data || dashboardRes
      
      stats.value = {
        total_manuscripts: data.total_manuscripts || data.totalManuscripts || 0,
        pending_manuscripts: data.pending_manuscripts || data.pendingManuscripts || 0,
        under_review: data.under_review || data.underReview || 0,
        completed_reviews: data.completed_reviews || data.completedReviews || 0,
        total_users: data.total_users || data.totalUsers || 0,
        recent_submissions: data.recent_submissions || data.recentSubmissions || 0,
        user_roles: {}
      }
      
      const pendingList = dashboardRes.data?.pending_list || dashboardRes.pending_list || []
      recentJournalsList.value = pendingList.slice(0, 5)
    }
  } catch (error) {
    console.error('获取看板数据失败:', error)
    stats.value = {
      total_manuscripts: filteredJournalsFallback.value.length,
      pending_manuscripts: pendingJournalsFallback.value.length,
      under_review: 0,
      completed_reviews: 0,
      total_users: 2345,
      recent_submissions: 45,
      user_roles: {}
    }
  } finally {
    isLoading.value = false
  }
})

// Fallback: 旧的 Mock 数据逻辑（仅当后端不可用时使用）
const filteredJournalsFallback = computed(() => {
  let list = userStore.journals
  const role = user.value?.role
  if (role === 'editor') return list
  return list
})

const pendingJournalsFallback = computed(() => filteredJournalsFallback.value.filter(j => 
  j.status === 'Pending' || 
  j.status === 'Under Review' || 
  j.status === 'pending_initial_review' ||
  j.status === 'initial_review_passed' ||
  j.status === 'under_peer_review' ||
  j.status === 'review_completed' ||
  j.status === 'final_decision_pending'
).length)

// 统计信息（使用后端数据，Fallback 到 Mock）
const totalJournals = computed(() => stats.value.total_manuscripts || filteredJournalsFallback.value.length)
const pendingJournals = computed(() => stats.value.pending_manuscripts || pendingJournalsFallback.value.length)
const totalUsers = computed(() => stats.value.total_users || 2345)
const recentSubmissions = computed(() => stats.value.recent_submissions || 45)

// 近期投稿（优先使用后端列表）
const recentJournals = computed(() => {
  if (recentJournalsList.value.length > 0) {
    return recentJournalsList.value
  }
  return filteredJournalsFallback.value.slice(0, 5)
})

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
  if (status === 'Published' || status === 'accepted' || status === 'published') return t('status.published')
  if (status === 'Pending' || status === 'pending_initial_review') return t('status.pending_initial_review')
  if (status === 'initial_review_passed') return t('status.initial_review_passed')
  if (status === 'Under Review' || status === 'under_peer_review' || status === 'under_review') return t('status.under_review')
  if (status === 'review_completed') return t('status.review_completed')
  if (status === 'final_decision_pending') return t('status.pending_final_decision')
  if (status === 'Rejected' || status === 'rejected' || status === 'initial_review_rejected') return t('status.initial_review_rejected')
  if (status === 'revision_required') return t('status.revision_required')
  return status
}

const getStatusClass = (status) => {
  const s = status?.toLowerCase()
  if (s === 'published' || s === 'accepted') return 'published'
  if (s === 'pending' || s === 'pending_initial_review' || s === 'initial_review_passed' || s === 'under_peer_review' || s === 'under_review' || s === 'review_completed' || s === 'final_decision_pending' || s === 'revision_required') return 'pending'
  if (s === 'rejected' || s === 'initial_review_rejected') return 'rejected'
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
              <p class="stat-label">{{ t('dashboard.stats.totalJournals') }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingJournals }}</h3>
              <p class="stat-label">{{ t('dashboard.stats.pendingJournals') }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ totalUsers }}</h3>
              <p class="stat-label">{{ t('dashboard.stats.totalUsers') }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ recentSubmissions }}</h3>
              <p class="stat-label">{{ t('dashboard.stats.recentSubmissions') }}</p>
            </div>
          </div>
          
          <!-- New Widgets for Reviewer Management -->
          <div class="stat-card action-card" @click="navigateTo('/editor/audit/recommended-reviewers')">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingRecommendations }}</h3>
              <p class="stat-label">{{ t('dashboard.stats.authorRecommendations') }}</p>
              <span class="action-hint">{{ t('dashboard.stats.pendingApproval') }}</span>
            </div>
          </div>
          
          <div class="stat-card action-card" @click="navigateTo('/editor/audit/opposed-reviewers')">
            <div class="stat-content">
              <h3 class="stat-number">{{ pendingOppositions }}</h3>
              <p class="stat-label">{{ t('dashboard.stats.avoidanceRequests') }}</p>
              <span class="action-hint">{{ t('dashboard.stats.pendingReview') }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 用户角色分布（仅管理员可见） -->
      <section v-if="user?.role === 'admin' && Object.keys(stats.user_roles).length > 0" class="stats-section">
        <div class="section-header">
          <h2 class="section-title">{{ t('dashboard.userRoles.title') }}</h2>
        </div>
        <div class="stats-grid">
          <div v-for="(count, role) in stats.user_roles" :key="role" class="stat-card">
            <div class="stat-content">
              <h3 class="stat-number">{{ count }}</h3>
              <p class="stat-label">{{ t(`dashboard.userRoles.${role}`, role) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">{{ t('dashboard.recentJournals.title') }}</h2>
        </div>
        <div class="journals-list">
          <div v-if="isLoading" class="loading-state">{{ t('common.loading') }}</div>
          <div 
            v-else
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h4 class="journal-title">{{ journal.title }}</h4>
              <p class="journal-meta">{{ t('dashboard.recentJournals.author') }}: {{ journal.author }} | {{ t('dashboard.recentJournals.date') }}: {{ journal.date || journal.submissionDate }}</p>
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
        <p>{{ t('auth.footer.copyright') }}</p>
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