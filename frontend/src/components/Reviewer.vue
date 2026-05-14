<script setup>
import { ref, computed } from 'vue'
import { truncateHtml } from '../utils/helpers.js'
import { useToastStore } from '../stores/toast'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '../stores/user'

const { t } = useI18n()
const toastStore = useToastStore()
const userStore = useUserStore()

const props = defineProps(['user', 'navigateTo', 'journals', 'updateJournals'])

if (props.user?.role !== 'reviewer' && props.user?.role !== 'admin') {
  toastStore.add({ message: t('reviewer.permissionDenied'), type: 'warning' })
  props.navigateTo('home')
}

// 统计数据
const stats = computed(() => {
  // 所有待审核状态：待审核、审稿中、待初审、待复审、待终审
  const pendingStatuses = ['待审核', '审稿中', '待初审', '待复审', '待终审', 'Pending', 'Under Review', 'pending_initial_review', 'under_peer_review']
  
  return {
    totalJournals: props.journals.length,
    pendingJournals: props.journals.filter(journal => pendingStatuses.includes(journal.status)).length,
    reviewStage1Journals: props.journals.filter(journal => pendingStatuses.includes(journal.status) && (journal.reviewStage === '初审' || journal.reviewStage === 'Initial Review')).length,
    reviewStage2Journals: props.journals.filter(journal => pendingStatuses.includes(journal.status) && (journal.reviewStage === '复审' || journal.reviewStage === 'Peer Review')).length
  }
})

// 待审核稿件 - 审核员只看到复审阶段，管理员看到初审和终审阶段
const pendingJournals = computed(() => {
  const isAdmin = props.user?.role === 'admin'
  const allowedStages = isAdmin ? ['初审', '终审', 'Initial Review', 'Final Decision'] : ['复审', 'Peer Review']
  
  // 所有待审核状态：待审核、审稿中、待初审、待复审、待终审
  const pendingStatuses = ['待审核', '审稿中', '待初审', '待复审', '待终审', 'Pending', 'Under Review', 'pending_initial_review', 'under_peer_review']
  
  return props.journals.filter(journal => {
    return pendingStatuses.includes(journal.status) && allowedStages.includes(journal.reviewStage)
  })
  .sort((a, b) => new Date(b.date) - new Date(a.date))
})

// 退出登录
const handleLogout = async () => {
  await userStore.logout()
  props.navigateTo('login')
}

// 返回首页
const goBack = () => {
  props.navigateTo('home')
}

// 查看稿件详情
const viewJournalDetail = (id) => {
  props.navigateTo('journal', id)
}
</script>

<template>
  <div class="reviewer-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>{{ $t('common.platformName') }}</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goBack">{{ $t('nav.home') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">{{ $t('reviewer.dashboard') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">{{ $t('nav.profile') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">{{ $t('nav.logout') }}</a></li>
        </ul>
      </div>
    </nav>

    <!-- 审核员后台内容 -->
    <main class="reviewer-content">
      <div class="reviewer-wrapper">
        <h2 class="page-title">{{ $t('reviewer.dashboard') }}</h2>
        
        <!-- 统计数据 -->
        <div class="stats-section">
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.totalJournals }}</h3>
            <p class="stat-label">{{ $t('reviewer.stats.totalJournals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.pendingJournals }}</h3>
            <p class="stat-label">{{ $t('reviewer.stats.pendingJournals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.reviewStage1Journals }}</h3>
            <p class="stat-label">{{ $t('reviewer.stats.stage1Journals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.reviewStage2Journals }}</h3>
            <p class="stat-label">{{ $t('reviewer.stats.stage2Journals') }}</p>
          </div>
        </div>
        
        <!-- 待审核稿件 -->
        <div class="pending-journals">
          <h3 class="section-title">{{ $t('reviewer.pendingList.title') }}</h3>
          
          <div v-if="pendingJournals.length > 0" class="journal-list">
            <div 
              v-for="journal in pendingJournals" 
              :key="journal.id" 
              class="journal-item"
            >
              <div class="journal-info">
                <h4 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h4>
                <p class="journal-meta">{{ $t('reviewer.pendingList.author') }}：{{ journal.author }} | {{ $t('reviewer.pendingList.date') }}：{{ journal.date }} | {{ $t('reviewer.pendingList.module') }}：{{ journal.module }}</p>
                <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
              </div>
              <div class="journal-status">
                <span class="status-tag" :class="journal.status.toLowerCase()">
                  {{ journal.status }}
                  <span class="review-stage">({{ journal.reviewStage }})</span>
                </span>
              </div>
            </div>
          </div>
          
          <div v-else class="no-journals">
            <p>{{ $t('reviewer.pendingList.empty') }}</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 {{ $t('common.platformName') }}. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.reviewer-container {
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

/* 审核员后台内容 */
.reviewer-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.reviewer-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

/* 统计数据 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3498db;
  margin: 0 0 0.5rem 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0;
  font-size: 1rem;
}

/* 待审核稿件 */
.pending-journals {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
}

.journal-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.journal-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.1rem;
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
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.journal-abstract {
  color: #555;
  margin: 0;
  font-size: 0.85rem;
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 2;
  -moz-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.journal-status {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-tag {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.status-tag.审稿中 {
  background: #cce7ff;
  color: #004085;
}

.status-tag.已通过 {
  background: #d4edda;
  color: #155724;
}

.status-tag.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

.review-stage {
  font-size: 0.8rem;
  opacity: 0.8;
  margin-left: 0.5rem;
}

.no-journals {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

/* 按钮样式 */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.7;
  opacity: 0.7;
}

/* 页脚样式 */
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