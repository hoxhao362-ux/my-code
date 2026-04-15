import { defineStore } from 'pinia'
import { ref } from 'vue'
import { journalApi } from '../utils/api'

export const useManuscriptStore = defineStore('manuscript', () => {
  const manuscripts = ref([])
  const currentManuscript = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 获取所有稿件（管理员/编辑）
  const fetchAllManuscripts = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await journalApi.getAllJournals()
      manuscripts.value = data
    } catch (err) {
      error.value = err.message || 'Failed to fetch manuscripts'
      console.error(error.value)
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户的稿件（作者）
  const fetchMyManuscripts = async (username) => {
    loading.value = true
    error.value = null
    try {
      const data = await journalApi.getMyJournals(username)
      manuscripts.value = data
    } catch (err) {
      error.value = err.message || 'Failed to fetch my manuscripts'
      console.error(error.value)
    } finally {
      loading.value = false
    }
  }

  // 获取单个稿件详情
  const fetchManuscriptDetail = async (id) => {
    loading.value = true
    error.value = null
    try {
      const data = await journalApi.getJournalDetail(id)
      currentManuscript.value = data
      return data
    } catch (err) {
      error.value = err.message || 'Failed to fetch manuscript detail'
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
      const result = await journalApi.upload(formData)
      return result
    } catch (err) {
      error.value = err.message || 'Submission failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新稿件信息
  const updateManuscript = async (id, updates) => {
    loading.value = true
    try {
      await journalApi.updateJournal(id, updates)
      // 更新本地状态
      const index = manuscripts.value.findIndex(m => String(m.id) === String(id))
      if (index !== -1) {
        manuscripts.value[index] = { ...manuscripts.value[index], ...updates }
      }
      if (currentManuscript.value && String(currentManuscript.value.id) === String(id)) {
        currentManuscript.value = { ...currentManuscript.value, ...updates }
      }
    } catch (err) {
      error.value = err.message || 'Update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除稿件
  const deleteManuscript = async (id) => {
    loading.value = true
    try {
      await journalApi.deleteJournal(id)
      manuscripts.value = manuscripts.value.filter(m => String(m.id) !== String(id))
    } catch (err) {
      error.value = err.message || 'Delete failed'
      throw err
    } finally {
      loading.value = false
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
    updateManuscript,
    deleteManuscript
  }
})
