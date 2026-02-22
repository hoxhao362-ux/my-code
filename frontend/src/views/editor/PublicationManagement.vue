<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'

const userStore = useUserStore()
const router = useRouter()

// Get accepted manuscripts
const acceptedManuscripts = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED || 
    journal.status === MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION || 
    journal.status === MANUSCRIPT_STATUS.PENDING_COPYRIGHT || 
    journal.status === MANUSCRIPT_STATUS.PENDING_PROOF || 
    journal.status === MANUSCRIPT_STATUS.PENDING_PUBLICATION || 
    journal.status === MANUSCRIPT_STATUS.PUBLISHED
  )
})

// Navigate to publication process for a manuscript
const goToPublicationProcess = (manuscriptId) => {
  router.push(`/editor/publication/${manuscriptId}`)
}
</script>

<template>
  <div class="publication-management">
    <div class="page-header">
      <h2>Publication Management</h2>
      <p>Manage the publication process for accepted manuscripts</p>
    </div>
    
    <div class="manuscripts-list">
      <h3>Accepted Manuscripts</h3>
      <div class="manuscripts-grid">
        <div 
          v-for="manuscript in acceptedManuscripts" 
          :key="manuscript.id"
          class="manuscript-card"
          @click="goToPublicationProcess(manuscript.id)"
        >
          <div class="manuscript-card-header">
            <span class="manuscript-id">ID: {{ manuscript.id }}</span>
            <span class="manuscript-status">{{ manuscript.status }}</span>
          </div>
          <h4 class="manuscript-title">{{ manuscript.title }}</h4>
          <div class="manuscript-meta">
            <p>Author: {{ manuscript.writer }}</p>
            <p>Module: {{ manuscript.module }}</p>
            <p>Submitted: {{ manuscript.submissionDate }}</p>
          </div>
          <div class="manuscript-actions">
            <button class="btn btn-red">Manage Publication</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.publication-management {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.publication-management .page-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #333;
}

.publication-management .page-header h2 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.publication-management .page-header p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.manuscripts-list h3 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.manuscripts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.manuscript-card {
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.manuscript-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-color: #C93737;
}

.manuscript-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.manuscript-id {
  font-size: 12px;
  font-weight: bold;
  color: #666;
}

.manuscript-status {
  font-size: 12px;
  font-weight: bold;
  color: #28A745;
  background: #e8f5e8;
  padding: 4px 8px;
  border-radius: 12px;
}

.manuscript-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  line-height: 1.4;
}

.manuscript-meta {
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.manuscript-meta p {
  margin: 5px 0;
}

.manuscript-actions {
  text-align: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.btn-red {
  background: #C93737;
  color: white;
}

.btn-red:hover {
  background: #B02E2E;
}
</style>