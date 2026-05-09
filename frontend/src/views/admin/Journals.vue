<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

// TODO: 后端暂未实现栏目/期号管理接口，当前使用本地 Mock 数据
// 待后端实现后需替换为真实 API 调用：
// - GET /admin/columns - 获取栏目列表
// - POST /admin/columns - 创建栏目
// - PUT /admin/columns/{id} - 更新栏目
// - GET /admin/issues - 获取期号列表
// - POST /admin/issues - 创建期号
// - PUT /admin/issues/{id}/publish - 发布期号

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
  <div class="jp-container">
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
          <button class="btn btn-primary" @click="handleAddColumn">Add Column</button>
          <button class="btn btn-primary" @click="handleCreateIssue">Create Issue</button>
        </div>
      </div>

      <!-- Column Management Section -->
      <section class="management-section">
        <div class="section-header">
          <h2>Column Management</h2>
        </div>
        <table class="jp-table">
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
        <table class="jp-table">
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
                <button class="btn-text danger" v-if="issue.status === 'pending_publish'" @click="handlePublish(issue)">Publish</button>
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
          <button class="btn btn-primary" @click="saveColumn">Save</button>
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
          <button class="btn btn-primary" @click="saveIssue">Create</button>
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
  position: relative;
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
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  border-left: 4px solid #0056B3;
  padding-left: 12px;
  margin-bottom: 20px;
}

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

.hover-row:hover td {
  background-color: #f8f9fa;
}

/* Cells */
.dual-text {
  display: flex;
  flex-direction: column;
}

.dual-text .cn { font-weight: 600; font-size: 14px; color: #333; }
.dual-text .en { font-size: 12px; color: #6c757d; font-style: italic; }

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 5px;
}
.status-dot.enabled { background-color: #28a745; }
.status-dot.disabled { background-color: #ced4da; }

.status-badge {
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}
.status-badge.published { background: #e8f5e9; border-color: #28a745; color: #28a745; }
.status-badge.pending_publish { background: #fff3e0; border-color: #fd7e14; color: #fd7e14; }
.status-badge.archived { background: #f8f9fa; color: #6c757d; }

/* Buttons */
.btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
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

.btn-text {
  background: none;
  border: none;
  color: #0056B3;
  cursor: pointer;
  font-size: 14px;
  margin-right: 15px;
  text-decoration: none;
  padding: 0;
}
.btn-text:hover { 
  text-decoration: underline; 
}
.btn-text.danger { 
  color: #dc3545; 
}

/* Footer */
.preview-footer {
  margin-top: 40px;
  text-align: center;
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

.audit-note {
  font-size: 13px;
  color: #6c757d;
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
.form-group input { width: 100%; padding: 8px; border: 1px solid #CCC; font-family: inherit; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

</style>