<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// Tabs
const activeTab = ref('members') // members, team, invitations, permissions

// Mock Data - Board Members (Editors)
const boardMembers = ref([
  { id: 1, name: 'Prof. John Doe', institution: 'Harvard Medical School', role: 'Editor-in-Chief', status: 'Active', email: 'john.doe@harvard.edu' },
  { id: 2, name: 'Dr. Jane Smith', institution: 'Oxford University', role: 'Senior Editor', status: 'Active', email: 'jane.smith@ox.ac.uk' }
])

// Mock Data - Editorial Team (AE, EA, Advisory)
const teamMembers = ref([
  { id: 101, name: 'Dr. Alan Turing', institution: 'Cambridge', role: 'Associate Editor', field: 'AI in Medicine', status: 'Active' },
  { id: 102, name: 'Sarah Connor', institution: '-', role: 'Editorial Assistant', field: 'Administrative', status: 'Active' }
])

// Mock Data - Invitations
const invitations = ref([
  { id: 501, type: 'Editor Nomination', recipient: 'prof.lee@tokyo.u.jp', sent_by: 'Prof. John Doe', sent_at: '2026-02-14', status: 'Pending', expires: '2026-02-21' },
  { id: 502, type: 'Associate Editor', recipient: 'dr.williams@yale.edu', sent_by: 'Dr. Jane Smith', sent_at: '2026-02-10', status: 'Accepted', expires: '2026-02-17' }
])

// Invitation Form
const showInviteModal = ref(false)
const inviteForm = ref({
  role: 'associate_editor', // editor, associate_editor, assistant, advisory
  name: '',
  email: '',
  institution: '',
  message: '',
  nominator2: '' // For Editor role
})

// Actions
const handleTabChange = (tab) => {
  activeTab.value = tab
}

const openInviteModal = () => {
  inviteForm.value = { role: 'associate_editor', name: '', email: '', institution: '', message: '', nominator2: '' }
  showInviteModal.value = true
}

const generateToken = () => {
  return Math.random().toString(36).substr(2, 9).toUpperCase()
}

const sendInvitation = () => {
  // Mock sending
  const token = generateToken()
  const inviteLink = `${window.location.origin}/invite/register?token=${token}&role=${inviteForm.value.role}`
  
  const newInvite = {
    id: Date.now(),
    type: formatRole(inviteForm.value.role),
    recipient: inviteForm.value.email,
    sent_by: user.value.username || 'Current Editor',
    sent_at: new Date().toISOString().split('T')[0],
    status: 'Pending',
    expires: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0], // 7 days default
    link: inviteLink,
    token: token
  }
  
  invitations.value.unshift(newInvite)
  showInviteModal.value = false
  
  // Show the link to the user (Mocking email sending)
  alert(`Invitation Generated!\n\nRole: ${formatRole(inviteForm.value.role)}\nLink: ${inviteLink}\n\n(In production, this would be emailed to ${inviteForm.value.email})`)
}

const formatRole = (role) => {
  const map = {
    'editor': 'Editor (Board Nomination)',
    'associate_editor': 'Associate Editor',
    'assistant': 'Editorial Assistant',
    'advisory': 'Advisory Editor'
  }
  return map[role] || role
}

const revokeInvite = (invite) => {
  if (confirm('Are you sure you want to revoke this invitation?')) {
    invite.status = 'Revoked'
  }
}

const removeMember = (member) => {
  if (confirm(`Remove ${member.name} from the team? This requires Board consensus.`)) {
    member.status = 'Removed'
  }
}

</script>

<template>
  <div class="jp-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user"
      current-page="editor-board"
      :toggle-directory="()=>{}"
      :logout="userStore.logout"
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Editorial Board Management</h1>
        <p class="sub-caption">Highest Authority & Decision Making Body. Restricted Access.</p>
      </div>

      <!-- Tabs -->
      <div class="jp-tabs">
        <button 
          v-for="tab in ['members', 'team', 'invitations', 'permissions']" 
          :key="tab"
          class="tab-btn"
          :class="{ active: activeTab === tab }"
          @click="handleTabChange(tab)"
        >
          {{ tab === 'members' ? 'Board Members' : tab === 'team' ? 'Editorial Team' : tab === 'invitations' ? 'Invitation Center' : 'Permissions' }}
        </button>
      </div>

      <!-- Tab Content: Board Members -->
      <section v-if="activeTab === 'members'" class="tab-content">
        <div class="section-header">
          <h2>Board Members (Editors)</h2>
          <button class="btn btn-primary" @click="openInviteModal">Nominate New Editor</button>
        </div>
        <p class="info-text">Note: Nomination requires 2 existing board members' consensus. Invite link expires in 7 days.</p>
        
        <table class="jp-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Institution</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in boardMembers" :key="m.id">
              <td class="bold-text">{{ m.name }}</td>
              <td>{{ m.institution }}</td>
              <td>{{ m.role }}</td>
              <td><span class="status-dot" :class="m.status.toLowerCase()"></span> {{ m.status }}</td>
              <td class="actions">
                <button class="btn-text">View Profile</button>
                <button class="btn-text text-danger">Suspend</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Tab Content: Editorial Team -->
      <section v-if="activeTab === 'team'" class="tab-content">
         <div class="section-header">
          <h2>Editorial Team (AE & Staff)</h2>
          <button class="btn btn-primary" @click="openInviteModal">Appoint New Member</button>
        </div>
        
        <table class="jp-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Field / Function</th>
              <th>Institution</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in teamMembers" :key="m.id">
              <td class="bold-text">{{ m.name }}</td>
              <td>{{ m.role }}</td>
              <td>{{ m.field }}</td>
              <td>{{ m.institution }}</td>
              <td><span class="status-dot" :class="m.status.toLowerCase()"></span> {{ m.status }}</td>
              <td class="actions">
                <button class="btn-text">Edit Rights</button>
                <button class="btn-text text-danger" @click="removeMember(m)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Tab Content: Invitations -->
      <section v-if="activeTab === 'invitations'" class="tab-content">
        <div class="section-header">
          <h2>Invitation Management</h2>
        </div>
        <p class="info-text">All invitations are tracked. Expired links are automatically invalidated.</p>

        <table class="jp-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Recipient</th>
              <th>Sent By</th>
              <th>Sent At</th>
              <th>Expires</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in invitations" :key="inv.id">
              <td class="bold-text">{{ inv.type }}</td>
              <td>{{ inv.recipient }}</td>
              <td>{{ inv.sent_by }}</td>
              <td>{{ inv.sent_at }}</td>
              <td>{{ inv.expires }}</td>
              <td>
                <span class="status-badge" :class="inv.status.toLowerCase()">{{ inv.status }}</span>
              </td>
              <td class="actions">
                <button class="btn-text" v-if="inv.status === 'Pending'" @click="revokeInvite(inv)">Revoke</button>
                <button class="btn-text" v-if="inv.status === 'Pending'" @click="alert('Link copied: ' + inv.link)">Copy Link</button>
                <span v-else class="disabled-text">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Tab Content: Permissions -->
      <section v-if="activeTab === 'permissions'" class="tab-content">
        <div class="section-header">
          <h2>Role Permission Overview</h2>
        </div>
        <div class="permission-grid">
          <div class="perm-card">
            <h3>Editor (Board)</h3>
            <ul>
              <li><strong>Final Decision:</strong> Yes</li>
              <li><strong>Team Management:</strong> Yes (All)</li>
              <li><strong>Invitation:</strong> Yes (All)</li>
              <li><strong>Access:</strong> Full System</li>
            </ul>
          </div>
          <div class="perm-card">
            <h3>Associate Editor</h3>
            <ul>
              <li><strong>Final Decision:</strong> No</li>
              <li><strong>Team Management:</strong> No</li>
              <li><strong>Invitation:</strong> No</li>
              <li><strong>Access:</strong> Assigned Manuscripts Only</li>
            </ul>
          </div>
          <div class="perm-card">
            <h3>EA & Advisory</h3>
            <ul>
              <li><strong>Final Decision:</strong> No</li>
              <li><strong>Team Management:</strong> No</li>
              <li><strong>Invitation:</strong> No</li>
              <li><strong>Access:</strong> Read-Only / Process Support</li>
            </ul>
          </div>
        </div>
      </section>

    </main>

    <!-- Invitation Modal -->
    <div v-if="showInviteModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Initiate Invitation</h3>
        <p class="modal-subtitle">Only Board Members can initiate invitations.</p>
        
        <div class="form-group">
          <label>Role to Invite</label>
          <select v-model="inviteForm.role">
            <option value="editor">Editor (Board Member Nomination)</option>
            <option value="associate_editor">Associate Editor</option>
            <option value="assistant">Editorial Assistant</option>
            <option value="advisory">Advisory Editor</option>
          </select>
        </div>

        <div class="form-group">
          <label>Recipient Name</label>
          <input v-model="inviteForm.name" placeholder="Full Name">
        </div>

        <div class="form-group">
          <label>Institutional Email</label>
          <input v-model="inviteForm.email" placeholder="official@institution.edu">
        </div>
        
        <div class="form-group">
          <label>Institution</label>
          <input v-model="inviteForm.institution" placeholder="University / Institute">
        </div>

        <div class="form-group" v-if="inviteForm.role === 'editor'">
          <label>Second Nominator (Required for Board Member)</label>
          <select v-model="inviteForm.nominator2" class="form-control">
            <option value="" disabled>Select a Board Member</option>
            <option v-for="m in boardMembers" :key="m.id" :value="m.name">{{ m.name }}</option>
          </select>
        </div>

        <div class="form-group" v-if="inviteForm.role === 'editor'">
          <label>Nomination Reason (Required)</label>
          <textarea v-model="inviteForm.message" rows="3" placeholder="Why nominate this person?"></textarea>
        </div>

        <div class="modal-actions">
          <button class="btn btn-grey" @click="showInviteModal = false">Cancel</button>
          <button class="btn btn-primary" @click="sendInvitation">Generate Invite Link</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.jp-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
  color: #333333;
}

.content {
  padding: 40px;
  max-width: 1200px;
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
  color: #333;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sub-caption {
  font-size: 14px;
  color: #dc3545;
  font-style: italic;
}

/* Tabs */
.jp-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #0056B3;
  border-bottom: 3px solid #0056B3;
  font-weight: bold;
}

/* Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.info-text {
  font-size: 13px;
  color: #777;
  margin-bottom: 20px;
  background: #F9F9F9;
  padding: 10px;
  border-left: 3px solid #999;
}

/* Tables */
.jp-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-top: 20px;
}

.jp-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 2px solid #e9ecef;
}

.jp-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  color: #333;
}

.jp-table tr:last-child td {
  border-bottom: none;
}

.jp-table tr:hover {
  background-color: #f8f9fa;
}

.bold-text { font-weight: bold; }

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 5px;
}
.status-dot.active { background: #2E7D32; }
.status-dot.removed { background: #dc3545; }

.status-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  text-transform: uppercase;
}
.status-badge.accepted { background: #E8F5E9; color: #2E7D32; }
.status-badge.pending { background: #FFF3E0; color: #EF6C00; }
.status-badge.revoked { background: #F5F5F5; color: #999; }

/* Permissions Grid */
.permission-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.perm-card {
  border: 1px solid #EEE;
  padding: 20px;
  background: #FAFAFA;
}

.perm-card h3 {
  margin-top: 0;
  font-size: 16px;
  color: #0056B3;
  border-bottom: 1px solid #DDD;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.perm-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.perm-card li {
  margin-bottom: 10px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
}

/* Actions */
.actions {
  display: flex;
  gap: 10px;
}

.btn-text {
  background: none;
  border: none;
  color: #555;
  cursor: pointer;
  text-decoration: underline;
  font-size: 12px;
}
.btn-text.text-danger { color: #dc3545; }
.btn-text:hover { color: #000; }

/* Buttons */
.btn-primary {
  background: #0056B3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary:hover {
  background: #004494;
}
.btn-grey { background: #EEE; color: #333; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-box {
  background: white;
  padding: 30px;
  width: 500px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.modal-box h3 { margin-top: 0; margin-bottom: 5px; color: #333; }
.modal-subtitle { font-size: 12px; color: #dc3545; margin-bottom: 20px; }

.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 12px; font-weight: bold; margin-bottom: 5px; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #CCC;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>