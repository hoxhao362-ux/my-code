<template>
  <div class="empty-state-wrapper">
    <div class="empty-state-content">
      <div class="empty-icon">
        <slot name="icon">
          <!-- 默认图标 -->
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="default-icon">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </slot>
      </div>
      <h3 class="empty-title">{{ title }}</h3>
      <p class="empty-description" v-if="description">{{ description }}</p>
      <div class="empty-actions" v-if="$slots.action || actionText">
        <slot name="action">
          <button v-if="actionText" class="btn btn-primary" @click="$emit('action-click')">
            {{ actionText }}
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: 'No Data Available'
  },
  description: {
    type: String,
    default: ''
  },
  actionText: {
    type: String,
    default: ''
  }
})

defineEmits(['action-click'])
</script>

<style scoped>
.empty-state-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 2rem;
  width: 100%;
  height: 100%;
  min-height: 300px;
  background-color: transparent;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  margin-bottom: 1.5rem;
  color: #bdc3c7;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: float 3s ease-in-out infinite;
}

.default-icon {
  color: #cbd5e1;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.empty-description {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.empty-actions {
  margin-top: 1rem;
}

.btn {
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.2);
}

.btn-primary:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}
</style>