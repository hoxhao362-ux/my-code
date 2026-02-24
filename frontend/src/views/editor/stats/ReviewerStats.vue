<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// Mock Data Generators
const generateStats = () => {
  return {
    totalReviewers: 142,
    activeReviewers: 38,
    avgTurnaroundDays: 14.2,
    acceptanceRate: 68, // % of invitations accepted
    avgRating: 4.5, // out of 5
    
    // For Adoption Rate Chart
    adoption: {
      recommended: { total: 45, adopted: 32 },
      opposed: { total: 12, respected: 12 } // 100% respected
    },

    // For Turnaround Time Distribution
    turnaroundDist: [
      { label: '< 7 Days', value: 15, color: '#4CAF50' },
      { label: '7-14 Days', value: 45, color: '#2196F3' },
      { label: '15-21 Days', value: 25, color: '#FFC107' },
      { label: '> 21 Days', value: 15, color: '#F44336' }
    ]
  }
}

const stats = ref(generateStats())
const dateRange = ref('last_year')

const refreshStats = () => {
  // Simulate data fetch based on date range
  stats.value = generateStats()
  // Add some random variation
  stats.value.totalReviewers += Math.floor(Math.random() * 10)
}

// Helper for CSV Export
const exportReport = () => {
  const headers = ['Metric', 'Value']
  const rows = [
    ['Total Reviewers', stats.value.totalReviewers],
    ['Active Reviewers', stats.value.activeReviewers],
    ['Avg Turnaround (Days)', stats.value.avgTurnaroundDays],
    ['Invitation Acceptance Rate', stats.value.acceptanceRate + '%'],
    ['Recommended Adoption Rate', Math.round((stats.value.adoption.recommended.adopted / stats.value.adoption.recommended.total) * 100) + '%'],
    ['Opposed Respected Rate', Math.round((stats.value.adoption.opposed.respected / stats.value.adoption.opposed.total) * 100) + '%']
  ]

  let csvContent = "data:text/csv;charset=utf-8," 
    + headers.join(",") + "\n" 
    + rows.map(e => e.join(",")).join("\n")

  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `reviewer_stats_${dateRange.value}_${new Date().toISOString().split('T')[0]}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

</script>

<template>
  <div class="jp-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user" 
      current-page="editor-stats" 
      :toggle-directory="()=>{}" 
      :logout="userStore.logout" 
    />

    <main class="content">
      <div class="page-header">
        <h1 class="main-title">Reviewer Data Statistics & Reports</h1>
        <p class="subtitle">Comprehensive analysis of reviewer performance, turnaround times, and recommendation adherence.</p>
        
        <div class="controls">
          <select v-model="dateRange" @change="refreshStats" class="date-select">
            <option value="last_month">Last 30 Days</option>
            <option value="last_quarter">Last Quarter</option>
            <option value="last_year">Last Year</option>
            <option value="all_time">All Time</option>
          </select>
          
          <button class="btn btn-primary" @click="exportReport">
            <span class="icon">⬇</span> Export Report (CSV)
          </button>
        </div>
      </div>

      <!-- Key Metrics Grid -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value">{{ stats.totalReviewers }}</div>
          <div class="metric-label">Total Reviewers Database</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ stats.activeReviewers }}</div>
          <div class="metric-label">Active (Last 90 Days)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ stats.avgTurnaroundDays }} <span class="unit">days</span></div>
          <div class="metric-label">Avg. Turnaround Time</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ stats.acceptanceRate }}<span class="unit">%</span></div>
          <div class="metric-label">Invitation Acceptance Rate</div>
        </div>
      </div>

      <div class="charts-container">
        
        <!-- Author Recommendation Analysis -->
        <div class="chart-card">
          <h3 class="chart-title">Author Recommendation Analysis</h3>
          <div class="chart-content">
            <!-- Recommended Reviewers Adoption -->
            <div class="bar-group">
              <div class="bar-label-row">
                <span>Recommended Reviewers Adopted</span>
                <span class="bold">{{ stats.adoption.recommended.adopted }} / {{ stats.adoption.recommended.total }} ({{ Math.round((stats.adoption.recommended.adopted / stats.adoption.recommended.total) * 100) }}%)</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill green" :style="{ width: (stats.adoption.recommended.adopted / stats.adoption.recommended.total * 100) + '%' }"></div>
              </div>
              <p class="chart-hint">Percentage of writer-recommended reviewers invited by editors.</p>
            </div>

            <!-- Opposed Reviewers Respected -->
            <div class="bar-group">
              <div class="bar-label-row">
                <span>Opposed Reviewers Respected</span>
                <span class="bold">{{ stats.adoption.opposed.respected }} / {{ stats.adoption.opposed.total }} ({{ Math.round((stats.adoption.opposed.respected / stats.adoption.opposed.total) * 100) }}%)</span>
              </div>
              <div class="progress-bg">
                <div class="progress-fill blue" :style="{ width: (stats.adoption.opposed.respected / stats.adoption.opposed.total * 100) + '%' }"></div>
              </div>
              <p class="chart-hint">Percentage of writer-opposed reviewers successfully excluded.</p>
            </div>
          </div>
        </div>

        <!-- Turnaround Time Distribution -->
        <div class="chart-card">
          <h3 class="chart-title">Review Turnaround Time Distribution</h3>
          <div class="chart-content vertical-chart">
            <div v-for="(item, index) in stats.turnaroundDist" :key="index" class="v-bar-item">
              <div class="v-bar-track">
                <div class="v-bar-fill" :style="{ height: item.value + '%', backgroundColor: item.color }">
                  <span class="v-bar-val">{{ item.value }}%</span>
                </div>
              </div>
              <div class="v-bar-label">{{ item.label }}</div>
            </div>
          </div>
        </div>

      </div>

      <!-- Detailed Table -->
      <div class="detail-section">
        <h3 class="section-title">Top Performing Reviewers</h3>
        <table class="jp-table">
          <thead>
            <tr>
              <th>Reviewer Name</th>
              <th>Affiliation</th>
              <th>Reviews Completed</th>
              <th>Avg Days</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Dr. Sarah Jenkins</td>
              <td>University of Oxford</td>
              <td>12</td>
              <td>8.5</td>
              <td>★★★★★</td>
            </tr>
             <tr>
              <td>Prof. Michael Chang</td>
              <td>Stanford Medicine</td>
              <td>9</td>
              <td>11.2</td>
              <td>★★★★☆</td>
            </tr>
             <tr>
              <td>Dr. Emily White</td>
              <td>Johns Hopkins</td>
              <td>7</td>
              <td>14.0</td>
              <td>★★★★☆</td>
            </tr>
             <tr>
              <td>Dr. Robert Chen</td>
              <td>Tsinghua University</td>
              <td>15</td>
              <td>6.8</td>
              <td>★★★★★</td>
            </tr>
          </tbody>
        </table>
      </div>

    </main>
  </div>
</template>

<style scoped>
.jp-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f6f8;
  min-height: 100vh;
  color: #333;
}

.content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.date-select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
}

.btn-primary {
  background: #0056b3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.btn-primary:hover {
  background: #004494;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  text-align: center;
  border-top: 4px solid #0056B3; /* Journal Blue */
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.unit {
  font-size: 14px;
  color: #888;
  font-weight: normal;
  margin-left: 4px;
}

.metric-label {
  font-size: 13px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Charts Area */
.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

/* Horizontal Bar Chart */
.bar-group {
  margin-bottom: 25px;
}

.bar-label-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.bold { font-weight: bold; }

.progress-bg {
  height: 24px;
  background: #e9ecef;
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  display: flex;
  align-items: center;
  padding-left: 10px;
  color: white;
  font-size: 12px;
  transition: width 0.5s ease;
}

.progress-fill.green { background: #28a745; }
.progress-fill.blue { background: #007bff; }

.chart-hint {
  font-size: 12px;
  color: #888;
  margin-top: 5px;
  font-style: italic;
}

/* Vertical Bar Chart */
.vertical-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding-top: 20px;
}

.v-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 15%;
}

.v-bar-track {
  flex: 1;
  width: 100%;
  background: #f8f9fa;
  border-radius: 4px;
  position: relative;
  display: flex;
  align-items: flex-end;
}

.v-bar-fill {
  width: 100%;
  border-radius: 4px;
  position: relative;
  transition: height 0.5s ease;
}

.v-bar-val {
  position: absolute;
  top: -20px;
  width: 100%;
  text-align: center;
  font-size: 12px;
  font-weight: bold;
  color: #333;
}

.v-bar-label {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* Table Section */
.detail-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.jp-table {
  width: 100%;
  border-collapse: collapse;
}

.jp-table th {
  text-align: left;
  padding: 12px;
  background: #f8f9fa;
  border-bottom: 2px solid #ddd;
  font-weight: bold;
  color: #555;
}

.jp-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.jp-table tr:last-child td {
  border-bottom: none;
}
</style>