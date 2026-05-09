<template>
  <div class="feedback-container">
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="feedback-wrapper">
      <div class="header">
        <h1>意见反馈</h1>
        <p class="subtitle">您的反馈对我们非常重要，感谢您的支持与建议</p>
      </div>
      
      <section class="feedback-section">
        <div class="feedback-content">
          <div v-if="error" class="alert alert-error">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>
          
          <form class="feedback-form" @submit.prevent="submitFeedback">
            <div class="form-row">
              <div class="form-group">
                <label for="name">姓名</label>
                <input 
                  type="text" 
                  id="name" 
                  v-model="form.name" 
                  class="form-control"
                  placeholder="请输入您的姓名"
                  required
                  :disabled="submitting"
                >
              </div>
              <div class="form-group">
                <label for="email">邮箱</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="form.email" 
                  class="form-control"
                  placeholder="请输入您的邮箱"
                  required
                  :disabled="submitting"
                >
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="feedbackType">反馈类型</label>
                <select 
                  id="feedbackType" 
                  v-model="form.feedbackType" 
                  class="form-control"
                  required
                  :disabled="submitting"
                >
                  <option value="建议">建议</option>
                  <option value="bug">bug报告</option>
                  <option value="投诉">投诉</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div class="form-group">
                <label for="subject">主题</label>
                <input 
                  type="text" 
                  id="subject" 
                  v-model="form.subject" 
                  class="form-control"
                  placeholder="请输入反馈主题"
                  required
                  :disabled="submitting"
                >
              </div>
            </div>
            <div class="form-group">
              <label for="content">反馈内容</label>
              <textarea 
                id="content" 
                v-model="form.content" 
                class="form-control textarea-large"
                rows="10"
                placeholder="请详细描述您的反馈内容，包括问题发生的场景、操作步骤等"
                required
                :disabled="submitting"
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
                  :disabled="submitting"
                >
                <label for="screenshot" class="file-label">
                  <span v-if="!form.screenshot">点击选择文件或拖拽文件到此处</span>
                  <span v-else class="file-name">{{ form.screenshot.name }}</span>
                </label>
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting">提交中...</span>
                <span v-else>提交反馈</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../../stores/user'

const router = useRouter()
const userStore = useUserStore()
const user = ref(userStore.user)

const form = ref({
  name: user.value?.username || '',
  email: user.value?.email || '',
  feedbackType: '建议',
  subject: '',
  content: '',
  screenshot: null
})

const error = ref('')
const success = ref('')
const submitting = ref(false)

const goBack = () => {
  router.back()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    form.value.screenshot = file
  }
}

// 验证邮箱格式
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const submitFeedback = () => {
  // 表单验证
  if (!form.value.name || !form.value.email || !form.value.feedbackType || !form.value.subject || !form.value.content) {
    error.value = '请填写完整的表单信息'
    return
  }
  
  if (!validateEmail(form.value.email)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  
  submitting.value = true
  error.value = ''
  success.value = ''
  
  try {
    // 准备反馈数据
    const feedbackData = {
      id: Date.now(),
      type: '意见反馈',
      name: form.value.name,
      email: form.value.email,
      subject: form.value.subject,
      content: form.value.content,
      feedbackType: form.value.feedbackType,
      // 截图暂时不处理，因为localStorage无法直接存储文件
      screenshot: form.value.screenshot ? form.value.screenshot.name : null
    }
    
    // 使用userStore添加反馈消息
    userStore.addFeedbackMessage(feedbackData)
    
    submitting.value = false
    success.value = '感谢您的反馈！我们将认真考虑您的意见和建议。'
    
    // 清空表单
    resetForm()
    
    // 5秒后清空成功提示
    setTimeout(() => {
      success.value = ''
    }, 5000)
  } catch (err) {
    console.error('反馈提交失败:', err)
    submitting.value = false
    error.value = '提交失败，请稍后重试'
  }
}

const resetForm = () => {
  form.value = {
    name: user.value?.username || '',
    email: user.value?.email || '',
    feedbackType: '建议',
    subject: '',
    content: '',
    screenshot: null
  }
  // 重置文件输入
  const fileInput = document.getElementById('screenshot')
  if (fileInput) {
    fileInput.value = ''
  }
}

// 组件挂载时自动填充用户信息
onMounted(() => {
  user.value = userStore.user
  form.value.name = user.value?.username || ''
  form.value.email = user.value?.email || ''
})
</script>

<style scoped>
/* 主容器样式 */
.feedback-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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

/* 反馈包裹器样式 */
.feedback-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  text-align: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 1rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 反馈部分样式 */
.feedback-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

/* 反馈内容样式 */
.feedback-content {
  max-width: 700px;
  margin: 0 auto;
}

/* 表单样式 */
.feedback-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 表单行样式 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

/* 表单组样式 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #555;
}

/* 表单控件样式 */
.form-control {
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: white;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.textarea-large {
  resize: vertical;
  min-height: 200px;
  font-family: inherit;
}

/* 文件上传样式 */
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
  border-radius: 6px;
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

/* 表单操作按钮样式 */
.form-actions {
  display: flex;
  justify-content: flex-end;
}

/* 按钮样式 */
.btn {
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 提示信息样式 */
.alert {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  font-weight: 500;
}

.alert-error {
  background-color: #fee;
  color: #e74c3c;
  border: 1px solid #fcc;
}

.alert-success {
  background-color: #efe;
  color: #2ecc71;
  border: 1px solid #cfc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feedback-container {
    padding: 1rem;
  }
  
  .header h1 {
    font-size: 1.6rem;
  }
  
  .feedback-section {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    justify-content: center;
  }
  
  .btn {
    width: 100%;
  }
}
</style>