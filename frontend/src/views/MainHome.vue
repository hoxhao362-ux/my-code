<script setup>
import { ref, computed } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const router = useRouter()

const goToSubmit = () => {
  router.push('/submission')
}

const goToFullText = (id) => {
  router.push(`/journal/${id}`)
}

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 从userStore获取公告数据
const announcements = computed(() => userStore.announcements)

// 近期投稿列表（取前4条）
const recentJournals = computed(() => {
  return userStore.journals.slice(0, 4)
})

// 最近浏览量最高的四篇作品
const topViewedJournals = computed(() => {
  return [...userStore.journals]
    .sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
    .slice(0, 4)
})

// 搜索相关状态
const searchKeyword = ref('')
const searchStatus = ref('all')
const searchModule = ref('all')
const searchResults = ref([])
const showSearchResults = ref(false)
</script>

<template>
  <div class="home-container">
    <!-- 顶部极窄顶条 -->
    <div class="top-bar">
      <div class="top-bar-content">
        <span>{{ t('home.topBar') }}</span>
      </div>
    </div>

    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'home'"
      :logout="userStore.logout"
    />

    <!-- 首屏核心视觉区 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">{{ t('home.hero.title') }}</h1>
          <p class="hero-subtitle">{{ t('home.hero.subtitle') }}</p>
          <button 
            class="hero-submit-btn"
            @click="goToSubmit"
          >
            {{ t('home.hero.submit') }}
          </button>
        </div>
        <div class="hero-graphic">
          <!-- 学术类抽象图形占位 -->
          <div class="graphic-placeholder"></div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
      <!-- 最新文章 -->
      <section class="latest-articles-section">
        <h2 class="section-title">{{ t('home.sections.latestArticles') }}</h2>
        <div class="articles-grid">
          <div 
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="article-card"
          >
            <div class="article-category">{{ journal.module || 'Research' }}</div>
            <h3 class="article-title clickable" @click="goToFullText(journal.id)">{{ journal.title }}</h3>
            <p class="article-meta">{{ t('nav.logo') }} | {{ journal.date || journal.submissionDate }}</p>
            <p class="article-author">{{ t('allPending.author') }}: {{ journal.author }}</p>
          </div>
        </div>
      </section>

      <!-- 期刊家族 -->
      <section class="journal-family-section">
        <h2 class="section-title">{{ t('home.sections.journalFamily') }}</h2>
        <div class="journal-family-grid">
          <div class="journal-family-item">
            <h3 class="journal-family-name">{{ t('home.journalFamily.main') }}</h3>
          </div>
          <div class="journal-family-item">
            <h3 class="journal-family-name">{{ t('home.journalFamily.letters') }}</h3>
          </div>
          <div class="journal-family-item">
            <h3 class="journal-family-name">{{ t('home.journalFamily.reviews') }}</h3>
          </div>
          <div class="journal-family-item">
            <h3 class="journal-family-name">{{ t('home.journalFamily.caseReports') }}</h3>
          </div>
        </div>
      </section>

      <!-- 专题合集 -->
      <section class="special-collections-section">
        <div class="special-collections-content">
          <div class="special-collection-main">
            <h3 class="special-collection-title">{{ t('home.sections.specialCollections') }}: Emerging Research</h3>
          </div>
          <div class="special-collection-side">
            <div class="special-collection-item">
              <h4 class="special-collection-item-title">Research Methods</h4>
            </div>
            <div class="special-collection-item">
              <h4 class="special-collection-item-title">Clinical Trials</h4>
            </div>
          </div>
        </div>
      </section>

      <!-- 新闻与观点 -->
      <section class="news-views-section">
        <div class="news-views-content">
          <div class="news-main">
            <h3 class="news-title">{{ t('reviewerDashboard.announcements.title') }}</h3>
            <div 
              v-for="announcement in announcements.slice(0, 1)" 
              :key="announcement.id" 
              class="news-item"
            >
              <h4 class="news-item-title">{{ announcement.title }}</h4>
              <p class="news-item-content">{{ announcement.content }}</p>
            </div>
          </div>
          <div class="news-side">
            <h3 class="news-side-title">Latest Updates</h3>
            <div 
              v-for="announcement in announcements.slice(1, 3)" 
              :key="announcement.id" 
              class="news-side-item"
            >
              <h4 class="news-side-item-title">{{ announcement.title }}</h4>
              <p class="news-side-item-date">{{ announcement.date }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 订阅/推广区块 -->
      <section class="subscribe-section">
        <div class="subscribe-content">
          <h2 class="subscribe-title">{{ t('home.subscribe.title') }}</h2>
          <p class="subscribe-text">{{ t('home.subscribe.text') }}</p>
        </div>
      </section>
    </main>

    <!-- 底部区域 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-grid">
          <div class="footer-column">
            <h3 class="footer-column-title">{{ t('footer.about.title') }}</h3>
            <ul class="footer-links">
              <li><a href="#">{{ t('footer.about.us') }}</a></li>
              <li><a href="#">{{ t('footer.about.mission') }}</a></li>
              <li><a href="#">{{ t('footer.about.team') }}</a></li>
              <li><a href="#">{{ t('footer.about.contact') }}</a></li>
            </ul>
          </div>
          <div class="footer-column">
            <h3 class="footer-column-title">{{ t('footer.journals.title') }}</h3>
            <ul class="footer-links">
              <li><a href="#">{{ t('home.journalFamily.main') }}</a></li>
              <li><a href="#">{{ t('home.journalFamily.letters') }}</a></li>
              <li><a href="#">{{ t('home.journalFamily.reviews') }}</a></li>
              <li><a href="#">{{ t('home.journalFamily.caseReports') }}</a></li>
            </ul>
          </div>
          <div class="footer-column">
            <h3 class="footer-column-title">{{ t('footer.authors.title') }}</h3>
            <ul class="footer-links">
              <li><a href="#">{{ t('footer.authors.instructions') }}</a></li>
              <li><a href="#">{{ t('footer.authors.guidelines') }}</a></li>
              <li><a href="#">{{ t('footer.authors.process') }}</a></li>
              <li><a href="#">{{ t('footer.authors.ethics') }}</a></li>
            </ul>
          </div>
          <div class="footer-column">
            <h3 class="footer-column-title">{{ t('footer.resources.title') }}</h3>
            <ul class="footer-links">
              <li><a href="#">{{ t('footer.resources.faq') }}</a></li>
              <li><a href="#">{{ t('footer.resources.help') }}</a></li>
              <li><a href="#">{{ t('footer.resources.privacy') }}</a></li>
              <li><a href="#">{{ t('footer.resources.terms') }}</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 {{ t('nav.logo') }}. {{ t('footer.rights') }}</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 整体容器 */
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #FFFFFF;
  color: #333333;
}

/* 顶部极窄顶条 */
.top-bar {
  background-color: #003366;
  height: 18px;
  width: 100%;
}

.top-bar-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 100%;
  display: flex;
  align-items: center;
}

.top-bar-content span {
  font-size: 12px;
  color: #FFFFFF;
  font-family: Arial, sans-serif;
}

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 60px; /* 为导航栏留出空间 */
}

/* 首屏核心视觉区 */
.hero-section {
  width: 100%;
  padding: 7rem 0 6rem;
  background-color: #FFFFFF;
  border-bottom: 1px solid #F5F5F5;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 3rem;
}

.hero-text {
  flex: 6;
}

.hero-title {
  font-size: 52px;
  font-weight: bold;
  color: #003366;
  margin: 0 0 25px 0;
  line-height: 1.2;
  font-family: Arial, sans-serif;
}

.hero-subtitle {
  font-size: 20px;
  color: #555555;
  margin: 0;
  line-height: 1.6;
  font-family: Arial, sans-serif;
  max-width: 80%;
}

.hero-graphic {
  flex: 4;
}

.graphic-placeholder {
  width: 100%;
  height: 240px;
  background-color: #F5F5F5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.graphic-placeholder::after {
  content: "Academic Research Visualization";
  font-size: 14px;
  color: #777777;
  font-family: Arial, sans-serif;
}

/* 首屏提交按钮 */
.hero-submit-btn {
  background-color: #003366;
  color: #FFFFFF;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: Arial, sans-serif;
  margin-top: 2rem;
}

.hero-submit-btn:hover {
  background-color: #002244;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 51, 102, 0.3);
}

/* 区块标题 */
.section-title {
  font-size: 24px;
  font-weight: bold;
  color: #000000;
  margin-bottom: 30px;
  font-family: Arial, sans-serif;
}

/* 最新文章 */
.latest-articles-section {
  margin-bottom: 60px;
  padding-top: 1rem;
}

.section-title {
  font-size: 28px;
  font-weight: bold;
  color: #000000;
  margin-bottom: 35px;
  font-family: Arial, sans-serif;
  position: relative;
  padding-bottom: 10px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background-color: #003366;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 35px;
}

.article-card {
  width: 100%;
  min-height: 140px;
  padding: 1.5rem;
  background-color: #FFFFFF;
  border: 1px solid #F5F5F5;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.article-category {
  font-size: 11px;
  font-weight: bold;
  color: #003366;
  text-transform: uppercase;
  margin-bottom: 12px;
  font-family: Arial, sans-serif;
  letter-spacing: 0.5px;
}

.article-title {
  font-size: 18px;
  font-weight: bold;
  color: #000000;
  margin: 0 0 12px 0;
  line-height: 1.4;
  font-family: Arial, sans-serif;
  transition: color 0.3s ease;
}

.article-card:hover .article-title {
  color: #003366;
}

.article-title.clickable {
  cursor: pointer;
}

.article-title.clickable:hover{
  text-decoration: underline;
}

.article-meta {
  font-size: 13px;
  color: #777777;
  margin: 0 0 8px 0;
  line-height: 1.3;
  font-family: Arial, sans-serif;
}

.article-author {
  font-size: 11px;
  color: #999999;
  margin: 0;
  line-height: 1.2;
  font-family: Arial, sans-serif;
}

/* 期刊家族 */
.journal-family-section {
  margin-bottom: 60px;
  padding-top: 2rem;
}

.journal-family-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
}

.journal-family-item {
  background-color: #F5F5F5;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.journal-family-item:hover {
  background-color: #E8E8E8;
  transform: translateY(-2px);
}

.journal-family-name {
  font-size: 16px;
  font-weight: bold;
  color: #003366;
  margin: 0;
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0 1rem;
}

/* 专题合集 */
.special-collections-section {
  margin-bottom: 60px;
  padding-top: 2rem;
}

.special-collections-content {
  display: flex;
  gap: 35px;
}

.special-collection-main {
  flex: 7;
  height: 220px;
  background-color: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.special-collection-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 51, 102, 0.05);
  transition: all 0.3s ease;
}

.special-collection-main:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.special-collection-main:hover::before {
  background-color: rgba(0, 51, 102, 0.08);
}

.special-collection-title {
  font-size: 30px;
  font-weight: bold;
  color: #003366;
  margin: 0;
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0 2rem;
  position: relative;
  z-index: 1;
}

.special-collection-side {
  flex: 3;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.special-collection-item {
  height: 105px;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  background-color: #FFFFFF;
  border: 1px solid #F5F5F5;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.special-collection-item:hover {
  background-color: #F9FAFB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.special-collection-item-title {
  font-size: 20px;
  font-weight: bold;
  color: #000000;
  margin: 0;
  font-family: Arial, sans-serif;
  transition: color 0.3s ease;
}

.special-collection-item:hover .special-collection-item-title {
  color: #003366;
}

/* 新闻与观点 */
.news-views-section {
  margin-bottom: 60px;
  padding-top: 2rem;
}

.news-views-content {
  display: flex;
  gap: 35px;
}

.news-main {
  flex: 6;
  height: 280px;
  padding: 1.5rem;
  background-color: #FFFFFF;
  border: 1px solid #F5F5F5;
  border-radius: 4px;
}

.news-title {
  font-size: 24px;
  font-weight: bold;
  color: #003366;
  margin: 0 0 1.5rem 0;
  font-family: Arial, sans-serif;
  position: relative;
  padding-bottom: 8px;
}

.news-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background-color: #003366;
}

.news-item-title {
  font-size: 20px;
  font-weight: bold;
  color: #000000;
  margin: 0 0 0.8rem 0;
  font-family: Arial, sans-serif;
  line-height: 1.4;
}

.news-item-content {
  font-size: 15px;
  color: #555555;
  margin: 0;
  line-height: 1.6;
  font-family: Arial, sans-serif;
}

.news-side {
  flex: 4;
  height: 280px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.news-side-title {
  font-size: 20px;
  font-weight: bold;
  color: #003366;
  margin: 0 0 1.2rem 0;
  font-family: Arial, sans-serif;
  position: relative;
  padding-bottom: 8px;
}

.news-side-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background-color: #003366;
}

.news-side-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 1rem;
  background-color: #FFFFFF;
  border: 1px solid #F5F5F5;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.news-side-item:hover {
  background-color: #F9FAFB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.news-side-item-title {
  font-size: 16px;
  font-weight: bold;
  color: #000000;
  margin: 0;
  font-family: Arial, sans-serif;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.news-side-item:hover .news-side-item-title {
  color: #003366;
}

.news-side-item-date {
  font-size: 12px;
  color: #999999;
  margin: 0;
  font-family: Arial, sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 订阅/推广区块 */
.subscribe-section {
  background-color: #003366;
  width: 100%;
  padding: 4rem 0;
  margin-bottom: 0;
}

.subscribe-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.subscribe-title {
  font-size: 28px;
  font-weight: bold;
  color: #FFFFFF;
  margin: 0 0 20px 0;
  font-family: Arial, sans-serif;
}

.subscribe-text {
  font-size: 16px;
  color: #E6E6E6;
  margin: 0;
  font-family: Arial, sans-serif;
  max-width: 60%;
  margin: 0 auto;
  line-height: 1.6;
}

/* 底部区域 */
.footer {
  background-color: #F9FAFB;
  width: 100%;
  padding: 3rem 0 2rem;
  border-top: 1px solid #E5E7EB;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 2.5rem;
}

.footer-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.footer-column-title {
  font-size: 16px;
  font-weight: bold;
  color: #003366;
  margin: 0;
  font-family: Arial, sans-serif;
  position: relative;
  padding-bottom: 8px;
}

.footer-column-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 30px;
  height: 2px;
  background-color: #003366;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-links li a {
  font-size: 13px;
  color: #555555;
  text-decoration: none;
  line-height: 1.8;
  font-family: Arial, sans-serif;
  transition: color 0.3s ease;
}

.footer-links li a:hover {
  color: #003366;
  text-decoration: underline;
}

.footer-bottom {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #E5E7EB;
  padding-top: 1.5rem;
}

.footer-bottom p {
  font-size: 11px;
  color: #777777;
  margin: 0;
  font-family: Arial, sans-serif;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  
  .hero-text,
  .hero-graphic {
    flex: 1;
    width: 100%;
  }
  
  .special-collections-content,
  .news-views-content {
    flex-direction: column;
  }
  
  .special-collection-main,
  .special-collection-side,
  .news-main,
  .news-side {
    flex: 1;
    width: 100%;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
  }
  
  .journal-family-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>