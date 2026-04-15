<script setup>
import { ref, computed } from 'vue'
import { MANUSCRIPT_STATUS, STATUS_LABELS } from '../../constants/manuscriptStatus'

const props = defineProps({
  manuscripts: {
    type: Array,
    required: true,
    default: () => []
  }
})

const isChecking = ref(false)
const showResults = ref(false)
const checkTime = ref('')
const anomalies = ref([])

// --- Duplicate Logic from Dashboard.vue for "Actual" detection ---
// We duplicate this to ensure we are testing the *intended* logic vs *actual* behavior
// If Dashboard.vue changes, this might drift, which is good for regression testing (detection).
// However, to detect if "Dashboard is NOT showing it", we need to know what Dashboard *is* showing.
// So we replicate the Dashboard's filter logic here.

const isProcessing = (status) => [
  MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
  MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW,
  MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED,
  MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
  MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
].includes(status)

const isUnderReview = (status) => [
  MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
].includes(status)

const isWaitingApproval = (status) => [
  'Awaiting Author Approval' 
].includes(status)

const isNeedingRevision = (status) => [
  MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION,
  MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
].includes(status)

const isRevisionProcessing = (status) => [
  'Revision Submitted'
].includes(status)

const isDecisionMade = (status) => {
  if (!status) return false
  return [
    MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED,
    MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  ].includes(status)
}

const isInProduction = (status) => [
  MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION,
  MANUSCRIPT_STATUS.PENDING_COPYRIGHT,
  MANUSCRIPT_STATUS.PENDING_PROOF,
  MANUSCRIPT_STATUS.PENDING_PUBLICATION,
  MANUSCRIPT_STATUS.PUBLISHED
].includes(status)

const isWithdrawn = (status) => [
  MANUSCRIPT_STATUS.WITHDRAWN
].includes(status)

const getActualModules = (status) => {
  const modules = []
  if (isProcessing(status)) modules.push('Submissions Being Processed')
  if (isWaitingApproval(status)) modules.push('Submissions Waiting for Author\'s Approval')
  if (isUnderReview(status)) modules.push('Under Review')
  if (isNeedingRevision(status)) modules.push('Submissions Needing Revision')
  if (isRevisionProcessing(status)) modules.push('Revisions Being Processed')
  if (isDecisionMade(status)) modules.push('Submissions with a Decision')
  if (isInProduction(status)) modules.push('In Production')
  if (isWithdrawn(status)) modules.push('Withdrawn')
  return modules
}

// --- Journal Platform Requirement Rules ---
// Based on the SRS Document provided
const RULES = [
  {
    name: 'New Submissions Check',
    triggers: [MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW], // "Submitted / Pending Screening"
    expected: 'Submissions Being Processed' // Requirement says "Submit New Manuscript" but that's a button. Mapping to list.
  },
  {
    name: 'Processing Check',
    triggers: [
      MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW, // "Under Screening"
      MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED, // Implicitly processing?
      MANUSCRIPT_STATUS.PENDING_FINAL_DECISION, // Implicitly processing?
      MANUSCRIPT_STATUS.UNDER_FINAL_DECISION // "Assigned to Editor"?
    ],
    expected: 'Submissions Being Processed'
  },
  {
    name: 'Waiting Approval Check',
    triggers: ['Awaiting Author Approval'],
    expected: 'Submissions Waiting for Author\'s Approval'
  },
  {
    name: 'Under Review Check',
    triggers: [MANUSCRIPT_STATUS.UNDER_PEER_REVIEW],
    expected: 'Under Review'
  },
  {
    name: 'Revision Needed Check',
    triggers: [
      MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION,
      MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
    ],
    expected: 'Submissions Needing Revision'
  },
  {
    name: 'Revision Processing Check',
    triggers: ['Revision Submitted'],
    expected: 'Revisions Being Processed'
  },
  {
    name: 'Decision Made Check',
    triggers: [
      MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED,
      MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED,
      MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
    ],
    expected: 'Submissions with a Decision'
  },
  {
    name: 'In Production Check',
    triggers: [
      // Requirement says "In Production / Accepted & In Production"
      // Code has specific statuses
      MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION,
      MANUSCRIPT_STATUS.PENDING_COPYRIGHT,
      MANUSCRIPT_STATUS.PENDING_PROOF,
      MANUSCRIPT_STATUS.PENDING_PUBLICATION,
      MANUSCRIPT_STATUS.PUBLISHED
    ],
    expected: 'In Production'
  },
  {
    name: 'Withdrawn Check',
    triggers: [MANUSCRIPT_STATUS.WITHDRAWN],
    expected: 'Withdrawn'
  }
]

const runCheck = () => {
  isChecking.value = true
  anomalies.value = []
  checkTime.value = new Date().toLocaleString()
  
  // Process
  setTimeout(() => {
    props.manuscripts.forEach(ms => {
      const status = ms.status
      const actualModules = getActualModules(status)
      
      // Find matching rule
      const rule = RULES.find(r => r.triggers.includes(status))
      
      if (rule) {
        // Check if expected module is in actual modules
        if (!actualModules.includes(rule.expected)) {
          anomalies.value.push({
            id: ms.id,
            title: ms.title,
            status: status,
            statusLabel: STATUS_LABELS[status] || status,
            expected: rule.expected,
            actual: actualModules.length > 0 ? actualModules.join(', ') : 'None (Hidden)',
            suggestion: `Check filter logic for '${rule.expected}'. Status '${status}' might be missing.`
          })
        }
      } else {
        // Status not covered by rules?
        // Requirement doesn't say to report unknown statuses, but good for debugging.
        // We'll skip for now to stick to SRS.
      }
    })
    
    showResults.value = true
    isChecking.value = false
  }, 500) // Simulate processing time
}

defineExpose({ runCheck })

</script>

<template>
  <div class="flow-check-panel" v-if="showResults">
    <div class="panel-header">
      <h3>Flow Check Report</h3>
      <button class="close-btn" @click="showResults = false">&times;</button>
    </div>
    
    <div class="panel-body">
      <!-- Overview -->
      <div class="overview-section">
        <div class="stat-item">
          <span class="label">Check Time:</span>
          <span class="value">{{ checkTime }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Total Manuscripts:</span>
          <span class="value">{{ manuscripts.length }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Anomalies Found:</span>
          <span class="value count-badge" :class="{ 'zero': anomalies.length === 0, 'error': anomalies.length > 0 }">
            {{ anomalies.length }}
          </span>
        </div>
      </div>
      
      <!-- Anomalies List -->
      <div v-if="anomalies.length > 0" class="anomalies-section">
        <h4>Anomaly Details</h4>
        <div class="table-container">
          <table class="anomaly-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Status Code</th>
                <th>Expected Module</th>
                <th>Actual Module</th>
                <th>Suggestion</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in anomalies" :key="item.id">
                <td>#{{ item.id }}</td>
                <td><code class="status-code">{{ item.status }}</code></td>
                <td>{{ item.expected }}</td>
                <td class="actual-col">{{ item.actual }}</td>
                <td>{{ item.suggestion }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else class="success-message">
        <span class="check-icon">✓</span> All manuscripts are flowing correctly according to Peerex Peer norms.
      </div>
    </div>
  </div>
</template>

<style scoped>
.jp-flow-check {
  background-color: white;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-family: 'Segoe UI', sans-serif;
  border-left: 4px solid #0056B3;
}

.header h3 {
  margin-top: 0;
  color: #333;
  font-size: 18px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.panel-body {
  padding: 1.5rem;
}

.overview-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item .label {
  font-size: 0.85rem;
  color: #666;
}

.stat-item .value {
  font-weight: bold;
  font-size: 1.1rem;
}

.count-badge.zero { color: #28a745; }
.count-badge.error { color: #dc3545; }

.table-container {
  overflow-x: auto;
}

.anomaly-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.anomaly-table th,
.anomaly-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.anomaly-table th {
  background: #f9f9f9;
  font-weight: 600;
  color: #555;
}

.status-code {
  background: #f0f0f0;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.85rem;
}

.actual-col {
  color: #dc3545;
  font-weight: 500;
}

.success-message {
  text-align: center;
  padding: 2rem;
  color: #28a745;
  font-size: 1.1rem;
}

.check-icon {
  font-size: 1.5rem;
  margin-right: 0.5rem;
}
</style>
