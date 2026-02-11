<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'about-history'"
      :logout="userStore.logout"
    />
    
    <div class="content-area">
      <div class="header">
        <h1>Journal History</h1>
        <p class="intro">Tracing the legacy of medical excellence since 1823.</p>
      </div>

      <div class="timeline">
        <div v-for="event in events" :key="event.year" class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div class="time">{{ event.year }}</div>
            <h3 class="title" @click="toggleDetails(event.year)">
              {{ event.title }}
              <span class="toggle-icon">{{ event.expanded ? '▲' : '▼' }}</span>
            </h3>
            <p class="desc">{{ event.description }}</p>
            
            <div v-if="event.expanded" class="details">
              <p>{{ event.details }}</p>
              <div v-if="event.image" class="image-wrapper" @click="openImage(event.image)">
                <div class="image-placeholder">Cover Image</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-link">
        <a href="#">View Full Archives</a>
      </div>
    </div>

    <!-- Image Modal -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal-content">
        <div class="modal-image-placeholder">Full Size Image</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const showModal = ref(false)

const events = reactive([
  {
    year: '2025',
    title: 'Impact Factor Reaches 168.9',
    description: 'The Lancet continues to lead as one of the world\'s most influential medical journals.',
    details: 'This milestone reflects the high quality of research published and its global impact on clinical practice and health policy.',
    expanded: false,
    image: 'cover-2025.jpg'
  },
  {
    year: '2020',
    title: 'COVID-19 Response',
    description: 'Published critical early research on SARS-CoV-2.',
    details: 'The journal accelerated its review process to disseminate vital information during the pandemic.',
    expanded: false
  },
  {
    year: '1823',
    title: 'Founded by Thomas Wakley',
    description: 'The first issue was published on October 5th.',
    details: 'Wakley named the journal after the surgical instrument, symbolizing its mission to cut out corruption in medicine.',
    expanded: false,
    image: 'cover-1823.jpg'
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
  border-left: 2px solid #C93737;
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
  background-color: #C93737;
  border: 2px solid white;
}

.timeline-content:hover {
  background-color: #F9F9F9;
  border-radius: 4px;
}

.time {
  font-size: 14px;
  font-weight: bold;
  color: #C93737;
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
  color: #C93737;
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
