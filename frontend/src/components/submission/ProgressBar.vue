<script setup>
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'

const store = useSubmissionStore()
const { t } = useI18n()
</script>

<template>
  <div class="progress-bar-container">
    <div class="progress-steps">
      <div 
        v-for="(step, index) in store.steps" 
        :key="step.id"
        class="step-item"
        :class="[step.status]"
        @click="store.goToStep(step.id)"
      >
        <div class="step-icon">
          <span v-if="step.status === 'completed'" class="icon">✓</span>
          <span v-else-if="step.status === 'current'" class="icon">⬇</span>
          <span v-else-if="step.status === 'error'" class="icon">!</span>
          <span v-else class="icon">{{ step.id }}</span>
        </div>
        <div class="step-label">{{ t(step.name) }}</div>
        <div v-if="index < store.steps.length - 1" class="step-line" :class="{ 'completed': step.status === 'completed' }"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.progress-bar-container {
  margin-bottom: 2rem;
  padding: 1rem 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  cursor: pointer;
}

.step-item.completed { cursor: pointer; }
.step-item.current { cursor: default; }
.step-item.error { cursor: pointer; }
.step-item.pending { cursor: pointer; }

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #ddd;
  background: white;
  z-index: 2;
  transition: all 0.3s ease;
  font-weight: bold;
  font-size: 14px;
}

.step-label {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  text-align: center;
}

/* Styles per status */
.step-item.completed .step-icon {
  border-color: #2ecc71;
  background: #2ecc71;
  color: white;
}
.step-item.completed .step-label { color: #2ecc71; }

.step-item.current .step-icon {
  border-color: #3498db;
  color: #3498db;
}
.step-item.current .step-label { color: #3498db; font-weight: bold; }

.step-item.error .step-icon {
  border-color: #e74c3c;
  background: #e74c3c;
  color: white;
}
.step-item.error .step-label { color: #e74c3c; }

.step-item.pending .step-icon {
  border-color: #ccc;
  color: #ccc;
}

/* Connecting lines */
.step-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #eee;
  z-index: 1;
}

.step-line.completed {
  background: #2ecc71;
}
</style>
