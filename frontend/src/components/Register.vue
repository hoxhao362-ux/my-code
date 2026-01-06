<script setup>
import { ref, computed } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'login', 'navigateTo', 'adminCode', 'reviewerCode'])

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const email = ref('')
const phone = ref('')
const verificationCode = ref('')
const inputInvitationCode = ref('')
const error = ref('')
const countdown = ref(0)
const isCounting = ref(false)

// 正则表达式
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const phoneRegex = /^1[3-9]\d{9}$/

// 计算属性：是否可以发送验证码
const canSendCode = computed(() => {
  return emailRegex.test(email.value) && !isCounting.value
})

// 发送验证码
const sendVerificationCode = () => {
  if (!emailRegex.test(email.value)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  
  // 模拟发送验证码
  alert('验证码已发送到您的邮箱：' + email.value)
  
  // 开始倒计时
  isCounting.value = true
  countdown.value = 60
  
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      isCounting.value = false
    }
  }, 1000)
}

// 加密密码（模拟）
const encryptPassword = (pwd) => {
  // 简单的Base64加密，实际项目中应该使用更安全的加密方式
  return btoa(pwd)
}

const handleRegister = () => {
  // 表单验证
  if (!username.value || !password.value || !confirmPassword.value || !email.value || !verificationCode.value) {
    error.value = '请填写完整信息'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  if (!emailRegex.test(email.value)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  
  if (phone.value && !phoneRegex.test(phone.value)) {
    error.value = '请输入有效的手机号'
    return
  }
  
  // 模拟验证码验证
  if (verificationCode.value !== '123456') {
    error.value = '验证码错误'
    return
  }
  
  // 邀请码验证，确定角色
  let role = 'user' // 默认普通用户
  if (inputInvitationCode.value === props.adminCode) {
    role = 'admin' // 管理员
  } else if (inputInvitationCode.value === props.reviewerCode) {
    role = 'reviewer' // 审核员
  } else if (inputInvitationCode.value === 'author123') {
    role = 'author' // 作者
  } else if (inputInvitationCode.value) {
    error.value = '无效的邀请码'
    return
  }
  
  // 模拟注册逻辑
  const userData = {
    username: username.value,
    password: encryptPassword(password.value), // 加密密码
    role: role,
    email: email.value,
    phone: phone.value,
    avatar: ''
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
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="请输入邮箱"
          />
        </div>
        <div class="form-group">
          <label for="phone">手机号（可选）</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="phone" 
            placeholder="请输入手机号"
          />
        </div>
        <div class="form-row">
          <div class="form-group" style="flex: 1;">
            <label for="verificationCode">验证码</label>
            <input 
              type="text" 
              id="verificationCode" 
              v-model="verificationCode" 
              placeholder="请输入验证码"
            />
          </div>
          <div class="form-group" style="margin-left: 10px;">
            <label>&nbsp;</label>
            <button 
              type="button" 
              class="code-btn" 
              :disabled="!canSendCode" 
              @click="sendVerificationCode"
            >
              {{ isCounting ? countdown + 's后重试' : '获取验证码' }}
            </button>
          </div>
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
          <label for="invitationCode">邀请码（可选）</label>
          <input 
            type="password" 
            id="invitationCode" 
            v-model="inputInvitationCode" 
            placeholder="输入邀请码成为管理员/审核员/作者，留空为普通用户"
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

.form-row {
  display: flex;
  align-items: flex-end;
}

.code-btn {
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.code-btn:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.code-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.7;
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
