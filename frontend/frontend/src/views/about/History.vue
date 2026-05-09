<script setup>
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { useI18n } from '../../composables/useI18n'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const { t } = useI18n()

const showModal = ref(false)

const events = reactive([
  {
    year: '2026',
    titleKey: 'about.history.events.2026.title',
    descKey: 'about.history.events.2026.desc',
    detailsKey: 'about.history.events.2026.details',
    expanded: false,
    image: 'cover-2026.jpg'
  },
  {
    year: '2025',
    titleKey: 'about.history.events.2025.title',
    descKey: 'about.history.events.2025.desc',
    detailsKey: 'about.history.events.2025.details',
    expanded: false
  },
  {
    year: '2024',
    titleKey: 'about.history.events.2024.title',
    descKey: 'about.history.events.2024.desc',
    detailsKey: 'about.history.events.2024.details',
    expanded: false,
    image: 'cover-2024.jpg'
  }
])

const toggleDetails = (year) => {
  const event = events.find(e => e.year === year)
  if (event) {
    event.expanded = !event.expanded
  }
}

const openImage = (img) => {
  showModal.value = true
}
</script>

<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'about-history'"
      :logout="userStore.logout"
    />
    
    <div class="content-area">
      <div class="header">
        <h1>{{ t('about.history.title') }}</h1>
        <p class="intro">{{ t('about.history.intro') }}</p>
      </div>

      <div class="timeline">
        <div v-for="event in events" :key="event.year" class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div class="time">{{ event.year }}</div>
            <h3 class="title" @click="toggleDetails(event.year)">
              {{ t(event.titleKey) }}
              <span class="toggle-icon">{{ event.expanded ? '▲' : '▼' }}</span>
            </h3>
            <p class="desc">{{ t(event.descKey) }}</p>
            
            <div v-if="event.expanded" class="details">
              <p>{{ t(event.detailsKey) }}</p>
              <div v-if="event.image" class="image-wrapper" @click="openImage(event.image)">
                <div class="image-placeholder">{{ t('about.history.coverImage') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-link">
        <a href="#">{{ t('about.history.viewArchives') }}</a>
      </div>
    </div>

    <!-- Image Modal -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal-content">
        <div class="modal-image-placeholder">{{ t('about.history.fullSizeImage') }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  padding-top: 0;
  margin-top: 80px;
  background-color: #fff;
}

.content-area {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 24px;
}

.header {
  text-align: center;
  margin-bottom: 60px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.intro {
  color: #666;
  font-size: 14px;
}

.timeline {
  position: relative;
  padding-left: 20px;
  border-left: 2px solid #0056B3;
  margin-left: 20px;
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
  padding-left: 30px;
}

.timeline-marker {
  position: absolute;
  left: -27px;
  top: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #0056B3;
  border: 2px solid white;
}

.timeline-content:hover {
  background-color: #F9F9F9;
  border-radius: 4px;
}

.time {
  font-size: 14px;
  font-weight: bold;
  color: #0056B3;
  margin-bottom: 4px;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-icon {
  font-size: 12px;
  color: #999;
}

.desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #E5E5E5;
  font-size: 14px;
  color: #333;
}

.image-wrapper {
  margin-top: 12px;
  width: 120px;
  height: 160px;
  background-color: #E0E0E0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
}

.footer-link {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #E5E5E5;
}

.footer-link a {
  color: #0056B3;
  text-decoration: none;
  font-weight: bold;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-image-placeholder {
  width: 300px;
  height: 400px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #333;
}
</style>
