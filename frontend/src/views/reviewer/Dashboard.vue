<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
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
