<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

const activeTab = ref('pending') // 'pending', 'history'

const myTasks = computed(() => {
  if (!user.value) return []
  return userStore.journals.filter(j => 
    // 1. Tasks assigned specifically to me
    (j.status === 'assigned_to_editor' && j.assignedEditor === user.value.username) ||
    // 2. Tasks in my workflow stages (Legacy/Simple logic)
    ((j.author === user.value.username || j.writer === user.value.username) && ['Submitted', 'Revision Submitted'].includes(j.status)) ||
    // 3. Reviewer tasks (if I am a reviewer)
    (user.value.role === 'reviewer' && j.status === 'under_peer_review' && j.reviewers?.some(r => r.name === user.value.username)) ||
    // 4. Legacy fallback
    ['Pending Screening', 'Pending Assignment', 'Under Review'].includes(j.status)
  )
})

const historyTasks = computed(() => {
  // Mock logic: Completed journals
  return userStore.journals.filter(j => 
    ['Accepted', 'Rejected', 'Published'].includes(j.status)
  )
})

const handleExport = () => {
  toastStore.add({ message: 'Exporting data to CSV...', type: 'info' })
}

const openDiscussion = (journal) => {
  toastStore.add({ message: 'Opening internal discussion board for: ' + journal.title, type: 'info' })
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-my-tasks" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>My Tasks & History</h1>
        <div class="actions">
          <button class="btn btn-secondary" @click="handleExport">Export Data</button>
        </div>
      </div>

      <div class="tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">Pending Tasks ({{ myTasks.length }})</button>
        <button class="tab-btn" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">History ({{ historyTasks.length }})</button>
      </div>

      <div class="tasks-list">
        <div v-for="journal in (activeTab === 'pending' ? myTasks : historyTasks)" :key="journal.id" class="task-item">
           <div class="task-main">
             <h3 class="task-title">{{ journal.title }}</h3>
             <div class="task-meta">
               <span class="status-badge" :class="journal.status.toLowerCase().replace(' ', '-')">{{ journal.status }}</span>
               <span>ID: #{{ journal.id }}</span>
               <span>Date: {{ journal.date }}</span>
             </div>
           </div>
           <div class="task-actions">
             <button class="btn-sm" @click="openDiscussion(journal)">Internal Discussion</button>
             <button class="btn-sm">View Log</button>
           </div>
        </div>
        
        <div v-if="(activeTab === 'pending' ? myTasks : historyTasks).length === 0" class="no-data">
          No records found in this section.
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.audit-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.content { flex: 1; max-width: 1200px; margin: 80px auto 0; padding: 2rem; width: 100%; }
.header { margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 1.8rem; color: #2c3e50; margin: 0; }

.tabs { display: flex; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid #ddd; }
.tab-btn { padding: 0.8rem 1.5rem; background: none; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-size: 1rem; color: #666; font-weight: 500; }
.tab-btn.active { color: #3498db; border-bottom-color: #3498db; }

.task-item { background: white; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.task-title { margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #333; }
.task-meta { display: flex; gap: 1rem; font-size: 0.85rem; color: #777; align-items: center; }
.status-badge { padding: 2px 6px; border-radius: 4px; background: #eee; font-weight: 500; }

.task-actions { display: flex; gap: 0.5rem; }
.btn-sm { padding: 0.4rem 0.8rem; font-size: 0.85rem; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.btn-sm:hover { background: #f0f0f0; }
.btn-secondary { background: #95a5a6; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; }

.no-data { text-align: center; padding: 3rem; color: #999; }
</style>
