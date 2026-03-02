<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../../composables/useI18n'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import ActionModal from '../../components/admin/manuscript/actions/ActionModal.vue'
import SensitiveOperationVerification from '../../components/SensitiveOperationVerification.vue'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const user = computed(() => userStore.submissionUser || userStore.user)

// State
const filter = ref({
  field: '',
  status: '',
  performance: ''
})
const selectedReviewers = ref([])
const showActionModal = ref(false)
const currentActionType = ref('')
const currentReviewer = ref(null)

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

// Dropdown state
const showBatchDropdown = ref(false)
const showActionDropdowns = ref({})

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  // 检查点击目标是否在下拉菜单内部
  const isDropdownClick = event.target.closest('.dropdown')
  const isActionDropdownClick = event.target.closest('.dropdown-action')
  
  // 如果点击的不是下拉菜单内部，则关闭所有下拉菜单
  if (!isDropdownClick && !isActionDropdownClick) {
    showBatchDropdown.value = false
    Object.keys(showActionDropdowns.value).forEach(key => {
      showActionDropdowns.value[key] = false
    })
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const toggleBatchDropdown = (event) => {
  // 阻止事件冒泡，避免触发handleClickOutside
  if (event) {
    event.stopPropagation()
  }
  showBatchDropdown.value = !showBatchDropdown.value
}

const toggleActionDropdown = (event, id) => {
  // 阻止事件冒泡，避免触发handleClickOutside
  if (event) {
    event.stopPropagation()
  }
  showActionDropdowns.value[id] = !showActionDropdowns.value[id]
}

// Mock Reviewers Data
const reviewers = ref([
  { 
    id: 1, 
    name: 'Dr. Reviewer One', 
    email: 'rev1@example.com', 
    field: 'Medical Imaging', 
    status: 'Active', 
    pendingCount: 2,
    avgTurnaround: '5 days',
    rejectionRate: '10%',
    completedReviews: 15
  },
  { 
    id: 2, 
    name: 'Prof. Reviewer Two', 
    email: 'rev2@example.com', 
    field: 'Drug Delivery', 
    status: 'Active', 
    pendingCount: 0,
    avgTurnaround: '8 days',
    rejectionRate: '25%',
    completedReviews: 42
  },
  { 
    id: 3, 
    name: 'Dr. Reviewer Three', 
    email: 'rev3@example.com', 
    field: 'Medical Imaging', 
    status: 'Inactive', 
    pendingCount: 0,
    avgTurnaround: '-',
    rejectionRate: '-',
    completedReviews: 0
  },
  { 
    id: 4, 
    name: 'Dr. Reviewer Four', 
    email: 'rev4@example.com', 
    field: 'Clinical Research', 
    status: 'Active', 
    pendingCount: 1,
    avgTurnaround: '12 days',
    rejectionRate: '5%',
    completedReviews: 8
  }
])

// Permissions
const canManageAll = computed(() => user.value?.role === 'editor' || user.value?.role === 'admin')
const canManageOwnField = computed(() => user.value?.role === 'associate_editor')
const isReadOnly = computed(() => ['editorial_assistant', 'advisory_editor'].includes(user.value?.role))

// Filter Logic
const filteredReviewers = computed(() => {
  let list = reviewers.value

  // Role-based Field Filter
  if (canManageOwnField.value) {
    // Mock: AE only sees their own field (e.g., Medical Imaging)
    // In real app, check against user.value.field
    // list = list.filter(r => r.field === user.value.field)
  }

  // UI Filters
  if (filter.value.field) {
    list = list.filter(r => r.field === filter.value.field)
  }
  if (filter.value.status) {
    list = list.filter(r => r.status === filter.value.status)
  }
  if (filter.value.performance) {
    if (filter.value.performance === 'high') {
       list = list.filter(r => parseInt(r.completedReviews) > 10)
    }
  }

  return list
})

const uniqueFields = computed(() => [...new Set(reviewers.value.map(r => r.field))])

// Actions
const openModal = (type, reviewer = null) => {
  if (isReadOnly.value && type !== 'view_history') return

  // Permission Check for AE
  if (canManageOwnField.value && reviewer) {
     // Check if reviewer is in AE's field (Mock check)
     // if (reviewer.field !== user.value.field) { alert("Access Denied"); return; }
  }

  currentActionType.value = type
  currentReviewer.value = reviewer
  showActionModal.value = true
}

const handleBatchAction = (type) => {
  if (selectedReviewers.value.length === 0) return
  if (!canManageAll.value) return // AE cannot batch operate? Prompt says: "AE: Not visible, no operation permission" for Batch Buttons.

  const selectedReviewerObjects = reviewers.value.filter(r => selectedReviewers.value.includes(r.id))

  const proceed = () => {
    if (type === 'invite') {
      currentActionType.value = 'batch_invite'
    } else if (type === 'remind') {
      const pendingReviewers = selectedReviewerObjects.filter(r => r.pendingCount > 0)
      if (pendingReviewers.length === 0) {
        toastStore.add({ message: t('editor.reviewers.alerts.noPending'), type: 'warning' })
        return
      }
      if (pendingReviewers.length < selectedReviewerObjects.length) {
      }
      currentActionType.value = 'batch_remind'
    } else if (type === 'mark_active') {
      const inactiveReviewers = selectedReviewerObjects.filter(r => r.status !== 'Active')
      if (inactiveReviewers.length === 0) {
        toastStore.add({ message: t('editor.reviewers.alerts.alreadyActive'), type: 'info' })
        return
      }
      currentActionType.value = 'batch_mark_active'
    } else if (type === 'mark_inactive') {
      const activeReviewers = selectedReviewerObjects.filter(r => r.status === 'Active')
      if (activeReviewers.length === 0) {
        toastStore.add({ message: t('editor.reviewers.alerts.alreadyInactive'), type: 'info' })
        return
      }
      currentActionType.value = 'batch_mark_inactive'
    }
    
    currentReviewer.value = selectedReviewerObjects
    showActionModal.value = true
  }

  if (type === 'mark_inactive') {
    verificationAction.value = t('editor.reviewers.batch.markInactive')
    verificationTarget.value = `${selectedReviewerObjects.length} ${t('editor.reviewers.title').split(' ')[0]}`
    pendingCallback.value = proceed
    showVerification.value = true
  } else {
    proceed()
  }
}

const handleModalSubmit = ({ type, data }) => {
  console.log('Action Submitted:', type, data)
  if (type === 'cancel_invitation' && currentReviewer.value) {
     toastStore.add({ message: t('editor.reviewers.alerts.invitationCancelled', { name: currentReviewer.value.name }), type: 'success' })
  } else if (type === 'invite_reviewer') {
     toastStore.add({ message: t('editor.reviewers.alerts.invitationSent', { name: currentReviewer.value.name }), type: 'success' })
  } else if (type === 'replace_reviewer') {
     toastStore.add({ message: t('editor.reviewers.alerts.replaced', { name: currentReviewer.value.name }), type: 'success' })
  } else if (type === 'batch_mark_active') {
    selectedReviewers.value.forEach(id => {
       const r = reviewers.value.find(rv => rv.id === id)
       if (r) r.status = 'Active'
    })
    toastStore.add({ message: t('editor.reviewers.alerts.batchActive'), type: 'success' })
    selectedReviewers.value = []
  } else if (type === 'batch_mark_inactive') {
    selectedReviewers.value.forEach(id => {
       const r = reviewers.value.find(rv => rv.id === id)
       if (r) r.status = 'Inactive'
    })
    toastStore.add({ message: t('editor.reviewers.alerts.batchInactive'), type: 'success' })
    selectedReviewers.value = []
  } else if (type === 'batch_invite') {
    toastStore.add({ message: t('editor.reviewers.alerts.batchInvited'), type: 'success' })
    selectedReviewers.value = []
  } else if (type === 'batch_remind') {
    toastStore.add({ message: t('editor.reviewers.alerts.batchReminded'), type: 'success' })
    selectedReviewers.value = []
  }
}

const toggleSelection = (id) => {
  if (selectedReviewers.value.includes(id)) {
    selectedReviewers.value = selectedReviewers.value.filter(i => i !== id)
  } else {
    selectedReviewers.value.push(id)
  }
}

const selectAll = (e) => {
  if (e.target.checked) {
    selectedReviewers.value = filteredReviewers.value.map(r => r.id)
  } else {
    selectedReviewers.value = []
  }
}

</script>

<template>
  <div class="reviewer-page">
    <div class="page-header">
      <h2>{{ t('editor.reviewers.title') }}</h2>
      <div class="role-badge">{{ t('editor.reviewers.currentRole') }}: {{ user?.role }}</div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filters">
        <select v-model="filter.field" class="filter-select" :disabled="isReadOnly || canManageOwnField">
          <option value="">{{ t('editor.reviewers.filter.allFields') }}</option>
          <option v-for="f in uniqueFields" :key="f" :value="f">{{ f }}</option>
        </select>
        <select v-model="filter.status" class="filter-select" :disabled="isReadOnly">
          <option value="">{{ t('editor.reviewers.filter.allStatus') }}</option>
          <option value="Active">{{ t('editor.reviewers.filter.active') }}</option>
          <option value="Inactive">{{ t('editor.reviewers.filter.inactive') }}</option>
        </select>
        <select v-model="filter.performance" class="filter-select" :disabled="isReadOnly">
           <option value="">{{ t('editor.reviewers.filter.performance') }}</option>
           <option value="high">{{ t('editor.reviewers.filter.highCompletion') }}</option>
        </select>
      </div>

      <!-- Batch Operations (Editor Only) -->
      <div v-if="canManageAll" class="batch-actions">
        <div class="dropdown">
          <button class="batch-btn" @click="toggleBatchDropdown($event)">{{ t('editor.reviewers.batch.operations') }} ▼</button>
          <div class="dropdown-content" v-if="showBatchDropdown">
            <a @click="handleBatchAction('invite'); showBatchDropdown = false">{{ t('editor.reviewers.batch.invite') }}</a>
            <a @click="handleBatchAction('remind'); showBatchDropdown = false">{{ t('editor.reviewers.batch.remind') }}</a>
            <a @click="handleBatchAction('mark_active'); showBatchDropdown = false">{{ t('editor.reviewers.batch.markActive') }}</a>
            <a @click="handleBatchAction('mark_inactive'); showBatchDropdown = false">{{ t('editor.reviewers.batch.markInactive') }}</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Reviewer List -->
    <div class="table-container">
      <SkeletonLoader :loading="isLoading" :count="5" height="60px" gap="2px">
        <table class="reviewer-table">
          <thead>
            <tr>
              <th v-if="canManageAll">
                <input 
                  type="checkbox" 
                  :checked="filteredReviewers.length > 0 && selectedReviewers.length === filteredReviewers.length"
                  @change="selectAll"
                >
              </th>
              <th>{{ t('editor.reviewers.columns.nameEmail') }}</th>
              <th>{{ t('editor.reviewers.columns.field') }}</th>
              <th>{{ t('editor.reviewers.columns.metrics') }}</th>
              <th>{{ t('editor.reviewers.columns.status') }}</th>
              <th>{{ t('editor.reviewers.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rev in filteredReviewers" :key="rev.id">
              <td v-if="canManageAll">
                <input type="checkbox" :checked="selectedReviewers.includes(rev.id)" @change="toggleSelection(rev.id)">
              </td>
              <td>
                <div class="rev-name">{{ rev.name }}</div>
                <div class="rev-email">{{ rev.email }}</div>
              </td>
              <td><span class="tag field">{{ rev.field }}</span></td>
              <td>
                <div class="metrics">
                  <span :title="t('editor.reviewers.metrics.completed')">✅ {{ rev.completedReviews }}</span>
                  <span :title="t('editor.reviewers.metrics.turnaround')">⏱️ {{ rev.avgTurnaround }}</span>
                  <span :title="t('editor.reviewers.metrics.rejectionRate')">🚫 {{ rev.rejectionRate }}</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="rev.status.toLowerCase()">{{ rev.status }}</span>
              </td>
              <td class="actions-cell">
                <!-- EA/AE View Only -->
                <template v-if="isReadOnly">
                   <button class="btn-link" @click="openModal('view_history', rev)">{{ t('editor.reviewers.actions.viewHistory') }}</button>
                </template>

                <!-- Editor/AE Actions -->
                <template v-else>
                  <div class="btn-group">
                     <button class="btn-primary-sm" @click="openModal('invite_reviewer', rev)">{{ t('editor.reviewers.actions.invite') }}</button>
                     <button v-if="rev.pendingCount > 0" class="btn-warning-sm" @click="openModal('remind_reviewer', rev)">{{ t('editor.reviewers.actions.remind') }}</button>
                     <button v-if="rev.pendingCount > 0" class="btn-danger-sm" @click="openModal('replace_reviewer', rev)">{{ t('editor.reviewers.actions.replace') }}</button>
                     <button class="btn-text" @click="openModal('cancel_invitation', rev)">{{ t('editor.reviewers.actions.cancel') }}</button>
                     <div class="dropdown-action">
                        <span class="dots" @click="toggleActionDropdown($event, rev.id)">•••</span>
                        <div class="dropdown-menu" v-if="showActionDropdowns[rev.id]">
                           <a @click="openModal('add_note', rev); showActionDropdowns[rev.id] = false">{{ t('editor.reviewers.actions.addNote') }}</a>
                           <a @click="openModal('view_history', rev); showActionDropdowns[rev.id] = false">{{ t('editor.reviewers.actions.viewHistory') }}</a>
                        </div>
                     </div>
                  </div>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </SkeletonLoader>
    </div>

    <ActionModal
      :visible="showActionModal"
      :reviewer="Array.isArray(currentReviewer) ? null : currentReviewer"
      :reviewers="Array.isArray(currentReviewer) ? currentReviewer : []"
      :action-type="currentActionType"
      :current-user="user"
      @close="showActionModal = false"
      @submit="handleModalSubmit"
    />

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
.reviewer-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 60px auto 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.role-badge {
  background: #e0e0e0;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  color: #555;
  font-weight: bold;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.filters {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.batch-btn {
  background: #165DFF;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content, .dropdown-menu {
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
  border-radius: 4px;
  right: 0;
}

.dropdown-menu {
  right: 0;
  top: 100%;
}

/* 移除hover效果，使用Vue状态控制下拉菜单 */
/* .dropdown:hover .dropdown-content, .dropdown-action:hover .dropdown-menu {
  display: block;
} */

.dropdown-content a, .dropdown-menu a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
  cursor: pointer;
}

.dropdown-content a:hover, .dropdown-menu a:hover {background-color: #f1f1f1;}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
}

.reviewer-table {
  width: 100%;
  border-collapse: collapse;
}

.reviewer-table th, .reviewer-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.reviewer-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.rev-name { font-weight: bold; color: #2c3e50; }
.rev-email { font-size: 0.85rem; color: #888; }

.tag.field { background: #f0f2f5; color: #555; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }

.metrics { display: flex; gap: 0.5rem; font-size: 0.85rem; color: #666; }

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}
.status-badge.active { background: #e8f5e9; color: #2e7d32; }
.status-badge.inactive { background: #ffebee; color: #c62828; }

.actions-cell {
  width: 280px;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-primary-sm { background: #165DFF; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-warning-sm { background: #ff9800; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-danger-sm { background: #F53F3F; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-text { background: none; border: none; color: #666; cursor: pointer; font-size: 0.8rem; text-decoration: underline; }
.btn-link { background: none; border: none; color: #165DFF; cursor: pointer; }

.dropdown-action {
  position: relative;
  cursor: pointer;
  padding: 0 5px;
}
.dots { font-weight: bold; color: #666; }

</style>
