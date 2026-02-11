<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import SubmissionNavigation from '../submission/components/SubmissionNavigation.vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser)

// Author submission data
const userJournals = computed(() => userStore.userJournals)

// Menu Groups Configuration
const menuGroups = computed(() => {
  // Helper to count journals by status or logic
  const count = (filterFn) => userJournals.value.filter(filterFn).length
  
  return [
    {
      title: 'New Submissions',
      items: [
        { label: 'Submit New Manuscript', count: null, action: 'submit' }, // Special action
        { label: 'Submissions Sent Back to Author', count: count(j => j.status === 'Sent Back'), key: 'sent_back' },
        { label: 'Incomplete Submissions', count: count(j => j.status === 'Incomplete'), key: 'incomplete' },
        { label: 'Submissions Waiting for Author\'s Approval', count: count(j => j.status === 'Waiting Approval'), key: 'waiting_approval' },
        { label: 'Submissions Being Processed', count: count(j => j.status === 'Being Processed' || j.status === '审稿中'), key: 'processing' }
      ]
    },
    {
      title: 'Revisions',
      items: [
        { label: 'Submissions Needing Revision', count: count(j => j.status === 'Needing Revision'), key: 'needing_revision' },
        { label: 'Revisions Sent Back to Author', count: count(j => j.status === 'Revision Sent Back'), key: 'revision_sent_back' },
        { label: 'Incomplete Submissions Being Revised', count: count(j => j.status === 'Incomplete Revision'), key: 'incomplete_revision' },
        { label: 'Revisions Waiting for Author\'s Approval', count: count(j => j.status === 'Revision Waiting Approval'), key: 'revision_waiting_approval' },
        { label: 'Revisions Being Processed', count: count(j => j.status === 'Revision Processing'), key: 'revision_processing' },
        { label: 'Declined Revisions', count: count(j => j.status === 'Revision Declined'), key: 'revision_declined' }
      ]
    },
    {
      title: 'Completed',
      items: [
        { label: 'Submissions with a Decision', count: count(j => j.status === 'Decision Made' || j.status === '已通过' || j.status === '未通过'), key: 'decision_made' },
        { label: 'Submissions with Production Completed', count: count(j => j.status === 'Production Completed'), key: 'production_completed' }
      ]
    }
  ]
})

// Active selection state
const activeGroupTitle = ref('New Submissions') // Default active group (though UI shows all groups, selection is detail view)
const selectedItemKey = ref(null)

// Handle item click
const handleItemClick = (item) => {
  if (item.action === 'submit') {
    router.push('/submission/author/submit')
    return
  }
  
  if (item.count > 0) {
    selectedItemKey.value = item.key
    // Smooth scroll to details or update details view
  }
}

// Get filtered manuscripts for selected item
const selectedManuscripts = computed(() => {
  if (!selectedItemKey.value) return []
  
  // Mapping keys to filter logic (simplified for demo)
  // In real app, this would be more complex or backend query
  switch (selectedItemKey.value) {
    case 'sent_back': return userJournals.value.filter(j => j.status === 'Sent Back')
    case 'incomplete': return userJournals.value.filter(j => j.status === 'Incomplete')
    case 'waiting_approval': return userJournals.value.filter(j => j.status === 'Waiting Approval')
    case 'processing': return userJournals.value.filter(j => j.status === 'Being Processed' || j.status === '审稿中')
    case 'decision_made': return userJournals.value.filter(j => j.status === 'Decision Made' || j.status === '已通过' || j.status === '未通过')
    // Add other cases...
    default: return []
  }
})

// Selected Item Label for header
const selectedItemLabel = computed(() => {
  for (const group of menuGroups.value) {
    const item = group.items.find(i => i.key === selectedItemKey.value)
    if (item) return item.label
  }
  return ''
})

</script>

<template>
  <div class="author-dashboard-container">
    <!-- 替换为投稿专用导航 -->
    <SubmissionNavigation />

    <!-- 作者后台内容 -->
    <main class="dashboard-content">
      <!-- 主内容区域 -->
      <div class="main-lists">
          <div v-for="group in menuGroups" :key="group.title" class="menu-group">
            <h3 class="group-title">{{ group.title }}</h3>
            <ul class="group-list">
              <li v-for="(item, index) in group.items" :key="index" class="list-item">
                <!-- Submit New Manuscript Link -->
                <a 
                  v-if="item.action === 'submit'" 
                  href="#" 
                  class="action-link"
                  @click.prevent="handleItemClick(item)"
                >
                  {{ item.label }}
                </a>
                
                <!-- Status Links -->
                <a 
                  v-else 
                  href="#" 
                  class="status-link"
                  :class="{ 
                    'active': selectedItemKey === item.key, 
                    'disabled': item.count === 0,
                    'clickable': item.count > 0
                  }"
                  @click.prevent="handleItemClick(item)"
                >
                  {{ item.label }} 
                  <span class="count">({{ item.count }})</span>
                </a>
              </li>
            </ul>
          </div>

          <!-- 稿件详情列表区域 (当选中某一项时显示) -->
          <transition name="fade">
            <div v-if="selectedItemKey && selectedManuscripts.length > 0" class="manuscript-details-section">
              <h3 class="details-title">{{ selectedItemLabel }} - Details</h3>
              
              <!-- 列表模板 -->
              <div class="manuscript-list">
                 <!-- 简单列表展示，可根据分类差异化模板 -->
                <div v-for="manuscript in selectedManuscripts" :key="manuscript.id" class="manuscript-card">
                   <div class="card-header">
                     <span class="ms-id">#{{ manuscript.id }}</span>
                     <span class="ms-status">{{ manuscript.status }}</span>
                   </div>
                   <h4 class="ms-title">{{ manuscript.title }}</h4>
                   <div class="ms-meta">
                     <span>Submitted: {{ manuscript.date }}</span>
                     <span>Module: {{ manuscript.module }}</span>
                   </div>
                   <div class="card-actions">
                     <button class="action-btn">View Submission</button>
                     <button class="action-btn">History</button>
                   </div>
                </div>
              </div>
            </div>
          </transition>
      </div>
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
.author-dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fff; /* White background as per screenshot */
  font-family: Arial, sans-serif;
}

.dashboard-content {
  flex: 1;
  width: 100%;
  max-width: 1400px; /* Wider layout */
  margin: 0 auto;
  padding: 2rem 1rem;
}

.main-lists {
  width: 100%;
}

.menu-group {
  margin-bottom: 2.5rem;
}

.group-title {
  font-size: 1.2rem;
  font-weight: normal;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.group-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  margin-bottom: 0.5rem;
}

.action-link {
  color: #0056b3;
  font-weight: normal;
  text-decoration: none;
  font-size: 0.95rem;
}

.action-link:hover {
  text-decoration: underline;
}

.status-link {
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.2s;
  display: inline-block;
}

.status-link.disabled {
  color: #777;
  cursor: default;
  pointer-events: none; /* Make unclickable */
}

.status-link.clickable {
  color: #0056b3;
  cursor: pointer;
}

.status-link.clickable:hover {
  text-decoration: underline;
}

.status-link.active {
  background-color: #e8f0fe;
  padding: 2px 5px;
  border-radius: 3px;
  font-weight: bold;
}

/* Manuscript Details Section */
.manuscript-details-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #0056b3;
}

.details-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.manuscript-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manuscript-card {
  background: #f9f9f9;
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.ms-title {
  margin: 0 0 0.5rem 0;
  color: #0056b3;
  font-size: 1.1rem;
}

.ms-meta {
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
  background: #eee;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
}

.action-btn:hover {
  background: #ddd;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.footer {
  background: #f8f9fa;
  color: #666;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #eee;
  margin-top: auto;
}
</style>