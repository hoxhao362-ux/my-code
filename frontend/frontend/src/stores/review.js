import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reviewApi } from '../utils/api'

export const useReviewStore = defineStore('review', () => {
  const reviewTasks = ref([])
  const currentReviewTask = ref(null)
  const isLoading = ref(false)
  const pagination = ref({
    page: 1,
    page_size: 10,
    total: 0
  })

  // 评审意见字段
  const reviewForm = ref({
    score: 5,
    comments: '',
    recommendations: '',
    decision: 'minor_revision'
  })

  // 获取我的审稿任务列表
  const fetchMyTasks = async (params = {}) => {
    isLoading.value = true
    try {
      const queryParams = {
        page: pagination.value.page,
        page_size: pagination.value.page_size,
        ...params
      }
      const response = await reviewApi.getMyTasks(queryParams)
      const data = response.data || response
      reviewTasks.value = data.items || []
      pagination.value.total = data.total || 0
      pagination.value.page = data.page || 1
      pagination.value.page_size = data.page_size || 10
    } catch (error) {
      console.error('获取审稿任务失败:', error)
      reviewTasks.value = []
    } finally {
      isLoading.value = false
    }
  }

  // 提交审稿意见
  const submitReview = async (taskId, reviewData) => {
    try {
      await reviewApi.submitReview(taskId, reviewData)
      await fetchMyTasks()
    } catch (error) {
      console.error('提交审稿意见失败:', error)
      throw error
    }
  }

  // 获取审稿人列表（管理员）
  const fetchReviewersList = async (params = {}) => {
    try {
      const response = await reviewApi.getReviewersList(params)
      return response.data || response
    } catch (error) {
      console.error('获取审稿人列表失败:', error)
      return []
    }
  }

  // 统计信息
  const reviewStats = computed(() => {
    return {
      pendingCount: reviewTasks.value.filter(t => t.status === 'pending').length,
      completedCount: reviewTasks.value.filter(t => t.status === 'completed').length,
      overdueCount: reviewTasks.value.filter(t => t.status === 'overdue').length
    }
  })

  return {
    reviewTasks,
    currentReviewTask,
    isLoading,
    pagination,
    reviewForm,
    reviewStats,
    fetchMyTasks,
    submitReview,
    fetchReviewersList
  }
})
