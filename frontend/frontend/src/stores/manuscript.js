import { defineStore } from 'pinia'
import { ref } from 'vue'
import { manuscriptApi, adminApi } from '../utils/api'

// 1. 适配后端 ManuscriptStatus 枚举
export const ManuscriptStatus = {
  PENDING_INITIAL_REVIEW: 'pending_initial_review',
  UNDER_INITIAL_REVIEW: 'under_initial_review',
  INITIAL_REVIEW_PASSED: 'initial_review_passed',
  INITIAL_REVIEW_REVISION: 'initial_review_revision',
  INITIAL_REVIEW_REJECTED: 'initial_review_rejected',
  PENDING_PEER_REVIEW: 'pending_peer_review',
  UNDER_PEER_REVIEW: 'under_peer_review',
  REVIEW_COMPLETED: 'review_completed',
  REVISION_REQUIRED: 'revision_required',
  REVISION_SUBMITTED: 'revision_submitted',
  PENDING_FINAL_DECISION: 'pending_final_decision',
  UNDER_FINAL_DECISION: 'under_final_decision',
  FINAL_DECISION_ACCEPTED: 'final_decision_accepted',
  FINAL_DECISION_REVISION: 'final_decision_revision',
  FINAL_DECISION_REJECTED: 'final_decision_rejected',
  PENDING_ACCEPTANCE_CONFIRMATION: 'pending_acceptance_confirmation',
  PENDING_COPYRIGHT: 'pending_copyright',
  PENDING_PROOF: 'pending_proof',
  PENDING_PUBLICATION: 'pending_publication',
  PUBLISHED: 'published',
  WITHDRAWN: 'withdrawn',
  TRANSFER_SUGGESTED: 'transfer_suggested',
  TRANSFERRED: 'transferred'
}

// 2. 适配后端 ReviewStage 枚举
export const ReviewStage = {
  INITIAL_REVIEW: 'initial_review',
  PEER_REVIEW: 'peer_review',
  FINAL_DECISION: 'final_decision'
}

// 3. 适配后端 WorkflowAction 枚举
export const WorkflowAction = {
  SAVE: 'save',
  SUBMIT: 'submit',
  WITHDRAW: 'withdraw',
  SCREEN: 'screen',
  ASSIGN: 'assign',
  REVIEW: 'review',
  DECIDE: 'decide',
  REVISE: 'revise',
  APPROVE: 'approve',
  PUBLISH: 'publish'
}

export const useManuscriptStore = defineStore('manuscript', () => {
  const manuscripts = ref([])
  const currentManuscript = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 获取所有稿件（管理员/编辑端）
  const fetchAllManuscripts = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await adminApi.getAllJournals(params)
      manuscripts.value = res.data?.items || res.data || []
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch manuscripts'
      console.error(error.value)
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户的稿件（作者端）
  const fetchMyManuscripts = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await manuscriptApi.getMyManuscripts(params)
      manuscripts.value = res.data?.items || res.data || []
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch my manuscripts'
      console.error(error.value)
    } finally {
      loading.value = false
    }
  }

  // 获取单个稿件详情
  const fetchManuscriptDetail = async (manuscript_id) => {
    loading.value = true
    error.value = null
    try {
      const res = await manuscriptApi.getManuscriptDetail(manuscript_id)
      const data = res.data || res
      currentManuscript.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch manuscript detail'
      console.error(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  // 提交新稿件
  const submitManuscript = async (formData) => {
    loading.value = true
    error.value = null
    try {
      const res = await manuscriptApi.upload(formData)
      return res.data || res
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Submission failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 触发工作流状态更新
  const updateManuscriptWorkflow = async (manuscript_id, actionData) => {
    loading.value = true
    try {
      const res = await manuscriptApi.updateWorkflow(manuscript_id, actionData)
      const updatedData = res.data || res
      
      // 更新本地状态
      const index = manuscripts.value.findIndex(m => String(m.manuscript_id) === String(manuscript_id))
      if (index !== -1) {
        manuscripts.value[index] = { ...manuscripts.value[index], ...updatedData }
      }
      if (currentManuscript.value && String(currentManuscript.value.manuscript_id) === String(manuscript_id)) {
        currentManuscript.value = { ...currentManuscript.value, ...updatedData }
      }
      return updatedData
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Workflow update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取当前可用工作流动作
  const fetchAvailableActions = async (manuscript_id) => {
    try {
      const res = await manuscriptApi.getAvailableActions(manuscript_id)
      return res.data || res
    } catch (err) {
      console.error('Failed to fetch actions:', err)
      return []
    }
  }

  return {
    manuscripts,
    currentManuscript,
    loading,
    error,
    fetchAllManuscripts,
    fetchMyManuscripts,
    fetchManuscriptDetail,
    submitManuscript,
    updateManuscriptWorkflow,
    fetchAvailableActions
  }
})
