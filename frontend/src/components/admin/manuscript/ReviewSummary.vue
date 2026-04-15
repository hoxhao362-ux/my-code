<script setup>
import { ref, computed, reactive } from 'vue'
import { useToastStore } from '../../../stores/toast'

const toastStore = useToastStore()

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  },
  reviews: {
    type: Array,
    default: () => [
      { id: 1, reviewerName: 'Reviewer 1', conclusion: 'Accept', content: 'The study is well-designed and the results are significant. I recommend publication.' },
      { id: 2, reviewerName: 'Reviewer 2', conclusion: 'Revise', content: 'The methodology needs clarification in section 2.3. Also, figure 4 is unclear.' },
      { id: 3, reviewerName: 'Reviewer 3', conclusion: 'Reject', content: 'The sample size is too small to draw robust conclusions. The novelty is limited.' }
    ]
  }
})

const emit = defineEmits(['submit', 'save-draft'])

// Form State
const summaryForm = reactive({
  consensus: '',
  divergence: '',
  coreRequirements: '',
  editorSupplement: ''
})

const isSubmitting = ref(false)

// Computed Statistics
const stats = computed(() => {
  const accept = props.reviews.filter(r => r.conclusion === 'Accept').length
  const revise = props.reviews.filter(r => r.conclusion === 'Revise').length
  const reject = props.reviews.filter(r => r.conclusion === 'Reject').length
  return { accept, revise, reject, total: props.reviews.length }
})

const isFormValid = computed(() => {
  return summaryForm.consensus.trim() && 
         summaryForm.divergence.trim() && 
         summaryForm.coreRequirements.trim()
})

// Toggle View for Original Reviews
const expandedReviews = ref({})
const toggleReview = (id) => {
  expandedReviews.value[id] = !expandedReviews.value[id]
}

const generateReport = () => {
  if (!isFormValid.value) return
  toastStore.add({ message: 'Report Generated. Ready to Submit.', type: 'success' })
}

const handleSubmit = () => {
  if (!isFormValid.value) return
  isSubmitting.value = true
  
  // Simulate API
  setTimeout(() => {
    emit('submit', { ...summaryForm })
    isSubmitting.value = false
  }, 1000)
}

</script>

<template>
  <div class="summary-container">
    <!-- Header -->
    <header class="header">
      <h2 class="title">Review Summary Structure</h2>
      <p class="subtitle">Complete summary of all reviewer comments required. Explicit consensus and divergence needed. Cannot submit to Final Decision if incomplete.</p>
      
      <div class="meta-info">
        <span>ID: {{ manuscript.id }}</span>
        <span>Title: {{ manuscript.title }}</span>
        <span>Reviewers: {{ stats.total }}</span>
        <span>Completed: {{ new Date().toLocaleDateString() }}</span>
      </div>
    </header>
    
    <div class="divider"></div>

    <div class="content-body">
      <!-- Left: Original Reviews -->
      <div class="col-left">
        <h3 class="col-title">Original Reviewer Comments (Anonymized)</h3>
        <div class="review-list">
          <div v-for="r in reviews" :key="r.id" class="review-item">
            <div class="review-header">
              <span class="reviewer-id">{{ r.reviewerName }}</span>
              <span class="conclusion-badge" :class="r.conclusion.toLowerCase()">{{ r.conclusion }}</span>
            </div>
            <div class="review-text">
              <p>{{ expandedReviews[r.id] ? r.content : r.content.substring(0, 150) + '...' }}</p>
            </div>
            <button class="btn-text" @click="toggleReview(r.id)">
              {{ expandedReviews[r.id] ? 'Collapse' : 'View Full Comments' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Structured Summary -->
      <div class="col-right">
        <h3 class="col-title">Review Summary Structure (Required)</h3>
        
        <!-- Module 1: Stats -->
        <div class="module">
          <label class="label">Reviewer Conclusion Statistics</label>
          <div class="stats-row">
            <span class="stat-item green">Accept: {{ stats.accept }}</span>
            <span class="stat-item orange">Revise: {{ stats.revise }}</span>
            <span class="stat-item red">Reject: {{ stats.reject }}</span>
          </div>
        </div>

        <!-- Module 2: Consensus -->
        <div class="module">
          <label class="label required">Consensus Opinion</label>
          <textarea 
            v-model="summaryForm.consensus" 
            placeholder="List points agreed upon by all reviewers (strengths, issues)..."
            class="input-area"
          ></textarea>
        </div>

        <!-- Module 3: Divergence -->
        <div class="module">
          <label class="label required">Divergence Opinion</label>
          <textarea 
            v-model="summaryForm.divergence" 
            placeholder="List conflicting views or inconsistent evaluations (enter 'None' if applicable)..."
            class="input-area"
          ></textarea>
        </div>

        <!-- Module 4: Core Requirements -->
        <div class="module">
          <label class="label required">Core Revision Requirements</label>
          <textarea 
            v-model="summaryForm.coreRequirements" 
            placeholder="Summarize common revision points and key academic requirements..."
            class="input-area h-120"
          ></textarea>
        </div>

        <!-- Module 5: Editor Supplement -->
        <div class="module">
          <label class="label">Editor's Supplementary Comments (Optional)</label>
          <input 
            v-model="summaryForm.editorSupplement" 
            type="text" 
            placeholder="Additional notes from the editor..."
            class="input-text"
          >
        </div>

      </div>
    </div>

    <div class="divider"></div>

    <!-- Footer Actions -->
    <footer class="footer">
      <div class="footer-hint">Report cannot be modified after generation. Submission enters Final Decision process.</div>
      <div class="footer-buttons">
        <button class="btn btn-secondary" :disabled="!isFormValid" @click="generateReport">Generate Summary Report</button>
        <button class="btn btn-primary" :disabled="!isFormValid || isSubmitting" @click="handleSubmit">Submit to Editor-in-Chief</button>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.summary-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: white;
  padding: 20px;
  height: 100%;
  color: #333;
  display: flex;
  flex-direction: column;
}

.header { text-align: center; margin-bottom: 20px; }
.title { font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333; }
.subtitle { font-size: 12px; color: #dc3545; margin-bottom: 10px; }
.meta-info { display: flex; justify-content: center; gap: 20px; font-size: 14px; color: #666; }

.divider { height: 1px; background: #eee; margin: 15px 0; }

.content-body { display: flex; flex: 1; gap: 20px; overflow: hidden; }
.col-left, .col-right { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-right: 10px; }

.col-title { font-size: 16px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }

/* Left Column */
.review-item { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px dashed #eee; }
.review-header { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; font-weight: bold; }
.conclusion-badge.accept { color: #28A745; }
.conclusion-badge.revise { color: #F5A623; }
.conclusion-badge.reject { color: #dc3545; }
.review-text { font-size: 14px; line-height: 1.5; color: #333; margin-bottom: 5px; }
.btn-text { background: none; border: none; color: #999; cursor: pointer; text-decoration: underline; font-size: 12px; }

/* Right Column */
.module { margin-bottom: 15px; }
.label { display: block; font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #333; }
.label.required::after { content: " *"; color: #dc3545; }

.stats-row { display: flex; gap: 15px; font-size: 14px; font-weight: bold; }
.stat-item.green { color: #28A745; }
.stat-item.orange { color: #F5A623; }
.stat-item.red { color: #dc3545; }

.input-area { width: 100%; height: 100px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 14px; resize: vertical; }
.input-area.h-120 { height: 120px; }
.input-text { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 14px; }

/* Footer */
.footer { margin-top: auto; padding-top: 15px; border-top: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.footer-hint { font-size: 12px; color: #999; font-style: italic; }
.footer-buttons { display: flex; gap: 15px; }

.btn { padding: 8px 20px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; font-family: inherit; }
.btn-primary { background: #0056B3; color: white; }
.btn-primary:hover { background: #004494; }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #5a6268; }
.btn-secondary:disabled { background: #ccc; cursor: not-allowed; }

</style>
