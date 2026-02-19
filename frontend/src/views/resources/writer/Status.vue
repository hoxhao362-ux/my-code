<template>
  <div class="status-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-writer-status'"
      :logout="userStore.logout"
    />
    <div class="query-section">
      <h1>Check Submission Status</h1>
      <div class="query-form">
        <div class="form-group">
          <label>Manuscript ID</label>
          <input 
            type="text" 
            v-model="manuscriptId" 
            placeholder="e.g., MS-2026-001"
            :class="{ active: focusedField === 'id' }"
            @focus="focusedField = 'id'"
            @blur="focusedField = null"
          />
        </div>
        <div class="form-group">
          <label>Corresponding Writer Email</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="writer@example.com"
            :class="{ active: focusedField === 'email' }"
            @focus="focusedField = 'email'"
            @blur="focusedField = null"
          />
        </div>
        <div class="form-checkbox">
          <label>
            <input type="checkbox" v-model="notify" />
            Receive email notifications for status changes
          </label>
        </div>
        <button class="btn-query" @click="checkStatus" :disabled="loading">
          {{ loading ? 'Checking...' : 'Check Status' }}
        </button>
      </div>
    </div>

    <div v-if="result" class="result-section">
      <div class="timeline">
        <div v-for="(item, index) in result.history" :key="index" class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div class="timeline-date">{{ item.date }}</div>
            <div class="timeline-status">{{ item.status }}</div>
            <div class="timeline-desc" v-if="item.description">{{ item.description }}</div>
          </div>
        </div>
      </div>

      <div class="current-status-box" v-if="result.currentStatus === 'Revision Required'">
        <h3>Action Required: Revision</h3>
        <p>The reviewers have recommended revisions for your manuscript. Please address their comments and upload your revised manuscript.</p>
        <button class="btn-upload" @click="uploadRevision">Upload Revision</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const router = useRouter()
const manuscriptId = ref('')
const email = ref('')
const notify = ref(false)
const focusedField = ref(null)
const loading = ref(false)
const result = ref(null)

const checkStatus = () => {
  if (!manuscriptId.value || !email.value) return
  
  loading.value = true
  // Mock API call
  setTimeout(() => {
    loading.value = false
    // Mock result based on input or random
    result.value = {
      currentStatus: 'Revision Required', // Hardcoded for demo
      history: [
        { date: '2026-02-09', status: 'Revision Required', description: 'Minor revisions requested by Reviewer 2.' },
        { date: '2026-01-20', status: 'Under Review', description: 'Manuscript sent to reviewers.' },
        { date: '2026-01-15', status: 'Initial Review', description: 'Passed format check.' },
        { date: '2026-01-10', status: 'Submitted', description: 'Manuscript received.' }
      ]
    }
  }, 1000)
}

const uploadRevision = () => {
  // Jump to existing submission system
  router.push('/submission/login')
}
</script>

<style scoped>
.status-container {
  max-width: 800px;
  margin: 80px auto 0;
  padding: 40px 24px 40px;
}

.query-section {
  text-align: center;
  margin-bottom: 60px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 32px;
}

.query-form {
  width: 60%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  text-align: left;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

input[type="text"],
input[type="email"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

input.active {
  border-color: #C93737;
  outline: none;
}

.form-checkbox {
  text-align: left;
  font-size: 12px;
  color: #999;
}

.btn-query {
  width: 100%;
  padding: 12px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-query:hover {
  background-color: #A02C2C;
}

.btn-query:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.result-section {
  border-top: 1px solid #E5E5E5;
  padding-top: 40px;
}

.timeline {
  position: relative;
  padding-left: 20px;
  border-left: 2px solid #C93737;
  margin-left: 20px;
}

.timeline-item {
  position: relative;
  margin-bottom: 32px;
  padding-left: 24px;
}

.timeline-marker {
  position: absolute;
  left: -27px; /* Adjust based on line width and padding */
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #C93737;
  border: 2px solid white;
}

.timeline-content:hover {
  background-color: #F9F9F9;
  border-radius: 4px;
}

.timeline-date {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.timeline-status {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.timeline-desc {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.current-status-box {
  background-color: #FFF0F0;
  border: 1px solid #FFD0D0;
  padding: 24px;
  border-radius: 4px;
  margin-top: 40px;
  text-align: center;
}

.current-status-box h3 {
  color: #C93737;
  margin-top: 0;
}

.btn-upload {
  margin-top: 16px;
  padding: 10px 24px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}

.btn-upload:hover {
  background-color: #A02C2C;
}
</style>
