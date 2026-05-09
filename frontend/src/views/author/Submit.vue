<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { useI18n } from 'vue-i18n'
import { manuscriptApi } from '../../utils/api'
import { useManuscriptStore } from '../../stores/manuscript'
import Navigation from '../../components/Navigation.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const toastStore = useToastStore()
const manuscriptStore = useManuscriptStore()

// 表单数据
const formData = ref({
  title: '',
  author: userStore.user?.username || '',
  abstract: '',
  keywords: '',
  content: '',
  modules: ['all'],
  attachments: []
})

const error = ref('')
const success = ref('')
const submitting = ref(false)

// 触发文件上传
const triggerFileUpload = () => {
  document.getElementById('attachment-upload').click()
}

// 附件上传处理
const handleFileUpload = (event) => {
  // 阻止事件冒泡和默认行为，防止表单提交
  event.stopPropagation()
  event.preventDefault()
  
  const file = event.target.files[0]
  if (file) {
    // 检查文件大小（限制10MB）
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      error.value = t('submit.validation.fileSize')
      return
    }
    
    // 检查文件类型
    const allowedTypes = ['.doc', '.docx', '.pdf']
    const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`
    if (!allowedTypes.includes(fileExtension)) {
      error.value = t('submit.validation.fileType')
      return
    }
    
    // 创建文件URL用于预览
    const fileUrl = URL.createObjectURL(file)
    
    // 添加到附件列表
    const attachment = {
      id: Date.now().toString(),
      name: file.name,
      type: file.type,
      size: file.size,
      url: fileUrl,
      file: file
    }
    
    formData.value.attachments.push(attachment)
    
    // 清空文件输入
    event.target.value = ''
  }
}

// 删除附件
const removeAttachment = (attachmentId) => {
  // 从附件列表中移除
  const index = formData.value.attachments.findIndex(att => att.id === attachmentId)
  if (index !== -1) {
    formData.value.attachments.splice(index, 1)
  }
}

// 预览附件
const previewAttachment = (attachment) => {
  const fileExtension = `.${attachment.name.split('.').pop().toLowerCase()}`
  const previewableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
  
  if (previewableExtensions.includes(fileExtension)) {
    // 使用FileReader读取文件内容并转换为data URL
    const reader = new FileReader()
    reader.onload = (e) => {
      const fileUrl = e.target.result
      // 创建一个新的预览窗口
      const previewWindow = window.open('', '_blank', 'width=1000,height=800')
      if (previewWindow) {
        // 设置基本的HTML结构
        previewWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>${t('preview.title', { name: attachment.name })}</title>
            <style>
              * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
              }
              body, html {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
              }
              .preview-header {
                padding: 15px 20px;
                background: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
              }
              .preview-title {
                font-weight: bold;
                color: #2c3e50;
                font-size: 16px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 60%;
              }
              .header-actions {
                display: flex;
                gap: 10px;
                align-items: center;
              }
              .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s ease;
                display: inline-block;
                text-align: center;
              }
              .btn-primary {
                background: #3498db;
                color: white;
              }
              .btn-primary:hover {
                background: #2980b9;
              }
              .btn-secondary {
                background: #95a5a6;
                color: white;
              }
              .btn-secondary:hover {
                background: #7f8c8d;
              }
              .preview-container {
                height: calc(100% - 60px);
                width: 100%;
                background: white;
                overflow: auto;
                position: relative;
              }
              .preview-content {
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                padding: 20px;
              }
              iframe {
                width: 100%;
                height: 100%;
                border: none;
                background: white;
              }
              img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
              }
              pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                font-family: 'Courier New', Courier, monospace;
                font-size: 14px;
                line-height: 1.6;
                width: 100%;
                max-width: 1000px;
                height: 100%;
                overflow: auto;
              }
              object {
                width: 100%;
                height: 100%;
                border: none;
              }
              .loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
                color: #666;
                font-size: 16px;
              }
              .loading::before {
                content: '';
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
              }
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
              .file-info {
                background: #f8f9fa;
                padding: 10px 20px;
                border-top: 1px solid #e0e0e0;
                color: #666;
                font-size: 14px;
              }
            </style>
          </head>
          <body>
            <div class="preview-header">
              <div class="preview-title">${attachment.name}</div>
              <div class="header-actions">
                <button class="btn btn-primary" onclick="downloadFile()">${t('preview.download')}</button>
                <button class="btn btn-secondary" onclick="closePreview()">${t('preview.close')}</button>
              </div>
            </div>
            <div class="preview-container">
              <div id="preview-content" class="preview-content">
                <div class="loading">${t('preview.loading')}</div>
              </div>
            </div>
            <div class="file-info">
              ${t('preview.fileType')}: ${fileExtension.substring(1).toUpperCase()} | ${t('preview.size')}: ${formatFileSize(attachment.size)}
            </div>
            <script>
              // 格式化文件大小
              function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
              }
              
              // 下载文件
              function downloadFile() {
                const link = document.createElement('a');
                link.href = '${fileUrl}';
                link.download = '${attachment.name}';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }
              
              // 关闭预览
              function closePreview() {
                window.close();
              }
              
              // 初始化预览
              function initPreview() {
                const contentDiv = document.getElementById('preview-content');
                const fileType = '${fileExtension}';
                const fileUrl = '${fileUrl}';
                
                contentDiv.innerHTML = '';
                
                if (fileType === '.pdf') {
                  // PDF预览，使用object标签替代iframe以获得更好的兼容性
                  const object = document.createElement('object');
                  object.data = fileUrl;
                  object.type = 'application/pdf';
                  object.style.width = '100%';
                  object.style.height = '100%';
                  
                  // 添加加载错误处理
                  object.onerror = function() {
                    contentDiv.innerHTML = '<div class="loading">${t('preview.pdfError')}</div>';
                  };
                  
                  contentDiv.appendChild(object);
                } else if (fileType.match(/\\.(jpg|jpeg|png|gif)$/i)) {
                  // 图片预览
                  const img = document.createElement('img');
                  img.src = fileUrl;
                  img.onload = function() {
                    console.log('Image loaded');
                  };
                  img.onerror = function() {
                    contentDiv.innerHTML = '<div class="loading">${t('preview.imgError')}</div>';
                  };
                  contentDiv.appendChild(img);
                } else if (fileType === '.txt') {
                  // 文本文件预览
                  fetch(fileUrl)
                  .then(response => response.text())
                  .then(text => {
                    const pre = document.createElement('pre');
                    pre.textContent = text;
                    contentDiv.appendChild(pre);
                  })
                  .catch(error => {
                    console.error('Text load failed:', error);
                    contentDiv.innerHTML = '<div class="loading">${t('preview.txtError')}</div>';
                  });
                } else {
                  // 其他文档类型，尝试使用object标签预览
                  const object = document.createElement('object');
                  object.data = fileUrl;
                  object.style.width = '100%';
                  object.style.height = '100%';
                  
                  object.onerror = function() {
                    contentDiv.innerHTML = '<div class="loading">${t('preview.unsupported')}</div>';
                  };
                  
                  contentDiv.appendChild(object);
                }
              }
              
              // 页面加载完成后初始化预览
              window.onload = initPreview;
            <\/script>
          </body>
          </html>
        `)
        previewWindow.document.close()
      }
    }
    // 检查attachment.file是否存在
    if (attachment.file) {
      reader.readAsDataURL(attachment.file)
    } else {
      // 如果file不存在，直接显示错误信息
      const previewWindow = window.open('', '_blank', 'width=1000,height=800')
      if (previewWindow) {
        previewWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>${t('preview.failedTitle')}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
              }
              .error-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                margin: 0 auto;
              }
              .error {
                font-size: 18px;
                color: #e74c3c;
                margin-bottom: 20px;
              }
              .btn {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                text-decoration: none;
                font-size: 14px;
                margin: 5px;
                display: inline-block;
              }
              .btn:hover {
                background-color: #2980b9;
              }
            </style>
          </head>
          <body>
            <div class="error-container">
              <h1>${t('preview.failedTitle')}</h1>
              <div class="error">${t('preview.linkExpired')}</div>
              <br>
              <a href="${attachment.url || attachment.name}" download="${attachment.name}" class="btn">${t('preview.download')}</a>
              <br><br>
              <button class="btn" onclick="window.close()">${t('preview.close')}</button>
            </div>
          </body>
          </html>
        `)
        previewWindow.document.close()
      }
    }
  } else {
    // 对于不可预览的文件，直接下载
    downloadAttachment(attachment)
  }
}

// 下载附件
const downloadAttachment = (attachment) => {
  // 创建一个临时的a标签用于下载
  const link = document.createElement('a')
  link.href = attachment.url
  link.download = attachment.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取所有模块
const modules = computed(() => userStore.modules)

const handleSubmit = async () => {
  let hasTitle = !!formData.value.title
  let hasAuthor = !!formData.value.author
  
  let hasAbstract = false
  if (typeof formData.value.abstract === 'string') {
    hasAbstract = !!formData.value.abstract && formData.value.abstract.replace(/<[^>]*>/g, '').trim() !== ''
  } else if (formData.value.abstract && formData.value.abstract.ops) {
    hasAbstract = formData.value.abstract.ops.some(op => op.insert && typeof op.insert === 'string' && op.insert.trim() !== '')
  }
  
  const hasAttachments = formData.value.attachments && formData.value.attachments.length > 0
  
  if (!hasTitle || !hasAuthor || !hasAbstract || !hasAttachments) {
    error.value = t('submit.errors.incomplete') || 'Please fill in Title, Author, Abstract, and attach manuscript files.'
    return
  }
  
  submitting.value = true
  error.value = ''
  success.value = ''
  
  try {
    const convertToHTML = (content) => {
      if (typeof content === 'string') return content
      return ''
    }
    
    const fd = new FormData()
    
    fd.append('title', formData.value.title)
    fd.append('article_type', 'Original Research')
    
    const authorArray = [{
      name: formData.value.author,
      is_first: true,
      is_corresponding: true,
      email: userStore.userInfo?.email || ''
    }]
    fd.append('authors', JSON.stringify(authorArray))
    
    fd.append('abstract', convertToHTML(formData.value.abstract))
    fd.append('keywords', formData.value.keywords)
    
    const moduleValue = formData.value.modules.includes('all') ? 'Others' : formData.value.modules.join(',')
    fd.append('subject', moduleValue)
    
    if (formData.value.attachments && formData.value.attachments.length > 0) {
      formData.value.attachments.forEach(att => {
        fd.append('file', att.file)
      })
    }
    
    const response = await manuscriptStore.submitManuscript(fd)
    
    console.log(`Successfully created manuscript ID: ${response.manuscript_id}, Status: ${response.status}`)
    
    success.value = t('submit.successMessage') || 'Manuscript submitted successfully! Waiting for initial review.'
    toastStore.add({ message: success.value, type: 'success' })
    
    setTimeout(() => {
      formData.value = {
        title: '',
        author: userStore.user?.username || '',
        abstract: '',
        keywords: '',
        content: '',
        modules: ['all'],
        attachments: []
      }
      success.value = ''
      router.push('/author/dashboard')
    }, 2000)
  } catch (err) {
    console.error('Submission Error:', err)
    error.value = err.response?.data?.detail || err.message || 'Submission failed. Please try again later.'
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/author/dashboard')
}
</script>

<template>
  <div class="main-submit-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'author-submit'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />
    
    <!-- 主内容 -->
    <main class="main-content">
      <div class="submit-form-wrapper">
        <!-- 投稿须知页面 -->
        <template v-if="route.path === '/admin/submission-rules'">
          <h2 class="submit-title">{{ t('submit.title') }}</h2>
          
          <div class="rules-content">
            <div class="rules-section">
              <h3 class="section-subtitle">{{ t('submit.formatReq') }}</h3>
              <ul class="rules-list">
                <li>{{ t('submit.rules.format.title') }}</li>
                <li>{{ t('submit.rules.format.author') }}</li>
                <li>{{ t('submit.rules.format.abstract') }}</li>
                <li>{{ t('submit.rules.format.keywords') }}</li>
                <li>{{ t('submit.rules.format.content') }}</li>
                <li>{{ t('submit.rules.format.attachment') }}</li>
                <li>{{ t('submit.rules.format.naming') }}</li>
                <li>{{ t('submit.rules.format.images') }}</li>
              </ul>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">{{ t('submit.copyrightReq') }}</h3>
              <ul class="rules-list">
                <li>{{ t('submit.rules.copyright.original') }}</li>
                <li>{{ t('submit.rules.copyright.noplagiarism') }}</li>
                <li>{{ t('submit.rules.copyright.rights') }}</li>
                <li>{{ t('submit.rules.copyright.confidential') }}</li>
                <li>{{ t('submit.rules.copyright.legal') }}</li>
                <li>{{ t('submit.rules.copyright.rejection') }}</li>
              </ul>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">{{ t('submit.rules.flow.title') }}</h3>
              <ol class="rules-list">
                <li>{{ t('submit.rules.flow.step1') }}</li>
                <li>{{ t('submit.rules.flow.step2') }}</li>
                <li>{{ t('submit.rules.flow.step3') }}</li>
                <li>{{ t('submit.rules.flow.step4') }}</li>
                <li>{{ t('submit.rules.flow.step5') }}</li>
                <li>{{ t('submit.rules.flow.step6') }}</li>
                <li>{{ t('submit.rules.flow.step7') }}</li>
                <li>{{ t('submit.rules.flow.step8') }}</li>
                <li>{{ t('submit.rules.flow.step9') }}</li>
              </ol>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">{{ t('submit.rules.review.title') }}</h3>
              <ol class="rules-list">
                <li>{{ t('submit.rules.review.step1') }}</li>
                <li>{{ t('submit.rules.review.step2') }}</li>
                <li>{{ t('submit.rules.review.step3') }}</li>
                <li>{{ t('submit.rules.review.step4') }}</li>
                <li>{{ t('submit.rules.review.step5') }}</li>
                <li>{{ t('submit.rules.review.step6') }}</li>
              </ol>
            </div>
            
            <div class="rules-actions">
              <button class="btn btn-primary" @click="router.push('/admin/author-submit')">
                {{ t('submit.actions.start') }}
              </button>
              <button class="btn btn-secondary" @click="goBack">
                {{ t('submit.actions.back') }}
              </button>
            </div>
          </div>
        </template>
        
        <!-- 在线投稿表单 -->
        <template v-else>
          <h2 class="submit-title">{{ t('submit.formTitle') }}</h2>
          
          <div v-if="error" class="alert error">{{ error }}</div>
          <div v-if="success" class="alert success">{{ success }}</div>
          
          <form class="submit-form">
            <div class="form-section">
              <h3 class="section-subtitle">{{ t('submit.title') }}</h3>
              
              <div class="form-group">
                <label for="title">{{ t('submit.articleTitle') }} <span class="required">*</span></label>
                <input 
                  type="text" 
                  id="title" 
                  v-model="formData.title" 
                  :placeholder="t('submit.articleTitle')"
                  required
                  :disabled="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="author">{{ t('submit.author') }} <span class="required">*</span></label>
                <input 
                  type="text" 
                  id="author" 
                  v-model="formData.author" 
                  :placeholder="t('submit.author')"
                  required
                  :disabled="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="keywords">{{ t('submit.keywords') }}</label>
                <input 
                  type="text" 
                  id="keywords" 
                  v-model="formData.keywords" 
                  :placeholder="t('submit.keywordsPlaceholder')"
                  :disabled="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="modules">{{ t('submit.module') }}</label>
                <div class="module-checkboxes">
                  <label class="module-checkbox">
                    <input 
                      type="checkbox" 
                      id="module-all" 
                      name="modules" 
                      v-model="formData.modules" 
                      value="all" 
                      :disabled="submitting"
                    >
                    <span>{{ t('directory.allModules') }}</span>
                  </label>
                  <label class="module-checkbox" v-for="module in modules" :key="module">
                    <input 
                      type="checkbox" 
                      :id="`module-${module}`" 
                      name="modules" 
                      v-model="formData.modules" 
                      :value="module" 
                      :disabled="submitting"
                    >
                    <span>{{ module }}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3 class="section-subtitle">{{ t('submit.content') }}</h3>
              
              <div class="form-group">
                <label for="abstract">{{ t('submit.abstract') }} <span class="required">*</span></label>
                <QuillEditor 
                  id="abstract"
                  v-model:content="formData.abstract"
                  contentType="html"
                  theme="snow"
                  toolbar="minimal"
                  :readOnly="submitting"
                />
              </div>
              
              <div class="form-group">
                <label for="content">{{ t('submit.content') }}</label>
                <QuillEditor 
                  id="content"
                  v-model:content="formData.content"
                  contentType="html"
                  theme="snow"
                  toolbar="essential"
                  :readOnly="submitting"
                />
              </div>
              
              <div class="form-group">
                <label>{{ t('submit.attachments') }}</label>
                <div class="file-upload-container">
                  <input 
                    type="file" 
                    id="attachment-upload" 
                    class="file-input" 
                    @change="handleFileUpload" 
                    accept=".doc,.docx,.pdf"
                  />
                  <div class="upload-trigger" @click="triggerFileUpload">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">{{ t('submit.upload') }}</div>
                    <div class="upload-hint">{{ t('submit.uploadHint') }}</div>
                  </div>
                </div>
                
                <!-- 附件列表 -->
                <div v-if="formData.attachments.length > 0" class="attachments-list">
                  <div v-for="attachment in formData.attachments" :key="attachment.id" class="attachment-item">
                    <div class="attachment-info">
                      <span class="attachment-icon">📄</span>
                      <span class="attachment-name">{{ attachment.name }}</span>
                      <span class="attachment-size">({{ formatFileSize(attachment.size) }})</span>
                    </div>
                    <div class="attachment-actions">
                      <button type="button" class="btn-icon view" @click="previewAttachment(attachment)" :title="t('preview.preview')">👁️</button>
                      <button type="button" class="btn-icon delete" @click="removeAttachment(attachment.id)" :title="t('common.delete')">🗑️</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="goBack" :disabled="submitting">
                {{ t('common.cancel') }}
              </button>
              <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
                {{ submitting ? t('submit.submitting') : t('submit.submit') }}
              </button>
            </div>
          </form>
        </template>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main-submit-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.submit-form-wrapper {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 40px;
}

.submit-title {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #3498db;
  text-align: center;
}

.rules-content {
  color: #34495e;
}

.rules-section {
  margin-bottom: 30px;
}

.section-subtitle {
  font-size: 18px;
  color: #2c3e50;
  margin-bottom: 15px;
  font-weight: 600;
}

.rules-list {
  padding-left: 20px;
  line-height: 1.8;
}

.rules-list li {
  margin-bottom: 8px;
}

.rules-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.submit-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 30px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.required {
  color: #e74c3c;
  margin-left: 4px;
}

input[type="text"],
select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input[type="text"]:focus,
select:focus {
  border-color: #3498db;
  outline: none;
}

.module-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.module-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.file-upload-container {
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  transition: border-color 0.3s;
  background: white;
}

.file-upload-container:hover {
  border-color: #3498db;
}

.file-input {
  display: none;
}

.upload-trigger {
  cursor: pointer;
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 16px;
  color: #3498db;
  font-weight: 500;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.attachments-list {
  margin-top: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: white;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #ebeef5;
}

.attachment-item:last-child {
  border-bottom: none;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.attachment-name {
  font-size: 14px;
  color: #606266;
}

.attachment-size {
  font-size: 12px;
  color: #909399;
}

.attachment-actions {
  display: flex;
  gap: 10px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.btn-icon:hover {
  background-color: #f5f7fa;
}

.btn-icon.delete:hover {
  color: #e74c3c;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #909399;
  color: white;
}

.btn-secondary:hover {
  background-color: #82848a;
}

.btn-secondary:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

.alert {
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.error {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fde2e2;
}

.success {
  background-color: #f0f9eb;
  color: #67c23a;
  border: 1px solid #e1f3d8;
}

:deep(.ql-editor) {
  min-height: 150px;
}
</style>