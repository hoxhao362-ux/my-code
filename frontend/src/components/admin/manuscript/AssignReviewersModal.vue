<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object,
  currentUser: Object
})

const emit = defineEmits(['close', 'send-invitations', 'save-draft'])

// State
const isLoading = ref(true)
const activeTab = ref('system') // 'system' or 'manual'
const invitationCollapsed = ref(false)
const searchQuery = ref('')
const selectedField = ref('')
const showNewReviewerModal = ref(false)
const showConfirmation = ref(false)
const isSending = ref(false)
const isSuccess = ref(false)
const hideIdentity = ref(true)

// Form Data
const invitation = reactive({
  subject: '',
  content: '',
  deadline: '2 Weeks'
})

// Mock Data for Reviewers
const systemReviewers = ref([])
const manualReviewers = ref([])
const selectedReviewers = ref([])

// New Reviewer Form
const newReviewer = reactive({
  name: '',
  email: '',
  institution: '',
  field: ''
})

// Constants
const fields = ['Oncology', 'Public Health', 'Cardiology', 'Neurology', 'Genetics']
const deadlineOptions = ['1 Week', '2 Weeks', '3 Weeks', '4 Weeks']

// Methods
const initData = () => {
  isLoading.value = true
  setTimeout(() => {
    // Mock System Recommended Reviewers
    systemReviewers.value = [
      { id: 'r1', name: 'Dr. Alice Smith', institution: 'Harvard Medical School', field: 'Oncology', score: 95, completionRate: '98%', cycle: '14 days', coi: false, type: 'Discipline Expert' },
      { id: 'r2', name: 'Dr. Bob Jones', institution: 'Johns Hopkins', field: 'Public Health', score: 88, completionRate: '92%', cycle: '18 days', coi: false, type: 'Statistics Expert' },
      { id: 'r3', name: 'Dr. Charlie Brown', institution: 'Mayo Clinic', field: 'Oncology', score: 85, completionRate: '85%', cycle: '21 days', coi: true, type: 'Discipline Expert' } // COI
    ]
    
    // Mock Manual Reviewers Pool (filtered by search later)
    manualReviewers.value = [
      { id: 'r4', name: 'Dr. David Lee', institution: 'UCSF', field: 'Cardiology', completionRate: '90%', cycle: '15 days' },
      { id: 'r5', name: 'Dr. Eva Green', institution: 'Oxford', field: 'Genetics', completionRate: '88%', cycle: '20 days' },
       { id: 'r6', name: 'Dr. Frank White', institution: 'Stanford', field: 'Oncology', completionRate: '95%', cycle: '12 days' }
    ]

    // Load Draft if exists
    const draft = localStorage.getItem(`assignment_draft_${props.manuscript?.id}`)
    if (draft) {
      const data = JSON.parse(draft)
      selectedReviewers.value = data.reviewers || []
      Object.assign(invitation, data.invitation)
    } else {
      // Default Invitation
      invitation.subject = `Invitation to Review: ${props.manuscript?.title || 'Manuscript'}`
      invitation.content = `Dear Dr. [Name],\n\nWe would like to invite you to review the manuscript titled "${props.manuscript?.title}".\n\nAbstract: ${props.manuscript?.abstract || '[Abstract]'}\n\nPlease let us know if you can accept this invitation.`
    }

    isLoading.value = false
  }, 1000)
}

const toggleSelection = (reviewer) => {
  if (reviewer.coi) return
  const index = selectedReviewers.value.findIndex(r => r.id === reviewer.id)
  if (index === -1) {
    selectedReviewers.value.push(reviewer)
  } else {
    selectedReviewers.value.splice(index, 1)
  }
}

const isSelected = (reviewer) => {
  return selectedReviewers.value.some(r => r.id === reviewer.id)
}

const filteredManualReviewers = computed(() => {
  return manualReviewers.value.filter(r => {
    const matchesSearch = !searchQuery.value || 
      r.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      r.institution.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesField = !selectedField.value || r.field === selectedField.value
    return matchesSearch && matchesField
  })
})

const addNewReviewer = () => {
  // Add to manual list and auto-select
  const newR = {
    id: `new_${Date.now()}`,
    name: newReviewer.name,
    institution: newReviewer.institution,
    field: newReviewer.field,
    completionRate: 'N/A',
    cycle: 'N/A',
    isNew: true
  }
  manualReviewers.value.push(newR)
  selectedReviewers.value.push(newR)
  showNewReviewerModal.value = false
  
  // Reset form
  newReviewer.name = ''
  newReviewer.email = ''
  newReviewer.institution = ''
  newReviewer.field = ''
}

const handleSaveDraft = () => {
  localStorage.setItem(`assignment_draft_${props.manuscript?.id}`, JSON.stringify({
    reviewers: selectedReviewers.value,
    invitation: invitation
  }))
  emit('save-draft')
  alert('Reviewer assignment saved as draft.')
}

const validateAndSend = () => {
  if (selectedReviewers.value.length === 0) {
    alert('Please select at least one reviewer.')
    return
  }
  
  if (hideIdentity.value) {
     alert("Reviewers assigned with blind review enabled - author will not see reviewer identities.")
  }
  
  showConfirmation.value = true
}

const confirmSend = async () => {
  isSending.value = true
  showConfirmation.value = false
  
  // Simulate API
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  isSending.value = false
  isSuccess.value = true
  
  emit('send-invitations', {
    reviewers: selectedReviewers.value,
    invitation: invitation
  })
  
  setTimeout(() => {
    emit('close')
    isSuccess.value = false
  }, 3000)
}

const cancel = () => {
  selectedReviewers.value = []
  emit('close')
}

// Watchers
watch(() => props.visible, (val) => {
  if (val) initData()
})

const requiredTypesMissing = computed(() => {
  const hasStat = selectedReviewers.value.some(r => r.type === 'Statistics Expert')
  // Simple check logic, can be more complex
  return !hasStat && activeTab.value === 'system'
})

</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-container">
      <!-- Skeleton -->
      <div v-if="isLoading" class="skeleton-screen">
         <div class="sk-header"></div>
         <div class="sk-body"></div>
      </div>

      <template v-else>
        <!-- Success Overlay -->
        <div v-if="isSuccess" class="success-overlay">
           <div class="success-content">
             <div class="success-icon">✓</div>
             <h3>Invitations sent successfully</h3>
           </div>
        </div>

        <!-- 1. Manuscript Basic Info (Top, Fixed) -->
        <header class="modal-header">
          <div class="header-top">
            <h2>Assign Reviewers - [{{ manuscript.id }}] Assign Reviewers</h2>
            <button class="close-btn" @click="cancel" :disabled="isSuccess">Close</button>
          </div>
          <div class="info-grid">
            <div class="info-item"><span>Title:</span> {{ manuscript.title }}</div>
            <div class="info-item"><span>Field:</span> {{ manuscript.module || manuscript.field }}</div>
            <div class="info-item"><span>Keywords:</span> {{ manuscript.keywords || 'N/A' }}</div>
            <div class="info-item"><span>Type:</span> {{ manuscript.type || 'Original Research' }}</div>
          </div>
          <div class="header-actions">
            <button class="btn-link">View Manuscript Abstract</button>
            <button class="btn-link">View Methodology Description</button>
          </div>
        </header>

        <!-- Scrollable Body -->
        <div class="modal-body">
          <!-- 2. Reviewer Candidates -->
          <section class="candidates-section">
            <div class="tabs">
              <button :class="{ active: activeTab === 'system' }" @click="activeTab = 'system'">System Recommended</button>
              <button :class="{ active: activeTab === 'manual' }" @click="activeTab = 'manual'">Manual Selection</button>
            </div>

            <!-- System Recommended -->
            <div v-if="activeTab === 'system'" class="reviewers-list">
              <div v-for="reviewer in systemReviewers" :key="reviewer.id" class="reviewer-card" :class="{ 'coi-disabled': reviewer.coi, 'selected': isSelected(reviewer) }">
                <div class="card-left">
                  <input type="checkbox" :checked="isSelected(reviewer)" @change="toggleSelection(reviewer)" :disabled="reviewer.coi">
                  <div class="reviewer-info">
                    <h4>{{ reviewer.name }} <span v-if="reviewer.coi" class="tag-coi">Conflict of Interest</span></h4>
                    <p>{{ reviewer.institution }} | {{ reviewer.field }}</p>
                    <div class="stats">
                      <span>Score: {{ reviewer.score }}</span>
                      <span>Completion: {{ reviewer.completionRate }}</span>
                      <span>Cycle: {{ reviewer.cycle }}</span>
                    </div>
                  </div>
                </div>
                <div class="card-right">
                   <span class="tag-type" v-if="reviewer.type">{{ reviewer.type }}</span>
                   <button class="btn-text">View Details</button>
                </div>
              </div>
              <div v-if="requiredTypesMissing" class="warning-msg">
                Please add the required type of reviewers (e.g., Statistics Expert)
              </div>
            </div>

            <!-- Manual Selection -->
            <div v-if="activeTab === 'manual'" class="manual-section">
              <div class="manual-filters">
                <input v-model="searchQuery" placeholder="Search by Name, Institution..." class="search-input">
                <select v-model="selectedField" class="filter-select">
                  <option value="">All Fields</option>
                  <option v-for="f in fields" :key="f" :value="f">{{ f }}</option>
                </select>
                <button class="btn-outline" @click="showNewReviewerModal = true">+ Add New Reviewer</button>
              </div>
              
              <div class="reviewers-list">
                 <div v-for="reviewer in filteredManualReviewers" :key="reviewer.id" class="reviewer-card" :class="{ 'selected': isSelected(reviewer) }">
                   <div class="card-left">
                     <input type="checkbox" :checked="isSelected(reviewer)" @change="toggleSelection(reviewer)">
                     <div class="reviewer-info">
                       <h4>{{ reviewer.name }}</h4>
                       <p>{{ reviewer.institution }} | {{ reviewer.field }}</p>
                       <div class="stats">
                         <span>Completion: {{ reviewer.completionRate }}</span>
                         <span>Cycle: {{ reviewer.cycle }}</span>
                       </div>
                     </div>
                   </div>
                 </div>
              </div>
            </div>
          </section>

          <!-- 3. Invitation Editing -->
          <section class="invitation-section" :class="{ collapsed: invitationCollapsed }">
            <div class="section-header" @click="invitationCollapsed = !invitationCollapsed">
              <h3>Invitation Editing ({{ selectedReviewers.length }} Selected)</h3>
              <span class="arrow">{{ invitationCollapsed ? '▼' : '▲' }}</span>
            </div>
            
            <div v-show="!invitationCollapsed" class="invitation-form">
              <div class="form-row">
                <label>Deadline:</label>
                <select v-model="invitation.deadline">
                  <option v-for="d in deadlineOptions" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
              <div class="form-row">
                <label>Subject:</label>
                <input v-model="invitation.subject" class="full-width">
              </div>
              <div class="form-row">
                 <label>Content:</label>
                 <textarea v-model="invitation.content" rows="6" class="full-width"></textarea>
              </div>
              <button class="btn-outline small">Preview</button>
            </div>
            
            <div v-show="!invitationCollapsed" class="blind-review-option">
              <label class="checkbox-label">
                <input type="checkbox" v-model="hideIdentity" disabled>
                <span class="brand-red-text">Hide reviewer identity from authors</span>
              </label>
              <p class="helper-text">Reviewer names and affiliations will remain anonymous to authors.</p>
            </div>
          </section>
        </div>

        <!-- 4. Action Buttons (Bottom, Fixed) -->
        <footer class="modal-footer">
          <button class="btn btn-secondary" @click="handleSaveDraft">Save Draft</button>
          <button class="btn btn-cancel" @click="cancel">Cancel</button>
          <button 
            class="btn btn-primary" 
            :disabled="selectedReviewers.length === 0"
            @click="validateAndSend"
          >
            Send Invitations
          </button>
        </footer>
      </template>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmation" class="confirm-modal">
      <div class="confirm-content">
        <h3>Confirm to send reviewer invitations?</h3>
        <div class="confirm-actions">
          <button class="btn btn-cancel" @click="showConfirmation = false">Cancel</button>
          <button class="btn btn-primary" @click="confirmSend">Confirm</button>
        </div>
      </div>
    </div>

    <!-- Add New Reviewer Modal (Simplified) -->
    <div v-if="showNewReviewerModal" class="sub-modal">
       <div class="sub-modal-content">
         <h3>Add New Reviewer</h3>
         <input v-model="newReviewer.name" placeholder="Name">
         <input v-model="newReviewer.email" placeholder="Email">
         <input v-model="newReviewer.institution" placeholder="Institution">
         <select v-model="newReviewer.field">
           <option value="" disabled>Select Field</option>
           <option v-for="f in fields" :key="f" :value="f">{{ f }}</option>
         </select>
         <div class="actions">
           <button @click="showNewReviewerModal = false">Cancel</button>
           <button class="btn-primary" @click="addNewReviewer">Add</button>
         </div>
       </div>
    </div>

  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 2000;
}
.modal-container {
  background: white; width: 900px; height: 90vh;
  display: flex; flex-direction: column;
  border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  position: relative;
}
.modal-header {
  padding: 1.5rem; border-bottom: 1px solid #eee;
}
.header-top { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.9rem; }
.info-item span { font-weight: 600; color: #7f8c8d; margin-right: 0.5rem; }
.header-actions { margin-top: 1rem; display: flex; gap: 1rem; }

.modal-body { flex: 1; overflow-y: auto; padding: 1.5rem; background: #f9f9f9; }

.tabs { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 1rem; }
.tabs button {
  padding: 0.8rem 1.5rem; background: none; border: none; cursor: pointer;
  border-bottom: 2px solid transparent;
}
.tabs button.active { border-bottom-color: #3498db; color: #3498db; font-weight: bold; }

.reviewers-list { display: flex; flex-direction: column; gap: 0.8rem; }
.reviewer-card {
  background: white; padding: 1rem; border-radius: 6px; border: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.reviewer-card.selected { border-color: #3498db; background: #f0f8ff; }
.reviewer-card.coi-disabled { opacity: 0.7; background: #fff5f5; }

.card-left { display: flex; gap: 1rem; align-items: center; }
.reviewer-info h4 { margin: 0 0 0.2rem 0; }
.tag-coi { background: #e74c3c; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; margin-left: 0.5rem; }
.stats { font-size: 0.8rem; color: #7f8c8d; margin-top: 0.3rem; display: flex; gap: 1rem; }

.card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }
.tag-type { background: #e8f6f3; color: #1abc9c; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; }
.btn-text { background: none; border: none; color: #3498db; cursor: pointer; text-decoration: underline; font-size: 0.85rem; }

.warning-msg { color: #e74c3c; margin-top: 1rem; font-size: 0.9rem; font-weight: 500; }

.invitation-section { background: white; margin-top: 1.5rem; border-radius: 6px; padding: 1rem; border: 1px solid #eee; }
.section-header { display: flex; justify-content: space-between; cursor: pointer; font-weight: bold; }
.invitation-form { margin-top: 1rem; }
.form-row { margin-bottom: 1rem; }
.full-width { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }

.blind-review-option {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #eee;
}
.brand-red-text {
  color: #C93737;
  font-weight: 600;
  margin-left: 8px;
}
.helper-text {
  margin: 4px 0 0 24px;
  font-size: 12px;
  color: #999;
}

.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; background: white; }
.btn { padding: 0.6rem 1.5rem; border-radius: 4px; border: none; cursor: pointer; }
.btn-primary { background: #3498db; color: white; }
.btn-primary:disabled { background: #bdc3c7; cursor: not-allowed; }
.btn-secondary { background: white; border: 1px solid #ddd; }
.btn-cancel { background: #e74c3c; color: white; }
.btn-outline { background: transparent; border: 1px solid #3498db; color: #3498db; padding: 0.4rem 1rem; border-radius: 4px; cursor: pointer; }

/* Overlays */
.confirm-modal, .sub-modal {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 2100;
}
.confirm-content, .sub-modal-content {
  background: white; padding: 2rem; border-radius: 8px; width: 400px;
}
.confirm-actions, .actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }

.success-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.95); display: flex; justify-content: center; align-items: center; z-index: 2200;
}
.success-icon { font-size: 2rem; color: #27ae60; margin-bottom: 1rem; }

.manual-filters { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.search-input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; flex: 1; }
.filter-select { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }

.skeleton-screen { padding: 2rem; }
.sk-header { height: 100px; background: #eee; margin-bottom: 2rem; }
.sk-body { height: 400px; background: #eee; }
</style>
