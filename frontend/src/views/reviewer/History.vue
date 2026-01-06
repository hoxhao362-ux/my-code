<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 已审核的稿件列表
const reviewedJournals = computed(() => {
  return userStore.journals.filter(journal => journal.status !== '审稿中')
})
</script>

<template>
  <div class="reviewer-history-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'reviewer-history'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 审核历史内容 -->
    <main class="content">
      <div class="header">
        <h1>审核历史</h1>
      </div>

      <section class="journals-section">
        <div class="journals-list">
          <div 
            v-for="journal in reviewedJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase()">
              {{ journal.status }}
            </div>
          </div>
          <div v-if="reviewedJournals.length === 0" class="no-journals">
            <p>当前没有审核历史记录</p>
          </div>
        </div>
      </section>
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
/* 样式可以从原组件复制或修改 */
</style>