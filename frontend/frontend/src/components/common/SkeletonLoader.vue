<template>
  <div v-if="loading" class="skeleton-wrapper" :class="customClass">
    <div 
      v-for="n in count" 
      :key="n" 
      class="skeleton-item" 
      :style="{ height: height, width: width, marginBottom: gap }"
    ></div>
  </div>
  <slot v-else></slot>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    default: true
  },
  count: {
    type: Number,
    default: 3
  },
  height: {
    type: String,
    default: '20px'
  },
  width: {
    type: String,
    default: '100%'
  },
  gap: {
    type: String,
    default: '10px'
  },
  customClass: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}
.skeleton-item {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}
@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
