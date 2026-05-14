<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToastStore } from '../stores/toast'
import { encryptPassword } from '../utils/encryption'
import userApi from '../utils/api'

const props = defineProps(['user', 'login', 'navigateTo'])
const toastStore = useToastStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
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
    error.value = '请填写账号和密码'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const encryptedPassword = await encryptPassword(password.value)
    
    const res = await userApi.login({
      username: username.value,
      password: encryptedPassword
    })

    if (res.access_token) {
      if (props.login) {
        props.login(res)
      }
      toastStore.add({ message: '登录成功', type: 'success' })
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('register')
}
</script>

<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-form-wrapper">
      <div class="login-form">
        <h2 class="login-title">Peerex Peer</h2>
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
        <div class="remember-me">
          <input 
            type="checkbox" 
            id="rememberMe" 
            v-model="rememberMe" 
          />
          <label for="rememberMe">记住密码</label>
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button class="login-btn" @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <div class="register-link">
          <span>还没有账号？</span>
          <a href="#" @click.prevent="goToRegister">立即注册</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/images/wzmc_20140317155634.jpg') no-repeat center center;
  background-size: cover;
  filter: brightness(0.7);
  animation: bgScale 20s ease-in-out infinite alternate;
}

@keyframes bgScale {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.1);
  }
}

.login-form-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  max-width: 400px;
  z-index: 10;
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.login-title {
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
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
  font-size: 14px;
}

/* 记住密码样式 */
.remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 8px;
}

.remember-me input[type="checkbox"] {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.remember-me label {
  margin: 0;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.register-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.register-link a:hover {
  color: #2980b9;
  text-decoration: underline;
}
</style>
