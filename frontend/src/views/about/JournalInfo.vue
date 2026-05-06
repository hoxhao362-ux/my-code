<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { useI18n } from '../../composables/useI18n'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const showToast = ref(false)
const { t } = useI18n()

const copyISSN = () => {
  navigator.clipboard.writeText("XXXX-XXXX (Print), XXXX-XXXX (Online)").then(() => {
    showToast.value = true
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  })
}
</script>

<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'about-journal-info'"
      :logout="userStore.logout"
    />
    
    <div class="content-area">
      <div class="header-section">
        <h1>{{ t('about.journalInfo.title') }}</h1>
        <button class="copy-btn" @click="copyISSN">
          {{ t('about.journalInfo.copyISSN') }}
        </button>
      </div>

      <div class="info-block">
        <h2>{{ t('about.journalInfo.basicInfo') }}</h2>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.issnPrint') }}:</span>
          <span class="value">XXXX-XXXX</span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.issnOnline') }}:</span>
          <span class="value">XXXX-XXXX</span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.founded') }}:</span>
          <span class="value">2024</span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.frequency') }}:</span>
          <span class="value">Monthly</span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.impactFactor') }}:</span>
          <a href="#" class="link-value">{{ t('about.journalInfo.newJournal') }}</a>
        </div>
        <div class="info-row">
          <span class="label">{{ t('about.journalInfo.indexedIn') }}:</span>
          <div class="databases">
            <a href="#" class="db-link">Google Scholar</a>
            <a href="#" class="db-link">DOAJ</a>
          </div>
        </div>
      </div>

      <div class="info-block">
        <h2>{{ t('about.journalInfo.aimsScope') }}</h2>
        <p>{{ t('about.journalInfo.aimsScopeText') }}</p>
      </div>

      <div class="info-block">
        <h2>{{ t('about.journalInfo.copyright') }}</h2>
        <p>{{ t('about.journalInfo.copyrightText') }}</p>
      </div>

      <div class="info-block">
        <h2>{{ t('about.journalInfo.ethics') }}</h2>
        <p>{{ t('about.journalInfo.ethicsText') }}</p>
      </div>

      <div class="info-block">
        <h2>{{ t('about.journalInfo.contact') }}</h2>
<<<<<<< HEAD
        <p>{{ t('about.journalInfo.technicalIssues') }} <a href="mailto:support@journalplatform.com" class="link-text">support@journalplatform.com</a></p>
        <p>{{ t('about.journalInfo.submissionQueries') }} <a href="mailto:editorial@journalplatform.com" class="link-text">editorial@journalplatform.com</a></p>
=======
        <p>{{ t('about.journalInfo.technicalIssues') }} <a href="mailto:support@peerexpeer.com" class="link-text">support@peerexpeer.com</a></p>
        <p>{{ t('about.journalInfo.submissionQueries') }} <a href="mailto:editorial@peerexpeer.com" class="link-text">editorial@peerexpeer.com</a></p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>
    </div>

    <div v-if="showToast" class="toast">
      {{ t('about.journalInfo.copied') }}
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
