<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { platformJournalApi } from '@/utils/api'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const journalInfo = ref({})
const publishedArticles = ref([])
const loading = ref(false)

const loadJournalData = async () => {
  const journalId = route.params.id
  if (!journalId) return

  loading.value = true
  try {
    // 高效并发：同时获取期刊基础信息和它名下的所有论文
    const [infoRes, articlesRes] = await Promise.all([
      platformJournalApi.getJournal(journalId),
      platformJournalApi.getArticles({ journal_id: journalId, status: 'published' })
    ])
    
    journalInfo.value = infoRes.data || {}
    publishedArticles.value = articlesRes.data?.items || articlesRes.data || []
  } catch (error) {
    console.error('[Public API Error]: Failed to load journal details', error)
  } finally {
    loading.value = false
  }
}

// 导航至单篇文献的详情（PDF/HTML 阅读页）
const readArticle = (articleId) => {
  router.push(`/articles/${articleId}`)
}

onMounted(loadJournalData)
</script>

<template>
  <div class="journal-detail-container" v-if="!loading">
    <header class="journal-header">
      <h1>{{ journalInfo.title }}</h1>
      <p v-if="journalInfo.eic_name">Editor-in-Chief: {{ journalInfo.eic_name }}</p>
      <p v-if="journalInfo.issn">ISSN: {{ journalInfo.issn }}</p>
    </header>

    <section class="published-articles">
      <h2>{{ t('nav.latestArticles') || 'Latest Articles' }}</h2>
      <ul class="article-list" v-if="publishedArticles.length > 0">
        <li v-for="article in publishedArticles" :key="article.id">
          <h4 @click="readArticle(article.id)">{{ article.title }}</h4>
          <div class="meta">
            <span>{{ article.authors }}</span> •
            <span>{{ article.publish_date }}</span>
          </div>
        </li>
      </ul>
      <div v-else class="empty-state">
        {{ t('common.noData') || 'No published articles found.' }}
      </div>
    </section>
  </div>
  
  <div v-else class="loading-state">
    {{ t('common.loading') || 'Loading...' }}
  </div>
</template>

<style scoped>
.journal-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.journal-header {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 40px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.journal-header h1 {
  font-size: 2.5rem;
  color: #0056B3;
  margin-bottom: 10px;
}

.journal-header p {
  font-size: 1rem;
  color: #666;
  margin: 5px 0;
}

.published-articles {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.published-articles h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 30px;
  border-bottom: 2px solid #0056B3;
  padding-bottom: 10px;
}

.article-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.article-list li {
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.3s;
}

.article-list li:hover {
  background: #f9f9f9;
  padding-left: 10px;
}

.article-list li:last-child {
  border-bottom: none;
}

.article-list h4 {
  font-size: 1.2rem;
  color: #0056B3;
  margin-bottom: 10px;
}

.article-list .meta {
  font-size: 0.9rem;
  color: #666;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #666;
}
</style>
