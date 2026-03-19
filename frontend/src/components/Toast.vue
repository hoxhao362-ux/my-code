<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        class="toast-message"
        :class="['toast-' + toast.type]"
      >
        <div class="toast-content">
          <span class="toast-icon" v-if="toast.type === 'success'">✓</span>
          <span class="toast-icon" v-else-if="toast.type === 'error'">✕</span>
          <span class="toast-icon" v-else-if="toast.type === 'warning'">!</span>
          <span class="toast-text">{{ toast.message }}</span>
        </div>
        <button class="toast-close" @click="store.remove(toast.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from '../stores/toast'
import { computed } from 'vue'

const store = useToastStore()
const toasts = computed(() => store.toasts)
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none; /* Allow clicking through container */
}

.toast-message {
  pointer-events: auto; /* Enable clicks on toasts */
  min-width: 300px;
  max-width: 400px;
  padding: 12px 16px;
  border-radius: 4px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  line-height: 1.4;
  border-left: 4px solid #333;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toast-icon {
  font-weight: bold;
  font-size: 16px;
}

.toast-success {
  border-left-color: var(--color-success);
}
.toast-success .toast-icon {
  color: var(--color-success);
}

.toast-error {
  border-left-color: var(--color-primary); /* Peerex Peer Red for errors */
}
.toast-error .toast-icon {
  color: var(--color-primary);
}

.toast-warning {
  border-left-color: #FF9800; /* Keep orange for warning distinct from error */
}
.toast-warning .toast-icon {
  color: #FF9800;
}

.toast-info {
  border-left-color: var(--color-info);
}
.toast-info .toast-icon {
  color: var(--color-info);
}

.toast-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
  padding: 0 0 0 12px;
  line-height: 1;
}

.toast-close:hover {
  color: #333;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
