<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { EMAIL_TEMPLATES } from '../../../../constants/emailTemplates.js'

const props = defineProps({
  visible: Boolean,
  manuscript: Object,
  reviewer: Object, // Added reviewer prop
  reviewers: Array, // Added for batch operations
  actionType: String, // 'format_check', 'desk_reject', 'assign_editor', 'request_revision', 'withdraw', 'add_note', 'view_history', 'invite_reviewer', 'cancel_invitation', 'batch_invite', 'batch_remind', 'batch_mark_active', 'batch_mark_inactive' etc.
  currentUser: Object
})

const emit = defineEmits(['close', 'submit'])

// State
const isLoading = ref(true)
const isSubmitting = ref(false)
const conflictCheckResult = ref('Checking...')
const batchConflictResults = ref({}) // Map reviewer ID to result

// Forms Data
const forms = reactive({
  formatCheck: {
    docFormat: false,
    figures: false,
    references: false,
    abstract: false,
    keywords: false,
    ethics: false,
    remarks: ''
  },
  deskReject: {
    reason: '',
    detail: ''
  },
  assignEditor: {
    aeId: '',
    remarks: ''
  },
  requestRevision: {
    type: '',
    content: '',
    deadline: '',
    attachments: []
  },
  withdraw: {
    reason: '',
    detail: ''
  },
  addNote: {
    type: '',
    content: '',
    reminderTime: '',
    reminderRecipient: ''
  },
  // Under Review Actions
  remindReviewer: {
    selectedReviewers: [],
    subject: 'Reminder: Manuscript Review Due',
    content: 'Dear Dr. [Name], ...'
  },
  replaceReviewer: {
    originalReviewerId: '',
    reason: '',
    newReviewerId: '', // Would need integration with AssignReviewers logic
    invitationContent: ''
  },
  extendDeadline: {
    reviewerId: '',
    newDeadline: '',
    reason: ''
  },
  requestFurtherReview: {
    reason: '',
    detail: '',
    newReviewerId: '',
    content: ''
  },
  // Ready for Decision Actions
  approveDecision: {
    result: '',
    remarks: ''
  },
  // Decision Made Actions
  generateDecisionLetter: {
    content: ''
  },
  sendToProduction: {
    priority: 'Normal',
    remarks: '',
    attachments: []
  },
  archive: {
    type: '',
    remarks: ''
  },
  // Reviewer Management Actions
  inviteReviewer: {
    deadline: '',
    subject: EMAIL_TEMPLATES.reviewerInvitation.subject,
    content: EMAIL_TEMPLATES.reviewerInvitation.content
  },
  cancelInvitation: {
    reason: '',
    remarks: ''
  },
  // Batch Actions
  batchInvite: {
    selectedReviewers: [], // Subset of props.reviewers confirmed to invite
    deadline: '',
    subject: EMAIL_TEMPLATES.reviewerInvitation.subject,
    content: EMAIL_TEMPLATES.reviewerInvitation.content
  },
  batchRemind: {
    selectedManuscripts: [], // Should map manuscript IDs
    subject: 'Reminder: Manuscript Review Due',
    content: 'Dear Dr. [Name], ...'
  },
  batchMarkActive: {
    remarks: ''
  },
  batchMarkInactive: {
    reason: '',
    othersDetail: '' // for validation >= 20 chars
  },
  // New Action: Notify Author of Recommendation Results
  notifyWriterRecommendation: {
    subject: EMAIL_TEMPLATES.recommendationResults.subject,
    content: EMAIL_TEMPLATES.recommendationResults.content,
    channels: ['email', 'system_message'], // Default both selected
    additionalNote: ''
  }
})

// Mock Data
const aeList = ref([
  { id: 'ae1', name: 'Dr. Smith', field: 'Oncology' },
  { id: 'ae2', name: 'Dr. Jones', field: 'Cardiology' }
])
const reviewers = ref([
  { id: 'r1', name: 'Reviewer A', institution: 'Harvard', deadline: '2026-03-01' },
  { id: 'r2', name: 'Reviewer B', institution: 'Yale', deadline: '2026-02-28' }
])
const historyLogs = ref([
  { operator: 'Editor', type: 'Initial Review', time: '2026-02-01 10:00', result: 'Pass', remarks: 'Good quality' },
  { operator: 'Author', type: 'Submission', time: '2026-01-30 14:00', result: 'Submitted', remarks: '-' }
])
// Mock Pending Manuscripts for Reviewer
const pendingManuscripts = ref([
  { id: 'MS-001', title: 'Deep Learning in X-Ray', status: 'Under Review', due: '2026-02-20' },
  { id: 'MS-005', title: 'Cancer Research Update', status: 'Pending Acceptance', due: '2026-02-25' }
])

// Validation Logic
const isFormValid = computed(() => {
  switch (props.actionType) {
    case 'format_check':
      // If checks are false, remarks needed? Prompt says: "If not qualified, show red hint"
      // Let's assume remarks needed if any check is false.
      const allChecked = Object.values(forms.formatCheck).slice(0, 6).every(v => v === true)
      if (!allChecked && !forms.formatCheck.remarks) return false
      return true
    case 'desk_reject':
      return forms.deskReject.reason && forms.deskReject.detail.length >= 50
    case 'assign_editor':
      return !!forms.assignEditor.aeId
    case 'request_revision':
      return forms.requestRevision.type && forms.requestRevision.content && forms.requestRevision.deadline
    case 'withdraw':
      return forms.withdraw.reason && forms.withdraw.detail
    case 'add_note':
      return forms.addNote.type && forms.addNote.content
    case 'remind_reviewer':
      // If manuscript context, check selectedReviewers. If reviewer context, just content/subject.
      if (props.manuscript) {
        return forms.remindReviewer.selectedReviewers.length > 0 && forms.remindReviewer.subject && forms.remindReviewer.content
      } else {
        return forms.remindReviewer.subject && forms.remindReviewer.content
      }
    case 'replace_reviewer':
      // If manuscript context
      if (props.manuscript) {
        return forms.replaceReviewer.originalReviewerId && forms.replaceReviewer.reason
      } else {
        // Reviewer context
        return forms.replaceReviewer.newReviewerId && forms.replaceReviewer.reason
      }
    case 'extend_deadline':
      return forms.extendDeadline.reviewerId && forms.extendDeadline.newDeadline
    case 'request_further_review':
      return forms.requestFurtherReview.reason && forms.requestFurtherReview.detail
    case 'approve_decision':
      return forms.approveDecision.result && forms.approveDecision.remarks
    case 'generate_decision_letter':
      return !!forms.generateDecisionLetter.content
    case 'send_to_production':
      return !!forms.sendToProduction.priority
    case 'archive':
      return !!forms.archive.type
    case 'invite_reviewer':
      return forms.inviteReviewer.deadline && forms.inviteReviewer.subject && forms.inviteReviewer.content
    case 'cancel_invitation':
      return forms.cancelInvitation.reason
    case 'batch_invite':
      // Must select at least one reviewer (though usually all selected initially)
      // And template fields
      // Conflict check logic might be: only allow if at least one selected? 
      // User says: "System automatically checks... Editor can manually confirm".
      // We assume forms.batchInvite.selectedReviewers contains the final list to send.
      return forms.batchInvite.selectedReviewers.length > 0 && forms.batchInvite.deadline && forms.batchInvite.subject && forms.batchInvite.content
    case 'batch_remind':
      // Select manuscripts? 
      // "Editor can check manuscripts to remind".
      return forms.batchRemind.selectedManuscripts.length > 0 && forms.batchRemind.subject && forms.batchRemind.content
    case 'batch_mark_active':
      return true // remarks optional
    case 'batch_mark_inactive':
      if (forms.batchMarkInactive.reason === 'Others') {
        return forms.batchMarkInactive.othersDetail.length >= 20
      }
      return !!forms.batchMarkInactive.reason
    case 'notify_writer_recommendation':
      return forms.notifyWriterRecommendation.subject && forms.notifyWriterRecommendation.content && forms.notifyWriterRecommendation.channels.length > 0
    default:
      return true
  }
})

// Methods
const initData = () => {
  isLoading.value = true
  conflictCheckResult.value = 'Checking...'
  batchConflictResults.value = {}
  
  // Simulate Conflict Check for Invite
  if (props.actionType === 'invite_reviewer') {
    let content = EMAIL_TEMPLATES.reviewerInvitation.content
    content = content.replace('[Manuscript ID]', props.manuscript?.id || 'MS-2026-001')
                     .replace('[Manuscript Title]', props.manuscript?.title || 'Untitled')
                     .replace('[Submission Date]', '2026-02-10')
                     .replace('[Due Date]', forms.inviteReviewer.deadline || '2026-03-01') // Use form deadline if set, or default
                     .replace('[Reviewer Full Name]', props.reviewer?.name || 'Reviewer')
                     .replace('[Relevant Field, e.g., cardiovascular research]', props.reviewer?.reason || 'your expertise') // Use reason or field
    
    // Dynamic Link based on Reviewer Type
    const isExternal = props.reviewer?.type === 'External'
    const acceptLink = isExternal 
      ? `http://localhost:5173/reviewer-registration?email=${props.reviewer?.email}&invite=true`
      : `http://localhost:5173/login?email=${props.reviewer?.email}&redirect=review`
      
    content = content.replace('[Accept Link]', acceptLink)
                     .replace('[Decline Link]', `http://localhost:5173/reviewer-decline?email=${props.reviewer?.email}`)
    
    forms.inviteReviewer.content = content
    
    // Set Subject
    forms.inviteReviewer.subject = EMAIL_TEMPLATES.reviewerInvitation.subject
      .replace('[Manuscript ID]', props.manuscript?.id || 'MS-2026-001')
      .replace('[Manuscript Title]', props.manuscript?.title || 'Untitled')

    setTimeout(() => {
      conflictCheckResult.value = 'No conflicts found (Safe to Invite)'
    }, 1500)
  }

  // Batch Invite Init
  if (props.actionType === 'batch_invite') {
    forms.batchInvite.selectedReviewers = props.reviewers.map(r => r.id)
    props.reviewers.forEach(r => {
      batchConflictResults.value[r.id] = 'Checking...'
      setTimeout(() => {
        // Mock random conflict
        batchConflictResults.value[r.id] = Math.random() > 0.8 ? 'Conflict Found' : 'Safe'
      }, 1000 + Math.random() * 1000)
    })
  }
  
  // Batch Remind Init
  if (props.actionType === 'batch_remind') {
    forms.batchRemind.selectedManuscripts = []
  }

  // Notify Author Init
  if (props.actionType === 'notify_writer_recommendation' && props.reviewers) {
    let content = EMAIL_TEMPLATES.recommendationResults.content
    
    // Replace Basic Info
    content = content.replace('[Manuscript ID]', props.manuscript?.id || 'MS-2026-001')
                     .replace('[Manuscript Title]', props.manuscript?.title || 'Untitled')
                     .replace('[Submission Time]', '2026-02-10 10:00')
                     .replace('[Corresponding Author Full Name]', 'Dr. Author')
                     .replace('[Date]', new Date().toLocaleDateString())

    // Generate Dynamic Reviewer List
    let reviewersHtml = ''
    props.reviewers.forEach((r, index) => {
      const decisionColor = r.status === 'Rejected' ? '#999' : '#C93737' // Gray for Reject, Red for Approved (per template)
      const decisionText = r.status === 'Rejected' ? 'Rejected' : 'Approved'
      
      let detailLine = ''
      if (r.status === 'Rejected') {
        detailLine = `<p style="margin: 0; font-size: 14px; color: #555;">Rejection Reason: ${r.rejectionReason || 'Conflict of Interest'}</p>`
      } else {
        const inviteStatus = r.status === 'Invited' ? 'Invitation Sent' : 'Invitation will be sent shortly'
        detailLine = `<p style="margin: 0; font-size: 14px; color: #555;">Invitation Status: ${inviteStatus}</p>`
      }

      // Add border for all except last one (logic can be simple: always add margin bottom)
      const borderStyle = index < props.reviewers.length - 1 ? 'border-bottom: 1px dashed #ddd; padding-bottom: 10px; margin-bottom: 15px;' : 'margin-bottom: 5px;'

      reviewersHtml += `
        <div style="${borderStyle}">
          <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">${r.name}</p>
          <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">Affiliation: ${r.affiliation || 'N/A'}</p>
          <p style="margin: 0 0 5px 0; font-size: 14px; color: ${decisionColor}; font-weight: bold;">Editorial Decision: ${decisionText}</p>
          ${detailLine}
        </div>
      `
    })

    // Find the placeholder section start and end
    // We look for the first reviewer block start
    const startMarker = '<div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #ddd;">'
    const endMarker = 'Rejection Reason: [Objective reason, e.g., potential conflict of interest, research field mismatch]</p>\n              </div>'
    
    // Simple robust replacement: Find the container "Reviewer Recommendation Results" and "Next Processing Flow"
    // And replace the content between them.
    const containerStart = 'Reviewer Recommendation Results</p>'
    const containerEnd = '<div style="margin-bottom: 20px;">\n               <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold;'
    
    // Actually, finding unique strings is better.
    // The template has: <p ...>Reviewer Recommendation Results</p>
    // Then the reviewer blocks.
    // Then </div> (closing the gray box).
    // Then <div ...> <p ...>Next Processing Flow</p>
    
    // Let's use the container start and end div logic.
    const startIdx = content.indexOf(containerStart)
    if (startIdx !== -1) {
       const endIdx = content.indexOf('</div>', startIdx) // Find the closing div of the gray box
       if (endIdx !== -1) {
          // Keep the header "Reviewer Recommendation Results</p>"
          const headerEndIdx = startIdx + containerStart.length
          const prefix = content.substring(0, headerEndIdx)
          const suffix = content.substring(endIdx)
          
          content = prefix + '\n' + reviewersHtml + '\n' + suffix
       }
    }
    
    forms.notifyWriterRecommendation.content = content
    
    // Set Subject
    forms.notifyWriterRecommendation.subject = EMAIL_TEMPLATES.recommendationResults.subject
      .replace('[Manuscript ID]', props.manuscript?.id || 'MS-2026-001')
      .replace('[Manuscript Title]', props.manuscript?.title || 'Untitled')
  }

  // Reset forms based on actionType if needed
  setTimeout(() => {
    isLoading.value = false
  }, 500)
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  isSubmitting.value = true
  
  // Simulate API
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  emit('submit', {
    type: props.actionType,
    data: forms[props.actionType.replace(/_([a-z])/g, (g) => g[1].toUpperCase())] // convert snake_case to camelCase key
  })
  
  isSubmitting.value = false
  emit('close')
}

// Watchers
watch(() => props.visible, (val) => {
  if (val) initData()
})

// Titles
const modalTitle = computed(() => {
  const map = {
    format_check: 'Format Check',
    desk_reject: 'Desk Reject',
    assign_editor: 'Assign to Editor',
    request_revision: 'Request Revision',
    withdraw: 'Withdraw Manuscript',
    add_note: 'Add Internal Note',
    view_history: 'Manuscript History',
    remind_reviewer: 'Remind Reviewer',
    replace_reviewer: 'Replace Reviewer',
    extend_deadline: 'Extend Review Deadline',
    request_further_review: 'Request Further Review',
    approve_decision: 'Approve Decision',
    generate_decision_letter: 'Generate Decision Letter',
    send_to_production: 'Send to Production',
    archive: 'Archive Manuscript',
    invite_reviewer: 'Invite Reviewer',
    cancel_invitation: 'Cancel Invitation',
    batch_invite: 'Batch Invite Reviewers',
    batch_remind: 'Batch Remind Reviewers',
    batch_mark_active: 'Batch Mark as Active',
    batch_mark_inactive: 'Batch Mark as Inactive',
    notify_writer_recommendation: 'Notify Writer Recommendation Results'
  }
  let title = map[props.actionType] || 'Action'
  if (props.manuscript) {
    title += ` - [${props.manuscript.id}]`
  } else if (props.reviewer) {
    title += ` - [${props.reviewer.name}]`
  }
  return title
})

</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-container">
      <header class="modal-header">
        <h3>{{ modalTitle }}</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>

      <div class="modal-body" v-if="!isLoading">
        
        <!-- 1. Format Check -->
        <div v-if="actionType === 'format_check'">
           <div class="info-block">
             <p><strong>ID:</strong> {{ manuscript.id }} | <strong>Title:</strong> {{ manuscript.title }}</p>
           </div>
           <div class="check-list">
             <label><input type="checkbox" v-model="forms.formatCheck.docFormat"> Document Format (Word/PDF meets requirements)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.figures"> Figure/Tables Clarity (≥300dpi)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.references"> Reference Format</label>
             <label><input type="checkbox" v-model="forms.formatCheck.abstract"> Abstract Word Count (≤250 words)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.keywords"> Keyword Quantity (3-6 keywords)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.ethics"> Ethics Statement</label>
           </div>
           <div class="form-group">
             <label>Remarks (Required if unqualified)</label>
             <textarea v-model="forms.formatCheck.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 2. Desk Reject -->
        <div v-if="actionType === 'desk_reject'">
          <div class="warning-banner">Desk Reject is only for manuscripts clearly outside the scope /with extremely low academic quality</div>
          <div class="form-group">
            <label class="required">Rejection Reason</label>
            <select v-model="forms.deskReject.reason" class="select-input">
              <option value="" disabled>Select Reason</option>
              <option value="Out of Scope">Out of Scope</option>
              <option value="Insufficient Originality">Insufficient Originality</option>
              <option value="Methodological Flaws">Methodological Flaws</option>
              <option value="Severe Format Errors">Severe Format Errors</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">Detailed Reason (≥50 words)</label>
            <textarea v-model="forms.deskReject.detail" rows="6" class="textarea-input"></textarea>
          </div>
        </div>

        <!-- 3. Assign to Editor -->
        <div v-if="actionType === 'assign_editor'">
           <div class="form-group">
             <label class="required">Associate Editor List</label>
             <select v-model="forms.assignEditor.aeId" class="select-input">
               <option value="" disabled>Select AE</option>
               <option v-for="ae in aeList" :key="ae.id" :value="ae.id">{{ ae.name }} - {{ ae.field }}</option>
             </select>
           </div>
           <div class="form-group">
             <label>Assignment Remarks</label>
             <textarea v-model="forms.assignEditor.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 4. Request Revision -->
        <div v-if="actionType === 'request_revision'">
           <div class="form-group">
             <label class="required">Revision Type</label>
             <select v-model="forms.requestRevision.type" class="select-input">
               <option value="Format Revision">Format Revision</option>
               <option value="Content Revision">Content Revision</option>
               <option value="Attachment Revision">Attachment Revision</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">Content</label>
             <textarea v-model="forms.requestRevision.content" rows="6" class="textarea-input" placeholder="Rich Text Editor placeholder..."></textarea>
           </div>
           <div class="form-group">
             <label class="required">Deadline</label>
             <input type="date" v-model="forms.requestRevision.deadline" class="input-text">
           </div>
        </div>

        <!-- 5. Withdraw Manuscript -->
        <div v-if="actionType === 'withdraw'">
           <div class="warning-banner red">Withdrawal terminates the process and the manuscript cannot be recovered, please proceed with caution</div>
           <div class="form-group">
             <label class="required">Withdrawal Reason</label>
             <select v-model="forms.withdraw.reason" class="select-input">
               <option value="Author's Initiative">Author's Initiative</option>
               <option value="Academic Misconduct">Academic Misconduct</option>
               <option value="Duplicate Submission">Duplicate Submission</option>
               <option value="Others">Others</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">Detailed Explanation</label>
             <textarea v-model="forms.withdraw.detail" rows="4" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 6. Add Note -->
        <div v-if="actionType === 'add_note'">
           <div class="form-group">
             <label class="required">Note Type</label>
             <select v-model="forms.addNote.type" class="select-input">
               <option value="Communication Record">Communication Record</option>
               <option value="To-Do">To-Do</option>
               <option value="Special Instructions">Special Instructions</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">Content</label>
             <textarea v-model="forms.addNote.content" rows="4" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 7. View History -->
        <div v-if="actionType === 'view_history'">
           <div class="history-list">
             <div v-for="(log, idx) in historyLogs" :key="idx" class="history-item">
               <div class="history-meta">{{ log.time }} | {{ log.operator }}</div>
               <div class="history-content"><strong>{{ log.type }}</strong>: {{ log.result }}</div>
               <div class="history-remarks">{{ log.remarks }}</div>
             </div>
           </div>
        </div>
        
        <!-- Under Review Actions -->
        <!-- 8. Remind Reviewer -->
        <div v-if="actionType === 'remind_reviewer'">
          <div v-if="manuscript" class="reviewer-select-list">
             <label v-for="r in reviewers" :key="r.id">
               <input type="checkbox" :value="r.id" v-model="forms.remindReviewer.selectedReviewers">
               {{ r.name }} (Due: {{ r.deadline }})
             </label>
          </div>
          <div v-if="reviewer" class="pending-manuscripts">
             <h4>Pending Manuscripts</h4>
             <ul>
               <li v-for="ms in pendingManuscripts" :key="ms.id">
                 {{ ms.id }} - {{ ms.title }} (Due: {{ ms.due }})
               </li>
             </ul>
          </div>
          <div class="form-group">
            <label>Email Subject</label>
            <input v-model="forms.remindReviewer.subject" class="input-text">
          </div>
          <div class="form-group">
            <label>Email Content</label>
            <textarea v-model="forms.remindReviewer.content" rows="4" class="textarea-input"></textarea>
          </div>
        </div>
        
        <!-- 9. Replace Reviewer -->
        <div v-if="actionType === 'replace_reviewer'">
          <div v-if="manuscript" class="form-group">
            <label class="required">Original Reviewer</label>
            <select v-model="forms.replaceReviewer.originalReviewerId" class="select-input">
              <option v-for="r in reviewers" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div v-if="reviewer" class="info-block">
             Replacing Reviewer: <strong>{{ reviewer.name }}</strong>
             <div class="pending-list">
               Affects {{ pendingManuscripts.length }} Pending Manuscripts
             </div>
          </div>
          <div class="form-group">
            <label class="required">Reason</label>
            <select v-model="forms.replaceReviewer.reason" class="select-input">
              <option value="Rejected Review">Rejected Review</option>
              <option value="Unreachable">Unreachable</option>
              <option value="Conflict of Interest">Conflict of Interest</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">New Reviewer (Mock Select)</label>
            <select v-model="forms.replaceReviewer.newReviewerId" class="select-input">
               <option value="new_rev_1">Dr. Recommended 1 (Same Field)</option>
               <option value="new_rev_2">Dr. Recommended 2</option>
            </select>
          </div>
          <div class="info-block">System will automatically generate cancellation and new invitation emails.</div>
        </div>

        <!-- 16. Invite Reviewer -->
        <div v-if="actionType === 'invite_reviewer'">
           <div class="info-block">
             <p><strong>Reviewer:</strong> {{ reviewer?.name }} | <strong>Email:</strong> {{ reviewer?.email }}</p>
             <p><strong>Field:</strong> {{ reviewer?.field }} | <strong>Metrics:</strong> {{ reviewer?.avgTurnaround }} / {{ reviewer?.completedReviews }} reviews</p>
           </div>
           <div class="info-block" :class="conflictCheckResult.includes('Safe') ? 'green' : 'orange'">
             <strong>Conflict Check:</strong> {{ conflictCheckResult }}
           </div>
           <div class="form-group">
             <label class="required">Deadline</label>
             <input type="date" v-model="forms.inviteReviewer.deadline" class="input-text">
           </div>
           <div class="form-group">
             <label class="required">Email Subject</label>
             <input v-model="forms.inviteReviewer.subject" class="input-text">
           </div>
           <div class="form-group">
             <label class="required">Email Content</label>
             <textarea v-model="forms.inviteReviewer.content" rows="6" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 17. Cancel Invitation -->
         <div v-if="actionType === 'cancel_invitation'">
            <div class="warning-banner red">The system will automatically notify the reviewer after canceling the invitation</div>
            <div class="form-group">
              <label class="required">Reason</label>
              <select v-model="forms.cancelInvitation.reason" class="select-input">
                <option value="Mistaken Invitation">Mistaken Invitation</option>
                <option value="Reviewer Request">Reviewer Request</option>
                <option value="Others">Others</option>
              </select>
            </div>
            <div class="form-group">
              <label>Remarks</label>
              <textarea v-model="forms.cancelInvitation.remarks" rows="3" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 18. Batch Invite -->
         <div v-if="actionType === 'batch_invite'">
            <div class="reviewer-list-batch">
               <div v-for="r in reviewers" :key="r.id" class="batch-item">
                  <label>
                    <input type="checkbox" :value="r.id" v-model="forms.batchInvite.selectedReviewers">
                    {{ r.name }} ({{ r.email }})
                  </label>
                  <span class="conflict-tag" :class="batchConflictResults[r.id] === 'Safe' ? 'green' : 'orange'">
                     {{ batchConflictResults[r.id] }}
                  </span>
               </div>
            </div>
            <div class="form-group">
              <label class="required">Deadline</label>
              <input type="date" v-model="forms.batchInvite.deadline" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">Email Subject</label>
              <input v-model="forms.batchInvite.subject" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">Email Content</label>
              <textarea v-model="forms.batchInvite.content" rows="6" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 19. Batch Remind -->
         <div v-if="actionType === 'batch_remind'">
            <div class="info-block">
               Select Manuscripts to Remind (Mock List):
            </div>
            <div class="manuscript-select-list">
               <!-- Mocking manuscript list based on reviewers -->
               <div v-for="r in reviewers" :key="r.id">
                  <strong>{{ r.name }}</strong>
                  <div v-for="i in r.pendingCount" :key="i" class="ms-item">
                     <label>
                        <!-- Mock MS ID generation -->
                        <input type="checkbox" :value="`MS-${r.id}-${i}`" v-model="forms.batchRemind.selectedManuscripts">
                        MS-2026-{{ r.id }}0{{ i }} (Pending)
                     </label>
                  </div>
               </div>
            </div>
            <div class="form-group">
              <label class="required">Email Subject</label>
              <input v-model="forms.batchRemind.subject" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">Email Content</label>
              <textarea v-model="forms.batchRemind.content" rows="6" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 20. Batch Mark Active -->
         <div v-if="actionType === 'batch_mark_active'">
            <div class="info-block">
               Confirm marking {{ reviewers.length }} reviewers as <strong>Active</strong>?
            </div>
            <div class="reviewer-names-list">
               {{ reviewers.map(r => r.name).join(', ') }}
            </div>
            <div class="form-group">
               <label>Optional Remarks</label>
               <textarea v-model="forms.batchMarkActive.remarks" rows="3" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 21. Batch Mark Inactive -->
         <div v-if="actionType === 'batch_mark_inactive'">
            <div class="info-block">
               Confirm marking {{ reviewers.length }} reviewers as <strong>Inactive</strong>?
            </div>
            <div class="reviewer-names-list">
               {{ reviewers.map(r => r.name).join(', ') }}
            </div>
            <div class="form-group">
              <label class="required">Reason</label>
              <select v-model="forms.batchMarkInactive.reason" class="select-input">
                <option value="Long-term Rejection of Review">Long-term Rejection of Review</option>
                <option value="Unreachable">Unreachable</option>
                <option value="Academic Misconduct">Academic Misconduct</option>
                <option value="Others">Others</option>
              </select>
            </div>
            <div class="form-group" v-if="forms.batchMarkInactive.reason === 'Others'">
              <label class="required">Detailed Explanation (≥20 chars)</label>
              <textarea v-model="forms.batchMarkInactive.othersDetail" rows="3" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 22. Notify Author Recommendation Results -->
         <div v-if="actionType === 'notify_writer_recommendation'">
            <div class="info-block">
               <p>Notify writer about the decision on their recommended reviewers.</p>
            </div>
            
            <div class="form-group">
               <label class="required">Notification Channels</label>
               <div class="check-list horizontal">
                  <label><input type="checkbox" v-model="forms.notifyWriterRecommendation.channels" value="email"> Email</label>
                  <label><input type="checkbox" v-model="forms.notifyWriterRecommendation.channels" value="system_message"> Station Message</label>
               </div>
            </div>

            <div class="form-group">
              <label class="required">Email Subject</label>
              <input v-model="forms.notifyWriterRecommendation.subject" class="input-text">
            </div>
            
            <div class="form-group">
               <label>Email Content Preview (Auto-generated)</label>
               <!-- Use a read-only div for HTML preview if possible, or textarea -->
               <!-- The requirement says "Preview content... optional input for additional notes" -->
               <!-- Let's show the HTML content in a preview box and allow editing raw HTML or just show it read-only? -->
               <!-- "All content auto-filled... edit confirming" implies editable? -->
               <!-- "Reviewer Management" -> "Send Invite" -> "Auto-filled, cannot modify" (User 1) -->
               <!-- "Notify Author" -> "Preview content... optional input for additional notes" (User 5) -->
               
               <!-- So Content is Preview (Maybe ReadOnly), plus an Additional Note input -->
               <div class="html-preview" v-html="forms.notifyWriterRecommendation.content"></div>
            </div>

            <div class="form-group">
               <label>Additional Notes (Optional)</label>
               <textarea v-model="forms.notifyWriterRecommendation.additionalNote" rows="3" class="textarea-input" placeholder="Enter any additional explanation for the writer..."></textarea>
            </div>
         </div>
        
        <!-- 10. Extend Deadline -->
        <div v-if="actionType === 'extend_deadline'">
           <div class="form-group">
            <label class="required">Reviewer</label>
            <select v-model="forms.extendDeadline.reviewerId" class="select-input">
              <option v-for="r in reviewers" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">New Deadline</label>
            <input type="date" v-model="forms.extendDeadline.newDeadline" class="input-text">
          </div>
        </div>
        
        <!-- 11. Request Further Review -->
        <div v-if="actionType === 'request_further_review'">
           <div class="form-group">
             <label class="required">Reason</label>
             <select v-model="forms.requestFurtherReview.reason" class="select-input">
               <option value="Conflicting Reviews">Conflicting Reviews</option>
               <option value="Insufficient Comments">Insufficient Comments</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">Explanation</label>
             <textarea v-model="forms.requestFurtherReview.detail" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- Ready for Decision -->
        <!-- 12. Approve Decision -->
        <div v-if="actionType === 'approve_decision'">
           <div class="info-block">AE Recommendation: Accept (Mock)</div>
           <div class="form-group">
             <label class="required">Approval Result</label>
             <select v-model="forms.approveDecision.result" class="select-input">
               <option value="Approve">Approve</option>
               <option value="Reject & Revise">Reject & Revise</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">Remarks</label>
             <textarea v-model="forms.approveDecision.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- Decision Made -->
        <!-- 13. Generate Decision Letter -->
        <div v-if="actionType === 'generate_decision_letter'">
           <div class="form-group">
             <label class="required">Letter Content</label>
             <textarea v-model="forms.generateDecisionLetter.content" rows="10" class="textarea-input" placeholder="Dear Author..."></textarea>
           </div>
        </div>
        
        <!-- 14. Send to Production -->
        <div v-if="actionType === 'send_to_production'">
           <div class="form-group">
             <label class="required">Priority</label>
             <select v-model="forms.sendToProduction.priority" class="select-input">
               <option value="Normal">Normal</option>
               <option value="Urgent">Urgent</option>
             </select>
           </div>
           <div class="form-group">
             <label>Remarks</label>
             <textarea v-model="forms.sendToProduction.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- 15. Archive -->
        <div v-if="actionType === 'archive'">
           <div class="warning-banner red">Archived manuscripts will be moved to historical library, process information cannot be modified</div>
           <div class="form-group">
             <label class="required">Archive Type</label>
             <select v-model="forms.archive.type" class="select-input">
               <option value="Accepted Archive">Accepted Archive</option>
               <option value="Rejected Archive">Rejected Archive</option>
             </select>
           </div>
        </div>

      </div>

      <footer class="modal-footer">
        <button v-if="actionType !== 'view_history'" class="btn btn-cancel" @click="$emit('close')">Cancel</button>
        <button v-else class="btn btn-primary" @click="$emit('close')">Close</button>
        
        <button 
          v-if="actionType !== 'view_history'" 
          class="btn btn-primary" 
          :disabled="!isFormValid || isSubmitting"
          @click="handleSubmit"
        >
          Confirm
        </button>
      </footer>
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
  background: white; width: 600px; max-height: 90vh;
  display: flex; flex-direction: column;
  border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.modal-header {
  padding: 1rem 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;
}
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #2c3e50; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }

.modal-body { padding: 1.5rem; overflow-y: auto; flex: 1; }

.modal-footer {
  padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem;
}

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.9rem; }
.required::after { content: " *"; color: #e74c3c; }

.input-text, .select-input, .textarea-input { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; }

.warning-banner { background: #fff3cd; color: #856404; padding: 0.8rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; }
.warning-banner.red { background: #f8d7da; color: #721c24; }

.check-list label { display: block; margin-bottom: 0.5rem; cursor: pointer; }
.info-block { background: #f8f9fa; padding: 0.8rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; }

.info-block.green { background: #e8f5e9; color: #2e7d32; }
.info-block.orange { background: #fff3e0; color: #e65100; }
.pending-manuscripts { margin-bottom: 1rem; padding: 0.8rem; border: 1px solid #eee; border-radius: 4px; }
.pending-manuscripts h4 { margin: 0 0 0.5rem 0; font-size: 0.95rem; }
.pending-manuscripts ul { padding-left: 1.2rem; margin: 0; font-size: 0.9rem; color: #666; }
.history-meta { font-size: 0.8rem; color: #7f8c8d; }
.history-content { margin: 0.2rem 0; }
.history-remarks { font-size: 0.85rem; color: #555; font-style: italic; }

.reviewer-list-batch { max-height: 200px; overflow-y: auto; border: 1px solid #eee; padding: 0.5rem; margin-bottom: 1rem; border-radius: 4px; }
.batch-item { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px dashed #f0f0f0; }
.conflict-tag { font-size: 0.8rem; padding: 1px 5px; border-radius: 3px; }
.conflict-tag.green { background: #e8f5e9; color: #2e7d32; }
.conflict-tag.orange { background: #fff3e0; color: #e65100; }

.manuscript-select-list { max-height: 200px; overflow-y: auto; border: 1px solid #eee; padding: 0.5rem; margin-bottom: 1rem; border-radius: 4px; }
.ms-item { margin-left: 1rem; font-size: 0.9rem; color: #555; }
.reviewer-names-list { font-size: 0.9rem; color: #666; margin-bottom: 1rem; line-height: 1.4; }

.btn { padding: 0.6rem 1.5rem; border-radius: 4px; border: none; cursor: pointer; }
.btn-primary { background: #3498db; color: white; }
.btn-primary:disabled { background: #bdc3c7; cursor: not-allowed; }
.btn-cancel { background: #eee; color: #333; }
</style>
