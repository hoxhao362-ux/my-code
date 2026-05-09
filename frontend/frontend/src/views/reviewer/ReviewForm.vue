<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReviewStore } from '@/stores/review'
import { useI18n } from '@/composables/useI18n'
import { useToastStore } from '@/stores/toast'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const { t } = useI18n()
const reviewStore = useReviewStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

const taskId = ref(route.params.taskId)
const isSubmitting = ref(false)

const form = reactive({
  score: 5,
  comments: '',
  recommendations: '',
  decision: 'minor_revision'
})

const quillOptions = {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'header': [1, 2, 3, false] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['clean']
    ]
  },
  theme: 'snow'
}

onMounted(async () => {
  if (!taskId.value) {
    toastStore.error(t('review.errors.noTaskId'))
    router.push('/reviewer/dashboard')
    return
  }
  
  // 获取任务详情（如果后端实现了的话）
  await reviewStore.fetchMyTasks()
})

const validateForm = () => {
  if (!form.score || form.score < 1 || form.score > 5) {
    toastStore.error(t('review.errors.scoreRequired'))
    return false
  }
  if (!form.comments.trim()) {
    toastStore.error(t('review.errors.commentsRequired'))
    return false
  }
  if (!form.decision) {
    toastStore.error(t('review.errors.decisionRequired'))
    return false
  }
  return true
}

const submit = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    await reviewStore.submitReview(taskId.value, {
      score: form.score,
      comments: form.comments,
      recommendations: form.recommendations,
      decision: form.decision
    })
    toastStore.success(t('review.success.submitted'))
    router.push('/reviewer/dashboard')
  } catch (e) {
    toastStore.error(e.response?.data?.detail || t('common.error'))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="review-form-container">
    <h3 class="form-title">{{ t('review.title') }}</h3>

    <!-- 稿件信息展示 -->
    <div class="manuscript-info">
      <h4>{{ t('review.manuscriptInfo') }}</h4>
      <div v-if="reviewStore.currentReviewTask" class="info-grid">
        <div class="info-item">
          <span class="label">{{ t('review.taskId') }}:</span>
          <span class="value">#{{ reviewStore.currentReviewTask.manuscript_id }}</span>
        </div>
        <div class="info-item">
          <span class="label">{{ t('review.title') }}:</span>
          <span class="value">{{ reviewStore.currentReviewTask.title }}</span>
        </div>
        <div class="info-item">
          <span class="label">{{ t('review.authors') }}:</span>
          <span class="value">{{ reviewStore.currentReviewTask.authors }}</span>
        </div>
      </div>
    </div>

    <!-- 评分 -->
    <div class="form-group">
      <label class="form-label">{{ t('review.dimensions.score') }} <span class="required">*</span></label>
      <select v-model="form.score" class="form-select">
        <option :value="5">{{ t('review.levels.excellent') }} (5)</option>
        <option :value="4">{{ t('review.levels.good') }} (4)</option>
        <option :value="3">{{ t('review.levels.average') }} (3)</option>
        <option :value="2">{{ t('review.levels.belowAverage') }} (2)</option>
        <option :value="1">{{ t('review.levels.poor') }} (1)</option>
      </select>
    </div>

    <!-- 决策类型 -->
    <div class="form-group">
      <label class="form-label">{{ t('review.decision.label') }} <span class="required">*</span></label>
      <select v-model="form.decision" class="form-select">
        <option value="accept">{{ t('review.decision.accept') }}</option>
        <option value="reject">{{ t('review.decision.reject') }}</option>
        <option value="revision">{{ t('review.decision.revision') }}</option>
        <option value="minor_revision">{{ t('review.decision.minorRevision') }}</option>
        <option value="major_revision">{{ t('review.decision.majorRevision') }}</option>
      </select>
    </div>

    <!-- 给作者的公开评论（富文本） -->
    <div class="form-group">
      <label class="form-label">{{ t('review.comments.label') }} <span class="required">*</span></label>
      <QuillEditor 
        v-model:content="form.comments" 
        contentType="html" 
        :options="quillOptions"
        class="form-textarea large"
        :placeholder="t('review.comments.placeholder')"
      />
    </div>

    <!-- 给编辑的机密建议 -->
    <div class="form-group">
      <label class="form-label">{{ t('review.recommendations.label') }} ({{ t('common.optional') }})</label>
      <textarea 
        v-model="form.recommendations" 
        class="form-textarea"
        :placeholder="t('review.recommendations.placeholder')"
        rows="4"
      ></textarea>
    </div>

    <!-- 提交按钮 -->
    <div class="form-actions">
      <button class="btn-submit" @click="submit" :disabled="isSubmitting">
        {{ isSubmitting ? t('common.submitting') : t('common.submit') }}
      </button>
      <button class="btn-cancel" @click="router.push('/reviewer/dashboard')">
        {{ t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.review-form-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #C93737;
  padding-bottom: 0.5rem;
}

.manuscript-info {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.manuscript-info h4 {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.info-grid {
  display: grid;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  gap: 0.5rem;
}

.info-item .label {
  font-weight: 600;
  color: #333;
  min-width: 100px;
}

.info-item .value {
  color: #666;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.required {
  color: #C93737;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.form-select:focus {
  border-color: #C93737;
  outline: none;
}

.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.form-textarea.large {
  min-height: 200px;
}

.form-textarea:focus {
  border-color: #C93737;
  outline: none;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-submit {
  background: #C93737;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #a82e2e;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background: #666;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #555;
}
</style>
