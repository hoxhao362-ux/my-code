<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// State
const activeTab = ref('columns') // 'columns' or 'issues'
const showColumnModal = ref(false)
const showIssueModal = ref(false)

// Mock Data - Columns
const columns = ref([
  { id: 1, name_zh: '临床研究', name_en: 'Clinical Research', status: 'enabled', range: 'All Clinical Fields', words: '3000-5000', cycle: '4 weeks', order: 1 },
  { id: 2, name_zh: '公共卫生', name_en: 'Public Health', status: 'enabled', range: 'Epidemiology, Policy', words: '4000-6000', cycle: '5 weeks', order: 2 },
  { id: 3, name_zh: '全球健康', name_en: 'Global Health', status: 'disabled', range: 'Global Disease Burden', words: '5000+', cycle: '6 weeks', order: 3 }
])

// Mock Data - Issues
const issues = ref([
  { id: 202602, volume: 38, issue: 2, plan_date: '2026-02-15', actual_date: '-', status: 'pending_publish', columns: 'Clinical, Public Health', count: 12 },
  { id: 202601, volume: 38, issue: 1, plan_date: '2026-01-15', actual_date: '2026-01-15', status: 'published', columns: 'Clinical, Oncology', count: 15 },
  { id: 202512, volume: 37, issue: 12, plan_date: '2025-12-15', actual_date: '2025-12-16', status: 'archived', columns: 'All', count: 14 }
])

// Forms
const columnForm = ref({ name_zh: '', name_en: '', range: '', words: '', oa: false, cycle: '', desc: '' })
const issueForm = ref({ date: '', columns: [] })

// Actions
const handleAddColumn = () => {
  columnForm.value = { name_zh: '', name_en: '', range: '', words: '', oa: false, cycle: '', desc: '' }
  showColumnModal.value = true
}

const handleCreateIssue = () => {
  // Auto-calc next volume/issue logic (Mock)
  const lastIssue = issues.value[0]
  const nextIssueNum = lastIssue.issue + 1
  issueForm.value = { date: '', columns: [], volume: lastIssue.volume, issue: nextIssueNum }
  showIssueModal.value = true
}

const saveColumn = () => {
  columns.value.push({
    id: Date.now(),
    name_zh: columnForm.value.name_zh,
    name_en: columnForm.value.name_en,
    status: 'enabled',
    range: columnForm.value.range,
    words: columnForm.value.words,
    cycle: columnForm.value.cycle,
    order: columns.value.length + 1
  })
  showColumnModal.value = false
}

const saveIssue = () => {
  issues.value.unshift({
    id: Date.now(),
    volume: issueForm.value.volume,
    issue: issueForm.value.issue,
    plan_date: issueForm.value.date,
    actual_date: '-',
    status: 'pending_layout',
    columns: 'Selected',
    count: 0
  })
  showIssueModal.value = false
}

const toggleStatus = (col) => {
  col.status = col.status === 'enabled' ? 'disabled' : 'enabled'
}

const handlePublish = (issue) => {
  if (confirm(`Confirm publish Volume ${issue.volume} Issue ${issue.issue}? This cannot be undone.`)) {
    issue.status = 'published'
    issue.actual_date = new Date().toISOString().split('T')[0]
  }
}

</script>

<template>
  <div class="lancet-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user"
      current-page="editor-journals"
      :toggle-directory="()=>{}"
      :logout="userStore.logout"
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Journal Column & Issue Management</h1>
        <p class="warning-text">Columns and Issues are core configurations. Modifications require Editor-in-Chief approval. Do not delete arbitrarily.</p>
        <div class="header-actions">
          <button class="btn btn-red" @click="handleAddColumn">Add Column</button>
          <button class="btn btn-red" @click="handleCreateIssue">Create Issue</button>
        </div>
      </div>

      <!-- Column Management Section -->
      <section class="management-section">
        <div class="section-header">
          <h2>Column Management</h2>
        </div>
        <table class="lancet-table">
          <thead>
            <tr>
              <th style="width: 50px">Order</th>
              <th>Column Name (CN/EN)</th>
              <th>Status</th>
              <th>Scope</th>
              <th>Word Limit</th>
              <th>Review Cycle</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="col in columns" :key="col.id" class="hover-row">
              <td class="center-text">{{ col.order }}</td>
              <td>
                <div class="dual-text">
                  <span class="cn">{{ col.name_zh }}</span>
                  <span class="en">{{ col.name_en }}</span>
                </div>
              </td>
              <td>
                <span class="status-dot" :class="col.status"></span>
                {{ col.status === 'enabled' ? 'Active' : 'Disabled' }}
              </td>
              <td>{{ col.range }}</td>
              <td>{{ col.words }}</td>
              <td>{{ col.cycle }}</td>
              <td class="actions">
                <button class="btn-text">Edit</button>
                <button class="btn-text" @click="toggleStatus(col)">{{ col.status === 'enabled' ? 'Disable' : 'Enable' }}</button>
                <button class="btn-text">Sort</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Issue Scheduling Section -->
      <section class="management-section" style="margin-top: 40px;">
        <div class="section-header">
          <h2>Issue Scheduling</h2>
        </div>
        <table class="lancet-table">
          <thead>
            <tr>
              <th>Vol / Issue</th>
              <th>Plan Date</th>
              <th>Actual Date</th>
              <th>Status</th>
              <th>Columns</th>
              <th>Manuscripts</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="issue in issues" :key="issue.id" class="hover-row">
              <td class="bold-text">Vol {{ issue.volume }}, No {{ issue.issue }}</td>
              <td>{{ issue.plan_date }}</td>
              <td>{{ issue.actual_date }}</td>
              <td>
                <span class="status-badge" :class="issue.status">{{ issue.status.replace('_', ' ') }}</span>
              </td>
              <td>{{ issue.columns }}</td>
              <td>{{ issue.count }}</td>
              <td class="actions">
                <button class="btn-text" :disabled="issue.status === 'published' || issue.status === 'archived'">Assign</button>
                <button class="btn-text red" v-if="issue.status === 'pending_publish'" @click="handlePublish(issue)">Publish</button>
                <button class="btn-text">Details</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Public Preview Footer -->
      <div class="preview-footer">
        <button class="btn btn-grey">Public Preview</button>
        <p class="audit-note">All column and issue changes are automatically archived in the journal audit log.</p>
      </div>

    </main>

    <!-- Modals (Simplified for Text-Only Requirement) -->
    <div v-if="showColumnModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Add New Column</h3>
        <div class="form-group">
          <label>Chinese Name</label>
          <input v-model="columnForm.name_zh" placeholder="e.g. 临床研究">
        </div>
        <div class="form-group">
          <label>English Name</label>
          <input v-model="columnForm.name_en" placeholder="e.g. Clinical Research">
        </div>
        <div class="form-group">
          <label>Research Scope</label>
          <input v-model="columnForm.range">
        </div>
        <div class="form-group">
          <label>Word Limit</label>
          <input v-model="columnForm.words">
        </div>
        <div class="form-group">
          <label>Review Cycle</label>
          <input v-model="columnForm.cycle">
        </div>
        <div class="modal-actions">
          <button class="btn btn-grey" @click="showColumnModal = false">Cancel</button>
          <button class="btn btn-red" @click="saveColumn">Save</button>
        </div>
      </div>
    </div>

    <div v-if="showIssueModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Create New Issue</h3>
        <p>Vol {{ issueForm.volume }}, Issue {{ issueForm.issue }} (Auto-assigned)</p>
        <div class="form-group">
          <label>Plan Publish Date</label>
          <input type="date" v-model="issueForm.date">
        </div>
        <div class="modal-actions">
          <button class="btn btn-grey" @click="showIssueModal = false">Cancel</button>
          <button class="btn btn-red" @click="saveIssue">Create</button>
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
  position: relative;
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

.header-actions {
  position: absolute;
  right: 0;
  top: 0;
  display: flex;
  gap: 10px;
}

/* Tables */
.management-section {
  margin-bottom: 30px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  border-left: 3px solid #D1202F;
  padding-left: 10px;
  margin-bottom: 15px;
}

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

.hover-row:hover td {
  background-color: #F9F9F9;
}

/* Cells */
.dual-text {
  display: flex;
  flex-direction: column;
}

.dual-text .cn { font-weight: bold; font-size: 14px; }
.dual-text .en { font-size: 12px; color: #777; font-style: italic; }

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 5px;
}
.status-dot.enabled { background-color: #2E7D32; }
.status-dot.disabled { background-color: #CCC; }

.status-badge {
  padding: 2px 6px;
  font-size: 11px;
  border: 1px solid #CCC;
  border-radius: 4px;
  text-transform: uppercase;
}
.status-badge.published { background: #E8F5E9; border-color: #2E7D32; color: #2E7D32; }
.status-badge.pending_publish { background: #FFF3E0; border-color: #EF6C00; color: #EF6C00; }
.status-badge.archived { background: #F5F5F5; color: #757575; }

/* Buttons */
.btn {
  padding: 6px 16px;
  border-radius: 4px;
  border: none;
  font-family: Arial, sans-serif;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
}

.btn-red { background: #D1202F; color: white; }
.btn-red:hover { background: #B71C2B; }
.btn-grey { background: #EEE; color: #333; }
.btn-grey:hover { background: #E0E0E0; }

.btn-text {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 12px;
  margin-right: 10px;
}
.btn-text:hover { color: #333; text-decoration: underline; }
.btn-text.red { color: #D1202F; }

/* Footer */
.preview-footer {
  margin-top: 40px;
  text-align: center;
  border-top: 1px solid #EEE;
  padding-top: 20px;
}

.audit-note {
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-box {
  background: white;
  padding: 30px;
  border-radius: 4px;
  width: 500px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.modal-box h3 { margin-top: 0; margin-bottom: 20px; color: #333; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 12px; color: #555; margin-bottom: 5px; font-weight: bold; }
.form-group input { width: 100%; padding: 8px; border: 1px solid #CCC; font-family: 'Times New Roman'; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

</style>