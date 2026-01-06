<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
// 角色选择
const selectedRole = ref('')
// 记住密码
const rememberMe = ref(false)

// 从localStorage加载记住的密码
onMounted(() => {
  const savedUsername = localStorage.getItem('adminRememberedUsername')
  const savedPassword = localStorage.getItem('adminRememberedPassword')
  if (savedUsername && savedPassword) {
    username.value = savedUsername
    password.value = savedPassword
    rememberMe.value = true
  }
})

// 登录成功后跳转的目标页面
const targetPage = computed(() => {
  if (selectedRole.value === 'admin' || username.value === 'admin') {
    return '/admin/dashboard'
  } else if (selectedRole.value === 'reviewer' || username.value === 'reviewer') {
    return '/admin/audit-dashboard'
  } else if (selectedRole.value === 'author' || username.value === 'author') {
    return '/admin/author-dashboard'
  } else {
    return '/admin/login'
  }
})

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  
  // 加密密码
  const encryptedPassword = encryptPassword(password.value)
  
  // 角色分配优先级：1. 用户选择的角色 2. 用户名自动判断
  let role = selectedRole.value || (username.value === 'admin' ? 'admin' : 
             username.value === 'reviewer' ? 'reviewer' : 
             username.value === 'author' ? 'author' : 'user')
  
  // 模拟登录逻辑
  const userData = {
    username: username.value,
    password: encryptedPassword,
    role: role,
    email: '',
    phone: '',
    avatar: ''
  }
  
  // 调用状态管理的登录方法
  userStore.login(userData)
  
  // 记住密码功能（使用独立的localStorage键名）
  if (rememberMe.value) {
    localStorage.setItem('adminRememberedUsername', username.value)
    localStorage.setItem('adminRememberedPassword', password.value)
  } else {
    localStorage.removeItem('adminRememberedUsername')
    localStorage.removeItem('adminRememberedPassword')
  }
  
  // 跳转到对应的后台页面
  router.push(targetPage.value)
}

const goToRegister = () => {
  router.push('/admin/register')
}
</script>

<template>
  <div class="admin-login-container">
    <div class="admin-login-bg"></div>
    <div class="admin-login-form-wrapper">
      <div class="admin-login-form">
        <!-- 登录标题 -->
        <h2 class="admin-login-title">后台管理系统</h2>
        
        <div class="admin-form-group">
          <label for="admin-username">用户名</label>
          <input 
            type="text" 
            id="admin-username" 
            v-model="username" 
            placeholder="请输入用户名"
          />
        </div>
        <div class="admin-form-group">
          <label for="admin-password">密码</label>
          <input 
            type="password" 
            id="admin-password" 
            v-model="password" 
            placeholder="请输入密码"
          />
        </div>
        
        <!-- 记住密码 -->
        <div class="admin-form-group admin-remember-me">
          <input 
            type="checkbox" 
            id="admin-rememberMe" 
            v-model="rememberMe" 
          />
          <label for="admin-rememberMe">记住密码</label>
        </div>
        
        <!-- 角色选择 -->
        <div class="admin-form-group">
          <label for="admin-role">角色</label>
          <select 
            id="admin-role" 
            v-model="selectedRole"
            class="admin-role-select"
          >
            <option value="">请选择角色</option>
            <option value="admin">管理员</option>
            <option value="reviewer">审核员</option>
            <option value="author">作者</option>
          </select>
        </div>
        
        <p v-if="error" class="admin-error-message">{{ error }}</p>
        <button class="admin-login-btn" @click="handleLogin">登录后台</button>
        <div class="admin-register-link">
          <span>还没有账号？</span>
          <a href="#" @click.prevent="goToRegister">立即注册</a>
        </div>
        <div class="admin-back-link">
          <a href="/" @click.prevent="router.push('/')">返回主站</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 后台登录页面样式 */
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
  position: relative;
}

.admin-login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://via.placeholder.com/1920x1080');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  z-index: 0;
}

.admin-login-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
}

.admin-login-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #343a40;
  font-size: 1.8rem;
}

/* 表单样式 */
.admin-form-group {
  margin-bottom: 1.2rem;
}

.admin-form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-size: 0.95rem;
  font-weight: 500;
}

.admin-form-group input,
.admin-form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background-color: white;
}

.admin-form-group input:focus,
.admin-form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* 记住密码样式 */
.admin-remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1.2rem;
  gap: 0.5rem;
}

.admin-remember-me input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #007bff;
}

.admin-remember-me label {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
  cursor: pointer;
}

/* 角色选择样式 */
.admin-role-select {
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='none' stroke='%23495057' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 16px;
  padding-right: 2rem;
  appearance: none;
}

/* 错误消息样式 */
.admin-error-message {
  color: #dc3545;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* 登录按钮样式 */
.admin-login-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: background-color 0.3s, transform 0.1s;
  margin-bottom: 1rem;
}

.admin-login-btn:hover {
  background-color: #0056b3;
}

.admin-login-btn:active {
  transform: translateY(1px);
}

/* 注册链接样式 */
.admin-register-link {
  text-align: center;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.8rem;
}

.admin-register-link a {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-register-link a:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* 返回主站链接样式 */
.admin-back-link {
  text-align: center;
  font-size: 0.9rem;
}

.admin-back-link a {
  color: #6c757d;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-back-link a:hover {
  color: #495057;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-login-form-wrapper {
    padding: 1.8rem;
    margin: 1rem;
  }
  
  .admin-login-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>