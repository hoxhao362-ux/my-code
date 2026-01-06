<script setup>
import { ref, computed } from 'vue'

const props = defineProps(['user', 'navigateTo', 'journals', 'updateJournals'])

// 看门狗功能：检查用户是否有权限访问管理员后台
if (props.user?.role !== 'admin') {
  alert('您没有权限访问管理员后台')
  props.navigateTo('home')
}

// 统计数据
const stats = computed(() => {
  return {
    totalJournals: props.journals.length,
    pendingJournals: props.journals.filter(journal => journal.status === '审稿中').length,
    passedJournals: props.journals.filter(journal => journal.status === '已通过').length,
    rejectedJournals: props.journals.filter(journal => journal.status === '未通过').length
  }
})

// 退出登录
const handleLogout = () => {
  props.navigateTo('login')
}

// 返回首页
const goBack = () => {
  props.navigateTo('home')
}
</script>

<template>
  <div class="admin-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goBack">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">管理员后台</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 管理员后台内容 -->
    <main class="admin-content">
      <div class="admin-wrapper">
        <h2 class="page-title">管理员后台</h2>
        
        <!-- 统计数据 -->
        <div class="stats-section">
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.totalJournals }}</h3>
            <p class="stat-label">总投稿数</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.pendingJournals }}</h3>
            <p class="stat-label">待审核稿件</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.passedJournals }}</h3>
            <p class="stat-label">已通过稿件</p>
          </div>
          <div class="stat-card">
            <h3 class="stat-number">{{ stats.rejectedJournals }}</h3>
            <p class="stat-label">已拒绝稿件</p>
          </div>
        </div>
        
        <!-- 管理员功能 -->
        <div class="admin-functions">
          <div class="function-card">
            <h3>稿件管理</h3>
            <p>查看和管理所有稿件</p>
            <button class="btn btn-primary" @click="navigateTo('review')">
              进入稿件管理
            </button>
          </div>
          <div class="function-card">
            <h3>用户管理</h3>
            <p>管理所有用户账号</p>
            <button class="btn btn-primary" disabled>
              进入用户管理
            </button>
          </div>
          <div class="function-card">
            <h3>系统设置</h3>
            <p>配置系统参数</p>
            <button class="btn btn-primary" @click="navigateTo('profile')">
              进入系统设置
            </button>
          </div>
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
.admin-container {
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

/* 管理员后台内容 */
.admin-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.admin-wrapper {
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

/* 管理员功能 */
.admin-functions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.function-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.function-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.function-card h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.function-card p {
  color: #7f8c8d;
  margin: 0 0 1.5rem 0;
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