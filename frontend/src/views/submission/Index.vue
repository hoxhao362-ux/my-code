<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Login from './Login.vue'
import AdminRegister from '../auth/AdminRegister.vue'

import { useI18n } from '../../composables/useI18n'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()
// Use store state for reactivity
const submissionUser = computed(() => userStore.submissionUser)

// State to control login/register view
const showRegister = ref(false)

// Redirect to dashboard if already logged in
const checkLoginAndRedirect = () => {
  if (submissionUser.value) {
    const role = submissionUser.value.role
    if (role === 'writer') {
      router.push('/submission/writer/submit')
    } else if (role === 'reviewer') {
      router.push('/reviewer/dashboard')
    } else if (['editor', 'admin', 'associate_editor', 'editorial_assistant', 'advisory_editor'].includes(role)) {
      router.push('/editor/dashboard')
    }
  }
}

onMounted(() => {
  // Sync context just in case
  userStore.syncUserContext('submission')
  checkLoginAndRedirect()
})

watch(submissionUser, () => {
  checkLoginAndRedirect()
})

const goHome = () => {
  userStore.logoutSubmission()
  router.push('/home')
}

const goAbout = () => {
  router.push('/submission/about')
}

const goHelp = () => {
  router.push('/submission/help')
}

// Toggle between login and register
const toggleRegister = () => {
  showRegister.value = !showRegister.value
}

// Go back to login
const goToLogin = () => {
  showRegister.value = false
}
</script>

<template>
  <div class="submission-module">
    <header class="subnav">
      <div class="subnav-container">
        <div class="brand">{{ t('submission.brand') }}</div>
        <ul class="nav">
          <li><a href="#" @click.prevent="goHome">{{ t('submission.nav.home') }}</a></li>
          <li><a href="#" @click.prevent="goAbout">{{ t('submission.nav.about') }}</a></li>
          <li><a href="#" @click.prevent="goHelp">{{ t('submission.nav.help') }}</a></li>
        </ul>
      </div>
    </header>
    <main class="content">
      <div class="main-container">
        <aside class="sidebar">
          <div class="journal-cover">
            <img src="/images/24.jpg" alt="Journal Cover" class="cover-img" @error="(e) => e.target.src = 'https://via.placeholder.com/240x320?text=Journal+Cover'" />
          </div>
          <ul class="sidebar-links">
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">ℹ️</span>
                {{ t('submission.sidebar.instruction') }}
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">📖</span>
                {{ t('submission.sidebar.about') }}
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">✅</span>
                {{ t('submission.sidebar.checklist') }}
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">👥</span>
                {{ t('submission.sidebar.reviewers') }}
              </a>
            </li>
          </ul>
        </aside>
        
        <div class="main-login-area">
          <div class="welcome-banner">
            <h2>{{ t('submission.welcome.title') }}</h2>
            <h3>{{ t('submission.welcome.platform') }}</h3>
          </div>
          
          <div v-if="!submissionUser" class="login-wrapper">
            <Login v-if="!showRegister" @toggle-register="toggleRegister" />
            <AdminRegister v-else @go-to-login="goToLogin" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.submission-module {
  min-height: 100vh;
  background: #fff;
  font-family: Arial, sans-serif;
}
.subnav {
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
  padding: 0.5rem 0;
}
.subnav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.nav {
  display: flex;
  list-style: none;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
  justify-content: flex-start;
}
.brand {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.2rem;
}
.nav {
  display: flex;
  list-style: none;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
}
.nav a {
  color: #333;
  text-decoration: none;
  font-size: 0.95rem;
}
.nav a:hover {
  color: #3498db;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.main-container {
  display: flex;
  gap: 2rem;
}

.sidebar {
  width: 250px;
  flex-shrink: 0;
}

.journal-cover {
  margin-bottom: 2rem;
  border: 1px solid #ddd;
  padding: 5px;
}

.cover-img {
  width: 100%;
  height: auto;
  display: block;
}

.sidebar-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 0;
  color: #2c3e50;
  text-decoration: none;
  font-size: 0.95rem;
  border-bottom: 1px solid #eee;
}

.sidebar-link:hover {
  color: #3498db;
}

.sidebar-link .icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

.main-login-area {
  flex: 1;
}

.welcome-banner {
  margin-bottom: 2rem;
}

.welcome-banner h2 {
  font-size: 1.2rem;
  font-weight: normal;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.welcome-banner h3 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.login-wrapper {
  max-width: 600px;
}

@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
  }
}
</style>
