<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 模拟用户数据
const users = ref([
  { id: 1, username: 'admin', role: 'admin', email: 'admin@example.com', phone: '13800138000' },
  { id: 2, username: 'reviewer1', role: 'reviewer', email: 'reviewer1@example.com', phone: '13800138001' },
  { id: 3, username: 'author1', role: 'author', email: 'author1@example.com', phone: '13800138002' },
  { id: 4, username: 'user1', role: 'user', email: 'user1@example.com', phone: '13800138003' },
  { id: 5, username: 'user2', role: 'user', email: 'user2@example.com', phone: '13800138004' }
])
</script>

<template>
  <div class="admin-users-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-users'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 用户管理内容 -->
    <main class="content">
      <div class="header">
        <h1>用户管理</h1>
      </div>

      <section class="users-section">
        <div class="users-table-container">
          <table class="users-table">
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
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone }}</td>
                <td>
                  <button class="action-btn edit-btn">编辑</button>
                  <button class="action-btn delete-btn">删除</button>
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
/* 样式可以从原组件复制或修改 */
</style>