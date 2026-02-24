<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'
import { searchInstitutions } from '../../utils/validators'

const store = useSubmissionStore()
const { t } = useI18n()
const { scrollToError } = useErrorScroll()

// Helper: Institution Search for Reviewers
const showInstSuggestions = ref({}) // { 'type-index': true }
const instSuggestions = ref([])

const handleInstSearch = async (query, index, type) => {
  const key = `${type}-${index}`
  if (query.length < 2) {
    instSuggestions.value = []
    showInstSuggestions.value[key] = false
    return
  }
  
  const results = await searchInstitutions(query)
  instSuggestions.value = results
  if (results.length > 0) {
    showInstSuggestions.value = { [key]: true } // Only show one at a time
  } else {
    showInstSuggestions.value[key] = false
  }
}

const selectInstitution = (index, inst, type) => {
  const key = `${type}-${index}`
  if (type === 'rec') {
    store.formData.additionalInfo.recommendedReviewers[index].affiliation = inst
  } else {
    store.formData.additionalInfo.avoidedReviewers[index].affiliation = inst
  }
  showInstSuggestions.value[key] = false
}

// --- 1. Manuscript Anonymization Check Logic ---
const scanStatus = ref('pending') // pending, scanning, completed, needs_revision
const scanRisks = ref([])
const uploadedFileName = computed(() => store.formData.files?.[0]?.name || 'manuscript.pdf')
const uploadDate = computed(() => new Date().toISOString().split('T')[0])

const scanStatusText = computed(() => {
  if (scanStatus.value === 'pending') return 'Pending'
  if (scanStatus.value === 'scanning') return 'Scanning...'
  if (scanStatus.value === 'completed') return 'Completed'
  if (scanStatus.value === 'needs_revision') return 'Needs Revision'
  return 'Pending'
})

const scanStatusClass = computed(() => {
  if (scanStatus.value === 'pending') return 'status-pending'
  if (scanStatus.value === 'completed') return 'status-completed'
  if (scanStatus.value === 'needs_revision') return 'status-error'
  return ''
})

const handleScanManuscript = () => {
  scanStatus.value = 'scanning'
  setTimeout(() => {
    // Mock Random Result
    const hasRisk = Math.random() > 0.7
    if (hasRisk) {
      scanStatus.value = 'needs_revision'
      scanRisks.value = [
        'Page 1, Header: Author Name - [John Doe]',
        'Page 15, Acknowledgments: Fund Number - [Grant-2024-001]',
        'Page 22, References: Self-citation not anonymized'
      ]
      store.formData.additionalInfo.blindReview.confirmed = false
    } else {
      scanStatus.value = 'completed'
      scanRisks.value = []
    }
  }, 1500)
}

const confirmAnonymization = () => {
  store.formData.additionalInfo.blindReview.confirmed = true
}

const triggerReupload = () => {
  alert('Redirecting to File Upload step... (Mock)')
  // In real app, might emit event to parent to switch step
}

// --- 2. Reference Anonymization Logic ---
const refStatus = ref('pending') // pending, completed, confirmed
const originalReferences = ref([])
const anonymizedReferences = ref([])

const refStatusText = computed(() => {
  if (refStatus.value === 'pending') return 'Pending'
  if (refStatus.value === 'completed') return 'Completed'
  if (refStatus.value === 'confirmed') return 'Confirmed'
  return 'Pending'
})

const refStatusClass = computed(() => {
  if (refStatus.value === 'pending') return 'status-pending'
  if (refStatus.value === 'completed') return 'status-gray'
  if (refStatus.value === 'confirmed') return 'status-completed'
  return ''
})

const handleAnonymizeReferences = () => {
  // Mock Processing
  refStatus.value = 'processing' // temporary internal state
  setTimeout(() => {
    originalReferences.value = [
      { text: 'Zhang S. 2024. Deep learning in X-ray. Journal of AI.', isSelf: true },
      { text: 'Smith J. 2023. General radiology. Nature.', isSelf: false },
      { text: 'Zhang S, Li J. 2022. Early detection methods. IEEE.', isSelf: true }
    ]
    anonymizedReferences.value = [
      { text: 'Author et al. 2024. Deep learning in X-ray. Journal of AI.' },
      { text: 'Smith J. 2023. General radiology. Nature.' },
      { text: 'Author et al. 2022. Early detection methods. IEEE.' }
    ]
    refStatus.value = 'completed'
  }, 1500)
}

const confirmReferences = () => {
  refStatus.value = 'confirmed'
  // Store in formData if needed
}

const cancelRefConfirmation = () => {
  refStatus.value = 'completed'
}

// --- 3. Self-Citation Detection Logic ---
const selfCiteStatus = ref('pending') // pending, needs_verification, completed, confirmed
const selfCiteStats = ref({ explicit: 0, potential: 0, anonymized: 0 })
const explicitCitations = ref([])
const potentialCitations = ref([])

const selfCiteStatusText = computed(() => {
  if (selfCiteStatus.value === 'pending') return 'Pending'
  if (selfCiteStatus.value === 'needs_verification') return 'Needs Verification'
  if (selfCiteStatus.value === 'completed') return 'Completed'
  if (selfCiteStatus.value === 'confirmed') return 'Confirmed'
  return 'Pending'
})

const selfCiteStatusClass = computed(() => {
  if (selfCiteStatus.value === 'pending') return 'status-pending'
  if (selfCiteStatus.value === 'needs_verification') return 'status-error'
  if (selfCiteStatus.value === 'confirmed') return 'status-completed'
  return 'status-gray'
})

const detectSelfCitations = () => {
  // Mock Detection
  setTimeout(() => {
    selfCiteStats.value = { explicit: 2, potential: 1, anonymized: 2 }
    explicitCitations.value = [
      { page: 2, line: 15, text: '(Zhang, 2024)', anonymized: '(Author, 2024)' },
      { page: 5, line: 30, text: '(Zhang & Li, 2022)', anonymized: '(Author et al., 2022)' }
    ]
    potentialCitations.value = [
      { page: 3, line: 10, reason: 'Same affiliation (Univ of Science)', text: '(Wang et al., 2023)', userChoice: null }
    ]
    selfCiteStatus.value = 'needs_verification'
  }, 1500)
}

const confirmSelfCitations = () => {
  // Check if all potential are verified
  const allVerified = potentialCitations.value.every(c => c.userChoice)
  if (!allVerified) {
    alert('Please verify all potential self-citations first.')
    return
  }
  selfCiteStatus.value = 'confirmed'
}

const toggleCiteChoice = (cite, value) => {
  // Allow toggling (unselecting) by clicking the same value again
  if (cite.userChoice === value) {
    cite.userChoice = null
  } else {
    cite.userChoice = value
  }
}

onMounted(() => {
  // Initialize arrays if they don't exist (handling legacy drafts)
  if (!store.formData.additionalInfo.recommendedReviewers) {
    store.formData.additionalInfo.recommendedReviewers = []
  }
  if (!store.formData.additionalInfo.avoidedReviewers) {
    store.formData.additionalInfo.avoidedReviewers = []
  }

  if (store.steps[3].status === 'error') {
    scrollToError()
  }
})

// ... Existing logic ...


const questions = computed(() => [
  { key: 'q1', label: t('additionalInformation.questions.q1'), limit: 500 },
  { key: 'q2', label: t('additionalInformation.questions.q2'), limit: 500 },
  { key: 'q3', label: t('additionalInformation.questions.q3'), limit: 500 },
  { key: 'q4', label: t('additionalInformation.questions.q4'), limit: 500 },
  { key: 'q5', label: t('additionalInformation.questions.q5'), limit: 500 },
  { key: 'q6', label: t('additionalInformation.questions.q6'), limit: 500 },
])

const getCharCount = (text) => text ? text.length : 0

// Reviewer Logic
const addRecommendedReviewer = () => {
  if (store.formData.additionalInfo.recommendedReviewers.length >= 3) {
      alert("Maximum 3 recommended reviewers allowed.")
      return
  }
  
  store.formData.additionalInfo.recommendedReviewers.push({
      name: '',
      email: '',
      affiliation: '',
      reason: '',
      coiDeclared: false
    })
}

const removeRecommendedReviewer = (index) => {
  store.formData.additionalInfo.recommendedReviewers.splice(index, 1)
}

const addAvoidedReviewer = () => {
  store.formData.additionalInfo.avoidedReviewers.push({
    name: '',
    affiliation: '',
    reasonType: '',
    reason: ''
  })
}

const removeAvoidedReviewer = (index) => {
  store.formData.additionalInfo.avoidedReviewers.splice(index, 1)
}

// Validation Helpers
// const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/ // Removed per requirements

const isFieldInvalid = (value, type, minLength = 0) => {
  if (store.steps[3].status !== 'error') return false
  
  if (!value) return true // Required check
  
  // Removed Email Format Check
  // if (type === 'email') {
  //   return !emailRegex.test(value)
  // }

  if (type === 'coi') {
    return value !== true
  }
  
  // Removed Min Length Check
  // if (minLength > 0) {
  //   return value.length < minLength
  // }
  
  return false
}

const getFieldError = (value, type, minLength = 0) => {
  if (store.steps[3].status !== 'error') return ''
  
  if (!value) {
    if (type === 'name') return "Please enter the reviewer's full name"
    if (type === 'email') return "Please enter the reviewer's email address"
    if (type === 'reasonType') {
       return "Please select a reason category"
    }
    
    if (type === 'reason') {
        return "Please provide a justification"
    }
  }

  // Journal Platform Standard: If any required field is missing, the popup handles the main message.
  // Inline errors remain specific but aligned with the requirement "Complete all required fields".
  
  return ''
}

const handleConfirmAnonymization = () => {
  // Simulate scanning
  const confirmText = "You confirm that all writer identifying information has been removed from the manuscript."
  if (confirm(confirmText)) {
    store.formData.additionalInfo.blindReview.confirmed = true
  }
}

</script>

<template>
  <div class="step-container">
    <h2 class="step-title">Additional Information</h2>
    <!-- Fixed title as per requirements: "Step 4: Additional Info" highlighed in nav, title "Additional Information" -->

    <StepNavigation v-if="false" /> <!-- Keeping import but hiding if not needed here, actually used at bottom -->

    <!-- Manuscript Anonymization Check (Required) -->
    <div class="blind-review-section">
      <h3 class="section-title">Manuscript Anonymization Check <span class="required">(Required for Double-Blind Review)</span></h3>
      <p class="section-helper">The system will automatically scan your full manuscript for writer identifying information. <span class="text-red">All identifiers must be completely removed</span> to comply with double-blind review standards.</p>
      
      <div class="scan-status-container">
        <span class="status-label">Scan Status:</span>
        <span class="status-value" :class="scanStatusClass">{{ scanStatusText }}</span>
      </div>
      
      <div class="scan-target-info" v-if="uploadedFileName">
        Scanning target: {{ uploadedFileName }} (Uploaded on {{ uploadDate }})
      </div>

      <div class="scan-actions">
        <button 
          v-if="scanStatus !== 'scanning'"
          class="btn-brand-red" 
          @click="handleScanManuscript"
        >
          {{ scanStatus === 'pending' ? 'Scan Manuscript for Author Identifiers' : 'Rescan Manuscript' }}
        </button>
        <button v-else class="btn-brand-red disabled" disabled>
          Scanning... Please wait
        </button>
      </div>

      <!-- Scan Results -->
      <div v-if="scanStatus === 'completed'" class="scan-result success">
        <h4 class="result-title">No Writer Identifying Information Detected</h4>
        <p class="result-desc">The system has finished scanning your manuscript. No writer identifiers were found in the text, figures, tables, headers, footers or acknowledgments. You may proceed with submission.</p>
        <button class="btn-confirm-green" @click="confirmAnonymization" v-if="!store.formData.additionalInfo.blindReview.confirmed">
          Confirm & Proceed
        </button>
        <span v-else class="confirmed-badge">✓ Confirmed</span>
      </div>

      <div v-if="scanStatus === 'needs_revision'" class="scan-result error">
        <h4 class="result-title">Author Identifying Information Detected – Revision Required</h4>
        <ul class="risk-list">
          <li v-for="(risk, idx) in scanRisks" :key="idx">
            <span class="risk-dot">●</span> {{ risk }}
          </li>
        </ul>
        <p class="revision-hint">Please delete all detected writer identifiers, re-upload your revised manuscript, and click Rescan Manuscript to verify again.</p>
        <button class="btn-secondary" @click="triggerReupload">Re-upload Revised Manuscript</button>
      </div>
    </div>

    <!-- Reference Anonymization (Required) -->
    <div class="blind-review-section">
      <h3 class="section-title">Reference Anonymization for Double-Blind Review</h3>
      <p class="section-helper">The system will automatically anonymize all self-citations in your reference list. <span class="text-red">You must verify and confirm</span> the anonymized version before submission.</p>
      
      <div class="scan-status-container">
        <span class="status-label">Anonymization Status:</span>
        <span class="status-value" :class="refStatusClass">{{ refStatusText }}</span>
      </div>

      <div class="scan-actions">
        <button 
          v-if="refStatus === 'pending' || refStatus === 'completed'"
          class="btn-brand-red" 
          @click="handleAnonymizeReferences"
        >
          {{ refStatus === 'pending' ? 'Anonymize References' : 'Re-anonymize References' }}
        </button>
      </div>

      <!-- Reference Comparison -->
      <div v-if="refStatus !== 'pending'" class="ref-comparison-container">
        <div class="ref-col">
          <h4 class="ref-col-title">Original Reference List</h4>
          <div class="ref-list">
            <div v-for="(ref, idx) in originalReferences" :key="idx" class="ref-item" :class="{ 'self-citation': ref.isSelf }">
              <span v-if="ref.isSelf" class="red-star">*</span> {{ ref.text }}
            </div>
          </div>
        </div>
        <div class="ref-col">
          <h4 class="ref-col-title">Anonymized Reference List</h4>
          <div class="ref-list">
            <div v-for="(ref, idx) in anonymizedReferences" :key="idx" class="ref-item">
              {{ ref.text }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="refStatus === 'completed'" class="ref-confirm-actions">
        <p class="ref-hint">Please carefully compare the original and anonymized references to ensure no writer information remains.</p>
        <button class="btn-confirm-green" @click="confirmReferences">Confirm Anonymized References</button>
      </div>
      
      <div v-if="refStatus === 'confirmed'" class="ref-confirm-actions">
        <span class="confirmed-badge">✓ References Confirmed</span>
        <button class="btn-text-cancel" @click="cancelRefConfirmation">Cancel Confirmation</button>
      </div>
    </div>

    <!-- Self-Citation Detection (Required) -->
    <div class="blind-review-section">
      <h3 class="section-title">Self-Citation Detection & Processing</h3>
      <p class="section-helper">The system detects explicit and potential self-citations in your manuscript text and reference list. <span class="text-red">All self-citations must be anonymized</span> for blind review.</p>
      
      <div class="scan-status-container">
        <span class="status-label">Detection Status:</span>
        <span class="status-value" :class="selfCiteStatusClass">{{ selfCiteStatusText }}</span>
      </div>

      <div class="scan-actions">
        <button 
          v-if="selfCiteStatus !== 'confirmed'"
          class="btn-brand-red" 
          @click="detectSelfCitations"
        >
          {{ selfCiteStatus === 'pending' ? 'Detect Self-Citations' : 'Re-detect Self-Citations' }}
        </button>
      </div>

      <div v-if="selfCiteStatus !== 'pending'" class="self-cite-stats">
        <div class="stat-item"><span class="dot green">●</span> Explicit: {{ selfCiteStats.explicit }}</div>
        <div class="stat-item"><span class="dot orange">●</span> Potential: {{ selfCiteStats.potential }}</div>
        <div class="stat-item"><span class="dot blue">●</span> Anonymized: {{ selfCiteStats.anonymized }}</div>
      </div>

      <div v-if="selfCiteStatus === 'needs_verification' || selfCiteStatus === 'completed'" class="self-cite-details">
        <!-- Explicit -->
        <div class="cite-group">
          <h4 class="cite-group-title green">Explicit Self-Citations</h4>
          <div v-for="(cite, idx) in explicitCitations" :key="idx" class="cite-item">
            <div class="cite-loc">Page {{ cite.page }}, Line {{ cite.line }}</div>
            <div class="cite-text">{{ cite.text }} → {{ cite.anonymized }}</div>
          </div>
        </div>
        
        <!-- Potential -->
        <div class="cite-group">
          <h4 class="cite-group-title orange">Potential Self-Citations (Action Required)</h4>
          <div v-for="(cite, idx) in potentialCitations" :key="idx" class="cite-item">
            <div class="cite-loc">Page {{ cite.page }}, Line {{ cite.line }}</div>
            <div class="cite-reason">Reason: {{ cite.reason }}</div>
            <div class="cite-text">{{ cite.text }}</div>
            <div class="cite-verify">
              <label class="radio-label">
                <input 
                  type="radio" 
                  :name="'pot-'+idx" 
                  value="yes" 
                  :checked="cite.userChoice === 'yes'"
                  @click="toggleCiteChoice(cite, 'yes')"
                > 
                Is Self-Citation
              </label>
              <label class="radio-label">
                <input 
                  type="radio" 
                  :name="'pot-'+idx" 
                  value="no" 
                  :checked="cite.userChoice === 'no'"
                  @click="toggleCiteChoice(cite, 'no')"
                > 
                Not Self-Citation
              </label>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selfCiteStatus === 'needs_verification' || selfCiteStatus === 'completed'" class="blind-actions">
        <button class="btn-confirm-green" @click="confirmSelfCitations">Confirm Self-Citation Detection & Anonymization</button>
      </div>
       <div v-if="selfCiteStatus === 'confirmed'" class="blind-actions">
        <span class="confirmed-badge">✓ Self-Citations Confirmed</span>
      </div>
    </div>

    <!-- Mandatory Questions -->
    <div class="questions-section">
      <div v-for="(q, index) in questions" :key="q.key" class="form-group">
        <label class="form-label">
          {{ index + 1 }}. {{ q.label }} <span class="required">*</span>
        </label>
        <textarea 
          v-model="store.formData.additionalInfo[q.key]" 
          class="form-textarea"
          rows="3"
        ></textarea>
        <div class="char-count" :class="{ 'error': getCharCount(store.formData.additionalInfo[q.key]) > q.limit }">
          {{ getCharCount(store.formData.additionalInfo[q.key]) }} / {{ q.limit }}
        </div>
        <div v-if="getCharCount(store.formData.additionalInfo[q.key]) > q.limit" class="error-text">
          {{ t('additionalInformation.errors.limitExceeded') }}
        </div>
      </div>
    </div>

    <!-- Recommended Reviewers Section -->
    <div class="reviewers-section">
      <div class="section-header">
        <h3 class="section-title">Suggested Reviewers (Optional, 1–3 reviewers)</h3>
        <p class="section-helper">You may suggest 1–3 potential reviewers for your manuscript. All suggestions are subject to review and final approval by the editorial team.</p>
      </div>

      <div v-for="(reviewer, index) in store.formData.additionalInfo.recommendedReviewers" :key="'rec-' + index" class="reviewer-row">
        <div class="reviewer-fields">
            <!-- Full Name -->
            <div class="form-group-item">
                <label class="field-label">Full Name <span class="required">*</span></label>
                <input 
                    type="text" 
                    v-model="reviewer.name" 
                    class="form-input" 
                    :class="{ 'input-error': isFieldInvalid(reviewer.name, 'name') }"
                    placeholder="Enter reviewer's full name (e.g., John Smith)"
                >
                <div v-if="isFieldInvalid(reviewer.name, 'name')" class="error-text">
                    {{ getFieldError(reviewer.name, 'name') }}
                </div>
            </div>

            <!-- Email Address -->
            <div class="form-group-item">
                <label class="field-label">Email Address <span class="required">*</span></label>
                <input 
                    type="text" 
                    v-model="reviewer.email" 
                    class="form-input"
                    :class="{ 'input-error': isFieldInvalid(reviewer.email, 'email') }"
                    placeholder="Enter reviewer's valid academic/business email"
                >
                <div v-if="isFieldInvalid(reviewer.email, 'email')" class="error-text">
                    {{ getFieldError(reviewer.email, 'email') }}
                </div>
            </div>

            <!-- Affiliation -->
            <div class="form-group-item">
                <label class="field-label">Affiliation (Institution & Department)</label>
                <div style="position: relative;">
                    <input 
                        type="text" 
                        v-model="reviewer.affiliation" 
                        @input="e => handleInstSearch(e.target.value, index, 'rec')"
                        class="form-input"
                        placeholder="Enter reviewer's academic/business affiliation"
                    >
                    <ul v-if="showInstSuggestions[`rec-${index}`] && instSuggestions.length > 0" class="inst-suggestions">
                       <li v-for="inst in instSuggestions" :key="inst" @click="selectInstitution(index, inst, 'rec')">{{ inst }}</li>
                    </ul>
                </div>
            </div>

            <!-- Reason -->
            <div class="form-group-item full-width">
                <label class="field-label">Justification for Suggestion <span class="required">*</span></label>
                <textarea 
                    v-model="reviewer.reason" 
                    class="form-textarea"
                    rows="2"
                    :class="{ 'input-error': isFieldInvalid(reviewer.reason, 'reason') }"
                    placeholder="Explain why this reviewer is suitable (e.g., expertise in cardiovascular research)"
                ></textarea>
                <div v-if="isFieldInvalid(reviewer.reason, 'reason')" class="error-text">
                    {{ getFieldError(reviewer.reason, 'reason') }}
                </div>
            </div>

            <!-- COI Declaration (Missing Feature Added) -->
            <div class="form-group-item full-width">
              <label class="checkbox-label" :class="{ 'error-text': isFieldInvalid(reviewer.coiDeclared, 'coi') }">
                <input type="checkbox" v-model="reviewer.coiDeclared">
                <span class="checkbox-text" style="color: #333; font-weight: normal; margin-left: 8px;">
                  I confirm that I have no conflict of interest with this reviewer (e.g., no recent collaboration, mentorship, or shared institutional affiliation). <span class="required">*</span>
                </span>
              </label>
              <div v-if="isFieldInvalid(reviewer.coiDeclared, 'coi')" class="error-text" style="margin-left: 24px;">
                 You must declare no conflict of interest to recommend this reviewer.
              </div>
            </div>
        </div>
        <button class="remove-btn" @click="removeRecommendedReviewer(index)">Remove</button>
      </div>

      <button 
        class="add-btn" 
        @click="addRecommendedReviewer"
        :disabled="store.formData.additionalInfo.recommendedReviewers.length >= 3"
      >
        Add a Reviewer
      </button>
    </div>

    <!-- Avoided Reviewers Section -->
    <div class="reviewers-section">
      <div class="section-header">
        <h3 class="section-title">Avoided Reviewers (Optional)</h3>
        <p class="section-helper">Please list any reviewers you wish to avoid and provide a valid reason (e.g., conflict of interest). All requests will be reviewed by the editorial team.</p>
      </div>

      <div v-for="(reviewer, index) in store.formData.additionalInfo.avoidedReviewers" :key="'avoid-' + index" class="reviewer-row">
        <div class="reviewer-fields">
            <!-- Full Name -->
            <div class="form-group-item">
                <label class="field-label">Full Name <span class="required">*</span></label>
                <input 
                    type="text" 
                    v-model="reviewer.name" 
                    class="form-input" 
                    :class="{ 'input-error': isFieldInvalid(reviewer.name, 'name') }"
                    placeholder="Enter reviewer's full name to avoid"
                >
                <div v-if="isFieldInvalid(reviewer.name, 'name')" class="error-text">
                    {{ getFieldError(reviewer.name, 'name') }}
                </div>
            </div>

            <!-- Affiliation -->
            <div class="form-group-item">
                <label class="field-label">Affiliation</label>
                <div style="position: relative;">
                    <input 
                        type="text" 
                        v-model="reviewer.affiliation" 
                        @input="e => handleInstSearch(e.target.value, index, 'avoid')"
                        class="form-input"
                        placeholder="Enter reviewer's affiliation"
                    >
                    <ul v-if="showInstSuggestions[`avoid-${index}`] && instSuggestions.length > 0" class="inst-suggestions">
                       <li v-for="inst in instSuggestions" :key="inst" @click="selectInstitution(index, inst, 'avoid')">{{ inst }}</li>
                    </ul>
                </div>
            </div>

            <!-- Reason -->
            <div class="form-group-item full-width">
                <label class="field-label">Reason for Avoidance <span class="required">*</span></label>
                <textarea 
                    v-model="reviewer.reason" 
                    class="form-textarea"
                    rows="3"
                    :class="{ 'input-error': isFieldInvalid(reviewer.reason, 'reason', 80) }"
                    placeholder="Explain the reason for avoidance (e.g., personal conflict, competing research interests) - must be a valid academic/business reason"
                ></textarea>
                <div v-if="isFieldInvalid(reviewer.reason, 'reason', 80)" class="error-text">
                    {{ getFieldError(reviewer.reason, 'reason', 80) }}
                </div>
            </div>
        </div>
        <button class="remove-btn" @click="removeAvoidedReviewer(index)">Remove</button>
      </div>

      <button 
        class="add-btn" 
        @click="addAvoidedReviewer"
      >
        Add an Avoided Reviewer
      </button>
    </div>
    
    <!-- Blind Review Settings -->
    <div class="blind-review-section">
      <h3 class="section-title">Blind Review Settings (Required for Blind Peer Review)</h3>
      
      <div class="blind-checkbox-group">
        <label class="checkbox-label disabled">
          <input type="checkbox" :checked="store.formData.additionalInfo.blindReview.enabled" disabled>
          <span class="checkbox-text">Submit manuscript for blind peer review</span>
        </label>
        <p class="blind-hint">All writer identifying information will be removed from the manuscript for reviewers</p>
      </div>

      <div class="blind-actions">
        <button 
          class="btn-brand-red" 
          @click="handleConfirmAnonymization"
          :class="{ 'confirmed': store.formData.additionalInfo.blindReview.confirmed }"
        >
          {{ store.formData.additionalInfo.blindReview.confirmed ? 'Anonymization Confirmed ✓' : 'Confirm Anonymization' }}
        </button>
        <p class="self-check-hint">Please ensure no writer names, affiliations, or personal identifiers (including in figures/tables/filenames) are present in the manuscript.</p>
      </div>
      
      <div v-if="store.steps[3].status === 'error' && !store.formData.additionalInfo.blindReview.confirmed" class="error-text">
        Please confirm anonymization to proceed.
      </div>
    </div>

    <div v-if="store.steps[3].status === 'error'" class="error-msg main-error">
      {{ t('additionalInformation.errors.incomplete') }}
    </div>

    <hr class="divider">

    <!-- Optional Fields (Preserved) -->
    <div class="optional-section">
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="store.formData.additionalInfo.ssrn">
          {{ t('additionalInformation.ssrn') }}
        </label>
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('additionalInformation.socialMedia') }} ({{ t('common.optional') }})</label>
        <input 
          type="text" 
          v-model="store.formData.additionalInfo.socialMedia" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('additionalInformation.conference') }} ({{ t('common.optional') }})</label>
        <select v-model="store.formData.additionalInfo.conference" class="form-select">
          <option value="">{{ t('common.select') }}</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>
    </div>

    <StepNavigation />
  </div>
</template>

<style scoped>
.step-container {
  max-width: 800px;
  margin: 0 auto;
}

.step-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.form-group {
  margin-bottom: 2rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.required {
  color: #dc3545;
}

.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
}

.form-textarea:focus {
  border-color: #0056B3;
  outline: none;
  box-shadow: 0 0 0 1px rgba(0, 86, 179, 0.25);
}

.form-input, .form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus, .form-select:focus {
  border-color: #0056B3;
  outline: none;
  box-shadow: 0 0 0 1px rgba(0, 86, 179, 0.25);
}

.input-error {
  border-color: #dc3545 !important;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.char-count.error {
  color: #dc3545;
  font-weight: bold;
}

.error-text, .error-msg {
  color: #dc3545;
  font-size: 12px;
  margin-top: 5px;
}

.main-error {
  margin-bottom: 20px;
  font-weight: bold;
  text-align: center;
}

.divider {
  border: 0;
  border-top: 1px solid #eee;
  margin: 2rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

/* Reviewer Section Styles */
.reviewers-section {
  margin-bottom: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 24px;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 4px 0;
}

.section-helper {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.reviewer-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
  background: #f9f9f9;
  padding: 16px;
  border-radius: 4px;
}

.reviewer-fields {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.form-group-item {
  width: calc(50% - 8px);
}

.form-group-item.full-width {
  width: 100%;
}

.field-label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.add-btn {
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-btn:hover:not(:disabled) {
  background-color: #004494;
}

.add-btn:disabled {
  background-color: #E0E0E0;
  color: #999;
  cursor: not-allowed;
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 0;
  margin-top: 24px; /* Align with input fields */
}

.remove-btn:hover {
  text-decoration: underline;
  color: #666;
}

/* Blind Review Styles */
.blind-review-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fdfdfd;
  border: 1px solid #eee;
  border-radius: 4px;
}

.text-red { color: #dc3545; font-weight: bold; }

.scan-status-container { margin: 10px 0; font-size: 14px; }
.status-label { font-weight: 600; color: #333; margin-right: 5px; }
.status-value { font-weight: bold; }
.status-pending { color: #4A90E2; }
.status-completed { color: #28A745; }
.status-error { color: #dc3545; }
.status-gray { color: #666; }

.scan-target-info { font-size: 14px; color: #666; margin-bottom: 10px; }

.scan-result { margin-top: 15px; padding: 15px; border-radius: 4px; border: 1px solid #eee; }
.scan-result.success { background: #f0fff4; border-color: #d1e7dd; }
.scan-result.error { background: #fff5f5; border-color: #feb2b2; }

.result-title { margin: 0 0 5px 0; font-size: 16px; font-weight: bold; }
.success .result-title { color: #28A745; }
.error .result-title { color: #dc3545; }

.result-desc { font-size: 14px; color: #333; margin: 0 0 10px 0; }

.risk-list { list-style: none; padding: 0; margin: 10px 0; }
.risk-list li { font-size: 14px; margin-bottom: 5px; color: #333; }
.risk-dot { color: #dc3545; margin-right: 5px; }

.revision-hint { color: #dc3545; font-weight: bold; font-size: 14px; margin: 10px 0; }

.btn-confirm-green {
  background: #28A745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;
}
.btn-confirm-green:hover { background: #218838; }

.confirmed-badge { color: #28A745; font-weight: bold; font-size: 14px; }

.ref-comparison-container { display: flex; gap: 20px; margin-top: 15px; }
.ref-col { flex: 1; background: white; border: 1px solid #eee; border-radius: 4px; padding: 12px; }
.ref-col-title { font-size: 16px; color: #333; margin: 0 0 10px 0; }
.ref-list { max-height: 200px; overflow-y: auto; font-size: 13px; color: #555; }
.ref-item { margin-bottom: 8px; line-height: 1.4; }
.self-citation { color: #dc3545; }
.red-star { color: #C93737; font-weight: bold; }

.self-cite-stats { display: flex; gap: 15px; margin: 15px 0; padding: 10px; background: white; border: 1px solid #eee; border-radius: 8px; }
.stat-item { font-size: 14px; font-weight: 500; }
.dot { font-size: 16px; margin-right: 5px; }
.dot.green { color: #28A745; }
.dot.orange { color: #F5A623; }
.dot.blue { color: #4A90E2; }

.self-cite-details { margin-top: 15px; display: flex; flex-direction: column; gap: 15px; }
.cite-group { background: white; border: 1px solid #eee; padding: 10px; border-radius: 4px; }
.cite-group-title { font-size: 16px; margin: 0 0 10px 0; }
.cite-group-title.green { color: #28A745; }
.cite-group-title.orange { color: #F5A623; }

.cite-item { margin-bottom: 10px; border-bottom: 1px dashed #eee; padding-bottom: 10px; }
.cite-loc { font-size: 12px; color: #999; margin-bottom: 2px; }
.cite-text { font-size: 14px; color: #333; }
.cite-reason { font-size: 13px; color: #666; margin-bottom: 2px; font-style: italic; }
.cite-verify { margin-top: 5px; display: flex; gap: 15px; font-size: 13px; }

.btn-secondary { background: #E0E0E0; color: #333; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.btn-text-cancel { background: none; border: none; color: #999; cursor: pointer; text-decoration: underline; margin-left: 10px; }

.blind-checkbox-group {
  margin-bottom: 1rem;
}

.checkbox-label.disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.checkbox-text {
  color: #C93737;
  font-weight: 600;
  margin-left: 8px;
}

.blind-hint {
  margin: 4px 0 0 24px;
  font-size: 12px;
  color: #999;
}

.blind-actions {
  margin-top: 1rem;
}

.btn-brand-red {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-brand-red:hover {
  background-color: #c82333;
}

.btn-brand-red.confirmed {
  background-color: #27ae60;
  cursor: default;
}

.self-check-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.inst-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}

.inst-suggestions li {
  padding: 8px 12px;
  cursor: pointer;
}

.inst-suggestions li:hover {
  background: #f0f8ff;
}
</style>
