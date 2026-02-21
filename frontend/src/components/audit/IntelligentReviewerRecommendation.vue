<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['select', 'close'])

const userStore = useUserStore()
const loading = ref(true)
const recommendations = ref([])

// Mock "Smart" Algorithm
const generateRecommendations = () => {
  loading.value = true
  
  // Simulate API delay
  setTimeout(() => {
    const allReviewers = userStore.users.filter(u => u.role === 'reviewer')
    
    // Mock Matching Logic
    recommendations.value = allReviewers.map(reviewer => {
      // 1. Calculate Match Score (Mock based on ID to be deterministic but varied)
      // Base score 60 + random 0-40
      const matchScore = Math.floor(60 + Math.random() * 39)
      
      // 2. Mock Matching Keywords
      const allKeywords = ['Machine Learning', 'Clinical Trials', 'Epidemiology', 'Genetics', 'Public Health', 'Immunology']
      // Pick 2-3 random keywords
      const matchedKeywords = allKeywords.sort(() => 0.5 - Math.random()).slice(0, Math.floor(Math.random() * 2) + 2)
      
      // 3. Mock Workload (Active Tasks)
      const activeTasks = Math.floor(Math.random() * 5) // 0-4
      
      // 4. Mock Previous Stats
      const avgTurnaround = Math.floor(10 + Math.random() * 20) // 10-30 days
      const acceptanceRate = Math.floor(20 + Math.random() * 60) // 20-80%
      
      // 5. Calculate Recommendation Index (Weighted Score)
      // Higher match is better, lower workload is better
      const recommendationIndex = matchScore - (activeTasks * 5)
      
      return {
        ...reviewer,
        matchScore,
        matchedKeywords,
        activeTasks,
        avgTurnaround,
        acceptanceRate,
        recommendationIndex
      }
    })
    // Filter out low scores and sort by Index
    .filter(r => r.matchScore > 65)
    .sort((a, b) => b.recommendationIndex - a.recommendationIndex)
    .slice(0, 5) // Top 5
    
    loading.value = false
  }, 1500)
}

onMounted(() => {
  generateRecommendations()
})

const handleSelect = (reviewer) => {
  emit('select', reviewer)
}

const getScoreColor = (score) => {
  if (score >= 90) return '#4caf50' // Green
  if (score >= 80) return '#2196f3' // Blue
  if (score >= 70) return '#ff9800' // Orange
  return '#9e9e9e' // Grey
}

const getWorkloadClass = (tasks) => {
  if (tasks >= 3) return 'workload-high'
  if (tasks >= 1) return 'workload-medium'
  return 'workload-low'
}

</script>

<template>
  <div class="smart-recommendation-container">
    <div class="header">
      <h3>
        <span class="icon">🤖</span> 
        System Intelligent Recommendation
      </h3>
      <p class="desc">
        Based on manuscript title <strong>"{{ manuscript.title }}"</strong> and content analysis.
      </p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Analyzing manuscript content...</p>
      <p class="sub-text">Matching against 12,000+ reviewer profiles</p>
    </div>

    <div v-else class="recommendation-list">
      <div 
        v-for="(reviewer, index) in recommendations" 
        :key="reviewer.id" 
        class="recommendation-card"
        :class="{ 'top-pick': index === 0 }"
      >
        <div class="card-left">
          <div class="match-badge" :style="{ borderColor: getScoreColor(reviewer.matchScore), color: getScoreColor(reviewer.matchScore) }">
            {{ reviewer.matchScore }}% Match
          </div>
          <div class="rank">#{{ index + 1 }}</div>
        </div>
        
        <div class="card-main">
          <div class="reviewer-header">
            <h4>{{ reviewer.fullName }}</h4>
            <span class="affiliation">{{ reviewer.email }}</span>
          </div>
          
          <div class="keywords">
            <span v-for="kw in reviewer.matchedKeywords" :key="kw" class="keyword-tag">
              {{ kw }}
            </span>
          </div>
          
          <div class="stats-row">
            <div class="stat-item" :class="getWorkloadClass(reviewer.activeTasks)">
              <span class="label">Current Load:</span>
              <span class="value">{{ reviewer.activeTasks }} active</span>
              <span v-if="reviewer.activeTasks >= 3" class="warning-icon" title="High Workload">⚠️</span>
            </div>
            <div class="stat-item">
              <span class="label">Avg Turnaround:</span>
              <span class="value">{{ reviewer.avgTurnaround }} days</span>
            </div>
          </div>
        </div>
        
        <div class="card-actions">
          <button class="btn-select" @click="handleSelect(reviewer)">
            Select
          </button>
        </div>
      </div>
      
      <div v-if="recommendations.length === 0" class="no-results">
        No high-confidence matches found. Please try manual search.
      </div>
    </div>
  </div>
</template>

<style scoped>
.smart-recommendation-container {
  background: #f8f9fa;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.header {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header .icon {
  font-size: 1.5rem;
}

.desc {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.sub-text {
  font-size: 0.85rem;
  color: #999;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* List */
.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s;
}

.recommendation-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-color: #b3d4fc;
}

.recommendation-card.top-pick {
  border: 1px solid #ffd700;
  background: #fffdf5;
}

.card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  gap: 5px;
}

.match-badge {
  font-weight: bold;
  font-size: 0.9rem;
  border: 2px solid;
  padding: 4px 8px;
  border-radius: 20px;
  background: white;
}

.rank {
  font-size: 0.8rem;
  color: #999;
}

.card-main {
  flex: 1;
}

.reviewer-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 0.5rem;
}

.reviewer-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.affiliation {
  color: #666;
  font-size: 0.9rem;
}

.keywords {
  display: flex;
  gap: 6px;
  margin-bottom: 0.8rem;
  flex-wrap: wrap;
}

.keyword-tag {
  background: #f0f2f5;
  color: #555;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.stats-row {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.label {
  color: #888;
}

.value {
  font-weight: 500;
  color: #333;
}

/* Workload Colors */
.workload-low .value { color: #4caf50; }
.workload-medium .value { color: #ff9800; }
.workload-high .value { color: #f44336; }

.warning-icon {
  font-size: 0.9rem;
  cursor: help;
}

.card-actions {
  min-width: 100px;
  text-align: right;
}

.btn-select {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-select:hover {
  background: #2980b9;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-style: italic;
}
</style>
