<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()

// 投稿历史筛选状态
const selectedModule = ref('all')
const timeRange = ref('all')
const isExpanded = ref(false)

// 用户投稿历史筛选
const userJournals = computed(() => {
  let filtered = userStore.userJournals
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    filtered = filtered.filter(journal => journal.module === selectedModule.value)
  }
  
  // 时间范围筛选
  const now = new Date()
  let startDate
  switch (timeRange.value) {
    case 'today':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      break
    case 'week':
      startDate = new Date(now.setDate(now.getDate() - 7))
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
      break
    case 'year':
      startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
      break
    default:
      startDate = null
  }
  
  if (startDate) {
    filtered = filtered.filter(journal => new Date(journal.date) >= startDate)
  }
  
  // 按时间降序排序
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

// 显示的投稿列表（最近3篇或全部）
const displayedSubmissions = computed(() => {
  if (isExpanded.value) {
    return userJournals.value
  } else {
    return userJournals.value.slice(0, 3)
  }
})

// 查看稿件详情
const viewJournalDetail = (id) => {
  router.push(`/journal/${id}`)
}
</script>

<template>
  <div class="history-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'author-history'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 投稿历史内容 -->
    <main class="history-content">
      <div class="section-header">
        <h2 class="section-title">投稿历史</h2>
      </div>
      
      <!-- 筛选控件 -->
      <div class="submission-filters">
        <label for="module-filter">模块筛选：</label>
        <select 
          id="module-filter" 
          v-model="selectedModule"
          class="filter-select"
        >
          <option value="all">全部模块</option>
          <option 
            v-for="module in userStore.modules" 
            :key="module" 
            :value="module"
          >
            {{ module }}
          </option>
        </select>
        
        <label for="time-filter">时间范围：</label>
        <select 
          id="time-filter" 
          v-model="timeRange"
          class="filter-select"
        >
          <option value="all">全部时间</option>
          <option value="today">今日</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="year">本年</option>
        </select>
      </div>
      
      <div v-if="userJournals.length > 0" class="submission-list">
        <div 
          v-for="submission in displayedSubmissions" 
          :key="submission.id" 
          class="submission-item"
        >
          <div class="submission-info">
            <h4 class="submission-title" @click="viewJournalDetail(submission.id)">{{ submission.title }}</h4>
            <p class="submission-meta">投稿日期：{{ submission.date }} | 模块：{{ submission.module }}</p>
          </div>
          <div class="submission-actions">
            <div class="submission-status" :class="submission.status.toLowerCase()">
              {{ submission.status }}
            </div>
          </div>
        </div>
        
        <!-- 展开/收起按钮 -->
        <div v-if="userJournals.length > 3" class="expand-section">
          <button 
            class="btn btn-expand" 
            @click="isExpanded = !isExpanded"
          >
            {{ isExpanded ? '收起' : `展开全部（共${userJournals.length}篇）` }}
          </button>
        </div>
      </div>
      
      <div v-else class="no-submissions">
        <p>您还没有投稿记录</p>
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
/* 样式可以从原 Profile.vue 组件中的投稿历史部分复制 */
</style>