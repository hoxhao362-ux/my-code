<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../../../composables/useI18n'
import { useUserStore } from '../../../stores/user'
import { exportToExcel } from '../../../utils/export'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

// Filters
const selectedStatus = ref('all')
const selectedModule = ref('all')
const searchKeyword = ref('')
const selectedTimePeriod = ref('all') // 'all', 'day', 'week', 'month', 'year'

// Pagination
const currentPage = ref(1)
const pageSize = ref(10)

// Options
const statusOptions = ['all', 'Pending', 'Under Review', 'Accepted', 'Rejected', 'Revision Requested']
const moduleOptions = computed(() => {
  const modules = userStore.journals.map(journal => journal.module)
  return ['all', ...Array.from(new Set(modules))]
})

// Time Period Options
const timePeriodOptions = [
  { value: 'all', label: 'history.filters.allTime' },
  { value: 'day', label: 'history.filters.today' },
  { value: 'week', label: 'history.filters.week' },
  { value: 'month', label: 'history.filters.month' },
  { value: 'year', label: 'history.filters.year' }
]

// 稿件数据 - 这里可以根据状态筛选已归档的稿件
const filteredManuscripts = computed(() => {
  return userStore.journals.filter(journal => {
    // 只显示当前用户的稿件
    if ((journal.author || journal.writer) !== userStore.user?.username) {
      return false
    }
    
    // 状态筛选
    if (selectedStatus.value !== 'all' && journal.status !== selectedStatus.value) {
      return false
    }
    
    // 模块筛选
    if (selectedModule.value !== 'all' && journal.module !== selectedModule.value) {
      return false
    }
    
    // 关键词搜索
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      if (!journal.title.toLowerCase().includes(keyword) && 
          !(journal.author || journal.writer || '').toLowerCase().includes(keyword) && 
          !journal.keywords.toLowerCase().includes(keyword)) {
        return false
      }
    }
    
    // 时间段筛选
    if (selectedTimePeriod.value !== 'all') {
      const now = new Date()
      const journalDate = new Date(journal.date || journal.submitDate)
      let timeThreshold = new Date()
      
      switch (selectedTimePeriod.value) {
        case 'day':
          timeThreshold.setDate(now.getDate() - 1)
          break
        case 'week':
          timeThreshold.setDate(now.getDate() - 7)
          break
        case 'month':
          timeThreshold.setMonth(now.getMonth() - 1)
          break
        case 'year':
          timeThreshold.setFullYear(now.getFullYear() - 1)
          break
      }
      
      if (journalDate < timeThreshold) {
        return false
      }
    }
    
    return true
  })
})

const paginatedManuscripts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredManuscripts.value.slice(start, end)
})

const total = computed(() => filteredManuscripts.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 查看稿件详情
const viewManuscript = (id) => {
  router.push(`/admin/journal/${id}`)
}

// 导出数据
const exportHistory = () => {
  const dataToExport = filteredManuscripts.value.map(item => ({
    ID: item.id,
    [t('history.table.title')]: item.title,
    [t('history.table.module')]: item.module,
    [t('history.table.status')]: item.status,
    [t('history.table.submitDate')]: item.date || item.submitDate
  }))
  exportToExcel(dataToExport, `Manuscript_History_${new Date().toISOString().split('T')[0]}`)
}

// 状态显示辅助函数
const getStatusLabel = (status) => {
  if (!status) return ''
  const map = {
    'Accepted': t('history.status.accepted'),
    'Rejected': t('history.status.rejected'),
    'Pending': t('history.status.pending'),
    'Under Review': t('history.status.underReview'),
    'Revision Requested': t('history.status.revisionRequested')
  }
  return map[status] || status
}
</script>

<template>
  <div class="manuscript-history-container">
    <div class="page-header">
      <div class="header-left">
        <button class="btn btn-secondary" @click="router.back()">{{ t('common.back') }}</button>
        <h1>{{ t('history.title.manuscriptHistory') }}</h1>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="exportHistory" :disabled="total === 0">
          {{ t('history.export') }}
        </button>
      </div>
    </div>
    
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group search-group">
          <label for="search-input">{{ t('history.filters.keyword') }}:</label>
          <input 
            type="text" 
            id="search-input" 
            v-model="searchKeyword" 
            :placeholder="t('history.filters.searchPlaceholder')" 
            class="filter-control search-input"
          >
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label for="status-filter">{{ t('history.filters.status') }}:</label>
          <select id="status-filter" v-model="selectedStatus" class="filter-control">
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status === 'all' ? t('history.filters.allStatus') : getStatusLabel(status) }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="module-filter">{{ t('history.filters.module') }}:</label>
          <select id="module-filter" v-model="selectedModule" class="filter-control">
            <option v-for="module in moduleOptions" :key="module" :value="module">
              {{ module === 'all' ? t('history.filters.allModules') : module }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="time-period-filter">{{ t('history.filters.timeRange') }}:</label>
          <select id="time-period-filter" v-model="selectedTimePeriod" class="filter-control">
            <option v-for="option in timePeriodOptions" :key="option.value" :value="option.value">
              {{ t(option.label) }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <div class="manuscripts-table-wrapper">
      <table class="manuscripts-table">
        <thead>
          <tr>
            <th>{{ t('history.table.title') }}</th>
            <th>{{ t('history.table.module') }}</th>
            <th>{{ t('history.table.status') }}</th>
            <th>{{ t('history.table.submitDate') }}</th>
            <th>{{ t('history.table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="manuscript in paginatedManuscripts" :key="manuscript.id">
            <td class="title-cell" :title="manuscript.title">{{ manuscript.title }}</td>
            <td>{{ manuscript.module }}</td>
            <td>
              <span class="status-badge" :class="manuscript.status.toLowerCase().replace(/\s/g, '-')">
                {{ getStatusLabel(manuscript.status) }}
              </span>
            </td>
            <td>{{ manuscript.date || manuscript.submitDate }}</td>
            <td>
              <button class="btn btn-primary btn-sm" @click="viewManuscript(manuscript.id)">
                {{ t('history.table.viewDetail') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Empty State -->
      <div v-if="filteredManuscripts.length === 0" class="empty-state">
        <p>{{ t('history.noRecords') }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="total > 0">
      <div class="pagination-info">
        {{ t('history.pagination.total', { total: total }) }}
      </div>
      <div class="pagination-controls">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          {{ t('history.pagination.prev') }}
        </button>
        <span class="page-current">
          {{ t('history.pagination.page', { current: currentPage, total: totalPages }) }}
        </span>
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          {{ t('history.pagination.next') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.manuscript-history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-header h1 {
  font-family: 'Georgia', serif;
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

.filters-section {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 1rem;
  align-items: center;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-group {
  flex: 1;
}

.search-input {
  width: 100%;
}

.filter-control {
  padding: 0.7rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  min-width: 150px;
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.filter-group label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.manuscripts-table-wrapper {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.manuscripts-table {
  width: 100%;
  border-collapse: collapse;
}

.manuscripts-table th,
.manuscripts-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.manuscripts-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.manuscripts-table tr:hover {
  background-color: #f8f9fa;
}

.title-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Georgia', serif;
  font-weight: 500;
  color: #2c3e50;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
  letter-spacing: 0.5px;
}

.status-badge.accepted, .status-badge.published {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.rejected {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-badge.pending {
  background-color: #fff8e1;
  color: #fbc02d;
}

.status-badge.under-review {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.revision-requested {
  background-color: #fff3e0;
  color: #f57c00;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1.1rem;
}

.btn {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.page-btn {
  padding: 0.4rem 0.8rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-current {
  font-size: 0.9rem;
  color: #495057;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .manuscript-history-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left {
    justify-content: space-between;
  }
  
  .manuscripts-table {
    font-size: 0.85rem;
  }
  
  .manuscripts-table th,
  .manuscripts-table td {
    padding: 0.7rem 0.5rem;
  }
  
  .title-cell {
    max-width: 150px;
  }
  
  .btn-sm {
    padding: 0.4rem 0.7rem;
    font-size: 0.75rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>