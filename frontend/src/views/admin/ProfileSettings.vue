<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import Navigation from '../../components/Navigation.vue'
import { encryptPassword } from '../../utils/encryption'
import { userApi } from '../../utils/api'
import { useRoute } from 'vue-router'
import { validateORCID } from '../../utils/validators'

const userStore = useUserStore()
const toastStore = useToastStore()
const route = useRoute()
const user = computed(() => userStore.user)

// Tabs configuration
const activeTab = ref(route.query.tab || 'profile')
const tabs = computed(() => {
  const role = user.value?.role
  const items = [
    { id: 'profile', label: 'Profile Info', icon: '👤' },
    { id: 'security', label: 'Account Security', icon: '🔒' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' }
  ]
  
  if (role === 'editor' || role === 'admin') {
    items.push({ id: 'preferences', label: 'Editor Preferences', icon: '⚙️' })
    items.push({ id: 'api', label: 'API Access', icon: '🔑' })
  }
  
  return items
})

// Permissions
const canEditBasicInfo = computed(() => ['editor', 'admin', 'associate_editor', 'ea_ae'].includes(user.value?.role))
const canEditProfessionalInfo = computed(() => ['editor', 'admin', 'associate_editor'].includes(user.value?.role))
const canUploadAvatar = computed(() => ['editor', 'admin', 'associate_editor', 'ea_ae'].includes(user.value?.role))
const canManageSecurity = computed(() => ['editor', 'admin'].includes(user.value?.role)) // Full access
const canChangePassword = computed(() => ['editor', 'admin', 'associate_editor', 'ea_ae'].includes(user.value?.role))
const canConfigureAllNotifications = computed(() => ['editor', 'admin', 'associate_editor'].includes(user.value?.role))

// --- Tab 1: Profile Info ---
const profileForm = ref({
  // Basic
  name: '',
  email: '',
  title: '',
  affiliation: '',
  // Professional
  researchField: '',
  academicTitle: '',
  orcid: '',
  biography: '',
  // Preferences
  language: 'en',
  timezone: 'UTC+0',
  defaultTemplate: 'standard'
})

const isEditingProfile = ref(false)
const orcidVerified = ref(false)
const orcidError = ref('')

// Real-time ORCID validation
watch(() => profileForm.value.orcid, async (val) => {
  if (!val) {
    orcidError.value = ''
    return
  }
  const result = await validateORCID(val)
  if (!result.valid) {
    orcidError.value = result.message
    orcidVerified.value = false
  } else {
    orcidError.value = ''
  }
})

const initProfile = () => {
  if (user.value) {
    profileForm.value.name = user.value.username || ''
    profileForm.value.email = user.value.email || ''
    profileForm.value.title = user.value.title || ''
    profileForm.value.affiliation = user.value.affiliation || ''
    // Mock professional info as it might not be in store
    profileForm.value.researchField = user.value.researchField || 'Computer Science'
    profileForm.value.academicTitle = user.value.academicTitle || 'Professor'
    profileForm.value.orcid = user.value.orcid || ''
    profileForm.value.biography = user.value.biography || ''
  }
}

const verifyOrcid = async () => {
  if (!profileForm.value.orcid) return
  
  const result = await validateORCID(profileForm.value.orcid)
  if (result.valid) {
    orcidVerified.value = true
    toastStore.add({ message: result.message, type: 'success' })
  } else {
    orcidVerified.value = false
    toastStore.add({ message: result.message, type: 'error' })
  }
}

const verifyEmail = () => {
   // Mock API call
   toastStore.add({ message: 'Verification email sent to ' + profileForm.value.email, type: 'success' })
}

const saveProfile = async () => {
  await userStore.updateUser({
    username: profileForm.value.name,
    email: profileForm.value.email,
    title: profileForm.value.title,
    affiliation: profileForm.value.affiliation,
    // Store other fields in local storage or extra fields if supported
    researchField: profileForm.value.researchField,
    academicTitle: profileForm.value.academicTitle,
    orcid: profileForm.value.orcid,
    biography: profileForm.value.biography
  })
  isEditingProfile.value = false
  toastStore.add({ message: 'Profile saved successfully', type: 'success' })
}

const handleAvatarUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 2 * 1024 * 1024) {
      toastStore.add({ message: 'File size must be ≤ 2MB', type: 'warning' })
      return
    }
    // Mock upload
    const reader = new FileReader()
    reader.onload = (e) => {
      userStore.updateUser({ avatar: e.target.result })
    }
    reader.readAsDataURL(file)
  }
}

// --- Tab 2: Account Security ---
const passwordForm = ref({ current: '', new: '', confirm: '' })
const twoFactor = ref({ enabled: false, method: 'email' })
const devices = ref([
  { id: 1, name: 'Chrome on Windows', ip: '192.168.1.1', time: '2026-02-07 10:00:00', current: true },
  { id: 2, name: 'Safari on iPhone', ip: '192.168.1.5', time: '2026-02-06 18:30:00', current: false }
])
const logs = ref([
  { id: 1, action: 'Login', time: '2026-02-07 10:00:00', ip: '192.168.1.1' },
  { id: 2, action: 'Update Profile', time: '2026-02-06 14:20:00', ip: '192.168.1.1' }
])

const isChangingPassword = ref(false)

const changePassword = async () => {
  if (isChangingPassword.value) return

  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
  if (!regex.test(passwordForm.value.new)) {
    toastStore.add({ message: 'Password must contain uppercase, lowercase, number, special char and be at least 8 chars.', type: 'warning' })
    return
  }
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    toastStore.add({ message: 'Passwords do not match.', type: 'warning' })
    return
  }

  isChangingPassword.value = true
  try {
    const encryptedOld = await encryptPassword(passwordForm.value.current)
    const encryptedNew = await encryptPassword(passwordForm.value.new)

    const payload = {
      old_password: encryptedOld,
      new_password: encryptedNew
    }
    await userApi.changePassword(payload)

    toastStore.add({ message: 'Password changed successfully. Please log in again.', type: 'success' })

    await userStore.logout()
    route.push('/login')
  } catch (error) {
    console.error('Change password failed:', error)
    toastStore.add({
      message: error.response?.data?.message || 'Failed to change password.',
      type: 'error'
    })
  } finally {
    isChangingPassword.value = false
    passwordForm.value.current = ''
    passwordForm.value.new = ''
    passwordForm.value.confirm = ''
  }
}

const toggle2FA = () => {
  twoFactor.value.enabled = !twoFactor.value.enabled
  if (twoFactor.value.enabled) {
    toastStore.add({ message: '2FA Enabled. Backup codes generated.', type: 'success' })
  }
}

const logoutDevice = (id) => {
  devices.value = devices.value.filter(d => d.id !== id)
}

const exportLogs = () => {
  const csvContent = "data:text/csv;charset=utf-8," 
    + "Action,Time,IP\n"
    + logs.value.map(e => `${e.action},${e.time},${e.ip}`).join("\n")
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", "operation_logs.csv")
  document.body.appendChild(link)
  link.click()
}

// --- Tab 3: Notifications ---
const notificationTypes = ref([
  { id: 1, name: 'Manuscript Submission', channel: 'email', frequency: 'instant', enabled: true },
  { id: 2, name: 'Review Invitation', channel: 'system', frequency: 'daily', enabled: true },
  { id: 3, name: 'Approval Reminder', channel: 'sms', frequency: 'weekly', enabled: true }
])
const globalNotification = ref(true)

const toggleGlobalNotifications = () => {
  globalNotification.value = !globalNotification.value
  notificationTypes.value.forEach(t => t.enabled = globalNotification.value)
}

const sendTestNotification = () => {
  toastStore.add({ message: 'Test notification sent!', type: 'success' })
}

// --- Tab 4: Editor Preferences ---
const reviewerRules = ref({
  fieldMatchWeight: 50,
  reviewSpeedWeight: 30,
  rejectionRateWeight: 20,
  autoRecommend: false
})
const defaultTemplate = ref('major_revision')
const workflow = ref({
  autoRemind: false,
  autoArchive: false
})

// --- Tab 5: API Access ---
const apiKeys = ref([
  { id: 1, key: 'sk_live_xxxxxxxx', scope: 'read_only', created: '2026-01-01', status: 'active' }
])
const newKeyScope = ref('read_only')
const newKeyValidity = ref('permanent')

const generateApiKey = () => {
  const key = 'sk_live_' + Math.random().toString(36).substring(2)
  apiKeys.value.push({
    id: Date.now(),
    key: key,
    scope: newKeyScope.value,
    created: new Date().toLocaleDateString(),
    status: 'active'
  })
}

const copyKey = (key) => {
  navigator.clipboard.writeText(key)
  toastStore.add({ message: 'Copied to Clipboard', type: 'success' })
}

const revokeKey = (id) => {
  const k = apiKeys.value.find(k => k.id === id)
  if (k) k.status = 'revoked'
}

onMounted(() => {
  initProfile()
})
</script>

<template>
  <div class="profile-settings-container">
    <Navigation :user="user" current-page="profile-settings" />

    <div class="settings-layout">
      <!-- Sidebar -->
      <aside class="settings-sidebar">
        <div class="user-brief">
          <div class="sidebar-avatar">
            <img v-if="user?.avatar" :src="user.avatar" alt="Avatar" />
            <span v-else>{{ user?.username?.charAt(0).toUpperCase() }}</span>
          </div>
          <h3>{{ user?.username }}</h3>
          <p>{{ user?.role }}</p>
        </div>
        <nav class="sidebar-nav">
          <a 
            v-for="tab in tabs" 
            :key="tab.id"
            href="#" 
            class="sidebar-link"
            :class="{ active: activeTab === tab.id }"
            @click.prevent="activeTab = tab.id"
          >
            <span class="icon">{{ tab.icon }}</span>
            {{ tab.label }}
          </a>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="settings-content">
        <!-- Tab 1: Profile Info -->
        <section v-if="activeTab === 'profile'" class="settings-section">
          <header class="section-header">
            <h2>Profile Info</h2>
            <p>Manage personal identity and professional information.</p>
          </header>

          <div class="card">
            <div class="card-header">
              <h3>Basic Information</h3>
              <button v-if="canEditBasicInfo && !isEditingProfile" class="btn btn-outline" @click="isEditingProfile = true">Edit</button>
              <button v-if="isEditingProfile" class="btn btn-primary" @click="saveProfile">Save</button>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Name</label>
                <input v-model="profileForm.name" :disabled="!isEditingProfile" class="form-control" />
              </div>
              <div class="form-group">
                <label>Email</label>
                <div class="input-group">
                  <input v-model="profileForm.email" :disabled="!isEditingProfile" class="form-control" />
                  <button v-if="isEditingProfile" @click="verifyEmail" class="btn btn-sm">Verify</button>
                </div>
              </div>
              <div class="form-group">
                <label>Title</label>
                <input v-model="profileForm.title" :disabled="!isEditingProfile" class="form-control" />
              </div>
              <div class="form-group">
                <label>Affiliation</label>
                <input v-model="profileForm.affiliation" :disabled="!isEditingProfile" class="form-control" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h3>Professional Information</h3>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Research Field</label>
                <input v-model="profileForm.researchField" :disabled="!canEditProfessionalInfo || !isEditingProfile" class="form-control" />
              </div>
              <div class="form-group">
                <label>Academic Title</label>
                <input v-model="profileForm.academicTitle" :disabled="!canEditProfessionalInfo || !isEditingProfile" class="form-control" />
              </div>
              <div class="form-group">
                <label>ORCID ID</label>
                <div class="input-group">
                  <input 
                    v-model="profileForm.orcid" 
                    :disabled="!canEditProfessionalInfo || !isEditingProfile" 
                    class="form-control" 
                    :class="{ 'error': orcidError }"
                    placeholder="0000-0000-0000-0000"
                  />
                  <button v-if="canEditProfessionalInfo && isEditingProfile" @click="verifyOrcid" class="btn btn-sm">Verify API</button>
                </div>
                <span v-if="orcidError" class="error-msg">{{ orcidError }}</span>
                <span v-if="orcidVerified && !orcidError" class="text-success">Verified</span>
              </div>
              <div class="form-group full-width">
                <label>Personal Biography</label>
                <textarea v-model="profileForm.biography" :disabled="!canEditProfessionalInfo || !isEditingProfile" class="form-control" rows="3"></textarea>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h3>Profile Avatar</h3>
            </div>
            <div class="avatar-upload">
              <div class="current-avatar">
                <img v-if="user?.avatar" :src="user.avatar" />
                <div v-else class="avatar-placeholder">{{ user?.username?.charAt(0) }}</div>
              </div>
              <div v-if="canUploadAvatar" class="upload-controls">
                <label class="btn btn-outline">
                  Upload Avatar
                  <input type="file" hidden accept="image/png, image/jpeg" @change="handleAvatarUpload" />
                </label>
                <p class="hint">JPG/PNG, size ≤ 2MB</p>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h3>Preference Settings</h3>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Interface Language</label>
                <select v-model="profileForm.language" :disabled="!canEditBasicInfo" class="form-control">
                  <option value="en">English</option>
                  <option value="zh">Chinese</option>
                </select>
              </div>
              <div class="form-group">
                <label>Time Zone</label>
                <select v-model="profileForm.timezone" :disabled="!canEditBasicInfo" class="form-control">
                  <option value="UTC+0">UTC+0</option>
                  <option value="UTC+8">UTC+8</option>
                </select>
              </div>
              <div class="form-group">
                <label>Default Template</label>
                <select v-model="profileForm.defaultTemplate" :disabled="!canEditBasicInfo" class="form-control">
                  <option value="standard">Standard</option>
                  <option value="compact">Compact</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <!-- Tab 2: Account Security -->
        <section v-if="activeTab === 'security'" class="settings-section">
          <header class="section-header">
            <h2>Account Security</h2>
            <p>Ensure account security and meet compliance requirements.</p>
          </header>

          <div v-if="canChangePassword" class="card">
            <div class="card-header">
              <h3>Change Password</h3>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Old Password</label>
                <input type="password" v-model="passwordForm.current" class="form-control" />
              </div>
              <div class="form-group">
                <label>New Password</label>
                <input type="password" v-model="passwordForm.new" class="form-control" placeholder="Upper+Lower+Num+Special, ≥8 chars" />
              </div>
              <div class="form-group">
                <label>Confirm New Password</label>
                <input type="password" v-model="passwordForm.confirm" class="form-control" />
              </div>
              <div class="form-group full-width">
                <button class="btn btn-primary" @click="changePassword">Update Password</button>
              </div>
            </div>
          </div>

          <div v-if="canManageSecurity" class="card">
            <div class="card-header">
              <h3>Two-Factor Authentication</h3>
            </div>
            <div class="flex-row">
              <p>Secure your account with 2FA.</p>
              <button class="btn" :class="twoFactor.enabled ? 'btn-danger' : 'btn-success'" @click="toggle2FA">
                {{ twoFactor.enabled ? 'Disable 2FA' : 'Enable 2FA' }}
              </button>
            </div>
            <div v-if="twoFactor.enabled" class="mt-4">
              <label>Verification Method: </label>
              <select v-model="twoFactor.method" class="form-control inline-select">
                <option value="email">Email</option>
                <option value="sms">SMS</option>
              </select>
              <button class="btn btn-link">Download Backup Codes</button>
            </div>
          </div>

          <div v-if="canManageSecurity" class="card">
            <div class="card-header">
              <h3>Login Device Management</h3>
            </div>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>IP</th>
                  <th>Time</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in devices" :key="device.id">
                  <td>{{ device.name }} <span v-if="device.current" class="badge">Current</span></td>
                  <td>{{ device.ip }}</td>
                  <td>{{ device.time }}</td>
                  <td>
                    <button v-if="!device.current" class="btn btn-sm btn-danger" @click="logoutDevice(device.id)">Log Out</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

           <div v-if="canManageSecurity" class="card">
            <div class="card-header">
              <h3>Operation Logs</h3>
              <button class="btn btn-outline" @click="exportLogs">Export CSV</button>
            </div>
             <table class="data-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Time</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in logs" :key="log.id">
                  <td>{{ log.action }}</td>
                  <td>{{ log.time }}</td>
                  <td>{{ log.ip }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Tab 3: Notifications -->
        <section v-if="activeTab === 'notifications'" class="settings-section">
           <header class="section-header">
            <h2>Notifications</h2>
            <p>Customize receiving system notifications.</p>
          </header>

          <div class="card">
             <div class="card-header">
              <h3>Global Settings</h3>
            </div>
            <div class="flex-row">
              <label class="switch-label">
                <input type="checkbox" :checked="globalNotification" @change="toggleGlobalNotifications" :disabled="!canConfigureAllNotifications">
                Enable All Notifications
              </label>
              <div v-if="canConfigureAllNotifications">
                 <button class="btn btn-outline" @click="sendTestNotification">Send Test Notification</button>
                 <button class="btn btn-link">Restore Defaults</button>
              </div>
            </div>
          </div>

          <div class="card">
             <div class="card-header">
              <h3>Notification Types</h3>
            </div>
             <table class="data-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Channel</th>
                  <th>Frequency</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="type in notificationTypes" :key="type.id">
                  <td>{{ type.name }}</td>
                  <td>
                    <select v-model="type.channel" class="form-control" :disabled="!canConfigureAllNotifications && user.role !== 'associate_editor'">
                      <option value="email">Email</option>
                      <option value="system">System Message</option>
                      <option value="sms">SMS</option>
                    </select>
                  </td>
                  <td>
                     <select v-model="type.frequency" class="form-control" :disabled="!canConfigureAllNotifications && user.role !== 'associate_editor'">
                      <option value="instant">Instant</option>
                      <option value="daily">Daily Summary</option>
                      <option value="weekly">Weekly Summary</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Tab 4: Editor Preferences (Editor Only) -->
        <section v-if="activeTab === 'preferences'" class="settings-section">
           <header class="section-header">
            <h2>Editor Preferences</h2>
            <p>Professional configuration for workflow efficiency.</p>
          </header>

          <div class="card">
            <div class="card-header">
              <h3>Reviewer Recommendation Rules</h3>
            </div>
            <div class="form-grid">
               <div class="form-group full-width">
                 <label>Field Match Weight ({{ reviewerRules.fieldMatchWeight }}%)</label>
                 <input type="range" v-model="reviewerRules.fieldMatchWeight" min="0" max="100" class="range-input" />
               </div>
               <div class="form-group full-width">
                 <label>Review Speed Weight ({{ reviewerRules.reviewSpeedWeight }}%)</label>
                 <input type="range" v-model="reviewerRules.reviewSpeedWeight" min="0" max="100" class="range-input" />
               </div>
               <div class="form-group full-width">
                 <label>Rejection Rate Weight ({{ reviewerRules.rejectionRateWeight }}%)</label>
                 <input type="range" v-model="reviewerRules.rejectionRateWeight" min="0" max="100" class="range-input" />
               </div>
               <div class="form-group full-width">
                 <label class="switch-label">
                  <input type="checkbox" v-model="reviewerRules.autoRecommend">
                  Enable Auto Recommendation
                </label>
               </div>
            </div>
          </div>

          <div class="card">
             <div class="card-header">
              <h3>Workflow Automation</h3>
            </div>
            <div class="form-grid">
              <div class="form-group full-width">
                 <label class="switch-label">
                  <input type="checkbox" v-model="workflow.autoRemind">
                  Auto-send Reminder Emails (3 days before deadline)
                </label>
               </div>
               <div class="form-group full-width">
                 <label class="switch-label">
                  <input type="checkbox" v-model="workflow.autoArchive">
                  Auto-archive Decision Letters
                </label>
               </div>
            </div>
          </div>
        </section>

        <!-- Tab 5: API Access (Editor Only) -->
        <section v-if="activeTab === 'api'" class="settings-section">
           <header class="section-header">
            <h2>API Access</h2>
            <p>Manage API keys for external system integration.</p>
          </header>

          <div class="card">
            <div class="card-header">
              <h3>Generate API Key</h3>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Scope</label>
                <select v-model="newKeyScope" class="form-control">
                  <option value="read_only">Read Only</option>
                  <option value="read_write">Read/Write</option>
                </select>
              </div>
              <div class="form-group">
                <label>Validity</label>
                <select v-model="newKeyValidity" class="form-control">
                  <option value="permanent">Permanent</option>
                  <option value="1_year">1 Year</option>
                </select>
              </div>
              <div class="form-group">
                <label>&nbsp;</label>
                <button class="btn btn-primary" @click="generateApiKey">Generate New Key</button>
              </div>
            </div>
          </div>

           <div class="card">
             <div class="card-header">
              <h3>Active Keys</h3>
            </div>
             <table class="data-table">
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Scope</th>
                  <th>Created</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="k in apiKeys" :key="k.id">
                  <td>{{ k.key.substring(0, 12) }}...</td>
                  <td>{{ k.scope }}</td>
                  <td>{{ k.created }}</td>
                  <td><span class="badge" :class="k.status">{{ k.status }}</span></td>
                  <td>
                    <button class="btn btn-sm" @click="copyKey(k.key)">Copy</button>
                    <button v-if="k.status === 'active'" class="btn btn-sm btn-danger" @click="revokeKey(k.id)">Revoke</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped>
.profile-settings-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-top: 60px; /* Space for fixed navbar */
}

.settings-layout {
  display: flex;
  max-width: 1200px;
  margin: 2rem auto;
  gap: 2rem;
  padding: 0 1rem;
}

.settings-sidebar {
  width: 280px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 2rem;
  height: fit-content;
}

.user-brief {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.sidebar-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 1rem;
  overflow: hidden;
}

.sidebar-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  color: #555;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
}

.sidebar-link:hover, .sidebar-link.active {
  background: #e6f7ff;
  color: #1890ff;
}

.settings-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.section-header p {
  color: #7f8c8d;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  font-size: 1.1rem;
  margin: 0;
  color: #2c3e50;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.form-control {
  padding: 0.6rem;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 0.95rem;
}

.form-control:focus {
  border-color: #40a9ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.input-group .form-control {
  flex: 1;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-outline {
  background: white;
  border: 1px solid #d9d9d9;
  color: #666;
}

.btn-outline:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-link {
  background: none;
  color: #1890ff;
  text-decoration: underline;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.current-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  font-size: 2.5rem;
  color: #999;
}

.current-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hint {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background: #fafafa;
  color: #666;
  font-weight: 500;
}

.badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  background: #eee;
}

.badge.active {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.badge.revoked {
  background: #fff1f0;
  color: #cf1322;
  border: 1px solid #ffa39e;
}

.flex-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.range-input {
  width: 100%;
}

.mt-4 {
  margin-top: 1rem;
}

.inline-select {
  display: inline-block;
  width: auto;
  margin-right: 1rem;
}

.error-msg {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 4px;
  display: block;
}

.form-control.error {
  border-color: #ef4444;
}

.text-success {
  color: #52c41a;
  font-size: 0.85rem;
  margin-top: 4px;
  display: block;
}
</style>
