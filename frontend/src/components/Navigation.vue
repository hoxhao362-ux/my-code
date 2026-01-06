<script setup>
const props = defineProps({
  user: Object,
  currentPage: String,
  toggleDirectory: Function,
  navigateTo: Function,
  logout: Function
})

const goToSubmit = () => {
  props.navigateTo('submit')
}

const goToReview = () => {
  props.navigateTo('review')
}

const goToProfile = () => {
  props.navigateTo('profile')
}

const goToHome = () => {
  props.navigateTo('home')
}

const goToAdmin = () => {
  props.navigateTo('admin')
}

const handleLogout = () => {
  props.logout()
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo">
        <h1>期刊投稿平台</h1>
      </div>
      <ul class="navbar-menu">
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentPage === 'home' }"
            @click.prevent="goToHome"
          >
            首页
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            @click.prevent="toggleDirectory"
          >
            目录
          </a>
        </li>
        <!-- 后台管理已移至个人中心 -->
        <!-- 普通用户、作者和管理员都可以投稿 -->
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            @click.prevent="goToSubmit"
          >
            投稿
          </a>
        </li>
        <!-- 审稿功能：管理员和审核员可见 -->
        <li v-if="user?.role === 'admin' || user?.role === 'reviewer'" class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ active: currentPage === 'review' }"
            @click.prevent="goToReview"
          >
            审稿
          </a>
        </li>
        <!-- 作者中心：所有登录用户可见 -->
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ active: currentPage === 'profile' }"
            @click.prevent="goToProfile"
          >
            个人中心
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            @click.prevent="window.location.href = '/admin/login'"
          >
            登录后台
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link logout"
            @click.prevent="handleLogout"
          >
            退出登录
          </a>
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped>
/* 导航栏样式 - 固定在顶部 */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  border: none;
  outline: none;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.5rem;
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
  margin-left: 0.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  display: inline-block;
  border-radius: 5px;
  transition: all 0.3s ease;
  min-width: 70px;
  text-align: center;
}

.nav-link:hover,
.nav-link.active {
  color: #3498db;
  background: rgba(52, 152, 219, 0.1);
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
  background: rgba(231, 76, 60, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .nav-item {
    margin-left: 0;
  }
  
  .nav-link {
    font-size: 0.9rem;
    padding: 0.5rem 1rem;
    min-width: 70px;
  }
  
  .navbar-logo h1 {
    font-size: 1.3rem;
  }
}
</style>