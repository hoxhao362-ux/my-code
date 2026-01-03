<script setup>
import { ref } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'login', 'navigateTo'])

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const adminCode = ref('')
const error = ref('')

const handleRegister = () => {
  if (!username.value || !password.value || !confirmPassword.value) {
    error.value = '请填写完整信息'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  // 模拟管理员辨识密码验证
  const ADMIN_CODE = 'admin123' // 管理员辨识密码
  const role = adminCode.value === ADMIN_CODE ? 'admin' : 'user'
  
  // 模拟注册逻辑
  const userData = {
    username: username.value,
    role: role
  }
  
  // 调用父组件传递的登录方法（注册后直接登录）
  props.login(userData)
}

const goToLogin = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('login')
}
</script>

<template>
  <div class="register-container">
    <div class="register-form-wrapper">
      <div class="register-form">
        <h2 class="register-title">注册账号</h2>
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
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            placeholder="请再次输入密码"
          />
        </div>
        <div class="form-group">
          <label for="adminCode">管理员辨识密码（可选）</label>
          <input 
            type="password" 
            id="adminCode" 
            v-model="adminCode" 
            placeholder="输入管理员密码成为管理员，留空为普通用户"
          />
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button class="register-btn" @click="handleRegister">注册</button>
        <div class="login-link">
          <span>已有账号？</span>
          <a href="#" @click.prevent="goToLogin">立即登录</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-form-wrapper {
  width: 100%;
  max-width: 450px;
}

.register-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.register-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: bold;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
  font-size: 14px;
}

.register-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.register-btn:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.login-link a:hover {
  color: #5a6fd8;
  text-decoration: underline;
}
</style>
