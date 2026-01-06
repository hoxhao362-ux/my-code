<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { validateEmail, validatePhone } from '../../utils/encryption'

const userStore = useUserStore()

// 编辑模式
const isEditing = ref(false)

// 表单数据
const formData = ref({
  username: userStore.user?.username || '',
  email: userStore.user?.email || '',
  phone: userStore.user?.phone || '',
  avatar: userStore.user?.avatar || ''
})

// 头像弹窗状态
const showAvatarModal = ref(false)
const fileInput = ref(null)

// 进入编辑模式
const startEditing = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  // 重置表单数据
  formData.value = {
    username: userStore.user?.username || '',
    email: userStore.user?.email || '',
    phone: userStore.user?.phone || '',
    avatar: userStore.user?.avatar || ''
  }
}

// 保存用户信息
const saveUserInfo = () => {
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
  isEditing.value = false
}

// 查看头像
const viewAvatar = () => {
  showAvatarModal.value = true
}

// 关闭头像查看弹窗
const closeAvatarModal = () => {
  showAvatarModal.value = false
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
              class="user-avatar" 
              @click="viewAvatar"
            >
              <img 
                v-if="userStore.user?.avatar" 
                :src="userStore.user.avatar" 
                :alt="userStore.user.username"
                class="avatar-image"
              />
              <span v-else>{{ userStore.user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
              <!-- 悬停时显示操作提示 -->
              <div class="avatar-tooltip">点击查看大图</div>
            </div>
          </div>
          
          <div class="user-card-header">
            <h3 class="card-title">个人信息</h3>
            <button 
              class="btn btn-edit" 
              @click="isEditing ? saveUserInfo() : startEditing()"
            >
              {{ isEditing ? '保存' : '编辑' }}
            </button>
            <button 
              v-if="isEditing" 
              class="btn btn-cancel" 
              @click="cancelEditing"
            >
              取消
            </button>
          </div>
          
          <!-- 查看模式 -->
          <div v-if="!isEditing" class="user-info">
            <div class="user-details">
              <h2 class="user-name">{{ userStore.user?.username || '未知用户' }}</h2>
              <p class="user-role">
                {{ userStore.user?.role === 'admin' ? '管理员' : 
                   userStore.user?.role === 'reviewer' ? '审核员' : 
                   userStore.user?.role === 'author' ? '作者' : '普通用户' }}
              </p>
              <div class="user-contact">
                <p v-if="userStore.user?.email"><strong>邮箱：</strong>{{ userStore.user.email }}</p>
                <p v-if="userStore.user?.phone"><strong>手机号：</strong>{{ userStore.user.phone }}</p>
              </div>
            </div>
          </div>
          
          <!-- 编辑模式 -->
          <div v-else class="user-edit-form">
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
                <p>您还没有上传头像</p>
              </div>
            </div>
          </div>
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
/* 样式可以从原 Profile.vue 组件复制 */
</style>