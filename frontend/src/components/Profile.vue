<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  user: Object,
  navigateTo: Function
})

// 模拟投稿历史数据
const submissionHistory = ref([
  { id: 1, title: '基于深度学习的医学图像分析', date: '2024-01-01', status: '待审核' },
  { id: 2, title: '新型药物研发进展', date: '2024-01-02', status: '审核中' },
  { id: 3, title: '临床研究方法学探讨', date: '2024-01-03', status: '已通过' }
])

const goBack = () => {
  props.navigateTo('home')
}

const viewJournalDetail = (id) => {
  props.navigateTo('journal', id)
}

const handleLogout = () => {
  props.navigateTo('login')
}
</script>

<template>
  <div class="profile-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goBack">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 个人中心内容 -->
    <main class="profile-content">
      <div class="profile-wrapper">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <div class="user-info">
            <div class="user-avatar">
              <span>{{ user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
            </div>
            <div class="user-details">
              <h2 class="user-name">{{ user?.username || '未知用户' }}</h2>
              <p class="user-role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
            </div>
          </div>
        </div>

        <!-- 投稿历史 -->
        <div class="submission-section">
          <h3 class="section-title">投稿历史</h3>
          
          <div v-if="submissionHistory.length > 0" class="submission-list">
            <div 
              v-for="submission in submissionHistory" 
              :key="submission.id" 
              class="submission-item"
            >
              <div class="submission-info">
                <h4 class="submission-title" @click="viewJournalDetail(submission.id)">{{ submission.title }}</h4>
                <p class="submission-meta">投稿日期：{{ submission.date }}</p>
              </div>
              <div class="submission-status" :class="submission.status.toLowerCase()">
                {{ submission.status }}
              </div>
            </div>
          </div>
          
          <div v-else class="no-submissions">
            <p>您还没有投稿记录</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="btn btn-primary" @click="navigateTo('submit')">
            + 新投稿
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
.profile-container {
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

/* 个人中心内容 */
.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.profile-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 用户信息卡片 */
.user-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  font-weight: bold;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.user-role {
  color: #7f8c8d;
  margin: 0;
  font-size: 1rem;
}

/* 投稿历史 */
.submission-section {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.5rem;
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
  margin: 0;
  font-size: 0.9rem;
}

.submission-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
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

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
}

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

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
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
