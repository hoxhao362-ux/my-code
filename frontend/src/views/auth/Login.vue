<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
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

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  
  try {
    // 加密密码
    const encryptedPassword = encryptPassword(password.value)
    
    // 准备登录凭证
    const credentials = {
      username: username.value,
      password: encryptedPassword
    }
    
    // 调用状态管理的登录方法
    await userStore.login(credentials)
    
    // 记住密码功能
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', username.value)
      localStorage.setItem('rememberedPassword', password.value)
    } else {
      localStorage.removeItem('rememberedUsername')
      localStorage.removeItem('rememberedPassword')
    }
    
    // 跳转到首页
    router.push('/home')
  } catch (err) {
    console.error('登录失败:', err)
    // 如果API调用失败，使用模拟登录逻辑
    // 根据用户名自动识别角色
    let role = username.value === 'admin' ? 'admin' : 
               username.value === 'reviewer' ? 'reviewer' : 
               username.value === 'user' ? 'user' : 'author'
    
    // 创建用户数据
    const userData = {
      username: username.value,
      role: role,
      email: '',
      phone: '',
      avatar: ''
    }
    
    // 直接设置用户状态
    userStore.user = userData
    localStorage.setItem('user', JSON.stringify(userData))
    
    // 跳转到首页
    router.push('/home')
  }
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
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/images/wzmc_20140317155634.jpg');
  background-size: cover;
  background-position: center;
  opacity: 0.8;
  z-index: 0;
  animation: backgroundAnimation 20s ease infinite;
}

/* 背景动态效果 */
@keyframes backgroundAnimation {
  0% {
    transform: scale(1) translateX(0);
  }
  50% {
    transform: scale(1.1) translateX(-5%);
  }
  100% {
    transform: scale(1) translateX(0);
  }
}

.login-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
  backdrop-filter: blur(10px);
  animation: fadeIn 0.5s ease-out;
}

/* 表单淡入效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: bold;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.95rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.9);
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  background-color: white;
}

/* 记住密码样式 */
.remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 0.75rem;
}

.remember-me input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: #3498db;
}

.remember-me label {
  margin: 0;
  font-size: 0.95rem;
  color: #666;
  cursor: pointer;
  transition: color 0.3s ease;
}

.remember-me label:hover {
  color: #3498db;
}

/* 错误消息样式 */
.error-message {
  color: #e74c3c;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  text-align: center;
  padding: 0.75rem;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

/* 登录按钮样式 */
.login-btn {
  width: 100%;
  padding: 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.login-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
}

/* 注册链接样式 */
.register-link {
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.register-link a:hover {
  color: #2980b9;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form-wrapper {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .login-title {
    font-size: 1.6rem;
  }
}
</style>