<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useReviewStore } from '../../stores/review'
import Navigation from '../../components/Navigation.vue'
import { useI18n } from '../../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const reviewStore = useReviewStore()
const router = useRouter()
const user = computed(() => userStore.user)

let pollingInterval = null

// Status Filter
const statusFilter = ref('pending')

const filteredTasks = computed(() => {
  if (statusFilter.value === 'all') return reviewStore.reviewTasks.value
  return reviewStore.reviewTasks.value.filter(t => t.status === statusFilter.value)
})

// Status Helpers
const getStatusLabel = (status) => {
  const map = {
    'pending': 'reviewerDashboard.status.pending',
    'completed': 'reviewerDashboard.status.completed',
    'overdue': 'reviewerDashboard.status.overdue'
  }
  return t(map[status] || status)
}

const getStatusClass = (status) => {
  const map = {
    'pending': 'status-pending',
    'completed': 'status-completed',
    'overdue': 'status-overdue'
  }
  return map[status] || ''
}

const isOverdue = (dueDate) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  if (isNaN(due.getTime())) return false
  return new Date() > due
}

// Access Control & Polling
onMounted(async () => {
  if (user.value && user.value.status !== 'active') {
    router.push('/resources/reviewer/become')
    return
  }

  // Initial fetch
  await reviewStore.fetchMyTasks({ status: statusFilter.value })
  
  // Polling (60s)
  pollingInterval = setInterval(() => {
    reviewStore.fetchMyTasks({ status: statusFilter.value })
  }, 60000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})

// Navigation
const navigateToReview = (taskId) => {
  router.push({ name: 'ReviewerReviewForm', params: { taskId } })
}

const viewAllAssignments = (filter) => {
  statusFilter.value = filter
  reviewStore.fetchMyTasks({ status: filter === 'all' ? undefined : filter })
}

const isAssigned = (task) => {
  return !task.assigned_to || 
         task.assigned_to === user.value?.username || 
         String(task.assigned_to) === String(user.value?.id)
}

// Stats
const pendingReviews = computed(() => {
  return reviewStore.reviewTasks.value.filter(t => 
    t.status === 'pending' && isAssigned(t)
  )
})

const completedReviews = computed(() => {
  return reviewStore.reviewTasks.value.filter(t => 
    t.status === 'completed' && isAssigned(t)
  )
})

const overdueReviews = computed(() => {
  return reviewStore.reviewTasks.value.filter(t => 
    t.status === 'overdue' && isAssigned(t)
  )
})

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
          <div class="stat-label">{{ t('reviewerDashboard.stats.pendingReviews') }}</div>
        </div>
        
        <div class="stat-card" @click="viewAllAssignments('completed')">
          <div class="stat-value">{{ completedReviews.length }}</div>
          <div class="stat-label">{{ t('reviewerDashboard.stats.completedReviews') }}</div>
        </div>
        
        <div class="stat-card overdue" @click="viewAllAssignments('overdue')">
          <div class="stat-value text-red">{{ overdueReviews.length }}</div>
          <div class="stat-label">{{ t('reviewerDashboard.stats.overdueReviews') }}</div>
        </div>
      </section>

      <!-- Module 2: Review Task List -->
      <section class="dashboard-section task-list-section">
        <div class="section-header">
          <h2 class="section-title">{{ t('reviewerDashboard.tasks.title') }}</h2>
          <div class="filter-tabs">
            <button 
              v-for="filter in ['pending', 'completed', 'overdue']" 
              :key="filter"
              class="filter-tab"
              :class="{ active: statusFilter === filter }"
              @click="viewAllAssignments(filter)"
            >
              {{ getStatusLabel(filter) }}
            </button>
          </div>
        </div>

        <div v-if="reviewStore.isLoading" class="loading-state">
          {{ t('common.loading') }}
        </div>

        <div v-else-if="filteredTasks.length === 0" class="empty-state">
          {{ t('reviewerDashboard.tasks.empty') }}
        </div>

        <div v-else class="task-list">
          <div 
            v-for="task in filteredTasks" 
            :key="task.id"
            class="task-card"
            @click="navigateToReview(task.id)"
          >
            <div class="task-header">
              <span class="task-id">#{{ task.manuscript_id }}</span>
              <span class="task-status" :class="getStatusClass(task.status)">
                {{ getStatusLabel(task.status) }}
              </span>
            </div>
            <h3 class="task-title">{{ task.title }}</h3>
            <div class="task-meta">
              <span class="task-authors">{{ task.authors }}</span>
              <span class="task-due">
                {{ t('reviewerDashboard.tasks.dueDate') }}: {{ task.due_date }}
                <span v-if="isOverdue(task.due_date)" class="overdue-badge">
                  {{ t('reviewerDashboard.tasks.overdue') }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
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
}

.stat-card {
  background: white;
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
