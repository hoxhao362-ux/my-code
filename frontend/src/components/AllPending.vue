<script setup>
import { ref, computed, onMounted } from 'vue'
import Navigation from './Navigation.vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'journals', 'modules', 'updateJournals', 'toggleDirectory', 'logout'])

// 日期查询
const selectedDate = ref('')
// 时间范围筛选
const timeRange = ref('all') // 'all', 'today', 'week', 'month', 'year'
// 模块筛选
const selectedModule = ref('all')
// 阶段筛选（仅管理员）
const selectedStage = ref('all') // 'all', '初审', '终审'
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

// 待审稿件（从真实期刊数据中筛选，根据角色显示对应阶段）
const pendingJournals = computed(() => {
  // 基础筛选：只显示审稿中的稿件
  let journals = props.journals.filter(journal => journal.status === '审稿中')
  
  // 角色筛选：根据用户角色显示对应阶段的稿件
  if (props.user.role === 'admin') {
    // 管理员可以看到需要初审和终审的稿件
    journals = journals.filter(journal => 
      journal.reviewStage === '初审' || journal.reviewStage === '终审'
    )
    
    // 管理员专属：阶段筛选
    if (selectedStage.value !== 'all') {
      journals = journals.filter(journal => journal.reviewStage === selectedStage.value)
    }
  } else if (props.user.role === 'reviewer') {
    // 审核员只能看到需要复审的稿件
    journals = journals.filter(journal => journal.reviewStage === '复审')
  }
  
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

// 总页数
const totalPages = computed(() => {
  return Math.ceil(pendingJournals.value.length / pageSize.value)
})

// 当前页显示的稿件
const paginatedJournals = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return pendingJournals.value.slice(startIndex, endIndex)
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

// 处理审稿
const handleReview = (id, action) => {
  // 找到要审核的期刊
  const journalIndex = props.journals.findIndex(j => j.id === id)
  if (journalIndex !== -1) {
    const journal = {...props.journals[journalIndex]}
    let updateMessage = ''
    const today = new Date().toISOString().split('T')[0]
    
    // 确保reviewHistory数组存在
    if (!journal.reviewHistory) {
      journal.reviewHistory = []
    }
    
    // 获取当前阶段的审核评论
    const currentStageComment = journal[`${journal.reviewStage.toLowerCase()}Comment`] || ''
    
    // 三阶段审稿流程处理
    if (journal.reviewStage === '初审' && props.user.role === 'admin') {
      // 管理员处理初审
      if (action === 'approve') {
        // 初审通过，进入复审阶段
        journal.reviewStage = '复审'
        journal.status = '审稿中'
        updateMessage = `已通过初审，进入复审阶段：${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: '初审',
          status: '通过',
          reviewer: props.user.username,
          date: today,
          comment: currentStageComment || '初审通过，进入复审阶段',
          type: '完全保密'
        })
        
        // 清空初审评论，为复审阶段准备
        delete journal.chuShenComment
      } else {
        // 初审拒绝，直接未通过
        journal.status = '未通过'
        journal.reviewResult = '未通过'
        journal.reviewDate = today
        updateMessage = `已拒绝初审：${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: '初审',
          status: '未通过',
          reviewer: props.user.username,
          date: today,
          comment: currentStageComment || '初审未通过',
          type: '完全保密'
        })
        
        // 清空初审评论
        delete journal.chuShenComment
      }
    } else if (journal.reviewStage === '复审' && props.user.role === 'reviewer') {
      // 审核员处理复审
      if (action === 'approve') {
        // 复审通过，进入终审阶段
        journal.reviewStage = '终审'
        journal.status = '审稿中'
        updateMessage = `已通过复审，进入终审阶段：${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: '复审',
          status: '通过',
          reviewer: props.user.username,
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
          reviewer: props.user.username,
          date: today,
          comment: currentStageComment || '复审未通过',
          type: '完全保密'
        })
        
        // 清空复审评论
        delete journal.fuShenComment
      }
    } else if (journal.reviewStage === '终审' && props.user.role === 'admin') {
      // 管理员处理终审
      journal.status = action === 'approve' ? '已通过' : '未通过'
      journal.reviewResult = journal.status
      journal.reviewDate = today
      updateMessage = `已${journal.status}终审：${journal.title}`
      
      // 添加审核记录
      journal.reviewHistory.push({
        stage: '终审',
        status: journal.status === '已通过' ? '通过' : '未通过',
        reviewer: props.user.username,
        date: today,
        comment: currentStageComment || `${journal.status}终审`,
        type: '完全保密'
      })
      
      // 清空终审评论
      delete journal.zhongShenComment
    } else {
      alert('您没有权限处理此稿件或此稿件不在您负责的审稿阶段')
      return
    }
    
    // 更新原始期刊数组
    const updatedJournals = [...props.journals]
    updatedJournals[journalIndex] = journal
    props.updateJournals(updatedJournals)
    
    // 显示审核结果
    alert(updateMessage)
  }
}
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
        <div style="display: flex; align-items: center; gap: 1rem;">
          <button class="btn btn-back" @click="navigateTo('review')">返回审稿页面</button>
          <h2 class="review-title">所有待审稿件</h2>
        </div>
        <div class="review-stats">
          <span class="stat-item">待审稿件总数：{{ pendingJournals.length }}</span>
        </div>
      </div>

      <!-- 待审稿件筛选控件 -->
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
          
          <!-- 管理员专属筛选：初审/终审 -->
          <div v-if="props.user.role === 'admin'" class="stage-filter">
            <label for="stage-filter" class="filter-label">筛选阶段：</label>
            <select 
              id="stage-filter" 
              v-model="selectedStage"
              class="filter-select"
            >
              <option value="all">全部阶段</option>
              <option value="初审">初审</option>
              <option value="终审">终审</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 待审稿件列表 -->
      <div class="journals-list">
          <div 
            v-for="journal in paginatedJournals" 
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

          <!-- 无稿件提示 -->
          <div v-if="pendingJournals.length === 0" class="no-journals">
            <p>当前没有待审核的稿件</p>
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 0" class="pagination">
          <div class="pagination-info">
            共 {{ pendingJournals.length }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
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

/* 返回按钮样式 */
.btn-back {
  background: #95a5a6;
  color: white;
}

.btn-back:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
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
.time-range-filter,
.stage-filter {
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