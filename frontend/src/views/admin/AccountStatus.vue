<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 使用userStore中的用户数据
const users = computed(() => userStore.users)

// 重置密码
const resetPassword = (id) => {
  if (confirm('确定要重置该用户的密码吗？')) {
    // 这里可以添加重置密码的逻辑
    alert('密码重置成功！新密码为：123456')
  }
}

// 切换账号状态
const toggleUserStatus = (id) => {
  const user = userStore.users.find(u => u.id === id)
  if (user) {
    // 计算新状态
    const newStatus = user.status === 'active' ? 'inactive' : 'active'
    // 使用userStore更新状态，确保持久化
    userStore.updateUserStatus(id, newStatus)
    alert(`用户 ${user.username} 的状态已切换为 ${newStatus === 'active' ? '启用' : '禁用'}`)
  }
}
</script>

<template>
  <div class="admin-account-status-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-account-status'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />

    <!-- 账号状态管理内容 -->
    <main class="content">
      <div class="header">
        <h1>账号状态管理</h1>
      </div>

      <section class="account-status-section">
        <div class="users-table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>邮箱</th>
                <th>手机号</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone }}</td>
                <td>
                  <span class="status-badge" :class="user.status">
                    {{ user.status === 'active' ? '启用' : '禁用' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="action-btn status-btn" 
                    @click="toggleUserStatus(user.id)"
                  >
                    {{ user.status === 'active' ? '禁用' : '启用' }}
                  </button>
                  <button 
                    class="action-btn reset-btn" 
                    @click="resetPassword(user.id)"
                  >
                    重置密码
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
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
.admin-account-status-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

/* 账号状态管理样式 */
.account-status-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.users-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
}

.users-table tbody tr:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

/* 状态标签样式 */
.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

/* 操作按钮样式 */
.action-btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  margin-right: 0.5rem;
  transition: all 0.3s ease;
}

.status-btn {
  background-color: #ff9800;
  color: white;
}

.status-btn:hover {
  background-color: #f57c00;
  transform: translateY(-1px);
}

.reset-btn {
  background-color: #9c27b0;
  color: white;
}

.reset-btn:hover {
  background-color: #7b1fa2;
  transform: translateY(-1px);
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
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th,
  .users-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .action-btn {
    padding: 0.5rem 0.8rem;
    font-size: 0.8rem;
    margin-right: 0.25rem;
  }
}
</style>