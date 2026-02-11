<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useI18n } from '../../../composables/useI18n'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { t } = useI18n()

const user = computed(() => userStore.submissionUser)

const goHome = () => {
  // Return to main site home, clears submission session if needed or just navigates
  // Requirement says: "Submission route Home button only jumps back to Main Site Home"
  userStore.logoutSubmission()
  router.push('/home')
}

const goSubmit = () => {
  router.push('/submission/author/submit')
}

const goMainMenu = () => {
  router.push('/admin/author-dashboard')
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
          <li class="menu-item"><a href="#" @click.prevent="goMainMenu">Main Menu</a></li>
          <li class="menu-item active"><a href="#" @click.prevent="goSubmit">Submit a Manuscript</a></li>
          <li class="menu-item"><a href="#">About ▼</a></li>
          <li class="menu-item"><a href="#">Help ▼</a></li>
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
</style>