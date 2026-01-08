<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 日志类型
const logTypes = [
  { value: 'all', label: '全部日志' },
  { value: 'login', label: '登录日志' },
  { value: 'operation', label: '操作日志' },
  { value: 'error', label: '错误日志' }
]

// 日志数据 - 模拟数据
const logsData = ref([
  { id: 1, type: 'login', action: '登录成功', target: '', time: '2026-01-08 17:30:45', ip: '127.0.0.1', status: 'success' },
  { id: 2, type: 'operation', action: '修改用户角色', target: 'user1', time: '2026-01-08 17:25:30', ip: '127.0.0.1', status: 'success' },
  { id: 3, type: 'operation', action: '禁用用户', target: 'user2', time: '2026-01-08 17:20:15', ip: '127.0.0.1', status: 'success' },
  { id: 4, type: 'operation', action: '添加审核员', target: 'reviewer4', time: '2026-01-08 17:15:00', ip: '127.0.0.1', status: 'success' },
  { id: 5, type: 'operation', action: '修改投稿规则', target: '', time: '2026-01-08 17:10:45', ip: '127.0.0.1', status: 'success' },
  { id: 6, type: 'login', action: '登录失败', target: '', time: '2026-01-08 17:05:30', ip: '192.168.1.100', status: 'failed' },
  { id: 7, type: 'operation', action: '查看用户列表', target: '', time: '2026-01-08 17:00:15', ip: '127.0.0.1', status: 'success' },
  { id: 8, type: 'operation', action: '编辑用户信息', target: 'user3', time: '2026-01-08 16:55:00', ip: '127.0.0.1', status: 'success' },
  { id: 9, type: 'error', action: '权限不足', target: '/admin/system', time: '2026-01-08 16:50:45', ip: '192.168.1.101', status: 'error' },
  { id: 10, type: 'operation', action: '修改密码', target: '', time: '2026-01-08 16:45:30', ip: '127.0.0.1', status: 'success' }
])

// 日志过滤条件
const logFilters = ref({
  type: 'all',
  keyword: '',
  startDate: '',
  endDate: ''
})

// 分页设置
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: computed(() => filteredLogs.value.length)
})

// 计算过滤后的日志
const filteredLogs = computed(() => {
  return logsData.value.filter(log => {
    // 类型过滤
    const matchesType = logFilters.value.type === 'all' || log.type === logFilters.value.type
    
    // 关键词过滤
    const matchesKeyword = !logFilters.value.keyword || 
      log.action.toLowerCase().includes(logFilters.value.keyword.toLowerCase()) ||
      log.target.toLowerCase().includes(logFilters.value.keyword.toLowerCase()) ||
      log.ip.includes(logFilters.value.keyword)
    
    // 日期过滤
    const logDate = new Date(log.time)
    const startDate = logFilters.value.startDate ? new Date(logFilters.value.startDate) : null
    const endDate = logFilters.value.endDate ? new Date(logFilters.value.endDate) : null
    
    let matchesDate = true
    if (startDate && endDate) {
      matchesDate = logDate >= startDate && logDate <= endDate
    } else if (startDate) {
      matchesDate = logDate >= startDate
    } else if (endDate) {
      matchesDate = logDate <= endDate
    }
    
    return matchesType && matchesKeyword && matchesDate
  })
})

// 计算分页后的日志
const paginatedLogs = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredLogs.value.slice(start, end)
})

// 导出日志
const exportLogs = () => {
  // 这里应该实现日志导出功能，目前模拟导出
  alert('日志导出功能已触发！')
}

// 清空日志
const clearLogs = () => {
  if (confirm('确定要清空所有日志吗？此操作不可恢复！')) {
    logsData.value = []
    alert('日志已清空！')
  }
}

// 切换日志类型
const changeLogType = (type) => {
  logFilters.value.type = type
  pagination.value.currentPage = 1
}

// 重置筛选条件
const resetFilters = () => {
  logFilters.value = {
    type: 'all',
    keyword: '',
    startDate: '',
    endDate: ''
  }
  pagination.value.currentPage = 1
}

// 获取日志类型名称
const getLogTypeName = (type) => {
  const typeMap = {
    'operation': '操作日志',
    'login': '登录日志',
    'error': '错误日志'
  }
  return typeMap[type] || type
}

// 获取状态样式
const getStatusClass = (status) => {
  const statusMap = {
    'success': 'success',
    'failed': 'failed',
    'error': 'error'
  }
  return statusMap[status] || ''
}
</script>

<template>
  <div class="admin-profile-logs-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-profile-logs'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 操作日志内容 -->
    <main class="content">
      <div class="header">
        <h1>个人中心 - 操作记录</h1>
        <p class="subtitle">查看和管理您的操作日志</p>
      </div>

      <section class="logs-section">
        <!-- 日志类型切换 -->
        <div class="log-type-tabs">
          <button 
            v-for="type in logTypes" 
            :key="type.value"
            class="tab-btn"
            :class="{ active: logFilters.type === type.value }"
            @click="changeLogType(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
        
        <!-- 日志过滤和操作 -->
        <div class="logs-header">
          <div class="filter-controls">
            <div class="search-box">
              <input 
                type="text" 
                v-model="logFilters.keyword" 
                placeholder="搜索日志..."
                class="search-input"
              >
            </div>
            
            <div class="date-filters">
              <input 
                type="date" 
                v-model="logFilters.startDate" 
                class="date-input"
                placeholder="开始日期"
              >
              <span class="date-separator">至</span>
              <input 
                type="date" 
                v-model="logFilters.endDate" 
                class="date-input"
                placeholder="结束日期"
              >
            </div>
            
            <button class="btn btn-reset" @click="resetFilters">重置筛选</button>
          </div>
          
          <div class="log-actions">
            <button class="btn btn-export" @click="exportLogs">导出日志</button>
          </div>
        </div>
        
        <!-- 日志列表 -->
        <div class="logs-table-container">
          <table class="logs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>日志类型</th>
                <th>操作内容</th>
                <th>操作对象</th>
                <th>IP地址</th>
                <th>操作时间</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in paginatedLogs" :key="log.id" class="log-row">
                <td class="log-id">{{ log.id }}</td>
                <td>
                  <span class="log-type-badge" :class="log.type">
                    {{ getLogTypeName(log.type) }}
                  </span>
                </td>
                <td class="log-action">{{ log.action }}</td>
                <td class="log-target">{{ log.target || '-' }}</td>
                <td class="log-ip">{{ log.ip || '-' }}</td>
                <td class="log-time">{{ log.time }}</td>
                <td>
                  <span class="status-badge" :class="getStatusClass(log.status)">
                    {{ log.status }}
                  </span>
                </td>
              </tr>
              
              <!-- 空状态 -->
              <tr v-if="paginatedLogs.length === 0" class="empty-row">
                <td colspan="7" class="empty-cell">
                  <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 1a7 7 0 1 1 0 14A7 7 0 0 1 8 1zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm5.5 3a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm3-3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-1 4a1 1 0 1 0 0-2h1a1 1 0 1 0 0 2h-1z"/>
                    </svg>
                    <p>没有找到匹配的日志记录</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分页 -->
        <div class="pagination" v-if="pagination.total > 0">
          <div class="pagination-info">
            共 {{ pagination.total }} 条记录，第 {{ pagination.currentPage }} / {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
          </div>
          <div class="pagination-controls">
            <button 
              class="page-btn" 
              :disabled="pagination.currentPage === 1"
              @click="pagination.currentPage--"
            >
              上一页
            </button>
            <button 
              class="page-btn" 
              :disabled="pagination.currentPage === Math.ceil(pagination.total / pagination.pageSize)"
              @click="pagination.currentPage++"
            >
              下一页
            </button>
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
.admin-profile-logs-container {
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

/* 日志区域样式 */
.logs-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 日志类型标签页样式 */
.log-type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0;
}

.tab-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  background-color: #f8f9fa;
  color: #6c757d;
  border-radius: 6px 6px 0 0;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  background-color: #e9ecef;
  color: #495057;
}

.tab-btn.active {
  background-color: white;
  color: #3498db;
  border-bottom-color: #3498db;
}

/* 日志头部样式 */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* 筛选控件样式 */
.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.date-filters {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.date-input {
  padding: 0.9rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.date-separator {
  color: #6c757d;
  font-weight: 500;
}

/* 按钮样式 */
.btn {
  padding: 0.9rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-export {
  background-color: #3498db;
  color: white;
}

.btn-export:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-reset {
  background-color: #95a5a6;
  color: white;
}

.btn-reset:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

/* 日志列表样式 */
.logs-table-container {
  overflow-x: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  background-color: white;
}

.logs-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 10;
}

.logs-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
  vertical-align: top;
}

.log-row:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

/* 日志类型徽章样式 */
.log-type-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.log-type-badge.operation {
  background-color: #d4edda;
  color: #155724;
}

.log-type-badge.login {
  background-color: #cce7ff;
  color: #004085;
}

.log-type-badge.error {
  background-color: #f8d7da;
  color: #721c24;
}

/* 状态徽章样式 */
.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.success {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.error {
  background-color: #f8d7da;
  color: #721c24;
}

/* 日志列表列样式 */
.log-id {
  width: 60px;
  font-weight: 600;
  color: #6c757d;
}

.log-action {
  min-width: 150px;
}

.log-target {
  min-width: 150px;
}

.log-ip {
  width: 120px;
  color: #6c757d;
}

.log-time {
  width: 160px;
  color: #6c757d;
}

/* 空状态样式 */
.empty-row {
  text-align: center;
}

.empty-cell {
  padding: 4rem 2rem;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  color: #95a5a6;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0;
  color: #7f8c8d;
  font-size: 1rem;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.95rem;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.6rem 1.2rem;
  border: 1px solid #ddd;
  background-color: white;
  color: #3498db;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #e3f2fd;
  border-color: #3498db;
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  
  .logs-section {
    padding: 1.5rem;
  }
  
  .log-type-tabs {
    flex-wrap: wrap;
  }
  
  .logs-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .date-filters {
    flex-wrap: wrap;
  }
  
  .log-actions {
    display: flex;
    gap: 1rem;
    justify-content: stretch;
  }
  
  .btn {
    flex: 1;
    min-width: auto;
  }
  
  .logs-table {
    font-size: 0.85rem;
  }
  
  .logs-table th,
  .logs-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .pagination-info {
    text-align: center;
  }
  
  .pagination-controls {
    justify-content: center;
  }
}
</style>