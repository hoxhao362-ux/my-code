import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reviewApi } from '../utils/api'

export const useReviewStore = defineStore('review', () => {
  const pendingReviews = ref([]) // 待我审核的稿件
  const reviewHistory = ref([]) // 我的审稿历史
  const loading = ref(false)
  const error = ref(null)

  // 获取待审稿件
  const fetchPendingReviews = async () => {
    loading.value = true
    try {
      const data = await reviewApi.getPendingJournals()
      pendingReviews.value = data
    } catch (err) {
      error.value = err.message || 'Failed to fetch pending reviews'
    } finally {
      loading.value = false
    }
  }

  // 获取审稿历史
  const fetchReviewHistory = async (reviewerName) => {
    loading.value = true
    try {
      const data = await reviewApi.getReviewHistory(reviewerName)
      reviewHistory.value = data
    } catch (err) {
      error.value = err.message || 'Failed to fetch review history'
    } finally {
      loading.value = false
    }
  }

  // 提交审稿意见
  const submitReview = async (journalId, reviewData) => {
    loading.value = true
    try {
      await reviewApi.reviewJournal(journalId, reviewData)
      // 提交成功后，从待审列表中移除
      pendingReviews.value = pendingReviews.value.filter(j => String(j.id) !== String(journalId))
      // 刷新历史
      if (reviewData.reviewer) {
          await fetchReviewHistory(reviewData.reviewer)
      }
    } catch (err) {
      error.value = err.message || 'Failed to submit review'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 统计信息
  const reviewStats = computed(() => {
    return {
      pendingCount: pendingReviews.value.length,
      completedCount: reviewHistory.value.length
    }
  })

  return {
    pendingReviews,
    reviewHistory,
    loading,
    error,
    reviewStats,
    fetchPendingReviews,
    fetchReviewHistory,
    submitReview
  }
})
