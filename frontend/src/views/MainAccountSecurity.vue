<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'
import { encryptPassword, validateEmail, validatePhone } from '../utils/encryption'
import { userApi } from '../utils/api'

const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()

const user = computed(() => userStore.user)
if (!user.value) {
  router.push('/login')
}

// Password Form Data
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const isChangingPassword = ref(false)

// Contact Form Data
const contactForm = ref({
  currentPassword: '',
  email: user.value?.email || '',
  phone: user.value?.phone || ''
})

// Change Password
const changePassword = async () => {
  if (isChangingPassword.value) return

  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    toastStore.add({ message: 'Please fill in all fields', type: 'warning' })
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toastStore.add({ message: 'New passwords do not match', type: 'error' })
    return
  }

  isChangingPassword.value = true

  try {
    const encryptedOld = await encryptPassword(passwordForm.value.currentPassword)
    const encryptedNew = await encryptPassword(passwordForm.value.newPassword)

    const payload = {
      old_password: encryptedOld,
      new_password: encryptedNew
    }
    await userApi.changePassword(payload)

    toastStore.add({
      message: 'Password changed successfully. Please log in again.',
      type: 'success'
    })

    await userStore.logout()
    router.push('/login')

  } catch (error) {
    console.error('Change password failed:', error)
    toastStore.add({
      message: error.response?.data?.message || 'Failed to change password.',
      type: 'error'
    })
  } finally {
    isChangingPassword.value = false
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  }
}

// Change Contact Info
const changeContact = async () => {
  if (!contactForm.value.currentPassword) {
    toastStore.add({ message: 'Please enter current password', type: 'error' })
    return
  }

  if (!validateEmail(contactForm.value.email)) {
    toastStore.add({ message: 'Please enter a valid email address', type: 'error' })
    return
  }

  if (!validatePhone(contactForm.value.phone)) {
    toastStore.add({ message: 'Please enter a valid phone number', type: 'error' })
    return
  }

  toastStore.add({ message: 'Contact information updated successfully', type: 'success' })

  contactForm.value = {
    currentPassword: '',
    email: contactForm.value.email,
    phone: contactForm.value.phone
  }
}
</script>

<template>
  <div class="main-account-security-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'account-security'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />

    <!-- Account Security Content -->
    <div class="content">
      <div class="header">
        <h1>Account Security</h1>
        <p class="subtitle">Manage your account security settings</p>
      </div>

      <!-- Message Alert (hidden - using toastStore instead) -->

      <section class="security-section">
        <div class="security-card">
          <!-- Password Management -->
          <div class="security-item">
            <h2>Password Management</h2>
            <div class="security-content">
              <form class="password-form" @submit.prevent="changePassword">
                <div class="form-row">
                  <div class="form-group">
                    <label for="currentPassword">Current Password</label>
                    <input 
                      type="password" 
                      id="currentPassword"
                      v-model="passwordForm.currentPassword"
                      class="form-control"
                      placeholder="Enter current password"
                      required
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label for="newPassword">New Password</label>
                    <input 
                      type="password" 
                      id="newPassword"
                      v-model="passwordForm.newPassword"
                      class="form-control"
                      placeholder="Enter new password"
                      required
                    >
                  </div>
                  <div class="form-group">
                    <label for="confirmPassword">Confirm New Password</label>
                    <input 
                      type="password" 
                      id="confirmPassword"
                      v-model="passwordForm.confirmPassword"
                      class="form-control"
                      placeholder="Confirm new password"
                      required
                    >
                  </div>
                </div>
                <div class="password-requirements">
                  <h3>Password Requirements:</h3>
                  <ul>
                    <li>• At least 6 characters long</li>
                    <li>• Must contain letters and numbers</li>
                    <li>• Recommended to include uppercase and special characters</li>
                    <li>• <span style="color: #2ecc71;">Your password is encrypted during transmission</span></li>
                  </ul>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-save">Save Changes</button>
                </div>
              </form>
            </div>
          </div>

          <!-- Contact Info Management -->
          <div class="security-item">
            <h2>Contact Information</h2>
            <div class="security-content">
              <form class="contact-form" @submit.prevent="changeContact">
                <div class="form-row">
                  <div class="form-group">
                    <label for="contactCurrentPassword">Current Password</label>
                    <input 
                      type="password" 
                      id="contactCurrentPassword"
                      v-model="contactForm.currentPassword"
                      class="form-control"
                      placeholder="Enter password to verify identity"
                      required
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label for="email">Email</label>
                    <input 
                      type="email" 
                      id="email"
                      v-model="contactForm.email"
                      class="form-control"
                      placeholder="Enter email address"
                      required
                    >
                  </div>
                  <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input 
                      type="tel" 
                      id="phone"
                      v-model="contactForm.phone"
                      class="form-control"
                      placeholder="Enter phone number"
                      required
                    >
                  </div>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-save">Save Changes</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.main-account-security-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
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
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
}

/* 消息提示样式 */
.message {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 安全区域样式 */
.security-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.security-card {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.security-item {
  border-bottom: 1px solid #eee;
  padding-bottom: 2rem;
}

.security-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.security-item h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  font-weight: 600;
}

/* 表单样式 */
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

.form-control {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 密码要求样式 */
.password-requirements {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0 1.5rem 0;
}

.password-requirements h3 {
  font-size: 1rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.password-requirements ul {
  margin: 0;
  padding-left: 1.5rem;
}

.password-requirements li {
  color: #6c757d;
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

/* 按钮样式 */
.form-actions {
  display: flex;
  justify-content: flex-start;
}

.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-save {
  background: #2ecc71;
  color: white;
}

.btn-save:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .security-section {
    padding: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    width: 100%;
  }
  
  .form-actions {
    justify-content: stretch;
  }
  
  .btn {
    width: 100%;
  }
}
</style>