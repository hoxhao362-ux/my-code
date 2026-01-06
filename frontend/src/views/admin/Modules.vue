<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 模块列表
const modules = computed(() => userStore.modules)

// 新模块输入
const newModule = ref('')
const errorMessage = ref('')

// 添加新模块
const addModule = () => {
  if (!newModule.value.trim()) {
    errorMessage.value = '请输入模块名称'
    return
  }
  
  if (modules.value.includes(newModule.value)) {
    errorMessage.value = '模块已存在'
    return
  }
  
  userStore.addModule(newModule.value)
  newModule.value = ''
  errorMessage.value = ''
}

// 删除模块
const removeModule = (moduleName) => {
  userStore.removeModule(moduleName)
}
</script>

<template>
  <div class="admin-modules-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-modules'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 模块管理内容 -->
    <main class="content">
      <div class="header">
        <h1>模块管理</h1>
      </div>

      <section class="modules-section">
        <!-- 添加新模块 -->
        <div class="add-module-form">
          <h2>添加新模块</h2>
          <div class="form-group">
            <input 
              type="text" 
              v-model="newModule"
              placeholder="请输入模块名称"
              class="module-input"
            />
            <button class="add-btn" @click="addModule">+ 添加模块</button>
          </div>
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>

        <!-- 模块列表 -->
        <div class="modules-list">
          <h2>现有模块</h2>
          <div class="modules-grid">
            <div 
              v-for="module in modules" 
              :key="module" 
              class="module-card"
            >
              <div class="module-info">
                <span class="module-name">{{ module }}</span>
              </div>
              <div class="module-actions">
                <button 
                  class="delete-btn" 
                  @click="removeModule(module)"
                  :disabled="module === '其他'"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 样式可以从原组件复制或修改 */
</style>