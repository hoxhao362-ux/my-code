<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-news-latest'"
      :logout="userStore.logout"
    />
    <div class="header">
      <h1>Latest Articles</h1>
      <div class="filters">
        <select v-model="filterSubject">
          <option value="all">All Subjects</option>
          <option value="medicine">Medicine</option>
          <option value="biology">Biology</option>
        </select>
        <div class="checkboxes">
          <label><input type="checkbox" v-model="filterTypes" value="research" /> Research</label>
          <label><input type="checkbox" v-model="filterTypes" value="review" /> Review</label>
        </div>
      </div>
    </div>

    <div class="article-list">
      <div v-for="article in filteredArticles" :key="article.id" class="article-item">
        <h2 class="article-title" @click="viewAbstract(article.id)">{{ article.title }}</h2>
        <div class="article-meta">
          <span>{{ article.writers }}</span> | <span>{{ article.date }}</span>
        </div>
        <p class="article-abstract">{{ article.abstract }}</p>
        
        <div class="article-actions">
          <div class="share-icons">
            <span class="icon" title="Share on ResearchGate">RG</span>
            <span class="icon" title="Share on Twitter">Tw</span>
          </div>
          <button class="btn-read" @click="viewAbstract(article.id)">Read Abstract</button>
        </div>
      </div>
    </div>

    <div class="loading-trigger" ref="loadingTrigger">
      <div v-if="loading" class="spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const router = useRouter()
const filterSubject = ref('all')
const filterTypes = ref(['research', 'review'])
const articles = ref([])
const loading = ref(false)
const page = ref(1)

// Mock Data Generation
const generateArticles = (count) => {
  const newArticles = []
  for (let i = 0; i < count; i++) {
    const id = articles.value.length + i + 1
    newArticles.push({
      id,
      title: `Global Health Impact of Climate Change: A Systematic Review (Part ${id})`,
      writers: 'Smith J., Doe A., et al.',
      date: '2026-02-01',
      abstract: 'This study explores the correlation between rising temperatures and vector-borne diseases...',
      subject: id % 2 === 0 ? 'medicine' : 'biology',
      type: id % 3 === 0 ? 'review' : 'research'
    })
  }
  return newArticles
}

const loadMore = () => {
  if (loading.value) return
  loading.value = true
  setTimeout(() => {
    articles.value.push(...generateArticles(5))
    loading.value = false
    page.value++
  }, 1000)
}

const filteredArticles = computed(() => {
  return articles.value.filter(a => {
    const subjectMatch = filterSubject.value === 'all' || a.subject === filterSubject.value
    const typeMatch = filterTypes.value.includes(a.type)
    return subjectMatch && typeMatch
  })
})

const viewAbstract = (id) => {
  // Use existing route or mock
  router.push(`/journal/${id}`) // Assuming this route exists
}

// Intersection Observer for Infinite Scroll
const loadingTrigger = ref(null)
let observer = null

onMounted(() => {
  articles.value = generateArticles(10) // Initial load

  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      loadMore()
    }
  })
  
  if (loadingTrigger.value) {
    observer.observe(loadingTrigger.value)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 80px auto 0;
  padding: 40px 24px;
}

.header {
  margin-bottom: 40px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 24px;
  align-items: center;
  border-bottom: 1px solid #E5E5E5;
  padding-bottom: 16px;
}

select {
  padding: 8px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
}

.checkboxes {
  display: flex;
  gap: 16px;
}

.article-item {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E5E5E5;
}

.article-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  margin-bottom: 8px;
  transition: color 0.3s;
}

.article-title:hover {
  color: #C93737;
}

.article-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.article-abstract {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.article-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.share-icons .icon {
  font-size: 14px;
  color: #999;
  margin-right: 12px;
  cursor: pointer;
  font-weight: bold;
}

.share-icons .icon:hover {
  color: #C93737;
}

.btn-read {
  padding: 6px 12px;
  border: 1px solid #C93737;
  color: #C93737;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-read:hover {
  background: #C93737;
  color: white;
}

.loading-trigger {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #E5E5E5;
  border-top-color: #C93737;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
