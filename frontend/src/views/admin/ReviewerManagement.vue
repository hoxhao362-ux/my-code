<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 模拟审核员数据
const reviewers = ref([
  { id: 2, username: 'reviewer1', role: 'reviewer', email: 'reviewer1@example.com', phone: '13800138001' },
  { id: 6, username: 'reviewer2', role: 'reviewer', email: 'reviewer2@example.com', phone: '13800138005' },
  { id: 7, username: 'reviewer3', role: 'reviewer', email: 'reviewer3@example.com', phone: '13800138006' }
])

// 新增审核员表单
const showAddForm = ref(false)
const newReviewer = ref({
  username: '',
  email: '',
  phone: ''
})

// 添加审核员
const addReviewer = () => {
  if (!newReviewer.value.username) return
  
  const id = Math.max(...reviewers.value.map(r => r.id), 0) + 1
  reviewers.value.push({
    id,
    username: newReviewer.value.username,
    role: 'reviewer',
    email: newReviewer.value.email,
    phone: newReviewer.value.phone
  })
  
  // 重置表单
  newReviewer.value = {
    username: '',
    email: '',
    phone: ''
  }
  showAddForm.value = false
}

// 删除审核员
const deleteReviewer = (id) => {
  reviewers.value = reviewers.value.filter(reviewer => reviewer.id !== id)
}
</script>

<template>
  <div class="admin-reviewer-management-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-reviewer-management'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 审核员管理内容 -->
    <main class="content">
      <div class="header">
        <h1>审核员管理</h1>
        <button class="add-btn" @click="showAddForm = !showAddForm">
          {{ showAddForm ? '取消' : '新增审核员' }}
        </button>
      </div>

      <!-- 新增审核员表单 -->
      <section v-if="showAddForm" class="add-reviewer-section">
        <div class="form-container">
          <h2>新增审核员</h2>
          <form @submit.prevent="addReviewer">
            <div class="form-group">
              <label for="username">用户名</label>
              <input 
                type="text" 
                id="username" 
                v-model="newReviewer.username" 
                placeholder="请输入用户名"
                required
              >
            </div>
            <div class="form-group">
              <label for="email">邮箱</label>
              <input 
                type="email" 
                id="email" 
                v-model="newReviewer.email" 
                placeholder="请输入邮箱"
              >
            </div>
            <div class="form-group">
              <label for="phone">手机号</label>
              <input 
                type="tel" 
                id="phone" 
                v-model="newReviewer.phone" 
                placeholder="请输入手机号"
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="submit-btn">添加审核员</button>
              <button type="button" class="cancel-btn" @click="showAddForm = false">取消</button>
            </div>
          </form>
        </div>
      </section>

      <!-- 审核员列表 -->
      <section class="reviewers-section">
        <div class="reviewers-table-container">
          <table class="reviewers-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>邮箱</th>
                <th>手机号</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reviewer in reviewers" :key="reviewer.id">
                <td>{{ reviewer.id }}</td>
                <td>{{ reviewer.username }}</td>
                <td>{{ reviewer.role }}</td>
                <td>{{ reviewer.email }}</td>
                <td>{{ reviewer.phone }}</td>
                <td>
                  <button class="action-btn edit-btn">编辑</button>
                  <button class="action-btn delete-btn" @click="deleteReviewer(reviewer.id)">删除</button>
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
.admin-reviewer-management-container {
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

.add-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-btn:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

/* 新增审核员表单样式 */
.add-reviewer-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.form-container h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: flex-end;
}

.submit-btn {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.9rem 1.8rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.cancel-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.9rem 1.8rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 审核员列表样式 */
.reviewers-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.reviewers-table-container {
  overflow-x: auto;
}

.reviewers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.reviewers-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
}

.reviewers-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
}

.reviewers-table tbody tr:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

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

.edit-btn {
  background-color: #3498db;
  color: white;
}

.edit-btn:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background-color: #c0392b;
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
  
  .reviewers-table {
    font-size: 0.85rem;
  }
  
  .reviewers-table th,
  .reviewers-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .action-btn {
    padding: 0.5rem 0.8rem;
    font-size: 0.8rem;
    margin-right: 0.25rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>