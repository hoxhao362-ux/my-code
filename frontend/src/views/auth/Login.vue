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
  const savedUsername = localStorage.getItem('rememberedUsername')
  const savedPassword = localStorage.getItem('rememberedPassword')
  if (savedUsername && savedPassword) {
    username.value = savedUsername
    password.value = savedPassword
    rememberMe.value = true
  }
})

// 点击空白处时隐藏记住密码的下拉菜单
const handleDocumentClick = (e) => {
  // 这里可以添加逻辑来处理点击空白处的情况
  // 例如关闭下拉菜单或其他弹窗
}

// 添加全局点击事件监听
onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

// 登录成功后跳转的目标页面
const targetPage = computed(() => {
  if (selectedRole.value === 'admin') {
    return '/admin'
  } else if (selectedRole.value === 'reviewer') {
    return '/reviewer'
  } else if (selectedRole.value === 'author') {
    return '/author'
  } else {
    return '/'
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
             username.value === 'reviewer' ? 'reviewer' : 'user')
  
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
  
  // 记住密码功能
  if (rememberMe.value) {
    localStorage.setItem('rememberedUsername', username.value)
    localStorage.setItem('rememberedPassword', password.value)
  } else {
    localStorage.removeItem('rememberedUsername')
    localStorage.removeItem('rememberedPassword')
  }
  
  // 跳转到对应的页面
  router.push(targetPage.value)
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-form-wrapper">
      <div class="login-form">
        <!-- 登录标题 -->
        <h2 class="login-title">期刊投稿平台</h2>
        
        <!-- 登录入口切换 -->
        <div class="login-tabs">
          <button class="tab-btn active">网站主站</button>
          <button class="tab-btn">作者后台</button>
        </div>
        
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="请输入密码"
          />
        </div>
        
        <!-- 记住密码 -->
        <div class="form-group remember-me">
          <input 
            type="checkbox" 
            id="rememberMe" 
            v-model="rememberMe" 
          />
          <label for="rememberMe">记住密码</label>
        </div>
        
        <!-- 角色选择（仅主站登录显示） -->
        <div class="form-group">
          <label for="role">角色</label>
          <select 
            id="role" 
            v-model="selectedRole"
            class="role-select"
          >
            <option value="">请选择角色</option>
            <option value="admin">管理员</option>
            <option value="reviewer">审核员</option>
            <option value="author">作者</option>
            <option value="user">普通用户</option>
          </select>
        </div>
        
        <p v-if="error" class="error-message">{{ error }}</p>
        <button class="login-btn" @click="handleLogin">登录</button>
        <div class="register-link">
          <span>还没有账号？</span>
          <a href="#" @click.prevent="goToRegister">立即注册</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 登录页面样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  position: relative;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://via.placeholder.com/1920x1080');
  background-size: cover;
  background-position: center;
  opacity: 0.5;
  z-index: 0;
}

.login-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

/* 登录入口切换 */
.login-tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  color: #666;
}

.tab-btn.active {
  border-bottom-color: #4a90e2;
  color: #4a90e2;
  font-weight: 500;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90e2;
}

/* 记住密码样式 */
.remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.remember-me input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.remember-me label {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
  cursor: pointer;
}

/* 角色选择样式 */
.role-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
  transition: border-color 0.3s;
}

.role-select:focus {
  outline: none;
  border-color: #4a90e2;
}

/* 错误消息样式 */
.error-message {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* 登录按钮样式 */
.login-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
  margin-bottom: 1rem;
}

.login-btn:hover {
  background-color: #229954;
}

/* 注册链接样式 */
.register-link {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.register-link a {
  color: #4a90e2;
  text-decoration: none;
  transition: color 0.3s;
}

.register-link a:hover {
  color: #357abd;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form-wrapper {
    padding: 1.5rem;
    margin: 1rem;
  }
}
</style>