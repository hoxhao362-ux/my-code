<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'about-journal-info'"
      :logout="userStore.logout"
    />
    
    <div class="content-area">
      <div class="header-section">
        <h1>Journal Info (ISSN)</h1>
        <button class="copy-btn" @click="copyISSN">
          Copy ISSN
        </button>
      </div>

      <div class="info-block">
        <h2>Basic Information</h2>
        <div class="info-row">
          <span class="label">ISSN (Print):</span>
          <span class="value">0140-6736</span>
        </div>
        <div class="info-row">
          <span class="label">ISSN (Online):</span>
          <span class="value">1474-547X</span>
        </div>
        <div class="info-row">
          <span class="label">Founded:</span>
          <span class="value">1823</span>
        </div>
        <div class="info-row">
          <span class="label">Frequency:</span>
          <span class="value">Weekly</span>
        </div>
        <div class="info-row">
          <span class="label">Impact Factor (2025):</span>
          <a href="#" class="link-value">168.9 (Click to view JCR)</a>
        </div>
        <div class="info-row">
          <span class="label">Indexed In:</span>
          <div class="databases">
            <a href="#" class="db-link">PubMed</a>
            <a href="#" class="db-link">Scopus</a>
            <a href="#" class="db-link">Web of Science</a>
          </div>
        </div>
      </div>

      <div class="info-block">
        <h2>Aims & Scope</h2>
        <p>The Lancet publishes medical news, original research, and reviews on all aspects of clinical medicine and public health. We are committed to using science to improve human lives.</p>
      </div>

      <div class="info-block">
        <h2>Copyright & Open Access</h2>
        <p>Authors retain copyright under a Creative Commons Attribution (CC-BY) license. We offer Gold Open Access options for all accepted articles.</p>
      </div>

      <div class="info-block">
        <h2>Publication Ethics</h2>
        <p>We adhere to the COPE (Committee on Publication Ethics) guidelines. All manuscripts must comply with ethical standards for human and animal research.</p>
      </div>

      <div class="info-block">
        <h2>Contact Support</h2>
        <p>For technical issues: <a href="mailto:support@thelancet.com" class="link-text">support@thelancet.com</a></p>
        <p>For submission queries: <a href="mailto:editorial@thelancet.com" class="link-text">editorial@thelancet.com</a></p>
      </div>
    </div>

    <div v-if="showToast" class="toast">
      ISSN copied to clipboard.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const showToast = ref(false)

const copyISSN = () => {
  navigator.clipboard.writeText("0140-6736 (Print), 1474-547X (Online)").then(() => {
    showToast.value = true
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  })
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

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  border-bottom: 1px solid #E5E5E5;
  padding-bottom: 16px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.copy-btn {
  background-color: #C93737;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.copy-btn:hover {
  background-color: #A02C2C;
}

.info-block {
  margin-bottom: 40px;
}

h2 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E5E5;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.label {
  font-weight: bold;
  color: #333;
  width: 150px;
  flex-shrink: 0;
}

.value {
  color: #666;
}

.link-value, .link-text, .db-link {
  color: #333;
  text-decoration: none;
  border-bottom: 1px solid #E5E5E5;
  transition: all 0.3s;
}

.link-value:hover, .link-text:hover, .db-link:hover {
  color: #C93737;
  border-bottom-color: #C93737;
}

.databases {
  display: flex;
  gap: 16px;
}

p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
}

.toast {
  position: fixed;
  top: 100px;
  right: 24px;
  background-color: #333;
  color: white;
  padding: 12px 24px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
