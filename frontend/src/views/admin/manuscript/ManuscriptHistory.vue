<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 筛选条件
const selectedStatus = ref('all')
const selectedModule = ref('all')
const searchKeyword = ref('')
const selectedTimePeriod = ref('all') // 'all', 'day', 'week', 'month', 'year'

// 选项
const statusOptions = ['all', '待审核', '审核中', '已录用', '已拒稿', '修改再审']
const moduleOptions = computed(() => {
  const modules = userStore.journals.map(journal => journal.module)
  return ['all', ...Array.from(new Set(modules))]
})

// 时间段选项
const timePeriodOptions = [
  { value: 'all', label: '全部时间' },
  { value: 'day', label: '最近一天' },
  { value: 'week', label: '最近一周' },
  { value: 'month', label: '最近一月' },
  { value: 'year', label: '最近一年' }
]

// 稿件数据 - 这里可以根据状态筛选已归档的稿件
const archivedManuscripts = computed(() => {
  return userStore.journals.filter(journal => {
    // 只显示当前用户的稿件
    if (journal.author !== userStore.user?.username) {
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
          !journal.author.toLowerCase().includes(keyword) && 
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
  <div class="manuscript-history-container">
    <div class="page-header">
      <button class="btn btn-secondary" @click="router.back()">返回</button>
      <h1>历史投稿</h1>
    </div>
    
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label for="search-input">关键词搜索：</label>
          <input 
            type="text" 
            id="search-input" 
            v-model="searchKeyword" 
            placeholder="搜索标题、作者或关键词" 
            class="filter-control search-input"
          >
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label for="status-filter">状态筛选：</label>
          <select id="status-filter" v-model="selectedStatus" class="filter-control">
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status === 'all' ? '全部状态' : status }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="module-filter">模块筛选：</label>
          <select id="module-filter" v-model="selectedModule" class="filter-control">
            <option v-for="module in moduleOptions" :key="module" :value="module">
              {{ module === 'all' ? '全部模块' : module }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="time-period-filter">时间段：</label>
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
            <th>稿件标题</th>
            <th>模块</th>
            <th>状态</th>
            <th>提交时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="manuscript in archivedManuscripts" :key="manuscript.id">
            <td class="title-cell">{{ manuscript.title }}</td>
            <td>{{ manuscript.module }}</td>
            <td>
              <span class="status-badge" :class="manuscript.status.toLowerCase().replace(/\s/g, '-')">
                {{ manuscript.status }}
              </span>
            </td>
            <td>{{ manuscript.date || manuscript.submitDate }}</td>
            <td>
              <button class="btn btn-primary btn-sm" @click="viewManuscript(manuscript.id)">
                查看详情
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="archivedManuscripts.length === 0" class="empty-state">
        <p>暂无历史投稿记录</p>
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
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
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

.status-badge.已录用 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已拒稿 {
  background-color: #ffebee;
  color: #d32f2f;
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
  .manuscript-history-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
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