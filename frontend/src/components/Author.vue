<script setup>
import { ref, computed } from 'vue'
import { truncateHtml } from '../utils/helpers.js'
import { useToastStore } from '../stores/toast'
<<<<<<< HEAD

=======
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
const toastStore = useToastStore()

const props = defineProps(['user', 'navigateTo', 'journals', 'updateJournals'])

if (props.user?.role !== 'author' && props.user?.role !== 'admin') {
<<<<<<< HEAD
  toastStore.add({ message: '您没有权限访问作者后台', type: 'warning' })
=======
  toastStore.add({ message: t('author.permissionDenied'), type: 'warning' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  props.navigateTo('home')
}

// 统计数据
const stats = computed(() => {
  const userJournals = props.journals.filter(journal => journal.author === props.user?.username)
  return {
    totalJournals: userJournals.length,
    pendingJournals: userJournals.filter(journal => ['审稿中', 'Pending', 'Under Review'].includes(journal.status)).length,
    passedJournals: userJournals.filter(journal => ['已通过', 'Accepted'].includes(journal.status)).length,
    rejectedJournals: userJournals.filter(journal => ['未通过', 'Rejected'].includes(journal.status)).length
  }
})

// 我的投稿
const userJournals = computed(() => {
  return props.journals.filter(journal => journal.author === props.user?.username)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
})

// 退出登录
const handleLogout = () => {
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
  <div class="author-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>{{ $t('common.platformName') }}</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goBack">{{ $t('nav.home') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">{{ $t('author.dashboard') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">{{ $t('nav.profile') }}</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">{{ $t('nav.logout') }}</a></li>
        </ul>
      </div>
    </nav>

    <!-- 作者后台内容 -->
    <main class="author-content">
      <div class="author-wrapper">
        <h2 class="page-title">{{ $t('author.dashboard') }}</h2>
        
        <!-- 统计数据 -->
        <div class="stats-section">
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.totalJournals }}</h3>
            <p class="stat-label">{{ $t('author.stats.totalJournals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.pendingJournals }}</h3>
            <p class="stat-label">{{ $t('author.stats.pendingJournals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.passedJournals }}</h3>
            <p class="stat-label">{{ $t('author.stats.passedJournals') }}</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.rejectedJournals }}</h3>
            <p class="stat-label">{{ $t('author.stats.rejectedJournals') }}</p>
          </div>
        </div>
        
        <!-- 快速操作 -->
        <div class="quick-actions">
          <button class="btn btn-primary" @click="navigateTo('submit')">
            {{ $t('author.quickActions.newSubmission') }}
          </button>
        </div>
        
        <!-- 我的投稿 -->
        <div class="my-submissions">
          <h3 class="section-title">{{ $t('author.mySubmissions.title') }}</h3>
          
          <div v-if="userJournals.length > 0" class="submission-list">
            <div 
              v-for="journal in userJournals" 
              :key="journal.id" 
              class="submission-item"
            >
              <div class="submission-info">
                <h4 class="submission-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h4>
                <p class="submission-meta">{{ $t('author.mySubmissions.date') }}：{{ journal.date }} | {{ $t('author.mySubmissions.module') }}：{{ journal.module }}</p>
                <p class="submission-abstract" v-html="truncateHtml(journal.abstract)"></p>
              </div>
              <div class="submission-status" :class="journal.status.toLowerCase()">
                {{ journal.status }}
              </div>
            </div>
          </div>
          
          <div v-else class="no-submissions">
            <p>{{ $t('author.mySubmissions.empty') }}</p>
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
.author-container {
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

/* 作者后台内容 */
.author-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.author-wrapper {
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

/* 快速操作 */
.quick-actions {
  display: flex;
  justify-content: flex-end;
}

/* 我的投稿 */
.my-submissions {
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

.submission-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.submission-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.submission-info {
  flex: 1;
}

.submission-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.submission-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.submission-meta {
  color: #7f8c8d;
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.submission-abstract {
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

.submission-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 80px;
  text-align: center;
}

.submission-status.待审核 {
  background: #fff3cd;
  color: #856404;
}

.submission-status.审核中 {
  background: #cce7ff;
  color: #004085;
}

.submission-status.已通过 {
  background: #d4edda;
  color: #155724;
}

.submission-status.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

.no-submissions {
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
