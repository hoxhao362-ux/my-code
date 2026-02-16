<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// Filters
const selectedDiscipline = ref('all')
const selectedStatus = ref('all')
const selectedGrade = ref('all')

const disciplines = ['Clinical', 'Public Health', 'Global Health']
const grades = ['S', 'A', 'B', 'C']

// Mock Data - Reviewers (Anonymized)
const reviewers = ref([
  { id: 101, anon_id: 'REV-2026-001', discipline: 'Clinical', completed: 15, current_task: 'MS-2026-042', submitted_at: '2026-02-12', duration: '5 days', status: 'unevaluated', grade: '-', history_avg: 4.8 },
  { id: 102, anon_id: 'REV-2026-005', discipline: 'Public Health', completed: 8, current_task: 'MS-2026-038', submitted_at: '2026-02-10', duration: '12 days', status: 'evaluated', grade: 'A', history_avg: 4.2 },
  { id: 103, anon_id: 'REV-2026-012', discipline: 'Global Health', completed: 22, current_task: 'MS-2026-015', submitted_at: '2026-01-20', duration: '25 days', status: 'overdue_eval', grade: '-', history_avg: 3.5 }
])

// Evaluation Form
const showEvalModal = ref(false)
const currentReviewer = ref(null)
const evalForm = ref({
  timeliness: 5,
  professionalism: 5,
  standardization: 5,
  objectivity: 5,
  comment: ''
})

// Computed Grade
const calculatedGrade = computed(() => {
  const avg = (evalForm.value.timeliness + evalForm.value.professionalism + evalForm.value.standardization + evalForm.value.objectivity) / 4
  if (avg >= 4.8) return 'S'
  if (avg >= 4.0) return 'A'
  if (avg >= 3.0) return 'B'
  return 'C'
})

// Actions
const openEvaluation = (reviewer) => {
  currentReviewer.value = reviewer
  evalForm.value = { timeliness: 5, professionalism: 5, standardization: 5, objectivity: 5, comment: '' }
  showEvalModal.value = true
}

const submitEvaluation = () => {
  if (evalForm.value.comment.length < 30) {
    alert('Evaluation comment must be at least 30 characters.')
    return
  }
  
  // Update local state (Mock)
  currentReviewer.value.status = 'evaluated'
  currentReviewer.value.grade = calculatedGrade.value
  
  // Auto-downgrade logic (Mock)
  if (calculatedGrade.value === 'C') {
    alert(`Warning: Reviewer ${currentReviewer.value.anon_id} graded C. System will restrict future invitations.`)
  }
  
  showEvalModal.value = false
}

const viewEvaluation = (reviewer) => {
  alert(`Viewing evaluation history for ${reviewer.anon_id}...`)
}

</script>

<template>
  <div class="lancet-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user"
      current-page="audit-reviewer-management"
      :toggle-directory="()=>{}"
      :logout="userStore.logout"
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Reviewer Quality Evaluation</h1>
        <p class="warning-text">Evaluation must be objective. Results affect reviewer credit profile. Double-blind identity protection.</p>
        
        <div class="filter-bar">
           <select v-model="selectedDiscipline">
             <option value="all">All Disciplines</option>
             <option v-for="d in disciplines" :key="d" :value="d">{{ d }}</option>
           </select>
           <select v-model="selectedStatus">
             <option value="all">All Status</option>
             <option value="unevaluated">Pending Eval</option>
             <option value="evaluated">Evaluated</option>
             <option value="overdue_eval">Overdue</option>
           </select>
           <select v-model="selectedGrade">
             <option value="all">All Grades</option>
             <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
           </select>
        </div>
      </div>

      <!-- Reviewer List -->
      <table class="lancet-table">
        <thead>
          <tr>
            <th>Reviewer ID (Blind)</th>
            <th>Discipline</th>
            <th>Completed</th>
            <th>Current Task</th>
            <th>Submitted At</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reviewers" :key="r.id" class="hover-row">
            <td class="bold-text">{{ r.anon_id }}</td>
            <td>{{ r.discipline }}</td>
            <td>{{ r.completed }}</td>
            <td>{{ r.current_task }}</td>
            <td>{{ r.submitted_at }}</td>
            <td>{{ r.duration }}</td>
            <td>
              <span class="status-badge" :class="r.status">
                {{ r.status === 'unevaluated' ? 'Pending' : r.status === 'evaluated' ? 'Done' : 'Overdue' }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-red-sm" v-if="r.status === 'unevaluated'" @click="openEvaluation(r)">Evaluate</button>
              <button class="btn-text" v-else @click="viewEvaluation(r)">View Eval</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Evaluation History Footer -->
      <div class="history-section">
        <h3>Evaluation History</h3>
        <p class="audit-note">Evaluation records are automatically synced to reviewer archives.</p>
      </div>

    </main>

    <!-- Evaluation Modal -->
    <div v-if="showEvalModal" class="modal-overlay">
      <div class="modal-box large">
        <h3>Reviewer Quality Evaluation</h3>
        <p class="modal-subtitle">Target: {{ currentReviewer.anon_id }} | Task: {{ currentReviewer.current_task }}</p>
        
        <div class="rating-grid">
          <div class="rating-item">
            <label>Timeliness</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.timeliness = n" :class="{active: n <= evalForm.timeliness}">★</span>
            </div>
            <span class="score-display">{{ evalForm.timeliness }}</span>
          </div>
          <div class="rating-item">
            <label>Professionalism</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.professionalism = n" :class="{active: n <= evalForm.professionalism}">★</span>
            </div>
             <span class="score-display">{{ evalForm.professionalism }}</span>
          </div>
          <div class="rating-item">
            <label>Standardization</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.standardization = n" :class="{active: n <= evalForm.standardization}">★</span>
            </div>
             <span class="score-display">{{ evalForm.standardization }}</span>
          </div>
          <div class="rating-item">
            <label>Objectivity</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.objectivity = n" :class="{active: n <= evalForm.objectivity}">★</span>
            </div>
             <span class="score-display">{{ evalForm.objectivity }}</span>
          </div>
        </div>

        <div class="grade-preview">
          Calculated Grade: <span class="grade-badge" :class="calculatedGrade">{{ calculatedGrade }}</span>
        </div>

        <div class="form-group">
          <label>Evaluation Comment (Required, >30 chars)</label>
          <textarea v-model="evalForm.comment" rows="4" placeholder="Detailed feedback on the review quality..."></textarea>
          <p class="char-count">{{ evalForm.comment.length }} / 30 chars</p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-grey" @click="showEvalModal = false">Cancel</button>
          <button class="btn btn-red" @click="submitEvaluation">Submit Evaluation</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.lancet-container {
  font-family: 'Times New Roman', Times, serif;
  background-color: #FFFFFF;
  min-height: 100vh;
  color: #333333;
}

.content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.main-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.warning-text {
  font-size: 12px;
  color: #D1202F;
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.filter-bar select {
  padding: 6px 12px;
  border: 1px solid #CCC;
  font-family: 'Times New Roman';
  min-width: 150px;
}

/* Table */
.lancet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.lancet-table th {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid #CCC;
  font-weight: bold;
  color: #555;
}

.lancet-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #EEE;
  vertical-align: middle;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  text-transform: uppercase;
}
.status-badge.unevaluated { background: #E3F2FD; color: #1565C0; }
.status-badge.evaluated { background: #E8F5E9; color: #2E7D32; }
.status-badge.overdue_eval { background: #FFEBEE; color: #C62828; }

.btn-red-sm {
  background: #D1202F;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-text {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 12px;
  text-decoration: underline;
}

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-box.large {
  width: 600px;
  padding: 30px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.rating-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.rating-item label {
  display: block;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 5px;
}

.stars {
  color: #CCC;
  font-size: 20px;
  cursor: pointer;
  display: inline-block;
}

.stars span.active {
  color: #FFC107;
}

.score-display {
  margin-left: 10px;
  font-weight: bold;
  color: #333;
}

.grade-preview {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: bold;
}

.grade-badge {
  padding: 2px 8px;
  background: #EEE;
  border-radius: 4px;
}
.grade-badge.S { background: #E8F5E9; color: #2E7D32; }
.grade-badge.A { background: #E3F2FD; color: #1565C0; }
.grade-badge.B { background: #FFF3E0; color: #EF6C00; }
.grade-badge.C { background: #FFEBEE; color: #C62828; }

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #CCC;
  font-family: 'Times New Roman';
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.btn-red { background: #D1202F; color: white; }
.btn-grey { background: #EEE; color: #333; }

</style>