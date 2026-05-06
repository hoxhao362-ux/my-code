<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-author-guide'"
      :logout="userStore.logout"
    />
    <div class="sidebar">
      <nav class="sidebar-nav">
        <a 
          v-for="item in navItems" 
          :key="item.id" 
          :href="'#' + item.id" 
          class="nav-item"
          :class="{ active: activeSection === item.id }"
          @click.prevent="scrollToSection(item.id)"
        >
          {{ item.label }}
        </a>
      </nav>
      <button class="download-btn" @click="handleDownload">
        {{ $t('guide.downloadPdf') }}
      </button>
    </div>

    <div class="content-area">
      <div id="preparation" class="section">
        <h1>{{ $t('guide.preparation.title') }}</h1>
        <p>{{ $t('guide.preparation.desc') }}</p>
        <div class="highlight-box">
          <h2>{{ $t('guide.preparation.ethicsTitle') }}</h2>
          <p>{{ $t('guide.preparation.ethicsDesc') }}</p>
        </div>
      </div>
      
      <!-- 动态文章类型指南 -->
      <div id="article-types" class="section">
        <h1>Article Types & Requirements</h1>
        <div v-for="type in articleGuides" :key="type.type" class="article-type-box">
          <h2>{{ type.title }}</h2>
          <ul>
            <li><strong>Structure:</strong> {{ type.sections.find(s => s.id === 'structure').content }}</li>
            <li><strong>Abstract:</strong> {{ type.sections.find(s => s.id === 'abstract').content }}</li>
            <li><strong>Figures/Tables:</strong> {{ type.sections.find(s => s.id === 'figures').content }}</li>
            <li><strong>Ethics:</strong> {{ type.sections.find(s => s.id === 'ethics').content }}</li>
          </ul>
        </div>
      </div>

      <div id="formatting" class="section">
        <h1>{{ $t('guide.formatting.title') }}</h1>
        <h2>{{ $t('guide.formatting.textTitle') }}</h2>
        <p>{{ $t('guide.formatting.textDesc') }}</p>
        <h2>{{ $t('guide.formatting.figuresTitle') }}</h2>
        <p>{{ $t('guide.formatting.figuresDesc') }}</p>
      </div>

      <div id="process" class="section">
        <h1>{{ $t('guide.process.title') }}</h1>
        <p>{{ $t('guide.process.desc') }}</p>
      </div>

      <div id="policies" class="section">
        <h1>{{ $t('guide.policies.title') }}</h1>
        <h2>{{ $t('guide.policies.openAccessTitle') }}</h2>
        <p>{{ $t('guide.policies.openAccessDesc') }}</p>
        <h2>{{ $t('guide.policies.copyrightTitle') }}</h2>
        <p>{{ $t('guide.policies.copyrightDesc') }}</p>
      </div>

      <div id="faq" class="section">
        <h1>{{ $t('guide.faq.title') }}</h1>
        <div class="search-box">
          <input type="text" v-model="searchQuery" :placeholder="$t('guide.faq.searchPlaceholder')" />
        </div>
        <div class="faq-list">
          <div v-for="faq in filteredFaqs" :key="faq.question" class="faq-item">
            <h3>{{ faq.question }}</h3>
            <p>{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="toast">
      {{ $t('guide.toast') }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const navItems = computed(() => [
  { id: 'preparation', label: t('guide.preparation.title') },
  { id: 'article-types', label: 'Article Types' },
  { id: 'formatting', label: t('guide.formatting.title') },
  { id: 'process', label: t('guide.process.title') },
  { id: 'policies', label: t('guide.policies.title') },
  { id: 'faq', label: t('guide.faq.title') }
])

const articleGuides = computed(() => [
  {
    type: 'original',
    title: t('guide.articleTypes.original.title'),
    sections: [
      { id: 'structure', content: t('guide.articleTypes.original.structure') },
      { id: 'abstract', content: t('guide.articleTypes.original.abstract') },
      { id: 'figures', content: t('guide.articleTypes.original.figures') },
      { id: 'ethics', content: t('guide.articleTypes.original.ethics') }
    ]
  },
  {
    type: 'review',
    title: t('guide.articleTypes.review.title'),
    sections: [
      { id: 'structure', content: t('guide.articleTypes.review.structure') },
      { id: 'abstract', content: t('guide.articleTypes.review.abstract') },
      { id: 'figures', content: t('guide.articleTypes.review.figures') },
      { id: 'ethics', content: t('guide.articleTypes.review.ethics') }
    ]
  },
  {
    type: 'caseReport',
    title: t('guide.articleTypes.caseReport.title'),
    sections: [
      { id: 'structure', content: t('guide.articleTypes.caseReport.structure') },
      { id: 'abstract', content: t('guide.articleTypes.caseReport.abstract') },
      { id: 'figures', content: t('guide.articleTypes.caseReport.figures') },
      { id: 'ethics', content: t('guide.articleTypes.caseReport.ethics') }
    ]
  }
])

const activeSection = ref('preparation')
const searchQuery = ref('')
const showToast = ref(false)

const faqs = [
  { question: 'What is the word limit for Original Research?', answer: 'Original Research articles should not exceed 3,500 words in the main text, excluding abstract, references, and tables.' },
  { question: 'What is the structure required for Abstract?', answer: 'All Original Research articles require a structured abstract with four sections: Background, Methods, Findings, and Interpretation.' },
  { question: 'Do you require ethical approval?', answer: 'Yes. All manuscripts reporting human or animal data must include a statement confirming ethical approval by an institutional review board.' },
  { question: 'How long does the review process take?', answer: 'The average time to first decision is 4-6 weeks. Initial screening is typically completed within 1-3 working days.' },
  { question: 'What file formats are accepted?', answer: 'We accept Word (.docx), PDF, and LaTeX formats. Figures should be submitted as separate high-resolution images (minimum 300 dpi).' },
  { question: 'Is there a submission fee?', answer: 'No, there are no submission fees. Optional Open Access publication fees apply after acceptance.' },
  { question: 'How should references be formatted?', answer: 'References should follow the Vancouver style. Number them in the order they appear in the text.' },
  { question: 'What is your acceptance rate?', answer: 'Our journal has an acceptance rate of approximately 8-10% after peer review.' },
  { question: 'Do you offer open access?', answer: 'Yes, we offer both subscription and open access options. Contact the editorial office for details.' }
]

const filteredFaqs = computed(() => {
  if (!searchQuery.value) return faqs
  const query = searchQuery.value.toLowerCase()
  return faqs.filter(f => 
    f.question.toLowerCase().includes(query) || 
    f.answer.toLowerCase().includes(query)
  )
})

const scrollToSection = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
    activeSection.value = id
  }
}

const handleDownload = () => {
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Intersection Observer to update active section on scroll
let observer = null
onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeSection.value = entry.target.id
      }
    })
  }, { threshold: 0.5 })

  navItems.forEach(item => {
    const el = document.getElementById(item.id)
    if (el) observer.observe(el)
  })
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.page-container {
  display: flex;
  min-height: 100vh;
  background-color: #fff;
  padding-top: 0;
  margin-top: 80px; /* Space for fixed navbar */
}

.sidebar {
  width: 25%;
  background-color: #F5F5F5;
  padding: 32px 24px;
  position: fixed;
  height: calc(100vh - 80px);
  top: 80px; /* Navbar height + offset */
  left: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nav-item {
  color: #333;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover {
  color: #C93737;
}

.nav-item.active {
  color: #C93737;
  border-bottom-color: #C93737;
  font-weight: bold;
}

.download-btn {
  background-color: #C93737;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 60px; /* Space for footer/bottom */
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #A02C2C;
}

.content-area {
  margin-left: 25%;
  width: 75%;
  padding: 32px 48px;
  background-color: #fff;
}

.section {
  margin-bottom: 48px;
  padding-top: 24px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E5E5;
}

h2 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-top: 24px;
  margin-bottom: 16px;
}

p {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 16px;
}

.highlight-box {
  background-color: #F5F5F5;
  padding: 24px;
  border-radius: 4px;
  margin: 24px 0;
}

.search-box input {
  width: 100%;
  padding: 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 24px;
}

.search-box input:focus {
  border-color: #C93737;
  outline: none;
}

.faq-item {
  margin-bottom: 24px;
}

.faq-item h3 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.article-type-box {
  background-color: #F8F9FA;
  border-left: 4px solid #C93737;
  padding: 20px;
  margin-bottom: 24px;
  border-radius: 0 4px 4px 0;
}

.article-type-box h2 {
  margin-top: 0;
  color: #C93737;
}

.article-type-box ul {
  padding-left: 20px;
  margin-bottom: 0;
}

.article-type-box li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.toast {
  position: fixed;
  top: 80px;
  right: 24px;
  background-color: #333;
  color: white;
  padding: 12px 24px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    position: relative;
    height: auto;
    top: 0;
  }
  .content-area {
    margin-left: 0;
    width: 100%;
  }
}
</style>
