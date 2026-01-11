<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const router = useRouter()

const userStore = useUserStore()

// 反馈消息列表
const feedbackMessages = computed(() => userStore.feedbackMessages)

// 筛选条件
const filters = ref({
  type: 'all', // all, 联系我们, 意见反馈
  status: 'all', // all, 未处理, 已处理, 已回复
  search: ''
})

// 选中的消息ID（用于批量删除）
const selectedMessages = ref([])

// 详情模态框
const showDetailModal = ref(false)
const currentMessage = ref(null)

// 状态选项
const statusOptions = ['未处理', '已处理', '已回复']

// 确认删除模态框
const showDeleteModal = ref(false)
// 删除类型：single 或 batch
const deleteType = ref('single')
// 当前要删除的单个消息ID
const currentDeleteMessageId = ref(null)

// 筛选后的消息列表
const filteredMessages = computed(() => {
  return feedbackMessages.value.filter(message => {
    // 类型筛选
    if (filters.value.type !== 'all' && message.type !== filters.value.type) {
      return false
    }
    // 状态筛选
    if (filters.value.status !== 'all' && message.status !== filters.value.status) {
      return false
    }
    // 搜索筛选
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      return (
        message.name.toLowerCase().includes(searchLower) ||
        message.email.toLowerCase().includes(searchLower) ||
        message.subject.toLowerCase().includes(searchLower) ||
        message.content.toLowerCase().includes(searchLower)
      )
    }
    return true
  })
})

// 查看详情
const viewMessageDetail = (message) => {
  currentMessage.value = message
  showDetailModal.value = true
}

// 更新消息状态
const updateMessageStatus = (messageId, status) => {
  userStore.updateFeedbackMessageStatus(messageId, status)
}

// 打开删除确认模态框（单条删除）
const openDeleteModal = (messageId) => {
  deleteType.value = 'single'
  currentDeleteMessageId.value = messageId
  showDeleteModal.value = true
}

// 打开删除确认模态框（批量删除）
const openBatchDeleteModal = () => {
  if (selectedMessages.value.length === 0) {
    alert('请先选择要删除的消息')
    return
  }
  deleteType.value = 'batch'
  showDeleteModal.value = true
}

// 确认删除
const confirmDelete = () => {
  if (deleteType.value === 'single') {
    // 执行单条删除
    userStore.deleteFeedbackMessage(currentDeleteMessageId.value)
  } else {
    // 执行批量删除
    userStore.deleteMultipleFeedbackMessages(selectedMessages.value)
    selectedMessages.value = []
  }
  // 关闭模态框
  showDeleteModal.value = false
}

// 取消删除
const cancelDelete = () => {
  // 仅关闭模态框，不执行任何操作
  showDeleteModal.value = false
}

// 切换全选
const toggleSelectAll = (event) => {
  if (event.target.checked) {
    selectedMessages.value = filteredMessages.value.map(message => String(message.id))
  } else {
    selectedMessages.value = []
  }
}

// 切换单条选择
const toggleSelectMessage = (messageId) => {
  const idStr = String(messageId)
  const index = selectedMessages.value.indexOf(idStr)
  if (index > -1) {
    selectedMessages.value.splice(index, 1)
  } else {
    selectedMessages.value.push(idStr)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载时加载反馈消息
onMounted(() => {
  userStore.loadFeedbackMessages()
})
</script>

<template>
  <div class="feedback-management-container">
    <div class="feedback-header">
      <div class="header-left">
        <button 
          class="btn btn-secondary" 
          @click="router.back()"
        >
          返回
        </button>
        <h2>意见收纳管理</h2>
      </div>
      <div class="actions">
        <button 
          class="btn btn-danger" 
          @click="openBatchDeleteModal"
          :disabled="selectedMessages.length === 0"
        >
          批量删除 ({{ selectedMessages.length }})
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filters-section">
      <div class="filter-group">
        <label>类型筛选：</label>
        <select v-model="filters.type" class="filter-control">
          <option value="all">全部类型</option>
          <option value="联系我们">联系我们</option>
          <option value="意见反馈">意见反馈</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>状态筛选：</label>
        <select v-model="filters.status" class="filter-control">
          <option value="all">全部状态</option>
          <option value="未处理">未处理</option>
          <option value="已处理">已处理</option>
          <option value="已回复">已回复</option>
        </select>
      </div>
      
      <div class="filter-group search-group">
        <input 
          type="text" 
          v-model="filters.search" 
          class="filter-control search-input"
          placeholder="搜索姓名、邮箱、主题或内容..."
        >
      </div>
    </div>

    <!-- 反馈消息列表 -->
    <div class="feedback-table-wrapper">
      <table class="feedback-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <input 
                type="checkbox" 
                @change="toggleSelectAll($event)"
                :checked="selectedMessages.length === filteredMessages.length && filteredMessages.length > 0"
              >
            </th>
            <th>ID</th>
            <th>类型</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>主题</th>
            <th>状态</th>
            <th>提交时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="message in filteredMessages" :key="message.id">
            <td class="checkbox-col">
              <input 
                type="checkbox" 
                @change="toggleSelectMessage(message.id)"
                :checked="selectedMessages.includes(String(message.id))"
              >
            </td>
            <td>{{ message.id }}</td>
            <td>
              <span class="type-tag" :class="message.type.toLowerCase().replace(/\s/g, '-')">
                {{ message.type }}
              </span>
            </td>
            <td>{{ message.name }}</td>
            <td>{{ message.email }}</td>
            <td class="subject-col">{{ message.subject }}</td>
            <td>
              <select 
                v-model="message.status" 
                class="status-select"
                @change="updateMessageStatus(message.id, message.status)"
              >
                <option v-for="status in statusOptions" :key="status" :value="status">
                  {{ status }}
                </option>
              </select>
            </td>
            <td>{{ formatDate(message.createdAt) }}</td>
            <td class="actions-col">
              <button 
                class="btn btn-primary btn-sm" 
                @click="viewMessageDetail(message)"
              >
                详情
              </button>
              <button 
                class="btn btn-danger btn-sm" 
                @click="openDeleteModal(message.id)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="filteredMessages.length === 0" class="empty-state">
        <p>暂无反馈消息</p>
      </div>
    </div>

    <!-- 详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ currentMessage?.type }} - 消息详情</h3>
          <button class="close-btn" @click="showDetailModal = false">×</button>
        </div>
        <div class="modal-body" v-if="currentMessage">
          <div class="detail-item">
            <span class="detail-label">ID：</span>
            <span class="detail-value">{{ currentMessage.id }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">提交者：</span>
            <span class="detail-value">{{ currentMessage.name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">邮箱：</span>
            <span class="detail-value">{{ currentMessage.email }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">主题：</span>
            <span class="detail-value">{{ currentMessage.subject }}</span>
          </div>
          <div v-if="currentMessage.feedbackType" class="detail-item">
            <span class="detail-label">反馈类型：</span>
            <span class="detail-value">{{ currentMessage.feedbackType }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">内容：</span>
            <div class="detail-value content-value">{{ currentMessage.content }}</div>
          </div>
          <div class="detail-item">
            <span class="detail-label">状态：</span>
            <span class="detail-value status-badge" :class="currentMessage.status.toLowerCase().replace(/\s/g, '-')">
              {{ currentMessage.status }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">提交时间：</span>
            <span class="detail-value">{{ formatDate(currentMessage.createdAt) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 确认删除模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ deleteType === 'single' ? '确认删除' : '批量确认删除' }}</h3>
          <button class="close-btn" @click="cancelDelete">×</button>
        </div>
        <div class="modal-body">
          <p>{{ deleteType === 'single' ? '确定要删除这条反馈消息吗？' : '确定要删除选中的 ' + selectedMessages.length + ' 条反馈消息吗？' }} 此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">取消</button>
          <button class="btn btn-danger" @click="confirmDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feedback-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.feedback-header h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

.actions {
  display: flex;
  gap: 1rem;
}

/* 筛选区域样式 */
.filters-section {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.filter-control {
  padding: 0.7rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-group {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.7rem 1rem;
}

/* 表格样式 */
.feedback-table-wrapper {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.feedback-table {
  width: 100%;
  border-collapse: collapse;
}

.feedback-table th,
.feedback-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.feedback-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.feedback-table tr:hover {
  background-color: #f8f9fa;
}

.checkbox-col {
  width: 50px;
  text-align: center;
}

.subject-col {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-col {
  display: flex;
  gap: 0.5rem;
}

/* 类型标签样式 */
.type-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-tag.联系我们 {
  background-color: #e3f2fd;
  color: #1976d2;
}

.type-tag.意见反馈 {
  background-color: #e8f5e8;
  color: #388e3c;
}

/* 状态选择器样式 */
.status-select {
  padding: 0.4rem 0.7rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  background-color: white;
}

/* 按钮样式 */
.btn {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  text-align: right;
  background-color: #f8f9fa;
}

/* 详情样式 */
.detail-item {
  display: flex;
  margin-bottom: 1rem;
  gap: 1rem;
}

.detail-label {
  width: 100px;
  font-weight: 600;
  color: #2c3e50;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
  color: #555;
  word-break: break-word;
}

.content-value {
  white-space: pre-wrap;
  line-height: 1.6;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.未处理 {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.已处理 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已回复 {
  background-color: #e3f2fd;
  color: #1976d2;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feedback-management-container {
    padding: 1rem;
  }
  
  .feedback-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .feedback-table {
    font-size: 0.85rem;
  }
  
  .feedback-table th,
  .feedback-table td {
    padding: 0.7rem 0.5rem;
  }
  
  .actions-col {
    flex-direction: column;
    gap: 0.3rem;
  }
  
  .btn-sm {
    padding: 0.4rem 0.7rem;
    font-size: 0.75rem;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
  
  .detail-item {
    flex-direction: column;
    gap: 0.3rem;
  }
  
  .detail-label {
    width: auto;
    font-size: 0.9rem;
  }
}
</style>