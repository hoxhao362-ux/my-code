<script setup>
import { ref, watch } from 'vue'
import { stripHtmlTags, truncateText } from '../utils/helpers'
import { MANUSCRIPT_STATUS } from '../constants/manuscriptStatus'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'logout', 'journals', 'modules', 'incrementJournalView', 'showDirectory', 'toggleDirectory'])

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 模拟论文数据库，用于搜索功能
const allJournals = ref([
  { 
    id: 1, 
    title: 'Deep Learning in Medical Image Analysis', 
    author: 'John Smith', 
    date: '2024-01-01', 
    status: MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
    abstract: 'This paper explores the application of deep learning in medical image analysis, including image classification, object detection, and segmentation techniques.',
    keywords: ['Deep Learning', 'Medical Imaging', 'Image Analysis'],
    content: '<h3>Abstract</h3><p>This paper explores the application of deep learning in medical image analysis.</p>'
  },
  { 
    id: 2, 
    title: 'Advances in Novel Drug Development', 
    author: 'Jane Doe', 
    date: '2024-01-02', 
    status: MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
    abstract: 'This paper reviews recent advances in novel drug development, including small molecule drugs, biologics, and gene therapy.',
    keywords: ['Drug Development', 'Small Molecule Drugs', 'Biologics', 'Gene Therapy'],
    content: '<h3>Abstract</h3><p>This paper reviews recent advances in novel drug development.</p>'
  },
  { 
    id: 3, 
    title: 'Clinical Research Methodology', 
    author: 'Robert Johnson', 
    date: '2024-01-03', 
    status: MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED,
    abstract: 'This paper systematically introduces the basic methods and design principles of clinical research.',
    keywords: ['Clinical Research', 'Methodology', 'RCT', 'Ethics'],
    content: '<h3>Abstract</h3><p>This paper systematically introduces the basic methods and design principles of clinical research.</p>'
  },
  { 
    id: 4, 
    title: 'Public Health Policy Analysis', 
    author: 'Emily Brown', 
    date: '2024-01-04', 
    status: MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED,
    abstract: 'This paper analyzes the current status and problems of public health policies.',
    keywords: ['Public Health', 'Policy Analysis', 'Health Services'],
    content: '<h3>Abstract</h3><p>This paper analyzes the current status and problems of public health policies.</p>'
  },
  { 
    id: 5, 
    title: 'Bioinformatics in Medical Research', 
    author: 'Michael Chen', 
    date: '2024-01-05', 
    status: MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED,
    abstract: 'This paper introduces the application of bioinformatics in medical research.',
    keywords: ['Bioinformatics', 'Genomics', 'Proteomics', 'Metabolomics'],
    content: '<h3>Abstract</h3><p>This paper introduces the application of bioinformatics in medical research.</p>'
  },
  { 
    id: 6, 
    title: 'AI in Healthcare: Current Status and Challenges', 
    author: 'Sarah Wilson', 
    date: '2024-01-06', 
    status: MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
    abstract: 'This paper reviews the current status of AI applications in healthcare.',
    keywords: ['Artificial Intelligence', 'Healthcare', 'Medical Imaging', 'Drug Development'],
    content: '<h3>Abstract</h3><p>This paper reviews the current status of AI applications in healthcare.</p>'
  }
])

// 近期投稿列表（取前4条）
const recentJournals = ref(allJournals.value.slice(0, 4))

// 搜索相关状态
const searchKeyword = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const selectedJournal = ref(null)
const showJournalContent = ref(false)

// 搜索处理函数
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  searchResults.value = allJournals.value.filter(journal => 
    journal.title.toLowerCase().includes(keyword) ||
    journal.author.toLowerCase().includes(keyword) ||
    stripHtmlTags(journal.abstract).toLowerCase().includes(keyword) ||
    journal.keywords.some(k => k.toLowerCase().includes(keyword))
  )
  showSearchResults.value = true
  showJournalContent.value = false
  selectedJournal.value = null
}

// 在线阅读论文
const readJournal = (journal) => {
  selectedJournal.value = journal
  showJournalContent.value = true
  showSearchResults.value = false
}

// 关闭论文内容
const closeJournalContent = () => {
  showJournalContent.value = false
  selectedJournal.value = null
}

const goToSubmit = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('submit')
}

const goToReview = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('review')
}

const goToProfile = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('profile')
}

const handleLogout = () => {
  // 调用父组件传递的登出方法
  props.logout()
}





// 查看论文详情（更新阅读量）
const viewJournalDetail = (id) => {
  props.incrementJournalView(id)
  props.navigateTo('journal', id)
}
</script>

<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link active">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goToSubmit">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="goToReview">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goToProfile">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 首页内容 -->
    <main class="main-content">
      <!-- 平台统计 -->
      <section class="stats-section">
        <h2 class="section-title">平台统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalJournals }}</h3>
              <p class="stat-label">总投稿量</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.pendingReviews }}</h3>
              <p class="stat-label">待审核稿件</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalUsers }}</h3>
              <p class="stat-label">注册用户</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.recentSubmissions }}</h3>
              <p class="stat-label">近期投稿</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 论文检索 -->
      <section class="search-section">
        <div class="search-container">
          <h2 class="section-title">论文检索</h2>
          <div class="search-bar">
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="请输入关键词搜索论文..."
              class="search-input"
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">
              <span class="search-icon">🔍</span> 搜索
            </button>
          </div>
          
          <!-- 搜索结果展示 -->
          <div v-if="showSearchResults" class="search-results">
            <div class="results-header">
              <h3>搜索结果 ({{ searchResults.length }})</h3>
              <button class="close-btn" @click="showSearchResults = false">×</button>
            </div>
            <div v-if="searchResults.length > 0" class="results-list">
              <div 
                v-for="journal in searchResults" 
                :key="journal.id" 
                class="result-item"
              >
                <div class="result-info">
                  <h4 class="result-title">{{ journal.title }}</h4>
                  <p class="result-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
                  <div class="result-abstract" v-html="truncateHtml(journal.abstract)"></div>
                  <div class="result-keywords">
                    <span 
                      v-for="(keyword, index) in journal.keywords" 
                      :key="index" 
                      class="keyword-tag"
                    >
                      {{ keyword }}
                    </span>
                  </div>
                </div>
                <div class="result-actions">
                  <button 
                    class="action-btn read-btn" 
                    @click="readJournal(journal)"
                  >
                    在线阅读
                  </button>
                  <button 
                    class="action-btn detail-btn" 
                    @click="viewJournalDetail(journal.id)"
                  >
                    查看详情
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="no-results">
              <p>没有找到匹配的论文</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 论文在线阅读 -->
      <section v-if="showJournalContent && selectedJournal" class="journal-content-section">
        <div class="journal-content-container">
          <div class="journal-header">
            <h2 class="journal-title">{{ selectedJournal.title }}</h2>
            <button class="close-btn" @click="closeJournalContent">×</button>
          </div>
          <div class="journal-meta">
            <p>作者：{{ selectedJournal.author }} | 投稿日期：{{ selectedJournal.date }}</p>
            <div class="journal-keywords">
              <span 
                v-for="(keyword, index) in selectedJournal.keywords" 
                :key="index" 
                class="keyword-tag"
              >
                {{ keyword }}
              </span>
            </div>
          </div>
          <div class="journal-content" v-html="selectedJournal.content"></div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">近期投稿</h2>
          <button class="submit-btn" @click="goToSubmit">+ 新投稿</button>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase()">
              {{ journal.status }}
            </div>
          </div>
        </div>
      </section>

      <!-- 平台介绍 -->
      <section class="intro-section">
        <h2 class="section-title">关于我们</h2>
        <div class="intro-content">
          <p>本平台是一个专业的期刊投稿系统，致力于为科研人员提供便捷、高效的投稿体验。我们支持多种类型的学术论文投稿，包括基础研究、临床研究、综述等。</p>
          <p>平台拥有严格的审稿流程，确保每一篇投稿都能得到专业、公正的评审。同时，我们提供实时的投稿状态查询，让作者能够随时了解稿件的处理进展。</p>
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
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
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

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

/* 统计部分 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

/* 近期投稿 */
.journals-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.submit-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.journals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.journal-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.2rem;
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
  margin: 0;
  font-size: 0.9rem;
}

.journal-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  min-width: 80px;
}

.journal-status.待审核 {
  background: #f39c12;
  color: white;
}

.journal-status.审核中 {
  background: #3498db;
  color: white;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.已拒绝 {
  background: #e74c3c;
  color: white;
}

/* 论文检索样式 */
.search-section {
  margin-bottom: 2rem;
}

.search-container {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.search-input {
  flex: 1;
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

.search-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.search-icon {
  font-size: 1.1rem;
}

/* 搜索结果样式 */
.search-results {
  margin-top: 1.5rem;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  background: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 1rem;
  transition: all 0.3s ease;
}

.result-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

.result-info {
  flex: 1;
}

.result-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.result-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

.result-abstract {
  font-size: 0.95rem;
  color: #555;
  margin: 0 0 0.75rem 0;
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

.result-keywords {
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

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
  justify-content: flex-start;
  min-width: 120px;
}

.action-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.read-btn {
  background: #27ae60;
  color: white;
}

.read-btn:hover {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.detail-btn {
  background: #95a5a6;
  color: white;
}

.detail-btn:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  font-style: italic;
}

/* 论文在线阅读样式 */
.journal-content-section {
  margin-bottom: 2rem;
}

.journal-content-container {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.journal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.journal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  line-height: 1.3;
}

.journal-meta {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.journal-meta p {
  font-size: 1rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

.journal-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.journal-content {
  color: #333;
  line-height: 1.8;
  font-size: 1rem;
}

.journal-content h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin: 1.5rem 0 1rem 0;
  font-weight: 600;
}

.journal-content p {
  margin: 0 0 1rem 0;
  text-align: justify;
}

/* 平台介绍 */
.intro-section {
  margin-bottom: 2rem;
}

.intro-content {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.intro-content p {
  margin-bottom: 1rem;
  color: #555;
  line-height: 1.6;
}

/* 目录功能样式 */
.directory-section {
  margin-bottom: 2rem;
}

.directory-container {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.filters-container {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
}

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

.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
  background: white;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.journals-directory {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.journal-directory-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.journal-directory-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

.journal-directory-info {
  flex: 1;
}

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

.journal-directory-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

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

.journal-directory-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.journal-directory-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
  justify-content: flex-start;
  min-width: 120px;
}

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
</style>
