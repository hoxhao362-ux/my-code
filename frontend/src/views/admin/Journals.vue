<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 所有期刊
const journals = computed(() => userStore.journals)
</script>

<template>
  <div class="admin-journals-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-journals'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 期刊管理内容 -->
    <main class="content">
      <div class="header">
        <h1>期刊管理</h1>
      </div>

      <section class="journals-section">
        <div class="journals-table-container">
          <table class="journals-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>标题</th>
                <th>作者</th>
                <th>模块</th>
                <th>状态</th>
                <th>投稿日期</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="journal in journals" :key="journal.id">
                <td>{{ journal.id }}</td>
                <td>{{ journal.title }}</td>
                <td>{{ journal.author }}</td>
                <td>{{ journal.module }}</td>
                <td>
                  <span class="status-tag" :class="journal.status.toLowerCase()">
                    {{ journal.status }}
                  </span>
                </td>
                <td>{{ journal.date }}</td>
                <td>
                  <button class="action-btn view-btn">查看</button>
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