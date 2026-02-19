<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import SensitiveOperationVerification from '../../components/SensitiveOperationVerification.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

// 邮箱加密函数
const encryptEmail = (email) => {
  if (!email) return ''
  const [username, domain] = email.split('@')
  if (username.length <= 2) return `${username}@${domain}`
  return `${username.slice(0, 2)}${'*'.repeat(username.length - 2)}@${domain}`
}

// 手机号加密函数
const encryptPhone = (phone) => {
  if (!phone) return ''
  if (phone.length !== 11) return phone
  return `${phone.slice(0, 3)}${'*'.repeat(4)}${phone.slice(7)}`
}

// 模拟投稿记录数据
const submissionRecords = ref([
  { id: 1, userId: 3, title: '基于深度学习的医学图像分析', date: '2025-12-30', status: '已通过' },
  { id: 2, userId: 7, title: '新型冠状病毒疫苗研发进展', date: '2025-12-28', status: '已通过' },
  { id: 3, userId: 8, title: '临床路径管理在医院中的应用研究', date: '2025-12-25', status: '审稿中' },
  { id: 4, userId: 12, title: '公共卫生应急管理体系建设', date: '2025-12-20', status: '已通过' },
  { id: 5, userId: 3, title: '基因组学数据分析方法研究', date: '2025-12-15', status: '未通过' },
  { id: 6, userId: 4, title: '人工智能辅助诊断系统的设计与实现', date: '2025-12-10', status: '已通过' },
  { id: 7, userId: 7, title: '医学图像处理技术研究进展', date: '2025-11-30', status: '已通过' }
])

// 模拟审稿记录数据
const reviewRecords = ref([
  { id: 1, userId: 2, journalId: 1, title: '基于深度学习的医学图像分析', date: '2026-01-05', result: '通过' },
  { id: 2, userId: 2, journalId: 2, title: '新型冠状病毒疫苗研发进展', date: '2026-01-04', result: '通过' },
  { id: 3, userId: 6, journalId: 3, title: '临床路径管理在医院中的应用研究', date: '2026-01-03', result: '待处理' },
  { id: 4, userId: 10, journalId: 4, title: '公共卫生应急管理体系建设', date: '2026-01-02', result: '通过' },
  { id: 5, userId: 6, journalId: 5, title: '基因组学数据分析方法研究', date: '2026-01-01', result: '未通过' },
  { id: 6, userId: 1, journalId: 6, title: '人工智能辅助诊断系统的设计与实现', date: '2025-12-31', result: '通过' },
  { id: 7, userId: 10, journalId: 7, title: '医学图像处理技术研究进展', date: '2025-12-30', result: '通过' }
])

// 信息检索功能
const searchKeyword = ref('')
const roleFilter = ref('all')
const statusFilter = ref('all')

// 计算过滤后的用户列表
const filteredUsers = computed(() => {
  return userStore.users.filter(user => {
    // 关键词搜索
    const matchesKeyword = !searchKeyword.value || 
      user.username.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      user.email.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      user.phone.includes(searchKeyword.value)
    
    // 角色过滤
    const matchesRole = roleFilter.value === 'all' || user.role === roleFilter.value
    
    // 状态过滤
    const matchesStatus = statusFilter.value === 'all' || user.status === statusFilter.value
    
    return matchesKeyword && matchesRole && matchesStatus
  })
})

// 角色选项
const roleOptions = [
  { value: 'all', label: 'All Roles' },
  { value: 'admin', label: 'Admin (EIC)' },
  { value: 'editor', label: 'Editor' },
  { value: 'associate_editor', label: 'Associate Editor' },
  { value: 'editorial_assistant', label: 'Editorial Assistant' },
  { value: 'advisory_editor', label: 'Advisory Editor' },
  { value: 'reviewer', label: 'Reviewer' },
  { value: 'author', label: 'Author' },
  { value: 'user', label: 'User' }
]

// 状态选项
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' }
]

// 清空筛选
const clearFilters = () => {
  searchKeyword.value = ''
  roleFilter.value = 'all'
  statusFilter.value = 'all'
}

// 模态框状态管理
const showViewModal = ref(false)
const showEditModal = ref(false)
const showDisableModal = ref(false)
const showDeleteModal = ref(false)
const showConfirmModal = ref(false)
const showVerification = ref(false)
const verificationAction = ref('')
const verificationTarget = ref('')
const pendingCallback = ref(null)

// 当前操作的用户
const currentUser = ref(null)

// 编辑表单数据
const editForm = ref({
  role: '',
  resetPassword: false
})

// 禁用时长选项
const disableDurations = [
  { value: 1, label: '1 Day' },
  { value: 7, label: '7 Days' },
  { value: 30, label: '30 Days' },
  { value: 90, label: '90 Days' },
  { value: 0, label: 'Permanent' }
]

const disableForm = ref({
  duration: 7,
  reason: ''
})

// 管理员密码确认
const adminPassword = ref('')
const confirmAction = ref(null)
const confirmMessage = ref('')

// 获取用户的投稿记录
const getUserSubmissions = (userId) => {
  return submissionRecords.value.filter(record => record.userId === userId)
}

// 获取用户的审稿记录
const getUserReviews = (userId) => {
  return reviewRecords.value.filter(record => record.userId === userId)
}

// 查看用户信息
const viewUser = (user) => {
  currentUser.value = user
  showViewModal.value = true
}

// 编辑用户
const editUser = (user) => {
  currentUser.value = user
  editForm.value = {
    role: user.role,
    resetPassword: false
  }
  showEditModal.value = true
}

// 禁用用户
const disableUser = (user) => {
  currentUser.value = user
  disableForm.value = {
    duration: 7,
    reason: ''
  }
  showDisableModal.value = true
}

// 删除用户
const deleteUser = (user) => {
  currentUser.value = user
  showDeleteModal.value = true
}

// 打开确认模态框
const openConfirmModal = (action, message) => {
  confirmAction.value = action
  confirmMessage.value = message
  adminPassword.value = ''
  showConfirmModal.value = true
}

// 确认操作
const confirmOperation = () => {
  // 这里应该验证管理员密码，目前模拟验证
  if (adminPassword.value === 'admin123') {
    confirmAction.value()
    showConfirmModal.value = false
  } else {
    alert('Invalid admin password!')
  }
}

// 验证成功回调
const handleVerificationSuccess = () => {
  if (pendingCallback.value) {
    pendingCallback.value()
    pendingCallback.value = null
  }
}

// 执行编辑操作
const executeEdit = () => {
  // Check if role is changing from User to Admin - Warning
  let warning = 'Are you sure you want to update this user?'
  let isSensitive = false
  
  if (currentUser.value.role !== 'admin' && editForm.value.role === 'admin') {
     warning = 'Are you sure to set this user as Administrator?'
     isSensitive = true
  }

  const action = () => {
    if (editForm.value.resetPassword) {
      // 重置密码逻辑
      alert(`Password reset for user ${currentUser.value.username} to: 123456`)
    }
    if (editForm.value.role !== currentUser.value.role) {
      // 角色变更逻辑 - 使用userStore更新角色，确保持久化
      userStore.updateUserRole(currentUser.value.id, editForm.value.role)
      // 更新当前用户对象，确保模态框显示正确
      currentUser.value.role = editForm.value.role
      const roleName = editForm.value.role === 'editor' ? 'Editor' : 
                       editForm.value.role === 'reviewer' ? 'Reviewer' : 
                       editForm.value.role === 'author' ? 'Author' : 'User'
      alert(`User ${currentUser.value.username} role updated to ${roleName}`)
    }
    showEditModal.value = false
  }

  if (isSensitive) {
    // 敏感操作，触发二次验证
    verificationAction.value = 'Upgrade to Administrator'
    verificationTarget.value = currentUser.value.username
    pendingCallback.value = action
    showVerification.value = true
  } else {
    // 普通操作，使用原有确认
    openConfirmModal(action, warning)
  }
}

// 执行禁用操作
const executeDisable = () => {
  const action = () => {
    // 禁用用户逻辑 - 使用userStore更新状态，确保持久化
    userStore.updateUserStatus(currentUser.value.id, 'inactive')
    // 更新当前用户对象，确保模态框显示正确
    currentUser.value.status = 'inactive'
    const durationText = disableForm.value.duration === 0 ? 'Permanent' : `${disableForm.value.duration} days`
    alert(`User ${currentUser.value.username} disabled for: ${durationText}`)
    showDisableModal.value = false
  }

  // 禁用用户也是敏感操作
  verificationAction.value = 'Disable User Account'
  verificationTarget.value = currentUser.value.username
  pendingCallback.value = action
  showVerification.value = true
}

// 执行删除操作
const executeDelete = () => {
  const action = () => {
    // 删除用户逻辑 - 使用userStore删除用户，确保持久化
    userStore.deleteUser(currentUser.value.id)
    alert(`User ${currentUser.value.username} deleted`)
    showDeleteModal.value = false
  }
  
  // 删除也是敏感操作
  verificationAction.value = 'Delete User'
  verificationTarget.value = currentUser.value.username
  pendingCallback.value = action
  showVerification.value = true
}

// 启用用户
const enableUser = (user) => {
  openConfirmModal(() => {
    // 启用用户逻辑 - 使用userStore更新状态，确保持久化
    userStore.updateUserStatus(user.id, 'active')
    // 更新当前用户对象，确保界面显示正确
    user.status = 'active'
    alert(`User ${user.username} enabled`)
  }, 'Are you sure you want to enable this user?')
}
</script>

<template>
  <div class="admin-users-container">
    <!-- 导航栏 -->
    <Navigation 
      v-if="!embedded"
      :user="user"
      :current-page="'admin-users'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 用户管理内容 -->
    <main class="content" :class="{ 'embedded-content': embedded }">
      <div class="header">
        <h1>User Management</h1>
        <p class="subtitle">Manage all users, view, edit, disable or delete accounts</p>
      </div>

      <!-- 信息检索和筛选 -->
      <section class="search-filter-section">
        <div class="search-filter-container">
          <!-- 搜索输入框 -->
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchKeyword" 
              placeholder="Search by username, email or phone..." 
              class="search-input"
            >
            <button class="search-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            </button>
          </div>
          
          <!-- 筛选条件 -->
          <div class="filter-container">
            <div class="filter-group">
              <label for="roleFilter">角色筛选</label>
              <select id="roleFilter" name="roleFilter" v-model="roleFilter" class="filter-select">
                <option 
                  v-for="option in roleOptions" 
                  :key="option.value" 
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="statusFilter">状态筛选</label>
              <select id="statusFilter" name="statusFilter" v-model="statusFilter" class="filter-select">
                <option 
                  v-for="option in statusOptions" 
                  :key="option.value" 
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
            
            <button @click="clearFilters" class="clear-btn">
              清空筛选
            </button>
          </div>
        </div>
      </section>

      <!-- 用户统计信息 -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-number">{{ userStore.users.length }}</div>
            <div class="stat-label">Total Normals</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ userStore.users.filter(u => u.status === 'active').length }}</div>
            <div class="stat-label">Active Normals</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ userStore.users.filter(u => u.role === 'reviewer').length }}</div>
            <div class="stat-label">Reviewers</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ userStore.users.filter(u => u.role === 'author').length }}</div>
            <div class="stat-label">Writers</div>
          </div>
        </div>
      </section>

      <!-- 用户列表 -->
      <section class="users-section">
        <div class="users-table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>邮箱</th>
                <th>手机号</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
                <td class="user-id">{{ user.id }}</td>
                <td class="user-username">{{ user.username }}</td>
                <td>
                  <span class="role-badge" :class="user.role">
                    {{ user.role === 'admin' ? 'Admin' : 
                       user.role === 'editor' ? 'Editor' :
                       user.role === 'associate_editor' ? 'Associate Editor' :
                       user.role === 'editorial_assistant' ? 'Editorial Assistant' :
                       user.role === 'advisory_editor' ? 'Advisory Editor' :
                       user.role === 'reviewer' ? 'Reviewer' : 
                       user.role === 'author' ? 'Author' : 'User' }}
                  </span>
                </td>
                <td class="user-email">{{ encryptEmail(user.email) }}</td>
                <td class="user-phone">{{ encryptPhone(user.phone) }}</td>
                <td>
                  <span class="status-badge" :class="user.status">
                    {{ user.status === 'active' ? '启用' : '禁用' }}
                  </span>
                </td>
                <td class="action-column">
                  <button class="action-btn view-btn" @click="viewUser(user)">查看</button>
                  <button class="action-btn edit-btn" @click="editUser(user)">编辑</button>
                  <button 
                    class="action-btn status-btn" 
                    @click="user.status === 'active' ? disableUser(user) : enableUser(user)"
                  >
                    {{ user.status === 'active' ? '禁用' : '启用' }}
                  </button>
                  <button class="action-btn delete-btn" @click="deleteUser(user)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- 空状态提示 -->
          <div v-if="filteredUsers.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm5.5 3a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm-3-8a1 1 0 0 1 1-1h1a1 1 0 1 1 0 2H3.5a1 1 0 0 1-1-1zm8 7a1 1 0 1 0 0-2h-1a1 1 0 1 0 0 2h1z"/>
            </svg>
            <p>No matching users found</p>
            <button @click="clearFilters" class="empty-action-btn">
              Clear Filters
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- 查看用户信息模态框 -->
    <div v-if="showViewModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>User Information</h2>
          <button class="close-btn" @click="showViewModal = false">×</button>
        </div>
        <div class="modal-content">
          <div class="user-info-section">
            <h3>Personal Information</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Username:</span>
                <span class="info-value">{{ currentUser?.username }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Role:</span>
                <span class="info-value">{{ currentUser?.role === 'admin' ? 'Editor' : currentUser?.role === 'reviewer' ? 'Reviewer' : currentUser?.role === 'author' ? 'Author' : 'User' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Email:</span>
                <span class="info-value">{{ currentUser?.email }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Phone:</span>
                <span class="info-value">{{ currentUser?.phone }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Status:</span>
                <span class="info-value">{{ currentUser?.status === 'active' ? 'Active' : 'Inactive' }}</span>
              </div>
            </div>
          </div>
          
          <!-- 投稿记录 -->
          <div class="records-section" v-if="(currentUser?.role === 'user' || currentUser?.role === 'author') && getUserSubmissions(currentUser?.id).length > 0">
            <h3>Submission History</h3>
            <div class="records-table-container">
              <table class="records-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in getUserSubmissions(currentUser?.id)" :key="record.id">
                    <td class="record-title">{{ record.title }}</td>
                    <td>{{ record.date }}</td>
                    <td>{{ record.status }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- 审稿记录 -->
          <div class="records-section" v-if="(currentUser?.role === 'editor' || currentUser?.role === 'reviewer') && getUserReviews(currentUser?.id).length > 0">
            <h3>Review History</h3>
            <div class="records-table-container">
              <table class="records-table">
                <thead>
                  <tr>
                    <th>Manuscript</th>
                    <th>Date</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in getUserReviews(currentUser?.id)" :key="record.id">
                    <td class="record-title">{{ record.title }}</td>
                    <td>{{ record.date }}</td>
                    <td>{{ record.result }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn close-modal" @click="showViewModal = false">Close</button>
        </div>
      </div>
    </div>
    
    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Edit User</h2>
          <button class="close-btn" @click="showEditModal = false">×</button>
        </div>
        <div class="modal-content">
          <div class="edit-form">
            <div class="form-group">
              <label for="username">Username</label>
              <input type="text" id="username" name="username" :value="currentUser?.username" disabled class="disabled-input">
            </div>
            <div class="form-group">
              <label for="editRole">Role</label>
              <select id="editRole" name="editRole" v-model="editForm.role" class="form-control">
                <option value="admin">Admin</option>
                <option value="editor">Editor</option>
                <option value="associate_editor">Associate Editor</option>
                <option value="editorial_assistant">Editorial Assistant</option>
                <option value="advisory_editor">Advisory Editor</option>
                <option value="reviewer">Reviewer</option>
                <option value="author">Author</option>
                <option value="user">User</option>
              </select>
            </div>
            <div class="form-group checkbox-group">
              <input type="checkbox" id="resetPassword" v-model="editForm.resetPassword">
              <label for="resetPassword">Reset password to default (123456)</label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn close-modal" @click="showEditModal = false">Cancel</button>
          <button class="modal-btn confirm-modal" @click="executeEdit">Confirm</button>
        </div>
      </div>
    </div>
    
    <!-- 禁用用户模态框 -->
    <div v-if="showDisableModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Disable User</h2>
          <button class="close-btn" @click="showDisableModal = false">×</button>
        </div>
        <div class="modal-content">
          <p class="warning-text">Are you sure you want to disable <strong>{{ currentUser?.username }}</strong>?</p>
          <div class="disable-form">
            <div class="form-group">
              <label for="disableDuration">Duration</label>
              <select id="disableDuration" name="disableDuration" v-model="disableForm.duration" class="form-control">
                <option 
                  v-for="duration in disableDurations" 
                  :key="duration.value" 
                  :value="duration.value"
                >
                  {{ duration.label }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="disableReason">Reason</label>
              <textarea 
                id="disableReason" 
                name="disableReason" 
                v-model="disableForm.reason" 
                class="form-control" 
                rows="3" 
                placeholder="Reason for disabling..."
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn close-modal" @click="showDisableModal = false">Cancel</button>
          <button class="modal-btn confirm-modal" @click="executeDisable">Confirm</button>
        </div>
      </div>
    </div>
    
    <!-- 删除用户模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Delete User</h2>
          <button class="close-btn" @click="showDeleteModal = false">×</button>
        </div>
        <div class="modal-content">
          <p class="danger-text">Warning: Deleting <strong>{{ currentUser?.username }}</strong> will permanently remove all their data. This cannot be undone!</p>
          <p class="danger-text">Are you sure you want to proceed?</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn close-modal" @click="showDeleteModal = false">Cancel</button>
          <button class="modal-btn delete-modal" @click="executeDelete">Delete</button>
        </div>
      </div>
    </div>
    
    <!-- 管理员密码确认模态框 -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Admin Confirmation</h2>
          <button class="close-btn" @click="showConfirmModal = false">×</button>
        </div>
        <div class="modal-content">
          <p>{{ confirmMessage }}</p>
          <div class="form-group">
            <label for="adminPassword">Enter Admin Password:</label>
            <input type="password" id="adminPassword" name="adminPassword" v-model="adminPassword" class="form-control" placeholder="Admin Password">
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn close-modal" @click="showConfirmModal = false">Cancel</button>
          <button class="modal-btn confirm-modal" @click="confirmOperation">Confirm</button>
        </div>
      </div>
    </div>
    
    <!-- 敏感操作验证 -->
    <SensitiveOperationVerification
      :visible="showVerification"
      :action-type="verificationAction"
      :target="verificationTarget"
      @close="showVerification = false"
      @verify-success="handleVerificationSuccess"
    />
    
    <!-- 页脚 -->
    <footer class="footer" v-if="!embedded">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.admin-users-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.content.embedded-content {
  margin-top: 0;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 搜索筛选区域样式 */
.search-filter-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.search-filter-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 搜索框样式 */
.search-box {
  display: flex;
  gap: 0.5rem;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 0.9rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-btn {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* 筛选容器样式 */
.filter-container {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #555;
}

.filter-select {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: white;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 清空筛选按钮 */
.clear-btn {
  background-color: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.8rem 1.5rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-end;
}

.clear-btn:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

/* 统计信息区域样式 */
.stats-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.9;
  text-align: center;
}

/* 第三个统计卡片样式 - 审核员 */
.stat-container > div:nth-child(3) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* 第四个统计卡片样式 - 作者 */
.stat-container > div:nth-child(4) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

/* 用户列表区域样式 */
.users-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.users-table-container {
  overflow-x: auto;
}

/* 表格样式 */
.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  background-color: white;
}

.users-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 10;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
}

/* 用户行样式 */
.user-row {
  transition: all 0.3s ease;
}

.user-row:hover {
  background-color: #f8f9fa;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 角色徽章样式 */
.role-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.admin {
  background-color: #ff6b6b;
  color: white;
}

.role-badge.reviewer {
  background-color: #4ecdc4;
  color: white;
}

.role-badge.author {
  background-color: #45b7d1;
  color: white;
}

.role-badge.user {
  background-color: #a8e6cf;
  color: #2c3e50;
}

/* 状态徽章样式 */
.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

/* 操作按钮样式 */
.action-column {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 70px;
}

.view-btn {
  background-color: #3498db;
  color: white;
}

.view-btn:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(52, 152, 219, 0.3);
}

.edit-btn {
  background-color: #2ecc71;
  color: white;
}

.edit-btn:hover {
  background-color: #27ae60;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(46, 204, 113, 0.3);
}

.status-btn {
  background-color: #ff9800;
  color: white;
}

.status-btn:hover {
  background-color: #f57c00;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(255, 152, 0, 0.3);
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background-color: #c0392b;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #7f8c8d;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
  margin-top: 2rem;
}

.empty-state svg {
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
}

.empty-action-btn {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.9rem 1.8rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.empty-action-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* 页脚样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.footer-content p {
  margin: 0;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-content {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.modal-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-modal {
  background-color: #95a5a6;
  color: white;
}

.close-modal:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.confirm-modal {
  background-color: #3498db;
  color: white;
}

.confirm-modal:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.delete-modal {
  background-color: #e74c3c;
  color: white;
}

.delete-modal:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 用户信息查看样式 */
.user-info-section {
  margin-bottom: 2rem;
}

.user-info-section h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.info-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #7f8c8d;
}

.info-value {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}

/* 记录表格样式 */
.records-section {
  margin-bottom: 2rem;
}

.records-section h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 600;
}

.records-table-container {
  overflow-x: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.records-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
}

.records-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
}

.records-table tbody tr:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

.record-title {
  font-weight: 500;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.95rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.disabled-input {
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #6c757d;
  cursor: not-allowed;
  padding: 0.9rem;
  border-radius: 6px;
  width: 100%;
  font-size: 1rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #3498db;
}

.checkbox-group label {
  margin: 0;
  font-size: 0.95rem;
  color: #555;
  cursor: pointer;
}

/* 警告文本 */
.warning-text {
  color: #ff9800;
  font-weight: 500;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #fff3cd;
  border-radius: 6px;
  border: 1px solid #ffeeba;
}

/* 危险文本 */
.danger-text {
  color: #dc3545;
  font-weight: 500;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: 100%;
  }
  
  .stats-container {
    grid-template-columns: 1fr 1fr;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th,
  .users-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .action-column {
    flex-direction: column;
  }
  
  .action-btn {
    min-width: auto;
  }
  
  /* 模态框响应式 */
  .modal {
    width: 95%;
    margin: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}

@media (max-width: 576px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .search-filter-container {
    gap: 1rem;
  }
  
  .filter-container {
    gap: 1rem;
  }
}
</style>