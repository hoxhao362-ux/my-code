<template>
  <div v-if="count > 0" class="notification-badge" :class="{ 'pulse': count > 0 }">
    {{ displayCount }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  count: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 99
  }
})

const displayCount = computed(() => {
  return props.count > props.max ? `${props.max}+` : props.count
})
</script>

<style scoped>
.notification-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #C93737;
  color: white;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: bold;
  line-height: 1;
  position: absolute;
  top: -5px;
  right: -10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  z-index: 10;
}

.pulse {
  animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
  0% { box-shadow: 0 0 0 0 rgba(201, 55, 55, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(201, 55, 55, 0); }
  100% { box-shadow: 0 0 0 0 rgba(201, 55, 55, 0); }
}
</style>
