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
        <!-- 通知项示例 -->
        <div class="notification-item">
          <div class="notification-header">
            <div class="notification-title">稿件审核结果通知</div>
            <div class="notification-time">2024-01-15 14:30</div>
          </div>
          <div class="notification-content">
            您的稿件《基于深度学习的图像识别技术研究》已通过初审，请查看详情。
          </div>
          <div class="notification-actions">
            <button class="action-button">查看详情</button>
          </div>
        </div>
        
        <div class="notification-item">
          <div class="notification-header">
            <div class="notification-title">系统更新通知</div>
            <div class="notification-time">2024-01-10 09:00</div>
          </div>
          <div class="notification-content">
            期刊投稿平台已完成系统更新，新增了稿件进度实时查询功能。
          </div>
          <div class="notification-actions">
            <button class="action-button">了解更多</button>
          </div>
        </div>
        
        <div class="notification-item">
          <div class="notification-header">
            <div class="notification-title">审稿意见反馈</div>
            <div class="notification-time">2024-01-05 16:45</div>
          </div>
          <div class="notification-content">
            您的稿件《基于深度学习的图像识别技术研究》需要进行修改，请查看详细修改意见。
          </div>
          <div class="notification-actions">
            <button class="action-button">查看修改意见</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

const goBack = () => {
  router.back()
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