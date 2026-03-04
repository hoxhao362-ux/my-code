<template>
  <div class="consultation-container">
    <h2 class="page-title">在线咨询</h2>
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="consultation-content">
      <div class="contact-info">
        <h3>联系方式</h3>
        <div class="info-item">
          <span class="info-label">客服邮箱：</span>
          <span class="info-value">support@journalplatform.com</span>
        </div>
        <div class="info-item">
          <span class="info-label">客服电话：</span>
          <span class="info-value">400-123-4567</span>
        </div>
        <div class="info-item">
          <span class="info-label">工作时间：</span>
          <span class="info-value">周一至周五 9:00-17:00</span>
        </div>
      </div>
      <div class="consultation-form">
        <h3>在线咨询表单</h3>
        <form @submit.prevent="submitConsultation">
          <div class="form-group">
            <label for="subject">咨询主题</label>
            <input 
              type="text" 
              id="subject" 
              v-model="form.subject" 
              required 
              placeholder="请输入咨询主题"
            >
          </div>
          <div class="form-group">
            <label for="content">咨询内容</label>
            <textarea 
              id="content" 
              v-model="form.content" 
              required 
              rows="5" 
              placeholder="请详细描述您的问题"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="contact">联系方式</label>
            <input 
              type="text" 
              id="contact" 
              v-model="form.contact" 
              required 
              placeholder="请留下您的邮箱或电话，以便我们回复"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="submit-button">提交咨询</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useToastStore } from '../../../stores/toast'

const router = useRouter()
const toastStore = useToastStore()
const form = ref({
  subject: '',
  content: '',
  contact: ''
})

const goBack = () => {
  router.back()
}

const submitConsultation = () => {
  toastStore.add({ message: '咨询已提交，我们将尽快回复您！', type: 'success' })
  form.value = {
    subject: '',
    content: '',
    contact: ''
  }
}
</script>

<style scoped>
.consultation-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: #333;
}

.back-button-container {
  margin-bottom: 2rem;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.back-arrow {
  font-weight: bold;
}

.consultation-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

.contact-info {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.contact-info h3 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #3498db;
}

.info-item {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-label {
  font-weight: 500;
  color: #555;
  width: 80px;
}

.info-value {
  color: #333;
}

.consultation-form {
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.consultation-form h3 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #3498db;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.submit-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.submit-button:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .consultation-content {
    grid-template-columns: 1fr;
  }
}
</style>