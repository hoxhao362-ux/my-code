<script setup>
import { ref, onMounted, watch, computed } from 'vue'

const props = defineProps({
  user: Object,
  navigateTo: Function,
  adminCode: String,
  updateAdminCode: Function,
  updateUser: Function,
  modules: Array,
  updateModules: Function,
  addModule: Function,
  removeModule: Function,
  journals: Array
})

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

// 查看信息状态
const showFullContactInfo = ref(false)

// 切换查看信息状态
const toggleContactInfo = () => {
  showFullContactInfo.value = !showFullContactInfo.value
}

// 管理员密码设置
const adminCodeForm = ref({
  currentCode: '',
  newCode: '',
  confirmCode: ''
})
const adminCodeError = ref('')
const adminCodeSuccess = ref('')

// 模块管理
const moduleForm = ref({
  newModule: ''
})
const moduleError = ref('')
const moduleSuccess = ref('')

// 头像弹窗状态
const showAvatarModal = ref(false)

// 投稿历史筛选状态
const selectedModule = ref('all')
const timeRange = ref('all')
const isExpanded = ref(false)

// 用户投稿历史筛选
const userSubmissions = computed(() => {
  if (!props.user || !props.journals) return []
  
  let filtered = props.journals.filter(journal => journal.author === props.user.username)
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    filtered = filtered.filter(journal => journal.module === selectedModule.value)
  }
  
  // 时间范围筛选
  const now = new Date()
  let startDate
  switch (timeRange.value) {
    case 'today':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      break
    case 'week':
      startDate = new Date(now.setDate(now.getDate() - 7))
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
      break
    case 'year':
      startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
      break
    default:
      startDate = null
  }
  
  if (startDate) {
    filtered = filtered.filter(journal => new Date(journal.date) >= startDate)
  }
  
  // 按时间降序排序
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

// 显示的投稿列表（最近3篇或全部）
const displayedSubmissions = computed(() => {
  if (isExpanded.value) {
    return userSubmissions.value
  } else {
    return userSubmissions.value.slice(0, 3)
  }
})

const goBack = () => {
  props.navigateTo('home')
}

const viewJournalDetail = (id) => {
  props.navigateTo('journal', id)
}

const handleLogout = () => {
  props.navigateTo('login')
}

// 查看头像
const viewAvatar = () => {
  showAvatarModal.value = true
}

// 关闭头像查看弹窗
const closeAvatarModal = () => {
  showAvatarModal.value = false
}

// 保存管理员辨识密码
const saveAdminCode = () => {
  // 重置消息
  adminCodeError.value = ''
  adminCodeSuccess.value = ''
  
  // 验证当前密码是否正确
  if (adminCodeForm.value.currentCode !== props.adminCode) {
    adminCodeError.value = '当前密码不正确'
    return
  }
  
  // 验证新密码和确认密码是否一致
  if (adminCodeForm.value.newCode !== adminCodeForm.value.confirmCode) {
    adminCodeError.value = '两次输入的新密码不一致'
    return
  }
  
  // 验证新密码不能为空
  if (!adminCodeForm.value.newCode) {
    adminCodeError.value = '新密码不能为空'
    return
  }
  
  // 更新管理员密码
  props.updateAdminCode(adminCodeForm.value.newCode)
  
  // 显示成功消息
  adminCodeSuccess.value = '管理员密码已成功更新'
  
  // 重置表单
  adminCodeForm.value = {
    currentCode: '',
    newCode: '',
    confirmCode: ''
  }
  
  // 3秒后清除成功消息
  setTimeout(() => {
    adminCodeSuccess.value = ''
  }, 3000)
}

// 添加模块
const handleAddModule = () => {
  // 重置消息
  moduleError.value = ''
  moduleSuccess.value = ''
  
  // 验证模块名不能为空
  if (!moduleForm.value.newModule.trim()) {
    moduleError.value = '模块名不能为空'
    return
  }
  
  // 验证模块名是否已存在
  if (props.modules.includes(moduleForm.value.newModule.trim())) {
    moduleError.value = '该模块已存在'
    return
  }
  
  // 添加模块
  props.addModule(moduleForm.value.newModule.trim())
  
  // 显示成功消息
  moduleSuccess.value = '模块已成功添加'
  
  // 重置表单
  moduleForm.value.newModule = ''
  
  // 3秒后清除成功消息
  setTimeout(() => {
    moduleSuccess.value = ''
  }, 3000)
}

// 删除模块
const handleRemoveModule = (moduleName) => {
  // 确认删除
  if (confirm(`确定要删除模块 "${moduleName}" 吗？`)) {
    props.removeModule(moduleName)
    moduleSuccess.value = '模块已成功删除'
    
    // 3秒后清除成功消息
    setTimeout(() => {
      moduleSuccess.value = ''
    }, 3000)
  }
}
</script>

<template>
  <div class="profile-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>Peerex Peer</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goBack">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 个人中心内容 -->
    <main class="profile-content">
      <div class="profile-wrapper">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <!-- 头像位置 - 左上角 -->
          <div class="avatar-section">
            <div 
              class="user-avatar" 
              @click="viewAvatar"
            >
              <img 
                v-if="user?.avatar" 
                :src="user.avatar" 
                :alt="user.username"
                class="avatar-image"
              />
              <span v-else>{{ user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
              <!-- 悬停时显示操作提示 -->
              <div class="avatar-tooltip">点击查看大图</div>
            </div>
          </div>
          
          <div class="user-card-header">
            <h3 class="card-title">个人信息</h3>
            <div class="header-actions">
              <!-- 只显示查看信息按钮 -->
              <button 
                class="btn btn-view" 
                @click="toggleContactInfo"
              >
                {{ showFullContactInfo ? '隐藏信息' : '查看信息' }}
              </button>
            </div>
          </div>
          
          <!-- 用户信息 -->
          <div class="user-info">
            <div class="user-details">
              <h2 class="user-name">{{ user?.username || '未知用户' }}</h2>
              <p class="user-role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
              <div class="user-contact" v-if="showFullContactInfo">
                <p v-if="user?.email"><strong>邮箱：</strong>{{ encryptEmail(user.email) }}</p>
                <p v-if="user?.phone"><strong>手机号：</strong>{{ encryptPhone(user.phone) }}</p>
              </div>
            </div>
          </div>
          
          <!-- 隐藏的文件输入框 -->
          <input 
            type="file" 
            id="avatar-file" 
            accept="image/*"
            class="file-input"
            @change="handleAvatarUpload"
            ref="fileInput"
          />
          
          <!-- 头像查看弹窗 -->
          <div 
            v-if="showAvatarModal" 
            class="avatar-modal" 
            :class="{ show: showAvatarModal }"
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
        </div>

        <!-- 投稿历史 -->
        <div class="submission-section">
          <h3 class="section-title">投稿历史</h3>
          
          <!-- 筛选控件 -->
          <div class="submission-filters">
            <label for="module-filter">模块筛选：</label>
            <select 
              id="module-filter" 
              v-model="selectedModule"
              class="filter-select"
            >
              <option value="all">全部模块</option>
              <option 
                v-for="module in props.modules" 
                :key="module"
                :value="module"
              >
                {{ module }}
              </option>
            </select>
            
            <label for="time-filter">时间范围：</label>
            <select 
              id="time-filter" 
              v-model="timeRange"
              class="filter-select"
            >
              <option value="all">全部时间</option>
              <option value="today">今日</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="year">本年</option>
            </select>
          </div>
          
          <div v-if="userSubmissions.length > 0" class="submission-list">
            <div 
              v-for="submission in displayedSubmissions" 
              :key="submission.id" 
              class="submission-item"
            >
              <div class="submission-info">
                <h4 class="submission-title" @click="viewJournalDetail(submission.id)">{{ submission.title }}</h4>
                <p class="submission-meta">投稿日期：{{ submission.date }} | 模块：{{ submission.module }}</p>
              </div>
              <div class="submission-status" :class="submission.status.toLowerCase()">
                {{ submission.status }}
              </div>
            </div>
            
            <!-- 展开/收起按钮 -->
            <div v-if="userSubmissions.length > 3" class="expand-section">
              <button 
                class="btn btn-expand" 
                @click="isExpanded = !isExpanded"
              >
                {{ isExpanded ? '收起' : `展开全部（共${userSubmissions.length}篇）` }}
              </button>
            </div>
          </div>
          
          <div v-else class="no-submissions">
            <p>您还没有投稿记录</p>
          </div>
        </div>

        <!-- 管理员设置（仅管理员可见） -->
        <div v-if="user?.role === 'admin'" class="admin-settings">
          <div class="admin-card">
            <h3 class="section-title">管理员设置</h3>
            
            <div class="admin-code-section">
              <h4>管理员辨识密码设置</h4>
              <p class="setting-description">设置用户注册时的管理员辨识密码，用于区分管理员和普通用户</p>
              
              <div class="admin-code-form">
                <div class="form-row">
                  <div class="form-group">
                    <label for="currentCode">当前密码</label>
                    <input 
                      type="password" 
                      id="currentCode" 
                      v-model="adminCodeForm.currentCode"
                      placeholder="请输入当前管理员密码"
                    />
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="newCode">新密码</label>
                    <input 
                      type="password" 
                      id="newCode" 
                      v-model="adminCodeForm.newCode"
                      placeholder="请输入新的管理员密码"
                    />
                  </div>
                  
                  <div class="form-group">
                    <label for="confirmCode">确认密码</label>
                    <input 
                      type="password" 
                      id="confirmCode" 
                      v-model="adminCodeForm.confirmCode"
                      placeholder="请再次输入新密码"
                    />
                  </div>
                </div>
                
                <!-- 错误和成功消息 -->
                <div v-if="adminCodeError" class="error-message">{{ adminCodeError }}</div>
                <div v-if="adminCodeSuccess" class="success-message">{{ adminCodeSuccess }}</div>
                
                <!-- 保存按钮 -->
                <div class="save-admin-code">
                  <button class="btn btn-primary" @click="saveAdminCode">
                    保存管理员密码
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 模块管理 -->
            <div class="module-management-section">
              <h4>期刊模块管理</h4>
              <p class="setting-description">管理期刊的模块分类，用户投稿时可以选择所属模块</p>
              
              <!-- 错误和成功消息 -->
              <div v-if="moduleError" class="error-message">{{ moduleError }}</div>
              <div v-if="moduleSuccess" class="success-message">{{ moduleSuccess }}</div>
              
              <!-- 添加模块 -->
              <div class="add-module-section">
                <div class="form-row">
                  <div class="form-group">
                    <label for="newModule">添加新模块</label>
                    <input 
                      type="text" 
                      id="newModule" 
                      v-model="moduleForm.newModule"
                      placeholder="请输入模块名称"
                    />
                  </div>
                  <div class="form-group add-module-btn-container">
                    <label>&nbsp;</label>
                    <button class="btn btn-primary" @click="handleAddModule">
                      添加模块
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 模块列表 -->
              <div class="module-list-section">
                <h5>现有模块</h5>
                <div class="module-list">
                  <div 
                    v-for="module in modules" 
                    :key="module" 
                    class="module-item"
                  >
                    <span class="module-name">{{ module }}</span>
                    <button 
                      v-if="module !== '其他'" 
                      class="btn btn-delete"
                      @click="handleRemoveModule(module)"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="btn btn-primary" @click="navigateTo('submit')">
            + 新投稿
          </button>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.profile-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 导航栏样式（与其他页面保持一致） */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.8rem;
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
  margin-left: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #3498db;
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
}

/* 个人中心内容 */
.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.profile-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 用户信息卡片 */
.user-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-card {
  position: relative;
  padding-top: 5rem;
}

/* 头像区域样式 */
.avatar-section {
  position: absolute;
  top: -3rem;
  left: 2rem;
  z-index: 10;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2.5rem;
  font-weight: bold;
  overflow: hidden;
  cursor: pointer;
  border: 4px solid white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  position: relative;
}

.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.avatar-tooltip {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 15;
}

.user-avatar:hover .avatar-tooltip {
  opacity: 1;
  visibility: visible;
  bottom: -35px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 头像菜单样式 */
.avatar-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  min-width: 150px;
  z-index: 20;
}

.avatar-menu ul {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
}

.avatar-menu li {
  padding: 0.8rem 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #333;
}

.avatar-menu li:hover {
  background: #f8f9fa;
  color: #3498db;
}

/* 头像查看弹窗样式 */
.avatar-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.avatar-modal.show {
  opacity: 1;
  visibility: visible;
}

.modal-content {
  position: relative;
  background: transparent;
  padding: 0;
  border-radius: 10px;
  max-width: 95%;
  max-height: 95%;
  overflow: visible;
  transition: transform 0.3s ease;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 30px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.avatar-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 200px;
  min-height: 200px;
}

.full-size-avatar {
  max-width: 90vw;
  max-height: 90vh;
  display: block;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
}

.no-avatar-message {
  text-align: center;
  color: white;
  font-size: 1.2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

/* 用户信息卡片头部 */
.user-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.user-info {
  margin-top: 1rem;
}

.card-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.btn-view {
  background: #2ecc71;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 0.5rem;
}

.btn-view:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

.btn-edit {
  background: #3498db;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-cancel {
  background: #95a5a6;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 0;
}

.btn-cancel:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.user-role {
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
}

.user-contact {
  margin-top: 0.5rem;
}

.user-contact p {
  margin: 0.25rem 0;
  color: #555;
  font-size: 0.95rem;
}

/* 编辑表单样式 */
.user-edit-form {
  padding: 1rem 0;
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
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 文件输入框隐藏 */
.file-input {
  display: none;
}

/* 头像上传样式 */
.avatar-upload-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.avatar-upload-btn {
  background: #95a5a6;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-block;
  width: fit-content;
}

.avatar-upload-btn:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
}

.avatar-upload-hint {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-style: italic;
}

/* 投稿历史 */
.submission-section {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
}

.submission-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.submission-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.submission-info {
  flex: 1;
}

.submission-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.submission-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.submission-meta {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
}

.submission-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.submission-status.待审核 {
  background: #fff3cd;
  color: #856404;
}

.submission-status.审核中 {
  background: #cce7ff;
  color: #004085;
}

.submission-status.已通过 {
  background: #d4edda;
  color: #155724;
}

.submission-status.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

.no-submissions {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

/* 投稿历史筛选样式 */
.submission-filters {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 0.8rem 1.2rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #eee;
  width: 100%;
  box-sizing: border-box;
  overflow: visible;
  flex-wrap: wrap;
}

.submission-filters label {
  font-weight: 500;
  color: #555;
  font-size: 0.85rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.submission-filters .filter-select {
  padding: 0.5rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
  min-width: 120px;
  flex-shrink: 0;
  display: block;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 展开/收起按钮样式 */
.expand-section {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn-expand {
  background: #f0f2f5;
  color: #333;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-expand:hover {
  background: #e4e6eb;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* 管理员设置样式 */
.admin-settings {
  margin-top: 2rem;
}

.admin-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.admin-code-section {
  margin-top: 1.5rem;
}

.admin-code-section h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.setting-description {
  color: #7f8c8d;
  font-size: 0.95rem;
  margin: 0 0 1.5rem 0;
}

.admin-code-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #eee;
}

.save-admin-code {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.error-message {
  color: #e74c3c;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.success-message {
  color: #27ae60;
  margin: 1rem 0;
  font-size: 0.9rem;
}

/* 模块管理样式 */
.module-management-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.module-management-section h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.module-management-section h5 {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 1.5rem 0 1rem 0;
}

.add-module-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #eee;
  margin-bottom: 1.5rem;
}

.add-module-btn-container {
  display: flex;
  align-items: flex-end;
}

.module-list-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #eee;
}

.module-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.module-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.module-name {
  font-weight: 500;
  color: #2c3e50;
}

.btn-delete {
  background: #e74c3c;
  color: white;
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-delete:hover {
  background: #c0392b;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(231, 76, 60, 0.4);
}

/* 页脚样式 */
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
</style>
