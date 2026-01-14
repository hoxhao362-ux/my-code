<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import Navigation from '../components/Navigation.vue'
import { exportJournalToPDF, checkExportPermission } from '../utils/export'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const route = useRoute()
const router = useRouter()
const journalId = computed(() => route.params.id)

// 返回上一页
const goBack = () => {
  router.back()
  // 使用setTimeout确保路由切换完成后再打开目录
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
  return userStore.journals.find(j => {
    // 转换id类型为字符串进行比较，解决类型不匹配问题
    return String(j.id) === String(journalId.value)
  })
})

// 获取当前用户
const user = computed(() => userStore.user)

// 导出期刊
const handleExportJournal = () => {
  if (journal.value) {
    exportJournalToPDF(journal.value)
  }
}

// 检查是否有导出权限
const canExport = computed(() => {
  if (!journal.value || !user.value) return false
  return checkExportPermission(user.value.role, 'journal', journal.value, user.value.id)
})

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
      :current-page="'journal'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />
    
    <div v-if="journal" class="journal-detail-content">
      <!-- 头部卡片 -->
      <header class="journal-detail-header">
        <div class="header-actions">
          <button class="back-btn" @click="goBack">
            <span class="icon">←</span> 返回
          </button>
          <button 
            v-if="canExport" 
            class="export-btn" 
            @click="handleExportJournal"
          >
            <span class="icon">📄</span> 导出PDF
          </button>
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
        </div>
      </header>

      <!-- 摘要卡片 -->
      <section class="journal-abstract card">
        <h2 class="section-title">摘要</h2>
        <p class="abstract-content">{{ journal.abstract }}</p>
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
    <!-- 未找到期刊 -->
    <div v-else class="no-journal card">
      <div class="no-journal-content">
        <div class="no-journal-icon">📄</div>
        <h2>未找到该期刊</h2>
        <p>抱歉，您访问的期刊不存在或已被删除</p>
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

/* 主内容区域 */
.journal-detail-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 头部卡片 */
.journal-detail-header {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
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

.journal-status.已通过 {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.journal-status.审稿中 {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.journal-status.待审核 {
  background: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.journal-status.未通过 {
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
  border-bottom: 3px solid #667eea;
  display: inline-block;
}

/* 摘要样式 */
.journal-abstract {
  margin-bottom: 0;
}

.abstract-content {
  font-size: 1.15rem;
  line-height: 1.8;
  color: #555;
  text-align: justify;
  background: rgba(102, 126, 234, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid #667eea;
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
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.5rem 1.25rem;
  border-radius: 24px;
  font-size: 0.95rem;
  font-weight: 600;
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.keyword-tag:hover {
  background: #667eea;
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

/* 正文样式 */
.journal-content {
  margin-bottom: 0;
  line-height: 1.8;
  color: #333;
  font-size: 1.15rem;
}

.content-body {
  background: rgba(118, 75, 162, 0.03);
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid rgba(118, 75, 162, 0.1);
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