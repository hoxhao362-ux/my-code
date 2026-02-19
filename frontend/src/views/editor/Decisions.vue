<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import SensitiveOperationVerification from '../../components/SensitiveOperationVerification.vue'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'

const userStore = useUserStore()
const user = computed(() => userStore.submissionUser || userStore.user)

// Permissions
const canEditDecision = computed(() => ['admin', 'editor', 'associate_editor'].includes(user.value?.role))
const canSendDecision = computed(() => ['admin', 'associate_editor'].includes(user.value?.role))
const canManageTemplates = computed(() => ['admin', 'editor'].includes(user.value?.role))
const canApprove = computed(() => ['admin', 'editor'].includes(user.value?.role))
const isReadOnly = computed(() => user.value?.role === 'advisory_editor' || user.value?.role === 'editorial_assistant')

// Data
const decisionTemplates = ref([
  { id: 1, name: 'Accept', category: 'Accept', field: 'General', usage: 12, content: 'Dear {{writer_name}},\n\nWe are pleased to accept your manuscript "{{manuscript_title}}" (ID: {{manuscript_id}}) for publication.\n\nBest regards,\n{{editor_name}}' },
  { id: 2, name: 'Minor Revision', category: 'Minor Revision', field: 'General', usage: 45, content: 'Dear {{writer_name}},\n\nYour manuscript "{{manuscript_title}}" requires minor revisions.\n\nReview Comments:\n{{review_comments}}\n\nBest regards,\n{{editor_name}}' },
  { id: 3, name: 'Major Revision', category: 'Major Revision', field: 'General', usage: 30, content: 'Dear {{writer_name}},\n\nYour manuscript "{{manuscript_title}}" requires major revisions.\n\nReview Comments:\n{{review_comments}}\n\nBest regards,\n{{editor_name}}' },
  { id: 4, name: 'Reject', category: 'Reject', field: 'General', usage: 8, content: 'Dear {{writer_name}},\n\nWe regret to inform you that we cannot accept your manuscript "{{manuscript_title}}" for publication at this time.\n\nBest regards,\n{{editor_name}}' }
])

const templateCategories = ['All', 'Accept', 'Minor Revision', 'Major Revision', 'Reject']
const templateFields = ['All', 'General', 'Medical Imaging', 'Oncology', 'Cardiology']
const selectedCategory = ref('All')
const selectedField = ref('All')

// Filtered Templates
const filteredTemplates = computed(() => {
  let list = decisionTemplates.value
  if (selectedCategory.value !== 'All') {
    list = list.filter(t => t.category === selectedCategory.value)
  }
  if (selectedField.value !== 'All') {
    list = list.filter(t => t.field === selectedField.value)
  }
  // Sort by usage
  return list.sort((a, b) => b.usage - a.usage)
})

// Mock Template History
const showTemplateHistory = ref(false)
const templateHistory = ref([
  { version: 'v1.2', date: '2026-01-15', modifier: 'Editor', content: '...' },
  { version: 'v1.1', date: '2025-12-10', modifier: 'Admin', content: '...' }
])

// Mock Manuscripts - Sync with User Store
const manuscripts = computed(() => {
  return userStore.journals.filter(j => 
    j.status === 'review_completed' || 
    j.status === '已审核' ||
    j.status === 'final_decision_pending' ||
    // Include manuscripts with recent decisions for drafting letters
    j.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED ||
    j.status === MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED ||
    j.status === MANUSCRIPT_STATUS.FINAL_DECISION_REVISION ||
    j.status === MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION ||
    j.status === MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
  )
})

// Auto-load draft from Decision Making module
onMounted(() => {
  const drafts = userStore.decisionDrafts || []
  if (drafts.length > 0) {
    // Sort by lastUpdated desc
    const sortedDrafts = [...drafts].sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated))
    const latestDraft = sortedDrafts[0]
    
    // Check if within 5 minutes (fresh context switch)
    const diff = new Date() - new Date(latestDraft.lastUpdated)
    if (diff < 5 * 60 * 1000) {
      selectedManuscriptId.value = latestDraft.manuscriptId
      decisionContent.value = latestDraft.content
      
      // Try to match template
      const tpl = decisionTemplates.value.find(t => t.name === latestDraft.templateType || t.category === latestDraft.templateType)
      if (tpl) {
        selectedTemplate.value = tpl
      }
      
      // Set status to Draft
      approvalStatus.value = 'Draft'
      autoSaveStatus.value = 'Draft loaded from Decision Making module'
    }
  }
})

// Mock Approval Queue Data
const approvalQueue = ref([
  {
    id: 1,
    manuscriptId: 'MS-002',
    manuscriptTitle: 'Novel Drug Delivery Systems',
    author: 'Prof. Bob',
    submittedBy: 'Associate Editor',
    submittedDate: '2026-02-01',
    status: 'Pending',
    templateUsed: 'Minor Revision',
    assignedTo: 'editor'
  },
  {
    id: 2,
    manuscriptId: 'MS-004',
    manuscriptTitle: 'AI Applications in Healthcare',
    author: 'Dr. David',
    submittedBy: 'Associate Editor',
    submittedDate: '2026-02-03',
    status: 'Pending',
    templateUsed: 'Major Revision',
    assignedTo: 'editor'
  },
  {
    id: 3,
    manuscriptId: 'MS-005',
    manuscriptTitle: 'Genomic Sequencing Technologies',
    author: 'Prof. Eve',
    submittedBy: 'Associate Editor',
    submittedDate: '2026-02-05',
    status: 'Pending',
    templateUsed: 'Reject',
    assignedTo: 'editor'
  }
])

const reviewComments = ref([
  { reviewer: 'Reviewer 1', content: 'Excellent work, but needs better figures.', selected: false },
  { reviewer: 'Reviewer 2', content: 'Methodology section is unclear. Please clarify sample size.', selected: false },
  { reviewer: 'Reviewer 3', content: 'References are outdated.', selected: false }
])

const sentLetters = ref([
  { id: 101, recipient: 'Dr. Alice', subject: 'Decision on MS-001', date: '2026-02-01', status: 'Sent', openStatus: 'Opened' },
  { id: 102, recipient: 'Prof. Bob', subject: 'Decision on MS-002', date: '2026-01-28', status: 'Approved', openStatus: 'Unopened' }
])

// State
const activeTab = ref('draft') // draft, sent, approval
const selectedTemplate = ref(null)
const selectedManuscriptId = ref('')
const decisionContent = ref('')
const approvalStatus = ref('Draft') // Draft, Pending, Approved, Rejected
const autoSaveStatus = ref('')
const canViewDetails = computed(() => !isReadOnly.value)


// Computed
const filteredManuscripts = computed(() => {
  if (user.value?.role === 'associate_editor') {
    // AE only sees assigned (Mock)
    return manuscripts.value.filter(m => m.assignedTo === 'ae_user' || m.assignedTo === 'associate_editor') 
    // For demo purposes, let's just return all if mock data doesn't align perfectly or assume 'ae_user'
    // return manuscripts.value 
  }
  return manuscripts.value
})

const selectedManuscript = computed(() => manuscripts.value.find(m => m.id === selectedManuscriptId.value))

// Methods
const selectTemplate = (tpl) => {
  selectedTemplate.value = tpl
  // Auto-fill if manuscript selected
  if (selectedManuscript.value) {
    decisionContent.value = fillTemplate(tpl.content, selectedManuscript.value)
  } else {
    decisionContent.value = tpl.content
  }
  approvalStatus.value = 'Draft'
}

const fillTemplate = (content, ms) => {
  let text = content
  text = text.replace(/{{writer_name}}/g, ms.author)
  text = text.replace(/{{manuscript_title}}/g, ms.title)
  text = text.replace(/{{manuscript_id}}/g, ms.id)
  text = text.replace(/{{editor_name}}/g, user.value?.username || 'Editor')
  text = text.replace(/{{review_comments}}/g, '[Insert Review Comments Here]')
  return text
}

const handleManuscriptChange = () => {
  if (selectedTemplate.value) {
     // Re-apply template with new manuscript data? Or just warn?
     // Let's re-fill for convenience
     decisionContent.value = fillTemplate(selectedTemplate.value.content, selectedManuscript.value)
  }
}

const insertComment = (comment) => {
  decisionContent.value += `\n\n[${comment.reviewer}]: ${comment.content}`
}

const handleSaveDraft = () => {
  autoSaveStatus.value = 'Saving...'
  setTimeout(() => {
    autoSaveStatus.value = 'Saved at ' + new Date().toLocaleTimeString()
  }, 500)
}

// Auto-save simulation
setInterval(() => {
  if (decisionContent.value) handleSaveDraft()
}, 180000) // 3 mins

const handleSend = () => {
  if (user.value?.role === 'associate_editor') {
     // AE Workflow
     // 使用alert替代confirm，因为confirm在某些环境中不被支持
     alert("Submit this decision letter to Editor-in-Chief for approval?")
     // 模拟提交
     approvalStatus.value = 'Pending'
     alert("Submitted for Approval.")
  } else {
    // Editor Workflow
    if (approvalStatus.value === 'Pending') {
       // Approving AE's draft
       approvalStatus.value = 'Approved'
       alert("Decision Approved and Sent.")
    } else {
       // Direct Send
       approvalStatus.value = 'Approved' // Sent implies approved
       
       // Update Journal Status in Store
       if (selectedManuscript.value) {
         const updatedJournal = { ...selectedManuscript.value }
         if (selectedTemplate.value.category === 'Accept') updatedJournal.status = 'accepted'
         else if (selectedTemplate.value.category === 'Reject') updatedJournal.status = 'rejected'
         else if (selectedTemplate.value.category.includes('Revision')) updatedJournal.status = 'revision_required'
         else updatedJournal.status = 'final_decision_made' // Fallback
         
         userStore.updateJournal(updatedJournal)
       }

       alert("Decision Letter Sent to Author.")
    }
    // Add to sent history
    if (selectedManuscript.value) {
      sentLetters.value.unshift({
        id: Date.now(),
        recipient: selectedManuscript.value.author,
        subject: `Decision on ${selectedManuscript.value.id}`,
        date: new Date().toLocaleDateString(),
        status: 'Sent',
        openStatus: 'Unopened'
      })
    }
  }
}

const handleRejectApproval = () => {
  // 使用alert替代prompt，因为prompt在某些环境中不被支持
  alert("Enter reason for rejection functionality would open a form here.")
  // 模拟拒绝
  approvalStatus.value = 'Rejected'
  alert("Draft Rejected. Reason sent to Associate Editor.")
}



// 已移至下方，避免重复声明
// const handleViewDraft = (item) => {
//   alert(`Viewing draft for ${item.manuscriptId}`)
//   // 切换到 drafting tab 并加载内容
//   selectedManuscriptId.value = item.manuscriptId
//   activeTab.value = 'draft'
// }

// const handleAssignToAE = (item) => {
//   // 模拟转交操作
//   const ae = prompt("Enter new Associate Editor name:")
//   if (ae) {
//     alert(`Task assigned to ${ae}. Notification sent.`)
//     const index = approvalQueue.value.findIndex(q => q.id === item.id)
//     if (index !== -1) {
//       approvalQueue.value.splice(index, 1)
//     }
//   }
// }

const handleExportPDF = (letter) => {
  alert(`Exporting PDF for decision to ${letter.recipient}...\nIncluding sending time and metadata.`)
  // Mock Archive
  console.log("Archiving export record for", letter.id)
}

const handleCreateTemplate = () => {
  // 使用alert替代prompt，因为prompt在某些环境中不被支持
  alert("Template creation functionality would open a form here.")
  // 模拟创建模板
  const mockName = "New Template " + Date.now()
  decisionTemplates.value.push({ id: Date.now(), name: mockName, category: 'General', field: 'General', usage: 0, content: 'Dear {{writer_name}}, ...' })
}

const handleEditTemplate = (tpl) => {
  // 使用alert替代prompt，因为prompt在某些环境中不被支持
  alert("Template editing functionality would open an editor here.")
  // 模拟更新模板
  tpl.content += "\n[Updated]"
  alert("Template updated.")
}

const handleDeleteTemplate = (id) => {
  // 使用alert替代confirm，因为confirm在某些环境中不被支持
  alert("Template deletion functionality would show a confirmation here.")
  // 模拟删除模板
  decisionTemplates.value = decisionTemplates.value.filter(t => t.id !== id)
}

const handleRollback = (version) => {
  // Permission Check
  if (!canEditDecision.value) return;
  if (user.value?.role === 'associate_editor' && selectedManuscript.value?.assignedTo !== 'ae_user') {
    alert("You can only rollback drafts you created.");
    return;
  }

  if (confirm(`Rollback to Version ${version.version} - [${selectedManuscriptId.value}]\n\nConfirm rollback to this version? All unsaved changes to the current draft will be overwritten and cannot be recovered. The rollback operation will generate a new version record.`)) {
    // Mock Rollback Logic
    decisionContent.value = version.content || `[Content restored from ${version.version}]`; // Use version content if available
    alert(`Draft rolled back to ${version.version}. New version record generated.`);
    
    // Add new version record
    templateHistory.value.unshift({
      version: `v1.${templateHistory.value.length + 1}`,
      date: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString(),
      modifier: user.value?.username || 'Editor',
      content: decisionContent.value,
      summary: `Rolled back to Version ${version.version}`
    });
    
    showTemplateHistory.value = false;
  }
}

// Compare Logic
const showCompareModal = ref(false)
const showCompareView = ref(false)
const compareSourceVersion = ref(null) // The version clicked "Compare" on
const compareTargetVersion = ref(null) // The version selected to compare against

const handleCompare = (version) => {
  compareSourceVersion.value = version
  compareTargetVersion.value = templateHistory.value.find(v => v.version !== version.version) || templateHistory.value[0] // Default to latest or other
  showCompareModal.value = true
}

const executeCompare = () => {
  showCompareModal.value = false
  showCompareView.value = true
  showTemplateHistory.value = false // Close history list
}

const closeCompareView = () => {
  showCompareView.value = false
  showTemplateHistory.value = true // Re-open history list
}

const handleExportComparison = () => {
  if (user.value?.role === 'editorial_assistant' || user.value?.role === 'advisory_editor') return; // EA/AE hidden logic
  alert(`Exporting Comparison Report: ${selectedManuscriptId.value}-${compareSourceVersion.value.version}-${compareTargetVersion.value.version}.pdf`);
}

const showActionModal = ref(false)
const currentAction = ref('') // 'view_details', 'resend', 'forward', 'add_note', 'approve', 'reject', 'assign_ae'
const currentLetter = ref(null)

// Verification State
const showVerification = ref(false)
const verificationAction = ref('')
const verificationTarget = ref('')
const pendingCallback = ref(null)

// Verification Success Callback
const handleVerificationSuccess = () => {
  if (pendingCallback.value) {
    pendingCallback.value()
    pendingCallback.value = null
  }
}

// Forms for Modals
const actionForms = ref({
  resend: {
    recipient: '',
    subject: '',
    body: '',
    postscript: ''
  },
  forward: {
    recipient: '',
    postscript: '',
    includeOriginal: true
  },
  addNote: {
    type: 'Communication Record',
    content: '',
    reminderTime: ''
  },
  approve: {
    remarks: '',
    autoSend: true
  },
  reject: {
    reason: '',
    detail: '',
    notifyDrafter: true
  },
  assignAE: {
    targetAE: '',
    remarks: ''
  }
})

// View Details Tabs
const viewDetailsTab = ref('content') // content, history, delivery, notes

const openActionModal = (action, item) => {
  currentAction.value = action
  currentLetter.value = item
  showActionModal.value = true
  
  // Init Form Data
  if (action === 'resend') {
    actionForms.value.resend = {
      recipient: item.recipient,
      subject: `Resend: ${item.subject}`,
      body: 'Dear Author,\n\n[Original Content Loaded Here]\n...',
      postscript: ''
    }
  } else if (action === 'approve') {
    actionForms.value.approve = { remarks: '', autoSend: true }
  } else if (action === 'reject') {
    actionForms.value.reject = { reason: '', detail: '', notifyDrafter: true }
  } else if (action === 'assign_ae') {
    actionForms.value.assignAE = { targetAE: '', remarks: '' }
  }
}

const handleConfirmAction = () => {
  const proceed = () => {
    if (currentAction.value === 'resend') {
      alert(`Resending to ${actionForms.value.resend.recipient}...`)
      currentLetter.value.openStatus = 'Unopened'
      currentLetter.value.date = new Date().toLocaleDateString()
    } else if (currentAction.value === 'forward') {
      alert(`Forwarding to ${actionForms.value.forward.recipient}...`)
    } else if (currentAction.value === 'add_note') {
      alert('Internal Note Saved.')
    } else if (currentAction.value === 'approve') {
      alert('Decision Approved.')
      // Update queue
      const idx = approvalQueue.value.findIndex(q => q.id === currentLetter.value.id)
      if (idx !== -1) approvalQueue.value.splice(idx, 1)
      // Add to sent
      sentLetters.value.unshift({
        id: Date.now(),
        recipient: currentLetter.value.author,
        subject: `Decision on ${currentLetter.value.manuscriptId}`,
        date: new Date().toLocaleDateString(),
        status: 'Approved',
        openStatus: 'Unopened'
      })
    } else if (currentAction.value === 'reject') {
      if (actionForms.value.reject.reason === 'Others' && (!actionForms.value.reject.detail || actionForms.value.reject.detail.length < 20)) {
        alert("Please provide a detailed explanation (at least 20 chars).")
        return
      }
      alert('Decision Rejected.')
      const idx = approvalQueue.value.findIndex(q => q.id === currentLetter.value.id)
      if (idx !== -1) approvalQueue.value.splice(idx, 1)
    } else if (currentAction.value === 'assign_ae') {
      alert(`Task reassigned to ${actionForms.value.assignAE.targetAE}.`)
      const idx = approvalQueue.value.findIndex(q => q.id === currentLetter.value.id)
      if (idx !== -1) approvalQueue.value.splice(idx, 1)
    }
    
    showActionModal.value = false
  }

  if (currentAction.value === 'reject') {
    // Sensitive Action: Reject
    verificationAction.value = 'Reject Manuscript Decision'
    verificationTarget.value = currentLetter.value.manuscriptTitle
    pendingCallback.value = proceed
    showVerification.value = true
  } else {
    proceed()
  }
}

const handleViewSentLetter = (letter) => {
  openActionModal('view_details', letter)
}

const handleResend = (letter) => {
  openActionModal('resend', letter)
}

const handleForward = (letter) => {
  openActionModal('forward', letter)
}

const handleAddNote = (letter) => {
  openActionModal('add_note', letter)
}

const handleApprove = (item) => {
  openActionModal('approve', item)
}

const handleReject = (item) => {
  openActionModal('reject', item)
}

// Edit Mode Logic
const editMode = ref(false)

const canToggleEditMode = computed(() => {
  if (user.value?.role === 'editor') return true
  if (user.value?.role === 'associate_editor') {
    // AE can only edit own drafts
    return selectedManuscript.value?.assignedTo === 'ae_user' // Mock logic for "own draft"
  }
  return false
})

const isContentReadOnly = computed(() => {
  if (isReadOnly.value) return true
  if (!editMode.value) return true // Default read-only unless edit mode active
  return false
})

const handleToggleEditMode = () => {
  editMode.value = !editMode.value
}

// Approval Shortcut Methods (Reuse existing logic)
const handleShortcutApprove = () => {
  if (!selectedManuscript.value) return
  // Mock item structure for approve handler
  const item = {
    id: selectedManuscriptId.value, // Mock ID mapping
    manuscriptId: selectedManuscriptId.value,
    author: selectedManuscript.value.author
  }
  handleApprove(item)
}

const handleShortcutReject = () => {
  if (!selectedManuscript.value) return
  const item = {
    id: selectedManuscriptId.value,
    manuscriptId: selectedManuscriptId.value
  }
  handleReject(item)
}

// Version History Shortcut
const handleOpenVersionHistory = () => {
  showTemplateHistory.value = true
}

// Additional Approval Queue Methods
const handleViewDraft = (item) => {
  alert(`Viewing draft for manuscript ${item.manuscriptId}: ${item.manuscriptTitle}`)
  // 模拟查看草稿
  selectedManuscriptId.value = item.manuscriptId
  activeTab.value = 'draft'
  alert("Displaying decision draft in drafting tab.")
}

const handleViewDetails = (item) => {
  alert(`Viewing details for manuscript ${item.manuscriptId}: ${item.manuscriptTitle}`)
  // 模拟查看详情
  selectedManuscriptId.value = item.manuscriptId
  activeTab.value = 'draft'
  alert("Displaying decision details in drafting tab.")
}

// Dropdown State for Template Actions
const showTemplateDropdown = ref(null) // Stores template ID for dropdown visibility

const toggleTemplateDropdown = (id) => {
  if (showTemplateDropdown.value === id) {
    showTemplateDropdown.value = null
  } else {
    showTemplateDropdown.value = id
  }
}

</script>

<template>
  <div class="editor-page">
    <div class="page-header">
      <h2>Decisions & Letters</h2>
      <div class="tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'draft' }" @click="activeTab = 'draft'">Drafting</button>
        <button class="tab-btn" :class="{ active: activeTab === 'sent' }" @click="activeTab = 'sent'">Sent Letters</button>
        <button v-if="canApprove" class="tab-btn" :class="{ active: activeTab === 'approval' }" @click="activeTab = 'approval'">Approval Queue</button>
      </div>
    </div>

    <!-- Drafting Tab -->
    <div v-if="activeTab === 'draft'" class="decision-container">
      
      <!-- Left: Templates -->
      <div class="sidebar templates-sidebar" v-if="!isReadOnly">
        <div class="sidebar-header">
          <h3>Templates</h3>
          <button v-if="canManageTemplates" class="icon-btn" @click="handleCreateTemplate" title="Create Template">+</button>
        </div>
        
        <!-- Template Filters -->
        <div class="template-filters">
           <select v-model="selectedCategory" class="filter-sm">
             <option v-for="c in templateCategories" :key="c" :value="c">{{ c }}</option>
           </select>
           <select v-model="selectedField" class="filter-sm">
             <option v-for="f in templateFields" :key="f" :value="f">{{ f }}</option>
           </select>
        </div>

        <ul>
          <li 
            v-for="tpl in filteredTemplates" 
            :key="tpl.id"
            @click="selectTemplate(tpl)"
            :class="{ active: selectedTemplate?.id === tpl.id }"
            :title="`Used ${tpl.usage} times in 2026`"
          >
            <div class="tpl-item-content">
              <span>{{ tpl.name }}</span>
              <div class="tpl-actions" v-if="canManageTemplates">
                 <button class="dots-btn" @click.stop="toggleTemplateDropdown(tpl.id)">⋮</button>
                 <div v-if="showTemplateDropdown === tpl.id" class="dropdown-menu">
                    <a @click.stop="handleEditTemplate(tpl)">Edit</a>
                    <a @click.stop="showTemplateHistory = true; toggleTemplateDropdown(null)">History</a>
                    <a @click.stop="handleDeleteTemplate(tpl.id)">Delete</a>
                 </div>
              </div>
            </div>
            <div class="tpl-meta">Usage: {{ tpl.usage }}</div>
          </li>
        </ul>
      </div>

      <!-- Center: Editor -->
      <div class="editor-area">
        <div v-if="selectedTemplate || isReadOnly">
          <!-- Manuscript Selection -->
          <div class="form-group" v-if="!isReadOnly">
            <label>Select Manuscript (Auto-fill variables)</label>
            <select v-model="selectedManuscriptId" @change="handleManuscriptChange" class="ms-select">
              <option value="" disabled>-- Select Manuscript --</option>
              <option v-for="ms in filteredManuscripts" :key="ms.id" :value="ms.id">
                [{{ ms.id }}] {{ ms.title }}
              </option>
            </select>
          </div>

          <div class="editor-header">
            <h3>Drafting: {{ selectedTemplate?.name || 'New Decision' }}</h3>
            <div class="header-controls">
               <div v-if="canToggleEditMode" class="edit-mode-toggle">
                  <label class="switch">
                    <input type="checkbox" :checked="editMode" @change="handleToggleEditMode">
                    <span class="slider round"></span>
                  </label>
                  <span>Edit Mode</span>
               </div>
               <span class="status-tag" :class="approvalStatus.toLowerCase()">{{ approvalStatus }}</span>
            </div>
          </div>
          
          <textarea 
            v-model="decisionContent" 
            rows="15" 
            :disabled="isContentReadOnly"
            :class="{ 'read-only': isContentReadOnly }"
            placeholder="Select a template and manuscript to start..."
          ></textarea>
          
          <div class="status-bar">
            <span>{{ autoSaveStatus ? 'Draft Auto-Saved at ' + new Date().toLocaleTimeString() : '' }}</span>
          </div>

          <div class="actions" v-if="!isReadOnly">
            <button @click="handleSaveDraft" class="btn secondary">Save Draft</button>
            <button @click="handleOpenVersionHistory" class="btn secondary">Version History</button>
            
            <!-- Editor Approval Shortcuts -->
            <template v-if="user.role === 'editor'">
               <button @click="handleShortcutApprove" class="btn primary-sm">Approve</button>
               <button @click="handleShortcutReject" class="btn danger-sm">Reject</button>
            </template>
            
            <!-- Editor Approval Actions (Original Logic kept for fallback/context) -->
            <template v-if="approvalStatus === 'Pending' && canApprove">
               <button @click="handleSend" class="btn primary">Approve & Send</button>
               <button @click="handleRejectApproval" class="btn danger">Reject Draft</button>
            </template>
            
            <!-- Standard Send -->
            <template v-else>
               <button 
                 v-if="canSendDecision" 
                 @click="handleSend" 
                 class="btn primary"
               >
                 {{ user?.role === 'associate_editor' ? 'Submit for Approval' : 'Send Decision' }}
               </button>
            </template>
          </div>
        </div>
        <div v-else class="empty-state">
          Select a template to start drafting.
        </div>
      </div>

      <!-- Right: Review Comments -->
      <div class="sidebar comments-sidebar" v-if="selectedManuscriptId && !isReadOnly">
        <h3>Review Comments</h3>
        <div class="comment-list">
          <div v-for="(comment, idx) in reviewComments" :key="idx" class="comment-item">
            <div class="comment-header">
              <strong>{{ comment.reviewer }}</strong>
              <div class="comment-actions">
                 <button class="action-icon-btn" title="Highlight" @click="comment.highlighted = !comment.highlighted">H</button>
                 <button class="action-icon-btn danger" title="Delete" @click="reviewComments.splice(idx, 1)">x</button>
                 <button class="insert-btn" @click="insertComment(comment)" title="Insert into letter">Insert</button>
              </div>
            </div>
            <p :class="{ highlighted: comment.highlighted }">{{ comment.content }}</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Sent Letters Tab -->
    <div v-if="activeTab === 'sent'" class="sent-letters-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Recipient</th>
            <th>Subject</th>
            <th>Status</th>
            <th>Open Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="letter in sentLetters" :key="letter.id">
            <td>{{ letter.date }}</td>
            <td>{{ letter.recipient }}</td>
            <td>{{ letter.subject }}</td>
            <td><span class="status-tag sent">{{ letter.status }}</span></td>
            <td>{{ letter.openStatus }}</td>
            <td>
              <div class="action-buttons">
                <template v-if="canSendDecision">
                  <button class="btn-text" @click="handleViewSentLetter(letter)">View</button>
                  <button class="btn-text" v-if="letter.status === 'Sent'" @click="handleResend(letter)">Resend</button>
                  <button class="btn-text" @click="handleExportPDF(letter)">Export PDF</button>
                  <button class="btn-text" @click="handleForward(letter)">Forward</button>
                  <button class="btn-text" @click="handleAddNote(letter)">Add Note</button>
                </template>
                <template v-else-if="canEditDecision"> <!-- AE view only basic actions -->
                   <button class="btn-text" @click="handleViewSentLetter(letter)">View</button>
                   <button class="btn-text" @click="handleAddNote(letter)">Add Note</button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Approval Queue Tab (Editor Only) -->
    <div v-if="activeTab === 'approval'" class="approval-queue-container">
      <h3>Approval Queue</h3>
      <p>Decisions submitted by Associate Editors awaiting your approval.</p>
      
      <div class="approval-progress" style="margin-bottom: 30px;">
          <div class="step completed">Draft</div>
          <div class="line completed"></div>
          <div class="step active">Pending</div>
          <div class="line"></div>
          <div class="step">Approved/Rejected</div>
      </div>
      
      <div v-if="approvalQueue.length > 0" class="approval-list">
        <table class="approval-table">
          <thead>
            <tr>
              <th>Manuscript</th>
              <th>Author</th>
              <th>Submitted By</th>
              <th>Date Submitted</th>
              <th>Template Used</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in approvalQueue" :key="item.id">
              <td>
                <div class="ms-info">
                  <strong>{{ item.manuscriptTitle }}</strong>
                  <div class="ms-id">{{ item.manuscriptId }}</div>
                </div>
              </td>
              <td>{{ item.author }}</td>
              <td>{{ item.submittedBy }}</td>
              <td>{{ item.submittedDate }}</td>
              <td>{{ item.templateUsed }}</td>
              <td>
                <span class="status-tag pending">{{ item.status }}</span>
              </td>
              <td>
                <div class="action-buttons" v-if="canApprove">
                  <button class="btn primary-sm" @click="handleApprove(item)">Approve</button>
                  <button class="btn danger-sm" @click="handleReject(item)">Reject</button>
                  <button class="btn secondary-sm" @click="handleViewDraft(item)">View Draft</button>
                  <button class="btn secondary-sm" @click="handleAssignToAE(item)">Assign to Another AE</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-else class="empty-state" style="margin-top: 50px;">
        No pending approvals.
      </div>
    </div>

    <!-- Version History Modal -->
    <div v-if="showTemplateHistory" class="modal-overlay">
       <div class="modal-content">
          <h3>Template Version History</h3>
          <table class="history-table">
             <thead><tr><th>Version</th><th>Date</th><th>Modifier</th><th>Action</th></tr></thead>
             <tbody>
                <tr v-for="ver in templateHistory" :key="ver.version">
                   <td>{{ ver.version }}</td>
                   <td>{{ ver.date }}</td>
                   <td>{{ ver.modifier }}</td>
                   <td>
                      <button class="btn secondary-sm" v-if="canEditDecision && (user.role !== 'associate_editor' || selectedManuscript.assignedTo === 'ae_user')" @click="handleRollback(ver)">Rollback</button>
                      <button class="btn secondary-sm" @click="handleCompare(ver)">Compare</button>
                   </td>
                </tr>
             </tbody>
          </table>
          <button @click="showTemplateHistory = false" class="btn secondary">Close</button>
       </div>
    </div>

    <!-- Compare Version Selection Modal -->
    <div v-if="showCompareModal" class="modal-overlay">
       <div class="modal-content">
          <h3>Compare Versions - [{{ selectedManuscriptId }}]</h3>
          <div class="form-group">
             <label>Compare {{ compareSourceVersion?.version }} with:</label>
             <select v-model="compareTargetVersion" class="input-text">
                <option v-for="ver in templateHistory" :key="ver.version" :value="ver" :disabled="ver.version === compareSourceVersion?.version">
                   {{ ver.version }} ({{ ver.modifier }})
                </option>
             </select>
          </div>
          <div class="modal-footer">
             <button class="btn secondary" @click="showCompareModal = false">Cancel</button>
             <button class="btn primary" @click="executeCompare">Compare Now</button>
          </div>
       </div>
    </div>

    <!-- Split-Screen Compare View -->
    <div v-if="showCompareView" class="modal-overlay fullscreen">
       <div class="modal-content fullscreen-content">
          <div class="modal-header">
             <h3>Comparison: {{ compareSourceVersion?.version }} vs {{ compareTargetVersion?.version }}</h3>
             <button class="close-btn" @click="closeCompareView">×</button>
          </div>
          <div class="compare-container">
             <div class="compare-pane">
                <h4>{{ compareSourceVersion?.version }}</h4>
                <div class="compare-content">
                   <p>Dear <span class="diff-modified">Dr. Alice</span>,</p>
                   <p>We have reviewed your manuscript...</p>
                   <p class="diff-removed">Old content removed.</p>
                </div>
             </div>
             <div class="compare-pane">
                <h4>{{ compareTargetVersion?.version }}</h4>
                <div class="compare-content">
                   <p>Dear <span class="diff-modified">Prof. Bob</span>,</p>
                   <p>We have reviewed your manuscript...</p>
                   <p class="diff-added">New content added here.</p>
                </div>
             </div>
          </div>
          <div class="modal-footer">
             <button class="btn secondary" @click="closeCompareView">Close</button>
             <button class="btn primary" v-if="!isReadOnly" @click="handleExportComparison">Export Comparison Report</button>
          </div>
       </div>
    </div>

    <!-- Action Modals -->
    <div v-if="showActionModal" class="modal-overlay">
      <div class="modal-content large" v-if="currentAction === 'view_details'">
         <div class="modal-header">
           <h3>Decision Letter Details - [{{ currentLetter.subject }}]</h3>
           <button class="close-btn" @click="showActionModal = false">×</button>
         </div>
         <div class="tabs modal-tabs">
           <button :class="{ active: viewDetailsTab === 'content' }" @click="viewDetailsTab = 'content'">Letter Content</button>
           <button :class="{ active: viewDetailsTab === 'history' }" @click="viewDetailsTab = 'history'">Version History</button>
           <button :class="{ active: viewDetailsTab === 'delivery' }" @click="viewDetailsTab = 'delivery'">Delivery Log</button>
           <button :class="{ active: viewDetailsTab === 'notes' }" @click="viewDetailsTab = 'notes'">Internal Notes</button>
         </div>
         <div class="tab-content">
            <div v-if="viewDetailsTab === 'content'" class="letter-preview">
               <p>Dear {{ currentLetter.recipient }},</p>
               <p>This is the content of the decision letter...</p>
            </div>
            <div v-if="viewDetailsTab === 'history'">
               <ul class="timeline">
                  <li><strong>v1.0</strong> - Sent by Editor on {{ currentLetter.date }}</li>
               </ul>
            </div>
            <div v-if="viewDetailsTab === 'delivery'">
               <p><strong>Sent:</strong> {{ currentLetter.date }}</p>
               <p><strong>Recipient:</strong> {{ currentLetter.recipient }}</p>
               <p><strong>Status:</strong> {{ currentLetter.openStatus }}</p>
            </div>
            <div v-if="viewDetailsTab === 'notes'">
               <textarea placeholder="Add a note..." class="note-input"></textarea>
               <button class="btn primary-sm">Add Note</button>
            </div>
         </div>
         <div class="modal-footer">
            <button class="btn secondary" @click="handleExportPDF(currentLetter)">Export PDF</button>
            <button class="btn primary" v-if="canSendDecision" @click="handleResend(currentLetter)">Resend</button>
         </div>
      </div>

      <div class="modal-content" v-else>
         <h3>{{ currentAction === 'resend' ? 'Resend Decision Letter' : 
                currentAction === 'forward' ? 'Forward Decision Letter' :
                currentAction === 'add_note' ? 'Add Internal Note' :
                currentAction === 'approve' ? 'Approve Decision' :
                currentAction === 'reject' ? 'Reject Decision' :
                currentAction === 'assign_ae' ? 'Assign to Another AE' : 'Action' }}</h3>
         
         <!-- Resend Form -->
         <div v-if="currentAction === 'resend'">
            <div class="form-group">
               <label>Recipient</label>
               <input v-model="actionForms.resend.recipient" class="input-text">
            </div>
            <div class="form-group">
               <label>Subject</label>
               <input v-model="actionForms.resend.subject" class="input-text" disabled>
            </div>
            <div class="form-group">
               <label>Body</label>
               <textarea v-model="actionForms.resend.body" rows="5"></textarea>
            </div>
            <div class="form-group">
               <label>Postscript</label>
               <input v-model="actionForms.resend.postscript" class="input-text" placeholder="Ignore if received...">
            </div>
         </div>

         <!-- Forward Form -->
         <div v-if="currentAction === 'forward'">
            <div class="form-group">
               <label>Recipient</label>
               <select v-model="actionForms.forward.recipient" class="input-text">
                  <option value="editor1@journal.com">Editor 1</option>
                  <option value="reviewer1@uni.edu">Reviewer 1</option>
               </select>
            </div>
            <div class="form-group">
               <label>Postscript (Mandatory)</label>
               <textarea v-model="actionForms.forward.postscript" rows="3"></textarea>
            </div>
            <label><input type="checkbox" v-model="actionForms.forward.includeOriginal"> Include Original Email</label>
         </div>

         <!-- Add Note Form -->
         <div v-if="currentAction === 'add_note'">
            <div class="form-group">
               <label>Type</label>
               <select v-model="actionForms.addNote.type" class="input-text">
                  <option>Communication Record</option>
                  <option>To-Do</option>
                  <option>Special Instructions</option>
               </select>
            </div>
            <div class="form-group">
               <label>Content</label>
               <textarea v-model="actionForms.addNote.content" rows="4"></textarea>
            </div>
         </div>

         <!-- Approve Form -->
         <div v-if="currentAction === 'approve'">
            <div class="info-block">Preview: Dear Author...</div>
            <div class="form-group">
               <label>Approval Remarks</label>
               <textarea v-model="actionForms.approve.remarks" rows="3"></textarea>
            </div>
            <label><input type="checkbox" v-model="actionForms.approve.autoSend"> Auto-send to Author</label>
         </div>

         <!-- Reject Form -->
         <div v-if="currentAction === 'reject'">
            <div class="form-group">
               <label>Reason</label>
               <select v-model="actionForms.reject.reason" class="input-text">
                  <option>Content needs revision</option>
                  <option>Logic is not rigorous</option>
                  <option>Insufficient integration</option>
                  <option>Others</option>
               </select>
            </div>
            <div class="form-group" v-if="actionForms.reject.reason === 'Others'">
               <label>Explanation (≥20 chars)</label>
               <textarea v-model="actionForms.reject.detail" rows="3"></textarea>
            </div>
            <label><input type="checkbox" v-model="actionForms.reject.notifyDrafter"> Notify Original Drafter</label>
         </div>

         <!-- Assign AE Form -->
         <div v-if="currentAction === 'assign_ae'">
            <div class="form-group">
               <label>Target AE</label>
               <select v-model="actionForms.assignAE.targetAE" class="input-text">
                  <option>Dr. AE One</option>
                  <option>Prof. AE Two</option>
               </select>
            </div>
            <div class="form-group">
               <label>Remarks</label>
               <textarea v-model="actionForms.assignAE.remarks" rows="3"></textarea>
            </div>
         </div>

         <div class="modal-footer">
            <button class="btn secondary" @click="showActionModal = false">Cancel</button>
            <button class="btn primary" @click="handleConfirmAction">Confirm</button>
         </div>
      </div>
    </div>

    <!-- Sensitive Operation Verification -->
    <SensitiveOperationVerification
      :visible="showVerification"
      :action-type="verificationAction"
      :target="verificationTarget"
      @close="showVerification = false"
      @verify-success="handleVerificationSuccess"
    />

  </div>
</template>

<style scoped>
.editor-page {
  padding: 2rem;
  max-width: 1400px; /* Wider for 3 columns */
  margin: 60px auto 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.tabs { display: flex; gap: 1rem; }
.tab-btn { background: none; border: none; font-size: 1rem; cursor: pointer; padding: 0.5rem 1rem; color: #666; border-bottom: 2px solid transparent; }
.tab-btn.active { color: #3498db; border-bottom-color: #3498db; font-weight: bold; }

.decision-container {
  display: flex;
  gap: 1.5rem;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  min-height: 700px;
  align-items: stretch;
}

.sidebar {
  width: 280px;
  background: #f9f9f9;
  padding: 1rem;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}
.sidebar.comments-sidebar {
  border-right: none;
  border-left: 1px solid #eee;
}

.sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.icon-btn { background: #3498db; color: white; border: none; width: 24px; height: 24px; border-radius: 50%; cursor: pointer; }

.templates-sidebar ul { list-style: none; padding: 0; }
.templates-sidebar li { padding: 0.8rem; cursor: pointer; border-radius: 4px; margin-bottom: 0.5rem; background: white; border: 1px solid #eee; transition: all 0.2s; }
.templates-sidebar li:hover { border-color: #3498db; }
.templates-sidebar li.active { background: #e3f2fd; border-color: #3498db; color: #1565c0; font-weight: 500; }

.editor-area {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
}

.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #555; }
.ms-select { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; }

.editor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.status-tag { padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
.status-tag.draft { background: #e0e0e0; color: #555; }
.status-tag.pending { background: #fff3e0; color: #ef6c00; }
.status-tag.approved { background: #e8f5e9; color: #2e7d32; }
.status-tag.rejected { background: #ffebee; color: #c62828; }

textarea {
  width: 100%;
  flex: 1;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace; /* Monospace for editing feel */
  font-size: 0.95rem;
  line-height: 1.5;
  resize: none;
  margin-bottom: 0.5rem;
}

.status-bar { text-align: right; font-size: 0.8rem; color: #999; margin-bottom: 1rem; height: 1rem; }

.actions { display: flex; gap: 1rem; align-items: center; justify-content: flex-end; }
.btn { padding: 0.6rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
.btn.primary { background: #3498db; color: white; }
.btn.secondary { background: #ecf0f1; color: #2c3e50; }
.btn.danger { background: #e74c3c; color: white; }

.comment-list { overflow-y: auto; flex: 1; }
.comment-item { background: white; padding: 0.8rem; border: 1px solid #eee; border-radius: 4px; margin-bottom: 0.8rem; font-size: 0.9rem; }
.comment-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem; color: #555; }
.insert-btn { background: none; border: 1px solid #3498db; color: #3498db; border-radius: 3px; cursor: pointer; font-size: 0.75rem; padding: 2px 6px; }
.insert-btn:hover { background: #3498db; color: white; }

.sent-letters-container, .approval-queue-container {
  background: white; padding: 2rem; border-radius: 8px; min-height: 500px;
}
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }
.data-table th { background: #f8f9fa; color: #555; }
.btn-text { background: none; border: none; color: #3498db; cursor: pointer; margin-right: 0.5rem; }
.action-buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.approval-progress { display: flex; align-items: center; justify-content: center; margin-bottom: 2rem; }
.step { padding: 5px 10px; border-radius: 4px; background: #eee; color: #999; font-size: 0.9rem; }
.step.active { background: #fff3e0; color: #ef6c00; font-weight: bold; }
.step.completed { background: #e8f5e9; color: #2e7d32; }
.line { width: 50px; height: 2px; background: #eee; margin: 0 10px; }
.line.completed { background: #2e7d32; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 8px; width: 600px; max-height: 80vh; overflow-y: auto; }
.history-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
.history-table th, .history-table td { padding: 0.8rem; border-bottom: 1px solid #eee; text-align: left; }
.diff-view { background: #f9f9f9; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
.diff-added { background: #e8f5e9; color: #2e7d32; }
.diff-removed { background: #ffebee; color: #c62828; text-decoration: line-through; }

.dropdown-menu { position: absolute; background: white; border: 1px solid #eee; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 4px; z-index: 10; right: 0; min-width: 100px; }
.dropdown-menu a { display: block; padding: 0.5rem 1rem; color: #333; text-decoration: none; cursor: pointer; }
.dropdown-menu a:hover { background: #f5f5f5; }
.tpl-item-content { display: flex; justify-content: space-between; align-items: center; position: relative; }
.dots-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #999; }
.tpl-meta { font-size: 0.75rem; color: #999; margin-top: 4px; }
.template-filters { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.filter-sm { width: 48%; padding: 4px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.8rem; }
.comment-actions { display: flex; gap: 4px; }
.action-icon-btn { background: #eee; border: none; border-radius: 3px; cursor: pointer; font-size: 0.7rem; padding: 2px 5px; color: #666; }
.action-icon-btn.danger { color: #e74c3c; }
.highlighted { background-color: #fff9c4; }

/* Approval Queue Styles */
.approval-queue-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  min-height: 600px;
}

.approval-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.approval-table th,
.approval-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.approval-table th {
  background: #f8f9fa;
  color: #555;
  font-weight: 600;
}

.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; }
.modal-tabs { margin-bottom: 1rem; border-bottom: 1px solid #eee; }
.modal-tabs button { padding: 0.5rem 1rem; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; }
.modal-tabs button.active { border-bottom-color: #3498db; color: #3498db; font-weight: bold; }
.tab-content { min-height: 200px; padding: 1rem 0; }
.modal-footer { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; border-top: 1px solid #eee; padding-top: 1rem; }
.input-text { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
.info-block { background: #f9f9f9; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; border: 1px dashed #ddd; }
.note-input { width: 100%; height: 100px; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 0.5rem; resize: none; }
.modal-overlay.fullscreen { align-items: stretch; padding: 2rem; }
.modal-content.fullscreen-content { width: 100%; height: 100%; max-height: none; display: flex; flex-direction: column; }
.compare-container { display: flex; flex: 1; gap: 1rem; overflow: hidden; }
.compare-pane { flex: 1; border: 1px solid #eee; padding: 1rem; overflow-y: auto; background: #f9f9f9; }
.compare-content { font-family: monospace; white-space: pre-wrap; }
.diff-modified { background-color: #fff9c4; }

.ms-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ms-id {
  font-size: 0.8rem;
  color: #999;
  font-weight: normal;
}

.btn.primary-sm,
.btn.danger-sm,
.btn.secondary-sm {
  padding: 4px 10px;
  font-size: 0.8rem;
  margin-right: 5px;
}

.btn.primary-sm {
  background: #3498db;
  color: white;
}

.btn.danger-sm {
  background: #e74c3c;
  color: white;
}

/* Toggle Switch */
.switch { position: relative; display: inline-block; width: 34px; height: 20px; margin-right: 8px; vertical-align: middle; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; }
input:checked + .slider { background-color: #2196F3; }
input:checked + .slider:before { transform: translateX(14px); }
.slider.round { border-radius: 20px; }
.slider.round:before { border-radius: 50%; }

.header-controls { display: flex; align-items: center; gap: 1rem; }
.edit-mode-toggle { display: flex; align-items: center; font-size: 0.9rem; color: #555; }
textarea.read-only { background-color: #f9f9f9; color: #555; cursor: not-allowed; }

.btn.primary-sm { background: #3498db; color: white; padding: 0.6rem 1.2rem; }
.btn.danger-sm { background: #e74c3c; color: white; padding: 0.6rem 1.2rem; }
</style>