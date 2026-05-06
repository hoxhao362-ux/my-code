<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
<<<<<<< HEAD
import Navigation from '../../../components/Navigation.vue'
import { exportLogsToExcel, checkExportPermission } from '../../../utils/export'

=======
import { useI18n } from 'vue-i18n'
import Navigation from '../../../components/Navigation.vue'
import { exportLogsToExcel, checkExportPermission } from '../../../utils/export'

const { t } = useI18n()

>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

const userStore = useUserStore()
const toastStore = useToastStore()
const user = ref(userStore.user)

// Log Types
<<<<<<< HEAD
const logTypes = [
  { value: 'all', label: 'All Logs' },
  { value: 'operation', label: 'Operation Logs' },
  { value: 'login', label: 'Login Logs' },
  { value: 'error', label: 'Error Logs' }
]

// Log Data - Computed from Store
const logsData = computed(() => userStore.systemLogs)

=======
const logTypes = computed(() => [
  { value: 'all', label: t('logs.types.all') },
  { value: 'operation', label: t('logs.types.operation') },
  { value: 'login', label: t('logs.types.login') },
  { value: 'error', label: t('logs.types.error') }
])

// Log Data - Computed from Store
const logsData = computed(() => userStore.systemLogs)

>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
// Log Filters
const logFilters = ref({
  type: 'all',
  keyword: '',
  startDate: '',
  endDate: ''
})

// Pagination Settings
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: computed(() => filteredLogs.value.length)
})

// Filter Logs
const filteredLogs = computed(() => {
  return logsData.value.filter(log => {
    // Type Filter
    const matchesType = logFilters.value.type === 'all' || log.type === logFilters.value.type
    
    // Keyword Filter
    const matchesKeyword = !logFilters.value.keyword || 
      (log.user && log.user.toLowerCase().includes(logFilters.value.keyword.toLowerCase())) ||
      (log.action && log.action.toLowerCase().includes(logFilters.value.keyword.toLowerCase())) ||
      (log.target && log.target.toLowerCase().includes(logFilters.value.keyword.toLowerCase())) ||
      (log.ip && log.ip.includes(logFilters.value.keyword))
    
    // Date Filter
    const logDate = new Date(log.time)
    const startDate = logFilters.value.startDate ? new Date(logFilters.value.startDate) : null
    const endDate = logFilters.value.endDate ? new Date(logFilters.value.endDate) : null
    
    let matchesDate = true
    if (startDate && endDate) {
      // Add one day to end date to include the full day
      const endDateAdjusted = new Date(endDate)
      endDateAdjusted.setDate(endDateAdjusted.getDate() + 1)
      matchesDate = logDate >= startDate && logDate < endDateAdjusted
    } else if (startDate) {
      matchesDate = logDate >= startDate
    } else if (endDate) {
      const endDateAdjusted = new Date(endDate)
      endDateAdjusted.setDate(endDateAdjusted.getDate() + 1)
      matchesDate = logDate < endDateAdjusted
    }
    
    return matchesType && matchesKeyword && matchesDate
  })
})

// Paginated Logs
const paginatedLogs = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredLogs.value.slice(start, end)
})

// Export Logs
const exportLogs = () => {
  exportLogsToExcel(filteredLogs.value)
}

// Confirm Modal
const showConfirmModal = ref(false)

const openConfirmModal = () => {
  showConfirmModal.value = true
}

const confirmClearLogs = () => {
  userStore.systemLogs = []
  localStorage.removeItem('systemLogs')
  
  showConfirmModal.value = false
  toastStore.add({ message: 'Logs cleared successfully!', type: 'success' })
}

const cancelClearLogs = () => {
  showConfirmModal.value = false
}

const changeLogType = (type) => {
  logFilters.value.type = type
  pagination.value.currentPage = 1
}

const resetFilters = () => {
  logFilters.value = {
    type: 'all',
    keyword: '',
    startDate: '',
    endDate: ''
  }
  pagination.value.currentPage = 1
}

const getLogTypeName = (type) => {
  const typeMap = {
<<<<<<< HEAD
    'operation': 'Operation',
    'login': 'Login',
    'error': 'Error'
=======
    'operation': t('logs.types.operation'),
    'login': t('logs.types.login'),
    'error': t('logs.types.error')
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  }
  return typeMap[type] || type
}

const getStatusClass = (status) => {
  const statusMap = {
    'success': 'success',
    'failed': 'failed',
    'error': 'error'
  }
  return statusMap[status] || ''
}
</script>

<template>
  <div class="admin-logs-management-container">
    <Navigation 
      v-if="!embedded"
      :user="user"
      :current-page="'admin-system-logs'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <main class="content">
      <div class="header">
<<<<<<< HEAD
        <h1>System Settings - Logs Management</h1>
        <p class="subtitle">Manage platform operation logs, login logs, and error logs.</p>
=======
        <h1>{{ $t('logs.title') }}</h1>
        <p class="subtitle">{{ $t('logs.subtitle') }}</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>

      <section class="logs-section">
        <!-- Log Type Tabs -->
        <div class="log-type-tabs">
          <button 
            v-for="type in logTypes" 
            :key="type.value"
            class="tab-btn"
            :class="{ active: logFilters.type === type.value }"
            @click="changeLogType(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
        
        <!-- Filters & Actions -->
        <div class="logs-header">
          <div class="filter-controls">
            <div class="search-box">
              <input 
                type="text" 
                v-model="logFilters.keyword" 
<<<<<<< HEAD
                placeholder="Search logs..."
=======
                :placeholder="$t('logs.filters.searchPlaceholder')"
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
                class="search-input"
              >
            </div>
            
            <div class="date-filters">
              <input 
                type="date" 
                v-model="logFilters.startDate" 
                class="date-input"
<<<<<<< HEAD
                placeholder="Start Date"
              >
              <span class="date-separator">to</span>
=======
                :placeholder="$t('logs.filters.startDate')"
              >
              <span class="date-separator">{{ $t('logs.filters.to') }}</span>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
              <input 
                type="date" 
                v-model="logFilters.endDate" 
                class="date-input"
<<<<<<< HEAD
                placeholder="End Date"
              >
            </div>
            
            <button class="btn btn-reset" @click="resetFilters">Reset</button>
=======
                :placeholder="$t('logs.filters.endDate')"
              >
            </div>
            
            <button class="btn btn-reset" @click="resetFilters">{{ $t('logs.filters.reset') }}</button>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
          </div>
          
          <div class="log-actions">
            <button 
              v-if="checkExportPermission(user.role, 'logs')" 
              class="btn btn-export" 
              @click="exportLogs"
            >
<<<<<<< HEAD
              Export
            </button>
            <button class="btn btn-danger" @click="openConfirmModal">Clear Logs</button>
=======
              {{ $t('logs.actions.export') }}
            </button>
            <button class="btn btn-danger" @click="openConfirmModal">{{ $t('logs.actions.clear') }}</button>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
          </div>
        </div>
        
        <!-- Logs Table -->
        <div class="logs-table-container">
          <table class="logs-table">
            <thead>
              <tr>
<<<<<<< HEAD
                <th>ID</th>
                <th>Type</th>
                <th>User</th>
                <th>Action</th>
                <th>Target</th>
                <th>IP Address</th>
                <th>Time</th>
                <th>Status</th>
=======
                <th>{{ $t('logs.table.id') }}</th>
                <th>{{ $t('logs.table.type') }}</th>
                <th>{{ $t('logs.table.user') }}</th>
                <th>{{ $t('logs.table.action') }}</th>
                <th>{{ $t('logs.table.target') }}</th>
                <th>{{ $t('logs.table.ip') }}</th>
                <th>{{ $t('logs.table.time') }}</th>
                <th>{{ $t('logs.table.status') }}</th>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in paginatedLogs" :key="log.id" class="log-row">
                <td class="log-id">{{ log.id }}</td>
                <td>
                  <span class="log-type-badge" :class="log.type">
                    {{ getLogTypeName(log.type) }}
                  </span>
                </td>
                <td class="log-user">{{ log.user || 'System' }}</td>
                <td class="log-action">{{ log.action }}</td>
                <td class="log-target">{{ log.target || '-' }}</td>
                <td class="log-ip">{{ log.ip || '-' }}</td>
                <td class="log-time">{{ log.time }}</td>
                <td>
                  <span class="status-badge" :class="getStatusClass(log.status)">
                    {{ log.status }}
                  </span>
                </td>
              </tr>
              
              <!-- Empty State -->
              <tr v-if="paginatedLogs.length === 0" class="empty-row">
                <td colspan="8" class="empty-cell">
                  <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 1a7 7 0 1 1 0 14A7 7 0 0 1 8 1zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm5.5 3a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm-3-8a1 1 0 0 1 1-1h1a1 1 0 1 1 0 2H3.5a1 1 0 0 1-1-1zm8 7a1 1 0 1 0 0-2h-1a1 1 0 1 0 0 2h1z"/>
                    </svg>
<<<<<<< HEAD
                    <p>No matching logs found</p>
=======
                    <p>{{ $t('logs.table.empty') }}</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div class="pagination" v-if="pagination.total > 0">
          <div class="pagination-info">
            Total {{ pagination.total }} records, Page {{ pagination.currentPage }} / {{ Math.ceil(pagination.total / pagination.pageSize) }}
          </div>
          <div class="pagination-controls">
            <button 
              class="page-btn" 
              :disabled="pagination.currentPage === 1"
              @click="pagination.currentPage--"
            >
              Previous
            </button>
            <button 
              class="page-btn" 
              :disabled="pagination.currentPage === Math.ceil(pagination.total / pagination.pageSize)"
              @click="pagination.currentPage++"
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- Confirm Modal -->
    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="modal">
        <div class="modal-header">
<<<<<<< HEAD
          <h2>Confirm Clear Logs</h2>
          <button class="close-btn" @click="cancelClearLogs">&times;</button>
        </div>
        <div class="modal-content">
          <p>Are you sure you want to clear all logs? This action cannot be undone!</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="cancelClearLogs">Cancel</button>
          <button class="btn btn-danger" @click="confirmClearLogs">Clear All</button>
=======
          <h2>{{ $t('logs.actions.confirmClearTitle') }}</h2>
          <button class="close-btn" @click="cancelClearLogs">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ $t('logs.actions.confirmClearMessage') }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="cancelClearLogs">{{ $t('logs.actions.cancel') }}</button>
          <button class="btn btn-danger" @click="confirmClearLogs">{{ $t('logs.actions.confirm') }}</button>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
        </div>
      </div>
    </div>

    <footer class="footer">
      <div class="footer-content">
<<<<<<< HEAD
        <p>&copy; 2026 Journal Platform. All rights reserved.</p>
=======
        <p>&copy; 2026 {{ $t('common.platformName') }}. All rights reserved.</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.admin-logs-management-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 日志区域样式 */
.logs-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 日志类型标签页样式 */
.log-type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0;
}

.tab-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  background-color: #f8f9fa;
  color: #6c757d;
  border-radius: 6px 6px 0 0;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  background-color: #e9ecef;
  color: #495057;
}

.tab-btn.active {
  background-color: white;
  color: #3498db;
  border-bottom-color: #3498db;
}

/* 日志头部样式 */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* 筛选控件样式 */
.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.date-filters {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.date-input {
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.date-separator {
  color: #6c757d;
  font-weight: 500;
}

/* 按钮样式 */
.btn {
  padding: 0.9rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-export {
  background-color: #3498db;
  color: white;
}

.btn-export:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.btn-reset {
  background-color: #95a5a6;
  color: white;
}

.btn-reset:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

/* 日志列表样式 */
.logs-table-container {
  overflow-x: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  background-color: white;
}

.logs-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 10;
}

.logs-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
  vertical-align: top;
}

.log-row:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

/* 日志类型徽章样式 */
.log-type-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.log-type-badge.operation {
  background-color: #d4edda;
  color: #155724;
}

.log-type-badge.login {
  background-color: #cce7ff;
  color: #004085;
}

.log-type-badge.error {
  background-color: #f8d7da;
  color: #721c24;
}

/* 状态徽章样式 */
.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.success {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.error {
  background-color: #f8d7da;
  color: #721c24;
}

/* 日志列表列样式 */
.log-id {
  width: 60px;
  font-weight: 600;
  color: #6c757d;
}

.log-user {
  width: 120px;
  font-weight: 500;
}

.log-action {
  min-width: 150px;
}

.log-target {
  min-width: 150px;
}

.log-ip {
  width: 120px;
  color: #6c757d;
}

.log-time {
  width: 160px;
  color: #6c757d;
}

/* 空状态样式 */
.empty-row {
  text-align: center;
}

.empty-cell {
  padding: 4rem 2rem;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  color: #95a5a6;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0;
  color: #7f8c8d;
  font-size: 1rem;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.95rem;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.6rem 1.2rem;
  border: 1px solid #ddd;
  background-color: white;
  color: #3498db;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #e3f2fd;
  border-color: #3498db;
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 页脚样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.footer-content p {
  margin: 0;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  border-radius: 8px 8px 0 0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #2c3e50;
}

.modal-content {
  padding: 1.5rem;
  font-size: 1rem;
  color: #495057;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid #e9ecef;
}

.btn-cancel {
  background-color: #95a5a6;
  color: white;
}

.btn-cancel:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .logs-section {
    padding: 1.5rem;
  }
  
  .log-type-tabs {
    flex-wrap: wrap;
  }
  
  .logs-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .date-filters {
    flex-wrap: wrap;
  }
  
  .log-actions {
    display: flex;
    gap: 1rem;
    justify-content: stretch;
  }
  
  .btn {
    flex: 1;
    min-width: auto;
  }
  
  .logs-table {
    font-size: 0.85rem;
  }
  
  .logs-table th,
  .logs-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .pagination-info {
    text-align: center;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  /* 响应式模态框 */
  .modal {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-content {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
    flex-direction: column;
  }
  
  .modal-footer .btn {
    flex: 1;
    min-width: auto;
  }
}
</style>