<script setup>
import { reactive, ref } from 'vue'
import { useReviewStore } from '@/stores/review'
import { useI18n } from '@/composables/useI18n'
import { useToastStore } from '@/stores/toast'

const { t } = useI18n()
const reviewStore = useReviewStore()
const toastStore = useToastStore()

const form = reactive({
  // 后端要求：科学性分数 (1-5)
  score: 5,
  // 给作者的公开评论
  comments: '',
  // 给编辑的机密建议
  recommendations: '',
  // 最终建议 (accept/minor_revision/major_revision/reject)
  decision: 'minor_revision'
})

const submit = async () => {
  try {
    // taskId 从路由获取
    await reviewStore.submitOpinion(props.taskId, form)
    toastStore.success(t('common.success'))
    router.push('/reviewer/dashboard')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || t('common.error'))
  }
}
</script>

<template>
  <div class="review-form">
    <h3>{{ t('review.title') }}</h3>
    <div class="dimension">
      <label>{{ t('review.dimensions.methodology') }}</label>
      <select v-model="form.score">
        <option :value="5">{{ t('review.levels.excellent') }}</option>
        <option :value="1">{{ t('review.levels.poor') }}</option>
      </select>
    </div>
    <div class="decision">
      <label>{{ t('review.decision.label') }}</label>
      <select v-model="form.decision">
        <option value="accept">{{ t('review.decision.accept') }}</option>
        <option value="reject">{{ t('review.decision.reject') }}</option>
      </select>
    </div>
    <textarea v-model="form.comments" :placeholder="t('review.comments.placeholder')"></textarea>
    <button @click="submit">{{ t('common.submit') }}</button>
  </div>
</template>

<style scoped>
.review-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
}

.dimension,
.decision {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

select:focus {
  border-color: #3498db;
  outline: none;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 150px;
  margin-bottom: 1.5rem;
}

textarea:focus {
  border-color: #3498db;
  outline: none;
}

button {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background: #2980b9;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
