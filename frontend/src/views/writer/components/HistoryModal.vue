<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close'])

// Mock History Data Generator
const historyLogs = computed(() => {
  if (!props.manuscript) return []
  
  const logs = [
    {
      date: '2026-02-20 14:30:00',
      operator: 'System',
      action: 'Status Update',
      notes: `Status changed to ${props.manuscript.status}`,
      type: 'info'
    },
    {
      date: '2026-02-18 09:15:00',
      operator: props.manuscript.writer || 'Author',
      action: 'Submission',
      notes: 'Manuscript submitted successfully.',
      type: 'success'
    }
  ]

  // Add mock intermediate steps based on status
  if (props.manuscript.status.includes('Review') || props.manuscript.status.includes('Decision')) {
    logs.splice(1, 0, {
      date: '2026-02-19 10:00:00',
      operator: 'Editor',
      action: 'Screening',
      notes: 'Initial screening passed.',
      type: 'success'
    })
  }

  if (props.manuscript.status.includes('Revision')) {
    logs.splice(0, 0, {
      date: '2026-02-21 11:20:00',
      operator: 'Editor',
      action: 'Decision',
      notes: 'Revision required based on reviewer comments.',
      type: 'warning'
    })
  }

  return logs
})
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <h3>Submission History: {{ manuscript?.title }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-content">
        <div v-if="historyLogs.length === 0" class="no-data">
          No operation history available.
        </div>
        
        <ul v-else class="history-list">
          <li v-for="(log, index) in historyLogs" :key="index" class="history-item">
            <div class="timeline-marker" :class="log.type"></div>
            <div class="log-content">
              <div class="log-header">
                <span class="log-action">{{ log.action }}</span>
                <span class="log-date">{{ log.date }}</span>
              </div>
              <div class="log-meta">
                Operator: {{ log.operator }}
              </div>
              <div class="log-notes">
                {{ log.notes }}
              </div>
            </div>
          </li>
        </ul>
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
  max-height: 80vh;
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
  overflow-y: auto;
  flex: 1;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 2rem;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
}

/* Vertical Line */
.history-list::before {
  content: '';
  position: absolute;
  left: 14px; /* Align with marker center */
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: #eee;
}

.history-item {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc;
  z-index: 1;
  margin-top: 6px;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #eee;
  flex-shrink: 0;
  margin-left: 7px; /* Center on line */
}

.timeline-marker.success { background: #28a745; box-shadow: 0 0 0 2px #d4edda; }
.timeline-marker.warning { background: #ffc107; box-shadow: 0 0 0 2px #fff3cd; }
.timeline-marker.info { background: #17a2b8; box-shadow: 0 0 0 2px #d1ecf1; }

.log-content {
  flex: 1;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #eee;
}

.log-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.log-action {
  font-weight: bold;
  color: #333;
}

.log-date {
  font-size: 0.85rem;
  color: #999;
}

.log-meta {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.log-notes {
  font-size: 0.9rem;
  color: #444;
  line-height: 1.4;
}

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
