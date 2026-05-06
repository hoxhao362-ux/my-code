<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 筛选条件
const searchQuery = ref('')
const selectedModule = ref('all')
const selectedStatus = ref('all')
const selectedTimePeriod = ref('all')

// 获取所有可用模块
const modules = computed(() => userStore.modules)

// 获取所有可用状态
const statusOptions = computed(() => {
  const statuses = userStore.journals.map(journal => journal.status)
  return ['all', ...Array.from(new Set(statuses))]
})

// 时间段选项
const timePeriodOptions = [
  { value: 'all', label: '全部时间' },
  { value: 'today', label: '今日' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
  { value: 'year', label: '本年' }
]

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选后的稿件列表
const filteredJournals = computed(() => {
  let journals = userStore.journals
  
  // 信息查询筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    journals = journals.filter(journal => 
      journal.title.toLowerCase().includes(query) ||
      journal.author.toLowerCase().includes(query) ||
      journal.abstract.toLowerCase().includes(query) ||
      journal.keywords.some(keyword => keyword.toLowerCase().includes(query))
    )
  }
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
  }
  
  // 状态筛选
  if (selectedStatus.value !== 'all') {
    journals = journals.filter(journal => journal.status === selectedStatus.value)
  }
  
  // 时间筛选
  if (selectedTimePeriod.value !== 'all') {
    const now = new Date()
    let startDate
    
    switch (selectedTimePeriod.value) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        break
      case 'week':
        startDate = new Date(now)
        startDate.setDate(startDate.getDate() - 7)
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
      journals = journals.filter(journal => new Date(journal.date) >= startDate)
    }
  }
  
  return journals
})

// 当前页显示的数据
const paginatedJournals = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredJournals.value.slice(startIndex, endIndex)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredJournals.value.length / pageSize.value) || 1
})

// 页码变化时的处理函数
const handlePageChange = (page) => {
  currentPage.value = page
}

// 筛选条件变化时重置页码
const resetPage = () => {
  currentPage.value = 1
}

// 决定是否显示某个页码按钮，避免显示过多页码
const shouldShowPage = (page) => {
  // 显示当前页前后各2页，以及首页和末页
  return page === 1 || 
         page === totalPages.value || 
         (page >= currentPage.value - 2 && page <= currentPage.value + 2)
}
</script>

<template>
  <div class="admin-profile-manuscript-status-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-profile-manuscript-status'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 稿件状态查询内容 -->
    <main class="content">
      <div class="header">
        <h1>个人中心 - 稿件状态查询</h1>
        <p class="subtitle">查询和管理稿件的状态</p>
      </div>

      <section class="manuscript-status-section">
        <div class="manuscript-status-card">
          <!-- 筛选条件 -->
          <div class="filters-container">
            <div class="filter-group">
              <label for="search-input">信息查询</label>
              <input 
                type="text" 
                id="search-input"
                v-model="searchQuery"
                class="filter-control"
                placeholder="搜索标题、作者、摘要或关键词"
                @input="resetPage"
              >
            </div>
            
            <div class="filter-group">
              <label for="module-filter">模块筛选</label>
              <select 
                id="module-filter"
                v-model="selectedModule"
                class="filter-control"
                @change="resetPage"
              >
                <option value="all">全部模块</option>
                <option 
                  v-for="module in modules" 
                  :key="module"
                  :value="module"
                >
                  {{ module }}
                </option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="status-filter">状态筛选</label>
              <select 
                id="status-filter"
                v-model="selectedStatus"
                class="filter-control"
                @change="resetPage"
              >
                <option value="all">全部状态</option>
                <option 
                  v-for="status in statusOptions" 
                  :key="status"
                  :value="status"
                >
                  {{ status }}
                </option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="time-filter">时间筛选</label>
              <select 
                id="time-filter"
                v-model="selectedTimePeriod"
                class="filter-control"
                @change="resetPage"
              >
                <option 
                  v-for="option in timePeriodOptions" 
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- 稿件列表 -->
          <div class="journals-list">
            <div class="journals-table-container">
              <table class="journals-table">
                <thead>
                  <tr>
                    <th>稿件标题</th>
                    <th>作者</th>
                    <th>模块</th>
                    <th>状态</th>
                    <th>投稿日期</th>
                    <th>审核阶段</th>
                    <th>阅读量</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="journal in paginatedJournals" :key="journal.id">
                    <td class="journal-title">{{ journal.title }}</td>
                    <td>{{ journal.author }}</td>
                    <td>{{ journal.module }}</td>
                    <td>
                      <span class="status-badge" :class="journal.status.toLowerCase().replace(/\s/g, '-')">
                        {{ journal.status }}
                      </span>
                    </td>
                    <td>{{ journal.date }}</td>
                    <td>{{ journal.reviewStage || '未开始' }}</td>
                    <td>{{ journal.viewCount || 0 }}</td>
                  </tr>
                  <tr v-if="paginatedJournals.length === 0">
                    <td colspan="7" class="no-data">暂无稿件数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- 分页控件 -->
            <div class="pagination-container" v-if="totalPages > 1">
              <div class="pagination-info">
                共 {{ filteredJournals.length }} 条记录，第 {{ currentPage }}/{{ totalPages }} 页
              </div>
              <div class="pagination-controls">
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === 1"
                  @click="handlePageChange(1)"
                >
                  首页
                </button>
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === 1"
                  @click="handlePageChange(currentPage - 1)"
                >
                  上一页
                </button>
                
                <!-- 页码按钮 -->
                <span class="pagination-numbers">
                  <button 
                    v-for="page in totalPages" 
                    :key="page"
                    class="pagination-btn"
                    :class="{ active: page === currentPage }"
                    @click="handlePageChange(page)"
                    v-if="shouldShowPage(page)"
                  >
                    {{ page }}
                  </button>
                </span>
                
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === totalPages"
                  @click="handlePageChange(currentPage + 1)"
                >
                  下一页
                </button>
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === totalPages"
                  @click="handlePageChange(totalPages)"
                >
                  末页
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.admin-profile-manuscript-status-container {
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

/* 稿件状态查询区域样式 */
.manuscript-status-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 稿件状态卡片样式 */
.manuscript-status-card {
  max-width: 100%;
}

/* 筛选条件样式 */
.filters-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.filter-control {
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 稿件列表样式 */
.journals-list {
  margin-top: 2rem;
}

.journals-table-container {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.journals-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.journals-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
  font-size: 0.95rem;
  white-space: nowrap;
}

.journals-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
  font-size: 0.95rem;
}

.journals-table tbody tr:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

.journal-title {
  font-weight: 500;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 状态标签样式 */
.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.待审核 {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.审核中 {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.已通过 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已发表 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.未通过 {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-badge.修改再审 {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

/* 无数据样式 */
.no-data {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-style: italic;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-info {
  color: #666;
  font-size: 0.95rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: white;
  color: #333;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  min-width: 36px;
  text-align: center;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f0f0f0;
  border-color: #3498db;
}

.pagination-btn.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  .pagination-btn {
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
  }
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

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .manuscript-status-section {
    padding: 1.5rem;
  }
  
  .filters-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .filter-group {
    width: 100%;
    min-width: auto;
  }
  
  .journals-table {
    font-size: 0.85rem;
  }
  
  .journals-table th,
  .journals-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .journal-title {
    max-width: 150px;
  }
}
</style>