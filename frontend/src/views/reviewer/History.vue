<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 筛选相关状态
const timeRange = ref('all') // 'all', 'today', 'week', 'month', 'year'
const selectedModule = ref('all')
const selectedStatus = ref('all') // 'all', '已通过', '未通过', '复审', '终审'
const searchQuery = ref('')

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)

// 获取所有可用模块
const modules = computed(() => userStore.modules)

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

// 所有历史记录，包括已通过、未通过以及过初审进入复审/终审的稿件
const allHistory = computed(() => {
  // 基础筛选：获取所有非审稿中或处于复审/终审阶段的稿件
  let journals = userStore.journals.filter(journal => 
    journal.status === '已通过' || 
    journal.status === '未通过' ||
    (journal.status === '审稿中' && (journal.reviewStage === '复审' || journal.reviewStage === '终审'))
  )
  
  // 角色筛选：审核人员只能看到自己参与过复审的稿件
  journals = journals.filter(journal => {
    // 检查是否有该审核人员参与的复审记录
    return journal.reviewHistory && journal.reviewHistory.some(record => 
      record.stage === '复审' && record.reviewer === user.value.username
    )
  })
  
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
      journals = journals.filter(journal => journal.status === selectedStatus.value)
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

// 页码范围
const pageRange = computed(() => {
  const range = []
  const maxVisiblePages = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
  let end = Math.min(totalPages.value, start + maxVisiblePages - 1)
  
  // 调整起始页码以确保显示足够的页码
  if (end - start + 1 < maxVisiblePages) {
    start = Math.max(1, end - maxVisiblePages + 1)
  }
  
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  return range
})

// 导航到首页
const goToFirstPage = () => {
  currentPage.value = 1
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

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

// 导航到末页
const goToLastPage = () => {
  currentPage.value = totalPages.value
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 导航到指定页码
const goToPage = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="reviewer-history-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'reviewer-history'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 审核历史内容 -->
    <main class="content">
      <div class="header">
        <h1>审核历史</h1>
        <div class="review-stats">
          <span class="stat-item">历史记录总数：{{ allHistory.length }}</span>
        </div>
      </div>

      <!-- 筛选控件 -->
      <div class="filter-section">
        <div class="filters-container">
          <!-- 搜索输入框 -->
          <div class="search-filter">
            <label for="history-search-input" class="filter-label">搜索：</label>
            <input 
              type="text" 
              id="history-search-input" 
              v-model="searchQuery"
              class="search-input"
              placeholder="搜索标题、作者、摘要或关键词..."
            >
          </div>
          
          <!-- 模块筛选 -->
          <div class="module-filter">
            <label for="history-module-filter" class="filter-label">模块筛选：</label>
            <select 
              id="history-module-filter" 
              v-model="selectedModule"
              class="filter-select"
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
          
          <!-- 稿件状态筛选 -->
          <div class="status-filter">
            <label for="status-filter" class="filter-label">稿件状态：</label>
            <select 
              id="status-filter" 
              v-model="selectedStatus"
              class="filter-select"
            >
              <option value="all">全部状态</option>
              <option value="已通过">已通过</option>
              <option value="未通过">未通过</option>
              <option value="复审">复审</option>
              <option value="终审">终审</option>
            </select>
          </div>
          
          <!-- 时间范围筛选 -->
          <div class="time-range-filter">
            <label for="history-time-range-filter" class="filter-label">时间范围：</label>
            <select 
              id="history-time-range-filter" 
              v-model="timeRange"
              class="filter-select"
            >
              <option value="all">全部时间</option>
              <option value="today">今日</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="year">本年</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 审核历史列表 -->
      <section class="journals-section">
        <div class="journals-list">
          <div 
            v-for="journal in paginatedHistory" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">
                作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 
                审核日期：{{ journal.reviewDate }} | 
                <span class="review-result" :class="(journal.reviewResult || journal.status).toLowerCase()">
                  {{ journal.reviewResult || journal.status }}
                </span>
              </p>
              <p class="journal-abstract">{{ journal.abstract }}</p>
              
              <!-- 显示审稿建议 -->
              <div class="history-comment-section">
                <h4 class="comment-section-title">审稿建议：</h4>
                <div class="history-comment">
                  <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
                    <div v-for="(record, index) in journal.reviewHistory" :key="index" class="stage-comment">
                      <div class="stage-header">
                        <span class="stage-name">{{ record.stage }}：</span>
                        <span class="stage-status" :class="record.status.toLowerCase()">{{ record.status }}</span>
                        <span class="stage-reviewer">（{{ record.reviewer }}）</span>
                        <span class="stage-date">{{ record.date }}</span>
                      </div>
                      <div class="stage-content">{{ record.comment }}</div>
                    </div>
                  </div>
                  <div v-else>
                    无审稿建议
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="allHistory.length === 0" class="no-journals">
            <p>当前没有审核历史记录</p>
          </div>
        </div>
      </section>

      <!-- 分页控件 -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" @click="goToFirstPage" :disabled="currentPage === 1">
          首页
        </button>
        <button class="page-btn" @click="goToPrevPage" :disabled="currentPage === 1">
          上一页
        </button>
        
        <button 
          v-for="page in pageRange" 
          :key="page"
          class="page-btn" 
          :class="{ active: currentPage === page }"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
        
        <button class="page-btn" @click="goToNextPage" :disabled="currentPage === totalPages">
          下一页
        </button>
        <button class="page-btn" @click="goToLastPage" :disabled="currentPage === totalPages">
          末页
        </button>
        
        <div class="pagination-info">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ allHistory.length }} 篇历史记录
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.reviewer-history-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 主内容 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

/* 页面头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.review-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  background: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 筛选控件样式 */
.filter-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.filters-container {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.search-filter, 
.module-filter,
.status-filter,
.time-range-filter {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
  white-space: nowrap;
}

.search-input {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.3s ease;
  min-width: 200px;
}

.search-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.filter-select {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.3s ease;
  min-width: 150px;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 稿件列表 */
.journals-section {
  margin-bottom: 2rem;
}

.journals-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s ease;
}

.journal-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.journal-meta {
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
}

.journal-abstract {
  color: #555;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 审核结果状态 */
.review-result {
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.review-result.已通过 {
  background: #d4edda;
  color: #155724;
}

.review-result.已拒绝,
.review-result.未通过 {
  background: #f8d7da;
  color: #721c24;
}

/* 历史记录中的审稿建议 */
.history-comment-section {
  margin-top: 1rem;
  padding: 1rem;
  background: #e8f4f8;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.comment-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.history-comment {
  color: #555;
  line-height: 1.6;
}

.stage-comment {
  margin-bottom: 1rem;
  padding: 0.8rem;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #3498db;
}

.stage-comment:last-child {
  margin-bottom: 0;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stage-name {
  color: #2c3e50;
}

.stage-status {
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.stage-status.通过 {
  background: #d4edda;
  color: #155724;
}

.stage-status.未通过 {
  background: #f8d7da;
  color: #721c24;
}

.stage-reviewer {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.stage-date {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-left: auto;
}

.stage-content {
  color: #555;
  line-height: 1.5;
  font-size: 0.95rem;
  white-space: pre-wrap;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.page-btn {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #3498db;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.page-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  margin-left: 1rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* 无稿件提示 */
.no-journals {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 10px;
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
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .filters-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-filter, 
  .module-filter,
  .status-filter,
  .time-range-filter {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .search-input,
  .filter-select {
    width: 100%;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>