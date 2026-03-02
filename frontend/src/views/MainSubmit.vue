<script setup>
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'
import { useSubmissionStore } from '../stores/submission'
import { useI18n } from '../composables/useI18n'
import Navigation from '../components/Navigation.vue'

// Components
import ProgressBar from '../components/submission/ProgressBar.vue'
import Step1ArticleType from '../components/submission/Step1ArticleType.vue'
import Step2AttachFiles from '../components/submission/Step2AttachFiles.vue'
import Step3GeneralInfo from '../components/submission/Step3GeneralInfo.vue'
import Step4AdditionalInfo from '../components/submission/Step4AdditionalInfo.vue'
import Step5Comments from '../components/submission/Step5Comments.vue'
import Step6ManuscriptData from '../components/submission/Step6ManuscriptData.vue'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const submissionStore = useSubmissionStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

// Toggle directory
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// Check login
onMounted(() => {
  if (!userStore.user && route.path === '/submit') {
    // router.push('/login') // Uncomment if strict login required
  }
  submissionStore.init()
})

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="main-submit-container">
    <Navigation 
      :user="userStore.user"
      :current-page="'submit'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <main class="main-content">
      <div class="submit-wrapper">
        <!-- Submission Rules Page -->
        <template v-if="route.path === '/submission-rules'">
          <div class="rules-container">
             <h2 class="page-title">{{ t('submissionRules.title') }}</h2>
             <div class="rules-content">
                <p>{{ t('submissionRules.intro') }}</p>
                <ul class="rules-list">
                  <li><strong>{{ t('submissionRules.format') }}:</strong> {{ t('submissionRules.formatDesc') }}</li>
                  <li><strong>{{ t('submissionRules.authors') }}:</strong> {{ t('submissionRules.authorsDesc') }}</li>
                  <li><strong>{{ t('submissionRules.originality') }}:</strong> {{ t('submissionRules.originalityDesc') }}</li>
                </ul>
                <div class="actions">
                  <button class="btn btn-primary" @click="router.push('/submit')">{{ t('submissionRules.start') }}</button>
                </div>
             </div>
          </div>
        </template>

        <!-- Submission Process -->
        <template v-else>
          <ProgressBar />
          
          <div class="step-content">
            <KeepAlive>
              <component :is="[
                null,
                Step1ArticleType,
                Step2AttachFiles,
                Step3GeneralInfo,
                Step4AdditionalInfo,
                Step5Comments,
                Step6ManuscriptData
              ][submissionStore.currentStep]" />
            </KeepAlive>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main-submit-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 120px auto 0;
  padding: 2rem;
}

.submit-wrapper {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: 600px;
}

/* Rules Styles */
.rules-container {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

.rules-list {
  line-height: 1.8;
  color: #555;
  margin-bottom: 2rem;
  padding-left: 20px;
}

.actions {
  text-align: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-size: 16px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}
</style>
