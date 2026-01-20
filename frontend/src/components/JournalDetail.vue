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
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('home')">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 稿件详情内容 -->
    <main class="journal-detail-content">
      <div class="journal-detail-wrapper">
        <button class="back-btn" @click="goBack">← 返回</button>
        
        <div class="journal-detail-header">
          <h2 class="journal-title">{{ journal.title }}</h2>
          <div class="journal-meta">
            <span class="meta-item">作者：{{ journal.author }}</span>
            <span class="meta-item">投稿日期：{{ journal.date }}</span>
            <span class="meta-item status" :class="journal.status.toLowerCase()">{{ journal.status }}</span>
            <span class="meta-item">审稿阶段：{{ journal.reviewStage || '未明确' }}</span>
          </div>
        </div>

        <div class="journal-detail-body">
          <!-- 左侧：论文详情 -->
          <div class="journal-main-content">
            <section class="detail-section">
              <h3 class="section-title">摘要</h3>
              <div class="section-content" v-html="journal.abstract"></div>
            </section>

            <section class="detail-section">
              <h3 class="section-title">关键词</h3>
              <p class="section-content keywords">{{ journal.keywords }}</p>
            </section>

            <section class="detail-section">
              <h3 class="section-title">正文</h3>
              <div class="section-content content" v-html="journal.content"></div>
            </section>
          </div>
          
          <!-- 右侧：审核记录 -->
          <div class="journal-sidebar">
            <div class="review-records-section">
              <h3 class="section-title">审核记录</h3>
              
              <!-- 审核记录列表 -->
              <div class="review-records-list">
                <div v-if="journalReviewRecords.length === 0" class="no-records">
                  <p>暂无审核记录</p>
                </div>
                
                <div 
                  v-for="record in journalReviewRecords" 
                  :key="record.id" 
                  class="review-record-item"
                >
                  <div class="record-header">
                    <div class="record-stage">{{ record.reviewStage }}</div>
                    <div class="record-result" :class="record.reviewResult.toLowerCase()">
                      {{ record.reviewResult }}
                    </div>
                  </div>
                  <div class="record-content">
                    <div class="record-meta">
                      <div class="reviewer-info">审核人：{{ record.reviewerId }}</div>
                      <div class="review-date">审核日期：{{ new Date(record.reviewDate).toLocaleDateString() }}</div>
                    </div>
                    <div class="review-comments">
                      <h4>审核建议：</h4>
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
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.journal-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 导航栏样式（与其他页面保持一致） */
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
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.back-btn:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
}

.journal-detail-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #eee;
}

.journal-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.journal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.meta-item {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.meta-item.status {
  font-weight: 600;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
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
  gap: 2rem;
  align-items: flex-start;
}

/* 左侧主内容 */
.journal-main-content {
  flex: 1;
  min-width: 0;
}

/* 右侧边栏 */
.journal-sidebar {
  width: 350px;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
}

.review-records-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 审核记录项 */
.review-record-item {
  background: white;
  padding: 1.2rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 记录头部 */
.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #eee;
}

.record-stage {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.record-result {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
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
}

.reviewer-info {
  font-weight: 500;
}

.review-date {
  font-size: 0.85rem;
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
}

/* 无记录状态 */
.no-records {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-style: italic;
  background: white;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

/* 详情部分通用样式 */
.detail-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.section-content {
  color: #555;
  line-height: 1.6;
  margin: 0;
  font-size: 1rem;
}

.section-content.keywords {
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 5px;
  font-weight: 500;
}

.section-content.content {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 5px;
}

/* 富文本格式支持 */
.section-content.content h1,
.section-content.content h2,
.section-content.content h3,
.section-content.content h4,
.section-content.content h5,
.section-content.content h6 {
  margin: 1.5rem 0 1rem 0;
  font-weight: 600;
  line-height: 1.3;
}

.section-content.content h1 {
  font-size: 2rem;
}

.section-content.content h2 {
  font-size: 1.75rem;
}

.section-content.content h3 {
  font-size: 1.5rem;
}

.section-content.content h4 {
  font-size: 1.25rem;
}

.section-content.content h5 {
  font-size: 1.1rem;
}

.section-content.content h6 {
  font-size: 1rem;
}

.section-content.content p {
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.section-content.content ul,
.section-content.content ol {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.section-content.content ul {
  list-style-type: disc;
}

.section-content.content ol {
  list-style-type: decimal;
}

.section-content.content li {
  margin: 0.5rem 0;
  line-height: 1.6;
}

/* 对齐样式 */
.section-content.content .ql-align-center {
  text-align: center;
}

.section-content.content .ql-align-right {
  text-align: right;
}

.section-content.content .ql-align-justify {
  text-align: justify;
}

.section-content.content .ql-align-left {
  text-align: left;
}

/* 缩进样式 */
.section-content.content .ql-indent-1 {
  margin-left: 2rem;
}

.section-content.content .ql-indent-2 {
  margin-left: 4rem;
}

.section-content.content .ql-indent-3 {
  margin-left: 6rem;
}

.section-content.content pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.8;
}

/* 链接样式 */
.section-content.content a {
  color: #3498db;
  text-decoration: underline;
}

.section-content.content a:hover {
  color: #2980b9;
}

/* 图片样式 */
.section-content.content img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border-radius: 5px;
}

/* 代码块样式 */
.section-content.content pre.ql-syntax {
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
.section-content.content blockquote {
  border-left: 4px solid #3498db;
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: #666;
}

/* 水平分隔线样式 */
.section-content.content hr {
  border: none;
  border-top: 2px solid #eee;
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
  }
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
