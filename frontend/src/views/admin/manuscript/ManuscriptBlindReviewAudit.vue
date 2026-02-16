<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  manuscriptId: {
    type: String,
    required: true
  }
})

// --- Mock Data: 1. Manuscript Anonymization Scan Report ---
const scanReport = ref({
  scanTime: '2026-02-13 10:00:00',
  status: 'Passed', // Passed, Needs Revision
  risks: [], // Empty if passed
  // Mocking a failed state for demo purposes if needed, but default to passed for "happy path"
  // risks: [
  //   { page: 1, line: 12, type: 'Author Name', content: 'John Doe' },
  //   { page: 5, location: 'Footer', type: 'Affiliation', content: 'University of Science' }
  // ]
})

const scanHistory = ref([
  { time: '2026-02-13 10:00:00', editor: 'System', action: 'Scan Completed. Result: Passed.' }
])

// --- Mock Data: 2. Reference Anonymization Audit ---
const refAudit = ref({
  processTime: '2026-02-13 10:05:00',
  confirmTime: '2026-02-13 10:10:00',
  totalRefs: 45,
  anonymizedCount: 3,
  list: [
    { 
      id: 1, 
      original: 'Doe J, Smith A. 2024. Novel approaches in cardiology. J Med. 12(3):45-50.', 
      anonymized: 'Author et al. 2024. Novel approaches in cardiology. J Med. 12(3):45-50.',
      isSelfCite: true 
    },
    { 
      id: 2, 
      original: 'Brown K. 2023. Previous studies on heart failure. Lancet. 301:112.', 
      anonymized: 'Brown K. 2023. Previous studies on heart failure. Lancet. 301:112.',
      isSelfCite: false 
    },
    { 
      id: 3, 
      original: 'Doe J. 2022. Early foundations. Nature. 500:20.', 
      anonymized: 'Author. 2022. Early foundations. Nature. 500:20.',
      isSelfCite: true 
    }
  ]
})

// --- Mock Data: 3. Self-Citation Detection Audit ---
const selfCiteAudit = ref({
  detectTime: '2026-02-13 10:15:00',
  confirmTime: '2026-02-13 10:20:00',
  explicitCount: 2,
  potentialCount: 1,
  potentialList: [
    {
      id: 101,
      ref: 'Wilson R, Doe J. 2021. Collaborative works.',
      reason: 'Co-author match "Doe J"',
      authorVerify: 'Is Self-Citation' // or 'Not Self-Citation'
    }
  ]
})

// --- Logs ---
const auditLogs = ref([
  { time: '2026-02-13 10:20:00', editor: 'System', content: 'Author confirmed self-citation checks.' }
])

// --- Methods ---

const addLog = (content) => {
  const now = new Date()
  const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  auditLogs.value.unshift({
    time: timeStr,
    editor: 'Editor',
    content: content
  })
}

// 1. Scan Actions
const approveScan = () => {
  if (confirm('Confirm that the manuscript anonymization is compliant?')) {
    scanReport.value.status = 'Approved'
    addLog('Approved manuscript anonymization.')
  }
}

const requestScanRevision = () => {
  const feedback = prompt('Please enter revision instructions for the author:')
  if (feedback) {
    scanReport.value.status = 'Needs Revision'
    addLog(`Requested revision for anonymization. Feedback: ${feedback}`)
  }
}

// 2. Reference Actions
const approveRef = () => {
  if (confirm('Confirm that the reference anonymization is compliant?')) {
    addLog('Approved reference anonymization.')
    alert('Reference anonymization approved.')
  }
}

const requestRefRevision = () => {
  const feedback = prompt('Enter specific reference errors:')
  if (feedback) {
    addLog(`Requested revision for references. Feedback: ${feedback}`)
  }
}

// 3. Self-Cite Actions
const approveSelfCite = () => {
  if (confirm('Confirm that self-citation handling is compliant?')) {
    addLog('Approved self-citation detection results.')
    alert('Self-citation audit approved.')
  }
}

const requestSelfCiteReverify = () => {
  const feedback = prompt('Reason for re-verification request:')
  if (feedback) {
    addLog(`Requested re-verification of self-citations. Reason: ${feedback}`)
  }
}

const reDetectSelfCite = () => {
  if (confirm('Re-run self-citation detection? This will reset author confirmations.')) {
    addLog('Triggered re-detection of self-citations.')
    alert('Detection re-run successfully.')
  }
}

</script>

<template>
  <div class="blind-review-audit">
    
    <!-- 1. Manuscript Anonymization Scan Report -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">Manuscript Anonymization Scan Report</h2>
        <div class="status-tag" :class="scanReport.status.toLowerCase().replace(' ', '-')">
          {{ scanReport.status }}
        </div>
      </div>
      
      <div class="info-grid">
        <div class="info-item">
          <span class="label">Scan Time:</span>
          <span class="value">{{ scanReport.scanTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Risk Items Found:</span>
          <span class="value">{{ scanReport.risks.length }}</span>
        </div>
      </div>

      <!-- Risk List (if any) -->
      <div v-if="scanReport.risks.length > 0" class="risk-list">
        <div v-for="(risk, idx) in scanReport.risks" :key="idx" class="risk-item">
          <span class="risk-dot">●</span>
          Page {{ risk.page }}, {{ risk.location || 'Line ' + risk.line }}: {{ risk.type }} - <span class="risk-content">{{ risk.content }}</span>
        </div>
      </div>
      <div v-else class="success-message">
        ✅ No author identifying information detected.
      </div>

      <div class="action-bar">
        <button class="btn-action btn-red" @click="approveScan">Approve Anonymization</button>
        <button class="btn-action btn-gray" @click="requestScanRevision">Request Revision</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 2. Reference Anonymization Audit -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">Reference Anonymization Audit</h2>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <span class="label">Processed:</span>
          <span class="value">{{ refAudit.processTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Author Confirmed:</span>
          <span class="value">{{ refAudit.confirmTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Total / Anonymized:</span>
          <span class="value">{{ refAudit.totalRefs }} / {{ refAudit.anonymizedCount }}</span>
        </div>
      </div>

      <div class="ref-comparison-table">
        <div class="ref-header">
          <div class="col">Original Reference List</div>
          <div class="col">Anonymized Reference List</div>
        </div>
        <div class="ref-body">
          <div v-for="item in refAudit.list" :key="item.id" class="ref-row">
            <div class="col original">
              <span v-if="item.isSelfCite" class="self-cite-mark">*</span>
              <span :class="{ 'text-red': item.isSelfCite }">{{ item.original }}</span>
            </div>
            <div class="col anonymized">
              <span :class="{ 'text-green': item.isSelfCite }">{{ item.anonymized }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button class="btn-action btn-red" @click="approveRef">Approve Anonymization</button>
        <button class="btn-action btn-gray" @click="requestRefRevision">Request Revision</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 3. Self-Citation Detection Audit -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">Self-Citation Detection Audit</h2>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <span class="label">Detected:</span>
          <span class="value">{{ selfCiteAudit.detectTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Confirmed:</span>
          <span class="value">{{ selfCiteAudit.confirmTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Explicit / Potential:</span>
          <span class="value">{{ selfCiteAudit.explicitCount }} / {{ selfCiteAudit.potentialCount }}</span>
        </div>
      </div>

      <div class="potential-check-list" v-if="selfCiteAudit.potentialList.length > 0">
        <h4 class="sub-title">Author Verification Records (Potential Self-Citations)</h4>
        <div v-for="item in selfCiteAudit.potentialList" :key="item.id" class="check-item">
          <div class="check-content">
            <div class="ref-text">{{ item.ref }}</div>
            <div class="reason-text">Reason: {{ item.reason }}</div>
          </div>
          <div class="check-result">
            Author Selection: <span class="tag-verify">{{ item.authorVerify }}</span>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button class="btn-action btn-red" @click="approveSelfCite">Approve</button>
        <button class="btn-action btn-gray" @click="requestSelfCiteReverify">Request Re-verification</button>
        <button class="btn-action btn-gray" @click="reDetectSelfCite">Re-detect</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- Audit Logs -->
    <section class="audit-section">
      <h3 class="history-title">Audit Logs</h3>
      <div class="log-list">
        <div v-for="(log, idx) in auditLogs" :key="idx" class="log-item">
          {{ log.time }} | {{ log.editor }} | {{ log.content }}
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.blind-review-audit {
  padding: 1rem 0;
  font-family: Arial, sans-serif;
}

.audit-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.status-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}
.status-tag.passed, .status-tag.approved { color: #28A745; background: rgba(40, 167, 69, 0.1); }
.status-tag.needs-revision { color: #C93737; background: rgba(201, 55, 55, 0.1); }

.info-grid {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label { font-size: 12px; color: #999; }
.value { font-size: 14px; color: #333; font-weight: 500; }

.divider {
  height: 1px;
  background: #eee;
  margin: 2rem 0;
}

/* Risk List */
.risk-list {
  background: #fff0f0;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}
.risk-item { font-size: 14px; color: #333; margin-bottom: 8px; }
.risk-dot { color: #C93737; margin-right: 8px; }
.risk-content { font-weight: bold; }
.success-message { color: #28A745; font-size: 14px; margin-bottom: 1.5rem; font-weight: 500; }

/* Ref Comparison */
.ref-comparison-table {
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}
.ref-header {
  display: flex;
  background: #f5f5f5;
  padding: 10px;
  font-weight: bold;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #eee;
}
.ref-body {
  max-height: 300px;
  overflow-y: auto;
}
.ref-row {
  display: flex;
  border-bottom: 1px solid #eee;
}
.col {
  flex: 1;
  padding: 10px;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}
.col.original { border-right: 1px solid #eee; }
.text-red { color: #C93737; }
.text-green { color: #28A745; }
.self-cite-mark { color: #C93737; margin-right: 4px; font-weight: bold; }

/* Potential Check List */
.sub-title { font-size: 15px; color: #333; margin-bottom: 10px; }
.check-item {
  border: 1px solid #eee;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ref-text { font-size: 14px; color: #333; margin-bottom: 4px; }
.reason-text { font-size: 12px; color: #999; }
.tag-verify {
  background: #e6f7ff;
  color: #1890ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #91d5ff;
}

/* Actions */
.action-bar {
  display: flex;
  gap: 10px;
}
.btn-action {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-red { background: #C93737; color: white; }
.btn-red:hover { background: #B02E2E; }
.btn-gray { background: #E0E0E0; color: #333; }
.btn-gray:hover { background: #D0D0D0; }

/* Logs */
.history-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px; }
.log-list {
  max-height: 150px;
  overflow-y: auto;
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
}
.log-item {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
  font-family: monospace;
}
</style>
