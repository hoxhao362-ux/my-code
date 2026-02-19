<script setup>
import { ref, computed, reactive } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { validateEmail, validatePhone, encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()

// Edit State
const isEditing = ref(false)
const editForm = reactive({
  email: '',
  phone: ''
})
const errors = reactive({
  email: '',
  phone: ''
})

// Start Edit Mode
const startEdit = () => {
  editForm.email = userStore.user?.email || ''
  editForm.phone = userStore.user?.phone || ''
  isEditing.value = true
  showFullContactInfo.value = true // Auto-expand to show fields
}

// Cancel Edit Mode
const cancelEdit = () => {
  isEditing.value = false
  errors.email = ''
  errors.phone = ''
}

// Save Changes
const saveEdit = () => {
  // Reset errors
  errors.email = ''
  errors.phone = ''
  
  // Validate Email
  if (!validateEmail(editForm.email)) {
    errors.email = 'Invalid email format (e.g., xxx@journal.org)'
    return
  }
  
  // Validate Phone
  if (editForm.phone && !validatePhone(editForm.phone)) {
    errors.phone = 'Invalid phone number format'
    return
  }
  
  // Update Store (Mock update)
  userStore.updateUser({
    email: editForm.email,
    phone: editForm.phone
  })
  
  alert('Profile updated successfully')
  isEditing.value = false
}

// Validate on Blur
const validateField = (field) => {
  if (field === 'email') {
    if (!validateEmail(editForm.email)) {
      errors.email = 'Invalid email format (e.g., xxx@journal.org)'
    } else {
      errors.email = ''
    }
  }
  if (field === 'phone') {
    if (editForm.phone && !validatePhone(editForm.phone)) {
      errors.phone = 'Invalid phone number format'
    } else {
      errors.phone = ''
    }
  }
}

// 加密函数
const encryptEmail = (email) => {
  if (!email) return ''
  const [username, domain] = email.split('@')
  if (username.length <= 2) return `${username}@${domain}`
  return `${username.slice(0, 2)}${'*'.repeat(username.length - 2)}@${domain}`
}

const encryptPhone = (phone) => {
  if (!phone) return ''
  if (phone.length !== 11) return phone
  return `${phone.slice(0, 3)}${'*'.repeat(4)}${phone.slice(7)}`
}

// 头像弹窗状态
const showAvatarModal = ref(false)
const showAvatarActions = ref(false)
const fileInput = ref(null)
const formData = ref({})
const verificationData = ref({
  verifyPassword: '',
  isVerified: false
})

// 查看信息状态
const showFullContactInfo = ref(false)

// 切换查看信息状态
const toggleContactInfo = () => {
  showFullContactInfo.value = !showFullContactInfo.value
}

// 加密后的用户信息
const displayEmail = computed(() => {
  return encryptEmail(userStore.user?.email)
})

const displayPhone = computed(() => {
  return encryptPhone(userStore.user?.phone)
})

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
      alert('Please select an image file')
      return
    }
    
    // 检查文件大小（限制为5MB）
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size cannot exceed 5MB')
      return
    }
    
    // 读取文件并显示预览
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target.result
      // 更新用户头像
      formData.value.avatar = imageUrl
      userStore.updateUser({ avatar: imageUrl })
      alert('Avatar updated successfully')
    }
    reader.readAsDataURL(file)
    
    // 清空文件输入，允许再次选择同一个文件
    event.target.value = ''
  }
}

// 验证当前密码
const verifyPassword = () => {
  if (!verificationData.value.verifyPassword) {
    alert('Please enter current password')
    return
  }
  
  // 加密输入的密码进行验证
  const encryptedPassword = encryptPassword(verificationData.value.verifyPassword)
  
  // 验证密码是否正确
  if (encryptedPassword === userStore.user?.password) {
    verificationData.value.isVerified = true
  } else {
    alert('Current password incorrect')
    verificationData.value.isVerified = false
  }
}

</script>

<template>
  <div class="profile-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'author-profile'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
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
                  v-if="userStore.user?.avatar" 
                  :src="userStore.user.avatar" 
                  :alt="userStore.user.username"
                  class="avatar-image"
                />
                <span v-else>{{ userStore.user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
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
                  View Avatar
                </button>
                <button 
                  class="btn btn-password" 
                  @click="triggerFileSelect"
                >
                  Change Avatar
                </button>
              </div>
              
              <!-- 隐藏的文件输入控件 -->
              <input 
                type="file" 
                ref="fileInput"
                accept="image/*" 
                class="hidden-file-input" 
                @change="handleAvatarUpload"
              />
            </div>
          </div>
          
          <div class="user-card-header">
            <h3 class="card-title">Personal Information</h3>
            <div class="header-actions">
              <!-- Edit Actions -->
              <template v-if="isEditing">
                <button class="btn btn-save" @click="saveEdit">Save</button>
                <button class="btn btn-cancel" @click="cancelEdit">Cancel</button>
              </template>
              <template v-else>
                <button class="btn btn-edit" @click="startEdit">Edit</button>
                <button 
                  class="btn btn-view" 
                  @click="toggleContactInfo"
                >
                  {{ showFullContactInfo ? 'Hide Info' : 'View Info' }}
                </button>
              </template>
            </div>
          </div>
          
          <!-- 用户信息 -->
          <div class="user-info">
            <div class="user-details">
              <h2 class="user-name">{{ userStore.user?.username || 'Unknown User' }}</h2>
              <p class="user-role">
                {{ userStore.user?.role === 'admin' ? 'Admin' : 
                   userStore.user?.role === 'reviewer' ? 'Reviewer' : 
                   userStore.user?.role === 'author' ? 'Author' : 'User' }}
              </p>
              
              <!-- View Mode -->
              <div class="user-contact" v-if="!isEditing && showFullContactInfo">
                <p v-if="userStore.user?.email"><strong>Email:</strong> {{ encryptEmail(userStore.user.email) }}</p>
                <p v-if="userStore.user?.phone"><strong>Phone:</strong> {{ encryptPhone(userStore.user.phone) }}</p>
              </div>
              
              <!-- Edit Mode -->
              <div class="user-edit-form-inline" v-if="isEditing">
                 <div class="form-group-inline">
                   <label>Email</label>
                   <input 
                     type="email" 
                     v-model="editForm.email" 
                     @blur="validateField('email')"
                     :class="{ 'error-input': errors.email }"
                   />
                   <span class="error-text" v-if="errors.email">{{ errors.email }}</span>
                 </div>
                 <div class="form-group-inline">
                   <label>Phone</label>
                   <input 
                     type="tel" 
                     v-model="editForm.phone" 
                     @blur="validateField('phone')"
                     :class="{ 'error-input': errors.phone }"
                   />
                   <span class="error-text" v-if="errors.phone">{{ errors.phone }}</span>
                 </div>
              </div>
            </div>
          </div>
          
          <!-- 头像查看弹窗 -->
          <div 
            v-if="showAvatarModal" 
            class="avatar-modal" 
            :class="{ show: showAvatarModal }"
            @click="closeAvatarModal"
          >
            <div class="modal-content" @click.stop>
              <span class="close-btn" @click="closeAvatarModal">&times;</span>
              <div v-if="userStore.user?.avatar" class="avatar-preview-container">
                <img :src="userStore.user?.avatar" :alt="userStore.user?.username" class="full-size-avatar" />
              </div>
              <div v-else class="no-avatar-message">
                <p>No avatar uploaded</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Inline Edit Styles */
.user-edit-form-inline {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
  max-width: 400px;
  margin: 10px auto 0;
}

.form-group-inline {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.form-group-inline label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #555;
  font-size: 0.9rem;
}

.form-group-inline input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group-inline input.error-input {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 4px;
}

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

.profile-content.embedded-content {
  margin-top: 0;
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
  z-index: 10;
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

.btn-view {
  background: #2ecc71;
  color: white;
}

.btn-view:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
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

/* 密码操作区域 */
.password-action {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
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
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 1000;
}

.avatar-modal.show {
  opacity: 1;
  visibility: visible;
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
  .password-edit-section {
    padding: 1rem;
  }
}
</style>