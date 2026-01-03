<script setup>
import { ref } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'logout'])

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 近期投稿列表
const recentJournals = ref([
  { id: 1, title: '基于深度学习的医学图像分析', author: '张三', date: '2024-01-01', status: '待审核' },
  { id: 2, title: '新型药物研发进展', author: '李四', date: '2024-01-02', status: '审核中' },
  { id: 3, title: '临床研究方法学探讨', author: '王五', date: '2024-01-03', status: '已通过' },
  { id: 4, title: '公共卫生政策分析', author: '赵六', date: '2024-01-04', status: '已拒绝' }
])

const handleLogout = () => {
  // 调用父组件传递的登出方法
  props.logout()
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

const viewJournalDetail = (id) => {
  // 调用父组件传递的导航方法，跳转到稿件详情页
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
