<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import Navigation from '../../components/Navigation.vue'
import { userApi } from '../../utils/api'
import { encryptPassword } from '../../utils/encryption'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

const activeTab = ref('personal')

const tabs = [
  { id: 'personal', label: 'Personal Info' },
  { id: 'research', label: 'Research Areas / Keywords' },
  { id: 'notification', label: 'Notification Settings' },
  { id: 'security', label: 'Account Security' }
]

// Form States
const personalInfo = ref({
  fullName: user.value?.username || '',
  email: user.value?.email || '',
  institution: 'University of Example',
  title: 'Professor'
})

const researchAreas = ref({
  keywords: 'Machine Learning, Computer Vision, AI',
  primaryArea: 'Computer Science'
})

const notifications = ref({
  emailAlerts: true,
  smsAlerts: false,
  newsletter: true
})

const security = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const savePersonal = () => {
  toastStore.add({ message: 'Personal info saved successfully.', type: 'success' })
}

const saveResearch = () => {
  toastStore.add({ message: 'Research areas updated.', type: 'success' })
}

const saveNotifications = () => {
  toastStore.add({ message: 'Notification settings updated.', type: 'success' })
}

const isSubmittingPassword = ref(false)

const changePassword = async () => {
  if (isSubmittingPassword.value) return

  if (!security.value.currentPassword || !security.value.newPassword || !security.value.confirmPassword) {
    toastStore.add({ message: 'Please fill in all fields.', type: 'warning' })
    return
  }

  if (security.value.newPassword !== security.value.confirmPassword) {
    toastStore.add({ message: 'Passwords do not match.', type: 'warning' })
    return
  }

  isSubmittingPassword.value = true
  try {
    const encryptedOld = await encryptPassword(security.value.currentPassword)
    const encryptedNew = await encryptPassword(security.value.newPassword)

    await userApi.changePassword({
      old_password: encryptedOld,
      new_password: encryptedNew
    })

    toastStore.add({ message: 'Password changed successfully. Please log in again.', type: 'success' })

    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Reviewer change password failed:', error)
    toastStore.add({
      message: error.response?.data?.message || 'Failed to change password. Please verify your old password.',
      type: 'error'
    })
  } finally {
    isSubmittingPassword.value = false
    security.value.currentPassword = ''
    security.value.newPassword = ''
    security.value.confirmPassword = ''
  }
}

</script>

<template>
  <div class="profile-container">
    <Navigation :user="user" current-page="reviewer-profile" />

    <main class="content">
      <div class="page-header">
        <h1>Profile & Settings / 个人资料与设置</h1>
      </div>

      <div class="profile-layout">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
          <nav class="sidebar-nav">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              class="nav-item"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </nav>
        </aside>

        <!-- Main Content -->
        <div class="main-panel">
          
          <!-- Personal Info -->
          <div v-if="activeTab === 'personal'" class="panel-section">
            <h2>Personal Info</h2>
            <div class="form-group">
              <label>Full Name</label>
              <input v-model="personalInfo.fullName" type="text" />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="personalInfo.email" type="email" disabled />
              <span class="help-text">Contact admin to change email.</span>
            </div>
            <div class="form-group">
              <label>Institution</label>
              <input v-model="personalInfo.institution" type="text" />
            </div>
            <div class="form-group">
              <label>Title</label>
              <select v-model="personalInfo.title">
                <option>Professor</option>
                <option>Associate Professor</option>
                <option>Assistant Professor</option>
                <option>Lecturer</option>
                <option>Researcher</option>
              </select>
            </div>
            <button class="btn-primary" @click="savePersonal">Save Changes</button>
          </div>

          <!-- Research Areas -->
          <div v-if="activeTab === 'research'" class="panel-section">
            <h2>Research Areas / Keywords</h2>
            <div class="form-group">
              <label>Primary Research Area</label>
              <input v-model="researchAreas.primaryArea" type="text" />
            </div>
            <div class="form-group">
              <label>Keywords (comma separated)</label>
              <textarea v-model="researchAreas.keywords" rows="3"></textarea>
            </div>
            <button class="btn-primary" @click="saveResearch">Update Interests</button>
          </div>

          <!-- Notification Settings -->
          <div v-if="activeTab === 'notification'" class="panel-section">
            <h2>Notification Settings</h2>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="notifications.emailAlerts">
                Email Alerts for New Invitations
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="notifications.smsAlerts">
                SMS Alerts (Urgent Only)
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="notifications.newsletter">
                Receive System Announcements
              </label>
            </div>
            <button class="btn-primary" @click="saveNotifications">Save Preferences</button>
          </div>

          <!-- Account Security -->
          <div v-if="activeTab === 'security'" class="panel-section">
            <h2>Account Security / Change Password</h2>
            <div class="form-group">
              <label>Current Password</label>
              <input v-model="security.currentPassword" type="password" />
            </div>
            <div class="form-group">
              <label>New Password</label>
              <input v-model="security.newPassword" type="password" />
            </div>
            <div class="form-group">
              <label>Confirm New Password</label>
              <input v-model="security.confirmPassword" type="password" />
            </div>
            <button class="btn-primary" @click="changePassword">Change Password</button>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.content {
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.page-header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.profile-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.sidebar {
  width: 250px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}

.nav-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  border-left: 3px solid transparent;
  cursor: pointer;
  color: #666;
  font-weight: 500;
  transition: all 0.3s;
}

.nav-item:hover {
  background: #f9f9f9;
  color: #3498db;
}

.nav-item.active {
  background: #f0f8ff;
  color: #3498db;
  border-left-color: #3498db;
}

.main-panel {
  flex: 1;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.panel-section h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group input, 
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.help-text {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.25rem;
  display: block;
}

.btn-primary {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary:hover {
  background: #2980b9;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
  }
}
</style>
