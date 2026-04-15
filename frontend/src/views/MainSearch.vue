<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useUserStore } from '../stores/user'
import Navigation from '../components/Navigation.vue'

const router = useRouter()
const { t } = useI18n()
const userStore = useUserStore()

// Search State
const searchKeyword = ref('')
const searchStatus = ref('all')
const searchModule = ref('all')
const searchResults = ref([])
const hasSearched = ref(false)

// Mock Data for demonstration (Ideally from Store)
// Using userStore.journals if available, else fallback
const journals = ref(userStore.journals || []) 

// Filter Logic
const filterJournals = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    hasSearched.value = true
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
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
}
</script>

<template>
  <div class="search-page-container">
    <Navigation :user="userStore.user" />
    
    <div class="search-content">
      <header class="search-header">
        <h1>{{ t('search.title') }}</h1>
        <p>{{ t('search.subtitle') }}</p>
      </header>

      <section class="search-bar-section">
        <div class="search-bar">
          <input
            type="text"
            v-model="searchKeyword"
            :placeholder="t('search.placeholder')"
            class="search-input"
            @keyup.enter="filterJournals"
          />
          <button class="search-btn" @click="filterJournals">
            {{ t('search.button') }}
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
          <h3>{{ t('search.results', { count: searchResults.length }) }}</h3>
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
                {{ t('search.meta', { id: journal.id, author: journal.author, date: journal.date }) }}
              </p>
              <p class="result-abstract">{{ truncateText(stripHtmlTags(journal.abstract)) }}</p>
            </div>
            <div class="result-actions">
                <button class="action-btn" @click="router.push(`/journal/${journal.id}`)">{{ t('search.viewDetails') }}</button>
              </div>
          </div>
        </div>
        
        <div v-else class="no-results">
          <p>{{ t('search.noResults') }}</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
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
</style>