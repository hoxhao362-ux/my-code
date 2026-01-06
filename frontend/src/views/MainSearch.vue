<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

// 搜索相关状态
const searchKeyword = ref('')
const searchStatus = ref('all')
const searchModule = ref('all')
const searchResults = ref([])

// 过滤和排序期刊
const filterJournals = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  searchResults.value = userStore.journals.filter(journal => {
    // 关键词搜索
    const matchesKeyword = 
      journal.title.toLowerCase().includes(keyword) ||
      journal.author.toLowerCase().includes(keyword) ||
      journal.abstract.toLowerCase().includes(keyword) ||
      journal.keywords.some(k => k.toLowerCase().includes(keyword)) ||
      journal.module.toLowerCase().includes(keyword)
    
    // 状态筛选
    const matchesStatus = searchStatus.value === 'all' || journal.status === searchStatus.value
    
    // 模块筛选
    const matchesModule = searchModule.value === 'all' || journal.module === searchModule.value
    
    return matchesKeyword && matchesStatus && matchesModule
  })
}
</script>

<template>
  <div class="search-container">
    <header class="search-header">
      <h1>期刊搜索</h1>
    </header>

    <section class="search-bar-section">
      <div class="search-bar">
        <input
          type="text"
          v-model="searchKeyword"
          placeholder="请输入关键词搜索论文..."
          class="search-input"
          @keyup.enter="filterJournals"
        />
        <button class="search-btn" @click="filterJournals">
          <span class="search-icon">🔍</span> 搜索
        </button>
      </div>
      
      <!-- 搜索筛选条件 -->
      <div class="search-filters">
        <div class="filter-group">
          <label for="status-filter">状态：</label>
          <select 
            id="status-filter" 
            v-model="searchStatus" 
            class="filter-select"
            @change="filterJournals"
          >
            <option value="all">全部状态</option>
            <option value="已通过">已通过</option>
            <option value="审稿中">审稿中</option>
            <option value="未通过">未通过</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="module-filter">模块：</label>
          <select 
            id="module-filter" 
            v-model="searchModule" 
            class="filter-select"
            @change="filterJournals"
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
        </div>
      </div>
    </section>

    <!-- 搜索结果展示 -->
    <section v-if="searchKeyword" class="search-results">
      <div class="results-header">
        <h3>搜索结果 ({{ searchResults.length }})</h3>
      </div>
      <div v-if="searchResults.length > 0" class="results-list">
        <div 
          v-for="journal in searchResults" 
          :key="journal.id" 
          class="result-item"
        >
          <div class="result-info">
            <h4 class="result-title">{{ journal.title }}</h4>
            <p class="result-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            <p class="result-abstract">{{ journal.abstract }}</p>
            <div class="result-keywords">
              <span 
                v-for="(keyword, index) in journal.keywords" 
                :key="index" 
                class="keyword-tag"
              >
                {{ keyword }}
              </span>
            </div>
          </div>
          <div class="result-actions">
              <button class="action-btn detail-btn">
                查看详情
              </button>
            </div>
        </div>
      </div>
      <div v-else class="no-results">
        <p>没有找到匹配的论文</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* 样式可以从原 Home.vue 组件中的搜索部分复制 */
</style>