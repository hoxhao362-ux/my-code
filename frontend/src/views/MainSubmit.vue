<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const router = useRouter()
const route = useRoute()

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// 表单数据
const formData = ref({
  title: '',
  author: userStore.user?.username || '', // 初始化为当前用户的用户名
  abstract: '',
  keywords: '',
  content: '',
  module: 'all'
})

const error = ref('')
const success = ref('')
const submitting = ref(false)

// 获取所有模块
const modules = computed(() => userStore.modules)

// 组件挂载时初始化作者字段
onMounted(() => {
  if (userStore.user) {
    formData.value.author = userStore.user.username
  }
})

const handleSubmit = async () => {
  // 表单验证
  if (!formData.value.title || !formData.value.abstract || !formData.value.content) {
    error.value = '请填写完整的投稿信息'
    return
  }
  
  // 确保用户已登录
  if (!userStore.user) {
    error.value = '请先登录后再进行投稿'
    return
  }
  
  submitting.value = true
  error.value = ''
  success.value = ''
  
  try {
    // 创建新期刊对象
    const newJournal = {
      id: Date.now().toString(),
      title: formData.value.title,
      author: userStore.user.username, // 自动使用当前登录用户的用户名
      abstract: formData.value.abstract,
      keywords: formData.value.keywords.split(',').map(k => k.trim()).filter(Boolean),
      content: formData.value.content,
      module: formData.value.module === 'all' ? '其他' : formData.value.module,
      status: '待审核', // 初始状态为待审核
      reviewStage: '初审', // 初始审稿阶段为初审
      date: new Date().toISOString().split('T')[0],
      viewCount: 0,
      authorId: userStore.user.username // 使用用户名作为作者ID
    }
    
    // 调用userStore提供的addJournal方法
    userStore.addJournal(newJournal)
    
    // 显示成功消息
    success.value = '投稿成功！您的稿件已提交至审核队列'
    
    // 清空表单并跳转到个人中心，让用户可以立即看到投稿记录
    setTimeout(() => {
      formData.value = {
        title: '',
        author: userStore.user?.username || '', // 重置时保留当前用户名
        abstract: '',
        keywords: '',
        content: '',
        module: 'all'
      }
      success.value = ''
      router.push('/profile')
    }, 2000)
  } catch (err) {
    error.value = '投稿失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="main-submit-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'submit'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />
    
    <!-- 主内容 -->
    <main class="main-content">
      <div class="submit-form-wrapper">
        <!-- 投稿须知页面 -->
        <template v-if="route.path === '/submission-rules'">
          <h2 class="submit-title">投稿须知</h2>
          
          <div class="rules-content">
            <div class="rules-section">
              <h3 class="section-subtitle">格式要求</h3>
              <ul class="rules-list">
                <li><strong>标题格式：</strong>简洁明了，不超过20个汉字，避免使用特殊符号</li>
                <li><strong>作者信息：</strong>请填写真实姓名，多个作者之间用逗号分隔</li>
                <li><strong>摘要要求：</strong>200-500字，概述论文的研究目的、方法、结果和结论</li>
                <li><strong>关键词：</strong>3-5个，用逗号分隔，反映论文的核心内容</li>
                <li><strong>正文格式：</strong>结构清晰，包括引言、方法、结果、讨论和结论等部分</li>
                <li><strong>参考文献：</strong>采用标准格式，注明作者、标题、期刊名称、年份、卷号、页码等信息</li>
                <li><strong>图表要求：</strong>清晰可读，图表标题和编号完整，确保分辨率不低于300DPI</li>
              </ul>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">版权要求</h3>
              <ul class="rules-list">
                <li><strong>原创性声明：</strong>投稿者需确保所投论文为原创作品，未在其他期刊或平台发表过</li>
                <li><strong>版权转让：</strong>论文发表后，版权归期刊投稿平台所有，平台有权对论文进行编辑、修改和传播</li>
                <li><strong>引用规范：</strong>论文中引用他人成果需注明出处，避免抄袭和剽窃行为</li>
                <li><strong>保密要求：</strong>涉及国家机密、商业秘密或个人隐私的内容不得投稿</li>
                <li><strong>法律责任：</strong>投稿者需对论文内容的真实性和合法性负责，如因侵权等问题产生法律纠纷，由投稿者承担全部责任</li>
                <li><strong>退稿政策：</strong>平台有权根据审稿结果拒绝不符合要求的稿件，退稿后投稿者可自行处理稿件</li>
              </ul>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">投稿流程</h3>
              <ol class="rules-list">
                <li>注册并登录期刊投稿平台</li>
                <li>点击"投稿中心"->"在线投稿"，填写投稿信息</li>
                <li>上传论文全文（支持多种格式）</li>
                <li>提交投稿，获取投稿编号</li>
                <li>等待审稿结果，可通过个人中心查看稿件状态</li>
                <li>根据审稿意见修改论文（如需）</li>
                <li>论文发表，获取发表证明</li>
              </ol>
            </div>
            
            <div class="rules-actions">
              <button class="btn btn-primary" @click="router.push('/submit')">
                开始在线投稿
              </button>
              <button class="btn btn-secondary" @click="goBack">
                返回首页
              </button>
            </div>
          </div>
        </template>
        
        <!-- 在线投稿表单 -->
        <template v-else>
          <h2 class="submit-title">在线投稿</h2>
          
          <div v-if="error" class="alert error animate-fade-in">{{ error }}</div>
          <div v-if="success" class="alert success animate-fade-in">
            <div class="alert-icon">✓</div>
            <div class="alert-content">{{ success }}</div>
            <div class="alert-hint">即将跳转到个人中心查看投稿记录...</div>
          </div>
          
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
                  :disabled="submitting"
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
                  :disabled="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="keywords">关键词</label>
                <input 
                  type="text" 
                  id="keywords" 
                  v-model="formData.keywords" 
                  placeholder="请输入关键词，用逗号分隔"
                  :disabled="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="module">所属模块</label>
                <select 
                  id="module" 
                  v-model="formData.module"
                  required
                  :disabled="submitting"
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
                  :disabled="submitting"
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
                  :disabled="submitting"
                ></textarea>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="goBack" :disabled="submitting">取消</button>
              <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
                <span v-if="submitting">投稿中...</span>
                <span v-else>提交投稿</span>
              </button>
            </div>
          </form>
        </template>
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
.main-submit-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
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
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 500;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.alert.error {
  background: linear-gradient(135deg, #fee, #fdd);
  color: #e74c3c;
  border: 1px solid #fcc;
}

.alert.success {
  background: linear-gradient(135deg, #efe, #dfd);
  color: #2ecc71;
  border: 1px solid #cfc;
}

.alert-icon {
  font-size: 1.8rem;
  font-weight: bold;
  margin-top: 0.2rem;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.alert-hint {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 0.5rem;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease forwards;
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
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group select {
  cursor: pointer;
}

.form-group input:disabled,
.form-group textarea:disabled,
.form-group select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
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

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(149, 165, 166, 0.4);
}

/* 投稿须知样式 */
.rules-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.rules-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.rules-list {
  list-style-position: inside;
  padding-left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rules-list li {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
}

.rules-list strong {
  color: #2c3e50;
  font-weight: 600;
}

.rules-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.rules-actions .btn {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
}

/* 页脚 */
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
  .rules-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .rules-actions .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .rules-list {
    padding-left: 0;
  }
  
  .rules-section {
    padding: 1rem;
  }
}
</style>