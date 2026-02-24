<template>
  <div class="notifications-container">
    <h2 class="page-title">消息通知</h2>
    <div class="back-button-container" v-if="!embedded">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="notifications-content">
      <div class="notification-list">
        <div v-if="notifications.length === 0" class="no-notifications">
          暂无消息通知
        </div>
        <div v-for="notification in notifications" :key="notification.id" class="notification-item">
          <div class="notification-header">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-time">{{ formatDate(notification.createdAt) }}</div>
          </div>
          <div class="notification-content">
            {{ notification.content }}
          </div>
          <div class="notification-actions" v-if="notification.actionLabel">
            <button class="action-button" @click="notification.action && notification.action()">{{ notification.actionLabel }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

const notifications = computed(() => {
  // Simple filter: show all for now, or filter by user if needed
  // In a real app, the backend would filter this.
  // For this mock, we can filter by targetUser if present
  const currentUser = userStore.user?.username
  const currentRole = userStore.user?.role
  
  return userStore.notifications.filter(n => {
    // If no target specified, show to everyone (or admin)
    if (!n.targetUser && !n.targetRole) return true
    
    // Check target user
    if (n.targetUser && n.targetUser === currentUser) return true
    
    // Check target role
    if (n.targetRole && n.targetRole === currentRole) return true
    
    return false
  })
})

const goBack = () => {
  router.back()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.notifications-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: #333;
}

.back-button-container {
  margin-bottom: 2rem;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.back-arrow {
  font-weight: bold;
}

.notifications-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-item {
  padding: 1.2rem;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: box-shadow 0.3s ease;
}

.notification-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.notification-title {
  font-weight: bold;
  color: #333;
  font-size: 1rem;
}

.notification-time {
  font-size: 0.8rem;
  color: #666;
}

.notification-content {
  color: #555;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  justify-content: flex-end;
}

.action-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #2980b9;
}
</style>