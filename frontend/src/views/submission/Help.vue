<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useI18n } from '../../composables/useI18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()
const user = ref(userStore.user)

// --- State ---
const searchQuery = ref('')
const activeCategory = ref('dashboard')
const expandedFaqs = ref([])
const favorites = ref([]) // IDs of favorite articles

// --- Data ---
const categories = [
  { id: 'dashboard', name: t('submission.help.categories.dashboard') },
  { id: 'manuscripts', name: t('submission.help.categories.manuscripts') },
  { id: 'reviewers', name: t('submission.help.categories.reviewers') },
  { id: 'decisions', name: t('submission.help.categories.decisions') },
  { id: 'profile', name: t('submission.help.categories.profile') },
  { id: 'manual', name: t('submission.help.categories.manual') } // Special category
]

const articles = [
  { id: 101, category: 'dashboard', title: 'Understanding the Dashboard', content: 'Guide to dashboard widgets...' },
  { id: 102, category: 'manuscripts', title: 'How to batch invite reviewers?', steps: ['Go to Manuscripts', 'Select manuscript', 'Click Invite', 'Choose Reviewers', 'Send'] },
  { id: 103, category: 'manuscripts', title: 'Checking manuscript status', content: '...' },
  { id: 201, category: 'reviewers', title: 'Managing Reviewer Database', content: '...' },
  { id: 301, category: 'decisions', title: 'Drafting Decision Letters', content: '...' },
  // Manuals (Content filtered by role)
  { id: 901, category: 'manual', role: 'editor', title: 'Full Editor Manual', content: 'Complete guide for Editors...' },
  { id: 902, category: 'manual', role: 'associate_editor', title: 'Associate Editor Workflow', content: 'Guide for AEs...' },
  { id: 903, category: 'manual', role: 'ea_ae', title: 'EA Basics', content: 'Guide for EAs...' },
]

const faqs = ref([
  { id: 1, question: 'How do I reset my password?', answer: 'Go to login page and click Forgot Password.', likes: 120 },
  { id: 2, question: 'Can I change my role?', answer: 'Contact the administrator.', likes: 85 },
  { id: 3, question: 'What formats are supported?', answer: 'PDF, Word, LaTeX.', likes: 200 }
])

// --- Computed ---
const filteredArticles = computed(() => {
  if (activeCategory.value === 'manual') {
    // Role-based filtering for Manual
    const role = user.value?.role
    if (role === 'editor' || role === 'admin') {
      return articles.filter(a => a.category === 'manual') // Show all manuals or specific one? Requirement says "Full Manual" for Editor
    } else if (role === 'associate_editor') {
      return articles.filter(a => a.category === 'manual' && a.role === 'associate_editor')
    } else {
      return articles.filter(a => a.category === 'manual' && a.role === 'ea_ae')
    }
  }
  
  // Normal categories
  let result = articles.filter(a => a.category === activeCategory.value)
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = articles.filter(a => 
      a.title.toLowerCase().includes(query) || 
      (a.content && typeof a.content === 'string' && a.content.toLowerCase().includes(query))
    )
  }
  return result
})

const sortedFaqs = computed(() => {
  return [...faqs.value].sort((a, b) => b.likes - a.likes)
})

const favoriteArticles = computed(() => {
  return articles.filter(a => favorites.value.includes(a.id))
})

// --- Methods ---
const toggleFaq = (id) => {
  const index = expandedFaqs.value.indexOf(id)
  if (index === -1) expandedFaqs.value.push(id)
  else expandedFaqs.value.splice(index, 1)
}

const likeFaq = (id) => {
  const faq = faqs.value.find(f => f.id === id)
  if (faq) faq.likes++
}

const toggleFavorite = (id) => {
  const index = favorites.value.indexOf(id)
  if (index === -1) favorites.value.push(id)
  else favorites.value.splice(index, 1)
  // Save to local storage or backend
  localStorage.setItem('help_favorites', JSON.stringify(favorites.value))
}

const isFavorite = (id) => favorites.value.includes(id)

onMounted(() => {
  const savedFavs = localStorage.getItem('help_favorites')
  if (savedFavs) favorites.value = JSON.parse(savedFavs)
})

const goBack = () => router.back()
</script>

<template>
  <div class="help-center">
    <!-- Header -->
    <header class="help-header">
      <div class="header-content">
        <h1>{{ t('submission.help.title') }}</h1>
        <div class="search-box">
          <input type="text" v-model="searchQuery" :placeholder="t('submission.help.search')">
          <button>{{ t('submission.help.searchBtn') }}</button>
        </div>
      </div>
    </header>

    <div class="container layout">
      <!-- Sidebar Navigation -->
      <aside class="sidebar">
        <nav>
          <ul>
            <li v-for="cat in categories" :key="cat.id" 
                :class="{ active: activeCategory === cat.id }"
                @click="activeCategory = cat.id">
              {{ cat.name }}
            </li>
            <li class="separator"></li>
            <li :class="{ active: activeCategory === 'favorites' }" @click="activeCategory = 'favorites'">
              {{ t('submission.help.favorites') }}
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="content">
        <!-- Favorites View -->
        <div v-if="activeCategory === 'favorites'">
          <h2>{{ t('submission.help.favorites') }}</h2>
          <div v-if="favoriteArticles.length === 0" class="empty-state">{{ t('submission.help.noFavorites') }}</div>
          <div class="article-list">
             <div v-for="article in favoriteArticles" :key="article.id" class="article-card">
              <h3>{{ article.title }}</h3>
              <p class="article-preview">{{ typeof article.content === 'string' ? article.content.substring(0, 100) + '...' : 'View steps...' }}</p>
              <div class="actions">
                <button @click="toggleFavorite(article.id)" class="btn-fav active">★ {{ t('submission.help.removeFav') }}</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Normal Category View -->
        <div v-else>
          <h2>{{ categories.find(c => c.id === activeCategory)?.name }}</h2>
          
          <div class="article-list">
            <div v-for="article in filteredArticles" :key="article.id" class="article-card">
              <div class="article-header">
                <h3>{{ article.title }}</h3>
                <button @click="toggleFavorite(article.id)" class="btn-fav" :class="{ active: isFavorite(article.id) }">
                  {{ isFavorite(article.id) ? '★' : '☆' }}
                </button>
              </div>
              
              <div class="article-body">
                <div v-if="Array.isArray(article.steps)">
                  <ol>
                    <li v-for="(step, i) in article.steps" :key="i">{{ step }}</li>
                  </ol>
                </div>
                <div v-else>
                  <p>{{ article.content }}</p>
                </div>
              </div>
            </div>
            <div v-if="filteredArticles.length === 0" class="empty-state">
              {{ t('submission.help.noArticles') }}
            </div>
          </div>
        </div>

        <!-- FAQ Section (Always visible at bottom or separate tab? Requirement says "FAQ Module", implies separate section or integrated. Let's put it at the bottom of Dashboard or separate) -->
        <!-- Requirement: "FAQ Module: Sorted by heat... expand/collapse... like" -->
        <!-- Let's add FAQ as a section if Dashboard is selected, or make it a global footer section -->
        <div v-if="activeCategory === 'dashboard'" class="faq-section">
          <h3>{{ t('submission.help.faq') }}</h3>
          <div class="faq-list">
            <div v-for="faq in sortedFaqs" :key="faq.id" class="faq-item">
              <div class="faq-question" @click="toggleFaq(faq.id)">
                <span>{{ faq.question }}</span>
                <span class="toggle-icon">{{ expandedFaqs.includes(faq.id) ? '−' : '+' }}</span>
              </div>
              <div v-if="expandedFaqs.includes(faq.id)" class="faq-answer">
                <p>{{ faq.answer }}</p>
                <div class="faq-footer">
                  <button @click="likeFaq(faq.id)" class="btn-like">👍 {{ faq.likes }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.help-center {
  background-color: #f5f7fa;
  min-height: 100vh;
}

.help-header {
  background-color: #2c3e50;
  color: white;
  padding: 2rem 0;
  text-align: center;
}

.search-box {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.search-box input {
  padding: 0.5rem 1rem;
  width: 300px;
  border-radius: 4px;
  border: none;
}

.search-box button {
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.layout {
  display: flex;
  margin-top: 2rem;
  gap: 2rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 1rem;
}

.sidebar {
  width: 250px;
  flex-shrink: 0;
}

.sidebar nav ul {
  list-style: none;
  padding: 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sidebar nav li {
  padding: 1rem;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.sidebar nav li:hover {
  background-color: #f9f9f9;
}

.sidebar nav li.active {
  background-color: #e8f4fc;
  color: #3498db;
  font-weight: 600;
  border-left: 3px solid #3498db;
}

.sidebar nav li.separator {
  height: 10px;
  background: #f5f7fa;
  border: none;
  padding: 0;
  cursor: default;
}

.content {
  flex-grow: 1;
}

.article-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.article-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-fav {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #ccc;
}

.btn-fav.active {
  color: #f1c40f;
}

.faq-section {
  margin-top: 3rem;
}

.faq-item {
  background: white;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.faq-question {
  padding: 1rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  color: #34495e;
}

.faq-answer {
  padding: 1rem;
  border-top: 1px solid #eee;
  background-color: #fafafa;
}

.btn-like {
  margin-top: 0.5rem;
  padding: 0.3rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-like:hover {
  background: #f0f0f0;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>
