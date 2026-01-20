<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navigation from './Navigation.vue'
import { stripHtmlTags, truncateText } from '../utils/helpers.js'

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
          <button class="btn btn-back" @click="navigateTo('review')">返回审稿页面</button>
          <h2 class="review-title">所有历史审稿记录</h2>
        </div>
        <div class="review-stats">
          <span class="stat-item">历史记录总数：{{ allHistory.length }}</span>
        </div>
      </div>

      <!-- 历史记录筛选控件 -->
      <div class="filter-section">
        <div class="history-filters">
          <!-- 搜索输入框 -->
          <div class="search-filter">
            <label for="all-history-search-input" class="filter-label">搜索：</label>
            <input 
              type="text" 
              id="all-history-search-input" 
              v-model="searchQuery"
              class="search-input"
              placeholder="搜索标题、作者、摘要或关键词..."
            >
          </div>
          
          <!-- 模块筛选 -->
          <label for="history-module-filter">模块筛选：</label>
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
          
          <!-- 稿件状态筛选 -->
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
          
          <!-- 时间范围筛选 -->
          <label for="time-range-filter" class="filter-label">时间范围：</label>
          <select 
            id="time-range-filter" 
            v-model="timeRange"
            class="filter-select"
          >
            <option value="all">总共</option>
            <option value="today">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="year">本年</option>
          </select>
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
                作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 
                审核日期：{{ journal.reviewDate }} | 
                <span class="review-result" :class="(journal.reviewResult || journal.status).toLowerCase()">
                  {{ journal.reviewResult || journal.status }}
                </span>
              </p>
              <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
              
              <!-- 显示审稿建议 -->
            <div class="history-comment-section">
              <h4 class="comment-section-title">审稿建议：</h4>
              <div class="history-comment">
                <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
                  <div v-for="(record, index) in journal.reviewHistory" :key="index" class="stage-comment">
                    <div class="stage-header">
                      <span class="stage-name">{{ record.stage }}：</span>
                      <span class="stage-status" :class="record.status.toLowerCase()">{{ record.status }}</span>
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

          <!-- 无历史记录提示 -->
          <div v-if="allHistory.length === 0" class="no-journals">
            <p>当前没有匹配的审稿记录</p>
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 0" class="pagination">
          <div class="pagination-info">
            共 {{ allHistory.length }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
          </div>
          <div class="pagination-controls">
            <button 
              class="page-btn" 
              :disabled="currentPage === 1"
              @click="goToPrevPage"
            >
              上一页
            </button>
            <button 
              class="page-btn" 
              :disabled="currentPage === totalPages"
              @click="goToNextPage"
            >
              下一页
            </button>
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

/* 历史记录筛选控件 */
.filter-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.history-filters {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.history-filters label {
  font-weight: 500;
  color: #555;
  font-size: 0.85rem;
  white-space: nowrap;
}

.history-filters .filter-select,
.history-filters input[type="date"] {
  padding: 0.45rem 0.7rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.3s ease;
  min-width: 100px;
}

.history-filters .filter-select:focus,
.history-filters input[type="date"]:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.filter-label {
  font-weight: 500;
  color: #555;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-clear {
  background: #95a5a6;
  color: white;
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
}

/* 历史记录列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
  transition: all 0.3s ease;
}

.history-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.3rem;
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
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
}

.journal-abstract {
  color: #555;
  line-height: 1.6;
  margin: 0;
  font-size: 0.85rem;
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
}

.review-result.已通过 {
  background: #d4edda;
  color: #155724;
}

.review-result.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

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
  white-space: pre-wrap; /* 保留换行和空格 */
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
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
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
</style>