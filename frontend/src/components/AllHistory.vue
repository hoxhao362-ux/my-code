<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import Navigation from './Navigation.vue'
import { stripHtmlTags, truncateText } from '../utils/helpers.js'
import { exportToExcel } from '../utils/export'

const { t } = useI18n()

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'journals', 'modules', 'updateJournals', 'toggleDirectory', 'logout'])

// 时间范围筛选
const timeRange = ref('all') // 'all', 'today', 'week', 'month', 'year'
// 模块筛选
const selectedModule = ref('all')
// 稿件状态筛选
const selectedStatus = ref('all') // 'all', '已通过', '未通过', '复审', '终审'
// 当前页码
const currentPage = ref(1)
// 每页显示数量
const pageSize = ref(10)
// 搜索查询
const searchQuery = ref('')

// 通用时间范围筛选函数
const filterByTimeRange = (journals, dateField = 'date') => {
  if (timeRange.value === 'all') {
    return journals
  }
  
  const now = new Date()
  let startDate
  
  // 为每个case创建新的Date对象，避免修改原始now对象
  switch (timeRange.value) {
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
    return journals.filter(journal => new Date(journal[dateField]) >= startDate)
  }
  
  return journals
}

// 所有历史记录
const allHistory = computed(() => {
  // 先获取所有历史记录，包括已通过、未通过以及过初审进入复审/终审的稿件
  let journals = props.journals.filter(journal => 
    journal.status === '已通过' || 
    journal.status === '未通过' ||
    journal.status === '已发表' ||
    (journal.status === '审稿中' && (journal.reviewStage === '复审' || journal.reviewStage === '终审'))
  )
  
  // 角色筛选：审核人员只能看到自己参与过复审的稿件
  if (props.user.role === 'reviewer') {
    journals = journals.filter(journal => {
      // 检查是否有该审核人员参与的复审记录
      return journal.reviewHistory && journal.reviewHistory.some(record => 
        record.stage === '复审' && record.reviewer === props.user.username
      )
    })
  }
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
  }
  
  // 稿件状态筛选
  if (selectedStatus.value !== 'all') {
    if (selectedStatus.value === '复审') {
      journals = journals.filter(journal => journal.reviewStage === '复审')
    } else if (selectedStatus.value === '终审') {
      journals = journals.filter(journal => journal.reviewStage === '终审')
    } else {
      // 处理状态筛选，"已通过"包含"已发表"状态
      journals = journals.filter(journal => 
        journal.status === selectedStatus.value || 
        (selectedStatus.value === '已通过' && journal.status === '已发表')
      )
    }
  }
  
  // 时间范围筛选
  journals = filterByTimeRange(journals)
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    journals = journals.filter(journal => 
      journal.title.toLowerCase().includes(query) ||
      journal.author.toLowerCase().includes(query) ||
      journal.abstract.toLowerCase().includes(query) ||
      journal.keywords.some(keyword => keyword.toLowerCase().includes(query))
    )
  }
  
  return journals
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(allHistory.value.length / pageSize.value)
})

// 当前页显示的历史记录
const paginatedHistory = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return allHistory.value.slice(startIndex, endIndex)
})

// 导航到上一页
const goToPrevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 导航到下一页
const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 处理退出登录
const handleLogout = () => {
  props.logout()
}

// 查看稿件详情
const viewJournalDetail = (id) => {
  // 跳转到稿件详情页
  props.navigateTo('journal', id)
}

// 导出数据
const exportHistory = () => {
  const dataToExport = allHistory.value.map(item => ({
    ID: item.id,
    [t('history.table.title')]: item.title,
    [t('history.table.author')]: item.author,
    [t('history.table.module')]: item.module,
    [t('history.table.status')]: item.reviewResult || item.status,
    [t('history.table.submitDate')]: item.date,
    [t('history.table.reviewDate')]: item.reviewDate
  }))
  exportToExcel(dataToExport, `Review_History_${new Date().toISOString().split('T')[0]}`)
}

// 状态显示辅助函数
const getStatusLabel = (status) => {
  const map = {
    '已通过': t('history.status.accepted'),
    '未通过': t('history.status.rejected'),
    '已发表': t('history.status.published'),
    '复审': t('history.status.peer'),
    '终审': t('history.status.final')
  }
  return map[status] || status
}

// 组件挂载时滚动到页面顶部
onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<template>
  <div class="review-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'review'"
      :toggle-directory="toggleDirectory"
      :navigate-to="navigateTo"
      :logout="logout"
    />

    <!-- 审稿内容 -->
    <main class="review-content">
      <div class="review-header">
        <div class="header-flex">
          <button class="btn btn-back" @click="navigateTo('review')">{{ t('common.back') }}</button>
          <h2 class="review-title">{{ t('history.title.reviewHistory') }}</h2>
        </div>
        <div class="review-actions">
           <button class="btn btn-export" @click="exportHistory" :disabled="allHistory.length === 0">
             {{ t('history.export') }}
           </button>
        </div>
      </div>

      <!-- 历史记录筛选控件 -->
      <div class="filter-section">
        <div class="history-filters">
          <!-- 搜索输入框 -->
          <div class="search-filter">
            <label for="all-history-search-input" class="filter-label">{{ t('history.filters.keyword') }}：</label>
            <input 
              type="text" 
              id="all-history-search-input" 
              v-model="searchQuery"
              class="search-input"
              :placeholder="t('history.filters.searchPlaceholder')"
            >
          </div>
          
          <!-- 模块筛选 -->
          <div class="filter-group">
            <label for="history-module-filter">{{ t('history.filters.module') }}：</label>
            <select 
              id="history-module-filter" 
              v-model="selectedModule"
              class="filter-select"
            >
              <option value="all">{{ t('history.filters.allModules') }}</option>
              <option 
                v-for="module in modules" 
                :key="module"
                :value="module"
              >
                {{ module }}
              </option>
            </select>
          </div>
          
          <!-- 稿件状态筛选 -->
          <div class="filter-group">
            <label for="status-filter" class="filter-label">{{ t('history.filters.status') }}：</label>
            <select 
              id="status-filter" 
              v-model="selectedStatus"
              class="filter-select"
            >
              <option value="all">{{ t('history.filters.allStatus') }}</option>
              <option value="已通过">{{ t('history.status.accepted') }}</option>
              <option value="未通过">{{ t('history.status.rejected') }}</option>
              <option value="复审">{{ t('history.status.peer') }}</option>
              <option value="终审">{{ t('history.status.final') }}</option>
            </select>
          </div>
          
          <!-- 时间范围筛选 -->
          <div class="filter-group">
            <label for="time-range-filter" class="filter-label">{{ t('history.filters.timeRange') }}：</label>
            <select 
              id="time-range-filter" 
              v-model="timeRange"
              class="filter-select"
            >
              <option value="all">{{ t('history.filters.allTime') }}</option>
              <option value="today">{{ t('history.filters.today') }}</option>
              <option value="week">{{ t('history.filters.week') }}</option>
              <option value="month">{{ t('history.filters.month') }}</option>
              <option value="year">{{ t('history.filters.year') }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 历史记录列表 -->
      <div class="history-list">
          <div 
            v-for="journal in paginatedHistory" 
            :key="journal.id" 
            class="history-item"
          >
            <div class="journal-info">
              <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h3>
              <p class="journal-meta">
                {{ t('history.table.author') }}：{{ journal.author }} | 
                {{ t('history.table.submitDate') }}：{{ journal.date }} | 
                {{ t('history.table.reviewDate') }}：{{ journal.reviewDate }} | 
                <span class="review-result" :class="(journal.reviewResult || journal.status).toLowerCase()">
                  {{ getStatusLabel(journal.reviewResult || journal.status) }}
                </span>
              </p>
              <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
              
              <!-- 显示审稿建议 -->
            <div class="history-comment-section">
              <h4 class="comment-section-title">{{ t('history.reviewComment') }}：</h4>
              <div class="history-comment">
                <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
                  <div v-for="(record, index) in journal.reviewHistory" :key="index" class="stage-comment">
                    <div class="stage-header">
                      <span class="stage-name">{{ record.stage }}：</span>
                      <span class="stage-status" :class="record.status.toLowerCase()">{{ getStatusLabel(record.status) }}</span>
                    </div>
                    <div class="stage-content">{{ record.comment }}</div>
                  </div>
                </div>
                <div v-else>
                  {{ t('history.noComment') }}
                </div>
              </div>
            </div>
            </div>
          </div>

          <!-- 无历史记录提示 -->
          <div v-if="allHistory.length === 0" class="no-journals">
            <p>{{ t('history.noRecords') }}</p>
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 0" class="pagination">
          <div class="pagination-info">
            {{ t('history.pagination.total', { total: allHistory.length }) }}，
            {{ t('history.pagination.page', { current: currentPage, total: totalPages }) }}
          </div>
          <div class="pagination-controls">
            <button 
              class="page-btn" 
              :disabled="currentPage === 1"
              @click="goToPrevPage"
            >
              {{ t('history.pagination.prev') }}
            </button>
            <button 
              class="page-btn" 
              :disabled="currentPage === totalPages"
              @click="goToNextPage"
            >
              {{ t('history.pagination.next') }}
            </button>
          </div>
        </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
<<<<<<< HEAD
        <p>&copy; 2026 Journal Platform. All rights reserved.</p>
=======
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>
    </footer>
  </div>
</template>

<style scoped>
.review-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 审稿内容 */
.review-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.review-title {
  font-family: 'Georgia', serif;
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

/* 头部flex布局 */
.header-flex {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 历史记录筛选控件 */
.filter-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.history-filters {
  display: flex;
  align-items: flex-end;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-filter {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.history-filters label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.history-filters .filter-select,
.history-filters input[type="text"] {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.3s ease;
  min-width: 140px;
}

.history-filters .filter-select:focus,
.history-filters input[type="text"]:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.btn-export {
  background: #3498db;
  color: white;
  padding: 0.6rem 1.2rem;
  font-size: 0.9rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-export:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-export:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* 历史记录列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.history-item:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-family: 'Georgia', serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.journal-meta {
  color: #7f8c8d;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.journal-abstract {
  color: #555;
  line-height: 1.6;
  margin: 0;
  font-size: 0.95rem;
  font-style: italic;
}

/* 审核结果状态 */
.review-result {
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.review-result.已通过 {
  background: #d4edda;
  color: #155724;
}

.review-result.已拒绝, .review-result.未通过 {
  background: #f8d7da;
  color: #721c24;
}

/* 历史记录中的审稿建议 */
.history-comment-section {
  margin-top: 1.5rem;
  padding: 1.2rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.comment-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.8rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-comment {
  color: #555;
  line-height: 1.6;
}

/* 返回按钮样式 */
.btn-back {
  background: #95a5a6;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: #7f8c8d;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.5rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f5f7fa;
  border-color: #3498db;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f8f9fa;
  border-color: #e9ecef;
  color: #6c757d;
}

/* 无历史记录提示 */
.no-journals {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.no-journals p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* 页脚 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 1.5rem;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .review-content {
    padding: 1rem;
  }
  
  .history-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filter {
    min-width: 0;
  }
}
</style>