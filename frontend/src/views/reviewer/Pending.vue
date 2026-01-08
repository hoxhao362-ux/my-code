<script setup>
import { computed, ref } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 筛选相关状态
const searchQuery = ref('') // 搜索关键词
const selectedModule = ref('all') // 模块筛选
const timeRange = ref('all') // 时间范围筛选：'all', 'today', 'week', 'month', 'year'

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

// 待审核的稿件列表 - 仅显示复审阶段的稿件，并应用筛选条件
const pendingJournals = computed(() => {
  // 基础筛选：只显示审稿中且处于复审阶段的稿件
  let journals = userStore.journals.filter(journal => 
    journal.status === '审稿中' && journal.reviewStage === '复审'
  )
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    journals = journals.filter(journal => journal.module === selectedModule.value)
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

// 处理审稿
const handleReview = (id, action) => {
  // 找到要审核的期刊
  const journalIndex = userStore.journals.findIndex(j => j.id === id)
  if (journalIndex !== -1) {
    const journal = {...userStore.journals[journalIndex]}
    let updateMessage = ''
    const today = new Date().toISOString().split('T')[0]
    
    // 确保reviewHistory数组存在
    if (!journal.reviewHistory) {
      journal.reviewHistory = []
    }
    
    // 获取当前阶段的审核评论
    const currentStageComment = journal[`${journal.reviewStage.toLowerCase()}Comment`] || ''
    
    // 审核员处理复审
    if (journal.reviewStage === '复审') {
      if (action === 'approve') {
        // 复审通过，进入终审阶段
        journal.reviewStage = '终审'
        journal.status = '审稿中'
        updateMessage = `已通过复审，进入终审阶段：${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: '复审',
          status: '通过',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || '复审通过，进入终审阶段',
          type: '完全保密'
        })
        
        // 清空复审评论，为终审阶段准备
        delete journal.fuShenComment
      } else {
        // 复审拒绝，直接未通过
        journal.status = '未通过'
        journal.reviewResult = '未通过'
        journal.reviewDate = today
        updateMessage = `已拒绝复审：${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: '复审',
          status: '未通过',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || '复审未通过',
          type: '完全保密'
        })
        
        // 清空复审评论
        delete journal.fuShenComment
      }
      
      // 更新期刊
      userStore.updateJournal(journal)
      
      // 显示审核结果
      alert(updateMessage)
    } else {
      alert('您没有权限处理此稿件或此稿件不在您负责的审稿阶段')
      return
    }
  }
}
</script>

<template>
  <div class="reviewer-pending-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'reviewer-pending'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 待审核稿件内容 -->
    <main class="content">
      <div class="header">
        <h1>待审核稿件</h1>
        <div class="review-stats">
          <span class="stat-item">待复审稿件总数：{{ pendingJournals.length }}</span>
        </div>
      </div>

      <!-- 筛选控件 -->
      <div class="filter-section">
        <div class="filters-container">
          <!-- 搜索输入框 -->
          <div class="search-filter">
            <label for="pending-search-input" class="filter-label">搜索：</label>
            <input 
              type="text" 
              id="pending-search-input" 
              v-model="searchQuery"
              class="search-input"
              placeholder="搜索标题、作者、摘要或关键词..."
            >
          </div>
          
          <!-- 模块筛选 -->
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
          
          <!-- 时间范围筛选 -->
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

      <!-- 待审核稿件列表 -->
      <section class="journals-section">
        <div class="journals-list">
          <div 
            v-for="journal in pendingJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
              <p class="journal-abstract">{{ journal.abstract }}</p>
            </div>
            
            <!-- 审稿建议文本框 -->
            <div class="review-comment-section">
              <label :for="'comment-' + journal.id" class="comment-label">审稿建议：</label>
              <textarea 
                :id="'comment-' + journal.id" 
                v-model="journal[`${journal.reviewStage.toLowerCase()}Comment`]"
                class="review-comment"
                placeholder="请输入审稿建议..."
                rows="4"
              ></textarea>
            </div>
            
            <div class="journal-actions">
              <div class="journal-status">
                {{ journal.status }} - {{ journal.reviewStage }}
              </div>
              <div class="action-buttons">
                <button class="btn btn-approve" @click="handleReview(journal.id, 'approve')">通过</button>
                <button class="btn btn-reject" @click="handleReview(journal.id, 'reject')">拒绝</button>
              </div>
            </div>
          </div>
          <div v-if="pendingJournals.length === 0" class="no-journals">
            <p>当前没有待审核的稿件</p>
          </div>
        </div>
      </section>
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
.reviewer-pending-container {
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
  margin: 0;
  font-size: 0.95rem;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 审稿建议 */
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

/* 操作按钮 */
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
  
  .journal-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-buttons {
    align-self: flex-end;
  }
}
</style>