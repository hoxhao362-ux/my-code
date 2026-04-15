import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reviewApi } from '../utils/api'

export const useReviewStore = defineStore('review', () => {
  const pendingTasks = ref([])
  const isLoading = ref(false)

  // 获取真实的待审稿件列表
  const fetchPendingTasks = async () => {
    isLoading.value = true
    try {
      const response = await reviewApi.getPendingJournals()
      pendingTasks.value = Array.isArray(response) ? response : (response.items || [])
    } catch (error) {
      console.error('获取待审任务失败:', error)
      pendingTasks.value = []
    } finally {
      isLoading.value = false
    }
  }

  // 获取审稿历史
  const reviewHistory = ref([])
  const fetchReviewHistory = async () => {
    try {
      const response = await reviewApi.getReviewHistory()
      reviewHistory.value = Array.isArray(response) ? response : (response.items || [])
    } catch (error) {
      console.error('获取审稿历史失败:', error)
      reviewHistory.value = []
    }
  }

  // 提交审稿意见
  const submitReview = async (journalId, reviewData) => {
    try {
      await reviewApi.reviewJournal(journalId, reviewData)
      pendingTasks.value = pendingTasks.value.filter(j => String(j.id) !== String(journalId))
      await fetchReviewHistory()
    } catch (err) {
      console.error('提交审稿失败:', err)
      throw err
    }
  }

  // 统计信息
  const reviewStats = computed(() => {
    return {
      pendingCount: pendingTasks.value.length,
      completedCount: reviewHistory.value.length
    }
  })

  return {
    pendingTasks,
    isLoading,
    reviewHistory,
    reviewStats,
    fetchPendingTasks,
    fetchReviewHistory,
    submitReview
  }
})
