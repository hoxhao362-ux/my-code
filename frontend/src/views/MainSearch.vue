<script setup>
import { ref } from 'vue'
import { useUserStore } from '../stores/user'
<<<<<<< HEAD
import { stripHtmlTags, truncateText } from '../utils/helpers.js'

const userStore = useUserStore()

// 搜索相关状态
=======
import Navigation from '../components/Navigation.vue'

const userStore = useUserStore()

// Search State
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
const searchKeyword = ref('')
const searchStatus = ref('all')
const searchModule = ref('all')
const searchResults = ref([])
<<<<<<< HEAD

// 过滤和排序期刊
const filterJournals = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
=======
const hasSearched = ref(false)

// Mock Data for demonstration (Ideally from Store)
// Using userStore.journals if available, else fallback
const journals = ref(userStore.journals || []) 

// Filter Logic
const filterJournals = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    hasSearched.value = true
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
<<<<<<< HEAD
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
=======
  searchResults.value = journals.value.filter(journal => {
    // Keyword Match
    const matchesKeyword = 
      (journal.title && journal.title.toLowerCase().includes(keyword)) ||
      (journal.author && journal.author.toLowerCase().includes(keyword)) ||
      (journal.id && journal.id.toString().includes(keyword))
    
    // Status Filter
    const matchesStatus = searchStatus.value === 'all' || journal.status === searchStatus.value
    
    // Module Filter (if applicable)
    // const matchesModule = searchModule.value === 'all' || journal.module === searchModule.value
    
    return matchesKeyword && matchesStatus
  })
  hasSearched.value = true
}

// Helper: Truncate Text
const truncateText = (text, length = 100) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// Helper: Strip HTML
const stripHtmlTags = (html) => {
  if (!html) return ''
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
}
</script>

<template>
<<<<<<< HEAD
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
            <p class="result-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
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
=======
  <div class="search-page-container">
    <Navigation :user="userStore.user" />
    
    <div class="search-content">
      <header class="search-header">
        <h1>Search Manuscripts</h1>
        <p>Find research by ID, title, or author</p>
      </header>

      <section class="search-bar-section">
        <div class="search-bar">
          <input
            type="text"
            v-model="searchKeyword"
            placeholder="Search by Manuscript ID, Title or Author..."
            class="search-input"
            @keyup.enter="filterJournals"
          />
          <button class="search-btn" @click="filterJournals">
            Search
          </button>
        </div>
        
        <!-- Search Filters (Optional) -->
        <div class="search-filters" style="display: none;">
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="searchStatus" class="filter-select">
              <option value="all">All</option>
              <option value="Published">Published</option>
            </select>
          </div>
        </div>
      </section>

      <!-- Search Results -->
      <section v-if="hasSearched" class="search-results">
        <div class="results-header">
          <h3>Search Results ({{ searchResults.length }})</h3>
        </div>
        
        <div v-if="searchResults.length > 0" class="results-list">
          <div 
            v-for="journal in searchResults" 
            :key="journal.id" 
            class="result-item"
          >
            <div class="result-info">
              <h4 class="result-title">{{ journal.title }}</h4>
              <p class="result-meta">
                ID: {{ journal.id }} | Author: {{ journal.author }} | Date: {{ journal.date }}
              </p>
              <p class="result-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
            </div>
            <div class="result-actions">
               <button class="action-btn">View Details</button>
            </div>
          </div>
        </div>
        
        <div v-else class="no-results">
          <p>No matching results found</p>
        </div>
      </section>
    </div>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  </div>
</template>

<style scoped>
<<<<<<< HEAD
/* 样式可以从原 Home.vue 组件中的搜索部分复制 */
=======
.search-page-container {
  min-height: 100vh;
  background-color: #f9f9f9;
}

.search-content {
  max-width: 800px;
  margin: 80px auto 0;
  padding: 2rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.search-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.search-header p {
  color: #7f8c8d;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.search-btn {
  padding: 0 25px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.search-btn:hover {
  background-color: #2980b9;
}

.result-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-info {
  flex: 1;
}

.result-title {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.result-meta {
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 0.5rem;
}

.result-abstract {
  color: #555;
  font-size: 0.95rem;
}

.action-btn {
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #3498db;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
}

.action-btn:hover {
  background-color: #f0f8ff;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #999;
  background: white;
  border-radius: 8px;
}
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
</style>