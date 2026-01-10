<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import Navigation from '../components/Navigation.vue'

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
      <header class="journal-detail-header">
        <button class="back-btn" @click="goBack">返回</button>
        <h1 class="journal-title">{{ journal.title }}</h1>
        <div class="journal-meta">
          <p>作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
          <p>状态：<span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span> | 审核阶段：{{ journal.reviewStage || '未开始' }} | 审核结果：{{ journal.reviewResult || '待审核' }}</p>
        </div>
      </header>

      <section class="journal-abstract">
        <h2>摘要</h2>
        <p>{{ journal.abstract }}</p>
      </section>

      <section class="journal-keywords">
        <h2>关键词</h2>
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

      <section class="journal-content">
        <h2>正文</h2>
        <div v-html="journal.content"></div>
      </section>

      <!-- 审核历史记录 -->
      <section class="journal-review-history" v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
        <h2>审核历史记录</h2>
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
    </div>
    <div v-else class="no-journal">
      <p>未找到该稿件</p>
      <button class="btn btn-primary" @click="goBack">返回</button>
    </div>
  </div>
</template>

<style scoped>
.journal-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.journal-detail-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px; /* 为固定导航栏留出空间 */
}

.journal-detail-header {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.back-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.journal-title {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.journal-meta {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.95rem;
}

.journal-meta p {
  margin: 0.5rem 0;
}

.journal-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-weight: 500;
  font-size: 0.85rem;
}

.journal-status.待审核, .journal-status.审稿中 {
  background: #f39c12;
  color: white;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.未通过 {
  background: #e74c3c;
  color: white;
}

.journal-abstract, .journal-keywords, .journal-content, .journal-review-history {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.journal-abstract h2, .journal-keywords h2, .journal-content h2, .journal-review-history h2 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.journal-abstract p {
  line-height: 1.6;
  color: #555;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.keyword-tag {
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 500;
}

.journal-content {
  line-height: 1.8;
  color: #333;
}

.journal-content h3 {
  color: #2c3e50;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.journal-content p {
  margin-bottom: 1rem;
}

.journal-content ul, .journal-content ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.journal-content li {
  margin-bottom: 0.5rem;
}

.no-journal {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: white;
  margin: 2rem;
  padding: 3rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.no-journal p {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 2rem;
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

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* 审核历史记录样式 */
.review-history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-history-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.review-history-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.review-stage {
  font-weight: 600;
  color: #2c3e50;
}

.review-status {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-weight: 500;
  font-size: 0.85rem;
}

.review-status.已通过 {
  background: #2ecc71;
  color: white;
}

.review-status.未通过 {
  background: #e74c3c;
  color: white;
}

.review-date, .reviewer {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.review-comment {
  color: #555;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .journal-detail-content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .journal-detail-header {
    padding: 1.5rem;
  }
  
  .journal-title {
    font-size: 1.5rem;
  }
  
  .journal-abstract, .journal-keywords, .journal-content, .journal-review-history {
    padding: 1.5rem;
  }
  
  .review-history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
