<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

const reviewers = computed(() => {
  return userStore.users.filter(u => u.role === 'reviewer').map(r => ({
    ...r,
    // Mock performance data
    completedReviews: Math.floor(Math.random() * 20),
    avgTurnaround: Math.floor(Math.random() * 10) + 5 + ' days',
    qualityScore: (Math.random() * 2 + 3).toFixed(1)
  }))
})

const handleInvite = () => {
  alert('Invitation sent to new reviewer (Mock).')
}

const handleRemove = (reviewer) => {
  if (confirm(`Remove reviewer ${reviewer.username}?`)) {
    userStore.deleteUser(reviewer.id) // This actually deletes the user, might be too harsh for a mock, but fits "maintain list"
  }
}

const viewProfile = (reviewer) => {
  alert(`Viewing profile for ${reviewer.username}`)
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-reviewer-management" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Reviewer Management</h1>
        <div class="header-actions">
           <button class="btn btn-primary" @click="handleInvite">Invite New Reviewer</button>
        </div>
      </div>

      <div class="reviewers-table-container">
        <table class="reviewers-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Completed Reviews</th>
              <th>Avg Turnaround</th>
              <th>Quality Score</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="reviewer in reviewers" :key="reviewer.id">
              <td>{{ reviewer.username }}</td>
              <td>{{ reviewer.email }}</td>
              <td>{{ reviewer.completedReviews }}</td>
              <td>{{ reviewer.avgTurnaround }}</td>
              <td>
                <span class="score" :class="reviewer.qualityScore >= 4.0 ? 'high' : 'medium'">
                  {{ reviewer.qualityScore }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-text" @click="viewProfile(reviewer)">Profile</button>
                <button class="btn-text delete" @click="handleRemove(reviewer)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="reviewers.length === 0" class="no-data">
          No reviewers found.
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

.reviewers-table-container { background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); overflow: hidden; }
.reviewers-table { width: 100%; border-collapse: collapse; }
.reviewers-table th, .reviewers-table td { padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }
.reviewers-table th { background: #f8f9fa; font-weight: 600; color: #555; }
.reviewers-table tr:last-child td { border-bottom: none; }

.score { font-weight: bold; padding: 2px 6px; border-radius: 4px; }
.score.high { background: #e8f5e9; color: #2e7d32; }
.score.medium { background: #fff3e0; color: #ef6c00; }

.actions-cell { display: flex; gap: 0.5rem; }
.btn-text { background: none; border: none; cursor: pointer; color: #3498db; font-weight: 500; }
.btn-text.delete { color: #e74c3c; }
.btn-text:hover { text-decoration: underline; }

.btn-primary { background: #3498db; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; }
.btn-primary:hover { background: #2980b9; }

.no-data { padding: 2rem; text-align: center; color: #999; }
</style>
