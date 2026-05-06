<script setup>
import { ref, reactive, computed } from 'vue'
import { useToastStore } from '../../../stores/toast'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const toastStore = useToastStore()

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  },
  currentUser: Object
})

const emit = defineEmits(['close', 'submit', 'save-draft'])

// Checklist Data Structure
const checklistModules = reactive([
  {
    id: 1,
    title: 'Basic Information Completeness',
    desc: 'Verify that basic manuscript information is complete and accurate to avoid issues in subsequent processes.',
    items: [
      { id: '1-1', text: 'Manuscript title, abstract, and keywords are complete, standardized, without typos or ambiguity.', status: null, remark: '' },
      { id: '1-2', text: 'Author count and order match the submission declaration (check count only for blind review).', status: null, remark: '' },
      { id: '1-3', text: 'Corresponding author email and affiliation are valid and contactable.', status: null, remark: '' },
      { id: '1-4', text: 'Submission type and research field are correctly selected and match manuscript content.', status: null, remark: '' },
      { id: '1-5', text: 'Author submission declaration and conflict of interest statement have been submitted.', status: null, remark: '' }
    ]
  },
  {
    id: 2,
    title: 'Double-Blind Review Anonymity Compliance',
    desc: 'Verify that the manuscript is fully anonymized with no author identity leakage, strictly following double-blind review requirements.',
    items: [
      { id: '2-1', text: 'Main text contains no author names, affiliations, emails, or ORCID identifiers.', status: null, remark: '' },
      { id: '2-2', text: 'Figures, figure legends, table notes, headers, and footers contain no identity information.', status: null, remark: '' },
      { id: '2-3', text: 'Acknowledgments and funding sections have been anonymized.', status: null, remark: '' },
      { id: '2-4', text: 'Self-citations in references are anonymized without leaking author information.', status: null, remark: '' },
      { id: '2-5', text: 'Supplementary materials contain no identifiable author content.', status: null, remark: '' }
    ]
  },
  {
    id: 3,
    title: 'Format and Typesetting Standards',
    desc: 'Verify that manuscript format meets journal standards (Times New Roman, 1.5 spacing, etc.) for review and typesetting.',
    items: [
      { id: '3-1', text: 'Font, line spacing, and margins meet requirements (Times New Roman, 1.5 spacing, standard margins).', status: null, remark: '' },
      { id: '3-2', text: 'Figures and tables are clear, strictly numbered, and correspond to the text.', status: null, remark: '' },
      { id: '3-3', text: 'References are consistent and follow journal standards (Vancouver style).', status: null, remark: '' },
      { id: '3-4', text: 'Paragraphs and heading hierarchy are clear and not confused.', status: null, remark: '' },
      { id: '3-5', text: 'Manuscript files open normally without damage or garbled text.', status: null, remark: '' }
    ]
  },
  {
    id: 4,
    title: 'Content Integrity and Academic Basis',
    desc: 'Verify that academic content is complete and meets the basic conditions for peer review.',
    items: [
      { id: '4-1', text: 'Research purpose is clear and the topic is within the journal scope.', status: null, remark: '' },
      { id: '4-2', text: 'Methods, results, and discussion structures are complete without omissions.', status: null, remark: '' },
      { id: '4-3', text: 'Data and figures support the conclusions without obvious contradictions.', status: null, remark: '' },
      { id: '4-4', text: 'No large blank spaces, garbled text, or missing pages.', status: null, remark: '' },
      { id: '4-5', text: 'Language is fluent and does not affect understanding or review.', status: null, remark: '' }
    ]
  },
  {
    id: 5,
    title: 'Ethics and Academic Compliance',
    desc: 'Verify ethical compliance to prevent conflicts of interest, ethical violations, and academic misconduct.',
    items: [
      { id: '5-1', text: 'Conflict of interest statement submitted, complete, and anonymized.', status: null, remark: '' },
      { id: '5-2', text: 'Human research ethics approval number provided; ethics statement complete (N/A if not applicable).', status: null, remark: '', allowNA: true },
      { id: '5-3', text: 'Animal research ethics approval provided; follows 3R principles (N/A if not applicable).', status: null, remark: '', allowNA: true },
      { id: '5-4', text: 'No suspicion of fabricated data, falsified figures, or plagiarism.', status: null, remark: '' },
      { id: '5-5', text: 'Citations of others work are standardized without infringement or plagiarism suspicion.', status: null, remark: '' }
    ]
  },
  {
    id: 6,
    title: 'Other Supplementary Checks',
    desc: 'Verify supplementary checks to ensure no other violations or omissions.',
    items: [
      { id: '6-1', text: 'Attachments (ethics files, raw data) open normally without damage.', status: null, remark: '' },
      { id: '6-2', text: 'No irrelevant attachments submitted (e.g., CVs, unrelated data).', status: null, remark: '' },
      { id: '6-3', text: 'No obvious language errors (spelling, grammar) affecting reading.', status: null, remark: '' },
      { id: '6-4', text: 'Title and abstract contain no sensitive vocabulary or ambiguity.', status: null, remark: '' }
    ]
  }
])

const summaryOpinion = ref('')
const finalDecision = ref('') // 'pass', 'revise', 'reject'
const isSubmitting = ref(false)

// Computed Validation
const isFormValid = computed(() => {
  // 1. All items must have a status
  for (const module of checklistModules) {
    for (const item of module.items) {
      if (!item.status) return false
      // 2. If 'No', remark is required
      if (item.status === 'No' && !item.remark.trim()) return false
    }
  }
  // 3. Summary required (> 50 chars)
  if (summaryOpinion.value.length < 50) return false
  // 4. Decision required
  if (!finalDecision.value) return false
  
  return true
})

// Methods
const handleStatusChange = (item, status) => {
  item.status = status
  if (status !== 'No') {
    item.remark = '' // Clear remark if not 'No'
  }
}

const handleSubmit = () => {
  if (!isFormValid.value) return
  isSubmitting.value = true

  // Simulate API delay
  setTimeout(() => {
    // Map decision to status
    let newStatus = ''
    if (finalDecision.value === 'pass') newStatus = MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED
    else if (finalDecision.value === 'revise') newStatus = MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION
    else if (finalDecision.value === 'reject') newStatus = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED

    emit('submit', {
      checklist: checklistModules,
      summary: summaryOpinion.value,
      decision: finalDecision.value,
      newStatus: newStatus,
      timestamp: new Date().toISOString()
    })
    isSubmitting.value = false
  }, 1000)
}

const handleSave = () => {
  emit('save-draft', {
    checklist: checklistModules,
    summary: summaryOpinion.value,
    decision: finalDecision.value
  })
  toastStore.add({ message: 'Progress Saved', type: 'success' })
}

</script>

<template>
  <div class="checklist-container">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
<<<<<<< HEAD
        <h2 class="title">Structured Initial Review Checklist (Journal Platform Compliance)</h2>
=======
        <h2 class="title">Structured Initial Review Checklist (Peerex Peer Compliance)</h2>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
        <p class="subtitle">Please check item by item. All items must be verified. Remarks required for non-compliant items.</p>
      </div>
      <div class="header-right">
        <div class="meta">Manuscript ID: {{ manuscript.id }}</div>
        <div class="meta-title">{{ manuscript.title }}</div>
        <div class="meta-field">{{ manuscript.field }}</div>
      </div>
    </header>
    
    <div class="divider"></div>

    <!-- Checklist Body -->
    <div class="checklist-body">
      <div v-for="module in checklistModules" :key="module.id" class="module-block">
        <div class="module-header">
          <h3 class="module-title">{{ module.title }} <span class="required">*</span></h3>
          <p class="module-desc">{{ module.desc }}</p>
        </div>
        
        <div class="module-items">
          <div v-for="item in module.items" :key="item.id" class="checklist-item">
            <div class="item-main">
              <!-- Status Radios -->
              <div class="status-group" role="group" :aria-label="'Compliance status for: ' + item.text">
                <button 
                  class="status-btn yes" 
                  :class="{ active: item.status === 'Yes' }"
                  @click="handleStatusChange(item, 'Yes')"
                  title="Compliant"
                  aria-label="Compliant"
                  :aria-pressed="item.status === 'Yes'"
                >✓</button>
                <button 
                  class="status-btn no" 
                  :class="{ active: item.status === 'No' }"
                  @click="handleStatusChange(item, 'No')"
                  title="Non-Compliant"
                  aria-label="Non-Compliant"
                  :aria-pressed="item.status === 'No'"
                >✕</button>
                <button 
                  v-if="item.allowNA"
                  class="status-btn na" 
                  :class="{ active: item.status === 'NA' }"
                  @click="handleStatusChange(item, 'NA')"
                  title="Not Applicable"
                  aria-label="Not Applicable"
                  :aria-pressed="item.status === 'NA'"
                >-</button>
              </div>
              
              <!-- Item Text -->
              <div class="item-text" :class="{ 'text-red': item.status === 'No' }">
                {{ item.text }}
              </div>
            </div>

            <!-- Remark Input (Conditional) -->
            <div v-if="item.status === 'No'" class="remark-container">
              <label :for="'remark-' + item.id" class="remark-label">Specific Issue (Required):</label>
              <input 
                :id="'remark-' + item.id"
                v-model="item.remark" 
                type="text" 
                class="remark-input" 
                placeholder="Enter details (max 200 chars)..." 
                maxlength="200"
                aria-required="true"
              >
              <div v-if="!item.remark.trim()" class="error-text" role="alert">Remark is required for non-compliant items</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Footer / Decision -->
    <footer class="footer">
      <div class="footer-left">
        <label class="section-label">Initial Review Summary (Required) <span class="required">*</span></label>
        <textarea 
          v-model="summaryOpinion" 
          class="summary-input" 
          rows="4" 
          placeholder="Summarize the initial review findings and conclusion basis (min 50 words)..."
        ></textarea>
        <div class="word-count" :class="{ 'text-red': summaryOpinion.length < 50 }">
          Current: {{ summaryOpinion.length }} chars (Min 50)
        </div>
      </div>
      
      <div class="footer-right">
        <div class="decision-group">
          <label class="section-label">Conclusion <span class="required">*</span></label>
          <label class="radio-label">
            <input type="radio" v-model="finalDecision" value="pass"> Initial Review Passed
          </label>
          <label class="radio-label">
            <input type="radio" v-model="finalDecision" value="revise"> Return for Revision
          </label>
          <label class="radio-label">
            <input type="radio" v-model="finalDecision" value="reject"> Desk Reject
          </label>
        </div>
        
        <div class="action-buttons">
          <button class="btn btn-save" @click="handleSave">Save Progress</button>
          <button 
            class="btn btn-submit" 
            :disabled="!isFormValid || isSubmitting"
            :title="!isFormValid ? 'Please complete all required fields' : ''"
            @click="handleSubmit"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Decision' }}
          </button>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.checklist-container {
  font-family: 'Times New Roman', Times, serif;
  background: white;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  color: #333;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 5px 0;
}

.subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.meta { font-size: 14px; color: #666; font-weight: bold; }
.meta-title { font-size: 14px; color: #333; margin: 2px 0; font-style: italic; }
.meta-field { font-size: 12px; color: #999; }

.divider {
  height: 1px;
  background: #eee;
  margin: 1.5rem 0;
}

/* Modules */
.module-block { margin-bottom: 2rem; }
.module-header { margin-bottom: 1rem; border-bottom: 1px dashed #eee; padding-bottom: 5px; }
.module-title { font-size: 16px; font-weight: bold; color: #333; margin: 0; }
.module-desc { font-size: 12px; color: #999; margin: 2px 0 0 0; }
.required { color: #dc3545; }

/* Items */
.checklist-item {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f9f9f9;
}

.item-main {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.status-group {
  display: flex;
  gap: 5px;
  min-width: 100px;
}

.status-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: #999;
}

.status-btn:hover { border-color: #999; }

.status-btn.yes.active { background: #28A745; border-color: #28A745; color: white; }
.status-btn.no.active { background: #dc3545; border-color: #dc3545; color: white; }
.status-btn.na.active { background: #4A90E2; border-color: #4A90E2; color: white; }

.item-text {
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  flex: 1;
}
.text-red { color: #dc3545; }

.remark-container {
  margin-left: 115px; /* Align with text */
  margin-top: 10px;
}

.remark-label {
  font-size: 12px;
  color: #dc3545;
  font-weight: bold;
  margin-right: 10px;
}

.remark-input {
  width: 300px;
  padding: 5px;
  border: 1px solid #dc3545;
  border-radius: 4px;
  font-family: inherit;
  font-size: 13px;
}

.error-text {
  color: #dc3545;
  font-size: 12px;
  margin-top: 2px;
}

/* Footer */
.footer {
  display: flex;
  gap: 2rem;
}

.footer-left { flex: 2; }
.footer-right { flex: 1; display: flex; flex-direction: column; gap: 1.5rem; }

.section-label {
  display: block;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.summary-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
}

.word-count { font-size: 12px; color: #999; text-align: right; margin-top: 5px; }

.decision-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
}

.radio-label {
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  font-family: inherit;
}

.btn-submit {
  background: #0056B3;
  color: white;
}
.btn-submit:hover { background: #004494; }
.btn-submit:disabled { background: #ccc; cursor: not-allowed; }

.btn-save {
  background: #eee;
  color: #333;
}
.btn-save:hover { background: #ddd; }

</style>
