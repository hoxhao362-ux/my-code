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
  { time: '2026-02-13 10:00:00', editor: 'System', action: '扫描完成。结果：通过。' }
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
  { time: '2026-02-13 10:20:00', editor: 'System', content: '作者已确认自引检查结果。' }
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
  if (confirm('确认稿件匿名化符合要求吗？')) {
    scanReport.value.status = 'Approved'
    addLog('批准稿件匿名化。')
  }
}

const requestScanRevision = () => {
  const feedback = prompt('请输入给作者的修改指示:')
  if (feedback) {
    scanReport.value.status = 'Needs Revision'
    addLog(`请求匿名化修改。反馈: ${feedback}`)
  }
}

// 2. Reference Actions
const approveRef = () => {
  if (confirm('确认参考文献匿名化符合要求吗？')) {
    addLog('批准参考文献匿名化。')
    alert('参考文献匿名化已批准。')
  }
}

const requestRefRevision = () => {
  const feedback = prompt('输入具体的参考文献错误:')
  if (feedback) {
    addLog(`请求参考文献修改。反馈: ${feedback}`)
  }
}

// 3. Self-Cite Actions
const approveSelfCite = () => {
  if (confirm('确认自引处理符合要求吗？')) {
    addLog('批准自引检测结果。')
    alert('自引审计已批准。')
  }
}

const requestSelfCiteReverify = () => {
  const feedback = prompt('重新验证请求的原因:')
  if (feedback) {
    addLog(`请求重新验证自引。原因: ${feedback}`)
  }
}

const reDetectSelfCite = () => {
  if (confirm('重新运行自引检测？这将重置作者的确认。')) {
    addLog('触发了自引重新检测。')
    alert('检测已重新运行。')
  }
}

</script>

<template>
  <div class="blind-review-audit">
    
    <!-- 1. Manuscript Anonymization Scan Report -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">稿件匿名化扫描报告</h2>
        <div class="status-tag" :class="scanReport.status.toLowerCase().replace(' ', '-')">
          {{ scanReport.status === 'Passed' ? '通过' : (scanReport.status === 'Approved' ? '已批准' : '需修改') }}
        </div>
      </div>
      
      <div class="info-grid">
        <div class="info-item">
          <span class="label">扫描时间:</span>
          <span class="value">{{ scanReport.scanTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">发现风险项:</span>
          <span class="value">{{ scanReport.risks.length }}</span>
        </div>
      </div>

      <!-- Risk List (if any) -->
      <div v-if="scanReport.risks.length > 0" class="risk-list">
        <div v-for="(risk, idx) in scanReport.risks" :key="idx" class="risk-item">
          <span class="risk-dot">●</span>
          第 {{ risk.page }} 页, {{ risk.location || '第 ' + risk.line + ' 行' }}: {{ risk.type }} - <span class="risk-content">{{ risk.content }}</span>
        </div>
      </div>
      <div v-else class="success-message">
        ✅ 未检测到作者身份信息。
      </div>

      <div class="action-bar">
        <button class="btn-action btn-red" @click="approveScan">批准匿名化</button>
        <button class="btn-action btn-gray" @click="requestScanRevision">请求修改</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 2. Reference Anonymization Audit -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">参考文献匿名化审计</h2>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <span class="label">处理时间:</span>
          <span class="value">{{ refAudit.processTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">作者确认:</span>
          <span class="value">{{ refAudit.confirmTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">总数 / 已匿名化:</span>
          <span class="value">{{ refAudit.totalRefs }} / {{ refAudit.anonymizedCount }}</span>
        </div>
      </div>

      <div class="ref-comparison-table">
        <div class="ref-header">
          <div class="col">原始参考文献列表</div>
          <div class="col">匿名化参考文献列表</div>
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
        <button class="btn-action btn-red" @click="approveRef">批准匿名化</button>
        <button class="btn-action btn-gray" @click="requestRefRevision">请求修改</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 3. Self-Citation Detection Audit -->
    <section class="audit-section">
      <div class="section-header">
        <h2 class="section-title">自引检测审计 (Self-Citation Audit)</h2>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <span class="label">检测时间:</span>
          <span class="value">{{ selfCiteAudit.detectTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">确认时间:</span>
          <span class="value">{{ selfCiteAudit.confirmTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">明确自引 / 潜在自引:</span>
          <span class="value">{{ selfCiteAudit.explicitCount }} / {{ selfCiteAudit.potentialCount }}</span>
        </div>
      </div>

      <div class="potential-check-list" v-if="selfCiteAudit.potentialList.length > 0">
        <h4 class="sub-title">作者验证记录 (潜在自引)</h4>
        <div v-for="item in selfCiteAudit.potentialList" :key="item.id" class="check-item">
          <div class="check-content">
            <div class="ref-text">{{ item.ref }}</div>
            <div class="reason-text">原因: {{ item.reason }}</div>
          </div>
          <div class="check-result">
            作者选择: <span class="tag-verify">{{ item.authorVerify === 'Is Self-Citation' ? '确认为自引' : '非自引' }}</span>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button class="btn-action btn-red" @click="approveSelfCite">批准</button>
        <button class="btn-action btn-gray" @click="requestSelfCiteReverify">请求重新验证</button>
        <button class="btn-action btn-gray" @click="reDetectSelfCite">重新检测</button>
      </div>
    </section>

    <div class="divider"></div>

    <!-- Audit Logs -->
    <section class="audit-section">
      <h3 class="history-title">审计日志</h3>
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
