<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  writerName: {
    type: String,
    required: true
  },
  writerAffiliation: {
    type: String,
    default: ''
  },
  reviewer: {
    type: Object,
    required: true
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const checking = ref(false)
const riskLevel = ref('low') // low, medium, high
const issues = ref([])

// Mock COI Database
const mockPaperDatabase = [
  { title: "Study on X", writers: ["Zhang San", "Li Si", "Wang Wu"], year: 2024 },
  { title: "Research on Y", writers: ["Li Si", "Zhao Liu"], year: 2023 },
  { title: "Analysis of Z", writers: ["Chen Yi", "Lin Er"], year: 2025 }
]

// Mock Integrity Database (Blacklist)
const integrityBlacklist = [
  { name: 'Bad Actor', reason: 'Falsified Data (2022)' },
  { name: 'Fake Reviewer', reason: 'Identity Fraud' },
  { name: 'Plagiarist One', reason: 'Multiple Retractions' }
]

const checkCOI = () => {
  checking.value = true
  issues.value = []
  riskLevel.value = 'low'

  // Simulate API delay
  setTimeout(() => {
    // 0. Integrity Database Check (Priority)
    const integrityIssue = integrityBlacklist.find(b => 
      props.reviewer.username?.toLowerCase().includes(b.name.toLowerCase()) || 
      props.reviewer.name?.toLowerCase().includes(b.name.toLowerCase()) ||
      (props.reviewer.name && props.reviewer.name.toLowerCase().includes('bad')) // Legacy mock support
    )
    
    if (integrityIssue) {
       issues.value.push({
          type: 'Integrity',
          severity: 'critical', // New level
          message: `ACADEMIC MISCONDUCT RECORD: ${integrityIssue.reason || 'Flagged in Integrity Database'}`
       })
       riskLevel.value = 'high'
    }

    // 1. Institution Check (Fuzzy Match)
    if (props.writerAffiliation && props.reviewer.affiliation) {
      const authAff = props.writerAffiliation.toLowerCase()
      const revAff = props.reviewer.affiliation.toLowerCase()
      // Simple inclusion check
      if (authAff.includes(revAff) || revAff.includes(authAff)) {
        issues.value.push({
          type: 'Institution',
          severity: 'high',
          message: `Same institution detected: "${props.reviewer.affiliation}"`
        })
        riskLevel.value = 'high'
      }
    }

    // 2. Co-author Check (Last 3 Years)
    // Check if writerName and reviewer.username appear in same paper
    const coAuthoredPaper = mockPaperDatabase.find(paper => {
      const hasAuthor = paper.writers.some(a => a.includes(props.writerName) || props.writerName.includes(a))
      const hasReviewer = paper.writers.some(a => a.includes(props.reviewer.username) || props.reviewer.username.includes(a))
      return hasAuthor && hasReviewer
    })

    if (coAuthoredPaper) {
      issues.value.push({
        type: 'Collaboration',
        severity: 'high',
        message: `Recent co-authorship found: "${coAuthoredPaper.title}" (${coAuthoredPaper.year})`
      })
      riskLevel.value = 'high'
    }

    // 3. Random Mentor/Student Check (Mock)
    // 10% chance if no other issues
    if (issues.value.length === 0 && Math.random() < 0.1) {
      issues.value.push({
        type: 'Relationship',
        severity: 'medium',
        message: 'Potential academic relationship detected (Academic Lineage Database)'
      })
      riskLevel.value = riskLevel.value === 'high' ? 'high' : 'medium'
    }
    
    // 4. ORCID Network (Mock)
    if (Math.random() < 0.05) {
       issues.value.push({
        type: 'Network',
        severity: 'low',
        message: 'Close proximity in co-citation network'
      })
    }

    checking.value = false
  }, 800)
}

onMounted(() => {
  checkCOI()
})

watch(() => props.reviewer, () => {
  checkCOI()
})

const getRiskColor = (level) => {
  switch(level) {
    case 'high': return '#f44336'
    case 'medium': return '#ff9800'
    default: return '#4caf50'
  }
}

const getRiskLabel = (level) => {
  switch(level) {
    case 'high': return 'High Risk'
    case 'medium': return 'Medium Risk'
    default: return 'Safe'
  }
}
</script>

<template>
  <div class="coi-check-container" :class="{ 'compact': compact }">
    <div v-if="checking" class="checking-state">
      <span class="spinner-small"></span> Checking Conflict of Interest...
    </div>
    
    <div v-else class="result-state">
      <div class="risk-badge" :style="{ backgroundColor: getRiskColor(riskLevel) }">
        {{ getRiskLabel(riskLevel) }}
      </div>
      
      <div v-if="issues.length > 0" class="issues-list">
        <div v-for="(issue, idx) in issues" :key="idx" class="issue-item">
          <span class="issue-icon" v-if="issue.severity === 'high'">🚫</span>
          <span class="issue-icon" v-else-if="issue.severity === 'medium'">⚠️</span>
          <span class="issue-icon" v-else>ℹ️</span>
          <span class="issue-msg">{{ issue.message }}</span>
        </div>
      </div>
      <div v-else class="safe-msg">
        No obvious conflicts detected (Institution, Co-author, Network).
      </div>
    </div>
  </div>
</template>

<style scoped>
.coi-check-container {
  background: #fff;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.checking-state {
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner-small {
  width: 12px;
  height: 12px;
  border: 2px solid #ddd;
  border-top-color: #666;
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

.result-state {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-badge {
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  align-self: flex-start;
  font-weight: bold;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.issue-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  background: #fff5f5;
  padding: 4px;
  border-radius: 4px;
}

.issue-msg {
  color: #333;
}

.safe-msg {
  color: #4caf50;
  font-style: italic;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
