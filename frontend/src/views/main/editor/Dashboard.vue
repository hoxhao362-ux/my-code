<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { useI18n } from '../../../composables/useI18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const user = computed(() => userStore.user)

// Statistics for Main Site
const totalUsers = computed(() => userStore.users.filter(u => u.role === 'user').length)
const activeUsers = computed(() => userStore.users.filter(u => u.role === 'user' && u.status === 'active').length)
const totalEditors = computed(() => userStore.users.filter(u => u.role === 'editor').length)

const goToUsers = () => {
  router.push('/editor/users')
}

const goToContent = () => {
  // Placeholder for content management
  alert('Content Management module is under construction')
}

const goToSettings = () => {
  // Placeholder for site settings
  alert('Site Settings module is under construction')
}
</script>

<template>
  <div class="editor-dashboard-container">
    <Navigation 
      :user="user"
      :current-page="'editor-dashboard'"
      :logout="userStore.logout"
    />

    <main class="dashboard-content">
      <div class="dashboard-header">
        <h1 class="dashboard-title">{{ t('nav.roles.admin') }}</h1> <!-- "Editor Dashboard" -->
        <div class="user-info">
          <span class="welcome-message">Welcome, {{ user?.username }}</span>
        </div>
      </div>

      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" @click="goToUsers">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalUsers }}</h3>
              <p class="stat-label">Registered Users</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🟢</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ activeUsers }}</h3>
              <p class="stat-label">Active Users</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🛡️</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ totalEditors }}</h3>
              <p class="stat-label">Editors</p>
            </div>
          </div>
        </div>
      </section>

      <section class="actions-section">
        <h2 class="section-title">Quick Actions</h2>
        <div class="actions-grid">
          <div class="action-card" @click="goToUsers">
            <div class="action-icon">👤</div>
            <h3>User Management</h3>
            <p>Manage ordinary user accounts and permissions</p>
          </div>
          <div class="action-card" @click="goToContent">
            <div class="action-icon">📰</div>
            <h3>Content Management</h3>
            <p>Maintain main site content, news, and subscriptions</p>
          </div>
          <div class="action-card" @click="goToSettings">
            <div class="action-icon">⚙️</div>
            <h3>Site Settings</h3>
            <p>Configure basic site information and rules</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Journal Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.editor-dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.dashboard-content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.welcome-message {
  font-size: 1.1rem;
  color: #34495e;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  background-color: #f8f9fa;
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.action-card p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin: 0;
}

.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
}
</style>