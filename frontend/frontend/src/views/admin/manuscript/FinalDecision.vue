<script setup>
import { ref, computed, reactive } from 'vue'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  },
  currentUser: Object,
  reviews: Array // Mock reviews
})

const emit = defineEmits(['submit', 'save-draft', 'return-materials'])

// State
const isEIC = computed(() => props.currentUser?.role === 'associate_editor' || props.currentUser?.role === 'editor') // Assuming AE/EiC has decision power
const isEditor = computed(() => props.currentUser?.role === 'editor' || props.currentUser?.role === 'ea_ae')

// Editor Form Data
const editorForm = reactive({
  reportFile: null,
  suggestion: ''
})

// EiC Form Data
const eicForm = reactive({
  decision: '', // 'accept', 'revise', 'reject'
  reasons: [],
  revisionRequirements: '',
  finalOpinion: ''
})

const decisionReasons = [
  'Strong academic innovation',
  'Consistent reviewer recommendations',
  'Rigorous research design',
  'Significant clinical/theoretical value',
  'Insufficient originality',
  'Methodological flaws',
  'Ethical concerns',
  'Out of scope'
]

// Logic
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    editorForm.reportFile = {
      name: file.name,
      date: new Date().toLocaleDateString()
    }
  }
}

const isEditorFormValid = computed(() => {
  return editorForm.reportFile && editorForm.suggestion.length >= 50
})

const isEicFormValid = computed(() => {
  if (!eicForm.decision) return false
  if (eicForm.reasons.length === 0) return false
  if (eicForm.finalOpinion.length < 100) return false
  if (eicForm.decision === 'revise' && eicForm.revisionRequirements.length < 50) return false
  return true
})

const submitEditor = () => {
  if (!isEditorFormValid.value) return
  emit('submit', {
    role: 'editor',
    data: { ...editorForm },
    nextStatus: MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
  })
}

const submitEic = () => {
  if (!isEicFormValid.value) return
  
  let nextStatus = ''
  if (eicForm.decision === 'accept') nextStatus = MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED // -> Pending Confirmation
  else if (eicForm.decision === 'revise') nextStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
  else if (eicForm.decision === 'reject') nextStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED

  emit('submit', {
    role: 'eic',
    data: { ...eicForm },
    nextStatus: nextStatus
  })
}

</script>

<template>
  <div class="final-decision-container">
    
    <!-- Editor Interface (Preparation) -->
    <div v-if="!isEIC" class="role-view editor-view">
      <div class="left-col">
        <h3 class="col-title">Final Decision Preparation</h3>
        
        <div class="module">
          <label class="required">Upload Peer Review Summary Report</label>
          <div v-if="!editorForm.reportFile" class="upload-box">
            <input type="file" @change="handleFileUpload" class="file-input">
            <button class="btn btn-primary">Upload File</button>
            <div class="error-text">Report is required</div>
          </div>
          <div v-else class="file-info">
            📄 {{ editorForm.reportFile.name }} ({{ editorForm.reportFile.date }})
            <button @click="editorForm.reportFile = null" class="btn-text">Remove</button>
          </div>
        </div>

        <div class="module">
          <label>Initial Review Records</label>
          <button class="btn btn-gray-outline">View Online</button>
        </div>

        <div class="module">
          <label class="required">Editor's Suggestion</label>
          <textarea 
            v-model="editorForm.suggestion" 
            placeholder="Suggest Accept/Revise/Reject with reasons (min 50 words)..."
            rows="4"
          ></textarea>
          <div class="word-count" :class="{ 'text-red': editorForm.suggestion.length < 50 }">
            {{ editorForm.suggestion.length }} chars
          </div>
        </div>
      </div>

      <div class="right-col">
        <h3 class="col-title">Manuscript & Review Info</h3>
        <div class="info-block">
          <p><strong>ID:</strong> {{ manuscript.id }}</p>
          <p><strong>Title:</strong> {{ manuscript.title }}</p>
          <p><strong>Field:</strong> {{ manuscript.field }}</p>
        </div>
        
        <div class="reviews-list">
          <h4>Peer Review Details</h4>
          <div v-for="(r, i) in reviews" :key="i" class="review-item">
            <div class="review-header">
              <span>Reviewer {{ i + 1 }}</span>
              <span class="decision-tag" :class="r.recommendation">{{ r.recommendation }}</span>
            </div>
            <p class="review-summary">{{ r.summary }}</p>
            <button class="btn-text">View Full Report</button>
          </div>
          <div v-if="!reviews || reviews.length === 0">No reviews available.</div>
        </div>
      </div>
      
      <div class="bottom-bar">
        <button class="btn btn-gray" @click="$emit('save-draft')">Save Draft</button>
        <button 
          class="btn btn-primary" 
          :disabled="!isEditorFormValid"
          @click="submitEditor"
        >
          Submit to Editor-in-Chief
        </button>
      </div>
    </div>

    <!-- EiC Interface (Decision) -->
    <div v-if="isEIC" class="role-view eic-view">
      <header class="page-header">
        <h2>Final Decision (Peerex Peer Compliance)</h2>
        <div class="meta">
          <span>ID: {{ manuscript.id }}</span>
          <span>EiC: {{ currentUser.name }}</span>
        </div>
      </header>
      
      <div class="split-layout">
        <!-- Left: Materials -->
        <div class="left-panel">
          <h3 class="panel-title">Review Materials</h3>
          <div class="material-list">
            <div class="material-item">
              <span>Initial Review Checklist</span>
              <button class="btn-sm">View</button>
            </div>
            <div class="material-item">
              <span>Peer Review Reports ({{ reviews ? reviews.length : 0 }})</span>
              <button class="btn-sm">View All</button>
            </div>
            <div class="material-item">
              <span>Editor's Summary Report</span>
              <button class="btn-sm">View</button>
            </div>
          </div>
        </div>

        <!-- Right: Decision -->
        <div class="right-panel">
          <h3 class="panel-title">Final Decision <span class="required">*</span></h3>
          
          <div class="form-group">
            <label class="label">Decision</label>
            <div class="radio-group">
              <label><input type="radio" v-model="eicForm.decision" value="accept"> Accept (Direct)</label>
              <label><input type="radio" v-model="eicForm.decision" value="revise"> Revision Required</label>
              <label><input type="radio" v-model="eicForm.decision" value="reject"> Reject</label>
            </div>
          </div>

          <div class="form-group">
            <label class="label">Decision Rationale (Select all that apply)</label>
            <div class="checkbox-grid">
              <label v-for="r in decisionReasons" :key="r">
                <input type="checkbox" :value="r" v-model="eicForm.reasons"> {{ r }}
              </label>
            </div>
          </div>

          <div v-if="eicForm.decision === 'revise'" class="form-group">
            <label class="label required">Revision Requirements</label>
            <textarea 
              v-model="eicForm.revisionRequirements" 
              placeholder="Specific requirements for revision (min 50 chars)..."
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="label required">Final Decision Opinion</label>
            <textarea 
              v-model="eicForm.finalOpinion" 
              placeholder="Comprehensive decision opinion (min 100 chars)..."
              rows="5"
            ></textarea>
            <div class="word-count" :class="{ 'text-red': eicForm.finalOpinion.length < 100 }">
              {{ eicForm.finalOpinion.length }} chars (Min 100)
            </div>
          </div>

        </div>
      </div>

      <div class="bottom-bar">
        <button class="btn btn-gray" @click="$emit('return-materials')">Return for Materials</button>
        <button class="btn btn-gray" @click="$emit('save-draft')">Save Draft</button>
        <button 
          class="btn btn-primary" 
          :disabled="!isEicFormValid"
          @click="submitEic"
        >
          Submit Final Decision
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.final-decision-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: white;
  padding: 20px;
  height: 100%;
  color: #333;
}

/* Common */
.required::after { content: " *"; color: #dc3545; }
.text-red { color: #dc3545; }
.btn { padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }
.btn-primary { background: #0056B3; color: white; }
.btn-primary:hover { background: #004494; }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }
.btn-gray { background: #eee; color: #333; }
.btn-gray-outline { border: 1px solid #ddd; background: white; color: #333; padding: 4px 8px; }
.btn-text { background: none; border: none; color: #666; text-decoration: underline; cursor: pointer; }

/* Editor View */
.editor-view { display: flex; gap: 20px; flex-wrap: wrap; }
.left-col, .right-col { flex: 1; min-width: 300px; }
.col-title { font-size: 16px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 5px; margin-bottom: 15px; }

.module { margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; }
.upload-box { border: 1px dashed #0056B3; padding: 15px; text-align: center; }
.file-input { display: none; } /* Use label trigger or similar in real app, simplified here */
textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; }

.reviews-list { margin-top: 15px; }
.review-item { border-bottom: 1px solid #eee; padding: 10px 0; }
.review-header { display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; }
.decision-tag.Accept { color: green; }
.decision-tag.Reject { color: #dc3545; }
.review-summary { font-size: 13px; color: #666; margin: 5px 0; }

/* EiC View */
.page-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
.split-layout { display: flex; gap: 20px; border: 1px solid #eee; height: 500px; }
.left-panel { width: 40%; border-right: 1px solid #eee; padding: 15px; overflow-y: auto; background: #fcfcfc; }
.right-panel { width: 60%; padding: 15px; overflow-y: auto; }
.panel-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; }

.material-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; background: white; margin-bottom: 5px; }
.btn-sm { padding: 2px 8px; font-size: 12px; }

.form-group { margin-bottom: 15px; }
.label { display: block; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
.radio-group { display: flex; gap: 15px; }
.checkbox-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 14px; }

.bottom-bar { 
  margin-top: 20px; 
  display: flex; 
  justify-content: center; 
  gap: 15px; 
  width: 100%; 
  border-top: 1px solid #eee; 
  padding-top: 20px; 
}

</style>
