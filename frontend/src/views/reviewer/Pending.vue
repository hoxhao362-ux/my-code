<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 待审核的稿件列表
const pendingJournals = computed(() => userStore.pendingJournals)
</script>

<template>
  <div class="reviewer-pending-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'reviewer-pending'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 待审核稿件内容 -->
    <main class="content">
      <div class="header">
        <h1>待审核稿件</h1>
      </div>

      <section class="journals-section">
        <div class="journals-list">
          <div 
            v-for="journal in pendingJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
            </div>
            <div class="journal-actions">
              <button class="action-btn review-btn">开始审核</button>
            </div>
          </div>
          <div v-if="pendingJournals.length === 0" class="no-journals">
            <p>当前没有待审核的稿件</p>
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