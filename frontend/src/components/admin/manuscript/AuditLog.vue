<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  logs: {
    type: Array,
    default: () => [
      // Mock data
      { id: 1, time: '2026-02-13 15:30:22', role: 'Editor (John Doe)', node: 'Initial Review', action: 'Submitted initial review decision: Passed', result: 'Status: Initial Review Passed' },
      { id: 2, time: '2026-02-12 10:15:00', role: 'Author', node: 'Submission', action: 'Submitted manuscript', result: 'Status: Pending Initial Review' }
    ]
  }
})

// Filters
const filterForm = reactive({
  role: '',
  type: '',
  dateStart: '',
  dateEnd: ''
})

const roles = ['Editor', 'Editor-in-Chief', 'Reviewer', 'Author']
const types = ['Status Change', 'Comment', 'Revision', 'Notification', 'Decision']

// Filter Logic (Mock)
const filteredLogs = computed(() => {
  return props.logs.filter(log => {
    if (filterForm.role && !log.role.includes(filterForm.role)) return false
    // Add other filters as needed
    return true
  })
})

// Export
const exportLogs = () => {
  alert('Logs exported to PDF (Mock)')
}

// Detail Modal
const selectedLog = ref(null)
const showDetail = (log) => {
  selectedLog.value = log
}

</script>

<template>
  <div class="audit-log-container">
    <!-- Header -->
    <header class="header">
      <h2 class="title">Full Process Audit Log (Tamper-Proof)</h2>
      <p class="subtitle">Logs are automatically generated, permanently stored, and cannot be deleted or modified (Lancet Compliance).</p>
      
      <div class="filter-bar">
        <div class="filter-group">
          <select v-model="filterForm.role" class="filter-select">
            <option value="">All Roles</option>
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
          <select v-model="filterForm.type" class="filter-select">
            <option value="">All Actions</option>
            <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
          </select>
          <input type="date" v-model="filterForm.dateStart" class="filter-date">
          <span class="sep">-</span>
          <input type="date" v-model="filterForm.dateEnd" class="filter-date">
        </div>
        <div class="action-group">
          <button class="btn-gray">Search</button>
          <button class="btn-red" @click="exportLogs">Export Logs</button>
        </div>
      </div>
    </header>

    <!-- Log List -->
    <div class="log-list-wrapper">
      <div class="log-count">Total Records: {{ filteredLogs.length }}</div>
      <table class="log-table">
        <thead>
          <tr>
            <th width="180">Time</th>
            <th width="150">Role</th>
            <th width="120">Node</th>
            <th>Action</th>
            <th width="200">Result</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in filteredLogs" :key="log.id" class="log-row" @click="showDetail(log)">
            <td class="time-col">{{ log.time }}</td>
            <td>{{ log.role }}</td>
            <td>{{ log.node }}</td>
            <td class="action-col">{{ log.action }}</td>
            <td class="result-col">{{ log.result }}</td>
          </tr>
          <tr v-if="filteredLogs.length === 0">
            <td colspan="5" class="empty-row">No records found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedLog" class="modal-overlay" @click.self="selectedLog = null">
      <div class="modal-content">
        <h3 class="modal-title">Log Detail</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <label>Time:</label>
            <span>{{ selectedLog.time }}</span>
          </div>
          <div class="detail-item">
            <label>Role:</label>
            <span>{{ selectedLog.role }}</span>
          </div>
          <div class="detail-item">
            <label>Process Node:</label>
            <span>{{ selectedLog.node }}</span>
          </div>
          <div class="detail-item full">
            <label>Action Content:</label>
            <p>{{ selectedLog.action }}</p>
          </div>
          <div class="detail-item full">
            <label>Result:</label>
            <p>{{ selectedLog.result }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-gray" @click="selectedLog = null">Close</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.audit-log-container {
  font-family: 'Times New Roman', Times, serif;
  background: white;
  padding: 20px;
  height: 100%;
  color: #333;
  display: flex;
  flex-direction: column;
}

.header { text-align: center; margin-bottom: 20px; }
.title { font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333; }
.subtitle { font-size: 12px; color: #999; margin-bottom: 15px; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: #f9f9f9; padding: 10px; border-radius: 4px; }
.filter-group { display: flex; gap: 10px; align-items: center; }
.filter-select, .filter-date { padding: 5px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 13px; }
.sep { color: #999; }
.action-group { display: flex; gap: 10px; }

.btn-gray { padding: 5px 15px; border: 1px solid #ddd; background: #eee; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-red { padding: 5px 15px; border: none; background: #C93737; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; }

.log-list-wrapper { flex: 1; overflow-y: auto; }
.log-count { font-size: 12px; color: #666; margin-bottom: 5px; text-align: right; }

.log-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.log-table th { background: #f5f5f5; text-align: left; padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; color: #333; }
.log-table td { padding: 10px; border-bottom: 1px solid #eee; color: #333; }
.log-row:hover { background-color: #f9f9f9; cursor: pointer; }
.time-col { font-family: monospace; color: #666; }
.action-col { color: #333; }
.result-col { color: #666; font-style: italic; }
.empty-row { text-align: center; padding: 20px; color: #999; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 3000; }
.modal-content { background: white; padding: 20px; border-radius: 4px; width: 500px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.modal-title { font-size: 16px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }

.detail-grid { display: grid; grid-template-columns: 1fr; gap: 15px; }
.detail-item label { display: block; font-weight: bold; font-size: 13px; color: #666; margin-bottom: 3px; }
.detail-item span, .detail-item p { font-size: 14px; color: #333; margin: 0; }
.detail-item.full { grid-column: 1 / -1; }

.modal-footer { margin-top: 20px; text-align: right; }

</style>
