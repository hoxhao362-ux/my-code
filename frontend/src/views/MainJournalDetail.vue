<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import Navigation from '../components/Navigation.vue'

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
      <header class="journal-detail-header">
        <button class="back-btn" @click="goBack">返回</button>
        <h1 class="journal-title">{{ journal.title }}</h1>
        <div class="journal-meta">
          <p>作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
          <p>状态：<span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span></p>
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
    </div>
    <div v-else class="no-journal">
      <p>未找到该期刊</p>
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
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.journal-detail-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.journal-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.journal-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #7f8c8d;
  font-size: 1rem;
}

.journal-status {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  display: inline-block;
  margin-right: 1rem;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.审稿中 {
  background: #3498db;
  color: white;
}

.journal-status.未通过 {
  background: #e74c3c;
  color: white;
}

/* 返回按钮样式 */
.back-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  display: inline-block;
}

.back-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.back-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.journal-abstract {
  margin-bottom: 2rem;
}

.journal-abstract h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.journal-abstract p {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #555;
  text-align: justify;
}

.journal-keywords {
  margin-bottom: 2rem;
}

.journal-keywords h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.keyword-tag {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 0.35rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.keyword-tag:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.journal-content {
  margin-bottom: 2rem;
  line-height: 1.8;
  color: #333;
  font-size: 1.1rem;
}

.journal-content h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 2rem 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.journal-content h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 1.5rem 0 1rem 0;
}

.journal-content p {
  margin-bottom: 1.5rem;
  text-align: justify;
}

.journal-content ul, .journal-content ol {
  margin-bottom: 1.5rem;
  padding-left: 2rem;
}

.journal-content li {
  margin-bottom: 0.75rem;
}

.no-journal {
  text-align: center;
  padding: 4rem 2rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px dashed #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .journal-detail-content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .journal-title {
    font-size: 1.6rem;
  }
  
  .journal-meta {
    font-size: 0.9rem;
  }
  
  .journal-abstract p {
    font-size: 1rem;
  }
  
  .journal-content {
    font-size: 1rem;
  }
}
</style>