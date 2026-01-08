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

// 联系信息数据
const contactInfo = ref({
  email: 'admin@journal-platform.com',
  phone: '13800138000',
  address: '北京市海淀区中关村科技园区',
  workingHours: '周一至周五 9:00-18:00'
})

// 表单数据
const formData = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const error = ref('')
const success = ref('')
const submitting = ref(false)

// 验证邮箱格式
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// 提交联系表单
const handleSubmit = () => {
  // 表单验证
  if (!formData.value.name || !formData.value.email || !formData.value.subject || !formData.value.message) {
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
      type: '联系我们',
      name: formData.value.name,
      email: formData.value.email,
      subject: formData.value.subject,
      content: formData.value.message
    })
    
    submitting.value = false
    success.value = '您的留言已成功提交，我们将尽快与您联系！'
    
    // 清空表单
    formData.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
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
  <div class="contact-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'contact'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <!-- 联系我们内容 -->
    <main class="main-content">
      <div class="contact-wrapper">
        <div class="header">
          <h1>联系我们</h1>
          <p class="subtitle">如果您有任何问题或建议，欢迎通过以下方式联系我们</p>
        </div>

        <section class="contact-section">
          <div class="contact-content">
            <!-- 联系信息 -->
            <div class="contact-info">
              <h2 class="section-title">管理员联系方式</h2>
              <div class="info-list">
                <div class="info-item">
                  <div class="info-icon">📧</div>
                  <div class="info-details">
                    <h3>邮箱</h3>
                    <p>{{ contactInfo.email }}</p>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">📱</div>
                  <div class="info-details">
                    <h3>电话</h3>
                    <p>{{ contactInfo.phone }}</p>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">📍</div>
                  <div class="info-details">
                    <h3>地址</h3>
                    <p>{{ contactInfo.address }}</p>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">⏰</div>
                  <div class="info-details">
                    <h3>工作时间</h3>
                    <p>{{ contactInfo.workingHours }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 联系表单 -->
            <div class="contact-form-container">
              <h2 class="section-title">在线留言</h2>
              
              <div v-if="error" class="alert alert-error">{{ error }}</div>
              <div v-if="success" class="alert alert-success">{{ success }}</div>
              
              <form class="contact-form" @submit.prevent="handleSubmit">
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
                <div class="form-group">
                  <label for="subject">主题</label>
                  <input 
                    type="text" 
                    id="subject" 
                    v-model="formData.subject" 
                    class="form-control"
                    placeholder="请输入留言主题"
                    required
                    :disabled="submitting"
                  >
                </div>
                <div class="form-group">
                  <label for="message">留言内容</label>
                  <textarea 
                    id="message" 
                    v-model="formData.message" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入您的留言内容"
                    required
                    :disabled="submitting"
                  ></textarea>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting">提交中...</span>
                    <span v-else>提交留言</span>
                  </button>
                </div>
              </form>
            </div>
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
.contact-container {
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

/* 联系部分样式 */
.contact-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.contact-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

/* 联系内容布局 */
.contact-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

/* 联系信息样式 */
.contact-info {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 联系表单容器样式 */
.contact-form-container {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 标题样式 */
.section-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

/* 信息列表样式 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 信息项样式 */
.info-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

/* 信息图标样式 */
.info-icon {
  font-size: 1.8rem;
  color: #3498db;
  margin-top: 0.2rem;
}

/* 信息详情样式 */
.info-details {
  flex: 1;
}

.info-details h3 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.info-details p {
  font-size: 1rem;
  color: #555;
  margin: 0;
  line-height: 1.6;
}

/* 表单样式 */
.contact-form {
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
  min-height: 150px;
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
  
  .contact-section {
    padding: 1.5rem;
  }
  
  .contact-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .contact-info,
  .contact-form-container {
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