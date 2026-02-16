<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// Form
const generateForm = ref({
  quantity: 1,
  validity: 30,
  discipline: 'Clinical',
  role: 'senior_reviewer'
})

const disciplines = ['Clinical', 'Public Health', 'Global Health', 'Oncology']

// Mock Data - Codes
const codes = ref([
  { code: 'LANCET-2026-X8Y2', created_at: '2026-02-13 10:00', expires_at: '2026-03-15', discipline: 'Clinical', role: 'senior', status: 'unused', used_by: '-' },
  { code: 'LANCET-2026-A1B2', created_at: '2026-02-10 09:30', expires_at: '2026-03-12', discipline: 'Public Health', role: 'senior', status: 'used', used_by: 'Dr. Smith (Harvard)' },
  { code: 'LANCET-2026-K9L0', created_at: '2026-01-01 14:00', expires_at: '2026-01-08', discipline: 'Global Health', role: 'basic', status: 'expired', used_by: '-' },
  { code: 'LANCET-2026-Q5W6', created_at: '2026-02-12 11:00', expires_at: '2026-03-14', discipline: 'Clinical', role: 'senior', status: 'invalidated', used_by: '-' }
])

// Actions
const generateCodes = () => {
  if (generateForm.value.quantity < 1 || generateForm.value.quantity > 100) {
    alert('Quantity must be between 1 and 100.')
    return
  }
  
  // Mock Generation
  const newCodes = []
  for (let i = 0; i < generateForm.value.quantity; i++) {
    const randomStr = Math.random().toString(36).substring(2, 6).toUpperCase()
    newCodes.push({
      code: `LANCET-2026-${randomStr}`,
      created_at: new Date().toISOString().slice(0, 16).replace('T', ' '),
      expires_at: new Date(Date.now() + generateForm.value.validity * 86400000).toISOString().split('T')[0],
      discipline: generateForm.value.discipline,
      role: generateForm.value.role === 'senior_reviewer' ? 'senior' : 'basic',
      status: 'unused',
      used_by: '-'
    })
  }
  
  codes.value = [...newCodes, ...codes.value]
  alert(`${generateForm.value.quantity} invitation codes generated successfully.`)
}

const invalidateCode = (item) => {
  if (confirm(`Are you sure you want to invalidate code ${item.code}?`)) {
    item.status = 'invalidated'
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    alert('Code copied to clipboard!')
  })
}

</script>

<template>
  <div class="lancet-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user"
      current-page="editor-system-invitation-codes"
      :toggle-directory="()=>{}"
      :logout="userStore.logout"
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Reviewer Invitation Code Management</h1>
        <p class="warning-text">Policy: Invitation Code = Senior Access (Invite Only). Open Registration = Basic Access (Strict Audit).</p>
      </div>

      <!-- Generation Form -->
      <section class="generation-section">
        <div class="form-row">
          <div class="form-group">
            <label>Quantity (1-100)</label>
            <input type="number" v-model="generateForm.quantity" min="1" max="100">
          </div>
          <div class="form-group">
            <label>Validity Period</label>
            <select v-model="generateForm.validity">
              <option :value="7">7 Days</option>
              <option :value="15">15 Days</option>
              <option :value="30">30 Days</option>
            </select>
          </div>
          <div class="form-group">
            <label>Discipline</label>
            <select v-model="generateForm.discipline">
              <option v-for="d in disciplines" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Role Permission</label>
            <select v-model="generateForm.role">
              <option value="senior_reviewer">Senior Reviewer (Invited)</option>
              <option value="basic_reviewer">Basic Reviewer (Open)</option>
            </select>
          </div>
          <div class="form-group action">
            <button class="btn btn-red" @click="generateCodes">Generate Codes</button>
          </div>
        </div>
      </section>

      <!-- Code List -->
      <section class="list-section">
        <table class="lancet-table">
          <thead>
            <tr>
              <th>Invitation Code</th>
              <th>Created At</th>
              <th>Expires At</th>
              <th>Discipline</th>
              <th>Role</th>
              <th>Status</th>
              <th>Used By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in codes" :key="item.code" class="hover-row">
              <td class="code-font">{{ item.code }}</td>
              <td>{{ item.created_at }}</td>
              <td>{{ item.expires_at }}</td>
              <td>{{ item.discipline }}</td>
              <td>{{ item.role === 'senior' ? 'Senior' : 'Basic' }}</td>
              <td>
                <span class="status-badge" :class="item.status">{{ item.status }}</span>
              </td>
              <td>{{ item.used_by }}</td>
              <td class="actions">
                <button class="btn-text" v-if="item.status === 'unused'" @click="copyCode(item.code)">Copy</button>
                <button class="btn-text red" v-if="item.status === 'unused'" @click="invalidateCode(item)">Invalidate</button>
                <button class="btn-text" v-else disabled>View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Rules Footer -->
      <div class="rules-footer">
        <h3>Registration Channels Rule</h3>
        <div class="rule-box">
          <p><strong>Invitation Channel:</strong> Editor invites experts -> Instant Audit -> Senior Role.</p>
          <p><strong>Open Channel:</strong> Self-application -> Strict Audit (1-3 months) -> Basic Role.</p>
        </div>
        <p class="audit-note">All code operations and registration audits are permanently archived.</p>
      </div>

    </main>
  </div>
</template>

<style scoped>
.lancet-container {
  font-family: 'Times New Roman', Times, serif;
  background-color: #FFFFFF;
  min-height: 100vh;
  color: #333333;
}

.content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.main-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.warning-text {
  font-size: 12px;
  color: #D1202F;
}

/* Generation Form */
.generation-section {
  background: #F9F9F9;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 30px;
  border: 1px solid #EEE;
}

.form-row {
  display: flex;
  gap: 20px;
  align-items: flex-end;
  justify-content: center;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 12px;
  font-weight: bold;
  color: #555;
  margin-bottom: 5px;
}

.form-group input, .form-group select {
  padding: 8px;
  border: 1px solid #CCC;
  min-width: 150px;
  font-family: 'Times New Roman';
}

.form-group.action {
  padding-bottom: 1px;
}

.btn-red {
  background: #D1202F;
  color: white;
  border: none;
  padding: 9px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

/* Table */
.lancet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.lancet-table th {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid #CCC;
  font-weight: bold;
  color: #555;
}

.lancet-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #EEE;
  vertical-align: middle;
}

.code-font {
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  letter-spacing: 1px;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  text-transform: uppercase;
}
.status-badge.unused { background: #E3F2FD; color: #1565C0; }
.status-badge.used { background: #E8F5E9; color: #2E7D32; }
.status-badge.expired { background: #FFF3E0; color: #EF6C00; }
.status-badge.invalidated { background: #F5F5F5; color: #757575; }

.btn-text {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 12px;
  margin-right: 10px;
  text-decoration: underline;
}
.btn-text.red { color: #D1202F; }
.btn-text:disabled { color: #CCC; cursor: not-allowed; text-decoration: none; }

/* Rules */
.rules-footer {
  margin-top: 40px;
  border-top: 1px solid #EEE;
  padding-top: 20px;
}

.rules-footer h3 {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.rule-box {
  background: #F9F9F9;
  padding: 15px;
  font-size: 13px;
  color: #555;
  margin-bottom: 10px;
}

.rule-box p {
  margin: 5px 0;
}

.audit-note {
  font-size: 12px;
  color: #999;
  text-align: center;
}

</style>