<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

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
      error.value = '文件大小不能超过10MB'
      return
    }
    
    // 检查文件类型
    const allowedTypes = ['.doc', '.docx', '.pdf', '.txt']
    const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`
    if (!allowedTypes.includes(fileExtension)) {
      error.value = '只支持上传.doc, .docx, .pdf, .txt文件'
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
            <title>预览：${attachment.name}</title>
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
                <button class="btn btn-primary" onclick="downloadFile()">下载文件</button>
                <button class="btn btn-secondary" onclick="closePreview()">关闭预览</button>
              </div>
            </div>
            <div class="preview-container">
              <div id="preview-content" class="preview-content">
                <div class="loading">正在加载预览...</div>
              </div>
            </div>
            <div class="file-info">
              文件类型: ${fileExtension.substring(1).toUpperCase()} | 大小: ${formatFileSize(attachment.size)}
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
                    contentDiv.innerHTML = '<div class="loading">PDF预览失败，建议直接下载查看</div>';
                  };
                  
                  contentDiv.appendChild(object);
                } else if (fileType.match(/\\.(jpg|jpeg|png|gif)$/i)) {
                  // 图片预览
                  const img = document.createElement('img');
                  img.src = fileUrl;
                  img.onload = function() {
                    console.log('图片加载完成');
                  };
                  img.onerror = function() {
                    contentDiv.innerHTML = '<div class="loading">图片预览失败，建议直接下载查看</div>';
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
                      console.error('文本加载失败:', error);
                      contentDiv.innerHTML = '<div class="loading">文本预览失败，建议直接下载查看</div>';
                    });
                } else {
                  // 其他文档类型，尝试使用object标签预览
                  const object = document.createElement('object');
                  object.data = fileUrl;
                  object.style.width = '100%';
                  object.style.height = '100%';
                  
                  object.onerror = function() {
                    contentDiv.innerHTML = '<div class="loading">该文件类型无法预览，建议直接下载查看</div>';
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
            <title>预览：${attachment.name}</title>
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
              <h1>预览失败</h1>
              <div class="error">预览链接已失效，您可以重新上传文件或直接下载</div>
              <br>
              <a href="${attachment.url || attachment.name}" download="${attachment.name}" class="btn">下载文件</a>
              <br><br>
              <button class="btn" onclick="window.close()">关闭窗口</button>
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
  // 表单验证 - 处理Delta对象和HTML标签
  const hasTitle = !!formData.value.title
  const hasAuthor = !!formData.value.author
  
  // 处理摘要 - 可能是Delta对象或HTML字符串
  let hasAbstract = false
  if (typeof formData.value.abstract === 'string') {
    hasAbstract = !!formData.value.abstract && formData.value.abstract.replace(/<[^>]*>/g, '').trim() !== ''
  } else if (formData.value.abstract && formData.value.abstract.ops) {
    hasAbstract = formData.value.abstract.ops.some(op => op.insert && typeof op.insert === 'string' && op.insert.trim() !== '')
  }
  
  // 处理正文 - 可能是Delta对象或HTML字符串
  let hasContent = false
  if (typeof formData.value.content === 'string') {
    hasContent = !!formData.value.content && formData.value.content.replace(/<[^>]*>/g, '').trim() !== ''
  } else if (formData.value.content && formData.value.content.ops) {
    hasContent = formData.value.content.ops.some(op => op.insert && typeof op.insert === 'string' && op.insert.trim() !== '')
  }
  
  // 检查是否有附件
  const hasAttachments = formData.value.attachments && formData.value.attachments.length > 0
  
  if (!hasTitle || !hasAuthor || !hasAbstract || (!hasContent && !hasAttachments)) {
    error.value = '请填写完整的投稿信息，正文和附件至少需要填写一项'
    return
  }
  
  submitting.value = true
  error.value = ''
  success.value = ''
  
  try {
    // 编辑器已配置contentType="html"，直接返回HTML字符串
    const convertToHTML = (content) => {
      if (typeof content === 'string') {
        return content
      }
      return ''
    }
    
    // 创建新期刊对象
    const newJournal = {
      id: Date.now().toString(),
      title: formData.value.title,
      author: formData.value.author,
      abstract: convertToHTML(formData.value.abstract),
      keywords: formData.value.keywords.split(',').map(k => k.trim()).filter(Boolean),
      content: convertToHTML(formData.value.content),
      module: formData.value.modules.length > 0 && formData.value.modules.includes('all') ? '其他' : formData.value.modules.filter(m => m !== 'all'),
      status: '待审核', // 初始状态为待审核
      reviewStage: '初审', // 初始审稿阶段为初审
      date: new Date().toISOString().split('T')[0],
      viewCount: 0,
      attachments: formData.value.attachments.map(att => ({
        id: att.id,
        name: att.name,
        type: att.type,
        size: att.size,
        url: att.url
      }))
    }
    
    // 调用userStore提供的addJournal方法
    userStore.addJournal(newJournal)
    
    // 显示成功消息
    success.value = '投稿成功！您的稿件已提交至审核队列'
    
    // 清空表单并跳转
    setTimeout(() => {
      formData.value = {
        title: '',
        author: userStore.user?.username || '',
        abstract: '',
        keywords: '',
        content: '',
        modules: ['all']
      }
      success.value = ''
      router.push('/admin/author-dashboard')
    }, 2000)
  } catch (err) {
    error.value = '投稿失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/admin/author-dashboard')
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
          <h2 class="submit-title">投稿须知</h2>
          
          <div class="rules-content">
            <div class="rules-section">
              <h3 class="section-subtitle">格式要求</h3>
              <ul class="rules-list">
                <li><strong>标题格式：</strong>简洁明了，准确反映论文核心内容</li>
                <li><strong>作者信息：</strong>请填写真实姓名，多个作者之间用逗号分隔，顺序为第一作者、第二作者等</li>
                <li><strong>摘要要求：</strong>200-500字，概述论文的研究目的、方法、结果和结论</li>
                <li><strong>关键词：</strong>3-5个，用逗号分隔，反映论文的核心内容</li>
                <li><strong>正文要求：</strong>请将完整论文作为附件上传，论文应包含引言、方法、结果、讨论和结论等部分，参考文献格式规范</li>
                <li><strong>附件格式：</strong>支持上传.doc、.docx、.pdf格式的论文文件，单个文件大小不超过10MB</li>
                <li><strong>附件命名：</strong>建议以"作者姓名-论文标题"格式命名附件，避免使用特殊字符</li>
                <li><strong>图片要求：</strong>论文中的图片应清晰可读，分辨率不低于300dpi，图片版权归作者所有</li>
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
                <li>登录期刊投稿平台作者后台</li>
                <li>进入在线投稿页面，填写论文基本信息</li>
                <li>填写论文摘要，概述研究目的、方法、结果和结论</li>
                <li>上传完整论文附件，支持.doc、.docx、.pdf格式</li>
                <li>选择论文所属模块，输入关键词</li>
                <li>提交投稿，系统自动生成投稿ID</li>
                <li>等待审稿结果，可通过个人中心查看稿件状态</li>
                <li>根据审稿意见修改论文（如需）</li>
                <li>论文发表，可在期刊目录中查看</li>
              </ol>
            </div>
            
            <div class="rules-section">
              <h3 class="section-subtitle">审稿流程</h3>
              <ol class="rules-list">
                <li>稿件提交后进入待审核状态</li>
                <li>系统自动分配到初审阶段</li>
                <li>审核员进行评审，给出评审意见</li>
                <li>根据审核结果，稿件进入下一阶段或返回修改</li>
                <li>最终审核通过后，稿件状态更新为已发表</li>
                <li>作者可在个人中心查看完整的审核记录</li>
              </ol>
            </div>
            
            <div class="rules-actions">
              <button class="btn btn-primary" @click="router.push('/admin/submit')">
                开始在线投稿
              </button>
              <button class="btn btn-secondary" @click="goBack">
                返回个人中心
              </button>
            </div>
          </div>
        </template>
        
        <!-- 在线投稿表单 -->
        <template v-else>
          <h2 class="submit-title">在线投稿</h2>
          
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
                <label for="modules">所属模块</label>
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
                    <span>全部</span>
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
              <h3 class="section-subtitle">论文内容</h3>
              
              <div class="form-group">
                <label for="abstract">摘要 <span class="required">*</span></label>
                <QuillEditor 
                  id="abstract"
                  v-model:content="formData.abstract"
                  contentType="html"
                  placeholder="请输入论文摘要"
                  :disabled="submitting"
                  :options="{
                    modules: {
                      toolbar: [
                        ['bold', 'italic', 'underline'],
                        [{ 'header': [1, 2, false] }]
                      ]
                    }
                  }"
                  style="height: 150px;"
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="content">正文 <span class="required">*</span></label>
                <textarea 
                  id="content"
                  v-model="formData.content"
                  placeholder="请输入论文正文"
                  :disabled="submitting"
                  style="height: 300px; width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: inherit; font-size: 14px; resize: vertical;"
                  required
                ></textarea>
                
                <!-- 自定义附件上传按钮 -->
                <div class="custom-attachment-container">
                  <button 
                    type="button"
                    class="custom-attachment-btn"
                    @click="triggerFileUpload"
                    :disabled="submitting"
                  >
                    <span class="attachment-icon">📎</span> 上传附件
                  </button>
                  <input 
                    type="file" 
                    id="attachment-upload" 
                    style="display: none;" 
                    accept=".doc,.docx,.pdf,.txt" 
                    @change="handleFileUpload"
                  />
                </div>
                
                <!-- 附件列表显示 -->
                <div v-if="formData.attachments && formData.attachments.length > 0" class="attachments-list-container">
                  <h4 class="attachments-list-title">已上传附件：</h4>
                  <div class="attachments-list">
                    <div 
                      v-for="attachment in formData.attachments" 
                      :key="attachment.id"
                      class="attachment-item-display"
                    >
                      <div class="attachment-info">
                        <button 
                          type="button"
                          class="attachment-preview-btn"
                          @click="previewAttachment(attachment)"
                          :disabled="submitting"
                        >
                          <span class="attachment-icon">👁️</span> 预览
                        </button>
                        <button 
                          type="button"
                          class="attachment-download-btn"
                          @click="downloadAttachment(attachment)"
                          :disabled="submitting"
                        >
                          <span class="attachment-icon">📥</span> 下载
                        </button>
                      </div>
                      <div class="attachment-details">
                        <span class="attachment-name">{{ attachment.name }}</span>
                        <span class="attachment-size">({{ formatFileSize(attachment.size) }})</span>
                      </div>
                      <button 
                        type="button"
                        class="attachment-delete-btn"
                        @click="removeAttachment(attachment.id)"
                        :disabled="submitting"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
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
  display: inline-block;
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

/* 富文本编辑器样式 */
.ql-container.ql-snow {
  border-radius: 0 0 5px 5px;
  border: 1px solid #ddd;
  min-height: 150px;
}

.ql-toolbar.ql-snow {
  border-radius: 5px 5px 0 0;
  border: 1px solid #ddd;
  border-bottom: none;
  background-color: #f8f9fa;
}

/* 模块多选框样式 */
.module-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.5rem;
}

.module-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  transition: all 0.3s ease;
  background: white;
}

.module-checkbox:hover:not(:has(input:disabled)) {
  border-color: #3498db;
  background: #f0f8ff;
}

.module-checkbox input[type="checkbox"] {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.module-checkbox input[type="checkbox"]:checked + span {
  font-weight: 600;
  color: #3498db;
}

.module-checkbox input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.module-checkbox input[type="checkbox"]:disabled + span {
  color: #999;
  cursor: not-allowed;
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

/* 附件样式 */
.attachment-item {
  display: inline-block;
  margin: 5px 0;
  padding: 8px 12px;
  background-color: #f0f8ff;
  border: 1px solid #b3d9ff;
  border-radius: 5px;
  width: 100%;
  box-sizing: border-box;
}

.attachment-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #1e90ff;
  font-size: 14px;
}

.attachment-link:hover {
  text-decoration: underline;
}

.attachment-icon {
  margin-right: 8px;
  font-size: 16px;
}

.attachment-name {
  flex: 1;
  font-weight: 500;
}

.attachment-size {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

/* 自定义附件上传按钮样式 */
.custom-attachment-container {
  display: flex;
  justify-content: flex-start;
  margin-top: 1rem;
  gap: 1rem;
}

.custom-attachment-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.custom-attachment-btn:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.custom-attachment-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.custom-attachment-btn .attachment-icon {
  font-size: 1rem;
}

/* 附件列表样式 */
.attachments-list-container {
  margin-top: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 5px;
  padding: 1rem;
}

.attachments-list-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.attachment-item-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.8rem;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  transition: all 0.3s ease;
  flex-wrap: wrap;
  gap: 1rem;
}

.attachment-item-display:hover {
  border-color: #3498db;
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.1);
}

.attachment-info {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.attachment-preview-btn,
.attachment-download-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 3px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.attachment-preview-btn {
  background-color: #28a745;
  color: white;
}

.attachment-preview-btn:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.attachment-download-btn {
  background-color: #3498db;
  color: white;
}

.attachment-download-btn:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
}

.attachment-preview-btn:disabled,
.attachment-download-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.attachment-details {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 1;
  min-width: 200px;
  overflow: hidden;
}

.attachment-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.attachment-size {
  font-size: 0.85rem;
  color: #6c757d;
  white-space: nowrap;
}

.attachment-delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 3px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.attachment-delete-btn:hover:not(:disabled) {
  background-color: rgba(220, 53, 69, 0.1);
  transform: scale(1.1);
}

.attachment-delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  
  .module-checkboxes {
    flex-direction: column;
  }
  
  .module-checkbox {
    width: 100%;
  }
}
</style>