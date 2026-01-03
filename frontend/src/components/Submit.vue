<script setup>
import { ref } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'logout', 'modules'])

// 表单数据
const formData = ref({
  title: '',
  author: '',
  abstract: '',
  keywords: '',
  content: '',
  module: 'all'
})

const error = ref('')
const success = ref('')

const handleSubmit = () => {
  // 表单验证
  if (!formData.value.title || !formData.value.author || !formData.value.abstract || !formData.value.content) {
    error.value = '请填写完整的投稿信息'
    return
  }
  
  // 创建新期刊对象
  const newJournal = {
    id: Date.now().toString(),
    title: formData.value.title,
    author: formData.value.author,
    abstract: formData.value.abstract,
    keywords: formData.value.keywords,
    content: formData.value.content,
    module: formData.value.module === 'all' ? '其他' : formData.value.module,
    status: 'pending', // 初始状态为待审核
    date: new Date().toISOString(),
    viewCount: 0
  }
  
  // 调用App.vue提供的addJournal方法
  props.addJournal(newJournal)
  
  // 显示成功消息
  error.value = ''
  success.value = '投稿成功！您的稿件已提交至审核队列'
  
  // 清空表单并跳转
  setTimeout(() => {
    formData.value = {
      title: '',
      author: '',
      abstract: '',
      keywords: '',
      content: '',
      module: 'all'
    }
    success.value = ''
    props.navigateTo('home')
  }, 2000)
}

const goBack = () => {
  props.navigateTo('home')
}
</script>

<template>
  <div class="submit-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('home')">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link active">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="logout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 投稿表单 -->
    <main class="submit-content">
      <div class="submit-form-wrapper">
        <h2 class="submit-title">投稿</h2>
        
        <div v-if="error" class="alert error">{{ error }}</div>
        <div v-if="success" class="alert success">{{ success }}</div>
        
        <form class="submit-form">
          <div class="form-section">
            <h3 class="section-subtitle">基本信息</h3>
            
            <div class="form-group">
              <label for="title">论文标题 <span class="required">*</span></label>
              <input 
                type="text" 
                id="title" 
                v-model="formData.title" 
                placeholder="请输入论文标题"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="author">作者 <span class="required">*</span></label>
              <input 
                type="text" 
                id="author" 
                v-model="formData.author" 
                placeholder="请输入作者姓名"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="keywords">关键词</label>
              <input 
                type="text" 
                id="keywords" 
                v-model="formData.keywords" 
                placeholder="请输入关键词，用逗号分隔"
              />
            </div>
            
            <div class="form-group">
              <label for="module">所属模块</label>
              <select 
                id="module" 
                v-model="formData.module"
                required
              >
                <option value="all">其他</option>
                <option v-for="module in modules" :key="module" :value="module">{{ module }}</option>
              </select>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-subtitle">论文内容</h3>
            
            <div class="form-group">
              <label for="abstract">摘要 <span class="required">*</span></label>
              <textarea 
                id="abstract" 
                v-model="formData.abstract" 
                placeholder="请输入论文摘要"
                rows="5"
                required
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="content">正文 <span class="required">*</span></label>
              <textarea 
                id="content" 
                v-model="formData.content" 
                placeholder="请输入论文正文"
                rows="15"
                required
              ></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
            <button type="button" class="btn btn-primary" @click="handleSubmit">提交投稿</button>
          </div>
        </form>
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
.submit-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 导航栏样式（与Home.vue保持一致） */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #3498db;
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
}

/* 投稿内容 */
.submit-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.submit-form-wrapper {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.submit-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 2rem;
  color: #2c3e50;
}

/* 提示信息 */
.alert {
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.alert.error {
  background: #fee;
  color: #e74c3c;
  border: 1px solid #fcc;
}

.alert.success {
  background: #efe;
  color: #2ecc71;
  border: 1px solid #cfc;
}

/* 表单样式 */
.submit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-section {
  margin-bottom: 1rem;
}

.section-subtitle {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.required {
  color: #e74c3c;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

/* 按钮样式 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
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
</style>
