<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

// 应用初始化
onMounted(() => {
  const userStore = useUserStore()
  // 刷新期刊数据，确保从localStorage获取最新数据
  userStore.refreshJournals()
  // 加载反馈消息
  userStore.loadFeedbackMessages()
})
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>