<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  },
  // Previous revision requirements
  previousRequirements: {
    type: Array,
    default: () => [
      // Mock data
      { id: 1, text: 'Clarify the methodology in section 2.3 regarding sample selection.' },
      { id: 2, text: 'Update Figure 4 to include error bars.' },
      { id: 3, text: 'Address the ethical concerns raised by Reviewer 2.' }
    ]
  },
  // Author's response (Mock)
  authorResponse: {
    type: Object,
    default: () => ({
      version: 'R1',
      submitTime: '2026-03-01',
      items: [
        { reqId: 1, response: 'Added detailed description of inclusion/exclusion criteria in section 2.3, page 5.', location: 'Page 5, Line 120' },
        { reqId: 2, response: 'Figure 4 has been updated with standard deviation error bars.', location: 'Figure 4' },
        { reqId: 3, response: 'Added Ethics Statement in the methods section as requested.', location: 'Page 4, Line 90' }
      ]
    })
  },
  revisionCount: {
    type: Number,
    default: 1 // 1st Revision
  }
})

const emit = defineEmits(['submit', 'save-draft'])

// Check State
const checkState = reactive({}) // { reqId: 'pass' | 'fail' | 'partial' }
const reviewOpinion = ref('')
const finalDecision = ref('') // 'pass', 'retry', 'reject'
const isSubmitting = ref(false)

// Initialize check state
props.previousRequirements.forEach(req => {
  checkState[req.id] = null
})

// Validation
const isFormValid = computed(() => {
  // 1. All items checked
  const allChecked = props.previousRequirements.every(req => checkState[req.id])
  // 2. Decision made
  if (!finalDecision.value) return false
  // 3. Opinion filled
  if (!reviewOpinion.value.trim()) return false
  
  return allChecked
})

const maxRevisionsReached = computed(() => props.revisionCount >= 2)

// Actions
const handleCheck = (reqId, status) => {
  checkState[reqId] = status
}

const handleSubmit = () => {
  if (!isFormValid.value) return
  isSubmitting.value = true
  
  setTimeout(() => {
    emit('submit', {
      checks: checkState,
      decision: finalDecision.value,
      opinion: reviewOpinion.value
    })
    isSubmitting.value = false
  }, 1000)
}

</script>

<template>
  <div class="revision-check-container">
    <!-- Header -->
    <header class="header">
      <h2 class="title">Revision Re-Review (Lancet Standard)</h2>
      <p class="subtitle">Max 2 revisions allowed. Must verify item by item against original requirements.</p>
      
      <div class="meta-info">
        <span>Revision: {{ revisionCount }}/2</span>
        <span>Version: {{ authorResponse.version }}</span>
        <span>Submitted: {{ authorResponse.submitTime }}</span>
      </div>
    </header>
    
    <div class="divider"></div>

    <!-- Comparison Body -->
    <div class="comparison-body">
      <div class="col-left">
        <h3 class="col-title">Original Requirements</h3>
        <div v-for="req in previousRequirements" :key="req.id" class="req-item">
          <div class="req-badge">Req #{{ req.id }}</div>
          <p class="req-text">{{ req.text }}</p>
        </div>
      </div>

      <div class="col-right">
        <h3 class="col-title">Author Response & Check</h3>
        <div v-for="req in previousRequirements" :key="req.id" class="resp-item">
          <!-- Find corresponding response -->
          <div class="resp-content">
            <p class="resp-text">
              <strong>Response:</strong> 
              {{ authorResponse.items.find(i => i.reqId === req.id)?.response || 'No response provided.' }}
            </p>
            <p class="resp-loc">
              Location: {{ authorResponse.items.find(i => i.reqId === req.id)?.location || 'N/A' }}
            </p>
          </div>
          
          <!-- Check Actions -->
          <div class="check-actions">
            <label class="radio-label pass">
              <input type="radio" :name="`req-${req.id}`" value="pass" @change="handleCheck(req.id, 'pass')"> Met
            </label>
            <label class="radio-label partial">
              <input type="radio" :name="`req-${req.id}`" value="partial" @change="handleCheck(req.id, 'partial')"> Partial
            </label>
            <label class="radio-label fail">
              <input type="radio" :name="`req-${req.id}`" value="fail" @change="handleCheck(req.id, 'fail')"> Not Met
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Conclusion -->
    <footer class="footer">
      <div class="decision-section">
        <h3 class="section-title">Re-Review Conclusion</h3>
        
        <div class="decision-options">
          <label class="option-card">
            <input type="radio" v-model="finalDecision" value="pass">
            <div>
              <span class="opt-title">Pass & Proceed</span>
              <span class="opt-desc">Modifications meet all requirements.</span>
            </div>
          </label>

          <label v-if="!maxRevisionsReached" class="option-card">
            <input type="radio" v-model="finalDecision" value="retry">
            <div>
              <span class="opt-title">Return for Revision ({{ revisionCount + 1 }}/2)</span>
              <span class="opt-desc">Issues remain, allow one more chance.</span>
            </div>
          </label>

          <label class="option-card">
            <input type="radio" v-model="finalDecision" value="reject">
            <div>
              <span class="opt-title">Reject</span>
              <span class="opt-desc">Modifications failed to meet standards.</span>
            </div>
          </label>
        </div>

        <div class="opinion-box">
          <label class="required">Re-Review Opinion</label>
          <textarea 
            v-model="reviewOpinion" 
            placeholder="Justify your decision based on the modification checks..."
            rows="3"
          ></textarea>
        </div>
      </div>

      <div class="action-buttons">
        <button class="btn-gray" @click="$emit('save-draft')">Save Draft</button>
        <button class="btn-red" :disabled="!isFormValid || isSubmitting" @click="handleSubmit">Submit Conclusion</button>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.revision-check-container {
  font-family: 'Times New Roman', Times, serif;
  background: white;
  padding: 20px;
  height: 100%;
  color: #333;
  display: flex;
  flex-direction: column;
}

.header { text-align: center; margin-bottom: 20px; }
.title { font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333; }
.subtitle { font-size: 12px; color: #C93737; margin-bottom: 10px; }
.meta-info { display: flex; justify-content: center; gap: 20px; font-size: 14px; color: #666; font-weight: bold; }

.divider { height: 1px; background: #eee; margin: 15px 0; }

.comparison-body { display: flex; flex: 1; overflow-y: auto; border: 1px solid #eee; }
.col-left { width: 40%; border-right: 1px solid #eee; padding: 15px; background: #fcfcfc; }
.col-right { width: 60%; padding: 15px; }

.col-title { font-size: 16px; font-weight: bold; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 15px; }

/* Items */
.req-item, .resp-item { min-height: 100px; margin-bottom: 20px; border-bottom: 1px dashed #eee; padding-bottom: 15px; }
.req-badge { font-size: 12px; font-weight: bold; color: #666; margin-bottom: 5px; }
.req-text { font-size: 14px; line-height: 1.4; }

.resp-content { background: #f9f9f9; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
.resp-text { font-size: 14px; margin: 0 0 5px 0; }
.resp-loc { font-size: 12px; color: #666; font-style: italic; }

.check-actions { display: flex; gap: 15px; }
.radio-label { font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 5px; }
.radio-label.pass { color: #28A745; }
.radio-label.partial { color: #F5A623; }
.radio-label.fail { color: #C93737; }

/* Footer */
.footer { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
.section-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; }

.decision-options { display: flex; gap: 15px; margin-bottom: 20px; }
.option-card { flex: 1; border: 1px solid #ddd; padding: 15px; border-radius: 4px; cursor: pointer; display: flex; gap: 10px; align-items: flex-start; transition: all 0.2s; }
.option-card:hover { border-color: #999; background: #f9f9f9; }
.opt-title { display: block; font-weight: bold; font-size: 14px; margin-bottom: 3px; }
.opt-desc { display: block; font-size: 12px; color: #666; }

.opinion-box { margin-bottom: 20px; }
.required::after { content: " *"; color: #C93737; }
textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 14px; }

.action-buttons { text-align: center; display: flex; justify-content: center; gap: 15px; }
.btn-gray { padding: 8px 20px; border: 1px solid #ddd; background: #eee; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-red { padding: 8px 20px; border: none; background: #C93737; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-red:disabled { background: #ccc; cursor: not-allowed; }

</style>
