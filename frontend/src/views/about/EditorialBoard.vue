<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'about-editorial-board'"
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
      <a href="#" class="contact-link" @click.prevent="scrollToSection('contact')">Contact Editorial Office</a>
    </div>

    <div class="content-area">
      <div id="editor-in-chief" class="section">
        <h1>Editor-in-Chief</h1>
        <div class="card chief-card">
          <div class="chief-info">
            <div class="avatar-wrapper">
              <div class="avatar-placeholder">Photo</div>
            </div>
            <div class="info-text">
              <h2>Dr. Richard Horton</h2>
              <p class="position">Editor-in-Chief, The Lancet</p>
              <p class="field">Global Health, Public Health</p>
              <a href="#" class="orcid-link">ORCID: 0000-0000-0000-0000</a>
            </div>
          </div>
          <div class="message-box">
            <p>"The Lancet is committed to applying science to the betterment of society and the improvement of human health."</p>
          </div>
        </div>
      </div>

      <div id="deputy-editors" class="section">
        <h1>Deputy Editors</h1>
        <div class="cards-grid">
          <div v-for="editor in deputyEditors" :key="editor.id" class="card member-card">
            <div class="member-info">
              <div class="avatar-wrapper small">
                <div class="avatar-placeholder"></div>
              </div>
              <h3>{{ editor.name }}</h3>
              <p class="position">{{ editor.position }}</p>
              <p class="field">{{ editor.field }}</p>
              <a href="#" class="orcid-link">ORCID</a>
            </div>
          </div>
        </div>
      </div>

      <div id="editorial-board" class="section">
        <h1>Editorial Board</h1>
        <div class="filter-bar">
          <select v-model="selectedCategory">
            <option value="all">All Categories</option>
            <option value="Oncology">Oncology</option>
            <option value="Neurology">Neurology</option>
            <option value="Cardiology">Cardiology</option>
          </select>
        </div>
        <div class="cards-grid compact">
          <div v-for="member in filteredBoardMembers" :key="member.id" class="card member-card">
            <h3>{{ member.name }}</h3>
            <p class="position">{{ member.institution }}</p>
            <p class="field">{{ member.category }}</p>
          </div>
        </div>
      </div>

      <div id="youth-editorial-board" class="section">
        <h1>Youth Editorial Board</h1>
        <div class="cards-grid">
          <div v-for="member in youthMembers" :key="member.id" class="card member-card">
            <h3>{{ member.name }}</h3>
            <p class="position">{{ member.institution }}</p>
            <p class="field">Focus: {{ member.focus }}</p>
          </div>
        </div>
      </div>

      <div id="contact" class="section">
        <h1>Contact</h1>
        <div class="contact-info">
          <p><strong>Email:</strong> editorial@thelancet.com</p>
          <p><strong>Address:</strong> 125 London Wall, London, EC2Y 5AS, UK</p>
          <p><strong>Office Hours:</strong> Monday to Friday 09:00 - 17:00 GMT</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const navItems = [
  { id: 'editor-in-chief', label: 'Editor-in-Chief' },
  { id: 'deputy-editors', label: 'Deputy Editors' },
  { id: 'editorial-board', label: 'Editorial Board' },
  { id: 'youth-editorial-board', label: 'Youth Editorial Board' },
  { id: 'contact', label: 'Contact' }
]

const activeSection = ref('editor-in-chief')
const selectedCategory = ref('all')

const deputyEditors = [
  { id: 1, name: "Dr. Jane Doe", position: "Deputy Editor", field: "Infectious Diseases" },
  { id: 2, name: "Dr. John Smith", position: "Deputy Editor", field: "Cardiology" },
  { id: 3, name: "Dr. Emily Chen", position: "Deputy Editor", field: "Oncology" }
]

const boardMembers = [
  { id: 1, name: "Prof. A", institution: "Harvard University", category: "Oncology" },
  { id: 2, name: "Prof. B", institution: "Oxford University", category: "Neurology" },
  { id: 3, name: "Prof. C", institution: "Johns Hopkins", category: "Cardiology" },
  { id: 4, name: "Prof. D", institution: "Cambridge", category: "Oncology" }
]

const youthMembers = [
  { id: 1, name: "Dr. X", institution: "MIT", focus: "AI in Medicine" },
  { id: 2, name: "Dr. Y", institution: "Stanford", focus: "Genomics" }
]

const filteredBoardMembers = computed(() => {
  if (selectedCategory.value === 'all') return boardMembers
  return boardMembers.filter(m => m.category === selectedCategory.value)
})

const scrollToSection = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const offset = 80 // Navbar height
    const bodyRect = document.body.getBoundingClientRect().top
    const elementRect = element.getBoundingClientRect().top
    const elementPosition = elementRect - bodyRect
    const offsetPosition = elementPosition - offset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
    activeSection.value = id
  }
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
  }, { threshold: 0.2, rootMargin: "-80px 0px 0px 0px" })

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
}

.sidebar {
  width: 25%;
  background-color: #F5F5F5;
  padding: 32px 24px;
  position: fixed;
  height: calc(100vh - 80px);
  top: 80px;
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
  font-size: 14px;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover, .nav-item.active {
  color: #C93737;
  font-weight: bold;
  border-bottom-color: #C93737;
}

.contact-link {
  color: #C93737;
  text-decoration: none;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 40px;
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
  border-bottom: 1px solid #E5E5E5;
  padding-bottom: 8px;
}

h2 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.card {
  background: white;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  padding: 24px;
  transition: border-color 0.3s;
}

.card:hover {
  border-color: #C93737;
}

.chief-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chief-info {
  display: flex;
  gap: 24px;
  align-items: center;
}

.avatar-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #F5F5F5;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-wrapper.small {
  width: 60px;
  height: 60px;
  margin-bottom: 16px;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
}

.info-text p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.orcid-link {
  color: #C93737;
  font-size: 14px;
  text-decoration: none;
}

.message-box {
  background-color: #F5F5F5;
  padding: 16px;
  border-radius: 4px;
  font-style: italic;
  color: #333;
  font-size: 14px;
  line-height: 1.6;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 24px;
}

.member-card h3 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.member-card p {
  font-size: 14px;
  color: #666;
  margin: 2px 0;
}

.filter-bar {
  margin-bottom: 24px;
}

select {
  padding: 8px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  outline: none;
}

.contact-info p {
  margin-bottom: 12px;
  font-size: 14px;
  color: #333;
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
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
