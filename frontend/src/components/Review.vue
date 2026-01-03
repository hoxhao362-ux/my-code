<script setup>
import { ref, computed } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'journals', 'modules', 'updateJournals', 'toggleDirectory', 'logout'])

// 日期查询
const selectedDate = ref('')
// 时间范围筛选
const timeRange = ref('all') // 'all', 'today', 'week', 'month', 'year'
// 模块筛选
const selectedModule = ref('all')
// 当前激活的标签页
const activeTab = ref('pending')

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

// 待审稿件（从真实期刊数据中筛选）
const pendingJournals = computed(() => {
  let journals = props.journals.filter(journal => journal.status === '待审核' || journal.status === '审稿中')
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
  }
  
  // 时间范围筛选
  journals = filterByTimeRange(journals)
  
  return journals
})

// 历史审稿记录（从真实期刊数据中筛选）
const reviewHistory = computed(() => {
  let journals = props.journals.filter(journal => journal.status === '已通过' || journal.status === '未通过')
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
  }
  
  // 时间范围筛选
  journals = filterByTimeRange(journals)
  
  return journals
})

const goBack = () => {
  props.navigateTo('home')
}

const handleReview = (id, action) => {
  // 找到要审核的期刊
  const journalIndex = props.journals.findIndex(j => j.id === id)
  if (journalIndex !== -1) {
    const journal = {...props.journals[journalIndex]}
    const newStatus = action === 'approve' ? '已通过' : '未通过'
    
    // 更新期刊状态和审核信息
    journal.status = newStatus
    journal.reviewResult = newStatus
    journal.reviewDate = new Date().toISOString().split('T')[0]
    
    // 更新原始期刊数组
    const updatedJournals = [...props.journals]
    updatedJournals[journalIndex] = journal
    props.updateJournals(updatedJournals)
    
    // 显示审核结果
    alert(`已${newStatus}稿件：${journal.title}`)
  }
}

const viewJournalDetail = (id) => {
  // 跳转到稿件详情页
  props.navigateTo('journal', id)
}

// 过滤后的历史记录
const filteredHistory = computed(() => {
  // 先获取所有历史记录，不进行时间范围筛选，只进行模块和日期筛选
  let journals = props.journals.filter(journal => journal.status === '已通过' || journal.status === '未通过')
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
  }
  
  // 日期筛选
  if (selectedDate.value) {
    journals = journals.filter(item => {
      // 确保日期格式匹配
      const itemDate = new Date(item.date).toISOString().split('T')[0]
      return itemDate === selectedDate.value
    })
  }
  
  return journals
})
</script>

<template>
  <div class="review-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('home')">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">投稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 审稿内容 -->
    <main class="review-content">
      <div class="review-header">
        <h2 class="review-title">审稿管理</h2>
        <div class="review-stats">
          <span class="stat-item">待审稿件：{{ pendingJournals.length }}</span>
        </div>
      </div>

      <!-- 标签切换 -->
      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          待审稿件
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          历史记录
        </button>
      </div>
      
      <!-- 待审稿件筛选控件 -->
      <div v-if="activeTab === 'pending'" class="filter-section">
        <div class="filters-container">
          <div class="module-filter">
            <label for="module-filter" class="filter-label">模块筛选：</label>
            <select 
              id="module-filter" 
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
          
          <div class="time-range-filter">
            <label for="time-range-filter" class="filter-label">时间范围：</label>
            <select 
              id="time-range-filter" 
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

      <!-- 待审稿件列表 -->
      <div v-if="activeTab === 'pending'" class="journals-list">
        <div 
          v-for="journal in pendingJournals" 
          :key="journal.id" 
          class="journal-item"
        >
          <div class="journal-info">
            <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h3>
            <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            <p class="journal-abstract">{{ journal.abstract }}</p>
          </div>
          
          <!-- 审稿建议文本框 -->
          <div class="review-comment-section">
            <label for="comment-{{ journal.id }}" class="comment-label">审稿建议：</label>
            <textarea 
              id="comment-{{ journal.id }}" 
              v-model="journal.reviewComment"
              class="review-comment"
              placeholder="请输入审稿建议..."
              rows="4"
            ></textarea>
          </div>
          
          <div class="journal-actions">
            <div class="journal-status">{{ journal.status }}</div>
            <div class="action-buttons">
              <button class="btn btn-approve" @click="handleReview(journal.id, 'approve')">通过</button>
              <button class="btn btn-reject" @click="handleReview(journal.id, 'reject')">拒绝</button>
            </div>
          </div>
        </div>

        <!-- 无稿件提示 -->
        <div v-if="pendingJournals.length === 0" class="no-journals">
          <p>当前没有待审核的稿件</p>
        </div>
      </div>

      <!-- 历史记录 -->
      <div v-else class="history-section">
        <!-- 历史记录筛选 -->
        <div class="history-header">
          <h3 class="history-title">历史审稿记录</h3>
          <div class="history-filters">
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
            
            <!-- 日期查询 -->
            <label for="date-select">按日期查询：</label>
            <input 
              type="date" 
              id="date-select" 
              v-model="selectedDate"
              :max="new Date().toISOString().split('T')[0]"
            >
            <button class="btn btn-clear" @click="selectedDate = ''">清除</button>
          </div>
        </div>

        <!-- 历史记录列表 -->
        <div class="history-list">
          <div 
            v-for="journal in filteredHistory" 
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
              <p class="journal-abstract">{{ journal.abstract }}</p>
              
              <!-- 显示审稿建议 -->
              <div class="history-comment-section">
                <h4 class="comment-section-title">审稿建议：</h4>
                <div class="history-comment">
                  {{ journal.reviewComment || '无审稿建议' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 无历史记录提示 -->
        <div v-if="filteredHistory.length === 0" class="no-journals">
          <p>当前没有匹配的审稿记录</p>
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

/* 导航栏样式（与其他页面保持一致） */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #3498db;
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
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

/* 稿件列表 */
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
  font-size: 0.95rem;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.review-comment-section {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.comment-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.review-comment {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 100px;
  outline: none;
  transition: border-color 0.3s ease;
}

.review-comment:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.journal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.journal-status {
  font-weight: 600;
  color: #f39c12;
  font-size: 0.95rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-approve {
  background: #2ecc71;
  color: white;
}

.btn-approve:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

.btn-reject {
  background: #e74c3c;
  color: white;
}

.btn-reject:hover {
  background: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
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

/* 标签切换 */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: white;
  padding: 0.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 0.8rem 1.5rem;
  border: none;
  background: white;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #7f8c8d;
}

.tab-btn:hover {
  color: #3498db;
  background: #ecf0f1;
}

.tab-btn.active {
  background: #3498db;
  color: white;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
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

.module-filter,
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

/* 历史记录部分 */
.history-section {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.history-header {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.history-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
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

.history-filters .btn-clear {
  margin-left: 0.5rem;
}

.btn-clear {
  background: #95a5a6;
  color: white;
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
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
</style>