<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { adminApi } from '../../utils/api'
import Navigation from '../../components/Navigation.vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Pie } from 'vue-chartjs'
import { useI18n } from 'vue-i18n'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const { t } = useI18n()
const userStore = useUserStore()
const user = ref(userStore.user)
const loading = ref(true)

// Data refs
const trendData = ref({ labels: [], datasets: [] })
const moduleData = ref({ labels: [], datasets: [] })
const statusData = ref({ labels: [], datasets: [] })

// Chart options
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}))

const loadData = async () => {
  loading.value = true
  try {
    const [trend, modules, status] = await Promise.all([
      adminApi.getSubmissionTrend(),
      adminApi.getModuleDistribution(),
      adminApi.getJournalStatusStats()
    ])

    // Process Trend Data
    trendData.value = {
      labels: trend.map(item => item.date),
      datasets: [{
        label: t('dashboard.stats.recentSubmissions'),
        backgroundColor: '#3498db',
        borderColor: '#3498db',
        data: trend.map(item => item.count),
        fill: false,
        tension: 0.1
      }]
    }

    // Process Module Data
    moduleData.value = {
      labels: modules.map(item => item.name),
      datasets: [{
        backgroundColor: ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22', '#1abc9c'],
        data: modules.map(item => item.value)
      }]
    }

    // Process Status Data
    statusData.value = {
      labels: [
        t('status.pending_initial_review'), 
        t('status.under_review'), 
        t('status.accepted'), 
        t('status.rejected'), 
        t('status.published')
      ],
      datasets: [{
        label: t('common.status'),
        backgroundColor: ['#f39c12', '#3498db', '#2ecc71', '#e74c3c', '#9b59b6'],
        data: [
          status.pending,
          status.underReview,
          status.accepted,
          status.rejected,
          status.published
        ]
      }]
    }

  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="statistics-container">
    <Navigation 
      :user="user"
      :current-page="'admin-statistics'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <main class="content">
      <div class="header">
        <h1>{{ $t('nav.dataStatistics') }}</h1>
        <button class="btn-refresh" @click="loadData" :disabled="loading">
          {{ loading ? $t('common.loading') : $t('common.reset') }}
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="charts-grid">
        <!-- Submission Trend -->
        <div class="chart-card wide">
          <h3>{{ $t('dashboard.stats.recentSubmissions') }} (Trend)</h3>
          <div class="chart-wrapper">
            <Line :data="trendData" :options="chartOptions" />
          </div>
        </div>

        <!-- Module Distribution -->
        <div class="chart-card">
          <h3>{{ $t('common.module') }} Distribution</h3>
          <div class="chart-wrapper">
            <Pie :data="moduleData" :options="chartOptions" />
          </div>
        </div>

        <!-- Status Stats -->
        <div class="chart-card">
          <h3>{{ $t('common.status') }} Statistics</h3>
          <div class="chart-wrapper">
            <Bar :data="statusData" :options="chartOptions" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.statistics-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.content {
  flex: 1;
  max-width: 1400px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
}

.btn-refresh {
  padding: 0.5rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-refresh:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.chart-card h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  text-align: center;
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .content {
    margin-top: 70px;
    padding: 1rem;
  }
}
</style>
