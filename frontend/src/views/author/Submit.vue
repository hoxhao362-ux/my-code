<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()

// 表单数据
const formData = ref({
  title: '',
  author: userStore.user?.username || '',
  abstract: '',
  keywords: '',
  content: '',
  module: 'all'
})

// 附录相关状态
const appendices = ref([])
const maxFileSize = 10 * 1024 * 1024 // 10MB

const error = ref('')
const success = ref('')

const handleSubmit = () => {
  // 表单验证
  if (!formData.value.title || !formData.value.abstract || !formData.value.content) {
    error.value = '请填写完整的投稿信息'
    return
  }
  
  // 创建新期刊对象
  const newJournal = {
    id: Date.now().toString(),
    title: formData.value.title,
    author: userStore.user?.username || '匿名',
    abstract: formData.value.abstract,
    keywords: formData.value.keywords.split(',').map(k => k.trim()).filter(k => k),
    content: formData.value.content,
    module: formData.value.module === 'all' ? '其他' : formData.value.module,
    status: '审稿中', // 初始状态为审稿中
    reviewStage: '初审', // 默认进入初审阶段
    date: new Date().toISOString().split('T')[0],
    viewCount: 0,
    appendices: appendices.value
  }
  
  // 调用状态管理的添加期刊方法
  userStore.addJournal(newJournal)
  
  // 显示成功消息
  error.value = ''
  success.value = '投稿成功！您的稿件已提交至审核队列'
  
  // 清空表单并跳转
  setTimeout(() => {
    router.push('/author')
  }, 2000)
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="submit-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'author-submit'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 投稿表单 -->
    <main class="submit-content">
      <div class="submit-form-wrapper">
        <h2 class="submit-title">新投稿</h2>
        
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
                <option v-for="module in userStore.modules" :key="module" :value="module">{{ module }}</option>
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
          
          <!-- 附录上传部分 -->
          <div class="form-section">
            <h3 class="section-subtitle">附录</h3>
            <p class="appendix-hint">支持上传PDF、Word、代码、压缩包等文件，单个文件不超过10MB</p>
            
            <div class="form-group">
              <label for="appendix-upload">上传附录文件</label>
              <div class="upload-section">
                <input 
                  type="file" 
                  id="appendix-upload"
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.csv,.html,.css,.js,.json,.zip,.7z,.tar,.gz"
                  class="file-input"
                />
                <label for="appendix-upload" class="upload-btn">
                  <span class="upload-icon">📁</span> 选择文件
                </label>
              </div>
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
/* 样式可以从原 Submit.vue 组件复制 */
</style>