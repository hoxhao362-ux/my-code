<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToastStore } from '../../stores/toast'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

// State
const inviteToken = ref('')
const roleType = ref('') // editor, associate_editor, assistant, advisory
const isValid = ref(true)
const isSubmitted = ref(false)

// Form Data
const form = ref({
  name: '',
  email: '', // Pre-filled from invite
  institution: '',
  title: '', // Professor, etc.
  field: '',
  orcid: '',
  experience: '', // Text area for experience
  conflictInterest: false,
  confidentiality: false,
  signature: ''
})

// Mock Validation
onMounted(() => {
  inviteToken.value = route.query.token
  roleType.value = route.query.role || 'associate_editor'
  
  if (!inviteToken.value) {
    isValid.value = false
  } else {
    // Mock pre-fill
    form.value.email = 'invited.user@institution.edu'
  }
})

const handleSubmit = () => {
  if (!form.value.conflictInterest || !form.value.confidentiality || !form.value.signature) {
    toastStore.add({ message: 'Please agree to all terms and sign the confidentiality agreement.', type: 'warning' })
    return
  }
  
  console.log('Submitting registration:', form.value)
  isSubmitted.value = true
}

const getRoleName = (role) => {
  const map = {
    'editor': 'Editorial Board Member (Editor)',
    'associate_editor': 'Associate Editor',
    'assistant': 'EA/AE',
    'advisory': 'EA/AE'
  }
  return map[role] || role
}

</script>

<template>
  <div class="register-container">
    <div class="register-card" v-if="isValid && !isSubmitted">
      <div class="header">
        <h1>Official Appointment Registration</h1>
        <p class="role-badge">Invited Role: {{ getRoleName(roleType) }}</p>
        <p class="subtitle">Please complete your profile to activate your official appointment.</p>
      </div>

      <form @submit.prevent="handleSubmit" class="jp-form">
        <!-- Section 1: Identity -->
        <div class="form-section">
          <h3>1. Identity Verification</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Full Name</label>
              <input v-model="form.name" required placeholder="Official Name">
            </div>
            <div class="form-group">
              <label>Institutional Email</label>
              <input v-model="form.email" disabled class="disabled-input">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Institution</label>
              <input v-model="form.institution" required placeholder="University / Institute">
            </div>
            <div class="form-group">
              <label>Academic Title</label>
              <input v-model="form.title" required placeholder="e.g. Professor, Director">
            </div>
          </div>
          <div class="form-group">
            <label>ORCID iD</label>
            <input v-model="form.orcid" placeholder="0000-0000-0000-0000">
          </div>
        </div>

        <!-- Section 2: Professional (For Editors/AE/EA) -->
        <div class="form-section" v-if="['editor', 'associate_editor', 'ea_ae'].includes(roleType)">
          <h3>2. Academic Profile</h3>
          <div class="form-group">
            <label>Research Fields (Keywords)</label>
            <input v-model="form.field" required placeholder="e.g. Oncology, Immunology">
          </div>
          <div class="form-group">
            <label>Editorial & Review Experience</label>
            <textarea v-model="form.experience" rows="3" placeholder="List relevant journals and roles..."></textarea>
          </div>
        </div>

        <!-- Section 3: Legal & Ethics -->
        <div class="form-section">
          <h3>3. Legal & Ethics Declaration</h3>
          
          <div class="checkbox-group">
            <label>
              <input type="checkbox" v-model="form.conflictInterest" required>
              I declare that I have no undeclared Conflicts of Interest (COI) that would affect my impartiality.
            </label>
          </div>

          <div class="checkbox-group">
            <label>
              <input type="checkbox" v-model="form.confidentiality" required>
              I agree to the Confidentiality Agreement. All manuscripts and internal discussions are strictly confidential.
            </label>
          </div>

          <div class="form-group signature-group">
            <label>Electronic Signature (Type Full Name)</label>
            <input v-model="form.signature" required placeholder="I, [Name], agree to the above terms.">
            <p class="legal-note">By typing your name, you execute a binding electronic signature.</p>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-submit">Submit for Board Review</button>
        </div>
      </form>
    </div>

    <!-- Success State -->
    <div class="register-card success" v-else-if="isSubmitted">
      <div class="success-icon">✓</div>
      <h2>Registration Submitted</h2>
      <p>Your materials have been sent to the Editorial Board for final review.</p>
      <p>Once approved (usually 1-3 business days), you will receive an activation email with your login credentials.</p>
      <button class="btn-home" @click="router.push('/')">Return to Home</button>
    </div>

    <!-- Invalid Token -->
    <div class="register-card error" v-else>
      <h2>Invalid or Expired Invitation</h2>
      <p>This invitation link is invalid or has expired.</p>
      <p>Please contact the Editorial Office to request a new invitation.</p>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #F5F7FA;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.register-card {
  background: white;
  width: 100%;
  max-width: 700px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border-top: 5px solid #0056B3;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #EEE;
  padding-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.role-badge {
  display: inline-block;
  background: #FFF3E0;
  color: #E65100;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 10px;
  font-family: Arial, sans-serif;
}

.subtitle {
  color: #666;
  font-style: italic;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  font-size: 16px;
  font-weight: bold;
  color: #0056B3;
  border-bottom: 1px solid #EEE;
  padding-bottom: 8px;
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
  flex: 1;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: bold;
  color: #555;
  margin-bottom: 5px;
}

input, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #CCC;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
}

.disabled-input {
  background: #F9F9F9;
  color: #999;
}

.checkbox-group {
  margin-bottom: 10px;
}

.checkbox-group label {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  font-size: 14px;
  cursor: pointer;
}

.signature-group {
  margin-top: 20px;
  background: #FAFAFA;
  padding: 15px;
  border: 1px dashed #CCC;
}

.legal-note {
  font-size: 11px;
  color: #999;
  margin-top: 5px;
}

.btn-submit {
  background: #0056B3;
  color: white;
  border: none;
  padding: 14px 40px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-submit:hover {
  background: #004494;
}

/* Success State */
.success {
  text-align: center;
  padding: 60px 40px;
}

.success-icon {
  font-size: 50px;
  color: #2E7D32;
  margin-bottom: 20px;
}

.btn-home {
  margin-top: 20px;
  padding: 10px 20px;
  background: #EEE;
  border: none;
  cursor: pointer;
}

/* Error State */
.error {
  text-align: center;
  border-top-color: #999;
}
</style>