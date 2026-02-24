<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-reviewer-guidelines'"
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
    </div>

    <div class="content-area">
      <div id="responsibilities" class="section">
        <h1>Responsibilities</h1>
        <p>Reviewers are expected to provide an objective, unbiased, and timely assessment of the manuscript. You should respect the confidentiality of the peer review process.</p>
      </div>

      <div id="grading" class="section">
        <h1>Grading Standards</h1>
        <p>Please evaluate the manuscript based on: Originality, Methodology, Clarity, and Relevance to the field.</p>
        <div class="highlight-box">
          <h2>Score Scale</h2>
          <ul>
            <li><strong>Top 10%:</strong> Exceptional quality, high priority.</li>
            <li><strong>Top 25%:</strong> Good quality, suitable for publication with minor revisions.</li>
            <li><strong>Bottom 50%:</strong> Significant flaws or lack of novelty.</li>
          </ul>
        </div>
      </div>

      <div id="template" class="section">
        <h1>Report Template</h1>
        <div class="template-preview">
          <div class="template-image-placeholder">
            [Report Template Preview Image]
          </div>
          <button class="download-btn" @click="handleDownload">Download Report Template</button>
        </div>
      </div>

      <div id="coi" class="section">
        <h1>Conflict of Interest</h1>
        <p>If you have any competing interests (financial, professional, or personal) that could interfere with your judgment, you must decline the invitation to review.</p>
      </div>

      <div id="samples" class="section">
        <h1>Sample Reports</h1>
        <div class="accordion">
          <div class="accordion-item">
            <div class="accordion-header" @click="toggleSample">
              <span>Sample Review 1: Good Quality</span>
              <span class="arrow">{{ showSample ? '▲' : '▼' }}</span>
            </div>
            <div v-if="showSample" class="accordion-content">
              <p><strong>Summary:</strong> This study addresses an important question...</p>
              <p><strong>Strengths:</strong> robust methodology...</p>
              <p><strong>Weaknesses:</strong> sample size is small...</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="floating-sidebar">
      <h3>Top 10 Questions</h3>
      <ul>
        <li><a href="#">How to judge originality?</a></li>
        <li><a href="#">What if I am late?</a></li>
        <li><a href="#">Can I share the paper?</a></li>
        <li><a href="#">How to handle COI?</a></li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const navItems = [
  { id: 'responsibilities', label: 'Responsibilities' },
  { id: 'grading', label: 'Grading Standards' },
  { id: 'template', label: 'Report Template' },
  { id: 'coi', label: 'Conflict of Interest' },
  { id: 'samples', label: 'Sample Reports' }
]

const activeSection = ref('responsibilities')
const showSample = ref(false)

const scrollToSection = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
    activeSection.value = id
  }
}

const toggleSample = () => {
  showSample.value = !showSample.value
}

const handleDownload = () => {
  alert('Template download started.')
}

// Intersection Observer
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
  padding-top: 0;
  margin-top: 80px;
  position: relative;
}

.sidebar {
  width: 25%;
  background-color: #F5F5F5;
  padding: 32px 24px;
  position: fixed;
  height: calc(100vh - 120px);
  top: 120px;
  left: 0;
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
}

.nav-item:hover, .nav-item.active {
  color: #C93737;
  font-weight: bold;
}

.content-area {
  margin-left: 25%;
  width: 55%; /* Leave space for right sidebar */
  padding: 32px 48px;
  background-color: #fff;
}

.floating-sidebar {
  width: 20%;
  position: fixed;
  right: 0;
  top: 120px;
  height: calc(100vh - 120px);
  padding: 32px 24px;
  background-color: #fff;
  border-left: 1px solid #F5F5F5;
}

.floating-sidebar h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 16px;
}

.floating-sidebar ul {
  list-style: none;
  padding: 0;
}

.floating-sidebar li {
  margin-bottom: 12px;
}

.floating-sidebar a {
  color: #666;
  text-decoration: none;
  font-size: 14px;
}

.floating-sidebar a:hover {
  color: #C93737;
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
  border-bottom: 1px solid #E5E5E5;
  padding-bottom: 8px;
}

.template-preview {
  background-color: #F5F5F5;
  padding: 24px;
  text-align: center;
  border-radius: 4px;
}

.template-image-placeholder {
  height: 200px;
  background-color: #E0E0E0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #999;
}

.download-btn {
  background-color: #C93737;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 4px;
  cursor: pointer;
}

.accordion-item {
  border: 1px solid #E5E5E5;
  border-radius: 4px;
}

.accordion-header {
  padding: 16px;
  background-color: #F9F9F9;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}

.accordion-content {
  padding: 16px;
  background-color: white;
  border-top: 1px solid #E5E5E5;
}

@media (max-width: 1024px) {
  .content-area {
    width: 75%;
    padding-right: 24px;
  }
  .floating-sidebar {
    display: none;
  }
}
</style>
