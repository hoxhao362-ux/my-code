<script setup>
import { ref, computed, onMounted } from 'vue'
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
const activeTab = ref('manuscript')
const tabs = [
  { id: 'manuscript', label: 'Manuscript' },
  { id: 'reviewer_management', label: 'Reviewer Management' },
  { id: 'audit', label: 'Blind Review Audit' },
  { id: 'history', label: 'Review History' }
]

// Preview attachment
const previewAttachment = (attachment) => {
  const fileExtension = `.${attachment.name.split('.').pop().toLowerCase()}`
  const previewableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
  
  if (previewableExtensions.includes(fileExtension)) {
    const previewWindow = window.open('', '_blank', 'width=1000,height=800')
    if (previewWindow) {
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Preview: ${attachment.name}</title>
          <style>
            body { margin: 0; padding: 0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background: #f4f4f4; }
            .header { padding: 15px; background: white; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
            .title { font-weight: bold; color: #333; }
            .btn { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; color: white; text-decoration: none; font-size: 14px; }
            .btn-primary { background: #E30613; }
            .btn-secondary { background: #666; }
            .content { padding: 20px; text-align: center; height: calc(100vh - 70px); box-sizing: border-box; }
            iframe, object { width: 100%; height: 100%; border: none; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            img { max-width: 100%; max-height: 100%; object-fit: contain; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="title">${attachment.name}</div>
            <div>
              <a href="${attachment.url}" download="${attachment.name}" class="btn btn-primary">Download</a>
              <button onclick="window.close()" class="btn btn-secondary">Close</button>
            </div>
          </div>
          <div class="content" id="preview-content">
            <div style="margin-top: 100px;">Loading...</div>
          </div>
          <script>
            const ext = '${fileExtension}';
            const url = '${attachment.url}';
            const container = document.getElementById('preview-content');
            container.innerHTML = '';
            
            if (ext === '.pdf') {
               const obj = document.createElement('object');
               obj.data = url;
               obj.type = 'application/pdf';
               obj.innerHTML = '<p>Your browser does not support PDF preview. Please <a href="' + url + '">download</a> to view.</p>';
               container.appendChild(obj);
            } else if (['.jpg', '.jpeg', '.png', '.gif'].includes(ext)) {
               const img = document.createElement('img');
               img.src = url;
               container.appendChild(img);
            } else if (ext === '.txt') {
               fetch(url).then(r => r.text()).then(t => {
                 const pre = document.createElement('pre');
                 pre.style.textAlign = 'left';
                 pre.style.background = 'white';
                 pre.style.padding = '20px';
                 pre.innerText = t;
                 container.appendChild(pre);
               });
            } else {
               container.innerHTML = '<p>Preview is not available for this file type. Please download to view.</p>';
            }
          <\/script>
        </body>
        </html>
      `;
      
      previewWindow.document.write(htmlContent);
      previewWindow.document.close();
    }
  } else {
    handleDownloadAttachment(attachment)
  }
}

// 下载附件
const handleDownloadAttachment = (attachment) => {
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

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 状态辅助函数
const getStatusClass = (status) => {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s === 'approved' || s === 'published' || s === '已通过') return 'approved'
  if (s === 'rejected' || s === '未通过') return 'rejected'
  if (s === 'pending' || s === 'under review' || s === '审稿中') return 'pending'
  return ''
}

const getStatusText = (status) => {
  if (!status) return 'Unknown Status'
  const map = {
    'submitted': 'Submitted',
    'under review': 'Under Review',
    'approved': 'Accepted',
    'published': 'Published',
    'rejected': 'Rejected',
    'revision': 'Revision Required',
    'passed': 'Passed',
    'pending': 'Pending'
  }
  return map[status.toLowerCase()] || status
}

const getStageText = (stage) => {
  if (!stage) return 'Unknown Stage'
  const map = {
    'submission': 'Submission',
    'review': 'Review',
    'revision': 'Revision',
    'decision': 'Decision',
    'production': 'Production'
  }
  return map[stage.toLowerCase()] || stage
}

// 组件挂载时滚动到页面顶部
onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<template>
  <div class="lancet-container">
    <!-- 顶部导航 -->
    <Navigation 
      :user="user"
      :current-page="'admin-journal-detail'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />
    
    <div v-if="journal" class="lancet-main">
      <!-- Lancet-style Header -->
      <header class="lancet-header">
        <div class="journal-brand-row">
          <div class="journal-brand">THE LANCET</div>
          <div class="journal-sub-brand">Review System</div>
        </div>
        
        <div class="article-meta-top">
          <span class="meta-type">{{ journal.module === 'Research' ? 'Research Article' : (journal.module || 'Research Article') }}</span>
          <span class="meta-divider">|</span>
          <span class="meta-date">Published: {{ journal.date }}</span>
          <span class="meta-divider">|</span>
          <span class="meta-id">Manuscript ID: {{ journal.id }}</span>
        </div>
        
        <h1 class="article-title">{{ journal.title }}</h1>
        
        <div class="article-authors">
          <span class="author-label">Authors:</span>
          <span class="author-name">{{ journal.author }}</span>
          <span class="author-affiliations" v-if="journal.author"> (including all named authors)</span>
        </div>
        
        <div class="header-actions-row">
          <div class="action-buttons">
            <button class="action-btn download-btn" v-if="hasAttachments" @click="handleDownloadAttachment(journal.attachments[0])">
              <span class="icon">⬇</span> Download PDF
            </button>
            <button class="action-btn secondary-btn" @click="goBack">
              <span class="icon">←</span> Back to List
            </button>
          </div>
          <div class="status-indicator">
            <span class="status-label">Current Status:</span>
            <span class="status-badge" :class="getStatusClass(journal.status)">{{ getStatusText(journal.status) }}</span>
          </div>
        </div>
      </header>

      <!-- Sticky Navigation Bar -->
      <div class="lancet-tabs-nav">
        <div class="tabs-container">
          <button 
            v-for="tab in tabs" 
            :key="tab.id" 
            class="lancet-tab-btn" 
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
      
      <!-- Content Area: Two-column Layout -->
      <div class="lancet-content">
        <div class="lancet-layout-grid">
          
          <!-- Left Main Content Column -->
          <main class="lancet-main-column">
            
            <!-- Tab: Manuscript -->
            <div v-show="activeTab === 'manuscript'" class="tab-content fade-in">
              <!-- Abstract -->
              <section class="article-section">
                <h2 class="section-heading">Abstract</h2>
                <div class="abstract-text" v-html="journal.abstract || 'No abstract available'"></div>
              </section>

              <!-- Keywords -->
              <section class="article-section" v-if="journal.keywords">
                <div class="keywords-block">
                  <span class="keyword-label">Keywords:</span>
                  <span v-for="(k, i) in journal.keywords" :key="i" class="keyword-item">{{ k }}</span>
                </div>
              </section>

              <!-- Main Text -->
              <section class="article-section">
                <h2 class="section-heading">Main Text</h2>
                <div class="article-body" v-html="journal.content || 'No content available'"></div>
              </section>
              
              <!-- Declarations (Lancet-style standard declarations) -->
              <section class="article-section declarations-section">
                <h2 class="section-heading">Declarations</h2>
                <div class="declaration-item">
                  <h4>Conflict of Interest</h4>
                  <p>The authors declare no conflict of interest.</p>
                </div>
                <div class="declaration-item">
                  <h4>Data Sharing</h4>
                  <p>Study data are available from the corresponding author upon reasonable request.</p>
                </div>
              </section>

              <!-- Supplementary Materials -->
              <section class="article-section" v-if="hasAttachments">
                <h3 class="subsection-heading">Supplementary Materials</h3>
                <div class="file-list">
                  <div v-for="file in journal.attachments" :key="file.id" class="file-row">
                    <span class="file-icon">📄</span>
                    <a href="#" @click.prevent="previewAttachment(file)" class="file-link">{{ file.name }}</a>
                    <span class="file-size">({{ formatFileSize(file.size) }})</span>
                    <button class="sm-btn" @click="handleDownloadAttachment(file)">Download</button>
                  </div>
                </div>
              </section>
            </div>

            <!-- Tab: Reviewer Management -->
            <div v-show="activeTab === 'reviewer_management'" class="tab-content fade-in">
               <ManuscriptReviewerManagement :manuscript-id="journalId" />
            </div>

            <!-- Tab: Blind Review Audit -->
            <div v-show="activeTab === 'audit'" class="tab-content fade-in">
              <ManuscriptBlindReviewAudit :manuscript-id="journalId" />
            </div>

            <!-- Tab: Review History -->
            <div v-show="activeTab === 'history'" class="tab-content fade-in">
              <div class="history-timeline">
                 <div v-if="!journal.reviewHistory || journal.reviewHistory.length === 0" class="no-history">No review history available</div>
                 <div v-else v-for="(rec, idx) in journal.reviewHistory" :key="idx" class="timeline-item">
                   <div class="timeline-date">{{ rec.date }}</div>
                   <div class="timeline-content">
                     <div class="timeline-header">
                       <span class="stage-tag">{{ getStageText(rec.stage) }}</span>
                       <span class="status-tag" :class="rec.status">{{ getStatusText(rec.status) }}</span>
                     </div>
                     <div class="timeline-body">
                       <p class="reviewer-info">Reviewer: {{ rec.reviewer }}</p>
                       <p v-if="rec.comment" class="comment-box">{{ rec.comment }}</p>
                     </div>
                   </div>
                 </div>
              </div>
            </div>

          </main>

          <!-- Right Sidebar -->
          <aside class="lancet-sidebar">
            <div class="sidebar-widget">
              <h3 class="widget-title">Article Information</h3>
              <ul class="meta-list">
                <li><strong>DOI:</strong> 10.1016/S0140-6736(23)00000-X</li>
                <li><strong>Manuscript ID:</strong> {{ journal.id }}</li>
                <li><strong>Review Stage:</strong> {{ journal.reviewStage || 'Not Started' }}</li>
                <li><strong>Final Result:</strong> {{ journal.reviewResult || 'Processing' }}</li>
              </ul>
            </div>

            <div class="sidebar-widget">
              <h3 class="widget-title">Metrics</h3>
              <ul class="meta-list">
                 <li><strong>Citations:</strong> 0</li>
                 <li><strong>Views:</strong> 128</li>
              </ul>
            </div>

            <div class="sidebar-widget">
              <h3 class="widget-title">Quick Actions</h3>
              <div class="quick-actions">
                <button class="sidebar-btn" @click="activeTab = 'reviewer_management'">Assign Reviewers</button>
                <button class="sidebar-btn" @click="activeTab = 'audit'">Blind Review Audit</button>
                <button class="sidebar-btn outline" @click="goBack">Back to Dashboard</button>
              </div>
            </div>
          </aside>

        </div>
      </div>
    </div>

    <!-- 404 State -->
    <div v-else class="not-found">
      <h2>Manuscript Not Found</h2>
      <button @click="goBack">Back</button>
    </div>
  </div>
</template>

<style scoped>
/* Reset & Fonts */
.lancet-container {
  font-family: "Minion Pro", "Times New Roman", serif;
  background-color: #f4f4f4;
  min-height: 100vh;
  color: #222;
}

/* Header */
.lancet-header {
  background: white;
  padding: 40px 10%; /* Wide padding like Lancet */
  border-bottom: 1px solid #e0e0e0;
}

.journal-brand-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.journal-brand {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 24px;
  font-weight: 900;
  color: #000; /* Lancet logo is usually black text on white, or white on red. Using Black here for clean look */
  letter-spacing: 0.5px;
}

.journal-sub-brand {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 14px;
  color: #666;
  border-left: 1px solid #ccc;
  padding-left: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.article-meta-top {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-type {
  font-weight: 700;
  color: #E30613; /* Lancet Red for type */
  text-transform: uppercase;
}

.meta-divider {
  color: #ccc;
}

.article-title {
  font-family: "Minion Pro", "Times New Roman", serif;
  font-size: 38px;
  line-height: 1.2;
  font-weight: 400; 
  margin: 0 0 20px 0;
  color: #222;
}

.article-authors {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 16px;
  color: #444;
  margin-bottom: 30px;
}

.author-label {
  font-weight: bold;
  margin-right: 5px;
  color: #222;
}

.author-name {
  color: #E30613; /* Authors often highlighted */
  font-weight: 500;
}

.author-affiliations {
  color: #666;
  font-size: 14px;
}

/* Header Actions */
.header-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.action-btn {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  padding: 10px 24px;
  border: none;
  border-radius: 0; /* Square buttons like Lancet */
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.download-btn {
  background-color: #E30613;
  color: white;
}
.download-btn:hover { background-color: #be000b; }

.secondary-btn {
  background-color: #f4f4f4;
  color: #333;
}
.secondary-btn:hover { background-color: #e0e0e0; }

.status-indicator {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 14px;
  display: flex;
  align-items: center;
}
.status-label { color: #666; margin-right: 8px; }

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  background: #eee;
  color: #666;
}
.status-badge.approved { background: #e6f7ed; color: #1e7e34; }
.status-badge.rejected { background: #fbeaea; color: #dc3545; }
.status-badge.pending { background: #fff3cd; color: #856404; }

/* Sticky Tabs Navigation */
.lancet-tabs-nav {
  background: white;
  border-bottom: 1px solid #ddd;
  position: sticky;
  top: 60px; /* Adjust based on Navigation height */
  z-index: 100;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.tabs-container {
  width: 80%;
  margin: 0 auto;
  display: flex;
  gap: 40px;
}

.lancet-tab-btn {
  background: none;
  border: none;
  padding: 18px 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #555;
  cursor: pointer;
  position: relative;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.lancet-tab-btn.active {
  color: #E30613;
}

.lancet-tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #E30613;
}

/* Layout */
.lancet-content-wrapper {
  width: 80%;
  margin: 40px auto;
}

.lancet-layout-grid {
  display: grid;
  grid-template-columns: 2.5fr 1fr; /* Wider main column */
  gap: 50px;
}

/* Main Column */
.lancet-main-column {
  background: white;
  padding: 40px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.section-heading {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #E30613;
  margin-top: 0;
  margin-bottom: 25px;
  border-bottom: 2px solid #f4f4f4;
  padding-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.subsection-heading {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-top: 30px;
  margin-bottom: 15px;
}

.abstract-text {
  font-size: 18px;
  line-height: 1.6;
  color: #222;
  margin-bottom: 40px;
  font-weight: 500; /* Abstract is often slightly heavier or italic */
}

.keywords-block {
  background: #fcfcfc;
  padding: 20px;
  border-left: 4px solid #E30613;
  margin-bottom: 40px;
  font-family: "Helvetica Neue", sans-serif;
}
.keyword-label { font-weight: bold; margin-right: 10px; color: #333; }
.keyword-item { 
  display: inline-block; 
  margin-right: 8px; 
  color: #444; 
  background: #eee; 
  padding: 4px 10px; 
  border-radius: 0;
  font-size: 13px;
  font-weight: 500;
}

.article-body {
  font-size: 18px;
  line-height: 1.8;
  color: #222;
}

.declarations-section {
  margin-top: 50px;
  background: #f9f9f9;
  padding: 30px;
}

.declaration-item {
  margin-bottom: 20px;
}

.declaration-item h4 {
  font-family: "Helvetica Neue", sans-serif;
  font-size: 16px;
  margin-bottom: 5px;
  color: #333;
}

.declaration-item p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Sidebar */
.lancet-sidebar {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.sidebar-widget {
  background: white;
  padding: 25px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-top: 4px solid #333;
  border: 1px solid #eee;
  border-top-width: 4px;
  border-top-color: #333;
}

.widget-title {
  font-family: "Helvetica Neue", sans-serif;
  font-size: 15px;
  font-weight: 800;
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-family: "Helvetica Neue", sans-serif;
  font-size: 14px;
}

.meta-list li {
  margin-bottom: 12px;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
  display: flex;
  justify-content: space-between;
}

.meta-list li strong {
  color: #333;
}

.sidebar-btn {
  width: 100%;
  padding: 12px;
  background: #333;
  color: white;
  border: none;
  margin-bottom: 12px;
  cursor: pointer;
  font-weight: 700;
  text-align: center;
  font-family: "Helvetica Neue", sans-serif;
  font-size: 13px;
  text-transform: uppercase;
  transition: opacity 0.2s;
}
.sidebar-btn.outline {
  background: white;
  border: 1px solid #333;
  color: #333;
}
.sidebar-btn:hover { opacity: 0.85; }

/* History Timeline */
.history-timeline {
  font-family: "Helvetica Neue", sans-serif;
}
.timeline-item {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  border-left: 2px solid #eee;
  padding-left: 25px;
  position: relative;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -7px;
  top: 0;
  width: 12px;
  height: 12px;
  background: white;
  border: 3px solid #E30613;
  border-radius: 50%;
}
.timeline-date {
  font-size: 13px;
  color: #999;
  min-width: 90px;
  font-weight: 500;
}
.timeline-header {
  margin-bottom: 8px;
}
.stage-tag { font-weight: bold; margin-right: 10px; color: #333; }
.status-tag { 
  font-size: 11px; 
  padding: 3px 8px; 
  border-radius: 10px; 
  color: white; 
  background: #999; 
  text-transform: uppercase;
  font-weight: 700;
}
.status-tag.已通过 { background: #2ecc71; }
.status-tag.未通过 { background: #e74c3c; }
.comment-box {
  background: #f9f9f9;
  padding: 15px;
  margin-top: 10px;
  border-radius: 0;
  font-size: 14px;
  color: #444;
  border-left: 3px solid #ccc;
  font-style: italic;
}

/* Attachments */
.file-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #eee;
  margin-bottom: 10px;
  font-family: "Helvetica Neue", sans-serif;
  background: #fcfcfc;
}
.file-link { color: #222; text-decoration: none; font-weight: 600; flex: 1; }
.file-link:hover { color: #E30613; }
.sm-btn { 
  padding: 6px 12px; 
  font-size: 12px; 
  cursor: pointer; 
  background: #333; 
  color: white; 
  border: none;
  font-weight: bold;
}
.sm-btn:hover { background: #555; }

/* Responsive */
@media (max-width: 1024px) {
  .lancet-layout-grid { grid-template-columns: 1fr; }
  .lancet-header { padding: 30px 5%; }
  .lancet-content-wrapper { width: 95%; }
  .tabs-container { width: 95%; gap: 20px; overflow-x: auto; }
}
</style>