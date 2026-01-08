<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const email = ref('')
const phone = ref('')
const error = ref('')
// 角色选择
const selectedRole = ref('')

const isFormValid = computed(() => {
  return username.value && password.value && confirmPassword.value && password.value === confirmPassword.value
})

const handleRegister = async () => {
  if (!isFormValid.value) {
    error.value = '请填写完整的注册信息并确保密码一致'
    return
  }
  
  if (password.value.length < 6) {
    error.value = '密码长度不能少于6位'
    return
  }
  
  // 加密密码
  const encryptedPassword = encryptPassword(password.value)
  
  // 模拟注册逻辑
  const userData = {
    username: username.value,
    password: encryptedPassword,
    role: selectedRole.value || 'user',
    email: email.value,
    phone: phone.value,
    avatar: ''
  }
  
  // 检查用户名是否已存在
  // 这里可以添加实际的后端检查逻辑
  const isUsernameExists = false
  
  if (isUsernameExists) {
    error.value = '该用户名已被注册'
    return
  }
  
  // 调用状态管理的登录方法（注册后自动登录）
  userStore.login(userData)
  
  // 跳转到对应的后台页面
  if (selectedRole.value === 'admin') {
    router.push('/admin/dashboard')
  } else if (selectedRole.value === 'reviewer') {
    router.push('/admin/audit-dashboard')
  } else if (selectedRole.value === 'author') {
    router.push('/admin/author-dashboard')
  } else {
    router.push('/admin/login')
  }
}

const goToLogin = () => {
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-register-container">
    <div class="admin-register-bg"></div>
    <div class="admin-register-form-wrapper">
      <div class="admin-register-form">
        <!-- 注册标题 -->
        <h2 class="admin-register-title">后台注册</h2>
        
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
        <div class="admin-form-group">
          <label for="admin-confirm-password">确认密码</label>
          <input 
            type="password" 
            id="admin-confirm-password" 
            v-model="confirmPassword" 
            placeholder="请再次输入密码"
          />
        </div>
        <div class="admin-form-group">
          <label for="admin-email">邮箱</label>
          <input 
            type="email" 
            id="admin-email" 
            v-model="email" 
            placeholder="请输入邮箱"
          />
        </div>
        <div class="admin-form-group">
          <label for="admin-phone">手机号</label>
          <input 
            type="tel" 
            id="admin-phone" 
            v-model="phone" 
            placeholder="请输入手机号"
          />
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
        <button class="admin-register-btn" @click="handleRegister" :disabled="!isFormValid">注册账号</button>
        <div class="admin-login-link">
          <span>已有账号？</span>
          <a href="#" @click.prevent="goToLogin">立即登录</a>
        </div>
        <div class="admin-back-link">
          <a href="/" @click.prevent="router.push('/')">返回主站</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 后台注册页面样式 */
.admin-register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
  position: relative;
}

.admin-register-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://picsum.photos/1920/1080');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  z-index: 0;
}

.admin-register-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
}

.admin-register-title {
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

/* 注册按钮样式 */
.admin-register-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: background-color 0.3s, transform 0.1s;
  margin-bottom: 1rem;
}

.admin-register-btn:hover:not(:disabled) {
  background-color: #218838;
}

.admin-register-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.65;
}

.admin-register-btn:active:not(:disabled) {
  transform: translateY(1px);
}

/* 登录链接样式 */
.admin-login-link {
  text-align: center;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.8rem;
}

.admin-login-link a {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-login-link a:hover {
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
  .admin-register-form-wrapper {
    padding: 1.8rem;
    margin: 1rem;
  }
  
  .admin-register-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>