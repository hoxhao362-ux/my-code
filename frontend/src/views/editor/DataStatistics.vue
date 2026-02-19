<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// Filters
const timeRange = ref('week')
const selectedColumn = ref('all')
const selectedStatus = ref('all')

const columns = ['Clinical', 'Global Health', 'Public Health', 'Oncology'] // Mock columns

// Mock Data
const manuscriptStats = ref({
  total: 124,
  pending_initial: 15,
  initial_passed: 109,
  under_review: 42,
  pending_final: 8,
  accepted: 24,
  published: 20,
  rejected: 35,
  revision_rate: '35%',
  avg_initial_days: 2.5,
  avg_review_days: 14.2
})

const reviewStats = ref({
  active_reviewers: 56,
  total_tasks: 89,
  completion_rate: '92%',
  avg_time: '12.5 days',
  overdue: 3,
  quality_pass_rate: '98%',
  adoption_rate: '85%'
})

const pubStats = ref({
  annual_count: 120,
  oa_rate: '45%',
  issue_completion: '100%'
})

const reports = ref([
  { id: 101, name: 'Journal_Weekly_Report_2026_W06.pdf', period: '2026-02-02 ~ 2026-02-08', created_at: '2026-02-09 09:00', creator: 'Editor Admin', status: 'generated' },
  { id: 102, name: 'Journal_Monthly_Report_2026_01.pdf', period: '2026-01-01 ~ 2026-01-31', created_at: '2026-02-01 10:00', creator: 'Editor Chief', status: 'exported' },
  { id: 103, name: 'Reviewer_Performance_2025_Q4.xlsx', period: '2025-10-01 ~ 2025-12-31', created_at: '2026-01-15 14:30', creator: 'Editor Admin', status: 'archived' }
])

const handleQuery = () => {
  // Mock query simulation
  console.log('Querying data...', { time: timeRange.value, col: selectedColumn.value, status: selectedStatus.value })
  // In real app, fetch data here
}

const handleExportReport = () => {
  alert('Generating report... (Mock)')
}

const handleDownloadReport = (report) => {
  alert(`Downloading ${report.name}...`)
}

const handleArchiveReport = (report) => {
  report.status = 'archived'
}

</script>

<template>
  <div class="lancet-container">
    <!-- Note: Embedded prop usually handles nav, but for standalone dev we might keep it or rely on Portal -->
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user"
      current-page="editor-data-statistics"
      :toggle-directory="()=>{}"
      :logout="userStore.logout"
    />

    <main class="content">
      <!-- Top Header & Filter -->
      <div class="page-header">
        <h1 class="main-title">Journal Data Statistics & Reports</h1>
        <p class="sub-caption">Data updated in real-time. Reports generated automatically for management and audit.</p>
        
        <div class="filter-bar">
          <div class="filter-group">
            <label>Time Range:</label>
            <select v-model="timeRange">
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Column:</label>
            <select v-model="selectedColumn">
              <option value="all">All Columns</option>
              <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Status:</label>
            <select v-model="selectedStatus">
              <option value="all">All Status</option>
              <option value="pending">Pending Initial</option>
              <option value="review">Under Review</option>
              <option value="final">Final Decision</option>
              <option value="published">Published</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div class="action-group">
            <button class="btn btn-grey" @click="handleQuery">Query</button>
            <button class="btn btn-red" @click="handleExportReport">Export Report</button>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="stats-container">
        <!-- Module 1: Manuscript Stats -->
        <section class="stats-card">
          <div class="card-header">
            <h2>Manuscript Statistics</h2>
          </div>
          <div class="card-body">
            <div class="stat-grid">
              <div class="stat-item">
                <span class="label">Total Submissions</span>
                <span class="value">{{ manuscriptStats.total }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Pending Initial</span>
                <span class="value">{{ manuscriptStats.pending_initial }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Under Review</span>
                <span class="value">{{ manuscriptStats.under_review }}</span>
              </div>
              <div class="stat-item highlight-red">
                <span class="label">Accepted</span>
                <span class="value">{{ manuscriptStats.accepted }}</span>
              </div>
               <div class="stat-item highlight-red">
                <span class="label">Published</span>
                <span class="value">{{ manuscriptStats.published }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Rejected</span>
                <span class="value">{{ manuscriptStats.rejected }}</span>
              </div>
              <div class="stat-item full-width">
                <span class="label">Avg Initial Review</span>
                <span class="value">{{ manuscriptStats.avg_initial_days }} days</span>
              </div>
               <div class="stat-item full-width">
                <span class="label">Avg Peer Review</span>
                <span class="value">{{ manuscriptStats.avg_review_days }} days</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Module 2: Review Statistics -->
        <section class="stats-card">
          <div class="card-header">
            <h2>Review Statistics</h2>
          </div>
          <div class="card-body">
            <div class="stat-grid">
              <div class="stat-item">
                <span class="label">Active Reviewers</span>
                <span class="value">{{ reviewStats.active_reviewers }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Total Tasks</span>
                <span class="value">{{ reviewStats.total_tasks }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Completion Rate</span>
                <span class="value">{{ reviewStats.completion_rate }}</span>
              </div>
               <div class="stat-item">
                <span class="label">Avg Time</span>
                <span class="value">{{ reviewStats.avg_time }}</span>
              </div>
              <div class="stat-item highlight-orange">
                <span class="label">Overdue</span>
                <span class="value">{{ reviewStats.overdue }}</span>
              </div>
              <div class="stat-item">
                <span class="label">Quality Pass</span>
                <span class="value">{{ reviewStats.quality_pass_rate }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Module 3: Publication Stats -->
        <section class="stats-card">
          <div class="card-header">
            <h2>Publication & Column</h2>
          </div>
          <div class="card-body">
            <div class="stat-grid">
              <div class="stat-item full-width">
                <span class="label">Annual Publications</span>
                <span class="value">{{ pubStats.annual_count }}</span>
              </div>
              <div class="stat-item full-width">
                <span class="label">OA Rate</span>
                <span class="value">{{ pubStats.oa_rate }}</span>
              </div>
              <div class="stat-item full-width">
                <span class="label">Issue Completion</span>
                <span class="value">{{ pubStats.issue_completion }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Report Management -->
      <div class="reports-section">
        <h2 class="section-title">Report Management</h2>
        <div class="table-wrapper">
          <table class="lancet-table">
            <thead>
              <tr>
                <th>Report Name</th>
                <th>Period</th>
                <th>Created At</th>
                <th>Creator</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reports" :key="report.id">
                <td class="col-name">{{ report.name }}</td>
                <td>{{ report.period }}</td>
                <td>{{ report.created_at }}</td>
                <td>{{ report.creator }}</td>
                <td>
                  <span class="status-badge" :class="report.status">{{ report.status }}</span>
                </td>
                <td class="actions">
                  <button class="btn-text" @click="handleDownloadReport(report)">View</button>
                  <button class="btn-text red" @click="handleDownloadReport(report)">Export</button>
                  <button class="btn-text" @click="handleArchiveReport(report)" :disabled="report.status === 'archived'">Archive</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* Lancet Standard Typography & Colors */
.lancet-container {
  font-family: 'Times New Roman', Times, serif;
  background-color: #FFFFFF;
  min-height: 100vh;
  color: #333333;
}

.content {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 1px solid #EEEEEE;
  padding-bottom: 20px;
}

.main-title {
  font-size: 24px;
  font-weight: bold;
  color: #333333;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sub-caption {
  font-size: 12px;
  color: #666666;
  margin-bottom: 20px;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: center;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.filter-group label {
  font-weight: bold;
  color: #555;
}

.filter-group select {
  padding: 6px 12px;
  border: 1px solid #CCCCCC;
  border-radius: 0; /* Minimalist */
  font-family: 'Times New Roman', serif;
  color: #333;
  min-width: 120px;
}

/* Buttons */
.btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  font-family: Arial, sans-serif; /* Buttons often Sans for readability */
  font-weight: bold;
  font-size: 13px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.9;
}

.btn-red {
  background-color: #D1202F; /* Lancet Red */
  color: white;
}

.btn-grey {
  background-color: #EEEEEE;
  color: #333333;
}

/* Stats Cards */
.stats-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stats-card {
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  background: white;
  padding: 0;
  overflow: hidden;
}

.card-header {
  background: #F9F9F9;
  padding: 15px 20px;
  border-bottom: 1px solid #E0E0E0;
}

.card-header h2 {
  font-size: 16px;
  margin: 0;
  color: #333;
  font-weight: bold;
}

.card-body {
  padding: 20px;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item.full-width {
  grid-column: span 2;
}

.stat-item .label {
  font-size: 12px;
  color: #777;
  margin-bottom: 4px;
}

.stat-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.highlight-red .value {
  color: #D1202F;
}

.highlight-orange .value {
  color: #E67E22;
}

/* Reports Table */
.reports-section {
  border-top: 1px solid #EEE;
  padding-top: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.table-wrapper {
  overflow-x: auto;
}

.lancet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.lancet-table th {
  text-align: left;
  padding: 12px 15px;
  border-bottom: 2px solid #333;
  font-weight: bold;
  color: #333;
}

.lancet-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #EEE;
  color: #555;
}

.lancet-table tr:hover td {
  background-color: #F9F9F9;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  text-transform: uppercase;
}

.status-badge.generated { background: #E8F5E9; color: #2E7D32; }
.status-badge.exported { background: #E3F2FD; color: #1565C0; }
.status-badge.archived { background: #F5F5F5; color: #757575; }

.actions {
  display: flex;
  gap: 15px;
}

.btn-text {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
  text-decoration: none;
}

.btn-text:hover {
  text-decoration: underline;
}

.btn-text.red {
  color: #D1202F;
  font-weight: bold;
}

.btn-text:disabled {
  color: #CCC;
  cursor: not-allowed;
  text-decoration: none;
}

@media (max-width: 1024px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
}
</style>