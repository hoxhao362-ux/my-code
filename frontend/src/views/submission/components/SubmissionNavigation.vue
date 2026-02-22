<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useI18n } from '../../../composables/useI18n'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { t } = useI18n()

const user = computed(() => userStore.submissionUser)
const showAboutMenu = ref(false)
const showHelpMenu = ref(false)

const goHome = () => {
  // Return to main site home, clears submission session if needed or just navigates
  // Requirement says: "Submission route Home button only jumps back to Main Site Home"
  userStore.logoutSubmission()
  router.push('/home')
}

const goSubmit = () => {
  router.push({ name: 'submission-process' })
}

const goMainMenu = () => {
  router.push('/admin/writer-dashboard')
}

const handleLogout = () => {
  userStore.logoutSubmission()
  router.push('/submission')
}
</script>

<template>
  <nav class="submission-navbar">
    <div class="nav-container">
      <div class="nav-left">
        <span class="brand">Journal Submission Platform</span>
      </div>
      
      <div class="nav-right">
        <span v-if="user" class="user-info">
          {{ user.username }} | <a href="#" @click.prevent="handleLogout" class="logout-link">Logout</a>
        </span>
      </div>
    </div>
    
    <div class="nav-menu-bar">
      <div class="menu-container">
        <ul class="menu-list">
          <li class="menu-item"><a href="#" @click.prevent="goHome">Home</a></li>
          <li class="menu-item" :class="{ active: route.path === '/admin/writer-dashboard' }"><a href="#" @click.prevent="goMainMenu">Main Menu</a></li>
          <li class="menu-item" :class="{ active: route.path === '/submission/writer/submit' }"><a href="#" @click.prevent="goSubmit">Submit a Manuscript</a></li>
          <li class="menu-item" :class="{ active: route.path === '/writer/letters' }"><a href="#" @click.prevent="router.push('/writer/letters')">Letters</a></li>
          
          <!-- About Dropdown -->
          <li class="menu-item dropdown" 
              @mouseenter="showAboutMenu = true" 
              @mouseleave="showAboutMenu = false">
            <a href="#">About ▼</a>
            <ul class="dropdown-menu" v-if="showAboutMenu">
              <li><a href="#" @click.prevent="router.push('/about/editorial-board')">Editorial Board</a></li>
              <li><a href="#" @click.prevent="router.push('/about/journal-info')">Journal Info</a></li>
              <li><a href="#" @click.prevent="router.push('/about/history')">History</a></li>
            </ul>
          </li>

          <!-- Help Dropdown -->
          <li class="menu-item dropdown" 
              @mouseenter="showHelpMenu = true" 
              @mouseleave="showHelpMenu = false">
            <a href="#">Help ▼</a>
            <ul class="dropdown-menu" v-if="showHelpMenu">
              <li><a href="#" @click.prevent="router.push('/submission/help')">Help Center</a></li>
              <li><a href="#" @click.prevent="router.push('/submission/submission-rules')">Submission Rules</a></li>
              <li><a href="#" @click.prevent="router.push('/admin/help/feedback')">Feedback</a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.submission-navbar {
  background: white;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  display: flex;
  align-items: center;
}

.user-info {
  font-size: 0.9rem;
  color: #333;
}

.logout-link {
  color: #333;
  text-decoration: none;
}

.logout-link:hover {
  text-decoration: underline;
}

.nav-menu-bar {
  background: #e0e0e0;
  border-top: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
}

.menu-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.menu-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-item {
  position: relative;
}

.menu-item a {
  display: block;
  padding: 0.8rem 1.5rem;
  text-decoration: none;
  color: #333;
  font-size: 0.95rem;
  font-weight: normal;
}

.menu-item a:hover {
  background: #d0d0d0;
}

.menu-item.active a {
  font-weight: bold;
}

/* Dropdown Styles */
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #ccc;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  list-style: none;
  padding: 0;
  margin: 0;
  min-width: 180px;
  z-index: 1000;
}

.dropdown-menu li {
  border-bottom: 1px solid #eee;
}

.dropdown-menu li:last-child {
  border-bottom: none;
}

.dropdown-menu li a {
  padding: 10px 15px;
  color: #333;
  font-size: 0.9rem;
  display: block;
  text-decoration: none;
}

.dropdown-menu li a:hover {
  background-color: #f5f5f5;
  color: #005696;
}
</style>