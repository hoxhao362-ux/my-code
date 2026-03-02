<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close'])

// Mock Reviewer Data (Blinded for Author)
const reviewers = computed(() => {
  if (!props.manuscript) return []
  
  // Logic: Only show if status implies reviewers are assigned
  const status = props.manuscript.status.toLowerCase()
  if (!status.includes('review') && !status.includes('decision')) {
    return [] // "Manuscript not yet in review process" handled by empty state or parent check
  }

  // Generate 2-3 mock reviewers
  return [
    {
      id: 1,
      label: 'Reviewer #1',
      status: 'Review Submitted',
      statusClass: 'completed',
      progress: 100
    },
    {
      id: 2,
      label: 'Reviewer #2',
      status: 'Review in Progress',
      statusClass: 'pending',
      progress: 60
    },
    {
      id: 3,
      label: 'Reviewer #3',
      status: 'Invited',
      statusClass: 'invited',
      progress: 20
    }
  ]
})
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <h3>Reviewer Management: {{ manuscript?.title }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-content">
        <div v-if="reviewers.length === 0" class="no-data">
          Manuscript not yet in review process.
        </div>
        
        <div v-else class="reviewer-table-container">
          <p class="blind-notice">
            <span class="icon">🔒</span> Double-Blind Review Process Active. Reviewer identities are hidden.
          </p>
          
          <table class="reviewer-table">
            <thead>
              <tr>
                <th>Reviewer</th>
                <th>Status</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reviewer in reviewers" :key="reviewer.id">
                <td class="reviewer-col">
                  <span class="avatar-placeholder">?</span>
                  {{ reviewer.label }}
                </td>
                <td>
                  <span class="status-tag" :class="reviewer.statusClass">{{ reviewer.status }}</span>
                </td>
                <td>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: reviewer.progress + '%' }" :class="reviewer.statusClass"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-outline" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  width: 600px;
  max-width: 90%;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-content {
  padding: 1.5rem;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.blind-notice {
  background: #e3f2fd;
  color: #0d47a1;
  padding: 0.8rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.reviewer-table {
  width: 100%;
  border-collapse: collapse;
}

.reviewer-table th, .reviewer-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.reviewer-table th {
  background: #f9f9f9;
  color: #666;
  font-weight: 600;
}

.reviewer-col {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-weight: bold;
  color: #333;
}

.avatar-placeholder {
  width: 30px;
  height: 30px;
  background: #eee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-weight: bold;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-tag.completed { background: #d4edda; color: #155724; }
.status-tag.pending { background: #fff3cd; color: #856404; }
.status-tag.invited { background: #d1ecf1; color: #0c5460; }

.progress-bar {
  width: 100px;
  height: 6px;
  background: #eee;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
}

.progress-fill.completed { background: #28a745; }
.progress-fill.pending { background: #ffc107; }
.progress-fill.invited { background: #17a2b8; }

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.btn-outline {
  background: white;
  border: 1px solid #ccc;
  color: #333;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
