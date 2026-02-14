<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Login from './Login.vue'

const router = useRouter()
const userStore = useUserStore()
// Use store state for reactivity
const submissionUser = computed(() => userStore.submissionUser)

// Redirect to dashboard if already logged in
const checkLoginAndRedirect = () => {
  if (submissionUser.value) {
    const role = submissionUser.value.role
    if (role === 'author') {
      router.push('/submission/author/submit')
    } else if (role === 'reviewer') {
      router.push('/submission/reviewer/dashboard')
    } else if (role === 'editor' || role === 'admin') { // Renamed from admin to editor
      router.push('/submission/editor/dashboard')
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
</script>

<template>
  <div class="submission-module">
    <header class="subnav">
      <div class="subnav-container">
        <div class="brand">Submission Module</div>
        <ul class="nav">
          <li><a href="#" @click.prevent="goHome">Home</a></li>
          <li><a href="#" @click.prevent="goAbout">About</a></li>
          <li><a href="#" @click.prevent="goHelp">Help</a></li>
        </ul>
      </div>
    </header>
    <main class="content">
      <div class="main-container">
        <aside class="sidebar">
          <div class="journal-cover">
            <!-- Using a placeholder image from public folder -->
            <img src="/images/24.jpg" alt="Journal Cover" class="cover-img" />
          </div>
          <ul class="sidebar-links">
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">ℹ️</span>
                Instruction for Authors
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">📖</span>
                About the Journal
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">✅</span>
                Pre-submission checklist
              </a>
            </li>
            <li>
              <a href="#" class="sidebar-link">
                <span class="icon">👥</span>
                Peer Reviewers
              </a>
            </li>
          </ul>
        </aside>
        
        <div class="main-login-area">
          <div class="welcome-banner">
            <h2>Welcome to Submission Module for</h2>
            <h3>Journal Submission Platform</h3>
          </div>
          
          <div v-if="!submissionUser" class="login-wrapper">
            <Login />
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
