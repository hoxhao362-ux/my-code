<template>
  <div class="journal-hub">
    <!-- Platform Header -->
    <header class="hub-header">
      <div class="container">
        <div class="logo">
          <h1>Journal Platform</h1>
        </div>
        <nav class="hub-nav">
          <a href="#" class="nav-item">Journals</a>
          <a href="#" class="nav-item">Collections</a>
          <a href="#" class="nav-item">Multimedia</a>
          <a href="/login" class="nav-item login-btn">Login</a>
        </nav>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hub-hero">
      <div class="container">
        <div class="hero-content">
          <h2>Advancing Science, Improving Lives</h2>
          <p>Explore our network of high-impact journals covering the full spectrum of medical and scientific research.</p>
        </div>
      </div>
    </section>

    <!-- Journals Grid -->
    <section class="journals-section">
      <div class="container">
        <h3 class="section-title">Our Journals</h3>
        <div v-if="loading" class="loading">Loading journals...</div>
        <div v-else class="journals-grid">
          <div 
            v-for="journal in journals" 
            :key="journal.id" 
            class="journal-card"
            :style="{ borderTopColor: journal.color || '#005696' }"
          >
            <div class="journal-header" :style="{ backgroundColor: journal.color || '#005696' }">
              <h4>{{ journal.name }}</h4>
            </div>
            <div class="journal-body">
              <p class="description">{{ journal.description }}</p>
              <div class="metrics">
                <div class="metric">
                  <span class="label">Impact Factor</span>
                  <span class="value">{{ journal.impactFactor }}</span>
                </div>
              </div>
              <router-link :to="`/journals/${journal.id}`" class="visit-btn">
                Visit Journal
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="hub-footer">
      <div class="container">
        <p>&copy; {{ new Date().getFullYear() }} Journal Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { usePlatformStore } from '../stores/platform'

const platformStore = usePlatformStore()
const journals = computed(() => platformStore.journals)
const loading = computed(() => platformStore.loading)

onMounted(() => {
  platformStore.fetchJournals()
  platformStore.clearJournal() // Clear current journal context when on hub
})
</script>

<style scoped>
.journal-hub {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #333;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header */
.hub-header {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 15px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.hub-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  color: #005696;
  font-weight: 700;
}

.hub-nav {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-item {
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-item:hover {
  color: #005696;
}

.login-btn {
  padding: 8px 16px;
  background-color: #005696;
  color: #fff;
  border-radius: 4px;
}

.login-btn:hover {
  background-color: #00447a;
  color: #fff;
}

/* Hero */
.hub-hero {
  background: linear-gradient(135deg, #005696 0%, #002a4a 100%);
  color: #fff;
  padding: 80px 0;
  text-align: center;
}

.hero-content h2 {
  font-size: 48px;
  margin-bottom: 20px;
  font-weight: 300;
}

.hero-content p {
  font-size: 20px;
  opacity: 0.9;
  max-width: 800px;
  margin: 0 auto;
}

/* Journals Grid */
.journals-section {
  padding: 60px 0;
}

.section-title {
  font-size: 28px;
  margin-bottom: 40px;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

.journals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.journal-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  border-top: 4px solid #005696;
  display: flex;
  flex-direction: column;
}

.journal-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0,0,0,0.1);
}

.journal-header {
  padding: 20px;
  color: #fff;
}

.journal-header h4 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.journal-body {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.description {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.5;
  flex-grow: 1;
}

.metrics {
  margin-bottom: 20px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.metric .label {
  color: #888;
}

.metric .value {
  font-weight: bold;
  color: #333;
}

.visit-btn {
  display: block;
  text-align: center;
  background-color: #f0f0f0;
  color: #333;
  padding: 10px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  transition: background-color 0.2s;
}

.visit-btn:hover {
  background-color: #e0e0e0;
}

/* Footer */
.hub-footer {
  background: #333;
  color: #fff;
  padding: 40px 0;
  text-align: center;
  margin-top: auto;
}
</style>
