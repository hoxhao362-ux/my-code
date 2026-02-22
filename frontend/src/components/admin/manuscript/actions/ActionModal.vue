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
const conflictCheckResult = ref('正在检查...')
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
    subject: '提醒：稿件评审截止',
    content: '尊敬的 [Name] 教授/博士：...'
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
    subject: '提醒：稿件评审截止',
    content: '尊敬的 [Name] 教授/博士：...'
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
  { id: 'ae1', name: '李明 教授', field: '肿瘤学' },
  { id: 'ae2', name: '王强 博士', field: '心脏病学' }
])
const reviewers = ref([
  { id: 'r1', name: '审稿人 A', institution: '清华大学', deadline: '2026-03-01' },
  { id: 'r2', name: '审稿人 B', institution: '北京大学', deadline: '2026-02-28' }
])
const historyLogs = ref([
  { operator: '编辑', type: '初审', time: '2026-02-01 10:00', result: '通过', remarks: '质量良好' },
  { operator: '作者', type: '投稿', time: '2026-01-30 14:00', result: '已提交', remarks: '-' }
])
// Mock Pending Manuscripts for Reviewer
const pendingManuscripts = ref([
  { id: 'MS-001', title: '深度学习在X射线中的应用', status: '评审中', due: '2026-02-20' },
  { id: 'MS-005', title: '癌症研究更新', status: '待接受', due: '2026-02-25' }
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
  conflictCheckResult.value = '正在检查...'
  batchConflictResults.value = {}
  
  // Simulate Conflict Check for Invite
  if (props.actionType === 'invite_reviewer') {
    let content = EMAIL_TEMPLATES.reviewerInvitation.content
    content = content.replace('[Manuscript ID]', props.manuscript?.id || 'MS-2026-001')
                     .replace('[Manuscript Title]', props.manuscript?.title || '无标题')
                     .replace('[Submission Date]', '2026-02-10')
                     .replace('[Due Date]', forms.inviteReviewer.deadline || '2026-03-01') // Use form deadline if set, or default
                     .replace('[Reviewer Full Name]', props.reviewer?.name || 'Reviewer')
                     .replace('[Relevant Field, e.g., cardiovascular research]', props.reviewer?.reason || '您的专业领域') // Use reason or field
    
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
      .replace('[Manuscript Title]', props.manuscript?.title || '无标题')

    setTimeout(() => {
      conflictCheckResult.value = '未发现冲突 (可以邀请)'
    }, 1500)
  }

  // Batch Invite Init
  if (props.actionType === 'batch_invite') {
    forms.batchInvite.selectedReviewers = props.reviewers.map(r => r.id)
    props.reviewers.forEach(r => {
      batchConflictResults.value[r.id] = '正在检查...'
      setTimeout(() => {
        // Mock random conflict
        batchConflictResults.value[r.id] = Math.random() > 0.8 ? '发现冲突' : '安全'
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
                     .replace('[Manuscript Title]', props.manuscript?.title || '无标题')
                     .replace('[Submission Time]', '2026-02-10 10:00')
                     .replace('[Corresponding Author Full Name]', 'Dr. Author')
                     .replace('[Date]', new Date().toLocaleDateString())

    // Generate Dynamic Reviewer List
    let reviewersHtml = ''
    props.reviewers.forEach((r, index) => {
      const decisionColor = r.status === 'Rejected' ? '#999' : '#C93737' // Gray for Reject, Red for Approved (per template)
      const decisionText = r.status === 'Rejected' ? '已拒绝' : '已通过'
      
      let detailLine = ''
      if (r.status === 'Rejected') {
        detailLine = `<p style="margin: 0; font-size: 14px; color: #555;">拒绝原因：${r.rejectionReason || '利益冲突'}</p>`
      } else {
        const inviteStatus = r.status === 'Invited' ? '邀请已发送' : '邀请即将发送'
        detailLine = `<p style="margin: 0; font-size: 14px; color: #555;">邀请状态：${inviteStatus}</p>`
      }

      // Add border for all except last one (logic can be simple: always add margin bottom)
      const borderStyle = index < props.reviewers.length - 1 ? 'border-bottom: 1px dashed #ddd; padding-bottom: 10px; margin-bottom: 15px;' : 'margin-bottom: 5px;'

      reviewersHtml += `
        <div style="${borderStyle}">
          <p style="margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">${r.name}</p>
          <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;">所属机构：${r.affiliation || 'N/A'}</p>
          <p style="margin: 0 0 5px 0; font-size: 14px; color: ${decisionColor}; font-weight: bold;">编辑决定：${decisionText}</p>
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
    const containerStart = '审稿人推荐结果</p>'
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
      .replace('[Manuscript Title]', props.manuscript?.title || '无标题')
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
    format_check: '格式检查',
    desk_reject: '直接拒稿 (Desk Reject)',
    assign_editor: '分配编辑',
    request_revision: '要求修回',
    withdraw: '撤稿',
    add_note: '添加内部备注',
    view_history: '稿件历史',
    remind_reviewer: '提醒审稿人',
    replace_reviewer: '更换审稿人',
    extend_deadline: '延长审稿截止日期',
    request_further_review: '要求进一步审稿',
    approve_decision: '批准决定',
    generate_decision_letter: '生成决定信',
    send_to_production: '发送至出版',
    archive: '归档稿件',
    invite_reviewer: '邀请审稿人',
    cancel_invitation: '取消邀请',
    batch_invite: '批量邀请审稿人',
    batch_remind: '批量提醒审稿人',
    batch_mark_active: '批量标记为活跃',
    batch_mark_inactive: '批量标记为非活跃',
    notify_writer_recommendation: '通知作者推荐结果'
  }
  let title = map[props.actionType] || '操作'
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
             <p><strong>编号：</strong> {{ manuscript.id }} | <strong>标题：</strong> {{ manuscript.title }}</p>
           </div>
           <div class="check-list">
             <label><input type="checkbox" v-model="forms.formatCheck.docFormat"> 文档格式 (Word/PDF 符合要求)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.figures"> 图片/表格清晰度 (≥300dpi)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.references"> 参考文献格式</label>
             <label><input type="checkbox" v-model="forms.formatCheck.abstract"> 摘要字数 (≤250 words)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.keywords"> 关键词数量 (3-6 个)</label>
             <label><input type="checkbox" v-model="forms.formatCheck.ethics"> 伦理声明</label>
           </div>
           <div class="form-group">
             <label>备注 (如果不合格必填)</label>
             <textarea v-model="forms.formatCheck.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 2. Desk Reject -->
        <div v-if="actionType === 'desk_reject'">
          <div class="warning-banner">直接拒稿仅适用于明显超出范围或学术质量极低的稿件</div>
          <div class="form-group">
            <label class="required">拒稿原因</label>
            <select v-model="forms.deskReject.reason" class="select-input">
              <option value="" disabled>请选择原因</option>
              <option value="Out of Scope">超出范围</option>
              <option value="Insufficient Originality">创新性不足</option>
              <option value="Methodological Flaws">方法学缺陷</option>
              <option value="Severe Format Errors">严重格式错误</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">详细原因 (≥50 字)</label>
            <textarea v-model="forms.deskReject.detail" rows="6" class="textarea-input"></textarea>
          </div>
        </div>

        <!-- 3. Assign to Editor -->
        <div v-if="actionType === 'assign_editor'">
           <div class="form-group">
             <label class="required">副编辑 (AE) 列表</label>
             <select v-model="forms.assignEditor.aeId" class="select-input">
               <option value="" disabled>选择副编辑</option>
               <option v-for="ae in aeList" :key="ae.id" :value="ae.id">{{ ae.name }} - {{ ae.field }}</option>
             </select>
           </div>
           <div class="form-group">
             <label>分配备注</label>
             <textarea v-model="forms.assignEditor.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 4. Request Revision -->
        <div v-if="actionType === 'request_revision'">
           <div class="form-group">
             <label class="required">修回类型</label>
             <select v-model="forms.requestRevision.type" class="select-input">
               <option value="Format Revision">格式修改</option>
               <option value="Content Revision">内容修改</option>
               <option value="Attachment Revision">附件修改</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">内容</label>
             <textarea v-model="forms.requestRevision.content" rows="6" class="textarea-input" placeholder="富文本编辑器占位符..."></textarea>
           </div>
           <div class="form-group">
             <label class="required">截止日期</label>
             <input type="date" v-model="forms.requestRevision.deadline" class="input-text">
           </div>
        </div>

        <!-- 5. Withdraw Manuscript -->
        <div v-if="actionType === 'withdraw'">
           <div class="warning-banner red">撤稿将终止流程且无法恢复，请谨慎操作</div>
           <div class="form-group">
             <label class="required">撤稿原因</label>
             <select v-model="forms.withdraw.reason" class="select-input">
               <option value="Author's Initiative">作者主动撤稿</option>
               <option value="Academic Misconduct">学术不端</option>
               <option value="Duplicate Submission">一稿多投</option>
               <option value="Others">其他</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">详细说明</label>
             <textarea v-model="forms.withdraw.detail" rows="4" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 6. Add Note -->
        <div v-if="actionType === 'add_note'">
           <div class="form-group">
             <label class="required">备注类型</label>
             <select v-model="forms.addNote.type" class="select-input">
               <option value="Communication Record">沟通记录</option>
               <option value="To-Do">待办事项</option>
               <option value="Special Instructions">特殊说明</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">内容</label>
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
               {{ r.name }} (截止: {{ r.deadline }})
             </label>
          </div>
          <div v-if="reviewer" class="pending-manuscripts">
             <h4>待处理稿件</h4>
             <ul>
               <li v-for="ms in pendingManuscripts" :key="ms.id">
                 {{ ms.id }} - {{ ms.title }} (截止: {{ ms.due }})
               </li>
             </ul>
          </div>
          <div class="form-group">
            <label>邮件主题</label>
            <input v-model="forms.remindReviewer.subject" class="input-text">
          </div>
          <div class="form-group">
            <label>邮件内容</label>
            <textarea v-model="forms.remindReviewer.content" rows="4" class="textarea-input"></textarea>
          </div>
        </div>
        
        <!-- 9. Replace Reviewer -->
        <div v-if="actionType === 'replace_reviewer'">
          <div v-if="manuscript" class="form-group">
            <label class="required">原审稿人</label>
            <select v-model="forms.replaceReviewer.originalReviewerId" class="select-input">
              <option v-for="r in reviewers" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div v-if="reviewer" class="info-block">
             正在更换审稿人：<strong>{{ reviewer.name }}</strong>
             <div class="pending-list">
               影响 {{ pendingManuscripts.length }} 篇待处理稿件
             </div>
          </div>
          <div class="form-group">
            <label class="required">原因</label>
            <select v-model="forms.replaceReviewer.reason" class="select-input">
              <option value="Rejected Review">拒绝审稿</option>
              <option value="Unreachable">无法联系</option>
              <option value="Conflict of Interest">利益冲突</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">新审稿人 (模拟选择)</label>
            <select v-model="forms.replaceReviewer.newReviewerId" class="select-input">
               <option value="new_rev_1">推荐审稿人 1 (相同领域)</option>
               <option value="new_rev_2">推荐审稿人 2</option>
            </select>
          </div>
          <div class="info-block">系统将自动生成取消和新邀请邮件。</div>
        </div>

        <!-- 16. Invite Reviewer -->
        <div v-if="actionType === 'invite_reviewer'">
           <div class="info-block">
             <p><strong>审稿人：</strong> {{ reviewer?.name }} | <strong>邮箱：</strong> {{ reviewer?.email }}</p>
             <p><strong>领域：</strong> {{ reviewer?.field }} | <strong>指标：</strong> {{ reviewer?.avgTurnaround }} / {{ reviewer?.completedReviews }} 次审稿</p>
           </div>
           <div class="info-block" :class="conflictCheckResult.includes('Safe') || conflictCheckResult.includes('可以邀请') ? 'green' : 'orange'">
             <strong>冲突检查：</strong> {{ conflictCheckResult }}
           </div>
           <div class="form-group">
             <label class="required">截止日期</label>
             <input type="date" v-model="forms.inviteReviewer.deadline" class="input-text">
           </div>
           <div class="form-group">
             <label class="required">邮件主题</label>
             <input v-model="forms.inviteReviewer.subject" class="input-text">
           </div>
           <div class="form-group">
             <label class="required">邮件内容</label>
             <textarea v-model="forms.inviteReviewer.content" rows="6" class="textarea-input"></textarea>
           </div>
        </div>

        <!-- 17. Cancel Invitation -->
         <div v-if="actionType === 'cancel_invitation'">
            <div class="warning-banner red">取消邀请后，系统将自动通知审稿人</div>
            <div class="form-group">
              <label class="required">原因</label>
              <select v-model="forms.cancelInvitation.reason" class="select-input">
                <option value="Mistaken Invitation">误操作邀请</option>
                <option value="Reviewer Request">审稿人要求</option>
                <option value="Others">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>备注</label>
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
                  <span class="conflict-tag" :class="batchConflictResults[r.id] === '安全' || batchConflictResults[r.id] === 'Safe' ? 'green' : 'orange'">
                     {{ batchConflictResults[r.id] }}
                  </span>
               </div>
            </div>
            <div class="form-group">
              <label class="required">截止日期</label>
              <input type="date" v-model="forms.batchInvite.deadline" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">邮件主题</label>
              <input v-model="forms.batchInvite.subject" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">邮件内容</label>
              <textarea v-model="forms.batchInvite.content" rows="6" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 19. Batch Remind -->
         <div v-if="actionType === 'batch_remind'">
            <div class="info-block">
               选择要提醒的稿件 (模拟列表):
            </div>
            <div class="manuscript-select-list">
               <!-- Mocking manuscript list based on reviewers -->
               <div v-for="r in reviewers" :key="r.id">
                  <strong>{{ r.name }}</strong>
                  <div v-for="i in r.pendingCount" :key="i" class="ms-item">
                     <label>
                        <!-- Mock MS ID generation -->
                        <input type="checkbox" :value="`MS-${r.id}-${i}`" v-model="forms.batchRemind.selectedManuscripts">
                        MS-2026-{{ r.id }}0{{ i }} (待处理)
                     </label>
                  </div>
               </div>
            </div>
            <div class="form-group">
              <label class="required">邮件主题</label>
              <input v-model="forms.batchRemind.subject" class="input-text">
            </div>
            <div class="form-group">
              <label class="required">邮件内容</label>
              <textarea v-model="forms.batchRemind.content" rows="6" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 20. Batch Mark Active -->
         <div v-if="actionType === 'batch_mark_active'">
            <div class="info-block">
               确认将 {{ reviewers.length }} 位审稿人标记为 <strong>活跃</strong> 状态？
            </div>
            <div class="reviewer-names-list">
               {{ reviewers.map(r => r.name).join(', ') }}
            </div>
            <div class="form-group">
               <label>可选备注</label>
               <textarea v-model="forms.batchMarkActive.remarks" rows="3" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 21. Batch Mark Inactive -->
         <div v-if="actionType === 'batch_mark_inactive'">
            <div class="info-block">
               确认将 {{ reviewers.length }} 位审稿人标记为 <strong>非活跃</strong> 状态？
            </div>
            <div class="reviewer-names-list">
               {{ reviewers.map(r => r.name).join(', ') }}
            </div>
            <div class="form-group">
              <label class="required">原因</label>
              <select v-model="forms.batchMarkInactive.reason" class="select-input">
                <option value="Long-term Rejection of Review">长期拒绝审稿</option>
                <option value="Unreachable">无法联系</option>
                <option value="Academic Misconduct">学术不端</option>
                <option value="Others">其他</option>
              </select>
            </div>
            <div class="form-group" v-if="forms.batchMarkInactive.reason === 'Others'">
              <label class="required">详细说明 (≥20 字)</label>
              <textarea v-model="forms.batchMarkInactive.othersDetail" rows="3" class="textarea-input"></textarea>
            </div>
         </div>

         <!-- 22. Notify Author Recommendation Results -->
         <div v-if="actionType === 'notify_writer_recommendation'">
            <div class="info-block">
               <p>通知作者关于其推荐审稿人的决定。</p>
            </div>
            
            <div class="form-group">
               <label class="required">通知渠道</label>
               <div class="check-list horizontal">
                  <label><input type="checkbox" v-model="forms.notifyWriterRecommendation.channels" value="email"> 邮件</label>
                  <label><input type="checkbox" v-model="forms.notifyWriterRecommendation.channels" value="system_message"> 站内信</label>
               </div>
            </div>

            <div class="form-group">
              <label class="required">邮件主题</label>
              <input v-model="forms.notifyWriterRecommendation.subject" class="input-text">
            </div>
            
            <div class="form-group">
               <label>邮件内容预览 (自动生成)</label>
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
               <label>附加说明 (可选)</label>
               <textarea v-model="forms.notifyWriterRecommendation.additionalNote" rows="3" class="textarea-input" placeholder="输入给作者的附加说明..."></textarea>
            </div>
         </div>
        
        <!-- 10. Extend Deadline -->
        <div v-if="actionType === 'extend_deadline'">
           <div class="form-group">
            <label class="required">审稿人</label>
            <select v-model="forms.extendDeadline.reviewerId" class="select-input">
              <option v-for="r in reviewers" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="required">新截止日期</label>
            <input type="date" v-model="forms.extendDeadline.newDeadline" class="input-text">
          </div>
        </div>
        
        <!-- 11. Request Further Review -->
        <div v-if="actionType === 'request_further_review'">
           <div class="form-group">
             <label class="required">原因</label>
             <select v-model="forms.requestFurtherReview.reason" class="select-input">
               <option value="Conflicting Reviews">审稿意见冲突</option>
               <option value="Insufficient Comments">意见不充分</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">说明</label>
             <textarea v-model="forms.requestFurtherReview.detail" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- Ready for Decision -->
        <!-- 12. Approve Decision -->
        <div v-if="actionType === 'approve_decision'">
           <div class="info-block">副编辑推荐：接受 (模拟)</div>
           <div class="form-group">
             <label class="required">批准结果</label>
             <select v-model="forms.approveDecision.result" class="select-input">
               <option value="Approve">批准</option>
               <option value="Reject & Revise">拒绝并要求修改</option>
             </select>
           </div>
           <div class="form-group">
             <label class="required">备注</label>
             <textarea v-model="forms.approveDecision.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- Decision Made -->
        <!-- 13. Generate Decision Letter -->
        <div v-if="actionType === 'generate_decision_letter'">
           <div class="form-group">
             <label class="required">决定信内容</label>
             <textarea v-model="forms.generateDecisionLetter.content" rows="10" class="textarea-input" placeholder="尊敬的作者..."></textarea>
           </div>
        </div>
        
        <!-- 14. Send to Production -->
        <div v-if="actionType === 'send_to_production'">
           <div class="form-group">
             <label class="required">优先级</label>
             <select v-model="forms.sendToProduction.priority" class="select-input">
               <option value="Normal">普通</option>
               <option value="Urgent">紧急</option>
             </select>
           </div>
           <div class="form-group">
             <label>备注</label>
             <textarea v-model="forms.sendToProduction.remarks" rows="3" class="textarea-input"></textarea>
           </div>
        </div>
        
        <!-- 15. Archive -->
        <div v-if="actionType === 'archive'">
           <div class="warning-banner red">归档稿件将被移至历史库，流程信息将无法修改</div>
           <div class="form-group">
             <label class="required">归档类型</label>
             <select v-model="forms.archive.type" class="select-input">
               <option value="Accepted Archive">已接受归档</option>
               <option value="Rejected Archive">已拒稿归档</option>
             </select>
           </div>
        </div>

      </div>

      <footer class="modal-footer">
        <button v-if="actionType !== 'view_history'" class="btn btn-cancel" @click="$emit('close')">取消</button>
        <button v-else class="btn btn-primary" @click="$emit('close')">关闭</button>
        
        <button 
          v-if="actionType !== 'view_history'" 
          class="btn btn-primary" 
          :disabled="!isFormValid || isSubmitting"
          @click="handleSubmit"
        >
          确认
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
</style>
