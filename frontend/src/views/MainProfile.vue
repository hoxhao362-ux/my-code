<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import { useToastStore } from '../stores/toast'
import { validateEmail, validatePhone, encryptPassword } from '../utils/encryption'

// Email encryption: Keep first 2 and last 4 chars (domain), mask middle with *
const encryptEmail = (email) => {
  if (!email) return ''
  const [username, domain] = email.split('@')
  if (username.length <= 2) return `${username}@${domain}`
  return `${username.slice(0, 2)}${'*'.repeat(username.length - 2)}@${domain}`
}

// Phone encryption: Keep first 3 and last 4 digits, mask middle with *
const encryptPhone = (phone) => {
  if (!phone) return ''
  if (phone.length !== 11) return phone
  return `${phone.slice(0, 3)}${'*'.repeat(4)}${phone.slice(7)}`
}

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const toastStore = useToastStore()
const router = useRouter()
const route = useRoute()
const user = computed(() => userStore.user)

// Handle route params on mount
onMounted(() => {
  // Check if mode param exists (e.g. security mode)
  const mode = route.query.mode
  if (mode === 'security') {
    // Check if user is logged in
    if (!user.value) {
      router.push('/login')
      return
    }
    
    // Check user role
    const userRole = user.value.role || 'user'
    
    // If admin/backend role, redirect to backend security page
    if (['admin', 'reviewer', 'author'].includes(userRole)) {
      router.push('/admin/profile-security')
    } else {
      toastStore.add({ message: 'You do not have permission to access the security page. Please log in to the backend account first.', type: 'warning' })
      router.push('/profile')
    }
  }
})

// Avatar modal state
const showAvatarModal = ref(false)
const showAvatarActions = ref(false)
const fileInput = ref(null)

// Get current user's submission records
const userJournals = computed(() => {
  if (!user.value) return []
  return userStore.journals.filter(journal => journal.author === user.value.username)
})

// Toggle directory display
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// Contact info visibility state
const showFullContactInfo = ref(false)

// Toggle contact info visibility
const toggleContactInfo = () => {
  showFullContactInfo.value = !showFullContactInfo.value
}

// Show avatar action menu
const showAvatarMenu = (event) => {
  event.stopPropagation()
  showAvatarActions.value = true
}

// Hide avatar action menu
const hideAvatarMenu = () => {
  showAvatarActions.value = false
}

// View avatar
const viewAvatar = () => {
  showAvatarModal.value = true
  hideAvatarMenu()
}

// Close avatar modal
const closeAvatarModal = () => {
  showAvatarModal.value = false
}

// Trigger file selection
const triggerFileSelect = () => {
  hideAvatarMenu()
  fileInput.value?.click()
}

const handleAvatarUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (!file.type.startsWith('image/')) {
      toastStore.add({ message: 'Please select an image file', type: 'warning' })
      return
    }
    
    if (file.size > 5 * 1024 * 1024) {
      toastStore.add({ message: 'Image size cannot exceed 5MB', type: 'warning' })
      return
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target.result
      userStore.updateUser({ avatar: imageUrl })
      toastStore.add({ message: 'Avatar updated successfully', type: 'success' })
    }
    reader.readAsDataURL(file)
    
    event.target.value = ''
  }
}


</script>

<template>
  <div class="profile-container">
    <!-- Navigation -->
    <Navigation 
      :user="user"
      :current-page="'profile'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <!-- Profile Content -->
    <main class="profile-content">
      <div class="profile-wrapper">
        <!-- User Info Card -->
        <div class="user-card">
          <!-- Avatar Section -->
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
              
              <!-- Avatar Action Menu -->
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
              
              <!-- Hidden File Input -->
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
              <!-- View/Hide Info Button -->
              <button 
                class="btn btn-view" 
                @click="toggleContactInfo"
              >
                {{ showFullContactInfo ? 'Hide Details' : 'View Details' }}
              </button>
            </div>
          </div>
          
          <!-- User Details -->
          <div class="user-info">
            <div class="user-details">
              <h2 class="user-name">{{ user?.username || 'Unknown User' }}</h2>
              <p class="user-role">
                {{ user?.role === 'admin' ? 'Admin' : 
                   user?.role === 'reviewer' ? 'Reviewer' : 
                   user?.role === 'author' ? 'Author' : 'User' }}
              </p>
              <div class="user-contact" v-if="showFullContactInfo">
                <p v-if="user?.email"><strong>Email:</strong> {{ encryptEmail(user.email) }}</p>
                <p v-if="user?.phone"><strong>Phone:</strong> {{ encryptPhone(user.phone) }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Avatar View Modal -->
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
              <p>No avatar uploaded</p>
            </div>
          </div>
        </div>
        
        <!-- User Submissions -->
        <div class="journals-section">
          <h3 class="section-title">My Submissions</h3>
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
                  <span>Date: {{ journal.date }}</span>
                  <span>Module: {{ journal.module }}</span>
                  <span>Status: <span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span></span>
                  <span>Views: {{ journal.viewCount }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-journals">
            <p>No submission records</p>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="profile-actions">
          <button class="btn btn-primary" @click="$router.push('/submit')">
            Submit New Manuscript
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Profile Container */
.profile-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* Main Content */
.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* Space for fixed navbar */
}

.profile-wrapper {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

/* User Card */
.user-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* Avatar Section */
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

/* Avatar Actions Menu */
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

/* User Card Header */
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

/* Hidden File Input */
.hidden-file-input {
  display: none;
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

/* Header Actions */
.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Change Password Button */
.btn-password {
  background: #f39c12;
  color: white;
}

.btn-password:hover {
  background: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(243, 156, 18, 0.4);
}

/* Save Button */
.btn-save {
  background: #2ecc71;
  color: white;
}

.btn-save:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

/* Primary Button */
.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* Verification Section */
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

/* Edit Section Title */
.edit-section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
}

/* Info Edit and Password Edit Sections */
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

/* Password Requirements */
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

/* User Info View Mode */
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

/* User Info Edit Mode */
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

/* Journals Section */
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

/* Journal Status */
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

/* No Journals */
.no-journals {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
}

/* Action Buttons */
.profile-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 2rem;
}

/* Avatar Modal */
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

/* Footer */
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

/* Responsive Design */
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