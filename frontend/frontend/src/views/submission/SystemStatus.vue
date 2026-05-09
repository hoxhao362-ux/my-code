<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const user = ref(userStore.user)

// Mock Data for System Status
const systemStatus = ref({
  status: 'normal', // normal, partial, maintenance
  message: 'System is running normally',
  maintenance: {
    time: '2026-02-15 00:00 - 04:00 (UTC)',
    scope: 'Submission System, PDF Generation',
    expectedRecovery: '2026-02-15 04:00 (UTC)'
  }
})

const maintenanceHistory = ref([
  { id: 1, reason: 'Routine Maintenance', recoveryTime: '2026-01-10 03:00 (UTC)' },
  { id: 2, reason: 'Database Upgrade', recoveryTime: '2025-12-20 02:30 (UTC)' },
  { id: 3, reason: 'Security Patch', recoveryTime: '2025-11-05 01:00 (UTC)' }
])

const isSubscribed = ref(false)

const subscribeToReminders = () => {
  // Call backend API to subscribe (mocked)
  // userStore.subscribeToMaintenance(user.value.id, isSubscribed.value)
  console.log(`User ${user.value?.username} subscription status: ${isSubscribed.value}`)
}

const getStatusColor = (status) => {
  switch (status) {
    case 'normal': return 'green'
    case 'partial': return 'orange'
    case 'maintenance': return 'red'
    default: return 'gray'
  }
}

const getStatusText = (status) => {
   switch (status) {
    case 'normal': return 'System is running normally'
    case 'partial': return 'Partial functions limited (e.g., PDF export temporarily unavailable)'
    case 'maintenance': return 'System under maintenance, expected to recover in X hours'
    default: return 'Unknown Status'
  }
}

onMounted(() => {
  // Fetch real status from API if available
  // For now using mock data
})
</script>

<template>
  <div class="system-status-page">
    <div class="container">
      <h1>System Status</h1>
      
      <!-- Status Indicator -->
      <div class="status-card" :class="systemStatus.status">
        <div class="status-icon">
          <span class="dot" :style="{ backgroundColor: getStatusColor(systemStatus.status) }"></span>
        </div>
        <div class="status-info">
          <h2>{{ getStatusText(systemStatus.status) }}</h2>
          <p v-if="systemStatus.status !== 'normal'">{{ systemStatus.maintenance.time }}</p>
        </div>
      </div>

      <!-- Maintenance Announcement -->
      <div class="section">
        <h3>Maintenance Announcement</h3>
        <div class="announcement-card">
          <div class="info-row">
            <span class="label">Maintenance Time:</span>
            <span class="value">{{ systemStatus.maintenance.time }}</span>
          </div>
          <div class="info-row">
            <span class="label">Affected Scope:</span>
            <span class="value">{{ systemStatus.maintenance.scope }}</span>
          </div>
          <div class="info-row">
            <span class="label">Expected Recovery:</span>
            <span class="value">{{ systemStatus.maintenance.expectedRecovery }}</span>
          </div>
          
          <div class="subscribe-section">
            <label class="checkbox-label">
              <input type="checkbox" v-model="isSubscribed" @change="subscribeToReminders">
              Subscribe to Reminder (Notify 1 hour before maintenance)
            </label>
          </div>
        </div>
      </div>

      <!-- Maintenance History -->
      <div class="section">
        <h3>Maintenance History (Last 3 Months)</h3>
        <table class="history-table">
          <thead>
            <tr>
              <th>Maintenance Reason</th>
              <th>Actual Recovery Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in maintenanceHistory" :key="item.id">
              <td>{{ item.reason }}</td>
              <td>{{ item.recoveryTime }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-status-page {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

h3 {
  margin-bottom: 1rem;
  color: #34495e;
  border-bottom: 2px solid #e1e4e8;
  padding-bottom: 0.5rem;
}

.section {
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.status-card {
  display: flex;
  align-items: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
  border-left: 5px solid;
}

.status-card.normal { border-left-color: #2ecc71; }
.status-card.partial { border-left-color: #f39c12; }
.status-card.maintenance { border-left-color: #e74c3c; }

.status-icon {
  margin-right: 1.5rem;
}

.dot {
  display: block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
}

.status-info h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.announcement-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
}

.label {
  font-weight: 600;
  width: 150px;
  color: #7f8c8d;
}

.value {
  color: #2c3e50;
}

.subscribe-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th, .history-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.history-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #34495e;
}
</style>
