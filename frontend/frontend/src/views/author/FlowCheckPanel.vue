<script setup>
import { ref, computed, watch } from 'vue'
import { MANUSCRIPT_STATUS, STATUS_LABELS } from '../../constants/manuscriptStatus'
import { manuscriptApi } from '../../utils/api'

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

const isProcessing = (status) => [
  MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
  MANUSCRIPT_STATUS.SCREEN_EXPIRED,
  MANUSCRIPT_STATUS.INITIAL_REVIEW_IN_PROGRESS,
  MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED,
  MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
  MANUSCRIPT_STATUS.FINAL_DECISION_IN_PROGRESS
].includes(status)

const isUnderReview = (status) => [
  MANUSCRIPT_STATUS.REVIEWER_ASSIGNMENT_PENDING,
  MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
].includes(status)

const isWaitingApproval = (status) => [
  MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION,
  MANUSCRIPT_STATUS.AUTHOR_CONFIRMED
].includes(status)

const isNeedingRevision = (status) => [
  MANUSCRIPT_STATUS.FINAL_DECISION_REVISION,
  MANUSCRIPT_STATUS.AUTHOR_REVISING
].includes(status)

const isRevisionProcessing = (status) => [
  MANUSCRIPT_STATUS.REVISION_SUBMITTED
].includes(status)

const isDecisionMade = (status) => {
  if (!status) return false
  return [
    MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED,
    MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED,
    MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
  ].includes(status)
}

const isInProduction = (status) => [
  MANUSCRIPT_STATUS.IN_PRODUCTION,
  MANUSCRIPT_STATUS.PRODUCTION_COMPLETED,
  MANUSCRIPT_STATUS.ACCEPTED_FOR_PUBLISH,
  MANUSCRIPT_STATUS.PUBLISHED
].includes(status)

const isWithdrawn = (status) => [
  MANUSCRIPT_STATUS.WITHDRAWN
].includes(status)

const isTransfer = (status) => [
  MANUSCRIPT_STATUS.TRANSFER_SUGGESTED,
  MANUSCRIPT_STATUS.TRANSFERRED
].includes(status)

const getActualModules = (status) => {
  const modules = []
  if (isProcessing(status)) modules.push('Submissions Being Processed')
  if (isWaitingApproval(status)) modules.push("Submissions Waiting for Author's Approval")
  if (isUnderReview(status)) modules.push('Under Review')
  if (isNeedingRevision(status)) modules.push('Submissions Needing Revision')
  if (isRevisionProcessing(status)) modules.push('Revisions Being Processed')
  if (isDecisionMade(status)) modules.push('Submissions with a Decision')
  if (isInProduction(status)) modules.push('In Production')
  if (isWithdrawn(status)) modules.push('Withdrawn')
  if (isTransfer(status)) modules.push('Transfer')
  return modules
}

const RULES = [
  {
    name: 'New Submissions Check',
    triggers: [MANUSCRIPT_STATUS.SUBMITTED, MANUSCRIPT_STATUS.PENDING_SCREEN],
    expected: 'Submissions Being Processed'
  },
  {
    name: 'Processing Check',
    triggers: [
      MANUSCRIPT_STATUS.SCREEN_EXPIRED,
      MANUSCRIPT_STATUS.INITIAL_REVIEW_IN_PROGRESS,
      MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED,
      MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
      MANUSCRIPT_STATUS.FINAL_DECISION_IN_PROGRESS
    ],
    expected: 'Submissions Being Processed'
  },
  {
    name: 'Under Review Check',
    triggers: [MANUSCRIPT_STATUS.REVIEWER_ASSIGNMENT_PENDING, MANUSCRIPT_STATUS.UNDER_PEER_REVIEW],
    expected: 'Under Review'
  },
  {
    name: 'Revision Needed Check',
    triggers: [MANUSCRIPT_STATUS.FINAL_DECISION_REVISION, MANUSCRIPT_STATUS.AUTHOR_REVISING],
    expected: 'Submissions Needing Revision'
  },
  {
    name: 'Revision Processing Check',
    triggers: [MANUSCRIPT_STATUS.REVISION_SUBMITTED],
    expected: 'Revisions Being Processed'
  },
  {
    name: 'Decision Made Check',
    triggers: [
      MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED,
      MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED,
      MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
    ],
    expected: 'Submissions with a Decision'
  },
  {
    name: 'In Production Check',
    triggers: [
      MANUSCRIPT_STATUS.IN_PRODUCTION,
      MANUSCRIPT_STATUS.PRODUCTION_COMPLETED,
      MANUSCRIPT_STATUS.ACCEPTED_FOR_PUBLISH,
      MANUSCRIPT_STATUS.PUBLISHED
    ],
    expected: 'In Production'
  },
  {
    name: 'Withdrawn Check',
    triggers: [MANUSCRIPT_STATUS.WITHDRAWN],
    expected: 'Withdrawn'
  },
  {
    name: 'Transfer Check',
    triggers: [MANUSCRIPT_STATUS.TRANSFER_SUGGESTED, MANUSCRIPT_STATUS.TRANSFERRED],
    expected: 'Transfer'
  }
]

const runCheck = async () => {
  isChecking.value = true
  anomalies.value = []
  checkTime.value = new Date().toLocaleString()
  
  try {
    const manuscriptsToCheck = props.manuscripts.length > 0 
      ? props.manuscripts 
      : (await manuscriptApi.getMyManuscripts({ page: 1, page_size: 100 })).items || []

    manuscriptsToCheck.forEach(ms => {
      const status = ms.status
      const actualModules = getActualModules(status)
      const rule = RULES.find(r => r.triggers.includes(status))
      
      if (rule && !actualModules.includes(rule.expected)) {
        anomalies.value.push({
          id: ms.id || ms.jid,
          title: ms.title,
          status: status,
          statusLabel: STATUS_LABELS[status] || status,
          expected: rule.expected,
          actual: actualModules.length > 0 ? actualModules.join(', ') : 'None (Hidden)',
          suggestion: `Check filter logic for '${rule.expected}'. Status '${status}' might be missing.`
        })
      }
    })
    
    showResults.value = true
  } catch (error) {
    console.error('Flow check failed:', error)
  } finally {
    isChecking.value = false
  }
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
.flow-check-panel {
  background-color: white;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-family: 'Segoe UI', sans-serif;
  border-left: 4px solid #0056B3;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
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
