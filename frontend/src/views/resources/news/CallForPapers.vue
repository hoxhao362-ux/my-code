<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-news-calls'"
      :logout="userStore.logout"
    />
    <h1>{{ $t('news.calls.title') }}</h1>
    <p class="intro">{{ $t('news.calls.intro') }}</p>

    <div class="cards-grid">
      <div v-for="call in activeCalls" :key="call.id" class="call-card">
        <h2 class="card-title">{{ call.title }}</h2>
        <div class="card-info">
          <p><strong>{{ $t('news.calls.deadline') }}</strong> <span class="deadline">{{ call.deadline }}</span></p>
          <p><strong>{{ $t('news.calls.guestEditor') }}</strong> {{ call.editor }}</p>
        </div>
        <p class="card-desc">{{ call.description }}</p>
        <button class="btn-submit" @click="submitManuscript(call.id)">{{ $t('news.calls.submitNow') }}</button>
      </div>
    </div>

    <div class="past-calls">
      <h3>{{ $t('news.calls.pastIssues') }}</h3>
      <ul>
        <li v-for="past in pastCalls" :key="past.id">
          <a href="#">{{ past.title }} ({{ $t('news.calls.ended', { date: past.deadline }) }})</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const router = useRouter()

// TODO: In a real app, fetch these from an API (/api/calls-for-papers)
const activeCalls = computed(() => [
  {
    id: 1,
    title: "AI in Medical Diagnosis",
    deadline: "2026-06-30",
    editor: "Dr. Alan Turing",
    description: "Exploring the role of artificial intelligence in early disease detection and treatment planning."
  },
  {
    id: 2,
    title: "Pandemic Preparedness",
    deadline: "2026-08-15",
    editor: "Dr. Sarah Gilbert",
    description: "Lessons learned from COVID-19 and strategies for future global health crises."
  },
  {
    id: 3,
    title: "Mental Health in the Digital Age",
    deadline: "2026-09-01",
    editor: "Dr. Sigmund Freud",
    description: "Impact of social media and digital connectivity on adolescent mental health."
  }
])

const pastCalls = computed(() => [
  { id: 101, title: "Telemedicine Advances", deadline: "2025-12-31" },
  { id: 102, title: "Vaccine Equity", deadline: "2025-06-30" }
])

const submitManuscript = (id) => {
  // Redirect to submission system with special issue ID if supported
  router.push('/submission/login')
}
</script>

<style scoped>
.page-container {
  max-width: 1000px;
  margin: 80px auto 0;
  padding: 40px 24px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.intro {
  color: #666;
  margin-bottom: 40px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.call-card {
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  padding: 24px;
  background: white;
  transition: box-shadow 0.3s;
}

.call-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}

.card-info {
  font-size: 14px;
  color: #333;
  margin-bottom: 12px;
}

.deadline {
  color: #C93737;
  font-weight: bold;
}

.card-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 24px;
}

.btn-submit {
  background-color: #C93737;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-submit:hover {
  background-color: #A02C2C;
}

.past-calls {
  border-top: 1px solid #E5E5E5;
  padding-top: 24px;
}

.past-calls h3 {
  font-size: 16px;
  color: #666;
  margin-bottom: 16px;
}

.past-calls ul {
  list-style: none;
  padding: 0;
}

.past-calls li {
  margin-bottom: 8px;
}

.past-calls a {
  color: #999;
  text-decoration: none;
  font-size: 14px;
}

.past-calls a:hover {
  color: #C93737;
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
