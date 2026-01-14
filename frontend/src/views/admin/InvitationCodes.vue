<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 本地临时存储邀请码数据
const invitationCodes = ref({
  admin: 'ADMIN2026',
  reviewer: 'REVIEWER2026'
})

// 页面加载时从store获取最新邀请码
onMounted(() => {
  invitationCodes.value = { ...userStore.invitationCodes }
})

// 保存配置
const saveCodes = () => {
  // 保存到store，持久化到localStorage
  userStore.updateAllInvitationCodes(invitationCodes.value)
  alert('邀请码已保存！')
}

// 生成随机邀请码
const generateCode = (type) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let result = ''
  for (let i = 0; i < 10; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  const newCode = result.toUpperCase()
  // 只更新本地临时数据，不自动保存到store
  invitationCodes.value[type] = newCode
}
</script>

<template>
  <div class="admin-invitation-codes-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-invitation-codes'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 邀请码管理内容 -->
    <main class="content">
      <div class="header">
        <h1>邀请码管理</h1>
        <p class="subtitle">管理管理员和审核员的邀请码</p>
      </div>

      <section class="codes-section">
        <div class="codes-form-container">
          <form class="codes-form">
            <div class="form-section">
              <h3>邀请码设置</h3>
              
              <div class="code-group">
                <div class="code-info">
                  <h4>管理员邀请码</h4>
                  <p>用于邀请新管理员注册</p>
                </div>
                <div class="code-input-group">
                  <input 
                    type="text" 
                    v-model="invitationCodes.admin" 
                    class="code-input"
                    placeholder="管理员邀请码"
                  >
                  <button type="button" class="generate-btn" @click="generateCode('admin')">生成随机码</button>
                </div>
              </div>
              
              <div class="code-group">
                <div class="code-info">
                  <h4>审核员邀请码</h4>
                  <p>用于邀请新审核员注册</p>
                </div>
                <div class="code-input-group">
                  <input 
                    type="text" 
                    v-model="invitationCodes.reviewer" 
                    class="code-input"
                    placeholder="审核员邀请码"
                  >
                  <button type="button" class="generate-btn" @click="generateCode('reviewer')">生成随机码</button>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-save" @click="saveCodes">保存邀请码</button>
            </div>
          </form>
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
.admin-invitation-codes-container {
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

.subtitle {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 邀请码区域样式 */
.codes-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

.codes-form-container {
  max-width: 800px;
}

/* 表单样式 */
.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

/* 邀请码组样式 */
.code-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  gap: 2rem;
}

.code-info h4 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.code-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.code-input-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.code-input {
  padding: 0.9rem 1.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  min-width: 250px;
  transition: all 0.3s ease;
}

.code-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 按钮样式 */
.generate-btn {
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

.generate-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-save {
  background-color: #2ecc71;
  color: white;
}

.btn-save:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
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
  
  .codes-section {
    padding: 1.5rem;
  }
  
  .code-group {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .code-input-group {
    flex-direction: column;
  }
  
  .code-input {
    min-width: auto;
    width: 100%;
  }
  
  .generate-btn {
    width: 100%;
    min-width: auto;
  }
  
  .form-actions {
    justify-content: stretch;
  }
  
  .btn {
    width: 100%;
  }
}
</style>