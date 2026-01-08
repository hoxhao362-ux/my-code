<script setup>
import { ref } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const user = ref(userStore.user)

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// 表单数据
const formData = ref({
  name: user.value?.username || '',
  email: user.value?.email || '',
  feedbackType: '建议',
  subject: '',
  content: ''
})

const error = ref('')
const success = ref('')
const submitting = ref(false)

// 验证邮箱格式
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// 提交反馈表单
const handleSubmit = () => {
  // 表单验证
  if (!formData.value.name || !formData.value.email || !formData.value.feedbackType || !formData.value.subject || !formData.value.content) {
    error.value = '请填写完整的表单信息'
    return
  }
  
  if (!validateEmail(formData.value.email)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  
  submitting.value = true
  error.value = ''
  success.value = ''
  
  try {
    // 使用store保存反馈消息
    userStore.addFeedbackMessage({
      type: '意见反馈',
      name: formData.value.name,
      email: formData.value.email,
      subject: formData.value.subject,
      content: formData.value.content,
      feedbackType: formData.value.feedbackType
    })
    
    submitting.value = false
    success.value = '感谢您的反馈！我们将认真考虑您的意见和建议。'
    
    // 清空表单
    formData.value = {
      name: user.value?.username || '',
      email: user.value?.email || '',
      feedbackType: '建议',
      subject: '',
      content: ''
    }
    
    // 5秒后清空成功提示
    setTimeout(() => {
      success.value = ''
    }, 5000)
  } catch (err) {
    submitting.value = false
    error.value = '提交失败，请稍后重试'
  }
}
</script>

<template>
  <div class="feedback-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'feedback'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <!-- 意见反馈内容 -->
    <main class="main-content">
      <div class="feedback-wrapper">
        <div class="header">
          <h1>意见反馈</h1>
          <p class="subtitle">您的反馈对我们非常重要，感谢您的支持与建议</p>
        </div>

        <section class="feedback-section">
          <div class="feedback-content">
            <div v-if="error" class="alert alert-error">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>
            
            <form class="feedback-form" @submit.prevent="handleSubmit">
              <div class="form-row">
                <div class="form-group">
                  <label for="name">姓名</label>
                  <input 
                    type="text" 
                    id="name" 
                    v-model="formData.name" 
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
                    v-model="formData.email" 
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
                    v-model="formData.feedbackType" 
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
                    v-model="formData.subject" 
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
                  v-model="formData.content" 
                  class="form-control textarea-large"
                  rows="10"
                  placeholder="请详细描述您的反馈内容，包括问题发生的场景、操作步骤等"
                  required
                  :disabled="submitting"
                ></textarea>
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
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.feedback-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 主内容样式 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
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

.feedback-wrapper {
  max-width: 800px;
  margin: 0 auto;
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

/* 页脚样式 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
    margin-top: 70px;
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