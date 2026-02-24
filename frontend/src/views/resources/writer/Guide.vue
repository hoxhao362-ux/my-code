<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-writer-guide'"
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
        Download Full Guide PDF
      </button>
    </div>

    <div class="content-area">
      <div id="preparation" class="section">
        <h1>Preparation</h1>
        <p>Before submitting your manuscript, please ensure you have read the following guidelines carefully. Adherence to these guidelines will ensure a smooth review process.</p>
        <div class="highlight-box">
          <h2>Ethics & Disclosure</h2>
          <p>All writers must disclose any financial and personal relationships with other people or organizations that could inappropriately influence (bias) their work.</p>
        </div>
      </div>

      <div id="formatting" class="section">
        <h1>Formatting</h1>
        <h2>Text Formatting</h2>
        <p>Manuscripts should be submitted in Word format. Use a standard font (e.g., Times New Roman, Arial) at 12 pt size. Double-space the entire manuscript.</p>
        <h2>Figures & Tables</h2>
        <p>Figures should be high-resolution (min 300 dpi). Tables should be editable text, not images.</p>
      </div>

      <div id="process" class="section">
        <h1>Review Process</h1>
        <p>Our journal follows a double-blind peer review process. All manuscripts are initially screened by the editor. Manuscripts that meet the journal's standards are sent to at least two independent reviewers.</p>
      </div>

      <div id="policies" class="section">
        <h1>Policies</h1>
        <h2>Open Access</h2>
        <p>We offer writers the option to make their article open access. A publication fee applies.</p>
        <h2>Copyright</h2>
        <p>Writers retain copyright of their work under a Creative Commons Attribution License.</p>
      </div>

      <div id="faq" class="section">
        <h1>FAQ</h1>
        <div class="search-box">
          <input type="text" v-model="searchQuery" placeholder="Search FAQs..." />
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
      PDF download started...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const navItems = [
  { id: 'preparation', label: 'Preparation' },
  { id: 'formatting', label: 'Formatting' },
  { id: 'process', label: 'Review Process' },
  { id: 'policies', label: 'Policies' },
  { id: 'faq', label: 'FAQ' }
]

const activeSection = ref('preparation')
const searchQuery = ref('')
const showToast = ref(false)

const faqs = [
  { question: 'What is the word limit?', answer: 'Original Research articles should not exceed 3,500 words.' },
  { question: 'Do you charge a submission fee?', answer: 'No, there are no submission fees.' },
  { question: 'How long does the review take?', answer: 'The average time to first decision is 4 weeks.' }
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
