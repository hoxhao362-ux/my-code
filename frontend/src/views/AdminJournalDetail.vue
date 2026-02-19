<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import Navigation from '../components/Navigation.vue'
import { checkExportPermission } from '../utils/export'
import ManuscriptReviewerManagement from './admin/manuscript/ManuscriptReviewerManagement.vue'
import ManuscriptBlindReviewAudit from './admin/manuscript/ManuscriptBlindReviewAudit.vue'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const journalId = computed(() => route.params.id)

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取当前期刊详情
const journal = computed(() => {
  return userStore.journals.find(j => {
    // 转换id类型为字符串进行比较，解决类型不匹配问题
    return String(j.id) === String(journalId.value)
  })
})

// 获取当前用户
const user = computed(() => userStore.user)

// Tabs
const activeTab = ref('reviewer_management')
const tabs = [
  { id: 'manuscript', label: 'Manuscript Detail' },
  { id: 'reviewer_management', label: 'Reviewer Management' },
  { id: 'audit', label: 'Blind Review Audit' },
  { id: 'history', label: 'Review History' }
]

// Blind Review Audit State - Managed in component


// 预览附件
const previewAttachment = (attachment) => {
  const fileExtension = `.${attachment.name.split('.').pop().toLowerCase()}`
  const previewableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
  
  if (previewableExtensions.includes(fileExtension)) {
    // 对于Detail页面，直接使用attachment.url作为数据源，因为Detail页面的附件是从服务器获取的，不是本地文件
    // 创建一个新的预览窗口
    const previewWindow = window.open('', '_blank', 'width=1000,height=800')
    if (previewWindow) {
      // 构建HTML内容，使用字符串拼接避免Vue编译器解析错误
      const htmlContent = `
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
              const fileUrl = '${attachment.url}';
              
              contentDiv.innerHTML = '';
              
              if (fileType === '.pdf') {
                // PDF预览 - 使用object标签替代iframe，更可靠的PDF预览方式
                const object = document.createElement('object');
                object.data = fileUrl;
                object.type = 'application/pdf';
                object.style.width = '100%';
                object.style.height = '100%';
                
                // 提供备用内容
                const fallback = document.createElement('div');
                fallback.innerHTML = '<div class="loading">PDF预览失败，建议直接下载查看</div>';
                
                object.appendChild(fallback);
                contentDiv.appendChild(object);
              } else if (fileType.match(/\.(jpg|jpeg|png|gif)$/i)) {
                // 图片预览
                const img = document.createElement('img');
                img.src = fileUrl;
                img.style.maxWidth = '100%';
                img.style.maxHeight = '100%';
                img.style.objectFit = 'contain';
                img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
                
                img.onload = function() {
                  console.log('图片加载完成');
                };
                img.onerror = function() {
                  contentDiv.innerHTML = '<div class="loading">图片预览失败，建议直接下载查看</div>';
                };
                
                contentDiv.innerHTML = '';
                contentDiv.appendChild(img);
              } else if (fileType === '.txt') {
                // 文本文件预览 - 使用fetch获取文本内容
                fetch(fileUrl)
                  .then(response => response.text())
                  .then(text => {
                    const pre = document.createElement('pre');
                    pre.textContent = text;
                    contentDiv.innerHTML = '';
                    contentDiv.appendChild(pre);
                  })
                  .catch(error => {
                    console.error('文本加载失败:', error);
                    contentDiv.innerHTML = '<div class="loading">文本预览失败，建议直接下载查看</div>';
                  });
              } else {
                // 其他文档类型，直接提示无法预览
                contentDiv.innerHTML = '<div class="loading">该文件类型无法直接预览，建议直接下载查看</div>';
              }
            }
            
            // 页面加载完成后初始化预览
            window.onload = initPreview;
          <\/script>
        </body>
        </html>
      `;
      
      // 写入并关闭文档
      previewWindow.document.write(htmlContent);
      previewWindow.document.close();
    }
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
  return checkExportPermission(user.value.role, 'journal', journal.value, user.value.id)
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 组件挂载时滚动到页面顶部
onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<template>
  <div class="journal-detail-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-journal-detail'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />
    
    <div v-if="journal" class="journal-detail-content">
      <!-- 头部卡片 -->
      <header class="journal-detail-header">
        <div class="header-actions">
          <button class="back-btn" @click="goBack">
            <span class="icon">←</span> 返回
          </button>
          <!-- 附件下载按钮 -->
          <div v-if="hasAttachments" class="attachments-container">
            <div class="attachments-title">附件：</div>
            <div class="attachments-list">
              <div 
                v-for="attachment in journal.attachments" 
                :key="attachment.id"
                class="attachment-item"
              >
                <div class="attachment-info">
                  <span class="attachment-name">{{ attachment.name }} ({{ formatFileSize(attachment.size) }})</span>
                </div>
                <div class="attachment-actions">
                  <button 
                    class="attachment-preview-btn"
                    @click="previewAttachment(attachment)"
                  >
                    <span class="icon">👁️</span> 预览
                  </button>
                  <button 
                    class="attachment-download-btn"
                    @click="handleDownloadAttachment(attachment)"
                  >
                    <span class="icon">📥</span> 下载
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <h1 class="journal-title">{{ journal.title }}</h1>
        <div class="journal-meta">
          <div class="meta-row">
            <span class="meta-item">
              <strong>作者：</strong>{{ journal.author }}
            </span>
            <span class="meta-item">
              <strong>投稿日期：</strong>{{ journal.date }}
            </span>
          </div>
          <div class="meta-row">
            <span class="meta-item">
              <strong>模块：</strong>
              <span 
                v-if="Array.isArray(journal.module)" 
                class="module-tags"
              >
                <span 
                  v-for="(module, index) in journal.module" 
                  :key="index" 
                  class="module-tag"
                >
                  {{ module }}
                </span>
              </span>
              <span v-else>{{ journal.module }}</span>
            </span>
            <span class="meta-item">
              <strong>状态：</strong>
              <span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span>
            </span>
          </div>
          <div class="meta-row">
            <span class="meta-item">
              <strong>审核阶段：</strong>{{ journal.reviewStage || '未开始' }}
            </span>
            <span class="meta-item">
              <strong>审核结果：</strong>{{ journal.reviewResult || '待审核' }}
            </span>
          </div>
        </div>
      </header>

      <!-- Tabs Header -->
      <div class="tabs-header">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          class="tab-btn" 
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content: Manuscript -->
      <div v-show="activeTab === 'manuscript'">
        <!-- 摘要卡片 -->
        <section class="journal-abstract card">
          <h2 class="section-title">摘要</h2>
          <div class="abstract-content" v-html="journal.abstract"></div>
        </section>
  
        <!-- 关键词卡片 -->
        <section class="journal-keywords card">
          <h2 class="section-title">关键词</h2>
          <div class="keywords-list">
            <span 
              v-for="(keyword, index) in journal.keywords" 
              :key="index" 
              class="keyword-tag"
            >
              {{ keyword }}
            </span>
          </div>
        </section>
  
        <!-- 正文卡片 -->
        <section class="journal-content card">
          <h2 class="section-title">正文</h2>
          <div class="content-body" v-html="journal.content"></div>
        </section>
      </div>

      <!-- Tab Content: Reviewer Management -->
      <div v-show="activeTab === 'reviewer_management'" class="reviewer-management-tab">
        <section class="card">
           <ManuscriptReviewerManagement :manuscript-id="journalId" />
        </section>
      </div>

      <!-- Tab Content: Blind Review Audit -->
      <div v-show="activeTab === 'audit'" class="audit-tab">
        <section class="card">
          <ManuscriptBlindReviewAudit :manuscript-id="journalId" />
        </section>
      </div>

      <!-- Tab Content: History -->
      <div v-show="activeTab === 'history'">
        <!-- 审核历史记录卡片 -->
        <section class="journal-review-history card" v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
          <h2 class="section-title">审核历史记录</h2>
          <div class="review-history-list">
            <div 
              v-for="(record, index) in journal.reviewHistory" 
              :key="index" 
              class="review-history-item"
            >
              <div class="review-history-header">
                <span class="review-stage">{{ record.stage }}：</span>
                <span class="review-status" :class="record.status.toLowerCase()">{{ record.status }}</span>
                <span class="review-date">{{ record.date }}</span>
                <span class="reviewer">({{ record.reviewer }})</span>
              </div>
              <div class="review-comment" v-if="record.comment">{{ record.comment }}</div>
            </div>
          </div>
        </section>
        <div v-else class="card no-data">No history available.</div>
      </div>
    </div>
    <!-- 未找到稿件 -->
    <div v-else class="no-journal card">
      <div class="no-journal-content">
        <div class="no-journal-icon">📄</div>
        <h2>未找到该稿件</h2>
        <p>抱歉，您访问的稿件不存在或已被删除</p>
        <button class="back-btn" @click="goBack">返回</button>
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
  background-color: #f5f5f5;
  padding: 2rem 0;
}

/* 主内容区域 */
.journal-detail-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  margin-top: 100px; /* 为固定导航栏留出空间 */
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  box-shadow: none;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
}

/* 头部卡片 */
.journal-detail-header {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: none;
  border: 1px solid #e0e0e0;
}

/* Tabs */
.tabs-header {
  display: flex;
  gap: 1rem;
  border-bottom: 2px solid #ddd;
  margin-bottom: 1.5rem;
  background: white;
  padding: 0 1rem;
  border-radius: 8px 8px 0 0;
}

.tab-btn {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 600;
  color: #666;
  font-size: 1rem;
  margin-bottom: -2px;
}

.tab-btn.active {
  color: #C93737;
  border-bottom-color: #C93737;
}

.tab-btn:hover {
  color: #C93737;
}

/* Audit Styles */
.audit-intro {
  color: #666;
  margin-bottom: 1.5rem;
}

.audit-table {
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
}

.audit-header {
  display: flex;
  background: #f8f9fa;
  padding: 1rem;
  font-weight: 600;
  border-bottom: 1px solid #eee;
}

.audit-row {
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.col-item { flex: 2; }
.col-status { flex: 1; }
.col-action { flex: 1; display: flex; gap: 0.5rem; }

.item-name { font-weight: 500; color: #333; }
.ref-check { margin-top: 5px; }
.btn-text { background: none; border: none; color: #3498db; cursor: pointer; text-decoration: underline; padding: 0; font-size: 0.9rem; }
.feedback-text { color: #C93737; font-size: 0.9rem; margin-top: 5px; }

.status-pass { color: #2ecc71; font-weight: bold; }
.status-fail { color: #e74c3c; font-weight: bold; }
.status-pending { color: #f39c12; font-weight: bold; }

.btn-approve {
  background: #C93737;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-reject {
  background: #eee;
  color: #333;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.audit-footer {
  margin-top: 2rem;
  text-align: right;
}

.btn-complete {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}
.btn-complete:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* 标题样式 */
.journal-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  line-height: 1.3;
  letter-spacing: -0.5px;
}

/* 元信息样式 */
.journal-meta {
  color: #7f8c8d;
  font-size: 1rem;
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
.journal-status, .review-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  border-radius: 24px;
  font-size: 0.95rem;
  font-weight: 600;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.journal-status::before, .review-status::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.journal-status.已通过, .review-status.已通过 {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.journal-status.审稿中, .journal-status.待审核 {
  background: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.journal-status.未通过, .review-status.未通过 {
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

/* 章节样式 */
.section-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid #66b3ff;
  display: inline-block;
}

/* 摘要样式 */
.abstract-content {
  font-size: 1.15rem;
  line-height: 1.8;
  color: #555;
  text-align: justify;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #66b3ff;
}

/* 关键词样式 */
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
  line-height: 1.8;
  color: #333;
  font-size: 1.15rem;
}

.content-body {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  min-height: 200px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
  font-size: 1rem;
  color: #333;
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
  color: #3498db;
  text-decoration: underline;
}

.content-body a:hover {
  color: #2980b9;
}

/* 图片样式 */
.content-body img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border-radius: 5px;
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
  border-bottom: 3px solid #66b3ff;
}

.journal-content h3 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 2rem 0 1rem 0;
  color: #66b3ff;
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

/* 审核历史记录样式 */
.review-history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-history-item {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid #66b3ff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.review-history-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.review-stage {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1.1rem;
}

.review-date, .reviewer {
  color: #7f8c8d;
  font-size: 0.95rem;
  font-style: italic;
}

.review-comment {
  color: #555;
  line-height: 1.8;
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
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
  
  .review-history-item {
    padding: 1.5rem;
  }
  
  .review-history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
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