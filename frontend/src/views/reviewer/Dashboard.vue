<script setup>
<<<<<<< HEAD
import { computed } from 'vue'
=======
import { computed, ref, onMounted, onUnmounted } from 'vue'
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
<<<<<<< HEAD

// 待审核稿件 - 审核员只看到复审阶段，管理员看到初审和终审阶段
const pendingJournals = computed(() => {
  const isAdmin = userStore.user?.role === 'admin'
  const allowedStages = isAdmin ? ['初审', '终审'] : ['复审']
  
  return userStore.pendingJournals.filter(journal => {
    return allowedStages.includes(journal.reviewStage)
  })
})

// 已审核稿件
const reviewedJournals = computed(() => {
  const isAdmin = userStore.user?.role === 'admin'
  const username = userStore.user?.username
  
  if (isAdmin) {
    return userStore.journals.filter(journal => journal.status !== '审稿中' && journal.status !== '待审核')
  } else {
    return userStore.journals.filter(journal => {
      // 只显示已通过或未通过的稿件，且审核员参与了复审
      return (journal.status === '已通过' || journal.status === '未通过') && 
             journal.reviewHistory && 
             journal.reviewHistory.some(record => record.stage === '复审' && record.reviewer === username)
    })
  }
})

// 查看稿件详情
const viewJournalDetail = (id) => {
  router.push(`/admin/journal/${id}`)
}
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
              <h4 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }} <span class="view-detail-icon">📋</span></h4>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
            </div>
            <div class="journal-actions">
              <button class="btn btn-review">开始审核</button>
            </div>
          </div>
        </div>
      </section>
=======
const user = computed(() => userStore.user)

let pollingInterval = null

// Access Control & Polling
onMounted(() => {
  if (user.value && user.value.status !== 'active') {
    router.push('/resources/reviewer/become')
    return
  }

  // Initial fetch
  userStore.refreshJournals()
  
  // Polling (30s)
  pollingInterval = setInterval(() => {
    userStore.refreshJournals()
  }, 30000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})

// --- Logic Reuse (unchanged backend/data logic) ---

// Helper for due date calculation (simulated 14 days)
const getDueDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  d.setDate(d.getDate() + 14)
  return d.toISOString().split('T')[0]
}

const isOverdue = (date) => {
  const dueDateStr = getDueDate(date)
  if (!dueDateStr) return false
  const dueDate = new Date(dueDateStr)
  if (isNaN(dueDate.getTime())) return false
  const today = new Date()
  return today > dueDate
}

// Stats Logic
const pendingReviews = computed(() => {
  // Status '审稿中' (Under Review), not Re-review, not overdue
  return userStore.journals.filter(j => 
    j.status === '审稿中' && 
    j.reviewStage !== '复审' && 
    !isOverdue(j.date)
  )
})

const pendingReReviews = computed(() => {
  // Status '审稿中' and Stage '复审' (Re-review)
  return userStore.journals.filter(j => 
    j.status === '审稿中' && 
    j.reviewStage === '复审' && 
    !isOverdue(j.date)
  )
})

const overdueReviews = computed(() => {
  return userStore.journals.filter(j => 
    j.status === '审稿中' && 
    isOverdue(j.date)
  )
})

// Mock Data for Invitations and Announcements
const latestInvitations = computed(() => {
  return userStore.invitations.filter(i => i.status === 'Invited')
})

// New invitation indicator (mock logic)
const invitationSectionClicked = ref(false)
const hasNewInvitations = computed(() => !invitationSectionClicked.value && latestInvitations.value.some(i => i.isNew))

const clearDot = () => {
  invitationSectionClicked.value = true
}

const announcements = [
  { id: 1, title: 'System Maintenance Scheduled for Oct 25', date: '2023-10-20' },
  { id: 2, title: 'New Reviewer Guidelines Published', date: '2023-10-15' },
  { id: 3, title: 'Reviewer Recognition Program', date: '2023-09-30' }
]

// --- Navigation Actions ---

const viewAllAssignments = (filter) => {
  // Map to existing routes/logic
  // Assuming '/reviewer/assignments' handles query params or filter
  router.push({ path: '/reviewer/assignments', query: { filter } })
}

const viewInvitations = () => {
  router.push({ path: '/reviewer/assignments', query: { filter: 'invitations' } })
}

const viewAnnouncement = (id) => {
  // Mock modal or detail page
  console.log('View announcement', id)
  // router.push(`/announcements/${id}`)
}

</script>

<template>
  <div class="reviewer-dashboard">
    <!-- Top: Global Navigation -->
    <Navigation :user="user" current-page="reviewer-dashboard" />

    <main class="dashboard-container">
      
      <!-- Module 1: Core Statistics Cards -->
      <section class="dashboard-section stats-section">
        <div class="stat-card" @click="viewAllAssignments('pending')">
          <div class="stat-value">{{ pendingReviews.length }}</div>
          <div class="stat-label">Pending Reviews</div>
        </div>
        
        <div class="stat-card" @click="viewAllAssignments('re-reviews')">
          <div class="stat-value">{{ pendingReReviews.length }}</div>
          <div class="stat-label">Pending Re-reviews</div>
        </div>
        
        <div class="stat-card overdue" @click="viewAllAssignments('overdue')">
          <div class="stat-value text-red">{{ overdueReviews.length }}</div>
          <div class="stat-label">Overdue Reviews</div>
        </div>
      </section>

      <!-- Module 2 & 3: Invitations & Announcements -->
      <section class="dashboard-columns">
        
        <!-- Module 2: Latest Invitations -->
        <div class="column-module" @click="clearDot">
          <div class="module-header">
            <h2 class="module-title">
              Latest Invitations ({{ latestInvitations.length }})
              <span v-if="hasNewInvitations" class="notification-dot"></span>
            </h2>
            <a href="#" class="view-all-link" @click.prevent="viewInvitations">View All</a>
          </div>
          <div class="module-content">
            <div v-if="latestInvitations.length === 0" class="empty-state">
              No new invitations.
            </div>
            <div v-else class="invitation-list">
              <div v-for="inv in latestInvitations" :key="inv.id" class="invitation-item">
                <!-- Content would go here -->
                <div class="inv-title">{{ inv.title }}</div>
                <div class="inv-meta">{{ inv.date }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Module 3: System Announcements -->
        <div class="column-module">
          <div class="module-header">
            <h2 class="module-title">System Announcements</h2>
            <!-- No right action button as per spec -->
          </div>
          <div class="module-content">
            <div class="announcement-list">
              <div v-for="ann in announcements" :key="ann.id" class="announcement-item" @click="viewAnnouncement(ann.id)">
                <div class="ann-title">{{ ann.title }}</div>
                <div class="ann-date">{{ ann.date }}</div>
              </div>
            </div>
          </div>
        </div>

      </section>

>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
    </main>
  </div>
</template>

<style scoped>
<<<<<<< HEAD
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
=======
/* Global Layout */
.reviewer-dashboard {
  min-height: 100vh;
  background-color: #f9f9f9; /* Light background similar to main site */
  display: flex;
  flex-direction: column;
}

.dashboard-container {
  max-width: 1200px;
  width: 100%;
  margin: 80px auto 40px; /* Top margin for fixed nav */
  padding: 0 24px;
  box-sizing: border-box;
}

/* Sections */
.dashboard-section {
  margin-bottom: 32px;
}

/* Module 1: Stats Cards */
.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 Columns on PC */
  gap: 24px;
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
}

.stat-card {
  background: white;
<<<<<<< HEAD
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
  color: #3498db;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #2980b9;
  text-decoration: underline;
}

.view-detail-icon {
  font-size: 0.9rem;
  margin-left: 0.5rem;
  color: #7f8c8d;
  transition: transform 0.3s ease;
}

.journal-title:hover .view-detail-icon {
  transform: scale(1.2);
  color: #2980b9;
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
=======
  border: 1px solid #e5e5e5;
  border-radius: 4px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #C93737; /* Brand Red on Hover */
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #333;
}

.text-red {
  color: #C93737; /* Brand Red */
}

/* Module 2 & 3 Layout */
.dashboard-columns {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 2 Columns for modules */
  gap: 24px;
}

/* Column Modules */
.column-module {
  /* Minimal container, maybe no background? Spec says "White background + 24px padding" for content area */
  /* But layout structure says "Three main modules". Let's assume the module itself has the background */
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee; /* Divider line */
}

.module-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-all-link {
  color: #C93737;
  font-size: 14px;
  text-decoration: none;
}

.view-all-link:hover {
  text-decoration: underline;
}

.module-content {
  background: white;
  padding: 24px;
  border-radius: 4px;
  border: 1px solid #e5e5e5; /* Consistent with cards? Spec says "White background + 24px padding" for Invitations */
  min-height: 200px; /* Visual balance */
}

/* Notification Dot */
.notification-dot {
  width: 8px;
  height: 8px;
  background-color: #C93737;
  border-radius: 50%;
  display: inline-block;
}

/* Empty State */
.empty-state {
  color: #666;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
  font-style: italic;
}

/* Lists */
.announcement-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-item:hover .ann-title {
  color: #C93737;
}

.ann-title {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.ann-date {
  font-size: 12px;
  color: #666;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr; /* Stack cards */
  }
  
  .dashboard-columns {
    grid-template-columns: 1fr; /* Stack modules */
  }
  
  .dashboard-container {
    padding: 0 16px;
  }
}
</style>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
