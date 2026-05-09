<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlatformStore } from '../stores/platform'
import { useUserStore } from '../stores/user'
import { platformJournalApi } from '../utils/api'
import Navigation from '../components/Navigation.vue'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const router = useRouter()
const platformStore = usePlatformStore()
const userStore = useUserStore()
const { t } = useI18n()

const journalId = computed(() => route.params.id)
const currentJournal = computed(() => platformStore.currentJournal)
const loading = computed(() => platformStore.loading)

// 最新文章列表（从后端获取）
const recentArticles = ref([])
const articlesLoading = ref(false)

onMounted(async () => {
  if (journalId.value) {
    await platformStore.setJournal(journalId.value)
    await fetchArticles()
  }
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await platformStore.setJournal(newId)
    await fetchArticles()
  }
})

const fetchArticles = async () => {
  articlesLoading.value = true
  try {
    const res = await platformJournalApi.getArticles({
      journal_id: journalId.value,
      page: 1,
      page_size: 4
    })
    const data = res.data || res
    recentArticles.value = data.items || data || []
  } catch (error) {
    console.error('获取文章列表失败:', error)
    recentArticles.value = []
  } finally {
    articlesLoading.value = false
  }
}

const goToSubmit = () => {
  router.push('/submission')
}

const goToFullText = (id) => {
  router.push(`/journal/${id}`)
}

const journalColor = computed(() => currentJournal.value?.color || '#003366')
</script>

<template>
  <div v-if="loading" class="loading-state">
    Loading Journal...
  </div>
  <div v-else-if="currentJournal" class="home-container" :style="{ '--primary-color': journalColor }">
    <!-- Top Bar -->
    <div class="top-bar" :style="{ backgroundColor: journalColor }">
      <div class="top-bar-content">
        <router-link to="/" class="hub-link">← Return to Journal Hub</router-link>
        <span>{{ currentJournal.name }} - ISSN: {{ currentJournal.issn }}</span>
      </div>
    </div>

    <!-- Navigation (Reused, might need adaptation) -->
    <!-- For now, we wrap it or just use a simplified header for the journal view -->
    <header class="journal-header">
      <div class="container">
        <div class="journal-brand">
            <h1 :style="{ color: journalColor }">{{ currentJournal.name }}</h1>
        </div>
        <nav class="journal-nav">
            <a href="#">Home</a>
            <a href="#">Articles</a>
            <a href="#">Authors</a>
            <a href="#">About</a>
            <button class="submit-btn" :style="{ backgroundColor: journalColor }" @click="goToSubmit">Submit Paper</button>
        </nav>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h2 class="hero-title" :style="{ color: journalColor }">{{ currentJournal.description }}</h2>
          <p class="hero-subtitle">Leading the way in {{ currentJournal.name }} research and clinical practice.</p>
        </div>
        <div class="hero-graphic" :style="{ backgroundColor: journalColor, opacity: 0.1 }">
          <!-- Placeholder -->
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Latest Articles -->
      <section class="latest-articles-section">
        <h2 class="section-title" :style="{ borderColor: journalColor }">Latest Articles</h2>
        <div v-if="articlesLoading" class="articles-loading">Loading articles...</div>
        <div v-else class="articles-grid">
          <div 
            v-for="article in recentArticles" 
            :key="article.id || article.jid || article.article_id" 
            class="article-card"
          >
            <div class="article-category" :style="{ color: journalColor }">{{ article.module || article.subject || 'Research' }}</div>
            <h3 class="article-title clickable" @click="goToFullText(article.id || article.jid || article.article_id)">{{ article.title }}</h3>
            <p class="article-meta">{{ article.date || article.publish_date || article.create_time || 'N/A' }}</p>
            <p class="article-author">{{ article.author || article.authors || 'N/A' }}</p>
          </div>
        </div>
      </section>
      
      <!-- Journal Specific Info -->
      <section class="info-section">
        <div class="info-card">
            <h3>Impact Factor</h3>
            <p class="big-number" :style="{ color: journalColor }">{{ currentJournal.impactFactor }}</p>
        </div>
        <div class="info-card">
            <h3>Editor-in-Chief</h3>
            <p>{{ currentJournal.editorInChief }}</p>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; {{ new Date().getFullYear() }} {{ currentJournal.name }}. Part of the Journal Platform Network.</p>
      </div>
    </footer>
  </div>
  <div v-else class="error-state">
    Journal not found. <router-link to="/">Return to Hub</router-link>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #FFFFFF;
  color: #333333;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.top-bar {
  height: 30px;
  color: white;
  font-size: 12px;
}

.top-bar-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hub-link {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
}

.hub-link:hover {
  color: white;
}

.journal-header {
    border-bottom: 1px solid #eee;
    padding: 20px 0;
}

.journal-header .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.journal-brand h1 {
    margin: 0;
    font-size: 28px;
    font-family: 'Times New Roman', serif;
}

.journal-nav {
    display: flex;
    gap: 20px;
    align-items: center;
}

.journal-nav a {
    text-decoration: none;
    color: #555;
    font-weight: 500;
}

.submit-btn {
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.hero-section {
  padding: 60px 0;
  background-color: #f9f9f9;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.hero-text {
  flex: 1;
}

.hero-title {
  font-size: 36px;
  font-family: 'Times New Roman', serif;
  margin-bottom: 20px;
}

.hero-graphic {
  width: 200px;
  height: 200px;
  border-radius: 50%;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  width: 100%;
}

.section-title {
    font-size: 24px;
    border-bottom: 2px solid #ccc;
    padding-bottom: 10px;
    margin-bottom: 30px;
    font-family: 'Times New Roman', serif;
}

.articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
}

.article-card {
    border: 1px solid #eee;
    padding: 20px;
    border-radius: 4px;
    transition: box-shadow 0.2s;
}

.article-card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.article-category {
    font-size: 12px;
    text-transform: uppercase;
    margin-bottom: 10px;
    font-weight: bold;
}

.article-title {
    font-size: 18px;
    margin-bottom: 10px;
    line-height: 1.4;
    cursor: pointer;
}

.article-title:hover {
    text-decoration: underline;
}

.article-meta {
    font-size: 13px;
    color: #777;
    margin-bottom: 5px;
}

.article-author {
    font-size: 13px;
    color: #555;
    font-style: italic;
}

.info-section {
    display: flex;
    gap: 40px;
    margin-top: 60px;
    background: #f5f5f5;
    padding: 40px;
    border-radius: 8px;
}

.info-card h3 {
    margin-top: 0;
    font-size: 14px;
    text-transform: uppercase;
    color: #777;
}

.big-number {
    font-size: 48px;
    font-weight: bold;
    margin: 10px 0 0;
    font-family: 'Times New Roman', serif;
}

.footer {
    margin-top: auto;
    background: #333;
    color: white;
    padding: 40px 0;
    text-align: center;
}

.loading-state, .error-state {
    padding: 100px;
    text-align: center;
    font-size: 18px;
}
</style>
