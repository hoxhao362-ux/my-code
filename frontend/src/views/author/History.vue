<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../../composables/useI18n'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import SkeletonLoader from '../../components/common/SkeletonLoader.vue'
import { exportToExcel } from '../../utils/export'

const { t } = useI18n()
const userStore = useUserStore()
const router = useRouter()

const isLoading = ref(true)

onMounted(() => {
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
})

// 筛选状态
const selectedModule = ref('all')
const timeRange = ref('all')
const selectedStatus = ref('all')
const keyword = ref('')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

// 模块选项
const modules = computed(() => userStore.modules || [])

// 状态选项
const statusOptions = ['all', 'submitted', 'underReview', 'accepted', 'rejected', 'revisionRequested']

// 过滤后的数据
const filteredData = computed(() => {
  let data = userStore.userJournals || []
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    data = data.filter(item => item.module === selectedModule.value)
  }
  
  // 状态筛选
  if (selectedStatus.value !== 'all') {
    data = data.filter(item => item.status && item.status.toLowerCase() === selectedStatus.value.toLowerCase())
  }
  
  // 关键词筛选
  if (keyword.value) {
    const k = keyword.value.toLowerCase()
    data = data.filter(item => 
      (item.title && item.title.toLowerCase().includes(k)) ||
      (item.id && String(item.id).includes(k))
    )
  }
  
  // 时间范围筛选
  const now = new Date()
  let startDate
  switch (timeRange.value) {
    case 'today':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      break
    case 'week':
      startDate = new Date(now.setDate(now.getDate() - 7))
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
      break
    case 'year':
      startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
      break
    default:
      startDate = null
  }
  
  if (startDate) {
    data = data.filter(item => new Date(item.date) >= startDate)
  }
  
  // 按时间降序排序
  return data.sort((a, b) => new Date(b.date) - new Date(a.date))
})

// 分页数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const total = computed(() => filteredData.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 重置筛选
const resetFilters = () => {
  selectedModule.value = 'all'
  timeRange.value = 'all'
  selectedStatus.value = 'all'
  keyword.value = ''
  currentPage.value = 1
}

// 导出数据
const exportData = () => {
  const dataToExport = filteredData.value.map(item => ({
    ID: item.id,
    [t('history.table.title')]: item.title,
    [t('history.table.module')]: item.module,
    [t('history.table.status')]: item.status,
    [t('history.table.submitDate')]: item.date
  }))
  exportToExcel(dataToExport, `Submission_History_${new Date().toISOString().split('T')[0]}`)
}

// 查看详情
const viewJournalDetail = (id) => {
  router.push(`/journal/${id}`)
}

// 状态样式映射
const getStatusClass = (status) => {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s === 'accepted' || s === 'published') return 'status-accepted'
  if (s === 'rejected') return 'status-rejected'
  if (s === 'under review' || s === 'underreview') return 'status-under-review'
  if (s === 'revision requested' || s === 'revisionrequested') return 'status-revision'
  return 'status-pending'
}
</script>

<template>
  <div class="history-container">
    <Navigation 
      :user="userStore.user"
      :current-page="'author-history'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <main class="history-content">
      <div class="page-header">
        <h1 class="page-title">{{ t('history.title.submissionHistory') }}</h1>
      </div>
      
      <section class="history-card">
        <!-- 筛选区域 -->
        <div class="filters-header">
          <div class="filter-controls">
            <!-- 关键词搜索 -->
            <div class="search-box">
              <input 
                type="text" 
                v-model="keyword" 
                :placeholder="t('history.filters.searchPlaceholder')"
                class="form-control"
              >
            </div>
            
            <!-- 模块筛选 -->
            <select v-model="selectedModule" class="form-select">
              <option value="all">{{ t('history.filters.allModules') }}</option>
              <option v-for="m in modules" :key="m" :value="m">{{ m }}</option>
            </select>
            
            <!-- 状态筛选 -->
            <select v-model="selectedStatus" class="form-select">
              <option value="all">{{ t('history.filters.allStatus') }}</option>
              <option value="submitted">{{ t('history.status.submitted') }}</option>
              <option value="underReview">{{ t('history.status.underReview') }}</option>
              <option value="accepted">{{ t('history.status.accepted') }}</option>
              <option value="rejected">{{ t('history.status.rejected') }}</option>
              <option value="revisionRequested">{{ t('history.status.revisionRequested') }}</option>
            </select>
            
            <!-- 时间筛选 -->
            <select v-model="timeRange" class="form-select">
              <option value="all">{{ t('history.filters.allTime') }}</option>
              <option value="today">{{ t('history.filters.today') }}</option>
              <option value="week">{{ t('history.filters.week') }}</option>
              <option value="month">{{ t('history.filters.month') }}</option>
              <option value="year">{{ t('history.filters.year') }}</option>
            </select>
            
            <button class="btn btn-secondary" @click="resetFilters">
              {{ t('history.reset') }}
            </button>
          </div>
          
          <div class="action-buttons">
            <button class="btn btn-primary" @click="exportData" :disabled="total === 0">
              {{ t('history.export') }}
            </button>
          </div>
        </div>
        
        <!-- 数据表格 -->
        <div class="table-container">
          <SkeletonLoader :loading="isLoading" :count="5" height="60px">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>{{ t('history.table.title') }}</th>
                <th>{{ t('history.table.module') }}</th>
                <th>{{ t('history.table.submitDate') }}</th>
                <th>{{ t('history.table.status') }}</th>
                <th>{{ t('history.table.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedData" :key="item.id">
                <td class="col-id">#{{ item.id }}</td>
                <td class="col-title" :title="item.title">
                  <span class="title-link" @click="viewJournalDetail(item.id)">
                    {{ item.title }}
                  </span>
                </td>
                <td>{{ item.module }}</td>
                <td>{{ item.date }}</td>
                <td>
                  <span class="status-badge" :class="getStatusClass(item.status)">
                    {{ item.status }}
                  </span>
                </td>
                <td>
                  <button class="btn-link" @click="viewJournalDetail(item.id)">
                    {{ t('history.table.viewDetail') }}
                  </button>
                </td>
              </tr>
              <tr v-if="paginatedData.length === 0">
                <td colspan="6" class="empty-state">
                  {{ t('history.noRecords') }}
                </td>
              </tr>
            </tbody>
          </table>
          </SkeletonLoader>
        </div>
        
        <!-- 分页控件 -->
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
      </section>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.history-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.history-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1rem;
}

.page-title {
  font-family: 'Georgia', serif; /* Academic style */
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

.history-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-controls {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  align-items: center;
}

.form-control, .form-select {
  padding: 0.6rem 1rem;
  border: 1px solid #dce0e4;
  border-radius: 4px;
  font-size: 0.95rem;
  min-width: 140px;
}

.search-box .form-control {
  min-width: 240px;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #0056b3; /* Academic Blue */
  color: white;
}

.btn-primary:hover {
  background-color: #004494;
}

.btn-secondary {
  background-color: #f0f2f5;
  color: #555;
}

.btn-secondary:hover {
  background-color: #e4e6e9;
}

.btn-link {
  background: none;
  border: none;
  color: #0056b3;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.data-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #e9ecef;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.col-id {
  color: #888;
  width: 80px;
}

.col-title {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-link {
  color: #2c3e50;
  font-weight: 500;
  cursor: pointer;
}

.title-link:hover {
  color: #0056b3;
}

.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-accepted {
  background-color: #d4edda;
  color: #155724;
}

.status-rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.status-under-review {
  background-color: #cce5ff;
  color: #004085;
}

.status-revision {
  background-color: #fff3cd;
  color: #856404;
}

.status-pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
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

.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1.5rem;
  text-align: center;
  margin-top: auto;
}

.footer-content p {
  margin: 0;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .history-content {
    padding: 1rem;
  }
  
  .filters-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box .form-control {
    width: 100%;
    min-width: 0;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
