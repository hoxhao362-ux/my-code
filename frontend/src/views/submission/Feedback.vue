<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useI18n } from '../../composables/useI18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()
const user = ref(userStore.user)

// --- State ---
const activeTab = ref('submit') // submit, my-feedback, all-feedback
const submitting = ref(false)
const successMessage = ref('')
const selectedFeedback = ref(null) // For viewing details

const form = ref({
  type: t('submission.feedback.form.types.suggestion'),
  title: '',
  description: '',
  attachments: [],
  contact: user.value?.email || ''
})

// Mock Database (Load from localStorage via store in real app, here we mock store behavior for the new structure)
// We'll reuse userStore.feedbackMessages but might need to adapt structure if it differs
const feedbacks = ref([])

// --- Data Options ---
const feedbackTypes = [
  t('submission.feedback.form.types.suggestion'),
  t('submission.feedback.form.types.bug'),
  t('submission.feedback.form.types.question'),
  t('submission.feedback.form.types.others')
]

// --- Computed ---
const myFeedbacks = computed(() => {
  return feedbacks.value.filter(f => f.userId === user.value?.username || f.email === user.value?.email).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const allFeedbacks = computed(() => {
  return feedbacks.value.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const isEditor = computed(() => ['editor', 'admin'].includes(user.value?.role))

// --- Methods ---
const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 3) {
    alert(t('submission.feedback.alert.maxFiles'))
    return
  }
  // Check size 5MB
  const validFiles = files.filter(f => f.size <= 5 * 1024 * 1024)
  if (validFiles.length < files.length) {
    alert(t('submission.feedback.alert.fileSize'))
  }
  form.value.attachments = validFiles
}

const submitFeedback = () => {
  if (!form.value.title || !form.value.description) return

  submitting.value = true
  
  // Simulate API call
  setTimeout(() => {
    const newFeedback = {
      id: 'FB-' + Date.now(),
      userId: user.value?.username,
      email: form.value.contact,
      type: form.value.type,
      title: form.value.title,
      description: form.value.description,
      attachments: form.value.attachments.map(f => f.name),
      status: 'Pending',
      createdAt: new Date().toISOString(),
      replies: [],
      rating: 0
    }

    // Add to local store (mocking backend)
    // userStore.addFeedbackMessage(newFeedback) -- The store method expects slightly different structure, let's adapt or just use local array for this demo
    feedbacks.value.push(newFeedback)
    saveFeedbacks()

    submitting.value = false
    successMessage.value = t('submission.feedback.alert.success', { id: newFeedback.id })
    
    // Reset form
    form.value = {
      type: t('submission.feedback.form.types.suggestion'),
      title: '',
      description: '',
      attachments: [],
      contact: user.value?.email || ''
    }
    
    // Switch to My Feedback tab
    setTimeout(() => {
        successMessage.value = ''
        activeTab.value = 'my-feedback'
    }, 2000)
  }, 1000)
}

const viewFeedback = (fb) => {
  selectedFeedback.value = fb
}

const closeDetail = () => {
  selectedFeedback.value = null
}

const replyContent = ref('')
const submitReply = () => {
  if (!replyContent.value) return
  
  selectedFeedback.value.replies.push({
    author: user.value.username,
    role: user.value.role,
    content: replyContent.value,
    time: new Date().toISOString()
  })
  
  // Auto update status if editor replies
  if (isEditor.value && selectedFeedback.value.status === 'Pending') {
    selectedFeedback.value.status = 'Resolved' // Or keep pending? Requirement says Editor can update status. Let's assume manual update or auto.
  }

  replyContent.value = ''
  saveFeedbacks()
}

const updateStatus = (status) => {
  selectedFeedback.value.status = status
  saveFeedbacks()
}

const submitRating = (rating) => {
  selectedFeedback.value.rating = rating
  saveFeedbacks()
}

const saveFeedbacks = () => {
  localStorage.setItem('submission_feedbacks', JSON.stringify(feedbacks.value))
}

const loadFeedbacks = () => {
  const data = localStorage.getItem('submission_feedbacks')
  if (data) {
    feedbacks.value = JSON.parse(data)
  }
}

onMounted(() => {
  loadFeedbacks()
})

const formatDate = (isoString) => {
  return new Date(isoString).toLocaleString()
}
</script>

<template>
  <div class="feedback-page">
    <div class="container">
      <h1>{{ t('submission.feedback.title') }}</h1>
      
      <!-- Tabs -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'submit' }" @click="activeTab = 'submit'">{{ t('submission.feedback.tabs.submit') }}</button>
        <button :class="{ active: activeTab === 'my-feedback' }" @click="activeTab = 'my-feedback'">{{ t('submission.feedback.tabs.my') }}</button>
        <button v-if="isEditor" :class="{ active: activeTab === 'all-feedback' }" @click="activeTab = 'all-feedback'">{{ t('submission.feedback.tabs.all') }}</button>
      </div>

      <!-- Submit Form -->
      <div v-if="activeTab === 'submit'" class="tab-content">
        <div v-if="successMessage" class="success-alert">{{ successMessage }}</div>
        
        <form @submit.prevent="submitFeedback" class="feedback-form">
          <div class="form-group">
            <label>{{ t('submission.feedback.form.type') }}</label>
            <select v-model="form.type">
              <option v-for="t_opt in feedbackTypes" :key="t_opt" :value="t_opt">{{ t_opt }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ t('submission.feedback.form.title') }}</label>
            <input type="text" v-model="form.title" maxlength="50" required :placeholder="t('submission.feedback.form.placeholder.title')">
          </div>

          <div class="form-group">
            <label>{{ t('submission.feedback.form.description') }}</label>
            <textarea v-model="form.description" minlength="20" rows="6" required :placeholder="t('submission.feedback.form.placeholder.description')"></textarea>
          </div>

          <div class="form-group">
            <label>{{ t('submission.feedback.form.attachments') }}</label>
            <input type="file" multiple accept=".jpg,.png,.pdf" @change="handleFileUpload">
            <div class="file-list">
              <span v-for="file in form.attachments" :key="file.name" class="file-tag">{{ file.name }}</span>
            </div>
          </div>

          <div class="form-group">
            <label>{{ t('submission.feedback.form.contact') }}</label>
            <input type="email" v-model="form.contact" required>
          </div>

          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? t('common.loading') : t('common.submit') }}
          </button>
        </form>
      </div>

      <!-- Feedback List (My / All) -->
      <div v-if="activeTab === 'my-feedback' || activeTab === 'all-feedback'" class="tab-content">
        <div v-if="selectedFeedback" class="feedback-detail">
          <button @click="closeDetail" class="btn-back">&larr; Back to List</button>
          
          <div class="detail-header">
            <h2>{{ selectedFeedback.title }}</h2>
            <span class="status-badge" :class="selectedFeedback.status.toLowerCase()">{{ selectedFeedback.status }}</span>
          </div>
          
          <div class="detail-meta">
             <p><strong>ID:</strong> {{ selectedFeedback.id }}</p>
             <p><strong>Type:</strong> {{ selectedFeedback.type }}</p>
             <p><strong>Submitted:</strong> {{ formatDate(selectedFeedback.createdAt) }}</p>
             <p><strong>User:</strong> {{ selectedFeedback.userId }} ({{ selectedFeedback.email }})</p>
          </div>

          <div class="detail-body">
            <p>{{ selectedFeedback.description }}</p>
            <div v-if="selectedFeedback.attachments && selectedFeedback.attachments.length" class="attachments">
              <strong>Attachments:</strong>
              <ul>
                <li v-for="file in selectedFeedback.attachments" :key="file">{{ file }}</li>
              </ul>
            </div>
          </div>

          <!-- Replies -->
          <div class="replies-section">
            <h3>Replies</h3>
            <div v-if="selectedFeedback.replies.length === 0" class="no-replies">No replies yet.</div>
            <div v-for="(reply, idx) in selectedFeedback.replies" :key="idx" class="reply-card">
              <div class="reply-meta">
                <strong>{{ reply.author }}</strong> ({{ reply.role }}) - {{ formatDate(reply.time) }}
              </div>
              <div class="reply-content">{{ reply.content }}</div>
            </div>
          </div>

          <!-- Editor Actions -->
          <div v-if="isEditor" class="editor-actions">
            <h3>Editor Actions</h3>
            <div class="status-control">
              <label>Update Status:</label>
              <select :value="selectedFeedback.status" @change="e => updateStatus(e.target.value)">
                <option value="Pending">Pending</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div class="reply-box">
              <textarea v-model="replyContent" placeholder="Write a reply..."></textarea>
              <button @click="submitReply">Reply</button>
            </div>
          </div>

          <!-- User Rating (If Resolved) -->
          <div v-if="selectedFeedback.status === 'Resolved' && !isEditor" class="rating-section">
            <h3>Satisfaction Rating</h3>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="submitRating(n)" :class="{ active: n <= selectedFeedback.rating }">★</span>
            </div>
          </div>
        </div>

        <div v-else class="feedback-list">
          <table v-if="(activeTab === 'my-feedback' ? myFeedbacks : allFeedbacks).length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Submitted</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fb in (activeTab === 'my-feedback' ? myFeedbacks : allFeedbacks)" :key="fb.id">
                <td>{{ fb.id }}</td>
                <td>{{ fb.title }}</td>
                <td>{{ fb.type }}</td>
                <td>{{ formatDate(fb.createdAt) }}</td>
                <td><span class="status-badge" :class="fb.status.toLowerCase()">{{ fb.status }}</span></td>
                <td><button @click="viewFeedback(fb)" class="btn-view">View</button></td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-state">No feedback found.</div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.feedback-page {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

h1 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 2rem;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 600;
  color: #7f8c8d;
}

.tabs button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #34495e;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
}

.btn-submit {
  width: 100%;
  padding: 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover {
  background-color: #2980b9;
}

.success-alert {
  background-color: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.feedback-list table {
  width: 100%;
  border-collapse: collapse;
}

.feedback-list th, .feedback-list td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.pending { background-color: #fff3cd; color: #856404; }
.status-badge.resolved { background-color: #d4edda; color: #155724; }
.status-badge.closed { background-color: #e2e3e5; color: #383d41; }

.btn-view {
  padding: 0.3rem 0.8rem;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.detail-meta p {
  margin: 0.3rem 0;
  color: #666;
}

.detail-body {
  margin: 2rem 0;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.replies-section {
  margin-top: 2rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.reply-card {
  background: #f1f9fe;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.reply-meta {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.editor-actions {
  margin-top: 2rem;
  border-top: 2px dashed #eee;
  padding-top: 1rem;
  background: #fff8e1;
  padding: 1rem;
  border-radius: 4px;
}

.reply-box textarea {
  width: 100%;
  height: 80px;
  margin-bottom: 0.5rem;
}

.stars {
  font-size: 2rem;
  color: #ccc;
  cursor: pointer;
}

.stars span.active {
  color: #f1c40f;
}

.btn-back {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}

.file-tag {
  display: inline-block;
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8rem;
  margin-right: 5px;
  margin-top: 5px;
}
</style>
