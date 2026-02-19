<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'

const router = useRouter()
const userStore = useUserStore()

// Filters
const selectedStatus = ref('all')
const selectedModule = ref('all')
const searchKeyword = ref('')
const selectedTimePeriod = ref('all') // 'all', 'day', 'week', 'month', 'year'

// Options
const statusOptions = ['all', 'Submitted', 'Under Review', 'Accepted', 'Rejected', 'Revision Requested']
const moduleOptions = computed(() => {
  const modules = userStore.journals.map(journal => journal.module)
  return ['all', ...Array.from(new Set(modules))]
})

// Time Period Options
const timePeriodOptions = [
  { value: 'all', label: 'All Time' },
  { value: 'day', label: 'Last 24 Hours' },
  { value: 'week', label: 'Last Week' },
  { value: 'month', label: 'Last Month' },
  { value: 'year', label: 'Last Year' }
]

// 稿件数据
const manuscripts = computed(() => {
  return userStore.journals.filter(journal => {
    // 只显示当前用户的稿件
    if (journal.writer !== userStore.user?.username) {
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
          !journal.writer.toLowerCase().includes(keyword) && 
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

// 查看稿件详情
const viewManuscript = (id) => {
  router.push(`/admin/review-records/${id}`)
}
</script>

<template>
  <div class="my-manuscripts-container">
    <div class="page-header">
      <button class="btn btn-secondary" @click="router.back()">Back</button>
      <h1>My Manuscripts</h1>
    </div>
    
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label for="search-input">Keyword Search:</label>
          <input 
            type="text" 
            id="search-input" 
            v-model="searchKeyword" 
            placeholder="Search Title, Writer or Keywords" 
            class="filter-control search-input"
          >
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label for="status-filter">Status Filter:</label>
          <select id="status-filter" v-model="selectedStatus" class="filter-control">
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status === 'all' ? 'All Status' : status }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="module-filter">Module Filter:</label>
          <select id="module-filter" v-model="selectedModule" class="filter-control">
            <option v-for="module in moduleOptions" :key="module" :value="module">
              {{ module === 'all' ? 'All Modules' : module }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="time-period-filter">Time Period:</label>
          <select id="time-period-filter" v-model="selectedTimePeriod" class="filter-control">
            <option v-for="option in timePeriodOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <div class="manuscripts-table-wrapper">
      <table class="manuscripts-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Module</th>
            <th>Status</th>
            <th>Submitted Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="manuscript in manuscripts" :key="manuscript.id">
            <td class="title-cell">{{ manuscript.title }}</td>
            <td>{{ manuscript.module }}</td>
            <td>
              <span class="status-badge" :class="manuscript.status.toLowerCase().replace(/\s/g, '-')">
                {{ manuscript.status }}
              </span>
            </td>
            <td>{{ manuscript.submitDate }}</td>
            <td>
              <button class="btn btn-primary btn-sm" @click="viewManuscript(manuscript.id)">
                View Details
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Empty State -->
      <div v-if="manuscripts.length === 0" class="empty-state">
        <p>No manuscripts found</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-manuscripts-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
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
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-group.date-range {
  align-items: center;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-separator {
  color: #666;
  font-size: 0.9rem;
  margin: 0 0.25rem;
}

.date-input {
  min-width: 140px;
}

.search-input {
  min-width: 250px;
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

/* 视图切换标签页样式 */
.view-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background-color: white;
  padding: 0.3rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.tab-btn {
  flex: 1;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  background-color: #f8f9fa;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background-color: #e9ecef;
  color: #333;
}

.tab-btn.active {
  background-color: #3498db;
  color: white;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.tab-btn:focus {
  outline: none;
}

.filter-control {
  padding: 0.7rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  min-width: 150px;
}

/* 稿件进度相关样式 */
.manuscript-detail-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.manuscript-detail-header h2 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.manuscript-detail-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: #666;
}

.detail-meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.已投稿 {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.审核中 {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.已录用 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已拒稿 {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-badge.修改再审 {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.progress-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.progress-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.progress-timeline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  padding: 0 1rem;
}

.progress-timeline::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e9ecef;
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
}

.step-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #e9ecef;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e9ecef;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.85rem;
  color: #666;
  text-align: center;
  transition: all 0.3s ease;
}

.progress-step.completed .step-dot {
  background-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

.progress-step.completed .step-label {
  color: #3498db;
  font-weight: 500;
}

.progress-step.current .step-dot {
  background-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
  transform: scale(1.2);
}

.progress-step.current .step-label {
  color: #3498db;
  font-weight: 600;
}

.review-records-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.review-records-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.review-records-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-record-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.review-record-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.record-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.record-stage {
  font-weight: 600;
  color: #2c3e50;
}

.record-date {
  color: #666;
  font-size: 0.9rem;
}

.reviewer-name {
  color: #666;
  font-size: 0.9rem;
}

.record-result {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.record-result.通过 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.record-result.修改 {
  background-color: #fff3e0;
  color: #f57c00;
}

.record-result.不通过 {
  background-color: #ffebee;
  color: #d32f2f;
}

.record-comment, .record-modifications {
  margin-bottom: 1rem;
}

.record-comment h4, .record-modifications h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.record-comment p, .record-modifications p {
  margin: 0;
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap;
  background-color: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.no-records {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 2rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  color: #999;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .progress-timeline {
    padding: 0 0.5rem;
  }
  
  .step-label {
    font-size: 0.75rem;
  }
  
  .record-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .record-meta {
    gap: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    margin: 1rem;
  }
  
  .btn {
    width: 100%;
  }
  
  .manuscript-detail-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .progress-section, .review-records-section {
    padding: 1rem;
  }
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.manuscripts-table-wrapper {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
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
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.已投稿 {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.审核中 {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.已录用 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已拒稿 {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-badge.修改再审 {
  background-color: #f3e5f5;
  color: #7b1fa2;
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

.btn-primary:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .my-manuscripts-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters-section {
    padding: 1rem;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
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
}
</style>