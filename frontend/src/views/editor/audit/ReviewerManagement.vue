<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const toastStore = useToastStore()
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
    toastStore.add({ message: 'Evaluation comment must be at least 30 characters.', type: 'warning' })
    return
  }
  
  currentReviewer.value.status = 'evaluated'
  currentReviewer.value.grade = calculatedGrade.value
  
  if (calculatedGrade.value === 'C') {
    toastStore.add({ message: `Warning: Reviewer ${currentReviewer.value.anon_id} graded C. System will restrict future invitations.`, type: 'warning' })
  }
  
  showEvalModal.value = false
}

const viewEvaluation = (reviewer) => {
  toastStore.add({ message: `Viewing evaluation history for ${reviewer.anon_id}...`, type: 'info' })
}

</script>

<template>
  <div class="jp-container">
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
      <table class="jp-table">
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
              <button class="btn-primary-sm" v-if="r.status === 'unevaluated'" @click="openEvaluation(r)">Evaluate</button>
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
          <button class="btn btn-primary" @click="submitEvaluation">Submit Evaluation</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.jp-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
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
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.warning-text {
  font-size: 14px;
  color: #d9534f;
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.filter-bar select {
  padding: 8px 16px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  min-width: 150px;
}

/* Table */
.jp-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.jp-table th {
  text-align: left;
  padding: 15px;
  background-color: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
  font-weight: 600;
  color: #495057;
}

.jp-table td {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}
.status-badge.unevaluated { background: #e3f2fd; color: #0d47a1; }
.status-badge.evaluated { background: #e8f5e9; color: #1b5e20; }
.status-badge.overdue_eval { background: #ffebee; color: #c62828; }

.btn-primary-sm {
  background: #0056B3;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
}
.btn-primary-sm:hover {
  background: #004494;
}

.btn-text {
  background: none;
  border: none;
  color: #0056B3;
  cursor: pointer;
  font-size: 12px;
  text-decoration: none;
}
.btn-text:hover {
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
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.rating-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.rating-item label {
  display: block;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 5px;
  color: #495057;
}

.stars {
  color: #dee2e6;
  font-size: 24px;
  cursor: pointer;
  display: inline-block;
}

.stars span.active {
  color: #ffc107;
}

.score-display {
  margin-left: 10px;
  font-weight: bold;
  color: #495057;
}

.grade-preview {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
}

.grade-badge {
  padding: 4px 12px;
  background: #e9ecef;
  border-radius: 4px;
  margin-left: 10px;
}
.grade-badge.S { background: #e8f5e9; color: #1b5e20; }
.grade-badge.A { background: #e3f2fd; color: #0d47a1; }
.grade-badge.B { background: #fff3e0; color: #e65100; }
.grade-badge.C { background: #ffebee; color: #c62828; }

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 8px 24px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-primary { 
  background: #0056B3; 
  color: white; 
}
.btn-primary:hover {
  background: #004494;
}
.btn-grey { 
  background: #e9ecef; 
  color: #495057; 
}
.btn-grey:hover {
  background: #dee2e6;
}

</style>