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
/* 主容器样式 */
.admin-modules-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

/* 模块管理区域样式 */
.modules-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 添加模块表单样式 */
.add-module-form {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
}

.add-module-form h2,
.modules-list h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.form-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.module-input {
  flex: 1;
  padding: 0.9rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
  min-width: 250px;
}

.module-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.add-btn {
  padding: 0.9rem 1.5rem;
  border: none;
  background-color: #3498db;
  color: white;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.error-message {
  color: #e74c3c;
  margin-top: 0.75rem;
  font-size: 0.9rem;
  margin-left: 0;
}

/* 模块列表样式 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.module-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

.module-info {
  flex: 1;
}

.module-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.module-actions {
  display: flex;
  gap: 0.5rem;
}

.delete-btn {
  padding: 0.6rem 1.2rem;
  border: 1px solid #e74c3c;
  background-color: white;
  color: #e74c3c;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background-color: #e74c3c;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(231, 76, 60, 0.2);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ccc;
  color: #999;
}

/* 页脚样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.footer-content p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .modules-section {
    padding: 1.5rem;
  }
  
  .add-module-form h2,
  .modules-list h2 {
    font-size: 1.1rem;
  }
  
  .form-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .module-input {
    min-width: auto;
  }
  
  .add-btn {
    width: 100%;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .module-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .module-actions {
    justify-content: flex-end;
  }
}
</style>