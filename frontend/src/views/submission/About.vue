<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const goHome = () => {
  userStore.logoutSubmission()
  router.push('/home')
}
const goAbout = () => router.push('/submission/about')
const goHelp = () => router.push('/submission/help')
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
    <main class="page">
      <h2>About the Submission System</h2>
      <p>This module is dedicated to manuscript submission, peer review, and editorial workflows.</p>
    </main>
  </div>
  </template>

<style scoped>
.submission-module {
  min-height: 100vh;
  background: #f0f2f5;
}
.subnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #1f2d3d;
  color: #fff;
  padding: 0.75rem 0;
  z-index: 1000;
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
}
.nav {
  display: flex;
  list-style: none;
  gap: 1rem;
  margin: 0;
  padding: 0;
}
.nav a {
  color: #fff;
  text-decoration: none;
  padding: 0.4rem 0.75rem;
  border-radius: 4px;
}
.nav a:hover {
  background: rgba(255,255,255,0.1);
}
.page {
  max-width: 900px;
  margin: 100px auto 40px;
  padding: 0 1rem;
  font-family: Arial, sans-serif;
}
h2 {
  margin-bottom: 1rem;
}
p {
  color: #555;
}
</style>
