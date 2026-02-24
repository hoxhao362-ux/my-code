<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navigation from '../../components/Navigation.vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)

// --- Mock Data Enrichment ---
const rawJournals = computed(() => {
  let baseList = userStore.journals && userStore.journals.length > 0 ? userStore.journals : []
  
  if (baseList.length === 0) {
       baseList = [
         { id: 1, title: 'Journal of Oncology', module: 'Oncology' },
         { id: 2, title: 'Journal of Neurology', module: 'Neuroscience' },
         { id: 3, title: 'Journal of Global Health', module: 'Public Health' },
         { id: 4, title: 'Journal of Respiratory Medicine', module: 'Clinical Medicine' },
         { id: 5, title: 'Journal of Infectious Diseases', module: 'Clinical Medicine' }
       ]
    }

  return baseList.map((j, index) => ({
    ...j,
    title: j.title || `Journal ${index + 1}`,
    if: (Math.random() * 60 + 10).toFixed(3),
    reviewTime: Math.floor(Math.random() * 60 + 20),
    acceptanceRate: Math.floor(Math.random() * 20 + 5) + '%',
    annualPublications: Math.floor(Math.random() * 200 + 50),
    yearFounded: 1900 + Math.floor(Math.random() * 120),
    isOA: Math.random() > 0.3,
    description: 'Leading journal driving basic research to clinical translation and global health improvement.',
    categories: [j.module || 'General', 'Clinical Research', 'Reviews'],
  }))
})

// --- Filter State ---
const selectedField = ref('All Fields')
const fields = ['All Fields', 'Oncology', 'Neuroscience', 'Clinical Medicine', 'Public Health']

const coreAttributes = ref({
  highIF: false,     // IF >= 40
  fastReview: false, // <= 40 days
  oa: false          // Open Access
})

const sortBy = ref('if_desc')
const sortOptions = [
  { label: 'IF (Descending)', value: 'if_desc' },
  { label: 'IF (Ascending)', value: 'if_asc' },
  { label: 'Year Founded', value: 'year' },
  { label: 'Annual Publications', value: 'pub' }
]

// --- Interaction State ---
const expandedJournalId = ref(null)

// --- Subscription State ---
const subscribedJournals = ref([]) // Array of { id: number, preferences: [] }
const subscriptionModal = reactive({
  visible: false,
  journal: null
})
const subscriptionForm = reactive({
  email: '',
  preferences: []
})
const preferenceOptions = ['Table of Contents', 'Articles in Press', 'News & Events']

onMounted(() => {
  const stored = localStorage.getItem('subscribed_journals')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      // Migration: If array of numbers, convert to objects
      if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'number') {
        subscribedJournals.value = parsed.map(id => ({ id, preferences: ['Table of Contents'] }))
      } else {
        subscribedJournals.value = parsed
      }
    } catch (e) {
      console.error('Failed to parse subscriptions', e)
    }
  }
})

const isSubscribed = (id) => subscribedJournals.value.some(s => s.id === id)

const saveSubscriptions = () => {
  localStorage.setItem('subscribed_journals', JSON.stringify(subscribedJournals.value))
}

const openSubscriptionModal = (journal) => {
  subscriptionModal.journal = journal
  subscriptionModal.visible = true
  // Reset form
  subscriptionForm.email = user.value?.email || ''
  subscriptionForm.preferences = ['Table of Contents'] // Default
}

const handleUnsubscribe = (id) => {
  if (confirm('Are you sure you want to unsubscribe?')) {
     subscribedJournals.value = subscribedJournals.value.filter(s => s.id !== id)
     saveSubscriptions()
     alert('Successfully unsubscribed')
  }
}

const confirmSubscription = () => {
  if (!subscriptionForm.email || !subscriptionForm.email.includes('@')) {
    alert('Please enter a valid email address.')
    return
  }
  
  const newSub = {
    id: subscriptionModal.journal.id,
    email: subscriptionForm.email,
    preferences: [...subscriptionForm.preferences]
  }
  
  subscribedJournals.value.push(newSub)
  saveSubscriptions()
  alert('Successfully subscribed to manuscript updates')
  subscriptionModal.visible = false
}

const toggleSubscription = (journal) => {
  if (isSubscribed(journal.id)) {
    handleUnsubscribe(journal.id)
  } else {
    openSubscriptionModal(journal)
  }
}

const toggleExpand = (id) => {
  if (expandedJournalId.value === id) {
    expandedJournalId.value = null
  } else {
    expandedJournalId.value = id
  }
}

const clearFilters = () => {
  selectedField.value = 'All Fields'
  coreAttributes.value = { highIF: false, fastReview: false, oa: false }
  sortBy.value = 'if_desc'
}

// --- Computed Logic ---
const filteredJournals = computed(() => {
  let list = [...rawJournals.value]

  // 1. Field Filter
  if (selectedField.value !== 'All Fields') {
    list = list.filter(j => j.module === selectedField.value || (j.categories && j.categories.includes(selectedField.value)))
  }

  // 2. Core Attributes Filter
  if (coreAttributes.value.highIF) {
    list = list.filter(j => parseFloat(j.if) >= 40)
  }
  if (coreAttributes.value.fastReview) {
    list = list.filter(j => j.reviewTime <= 40)
  }
  if (coreAttributes.value.oa) {
    list = list.filter(j => j.isOA)
  }

  // 3. Sorting
  list.sort((a, b) => {
    if (sortBy.value === 'if_desc') return parseFloat(b.if) - parseFloat(a.if)
    if (sortBy.value === 'if_asc') return parseFloat(a.if) - parseFloat(b.if)
    if (sortBy.value === 'year') return b.yearFounded - a.yearFounded
    if (sortBy.value === 'pub') return b.annualPublications - a.annualPublications
    return 0
  })

  return list
})

const handleSubmit = (id) => {
  router.push('/submit')
}

const goToFullText = (id) => {
  // Check permission (mock logic as per requirements)
  // Public articles go directly, restricted ones check login/sub
  // For demo, we assume public access to detail page, detail page handles content logic
  router.push(`/journal/${id}`)
}

</script>

<template>
  <div class="page-wrapper">
    <Navigation :user="user" :current-page="'journals'" :logout="userStore.logout" />

    <main class="main-container">
      <!-- Filter Bar -->
      <section class="filter-bar">
        <div class="filter-group">
          <label>Field</label>
          <div class="select-wrapper">
            <select v-model="selectedField">
              <option v-for="f in fields" :key="f" :value="f">{{ f }}</option>
            </select>
          </div>
        </div>

        <div class="filter-group checkbox-group">
          <label>Core Attributes</label>
          <div class="checkboxes">
            <label class="checkbox-label">
              <input type="checkbox" v-model="coreAttributes.highIF"> High IF (≥40)
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="coreAttributes.fastReview"> Fast Review (≤40 days)
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="coreAttributes.oa"> Open Access (OA)
            </label>
          </div>
        </div>

        <div class="filter-group">
          <label>Sort By</label>
          <div class="select-wrapper">
            <select v-model="sortBy">
              <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>

        <div class="filter-actions">
           <button class="btn-clear" @click="clearFilters">Clear Filters</button>
        </div>
      </section>

      <!-- Journal List -->
      <section class="journal-list">
        <div 
          v-for="journal in filteredJournals" 
          :key="journal.id" 
          class="journal-card"
          :class="{ expanded: expandedJournalId === journal.id }"
          @click="toggleExpand(journal.id)"
        >
          <!-- Header (Collapsed State) -->
          <div class="card-header">
            <div class="journal-info-simple">
              <!-- Title as entry point to full text -->
              <h3 class="journal-name clickable-title" @click.stop="goToFullText(journal.id)">
                {{ journal.title }}
                <span v-if="isSubscribed(journal.id)" class="subscribed-badge">Subscribed</span>
              </h3>
              <div class="journal-stats-inline">
                <span class="stat-item">IF: {{ journal.if }}</span>
                <span class="divider">/</span>
                <span class="stat-item">Review: {{ journal.reviewTime }} days</span>
              </div>
            </div>
            
            <!-- Minimalist Triangle Icon -->
            <div class="expand-icon-container" @click.stop="toggleExpand(journal.id)">
              <div class="triangle-icon" :class="{ rotated: expandedJournalId === journal.id }"></div>
            </div>
          </div>

          <!-- Expanded Content -->
          <div class="card-body" v-if="expandedJournalId === journal.id" @click.stop>
            <div class="detail-row description">
              <span class="label">About</span>
              <p>{{ journal.description }}</p>
            </div>
            
            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">Sections</span>
                <div class="tags">
                  <span v-for="cat in journal.categories" :key="cat" class="tag">{{ cat }}</span>
                </div>
              </div>
              
              <div class="detail-item">
                <span class="label">Key Data</span>
                <div class="stats-grid">
                  <div class="stat">
                    <span class="val">{{ journal.annualPublications }}</span>
                    <span class="key">Annual Pubs</span>
                  </div>
                  <div class="stat">
                    <span class="val">{{ journal.acceptanceRate }}</span>
                    <span class="key">Acceptance Rate</span>
                  </div>
                  <div class="stat">
                    <span class="val">{{ journal.yearFounded }}</span>
                    <span class="key">Founded</span>
                  </div>
                </div>
              </div>

              <div class="detail-item actions-col">
                <div class="links">
                  <a href="#" class="link-item">Submission Guidelines &rarr;</a>
                  <a href="#" class="link-item">Template Download &rarr;</a>
                </div>
                <!-- Submit Action moved here -->
                <button class="btn-submit-inline" @click="handleSubmit(journal.id)">Submit Manuscript</button>
                
                <!-- Subscription Action -->
                <button 
                  class="btn-subscribe" 
                  :class="isSubscribed(journal.id) ? 'btn-unsubscribe' : 'btn-subscribe-action'"
                  @click.stop="toggleSubscription(journal)"
                >
                  {{ isSubscribed(journal.id) ? 'Unsubscribe' : 'Subscribe' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredJournals.length === 0" class="empty-state">
          No journals match your criteria.
        </div>
      </section>
    </main>

    <!-- Subscription Modal -->
    <div v-if="subscriptionModal.visible" class="modal-overlay" @click="subscriptionModal.visible = false">
      <div class="modal-content" @click.stop>
        <h3>Subscribe to {{ subscriptionModal.journal?.title }}</h3>
        <p>Stay updated with the latest research and journal news.</p>
        
        <div class="form-group">
          <label>Email Address <span class="required">*</span></label>
          <input 
            type="email" 
            v-model="subscriptionForm.email" 
            placeholder="Enter your email" 
            class="modal-input" 
            :disabled="!!user"
          />
          <span v-if="user" class="input-hint">Using your account email</span>
        </div>
        
        <div class="form-group">
          <label>Subscription Preferences <span class="required">*</span></label>
          <div class="checkbox-group">
            <label v-for="opt in preferenceOptions" :key="opt" class="checkbox-label-modal">
              <input type="checkbox" :value="opt" v-model="subscriptionForm.preferences"> {{ opt }}
            </label>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="btn-cancel" @click="subscriptionModal.visible = false">Cancel</button>
          <button class="btn-confirm" @click="confirmSubscription">Confirm Subscription</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Reset & Base */
* {
  box-sizing: border-box;
}

.page-wrapper {
  background-color: #f9f9f9;
  min-height: 100vh;
  padding-top: 120px; /* Nav height, increased to avoid content being blocked */
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #333;
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  background: white;
  padding: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.select-wrapper select {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 160px;
  color: #333;
  background-color: white;
  cursor: pointer;
  outline: none;
}

.select-wrapper select:focus {
  border-color: #333;
}

.checkboxes {
  display: flex;
  gap: 15px;
  align-items: center;
  height: 35px;
}

.checkbox-label {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #333;
}

.btn-clear {
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 0;
  height: 35px;
  border-bottom: 1px solid transparent;
  transition: all 0.2s;
}

.btn-clear:hover {
  color: #e74c3c;
  border-bottom-color: #e74c3c;
}

.filter-actions {
  margin-left: auto;
  padding-bottom: 2px;
}

/* Journal List */
.journal-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.journal-card {
  background: white;
  border: 1px solid #eee;
  position: relative; /* For absolute positioning of icon */
  cursor: pointer;
}

.journal-card:hover {
  border-color: #ccc;
}

/* Header */
.card-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  min-height: 80px; /* Consistent height */
}

.journal-info-simple {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.journal-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #333;
  transition: all 0.2s ease;
}

.clickable-title {
  cursor: pointer;
}

.clickable-title:hover {
  color: #0056B3; /* Brand Color */
  text-decoration: underline;
  text-decoration-thickness: 1px;
}

.journal-stats-inline {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 8px;
  align-items: center;
}

.divider {
  color: #ddd;
}

/* Triangle Icon */
.expand-icon-container {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
}

.expand-icon-container:hover {
  background-color: #f5f5f5;
}

/* CSS Triangle */
.triangle-icon {
  width: 0; 
  height: 0; 
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #666; /* Down pointing */
}

.triangle-icon.rotated {
  transform: rotate(180deg);
  border-top-color: #333; /* Darker when active */
}

/* Body */
.card-body {
  padding: 0 20px 20px 20px;
  border-top: 1px solid #f9f9f9;
  /* No animation as requested */
}

.detail-row {
  margin-top: 15px;
}

.detail-row p {
  margin: 5px 0 0 0;
  font-size: 14px;
  color: #555;
  line-height: 1.5;
}

.label {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  text-transform: uppercase;
  display: block;
  margin-bottom: 5px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr 1fr;
  gap: 20px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #f5f5f5;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #f0f0f0;
  color: #555;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 2px;
}

.stats-grid {
  display: flex;
  flex-direction: column; /* Stack stats in expanded view? User said "Core Data (Year/Acceptance/Founded)" */
  /* Or row? Grid fits better. Let's do row wrap or stack. The mockup implies they are key data points. */
  gap: 15px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .val {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.stat .key {
  font-size: 11px;
  color: #888;
}

.actions-col {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  gap: 15px;
}

.links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  font-size: 13px;
  color: #0056B3;
  text-decoration: none;
  font-weight: 500;
}

.link-item:hover {
  text-decoration: underline;
}

.btn-submit-inline {
  background: #0056B3;
  color: white;
  border: none;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit-inline:hover {
  background: #004494;
}

.btn-subscribe {
  border: none;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}

.btn-subscribe-action {
  background: #0056B3; /* Brand Blue */
  color: white;
}

.btn-subscribe-action:hover {
  background: #004494;
}

.btn-unsubscribe {
  background: #999;
  color: white;
}

.btn-unsubscribe:hover {
  background: #777;
}

.subscribed-badge {
  display: inline-block;
  background-color: #4caf50; /* Green */
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  vertical-align: middle;
  font-weight: normal;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
  background: white;
  border: 1px dashed #ddd;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 450px;
  color: #333;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.modal-content h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}
.modal-content p {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.form-group {
  margin-bottom: 1.25rem;
}
.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #333;
}
.required {
  color: #dc3545;
}
.modal-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 0.9rem;
}
.modal-input:disabled {
  background-color: #f5f5f5;
  color: #666;
}
.input-hint {
  font-size: 0.8rem;
  color: #888;
  margin-top: 4px;
  display: block;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
.checkbox-label-modal {
  font-weight: normal;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
}
.modal-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.btn-cancel {
  background: #f1f1f1;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
  font-weight: 500;
}
.btn-confirm {
  background: #0056B3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.btn-confirm:hover {
  background: #004494;
}
.btn-cancel:hover {
  background: #e5e5e5;
}

/* Responsive */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 10px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    flex-direction: row;
    justify-content: space-between;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    min-height: auto;
  }

  .expand-icon-container {
    top: 20px;
    right: 20px;
  }
}
</style>
