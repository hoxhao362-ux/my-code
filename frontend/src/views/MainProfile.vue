<script setup>
import { ref, computed } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import { validateEmail, validatePhone, encryptPassword } from '../utils/encryption'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const user = computed(() => userStore.user)

// 编辑模式
const isEditing = ref(false)
const isChangingPassword = ref(false)

// 头像弹窗状态
const showAvatarModal = ref(false)
const showAvatarActions = ref(false)
const fileInput = ref(null)

// 表单数据
const formData = ref({
  username: user.value?.username || '',
  email: user.value?.email || '',
  phone: user.value?.phone || '',
  avatar: user.value?.avatar || ''
})

// 密码更改数据
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证数据
const verificationData = ref({
  verifyPassword: '',
  isVerified: false
})

// 获取当前用户的投稿记录
const userJournals = computed(() => {
  if (!user.value) return []
  return userStore.journals.filter(journal => journal.author === user.value.username)
})

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// 进入编辑模式
const startEditing = () => {
  isEditing.value = true
  isChangingPassword.value = false
  // 重置验证状态
  verificationData.value = {
    verifyPassword: '',
    isVerified: false
  }
}

// 进入更改密码模式
const startChangePassword = () => {
  isEditing.value = true
  isChangingPassword.value = true
  // 重置密码表单
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  // 重置验证状态
  verificationData.value = {
    verifyPassword: '',
    isVerified: false
  }
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  isChangingPassword.value = false
  // 重置表单数据
  formData.value = {
    username: user.value?.username || '',
    email: user.value?.email || '',
    phone: user.value?.phone || '',
    avatar: user.value?.avatar || ''
  }
  // 重置密码表单
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  // 重置验证状态
  verificationData.value = {
    verifyPassword: '',
    isVerified: false
  }
}

// 显示头像操作菜单
const showAvatarMenu = (event) => {
  event.stopPropagation()
  showAvatarActions.value = true
}

// 隐藏头像操作菜单
const hideAvatarMenu = () => {
  showAvatarActions.value = false
}

// 查看头像
const viewAvatar = () => {
  showAvatarModal.value = true
  hideAvatarMenu()
}

// 关闭头像查看弹窗
const closeAvatarModal = () => {
  showAvatarModal.value = false
}

// 触发文件选择
const triggerFileSelect = () => {
  hideAvatarMenu()
  fileInput.value?.click()
}

// 处理头像上传
const handleAvatarUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }
    
    // 检查文件大小（限制为5MB）
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过5MB')
      return
    }
    
    // 读取文件并显示预览
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target.result
      // 更新用户头像
      formData.value.avatar = imageUrl
      userStore.updateUser({ avatar: imageUrl })
      alert('头像更新成功')
    }
    reader.readAsDataURL(file)
    
    // 清空文件输入，允许再次选择同一个文件
    event.target.value = ''
  }
}

// 验证当前密码
const verifyPassword = () => {
  if (!verificationData.value.verifyPassword) {
    alert('请输入当前密码')
    return
  }
  
  // 加密输入的密码进行验证
  const encryptedPassword = encryptPassword(verificationData.value.verifyPassword)
  
  // 验证密码是否正确
  if (encryptedPassword === user.value?.password) {
    verificationData.value.isVerified = true
  } else {
    alert('当前密码不正确')
    verificationData.value.isVerified = false
  }
}

// 保存用户信息
const saveUserInfo = () => {
  // 如果未验证密码，先验证
  if (!verificationData.value.isVerified) {
    alert('请先验证当前密码')
    return
  }
  
  // 验证邮箱格式
  if (formData.value.email && !validateEmail(formData.value.email)) {
    alert('请输入有效的邮箱地址')
    return
  }
  
  // 验证手机号格式
  if (formData.value.phone && !validatePhone(formData.value.phone)) {
    alert('请输入有效的手机号')
    return
  }
  
  // 更新用户数据
  userStore.updateUser(formData.value)
  
  // 退出编辑模式
  cancelEditing()
  alert('个人信息更新成功')
}

// 更改密码
const changePassword = () => {
  // 如果未验证密码，先验证
  if (!verificationData.value.isVerified) {
    alert('请先验证当前密码')
    return
  }
  
  // 验证新密码
  if (!passwordForm.value.newPassword) {
    alert('请输入新密码')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.value.newPassword.length < 6) {
    alert('新密码长度不能少于6位')
    return
  }
  
  // 加密新密码
  const encryptedNewPassword = encryptPassword(passwordForm.value.newPassword)
  
  // 更新用户密码
  userStore.updateUser({ password: encryptedNewPassword })
  
  // 退出编辑模式
  cancelEditing()
  alert('密码更改成功')
}
</script>

<template>
  <div class="profile-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'profile'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <!-- 个人中心内容 -->
    <main class="profile-content">
      <div class="profile-wrapper">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <!-- 头像位置 -->
          <div class="avatar-section">
            <div 
              class="user-avatar-container"
              @click="hideAvatarMenu"
            >
              <div 
                class="user-avatar" 
                @click.stop="showAvatarActions = !showAvatarActions"
              >
                <img 
                  v-if="user?.avatar" 
                  :src="user.avatar" 
                  :alt="user.username"
                  class="avatar-image"
                />
                <span v-else>{{ user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
              </div>
              
              <!-- 头像操作菜单 -->
              <div 
                v-if="showAvatarActions" 
                class="avatar-actions-menu"
              >
                <button 
                  class="btn btn-edit" 
                  @click="viewAvatar"
                >
                  查看头像
                </button>
                <button 
                  class="btn btn-password" 
                  @click="triggerFileSelect"
                >
                  更改头像
                </button>
              </div>
              
              <!-- 隐藏的文件输入控件 -->
              <input 
                type="file" 
                ref="fileInput"
                accept="image/*" 
                style="display: none" 
                @change="handleAvatarUpload"
              />
            </div>
          </div>
          
          <div class="user-card-header">
            <h3 class="card-title">个人信息</h3>
            <div class="header-actions">
              <!-- 查看模式下显示编辑和更改密码按钮 -->
              <template v-if="!isEditing">
                <button 
                  class="btn btn-edit" 
                  @click="startEditing()"
                >
                  编辑信息
                </button>
                <button 
                  class="btn btn-password" 
                  @click="startChangePassword()"
                >
                  更改密码
                </button>
              </template>
              <!-- 编辑模式下显示保存和取消按钮 -->
              <template v-else>
                <button 
                  class="btn btn-save" 
                  @click="isChangingPassword ? changePassword() : saveUserInfo()"
                >
                  保存
                </button>
                <button 
                  class="btn btn-cancel" 
                  @click="cancelEditing"
                >
                  取消
                </button>
              </template>
            </div>
          </div>
          
          <!-- 查看模式 -->
          <div v-if="!isEditing" class="user-info">
            <div class="user-details">
              <h2 class="user-name">{{ user?.username || '未知用户' }}</h2>
              <p class="user-role">
                {{ user?.role === 'admin' ? '管理员' : 
                   user?.role === 'reviewer' ? '审核员' : 
                   user?.role === 'author' ? '作者' : '普通用户' }}
              </p>
              <div class="user-contact">
                <p v-if="user?.email"><strong>邮箱：</strong>{{ user.email }}</p>
                <p v-if="user?.phone"><strong>手机号：</strong>{{ user.phone }}</p>
              </div>
            </div>
          </div>
          
          <!-- 编辑模式 -->
          <div v-else class="user-edit-form">
            <!-- 密码验证部分 -->
            <div class="verification-section">
              <h3 class="verification-title">身份验证</h3>
              <div class="verification-form">
                <div class="form-row">
                  <div class="form-group">
                    <label for="verify-password">请输入当前密码</label>
                    <div class="password-input-group">
                      <input 
                        type="password" 
                        id="verify-password" 
                        v-model="verificationData.verifyPassword"
                        placeholder="请输入当前密码"
                      />
                      <button class="btn btn-verify" @click="verifyPassword">
                        验证
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="verificationData.isVerified" class="verification-status success">
                  密码验证成功，可以进行后续操作
                </div>
                <div v-else class="verification-status pending">
                  请先验证当前密码
                </div>
              </div>
            </div>
            
            <!-- 个人信息编辑 -->
            <div v-if="!isChangingPassword" class="info-edit-section">
              <h3 class="edit-section-title">编辑个人信息</h3>
              <div class="form-row">
                <div class="form-group">
                  <label for="username">用户名</label>
                  <input 
                    type="text" 
                    id="username" 
                    v-model="formData.username"
                    placeholder="请输入用户名"
                  />
                </div>
                <div class="form-group">
                  <label for="email">邮箱</label>
                  <input 
                    type="email" 
                    id="email" 
                    v-model="formData.email"
                    placeholder="请输入邮箱"
                  />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label for="phone">手机号</label>
                  <input 
                    type="tel" 
                    id="phone" 
                    v-model="formData.phone"
                    placeholder="请输入手机号"
                  />
                </div>
              </div>
            </div>
            
            <!-- 更改密码表单 -->
            <div v-else class="password-edit-section">
              <h3 class="edit-section-title">更改密码</h3>
              <div class="form-row">
                <div class="form-group">
                  <label for="new-password">新密码</label>
                  <input 
                    type="password" 
                    id="new-password" 
                    v-model="passwordForm.newPassword"
                    placeholder="请输入新密码"
                    :disabled="!verificationData.isVerified"
                  />
                </div>
                <div class="form-group">
                  <label for="confirm-password">确认新密码</label>
                  <input 
                    type="password" 
                    id="confirm-password" 
                    v-model="passwordForm.confirmPassword"
                    placeholder="请确认新密码"
                    :disabled="!verificationData.isVerified"
                  />
                </div>
              </div>
              <div class="password-requirements">
                <p class="requirement-item">• 密码长度不能少于6位</p>
                <p class="requirement-item">• 密码应包含字母和数字</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 头像查看弹窗 -->
        <div 
          v-if="showAvatarModal" 
          class="avatar-modal" 
          @click="closeAvatarModal"
        >
          <div class="modal-content" @click.stop>
            <span class="close-btn" @click="closeAvatarModal">&times;</span>
            <div v-if="user?.avatar" class="avatar-preview-container">
              <img :src="user?.avatar" :alt="user?.username" class="full-size-avatar" />
            </div>
            <div v-else class="no-avatar-message">
              <p>您还没有上传头像</p>
            </div>
          </div>
        </div>
        
        <!-- 用户投稿记录 -->
        <div class="journals-section">
          <h3 class="section-title">我的投稿</h3>
          <div v-if="userJournals.length > 0" class="journals-list">
            <div 
              v-for="journal in userJournals" 
              :key="journal.id" 
              class="journal-item"
            >
              <div class="journal-info">
                <h4 class="journal-title" @click="$router.push(`/journal/${journal.id}`)">
                  {{ journal.title }}
                </h4>
                <div class="journal-meta">
                  <span>投稿日期：{{ journal.date }}</span>
                  <span>模块：{{ journal.module }}</span>
                  <span>状态：<span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span></span>
                  <span>阅读量：{{ journal.viewCount }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-journals">
            <p>暂无投稿记录</p>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="profile-actions">
          <button class="btn btn-primary" @click="$router.push('/submit')">
            去投稿
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
/* 个人中心样式 */
.profile-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 主内容 */
.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

.profile-wrapper {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

/* 用户信息卡片 */
.user-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* 头像部分 */
.avatar-section {
  display: flex;
  justify-content: center;
}

.user-avatar-container {
  position: relative;
  display: inline-block;
}

.user-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-size: 2.5rem;
  font-weight: bold;
  text-transform: uppercase;
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  display: block;
}

/* 头像操作菜单 */
.avatar-actions-menu {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.75rem;
  min-width: 140px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.avatar-actions-menu .btn {
  width: 100%;
  margin: 0;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  text-align: center;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-block;
  text-decoration: none;
  min-width: 70px;
}

/* 用户卡片头部 */
.user-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-edit {
  background: #3498db;
  color: white;
}

.btn-edit:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-cancel {
  background: #95a5a6;
  color: white;
  margin-left: 0.5rem;
}

.btn-cancel:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
}

/* 头部操作按钮 */
.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* 更改密码按钮 */
.btn-password {
  background: #f39c12;
  color: white;
}

.btn-password:hover {
  background: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(243, 156, 18, 0.4);
}

/* 保存按钮 */
.btn-save {
  background: #2ecc71;
  color: white;
}

.btn-save:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

/* 主按钮 */
.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* 身份验证部分 */
.verification-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.verification-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.verification-form {
  max-width: 600px;
}

.password-input-group {
  display: flex;
  gap: 0.8rem;
  align-items: flex-end;
}

.password-input-group input {
  flex: 1;
}

.btn-verify {
  background: #3498db;
  color: white;
  padding: 0.8rem 1.5rem;
  align-self: flex-end;
}

.btn-verify:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.verification-status {
  margin-top: 1rem;
  padding: 0.8rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
}

.verification-status.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.verification-status.pending {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

/* 编辑部分标题 */
.edit-section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
}

/* 信息编辑和密码编辑区域 */
.info-edit-section,
.password-edit-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #2ecc71;
}

.password-edit-section {
  border-left-color: #f39c12;
}

/* 密码要求 */
.password-requirements {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
}

.requirement-item {
  margin: 0.5rem 0;
  color: #6c757d;
  list-style-type: none;
}

.requirement-item::before {
  content: '•';
  color: #6c757d;
  font-weight: bold;
  display: inline-block;
  width: 1rem;
  margin-left: -1rem;
}

/* 用户信息查看模式 */
.user-info {
  width: 100%;
}

.user-details {
  text-align: center;
}

.user-name {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.user-role {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin: 0 0 1.5rem 0;
  font-weight: 500;
}

.user-contact {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  align-items: center;
}

.user-contact p {
  margin: 0;
  font-size: 1rem;
  color: #555;
}

/* 用户信息编辑模式 */
.user-edit-form {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.form-group input {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 投稿记录部分 */
.journals-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #3498db;
}

.journals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.journal-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.journal-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.journal-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #3498db;
}

.journal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.journal-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 期刊状态 */
.journal-status {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.审稿中 {
  background: #3498db;
  color: white;
}

.journal-status.未通过 {
  background: #e74c3c;
  color: white;
}

/* 无投稿记录 */
.no-journals {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
}

/* 操作按钮 */
.profile-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 2rem;
}

/* 头像查看弹窗 */
.avatar-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;
  visibility: visible;
  transition: all 0.3s ease;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  position: relative;
  max-width: 90%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #2c3e50;
}

.avatar-preview-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  max-height: 80vh;
  overflow: auto;
}

.full-size-avatar {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.no-avatar-message {
  padding: 2rem;
  text-align: center;
  color: #7f8c8d;
}

/* 页脚 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .profile-wrapper {
    padding: 1.5rem;
  }
  
  .user-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .header-actions .btn {
    width: 100%;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    width: 100%;
  }
  
  .password-input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-verify {
    align-self: stretch;
  }
  
  .verification-section,
  .info-edit-section,
  .password-edit-section,
  .journals-section {
    padding: 1rem;
  }
  
  .profile-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .profile-actions .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .journal-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
}
</style>