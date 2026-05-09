<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { stripHtmlTags } from '../utils/helpers'
import { useI18n } from '../composables/useI18n'

const router = useRouter()
const { t } = useI18n()

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 筛选相关状态
const searchKeyword = ref('')
const selectedModule = ref('all')
const selectedTimeRange = ref('all') // 时间筛选：all, day, week, month, year
const selectedSort = ref('newest') // 排序：newest（最新）, hottest（最热）

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const jumpPage = ref('')

// 从localStorage恢复页码
const restorePageState = () => {
  const savedPage = localStorage.getItem('directoryCurrentPage')
  if (savedPage) {
    currentPage.value = parseInt(savedPage, 10)
  }
}

// 保存页码到localStorage
const savePageState = () => {
  localStorage.setItem('directoryCurrentPage', currentPage.value.toString())
}

// 跳转到指定页码（通过输入框）
const jumpToPage = () => {
  const page = parseInt(jumpPage.value, 10)
  if (!isNaN(page) && page >= 1 && page <= totalPages.value) {
    goToPage(page)
  }
  jumpPage.value = ''
}

// 从userStore获取期刊数据
const journals = computed(() => userStore.journals)

// 筛选后的期刊列表
const filteredJournals = computed(() => {
  let result = [...journals.value]
  
  // 只展示通过的终稿或已发表的期刊
  result = result.filter(journal => 
    journal.status === '已通过' || journal.status === '已发表' || 
    journal.status === 'Accepted' || journal.status === 'Published'
  )
  
  // 按关键词筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(journal => 
      journal.title.toLowerCase().includes(keyword) ||
      journal.author.toLowerCase().includes(keyword) ||
      stripHtmlTags(journal.abstract).toLowerCase().includes(keyword) ||
      journal.keywords.some(k => k.toLowerCase().includes(keyword))
    )
  }
  
  // 按模块筛选
  if (selectedModule.value !== 'all') {
    result = result.filter(journal => journal.module === selectedModule.value)
  }
  
  // 按时间范围筛选
  if (selectedTimeRange.value !== 'all') {
    const now = new Date()
    let cutoffDate
    
    switch (selectedTimeRange.value) {
      case 'day':
        cutoffDate = new Date(now.getTime() - 24 * 60 * 60 * 1000)
        break
      case 'week':
        cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case 'year':
        cutoffDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
        break
      default:
        cutoffDate = new Date(0) // 1970-01-01
    }
    
    result = result.filter(journal => {
      const journalDate = new Date(journal.date)
      return journalDate >= cutoffDate
    })
  }
  
  // 排序
  if (selectedSort.value === 'hottest') {
    // 最热：按浏览量排序
    result.sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
  } else {
    // 最新：按日期排序
    result.sort((a, b) => new Date(b.date) - new Date(a.date))
  }
  
  return result
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredJournals.value.length / pageSize.value)
})

// 当前页显示的期刊列表
const currentPageJournals = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredJournals.value.slice(startIndex, endIndex)
})

// 切换到指定页码
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    savePageState()
  }
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    savePageState()
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    savePageState()
  }
}

// 页面加载时恢复页码
onMounted(() => {
  restorePageState()
})

// 获取所有模块
const modules = computed(() => {
  const moduleSet = new Set(['all'])
  journals.value.forEach(journal => moduleSet.add(journal.module))
  return Array.from(moduleSet)
})

// 查看期刊详情
const viewJournalDetail = (id) => {
  router.push(`/journal/${id}`)
}

const getLocalizedStatus = (status) => {
  const map = {
    '待审核': 'pending_initial_review',
    '审核中': 'under_peer_review',
    '已通过': 'final_decision_accepted',
    '已发表': 'published',
    '已拒绝': 'final_decision_rejected'
  }
  const key = map[status]
  if (key) return t(`status.${key}`)
  return t(`status.${status}`) || status
}
</script>

<template>
  <div class="directory-page">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'directory'"
      :logout="userStore.logout"
    />
    
    <!-- 主要内容 -->
    <main class="main-content">
      <section class="directory-section">
        <div class="directory-container">
          <h2 class="section-title">{{ t('directory.title') }}</h2>
          
          <!-- 筛选功能 -->
          <div class="filters-container">
            <!-- 关键词搜索 -->
            <div class="search-filter">
              <input
                type="text"
                id="search-input"
                name="search-input"
                v-model="searchKeyword"
                :placeholder="t('directory.searchPlaceholder')"
                class="search-input"
              />
            </div>
            
            <!-- 模块筛选 -->
            <div class="filter-group">
              <label for="module-filter">{{ t('directory.module') }}：</label>
              <select id="module-filter" v-model="selectedModule" class="filter-select">
                <option value="all">{{ t('directory.allModules') }}</option>
                <option v-for="module in modules" :key="module" :value="module">
                  {{ module }}
                </option>
              </select>
            </div>
            
            <!-- 时间筛选 -->
            <div class="filter-group">
              <label for="time-filter">{{ t('directory.timeRange') }}：</label>
              <select id="time-filter" v-model="selectedTimeRange" class="filter-select">
                <option value="all">{{ t('directory.allTime') }}</option>
                <option value="day">{{ t('directory.day') }}</option>
                <option value="week">{{ t('directory.week') }}</option>
                <option value="month">{{ t('directory.month') }}</option>
                <option value="year">{{ t('directory.year') }}</option>
              </select>
            </div>
            
            <!-- 排序筛选 -->
            <div class="filter-group">
              <label for="sort-filter">{{ t('directory.sort') }}：</label>
              <select id="sort-filter" v-model="selectedSort" class="filter-select">
                <option value="newest">{{ t('directory.newest') }}</option>
                <option value="hottest">{{ t('directory.hottest') }}</option>
              </select>
            </div>
          </div>
          
          <!-- 期刊目录列表 -->
          <div class="journals-directory">
            <div 
              v-for="journal in currentPageJournals" 
              :key="journal.id" 
              class="journal-directory-item"
            >
              <div class="journal-directory-info">
                <h3 class="journal-directory-title" @click="viewJournalDetail(journal.id)">
                  {{ journal.title }}
                </h3>
                <p class="journal-directory-meta">
                  {{ t('directory.author') }}：{{ journal.author }} | {{ t('directory.date') }}：{{ journal.date }}
                </p>
                <div class="journal-directory-abstract" v-html="journal.abstract"></div>
                <div class="journal-directory-keywords">
                  <span 
                    v-for="(keyword, index) in journal.keywords" 
                    :key="index" 
                    class="keyword-tag"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>
              <div class="journal-directory-status" :class="journal.status.toLowerCase()">
                {{ getLocalizedStatus(journal.status) }}
              </div>
            </div>
          </div>
          
          <!-- 无数据提示 -->
          <div v-if="filteredJournals.length === 0" class="no-journals">
            <p>{{ t('directory.noData') }}</p>
          </div>
          
          <!-- 分页组件 -->
          <div v-if="totalPages > 1" class="pagination-container">
            <div class="pagination-info">
              <span>{{ t('directory.pageInfo', { current: currentPage, total: totalPages, count: filteredJournals.length }) }}</span>
            </div>
            <div class="pagination-controls">
              <button 
                class="pagination-btn" 
                @click="prevPage"
                :disabled="currentPage === 1"
              >
                {{ t('directory.prevPage') }}
              </button>
              
              <!-- 页码按钮 -->
              <div class="page-numbers">
                <!-- 首页 -->
                <button 
                  class="page-btn" 
                  @click="goToPage(1)"
                  :class="{ active: currentPage === 1 }"
                >
                  1
                </button>
                
                <!-- 省略号 -->
                <span v-if="currentPage > 3" class="ellipsis">...</span>
                
                <!-- 当前页前后的页码 -->
                <button 
                  v-for="page in [currentPage - 2, currentPage - 1, currentPage, currentPage + 1, currentPage + 2]" 
                  :key="page"
                  class="page-btn"
                  @click="goToPage(page)"
                  :class="{ active: currentPage === page }"
                  v-if="page > 1 && page < totalPages"
                >
                  {{ page }}
                </button>
                
                <!-- 省略号 -->
                <span v-if="currentPage < totalPages - 2" class="ellipsis">...</span>
                
                <!-- 末页 -->
                <button 
                  v-if="totalPages > 1"
                  class="page-btn" 
                  @click="goToPage(totalPages)"
                  :class="{ active: currentPage === totalPages }"
                >
                  {{ totalPages }}
                </button>
              </div>
              
              <button 
                class="pagination-btn" 
                @click="nextPage"
                :disabled="currentPage === totalPages"
              >
                {{ t('directory.nextPage') }}
              </button>
              
              <!-- 页码输入框 -->
              <div class="page-jump-container">
                <span class="jump-text">{{ t('directory.jumpTo') }}</span>
                <input
                  type="number"
                  v-model="jumpPage"
                  class="page-input"
                  :placeholder="t('directory.page')"
                  min="1"
                  :max="totalPages"
                  @keyup.enter="jumpToPage"
                />
                <span class="jump-text">{{ t('directory.page') }}</span>
                <button class="jump-btn" @click="jumpToPage">
                  {{ t('directory.go') }}
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
.directory-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

/* 目录样式 */
.directory-section {
  margin-bottom: 2rem;
}

.directory-container {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

/* 筛选容器 */
.filters-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
}

/* 搜索输入框 */
.search-filter {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 筛选组 */
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

/* 筛选下拉框 */
.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
  background: white;
  min-width: 120px;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 期刊目录列表 */
.journals-directory {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 单条期刊目录项 */
.journal-directory-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
  align-items: flex-start;
}

.journal-directory-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

/* 期刊目录信息 */
.journal-directory-info {
  flex: 1;
}

/* 期刊标题 */
.journal-directory-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-directory-title:hover {
  color: #3498db;
  text-decoration: underline;
}

/* 期刊元信息 */
.journal-directory-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

/* 期刊摘要 */
.journal-directory-abstract {
  font-size: 0.95rem;
  color: #555;
  margin: 0 0 1rem 0;
  line-height: 1.5;
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 3;
  -moz-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
}

/* 关键词标签 */
.journal-directory-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.keyword-tag {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* 期刊状态 */
.journal-directory-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  min-width: 80px;
  margin-top: 0.5rem;
}

.journal-directory-status.待审核 {
  background: #f39c12;
  color: white;
}

.journal-directory-status.审核中 {
  background: #3498db;
  color: white;
}

.journal-directory-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-directory-status.已发表 {
  background: #2ecc71;
  color: white;
}

.journal-directory-status.已拒绝 {
  background: #e74c3c;
  color: white;
}

/* 无数据提示 */
.no-journals {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #e0e0e0;
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

/* 分页组件样式 */
.pagination-container {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.pagination-info {
  font-size: 0.95rem;
  color: #666;
  text-align: center;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.6rem 1.2rem;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.page-btn:hover:not(.active) {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.page-btn.active {
  background: #3498db;
  border-color: #3498db;
  color: white;
  font-weight: 500;
}

.ellipsis {
  color: #666;
  font-size: 1rem;
  margin: 0 0.5rem;
}

/* 页码跳转容器 */
.page-jump-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.jump-text {
  font-size: 0.95rem;
  color: #666;
}

.page-input {
  width: 60px;
  height: 36px;
  padding: 0 0.5rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  text-align: center;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.page-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.jump-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.jump-btn:hover {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filters-container {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .search-filter {
    min-width: auto;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .journal-directory-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .journal-directory-status {
    align-self: flex-start;
  }
  
  /* 分页响应式调整 */
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .page-numbers {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .page-btn {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  .pagination-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>