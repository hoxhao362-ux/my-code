<template>
  <div class="loader-wrapper" :class="{ 'full-screen': fullScreen, 'overlay': overlay }">
    <div class="loader-content">
      <div class="spinner" :class="size">
        <div class="double-bounce1"></div>
        <div class="double-bounce2"></div>
      </div>
      <p v-if="text" class="loader-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: 'Loading...'
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (val) => ['small', 'medium', 'large'].includes(val)
  },
  fullScreen: {
    type: Boolean,
    default: false
  },
  overlay: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.loader-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  width: 100%;
}

.loader-wrapper.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #f8f9fa;
  z-index: 9999;
}

.loader-wrapper.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
  backdrop-filter: blur(2px);
}

.loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loader-text {
  color: #3498db;
  font-weight: 500;
  font-size: 0.95rem;
  margin: 0;
  letter-spacing: 0.5px;
  animation: pulse 1.5s ease-in-out infinite;
}

/* Spinner Animation */
.spinner {
  position: relative;
}

.spinner.small { width: 30px; height: 30px; }
.spinner.medium { width: 50px; height: 50px; }
.spinner.large { width: 70px; height: 70px; }

.double-bounce1, .double-bounce2 {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #3498db;
  opacity: 0.6;
  position: absolute;
  top: 0;
  left: 0;
  animation: sk-bounce 2.0s infinite ease-in-out;
}

.double-bounce2 {
  animation-delay: -1.0s;
}

@keyframes sk-bounce {
  0%, 100% { 
    transform: scale(0.0);
  } 50% { 
    transform: scale(1.0);
  }
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>