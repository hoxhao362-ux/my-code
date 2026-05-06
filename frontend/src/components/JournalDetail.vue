<script setup>
import { ref, computed } from 'vue'
import { stripHtmlTags } from '../utils/helpers'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'journalId', 'logout', 'journals', 'reviewRecords', 'toggleDirectory'])

// 根据journalId获取当前显示的稿件
const journal = computed(() => {
  return props.journals.find(item => item.id === props.journalId) || null
})

// 获取当前稿件的审核记录
const journalReviewRecords = computed(() => {
  if (!props.reviewRecords || !props.journalId) return []
  return props.reviewRecords
    .filter(record => record.journalId === props.journalId)
    .sort((a, b) => new Date(a.reviewDate) - new Date(b.reviewDate))
})

const goBack = () => {
  // 返回上一页
  props.navigateTo('home')
}

// 切换目录显示
const toggleDirectory = () => {
  if (props.toggleDirectory) {
    props.toggleDirectory()
  }
}

// 处理退出登录
const handleLogout = () => {
  if (props.logout) {
    props.logout()
  }
}
</script>

<template>
  <div class="journal-detail-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
<<<<<<< HEAD
          <h1>Journal Platform</h1>
=======
          <h1>Peerex Peer</h1>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('home')">Home</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">Directory</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">Submit</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">Review</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">Profile</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">Logout</a></li>
        </ul>
      </div>
    </nav>

    <!-- 稿件详情内容 -->
    <main class="journal-detail-content">
      <div class="journal-detail-wrapper">
        <div class="article-actions">
          <button class="back-btn" @click="goBack">← Back</button>
          <div class="action-buttons">
            <button class="action-btn pdf-btn">Download PDF</button>
            <button class="action-btn cite-btn">Cite This Article</button>
          </div>
        </div>
        
        <div class="journal-detail-header">
          <h2 class="journal-title">{{ journal.title }}</h2>
          <div class="journal-meta">
            <span class="meta-item">Authors: {{ journal.author }}</span>
            <span class="meta-item">Submission Date: {{ journal.date }}</span>
            <span class="meta-item status" :class="journal.status.toLowerCase()">{{ journal.status }}</span>
            <span class="meta-item">Review Stage: {{ journal.reviewStage || 'Not specified' }}</span>
          </div>
        </div>

        <div class="journal-detail-body">
          <!-- 左侧：论文详情 -->
          <div class="journal-main-content">
            <section class="detail-section abstract-section">
              <h3 class="section-title">Abstract</h3>
              <div class="section-content abstract-content" v-html="journal.abstract"></div>
            </section>

            <section class="detail-section keywords-section">
              <h3 class="section-title">Keywords</h3>
              <div class="section-content keywords-content">
                <span v-for="(keyword, index) in journal.keywords.split(',').map(k => k.trim())" :key="index" class="keyword-tag">
                  {{ keyword }}
                </span>
              </div>
            </section>

            <section class="detail-section article-section">
              <h3 class="section-title">Article</h3>
              <div class="section-content article-content" v-html="journal.content"></div>
            </section>
          </div>
          
          <!-- 右侧：审核记录 -->
          <div class="journal-sidebar">
            <div class="review-records-section">
              <h3 class="section-title">Review Records</h3>
              
              <!-- 审核记录列表 -->
              <div class="review-records-list">
                <div v-if="journalReviewRecords.length === 0" class="no-records">
                  <p>No review records</p>
                </div>
                
                <div 
                  v-for="record in journalReviewRecords" 
                  :key="record.id" 
                  class="review-record-item"
                >
                  <div class="record-header">
                    <div class="record-stage">{{ record.reviewStage }}</div>
                    <div class="record-result" :class="record.reviewResult.toLowerCase()">{{ record.reviewResult }}</div>
                  </div>
                  <div class="record-content">
                    <div class="record-meta">
                      <div class="reviewer-info">Reviewer: {{ record.reviewerId }}</div>
                      <div class="review-date">Review Date: {{ new Date(record.reviewDate).toLocaleDateString() }}</div>
                    </div>
                    <div class="review-comments">
                      <h4>Review Comments:</h4>
                      <p>{{ record.reviewComments }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
<<<<<<< HEAD
        <p>&copy; 2026 Journal Platform. All rights reserved.</p>
=======
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>
    </footer>
  </div>
</template>

<style scoped>
.journal-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

/* 导航栏样式 */
.navbar {
  background: #0056B3;
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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
  color: #ecf0f1;
  text-decoration: underline;
}

.nav-link.logout {
  color: #ecf0f1;
}

.nav-link.logout:hover {
  color: #bdc3c7;
}

/* 稿件详情内容 */
.journal-detail-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.journal-detail-wrapper {
  background: white;
  padding: 2rem;
  border: 1px solid #e0e0e0;
}

/* 文章操作按钮 */
.article-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 3px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #7f8c8d;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.action-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 3px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pdf-btn {
  background: #0056B3;
  color: white;
}

.pdf-btn:hover {
  background: #004494;
}

.cite-btn {
  background: #34495e;
  color: white;
}

.cite-btn:hover {
  background: #5a6268;
}

/* 文章标题和元数据 */
.journal-detail-header {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.journal-title {
  font-size: 2.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  line-height: 1.3;
  font-family: 'Segoe UI', sans-serif;
}

.journal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
  font-size: 0.95rem;
  color: #7f8c8d;
}

.meta-item {
  display: inline-block;
}

.meta-item.status {
  font-weight: 600;
  padding: 0.2rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
}

.meta-item.待审核 {
  background: #fff3cd;
  color: #856404;
}

.meta-item.审核中 {
  background: #cce7ff;
  color: #004085;
}

.meta-item.已通过 {
  background: #d4edda;
  color: #155724;
}

.meta-item.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

/* 详情内容 - 左右分栏布局 */
.journal-detail-body {
  display: flex;
  gap: 3rem;
  align-items: flex-start;
}

/* 左侧主内容 */
.journal-main-content {
  flex: 1;
  min-width: 0;
}

/* 右侧边栏 */
.journal-sidebar {
  width: 320px;
  border-left: 1px solid #e0e0e0;
  padding-left: 2rem;
  position: sticky;
  top: 100px;
  height: fit-content;
}

/* 审核记录部分 */
.review-records-section {
  width: 100%;
}

.review-records-section .section-title {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.review-records-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 审核记录项 */
.review-record-item {
  background: #f9f9f9;
  padding: 1.2rem;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
}

/* 记录头部 */
.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #e0e0e0;
}

.record-stage {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.record-result {
  padding: 0.2rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.record-result.通过 {
  background: #d4edda;
  color: #155724;
}

.record-result.修改后通过 {
  background: #fff3cd;
  color: #856404;
}

.record-result.退回 {
  background: #cce7ff;
  color: #004085;
}

.record-result.驳回 {
  background: #f8d7da;
  color: #721c24;
}

/* 记录内容 */
.record-content {
  font-size: 0.9rem;
}

.record-meta {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-bottom: 0.8rem;
  color: #666;
  font-size: 0.85rem;
}

.reviewer-info {
  font-weight: 500;
}

.review-date {
  font-size: 0.8rem;
}

.review-comments h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #555;
  font-weight: 600;
}

.review-comments p {
  margin: 0;
  line-height: 1.5;
  color: #555;
  font-size: 0.85rem;
}

/* 无记录状态 */
.no-records {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-style: italic;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
}

/* 详情部分通用样式 */
.detail-section {
  margin-bottom: 3rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #0056B3;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.section-content {
  color: #333;
  line-height: 1.7;
  margin: 0;
  font-size: 1rem;
}

/* 摘要部分 */
.abstract-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #333;
}

/* 关键词部分 */
.keywords-content {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background: #f0f0f0;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  color: #555;
  border: 1px solid #e0e0e0;
}

/* 文章内容部分 */
.article-content {
  font-size: 1rem;
  line-height: 1.7;
  color: #333;
}

/* 富文本格式支持 */
.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4,
.article-content h5,
.article-content h6 {
  margin: 2rem 0 1rem 0;
  font-weight: 600;
  line-height: 1.3;
  color: #2c3e50;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.article-content h1 {
  font-size: 1.8rem;
}

.article-content h2 {
  font-size: 1.5rem;
}

.article-content h3 {
  font-size: 1.3rem;
}

.article-content h4 {
  font-size: 1.1rem;
}

.article-content h5 {
  font-size: 1rem;
}

.article-content h6 {
  font-size: 0.9rem;
}

.article-content p {
  margin: 0 0 1.2rem 0;
  line-height: 1.7;
}

.article-content ul,
.article-content ol {
  margin: 0 0 1.2rem 1.5rem;
  padding: 0;
}

.article-content ul {
  list-style-type: disc;
}

.article-content ol {
  list-style-type: decimal;
}

.article-content li {
  margin: 0.5rem 0;
  line-height: 1.7;
}

/* 对齐样式 */
.article-content .ql-align-center {
  text-align: center;
}

.article-content .ql-align-right {
  text-align: right;
}

.article-content .ql-align-justify {
  text-align: justify;
}

.article-content .ql-align-left {
  text-align: left;
}

/* 缩进样式 */
.article-content .ql-indent-1 {
  margin-left: 2rem;
}

.article-content .ql-indent-2 {
  margin-left: 4rem;
}

.article-content .ql-indent-3 {
  margin-left: 6rem;
}

.article-content pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.8;
}

/* 链接样式 */
.article-content a {
  color: #0056B3;
  text-decoration: none;
  border-bottom: 1px solid #0056B3;
}

.article-content a:hover {
  color: #004494;
  border-bottom: 1px solid #004494;
}

/* 图片样式 */
.article-content img {
  max-width: 100%;
  height: auto;
  margin: 1.5rem 0;
  border: 1px solid #e0e0e0;
}

/* 代码块样式 */
.article-content pre.ql-syntax {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid #e0e0e0;
}

/* 块引用样式 */
.article-content blockquote {
  border-left: 4px solid #0056B3;
  padding-left: 1rem;
  margin: 1.5rem 0;
  font-style: italic;
  color: #666;
}

/* 水平分隔线样式 */
.article-content hr {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 2rem 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .journal-detail-body {
    flex-direction: column;
  }
  
  .journal-sidebar {
    width: 100%;
    position: static;
    border-left: none;
    border-top: 1px solid #e0e0e0;
    padding-left: 0;
    padding-top: 2rem;
    margin-top: 2rem;
  }
  
  .article-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .action-btn {
    flex: 1;
    text-align: center;
  }
}

/* 页脚样式 */
.footer {
  background: #34495e;
  color: white;
  padding: 1.5rem 0;
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
