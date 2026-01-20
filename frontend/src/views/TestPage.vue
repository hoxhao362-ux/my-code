<template>
  <div class="test-page">
    <h1>测试页面</h1>
    <p>这是一个测试页面，用于检查应用是否能正常显示内容。</p>
  </div>
</template>

<script setup>
// 测试页面组件
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  color: #333;
  padding: 2rem;
}

h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

p {
  font-size: 1.2rem;
  color: #7f8c8d;
}
</style>