<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import { useToastStore } from '../stores/toast'
import Navigation from '../components/Navigation.vue'
import { stripHtmlTags } from '../utils/helpers'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()
const journalId = computed(() => route.params.id)

const goBack = () => {
  router.back()
  setTimeout(() => {
    directoryStore.openDirectory()
  }, 100)
}

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// 获取当前期刊详情
const journal = computed(() => {
  const found = userStore.journals.find(j => {
    // 转换id类型为字符串进行比较，解决类型不匹配问题
    return String(j.id) === String(journalId.value)
  })
  
  if (!found) return null
  
  // 为新稿件提供默认值，确保详情页能正常显示
  return {
    // 基础信息
    id: found.id,
    title: found.title || 'Untitled Manuscript',
    author: found.author || 'Unknown Author',
    date: found.date || found.submissionDate || new Date().toISOString().split('T')[0],
    status: found.status || 'pending_initial_review',
    module: found.module || 'Others',
    
    // 期刊元数据（新稿件可能没有）
    volume: found.volume || 'NONE',
    issue: found.issue || 'NONE',
    pages: found.pages || 'NONE',
    articleType: found.articleType || 'Original Article',
    doi: found.doi || 'NONE',
    doiUrl: found.doiUrl || '',
    onlineDate: found.onlineDate || found.publicationDate || found.date || 'Pending',
    
    // 作者信息
    correspondingAuthor: found.correspondingAuthor || null,
    affiliations: found.affiliations || null,
    
    // 摘要和关键词
    abstract: found.abstract || 'No abstract available.',
    keywords: found.keywords || [],
    
    // 结构化摘要字段
    background: found.background || null,
    methods: found.methods || null,
    findings: found.findings || null,
    interpretation: found.interpretation || null,
    funding: found.funding || 'None',
    
    // 正文内容
    introduction: found.introduction || null,
    methodsDetail: found.methodsDetail || null,
    results: found.results || null,
    discussion: found.discussion || null,
    content: found.content || null,
    
    // 文末声明
    authorContributions: found.authorContributions || null,
    declarationOfInterests: found.declarationOfInterests || 'None declared.',
    dataSharing: found.dataSharing || 'Data sharing not applicable.',
    acknowledgments: found.acknowledgments || null,
    fundingDetail: found.fundingDetail || found.funding || 'None',
    references: found.references || null,
    
    // 附件
    attachments: found.attachments || [],
    
    // 审核历史
    reviewHistory: found.reviewHistory || found.reviews || [],
    
    // 其他字段
    viewCount: found.viewCount || 0,
    reviewStage: found.reviewStage || 'Initial Review',
    submissionDate: found.submissionDate || found.date || new Date().toISOString().split('T')[0],
    ...found
  }
})

// 获取当前用户
const user = computed(() => userStore.user)

// 处理关键词列表（支持字符串和数组格式）
const keywordsList = computed(() => {
  if (!journal.value) return []
  const keywords = journal.value.keywords
  if (!keywords) return []
  if (Array.isArray(keywords)) {
    return keywords.filter(k => k && k.trim())
  }
  if (typeof keywords === 'string') {
    return keywords.split(',').map(k => k.trim()).filter(k => k)
  }
  return []
})

// 判断是否有结构化摘要
const hasStructuredAbstract = computed(() => {
  if (!journal.value) return false
  return !!(journal.value.background || journal.value.methods || journal.value.findings || journal.value.interpretation)
})

// Blind Review Logic (Mock)
const isBlindReview = ref(true)

// 预览附件
const previewAttachment = (attachment) => {
  if (!attachment || !attachment.name) return
  const fileExtension = `.${attachment.name.split('.').pop().toLowerCase()}`
  const previewableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
  
  if (previewableExtensions.includes(fileExtension)) {
    // 使用fetch获取文件内容并转换为data URL
    fetch(attachment.url)
      .then(response => response.blob())
      .then(blob => {
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
                    link.href = '${attachment.url}';
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
                        console.log('图片加载完成');
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
                          console.error('文本加载失败:', error);
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
              <\/body>
              <\/html>
            `)
            previewWindow.document.close()
          }
        }
        reader.readAsDataURL(blob)
      })
      .catch(error => {
        console.error('预览失败:', error)
        // 如果获取文件内容失败，直接下载
        handleDownloadAttachment(attachment)
      })
  } else {
    // 对于不可预览的文件，直接下载
    handleDownloadAttachment(attachment)
  }
}

// 下载附件
const handleDownloadAttachment = (attachment) => {
  // 创建一个临时的a标签用于下载
  const link = document.createElement('a')
  link.href = attachment.url
  link.download = attachment.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 检查是否有附件可以下载
const hasAttachments = computed(() => {
  return journal.value && journal.value.attachments && journal.value.attachments.length > 0
})

// 检查是否有导出权限（保留原有逻辑，用于向后兼容）
const canExport = computed(() => {
  if (!journal.value || !user.value) return false
  return true // 简化处理，默认允许导出
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleDownloadPDF = () => {
  // Mock PDF download
  console.log('Downloading PDF...')
  if (hasAttachments.value) {
      // Find a PDF attachment if possible
      const pdf = journal.value.attachments.find(a => a.name && a.name.toLowerCase().endsWith('.pdf'))
      if (pdf) {
          handleDownloadAttachment(pdf)
      } else {
           handleDownloadAttachment(journal.value.attachments[0])
      }
  } else {
      toastStore.add({ message: 'PDF not available for this demo article.', type: 'warning' })
  }
}

const handleCite = () => {
    toastStore.add({ message: `Citation: ${journal.value.author}. "${journal.value.title}". ${journal.value.date}.`, type: 'info' })
}

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<template>
  <div class="journal-detail-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'journal'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />
    
    <div v-if="journal" class="journal-detail-content">
      <!-- 页面顶部 -->
      <header class="journal-header">
        <div class="header-info">
          <div class="journal-info">
            <span class="journal-name">{{ t('nav.logo') }}</span> | 
            <span class="volume-issue">{{ t('journalDetail.header.volume') }} {{ journal.volume || 'X' }}, {{ t('journalDetail.header.issue') }} {{ journal.issue || 'X' }}</span> | 
            <span class="date-year">{{ journal.date || 'Date, Year' }}</span> | 
            <span class="pages">{{ t('journalDetail.header.pages') }} {{ journal.pages || 'X–X' }}</span>
          </div>
          <div class="article-meta">
            <span class="article-type">{{ journal.articleType || 'Original Article' }}</span> | 
            <span class="doi">DOI: {{ journal.doi || '10.1234/jsp.2026.xxxx' }}</span>
          </div>
          <div class="online-date">
            {{ t('journalDetail.header.publishedOnline') }}: {{ journal.onlineDate || 'Month Day, Year' }} | 
            <a v-if="journal.doiUrl" :href="journal.doiUrl" target="_blank">{{ journal.doiUrl }}</a>
            <span v-else>NONE</span>
          </div>
        </div>
      </header>

      <!-- Floating Action Box -->
      <div class="floating-actions">
        <button class="btn-float btn-download" @click="handleDownloadPDF">
          {{ t('journalDetail.actions.downloadPdf') }}
        </button>
        <a href="#" class="link-cite" @click.prevent="handleCite">{{ t('journalDetail.actions.cite') }}</a>
      </div>

      <!-- 标题区 -->
      <section class="title-section">
        <h1 class="journal-title">{{ journal.title }}</h1>
        <div class="author-list">
          <span class="authors">{{ journal.author }}</span>
        </div>
        <div class="corresponding-author" v-if="journal.correspondingAuthor">
          *{{ t('journalDetail.header.correspondence') }}: {{ journal.correspondingAuthor }}
        </div>
        <div class="author-affiliations" v-if="journal.affiliations">
          <h3>{{ t('journalDetail.header.affiliations') }}</h3>
          <div class="affiliation-list">
            <span v-for="(affiliation, index) in journal.affiliations" :key="index" class="affiliation-item">
              {{ index + 1 }}: {{ affiliation }}
            </span>
          </div>
        </div>
      </section>

      <!-- 摘要区 -->
      <section class="abstract-section">
        <h2 class="section-title">{{ t('journalDetail.sections.abstract') }}</h2>
        <!-- 如果有结构化摘要字段，显示结构化摘要 -->
        <div class="structured-abstract" v-if="hasStructuredAbstract">
          <div class="abstract-item" v-if="journal.background">
            <strong>{{ t('journalDetail.abstract.background') }}:</strong> {{ journal.background }}
          </div>
          <div class="abstract-item" v-if="journal.methods">
            <strong>{{ t('journalDetail.abstract.methods') }}:</strong> {{ journal.methods }}
          </div>
          <div class="abstract-item" v-if="journal.findings">
            <strong>{{ t('journalDetail.abstract.findings') }}:</strong> {{ journal.findings }}
          </div>
          <div class="abstract-item" v-if="journal.interpretation">
            <strong>{{ t('journalDetail.abstract.interpretation') }}:</strong> {{ journal.interpretation }}
          </div>
          <div class="abstract-item">
            <strong>{{ t('journalDetail.abstract.funding') }}:</strong> {{ journal.funding || 'None' }}
          </div>
        </div>
        <!-- 否则显示简单摘要 -->
        <div class="simple-abstract" v-else>
          <div class="abstract-content" v-html="journal.abstract || 'No abstract available.'"></div>
        </div>
      </section>

      <!-- 关键词 -->
      <section class="keywords-section" v-if="keywordsList.length > 0">
        <h2 class="section-title">{{ t('journalDetail.sections.keywords') }}</h2>
        <div class="keywords-list">
          <span 
            v-for="(keyword, index) in keywordsList" 
            :key="index" 
            class="keyword-tag"
          >
            {{ keyword }}
          </span>
        </div>
      </section>

      <!-- 正文结构 -->
      <section class="main-text">
        <h2 class="section-title">{{ t('journalDetail.sections.mainText') }}</h2>
        
        <!-- 如果有简单内容字段，直接显示 -->
        <div v-if="journal.content" class="text-section">
          <div class="section-content content-body" v-html="journal.content"></div>
        </div>
        
        <!-- 否则显示结构化正文 -->
        <template v-else>
          <!-- Introduction -->
          <div class="text-section" v-if="journal.introduction">
            <h3 class="section-subtitle">{{ t('journalDetail.mainText.introduction') }}</h3>
            <div class="section-content" v-html="journal.introduction"></div>
          </div>
          
          <!-- Methods -->
          <div class="text-section" v-if="journal.methodsDetail">
            <h3 class="section-subtitle">{{ t('journalDetail.mainText.methods') }}</h3>
            <div class="section-content" v-html="journal.methodsDetail"></div>
          </div>
          
          <!-- Results -->
          <div class="text-section" v-if="journal.results">
            <h3 class="section-subtitle">{{ t('journalDetail.mainText.results') }}</h3>
            <div class="section-content" v-html="journal.results"></div>
          </div>
          
          <!-- Discussion -->
          <div class="text-section" v-if="journal.discussion">
            <h3 class="section-subtitle">{{ t('journalDetail.mainText.discussion') }}</h3>
            <div class="section-content" v-html="journal.discussion"></div>
          </div>
        </template>
      </section>

      <!-- 文末声明 -->
      <section class="end-matter">
        <h2 class="section-title">{{ t('journalDetail.sections.endMatter') }}</h2>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.contributions') }}</h3>
          <p>{{ journal.authorContributions || "Authors' contributions not specified." }}</p>
        </div>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.interests') }}</h3>
          <p>{{ journal.declarationOfInterests || "None declared." }}</p>
        </div>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.dataSharing') }}</h3>
          <p>{{ journal.dataSharing || "Data sharing not applicable." }}</p>
        </div>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.acknowledgments') }}</h3>
          <p>{{ journal.acknowledgments || "Acknowledgments not specified." }}</p>
        </div>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.funding') }}</h3>
          <p>{{ journal.fundingDetail || journal.funding || "None" }}</p>
        </div>
        
        <div class="end-section">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.references') }}</h3>
          <div class="references-list">
            <p>{{ journal.references || "References not specified." }}</p>
          </div>
        </div>
        
        <!-- Supplementary Materials -->
        <div class="end-section" v-if="hasAttachments">
          <h3 class="section-subtitle">{{ t('journalDetail.endMatter.supplementary') }}</h3>
          <a href="#" class="link-supp" @click.prevent="previewAttachment(journal.attachments[0])">
            {{ t('journalDetail.actions.viewSupplementary') }}
          </a>
        </div>
      </section>

      <!-- 审核历史记录卡片 -->
      <section class="journal-review-history" v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
        <h2 class="section-title">
          {{ t('journalDetail.sections.reviewHistory') }}
          <span v-if="isBlindReview" class="blind-badge">{{ t('journalDetail.reviewHistory.blindBadge') }}</span>
        </h2>
        <div class="review-history-list">
          <div 
            v-for="(record, index) in journal.reviewHistory" 
            :key="index" 
            class="review-history-item"
          >
            <div class="review-history-header">
              <span class="review-stage">{{ record.stage || 'Review' }}:</span>
              <span class="review-status" :class="(record.status || 'unknown').toLowerCase()">{{ record.status || 'Pending' }}</span>
              <span class="review-date">{{ record.date }}</span>
              <span class="reviewer" v-if="isBlindReview">
                ({{ t('journalDetail.reviewHistory.reviewer') }} {{ index + 1 }} - [{{ t('journalDetail.reviewHistory.anonymized') }}])
              </span>
              <span class="reviewer" v-else>({{ record.reviewer }})</span>
            </div>
            <div class="review-comment" v-if="record.comment">
              <div v-if="isBlindReview" class="comment-content" v-html="record.comment.replace(/Reviewer Name/g, `[${t('journalDetail.reviewHistory.anonymized')}]`)"></div>
              <div v-else class="comment-content">{{ record.comment }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
    <!-- 未找到期刊 -->
    <div v-else class="no-journal card">
      <div class="no-journal-content">
        <div class="no-journal-icon">📄</div>
        <h2>{{ t('journalDetail.notFound.title') }}</h2>
        <p>{{ t('journalDetail.notFound.message') }}</p>
        <button class="back-btn" @click="goBack">{{ t('journalDetail.notFound.back') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全局容器 */
.journal-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  padding: 2rem 0;
  font-family: 'Times New Roman', Times, serif;
}

/* 主内容区域 */
.journal-detail-content {
  flex: 1;
  max-width: 900px; /* Readability width */
  margin: 0 auto;
  width: 100%;
  margin-top: 100px; /* 为固定导航栏留出空间 */
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: white;
  border-radius: 0;
  box-shadow: none;
  padding: 0 2rem;
  text-align: left;
}

/* 页面顶部 */
.journal-header {
  padding: 1rem 0;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.journal-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.online-date {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.online-date a {
  color: #e74c3c;
  text-decoration: none;
}

.online-date a:hover {
  text-decoration: underline;
}

/* 标题区 */
.title-section {
  margin: 1rem 0;
}

.journal-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 1rem 0;
  line-height: 1.3;
  text-align: left;
}

.author-list {
  margin-bottom: 0.5rem;
}

.authors {
  font-size: 1rem;
  color: #333;
  text-align: left;
}

.corresponding-author {
  font-size: 0.95rem;
  color: #666;
  margin-bottom: 0.5rem;
  text-align: left;
}

.author-affiliations {
  margin-top: 1rem;
  text-align: left;
}

.author-affiliations h3 {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.affiliation-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: #666;
}

/* 摘要区 */
.abstract-section {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  text-align: left;
}

.structured-abstract {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.95rem;
  line-height: 1.5;
  text-align: left;
}

.abstract-item {
  display: block;
  text-align: left;
}

.abstract-item strong {
  color: #333;
}

/* 关键词区 */
.keywords-section {
  margin: 1rem 0;
  text-align: left;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  text-align: left;
}

.keyword-tag {
  display: inline-block;
  background-color: #f0f0f0;
  color: #333;
  padding: 0.2rem 0.6rem;
  border-radius: 3px;
  font-size: 0.85rem;
  font-weight: normal;
}

/* 正文结构 */
.main-text {
  margin: 1rem 0;
  text-align: left;
}

.text-section {
  margin-bottom: 1.5rem;
  text-align: left;
}

.section-subtitle {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 0.5rem 0;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid #e0e0e0;
  text-align: left;
}

.section-content {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #333;
  text-align: left;
}

.section-content p {
  margin-bottom: 0.8rem;
  text-align: left;
}

/* 文末声明 */
.end-matter {
  margin: 1.5rem 0;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  text-align: left;
}

.end-section {
  margin-bottom: 1rem;
  text-align: left;
}

.end-section h3 {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.end-section p {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #666;
}

.references-list {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #666;
}

/* 审核历史记录 */
.journal-review-history {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
}

.review-history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-history-item {
  padding: 1rem;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
}

.review-history-header {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.95rem;
}

.review-stage {
  font-weight: bold;
  color: #333;
}

.review-status {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: bold;
}

.review-status.reviewed {
  background-color: #d4edda;
  color: #155724;
}

.review-date {
  color: #666;
}

.reviewer {
  color: #666;
  font-style: italic;
}

.review-comment {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
}

.blind-badge {
  font-size: 0.85rem;
  color: #666;
  font-weight: normal;
  margin-left: 1rem;
}

/* 章节标题通用样式 */
.section-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 1rem 0;
  padding-bottom: 0.3rem;
  border-bottom: 2px solid #e74c3c;
  text-align: left;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  border: none;
  margin-bottom: 1rem;
  text-align: left;
}

/* 头部卡片 */
.journal-detail-header {
  background: white;
  padding: 0;
  border: none;
  margin-bottom: 2rem;
}

/* 标题样式 */
.journal-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #333333; /* Journal Platform Dark Grey */
  margin: 0 0 1.5rem 0;
  line-height: 1.3;
  letter-spacing: -0.5px;
}

/* 元信息样式 */
.journal-meta {
  color: #7f8c8d;
  font-size: 0.95rem; /* Smaller, grey */
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.meta-item strong {
  color: #2c3e50;
  font-weight: 600;
}

/* 状态标签 */
.journal-status {
  padding: 0.5rem 1.25rem;
  border-radius: 24px;
  font-size: 0.95rem;
  font-weight: 600;
  text-align: center;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.journal-status::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.journal-status.accepted {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.journal-status.reviewing {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.journal-status.pending {
  background: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.journal-status.rejected {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

/* 模块标签 */
.module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.module-tag {
  display: inline-block;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.35rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* 附件样式 */
.attachments-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.attachments-title {
  font-size: 0.95rem;
  font-weight: 500;
  color: #2c3e50;
}

.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.8rem;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  gap: 1rem;
  width: 100%;
  transition: all 0.3s ease;
}

.attachment-item:hover {
  background-color: #f0f8ff;
  border-color: #b3d9ff;
  box-shadow: 0 2px 8px rgba(30, 144, 255, 0.1);
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.attachment-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.attachment-preview-btn,
.attachment-download-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.9rem;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.attachment-preview-btn {
  background-color: #28a745;
  color: white;
}

.attachment-preview-btn:hover {
  background-color: #218838;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
}

.attachment-download-btn {
  background-color: #3498db;
  color: white;
}

.attachment-download-btn:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
}

.attachment-preview-btn:active,
.attachment-download-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.module-tag:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 按钮样式 */
.back-btn, .export-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.75rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-decoration: none;
}

.back-btn {
  background: #667eea;
  color: white;
}

.back-btn:hover {
  background: #5a6fd8;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.export-btn {
  background: #2ecc71;
  color: white;
}

.export-btn:hover {
  background: #27ae60;
  box-shadow: 0 8px 24px rgba(46, 204, 113, 0.3);
}

.back-btn:active, .export-btn:active {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

/* 图标样式 */
.icon {
  font-size: 1.1rem;
}

/* 头部操作按钮容器 */
.header-actions {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

/* Floating Actions */
.floating-actions {
  position: fixed;
  top: 150px;
  right: calc(50% - 700px); /* Position to the right of content */
  width: 180px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  z-index: 100;
}

@media (max-width: 1400px) {
  .floating-actions {
    position: static;
    width: 100%;
    flex-direction: row;
    align-items: center;
    margin-bottom: 2rem;
    border: none;
    padding: 0;
  }
}

.btn-float {
  width: 100%;
  padding: 10px 0;
  border: none;
  font-weight: 700;
  cursor: pointer;
  text-align: center;
  font-size: 0.9rem;
  border-radius: 2px;
}

.btn-download {
  background-color: #C93737;
  color: white;
}

.btn-download:hover {
  background-color: #a02020;
}

.link-cite {
  color: #7f8c8d;
  font-size: 0.85rem;
  text-align: center;
  text-decoration: none;
}

.link-cite:hover {
  text-decoration: underline;
  color: #333;
}

/* 章节样式 */
.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem 0;
  padding-bottom: 0;
  border-bottom: none; /* Clean style */
  display: block;
}

/* 摘要样式 */
.journal-abstract {
  margin-bottom: 0;
}

.abstract-content {
  font-size: 1.15rem;
  line-height: 1.6; /* Journal Platform spec */
  color: #555; /* Light grey */
  text-align: justify;
  background: transparent; /* No background */
  padding: 0;
  border-radius: 0;
  border-left: none; /* Removed decoration */
  margin-bottom: 2rem;
}

/* 关键词样式 */
.journal-keywords {
  margin-bottom: 0;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.875rem;
}

.keyword-tag {
  display: inline-block;
  background: #f0f8ff;
  color: #4a90e2;
  padding: 0.5rem 1.25rem;
  border-radius: 24px;
  font-size: 0.95rem;
  font-weight: 600;
  border: 1px solid rgba(74, 144, 226, 0.2);
  box-shadow: none;
}

.keyword-tag:hover {
  background: #4a90e2;
  color: white;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

/* 正文样式 */
.journal-content {
  margin-bottom: 0;
  line-height: 1.6; /* Journal Platform spec */
  color: #333;
  font-size: 14px; /* Journal Platform spec */
}

.content-body {
  background: white;
  padding: 0; /* Remove padding/borders for clean read */
  border-radius: 0;
  border: none;
  min-height: 200px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  font-size: 14px;
  color: #333;
}

.link-supp {
  display: inline-block;
  margin-top: 1rem;
  font-weight: 700;
  color: #7f8c8d;
  text-decoration: none;
  transition: color 0.2s;
}

.link-supp:hover {
  color: #C93737;
  text-decoration: underline;
}

/* 富文本格式支持 */
.content-body h1,
.content-body h2,
.content-body h3,
.content-body h4,
.content-body h5,
.content-body h6 {
  margin: 1.5rem 0 1rem 0;
  font-weight: 600;
  line-height: 1.3;
}

.content-body h1 {
  font-size: 2rem;
}

.content-body h2 {
  font-size: 1.75rem;
}

.content-body h3 {
  font-size: 1.5rem;
}

.content-body h4 {
  font-size: 1.25rem;
}

.content-body h5 {
  font-size: 1.1rem;
}

.content-body h6 {
  font-size: 1rem;
}

.content-body p {
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.content-body ul,
.content-body ol {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.content-body ul {
  list-style-type: disc;
}

.content-body ol {
  list-style-type: decimal;
}

.content-body li {
  margin: 0.5rem 0;
  line-height: 1.6;
}

/* 对齐样式 */
.content-body .ql-align-center {
  text-align: center;
}

.content-body .ql-align-right {
  text-align: right;
}

.content-body .ql-align-justify {
  text-align: justify;
}

.content-body .ql-align-left {
  text-align: left;
}

/* 缩进样式 */
.content-body .ql-indent-1 {
  margin-left: 2rem;
}

.content-body .ql-indent-2 {
  margin-left: 4rem;
}

.content-body .ql-indent-3 {
  margin-left: 6rem;
}

/* 链接样式 */
.content-body a {
  color: #333;
  text-decoration: none;
  border-bottom: 1px solid #ccc; /* Subtle link style */
  transition: all 0.2s;
}

.content-body a:hover {
  color: #C93737;
  border-bottom-color: #C93737;
}

/* 图片样式 */
.content-body img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.5rem auto; /* Center images */
  border: 1px solid #eee; /* Thin grey border */
  border-radius: 0;
}

/* 代码块样式 */
.content-body pre.ql-syntax {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 5px;
  font-family: monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  overflow-x: auto;
  margin: 1rem 0;
}

/* 块引用样式 */
.content-body blockquote {
  border-left: 4px solid #3498db;
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: #666;
}

/* 水平分隔线样式 */
.content-body hr {
  border: none;
  border-top: 2px solid #eee;
  margin: 2rem 0;
}

.journal-content h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 2.5rem 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid #764ba2;
}

.journal-content h3 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 2rem 0 1rem 0;
  color: #764ba2;
}

.journal-content p {
  margin-bottom: 1.75rem;
  text-align: justify;
}

.journal-content ul, .journal-content ol {
  margin-bottom: 1.75rem;
  padding-left: 2.5rem;
}

.journal-content li {
  margin-bottom: 1rem;
  position: relative;
}

.journal-content ul li::before {
  content: '•';
  color: #667eea;
  font-weight: bold;
  display: inline-block;
  width: 1em;
  margin-left: -1em;
}

.journal-content ol li::before {
  content: counter(li);
  color: #667eea;
  font-weight: bold;
  display: inline-block;
  width: 1em;
  margin-left: -1em;
  counter-increment: li;
}

.journal-content ol {
  counter-reset: li;
}

/* 未找到期刊样式 */
.no-journal {
  text-align: center;
  padding: 4rem 2rem;
  margin-top: 80px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.no-journal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.no-journal-icon {
  font-size: 5rem;
  opacity: 0.5;
}

.no-journal h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.no-journal p {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin: 0;
  max-width: 400px;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .journal-detail-container {
    padding: 1.5rem 0;
  }
  
  .journal-detail-content {
    padding: 0 1.5rem;
  }
}

@media (max-width: 768px) {
  .journal-detail-content {
    padding: 0 1rem;
    margin-top: 70px;
  }
  
  .journal-detail-header,
  .card {
    padding: 1.5rem;
  }
  
  .journal-title {
    font-size: 1.8rem;
  }
  
  .meta-row {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .back-btn, .export-btn {
    width: 100%;
    justify-content: center;
  }
  
  .section-title {
    font-size: 1.4rem;
  }
  
  .abstract-content {
    font-size: 1rem;
    padding: 1rem;
  }
  
  .journal-content {
    font-size: 1rem;
  }
  
  .content-body {
    padding: 1.5rem;
  }
  
  .no-journal {
    padding: 3rem 1.5rem;
  }
  
  .no-journal-icon {
    font-size: 4rem;
  }
  
  .no-journal h2 {
    font-size: 1.6rem;
  }
}
</style>