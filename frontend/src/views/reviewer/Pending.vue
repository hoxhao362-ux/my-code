<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { stripHtmlTags, truncateText } from '../../utils/helpers.js'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'
import Navigation from '../../components/Navigation.vue'
import ReviewForm from '../../components/ReviewForm.vue'
import { reviewApi } from '../../utils/api'

const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

const showReviewModal = ref(false)
const currentReviewJournal = ref(null)

const openReviewModal = (journal) => {
  currentReviewJournal.value = journal
  showReviewModal.value = true
}

const handleReviewSubmit = async ({ ratings, comments, confidentialComments, decision }) => {
  if (!currentReviewJournal.value) return

  const journal = currentReviewJournal.value
  
  const reviewData = {
    decision: decision,
    ratings: ratings,
    comments_to_author: comments,
    confidential_comments: confidentialComments
  }

  try {
    await reviewApi.reviewJournal(journal.id, reviewData)
    
    toastStore.add({ message: '审稿意见已提交', type: 'success' })
    
    showReviewModal.value = false
    currentReviewJournal.value = null
    
    fetchPendingJournals()
  } catch (error) {
    toastStore.add({ message: '提交审稿失败：' + error.message, type: 'error' })
    console.error('提交审稿失败:', error)
  }
}

// 筛选相关状态
const searchQuery = ref('') // 搜索关键词
const selectedModule = ref('all') // 模块筛选
const timeRange = ref('all') // 时间范围筛选：'all', 'today', 'week', 'month', 'year'

// 分页相关状态
const currentPage = ref(1) // 当前页码
const pageSize = ref(10) // 每页显示数量

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(pendingJournalsFiltered.value.length / pageSize.value)
})

// 过滤后的待审核稿件列表
const pendingJournalsFiltered = computed(() => {
  // 基础筛选：只显示待审核或审稿中且处于审核阶段的稿件
  // 管理员看到初审和终审阶段的稿件，审核员只看到复审阶段的稿件
  let journals = userStore.journals.filter(journal => {
    const isAdmin = user.value?.role === 'admin';
    const allowedStages = isAdmin 
      ? ['Initial Review', 'Final Decision', '初审', '终审'] 
      : ['Peer Review', '复审'];
    // 包含所有待审核状态
    const isPendingStatus = [
      MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
      MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
      MANUSCRIPT_STATUS.PENDING_PEER_REVIEW,
      MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
      '待审核', '审稿中', '待初审', '待复审', '待终审'
    ].includes(journal.status);
    return isPendingStatus && allowedStages.some(stage => 
      journal.reviewStage === stage || 
      (stage === 'Initial Review' && journal.reviewStage === '初审') ||
      (stage === 'Peer Review' && journal.reviewStage === '复审') ||
      (stage === 'Final Decision' && journal.reviewStage === '终审')
    );
  })
  
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

// 分页后的待审核稿件列表
const pendingJournals = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return pendingJournalsFiltered.value.slice(startIndex, endIndex)
})

// 获取所有可用模块
const modules = computed(() => userStore.modules)

// 监听所有筛选条件变化，重置页码为1
watch([searchQuery, selectedModule, timeRange], () => {
  currentPage.value = 1
}, { deep: true })

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



// 查看稿件详情
const viewJournalDetail = (id) => {
  router.push(`/admin/journal/${id}`)
}

// 分页控制函数
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const goToFirstPage = () => {
  currentPage.value = 1
}

const goToLastPage = () => {
  currentPage.value = totalPages.value
}

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// 处理审稿
const handleReview = (id, action) => {
  // 找到要审核的期刊，使用String转换确保类型匹配
  const journalIndex = userStore.journals.findIndex(j => String(j.id) === String(id))
  if (journalIndex !== -1) {
    const journal = {...userStore.journals[journalIndex]}
    let updateMessage = ''
    const today = new Date().toISOString().split('T')[0]
    
    // 权限检查：管理员不能处理复审阶段的稿件，审核员只能处理复审阶段的稿件
    const isAdmin = user.value?.role === 'admin';
    const isReviewer = user.value?.role === 'reviewer';
    
    if (isAdmin && (journal.reviewStage === 'Peer Review' || journal.reviewStage === '复审')) {
      toastStore.add({ message: 'Admin cannot process Peer Review stage manuscripts!', type: 'warning' })
      return;
    }
    
    if (isReviewer && journal.reviewStage !== 'Peer Review' && journal.reviewStage !== '复审') {
      toastStore.add({ message: 'Reviewer can only process Peer Review stage manuscripts!', type: 'warning' })
      return;
    }
    
    // 确保reviewHistory数组存在
    if (!journal.reviewHistory) {
      journal.reviewHistory = []
    }
    
    // 获取当前阶段的审核评论
    const currentStageComment = journal[`${journal.reviewStage.toLowerCase()}Comment`] || ''
    
    // 根据当前审核阶段处理
    if (journal.reviewStage === 'Initial Review' || journal.reviewStage === '初审') {
      if (action === 'approve') {
        // 初审通过，进入复审阶段
        journal.reviewStage = 'Peer Review'
        journal.status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
        updateMessage = `Initial review approved, proceeding to peer review: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Initial Review',
          status: 'Approved',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Initial review approved, proceeding to peer review',
          type: 'Confidential'
        })
        
        // 清空初审评论，为复审阶段准备
        delete journal.chuShenComment
      } else {
        // 初审拒绝，直接未通过
        journal.status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
        journal.reviewResult = 'Rejected'
        journal.reviewDate = today
        updateMessage = `Initial review rejected: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Initial Review',
          status: 'Rejected',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Initial review rejected',
          type: 'Confidential'
        })
        
        // 清空初审评论
        delete journal.chuShenComment
      }
    } else if (journal.reviewStage === 'Peer Review' || journal.reviewStage === '复审') {
      if (action === 'approve') {
        // 复审通过，进入终审阶段
        journal.reviewStage = 'Final Decision'
        journal.status = MANUSCRIPT_STATUS.PENDING_FINAL_DECISION
        updateMessage = `Peer review approved, proceeding to final decision: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Peer Review',
          status: 'Approved',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Peer review approved, proceeding to final decision',
          type: 'Confidential'
        })
        
        // 清空复审评论，为终审阶段准备
        delete journal.fuShenComment
      } else {
        // 复审拒绝，直接未通过
        journal.status = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
        journal.reviewResult = 'Rejected'
        journal.reviewDate = today
        updateMessage = `Peer review rejected: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Peer Review',
          status: 'Rejected',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Peer review rejected',
          type: 'Confidential'
        })
        
        // 清空复审评论
        delete journal.fuShenComment
      }
    } else if (journal.reviewStage === 'Final Decision' || journal.reviewStage === '终审') {
      if (action === 'approve') {
        // 终审通过，审核完成
        journal.status = MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
        journal.reviewResult = 'Accepted'
        journal.reviewDate = today
        updateMessage = `Final decision approved, manuscript accepted: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Final Decision',
          status: 'Accepted',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Final decision approved, manuscript accepted',
          type: 'Confidential'
        })
        
        // 清空终审评论
        delete journal.zhongShenComment
      } else {
        // 终审拒绝，直接未通过
        journal.status = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
        journal.reviewResult = 'Rejected'
        journal.reviewDate = today
        updateMessage = `Final decision rejected: ${journal.title}`
        
        // 添加审核记录
        journal.reviewHistory.push({
          stage: 'Final Decision',
          status: 'Rejected',
          reviewer: user.value.username,
          date: today,
          comment: currentStageComment || 'Final decision rejected',
          type: 'Confidential'
        })
        
        // 清空终审评论
        delete journal.zhongShenComment
      }
    }
    
    userStore.updateJournal(journal)
    
    toastStore.add({ message: updateMessage, type: 'success' })
    
    if (journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED) {
      const authorIndex = userStore.users.findIndex(u => u.username === journal.author);
      if (authorIndex !== -1) {
        const authorUser = userStore.users[authorIndex];
        if (authorUser.role === 'user') {
          const updatedAuthorUser = {
            ...authorUser,
            role: 'author'
          };
          
          userStore.users[authorIndex] = updatedAuthorUser;
          localStorage.setItem('users', JSON.stringify(userStore.users));
          
          if (userStore.user && userStore.user.username === journal.author) {
            userStore.updateUser({ role: 'author' });
          }
          
          toastStore.add({ message: `Author ${journal.author} has been automatically upgraded to author role!`, type: 'success' })
        }
      }
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
        <h1>审核任务</h1>
        <div class="review-stats">
          <span class="stat-item">待审核稿件总数：{{ pendingJournals.length }}</span>
          <span v-if="user?.role === 'admin'" class="stat-item">待初审审核：{{ pendingJournals.filter(j => j.reviewStage === '初审').length }}</span>
          <span v-if="user?.role !== 'admin'" class="stat-item">待复审：{{ pendingJournals.filter(j => j.reviewStage === '复审').length }}</span>
          <span v-if="user?.role === 'admin'" class="stat-item">待终审审核：{{ pendingJournals.filter(j => j.reviewStage === '终审').length }}</span>
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
              <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }} <span class="view-detail-icon">📋</span></h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
              <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
            </div>
            
            <div class="journal-actions">
              <div class="journal-status">
                {{ journal.status }} - {{ journal.reviewStage }}
              </div>
              <div class="action-buttons">
                <button class="btn btn-primary" @click="openReviewModal(journal)">Start Review / 审稿</button>
              </div>
            </div>
          </div>
          <div v-if="pendingJournals.length === 0" class="no-journals">
            <p>当前没有待审核的稿件</p>
          </div>
        </div>
        
        <!-- 分页控件 -->
        <div v-if="totalPages > 1" class="pagination-section">
          <div class="pagination-info">
            <span>共 {{ pendingJournalsFiltered.length }} 条记录，第 {{ currentPage }}/{{ totalPages }} 页</span>
          </div>
          <div class="pagination-controls">
            <button 
              class="pagination-btn" 
              @click="goToFirstPage" 
              :disabled="currentPage === 1"
            >
              首页
            </button>
            <button 
              class="pagination-btn" 
              @click="goToPreviousPage" 
              :disabled="currentPage === 1"
            >
              上一页
            </button>
            
            <!-- 页码按钮 -->
            <div class="page-numbers">
              <button 
                v-for="page in totalPages" 
                :key="page"
                class="page-btn"
                :class="{ active: page === currentPage }"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
            </div>
            
            <button 
              class="pagination-btn" 
              @click="goToNextPage" 
              :disabled="currentPage === totalPages"
            >
              下一页
            </button>
            <button 
              class="pagination-btn" 
              @click="goToLastPage" 
              :disabled="currentPage === totalPages"
            >
              末页
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- Review Modal -->
    <div v-if="showReviewModal" class="modal-overlay">
      <div class="modal-content">
        <!-- Close Button -->
        <div class="modal-header">
          <button class="modal-close-btn" @click="showReviewModal = false">
            &times;
          </button>
        </div>
        <ReviewForm 
          :journal="currentReviewJournal" 
          @submit="handleReviewSubmit" 
          @cancel="showReviewModal = false" 
        />
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
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
  color: #3498db;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #2980b9;
  text-decoration: underline;
}

.view-detail-icon {
  font-size: 1rem;
  margin-left: 0.5rem;
  color: #7f8c8d;
  transition: transform 0.3s ease;
}

.journal-title:hover .view-detail-icon {
  transform: scale(1.2);
  color: #2980b9;
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

/* 分页控件样式 */
.pagination-section {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.pagination-info {
  font-size: 0.95rem;
  color: #666;
  font-weight: 500;
  background: #f8f9fa;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: #f8f9fa;
  padding: 0.4rem;
  border-radius: 25px;
}

.pagination-btn {
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 20px;
  background: transparent;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.pagination-btn:hover:not(:disabled) {
  background: #3498db;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.3rem;
}

.page-btn {
  padding: 0.7rem 1.1rem;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(.active) {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.page-btn.active {
  background: #3498db;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  transform: scale(1.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination-section {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.2rem;
  }
  
  .pagination-btn {
    padding: 0.6rem 0.9rem;
    font-size: 0.85rem;
    min-width: 70px;
  }
  
  .page-btn {
    padding: 0.6rem;
    font-size: 0.85rem;
    min-width: 35px;
    height: 35px;
  }
  
  .pagination-info {
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
    text-align: center;
  }
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 8px;
  background: white;
  width: 900px;
  max-width: 95vw;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

/* Modal Header and Close Button */
.modal-header {
  position: relative;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-close-btn {
  position: absolute;
  top: 0.5rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #999;
  transition: color 0.3s ease;
  padding: 0.25rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  color: #333;
  background: #f5f5f5;
}

.modal-content {
  position: relative;
}
</style>