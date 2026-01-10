<template>
  <div class="feedback-container">
    <h2 class="page-title">意见反馈</h2>
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="feedback-content">
      <div class="feedback-form">
        <h3>意见反馈表单</h3>
        <form @submit.prevent="submitFeedback">
          <div class="form-row">
            <div class="form-group">
              <label for="feedback-type">反馈类型</label>
              <select 
                id="feedback-type" 
                v-model="form.type" 
                required
              >
                <option value="">请选择反馈类型</option>
                <option value="system">系统问题</option>
                <option value="functionality">功能建议</option>
                <option value="content">内容问题</option>
                <option value="other">其他问题</option>
              </select>
            </div>
            <div class="form-group">
              <label for="contact">联系方式</label>
              <input 
                type="text" 
                id="contact" 
                v-model="form.contact" 
                placeholder="请留下您的邮箱或电话（可选）"
              >
            </div>
          </div>
          <div class="form-group">
            <label for="title">反馈标题</label>
            <input 
              type="text" 
              id="title" 
              v-model="form.title" 
              required 
              placeholder="请输入反馈标题"
            >
          </div>
          <div class="form-group">
            <label for="content">反馈内容</label>
            <textarea 
              id="content" 
              v-model="form.content" 
              required 
              rows="6" 
              placeholder="请详细描述您的问题或建议"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="screenshot">上传截图（可选）</label>
            <div class="file-upload">
              <input 
                type="file" 
                id="screenshot" 
                accept="image/*" 
                @change="handleFileUpload"
                class="file-input"
              >
              <label for="screenshot" class="file-label">
                <span v-if="!form.screenshot">点击选择文件或拖拽文件到此处</span>
                <span v-else class="file-name">{{ form.screenshot.name }}</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="submit-button">提交反馈</button>
            <button type="reset" class="reset-button" @click="resetForm">重置</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const form = ref({
  type: '',
  contact: '',
  title: '',
  content: '',
  screenshot: null
})

const goBack = () => {
  router.back()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    form.value.screenshot = file
  }
}

const submitFeedback = () => {
  // 这里可以添加提交逻辑，例如调用API
  alert('反馈已提交，我们将尽快处理！')
  resetForm()
}

const resetForm = () => {
  form.value = {
    type: '',
    contact: '',
    title: '',
    content: '',
    screenshot: null
  }
  // 重置文件输入
  const fileInput = document.getElementById('screenshot')
  if (fileInput) {
    fileInput.value = ''
  }
}
</script>

<style scoped>
.feedback-container {
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

.feedback-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.feedback-form h3 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #3498db;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.2rem;
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 150px;
}

.file-upload {
  position: relative;
  overflow: hidden;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.file-label {
  display: block;
  padding: 1rem;
  background-color: #f9f9f9;
  border: 2px dashed #ddd;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #555;
}

.file-label:hover {
  border-color: #3498db;
  background-color: #f0f8ff;
}

.file-name {
  color: #3498db;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 1rem;
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

.reset-button {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.reset-button:hover {
  background-color: #e0e0e0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>