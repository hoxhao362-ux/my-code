<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import Navigation from '../components/Navigation.vue'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 获取期刊ID
const journalId = computed(() => route.params.id)

// 当前期刊
const journal = computed(() => {
  return userStore.journals.find(j => String(j.id) === String(journalId.value))
})

// 审稿记录
const reviewRecords = computed(() => {
  // 从期刊的reviewHistory中获取审核记录，并转换为reviewRecords格式
  if (!journal.value?.reviewHistory) return []
  
  // 过滤掉修改记录，只显示真正的审核记录
  return journal.value.reviewHistory
    .filter(record => record.status !== '修改提交') // 过滤掉修改记录
    .map((record, index) => ({
      id: index.toString(),
      journalId: journal.value.id,
      reviewerId: record.reviewer,
      reviewStage: record.stage,
      reviewResult: record.status,
      reviewComments: record.comment,
      reviewDate: record.date,
      journalAuthor: journal.value.author,
      type: record.type
    }))
})

// 当前用户角色
const currentRole = computed(() => userStore.currentRole)
// 当前用户名
const currentUsername = computed(() => userStore.user?.username || '')

// 是否可以查看完整记录（管理员或相关审核人员）
const canViewFullRecords = () => {
  if (currentRole.value === 'admin') return true
  // 检查是否有任何记录是当前用户审核的
  return reviewRecords.value.some(record => record.reviewerId === currentUsername.value)
}

// 是否可以查看半公开记录（投稿人）
const canViewPartialRecords = () => {
  return journal.value?.author === currentUsername.value
}

// 添加新的审稿记录
const showAddRecordForm = ref(false)
const newRecord = ref({
  journalId: journalId.value,
  reviewerId: currentUsername.value,
  reviewStage: '',
  reviewResult: '',
  reviewComments: '',
  reviewDate: new Date().toISOString(),
  journalAuthor: ''
})

// 稿件编辑功能
const isEditing = ref(false)
const originalJournal = ref(null)
const editedJournal = ref(null)
const modificationDescription = ref('')

// 初始化编辑状态
const initializeEdit = () => {
  if (!journal.value) return
  
  // 保存原始稿件内容
  originalJournal.value = JSON.parse(JSON.stringify(journal.value))
  editedJournal.value = JSON.parse(JSON.stringify(journal.value))
  isEditing.value = true
  modificationDescription.value = ''
}

// 保存修改
const saveModifications = () => {
  if (!journal.value || !editedJournal.value) return
  
  // 查找最近一次被拒绝的审核阶段
  let rejectedStage = '初审' // 默认初审
  if (journal.value.reviewHistory) {
    // 遍历审核历史，找到最后一个被拒绝的记录
    const rejectedRecords = journal.value.reviewHistory.filter(record => 
      ['未通过', '已拒稿', '退回', '驳回'].includes(record.status)
    )
    if (rejectedRecords.length > 0) {
      // 使用最后一个被拒绝记录的阶段
      rejectedStage = rejectedRecords[rejectedRecords.length - 1].stage
    }
  }
  
  // 创建修改记录
  const modificationRecord = {
    stage: rejectedStage, // 使用被拒绝的具体阶段
    status: '修改提交',
    reviewer: currentUsername.value,
    date: new Date().toISOString().split('T')[0],
    comment: modificationDescription.value,
    type: '完全保密'
  }
  
  // 根据被拒绝的阶段设置相应的待审核状态
  let newStatus = '待审核' // 默认状态
  if (rejectedStage === '初审') {
    newStatus = '待初审'
  } else if (rejectedStage === '复审') {
    newStatus = '待复审'
  } else if (rejectedStage === '终审') {
    newStatus = '待终审'
  }
  
  // 更新期刊信息
  const updatedJournal = {
    ...editedJournal.value,
    status: newStatus, // 重置为相应阶段的待审核状态
    reviewHistory: [...(journal.value.reviewHistory || []), modificationRecord]
  }
  
  // 保存到store并获取结果
  const success = userStore.updateJournal(updatedJournal)
  
  if (success) {
    // 退出编辑模式
    isEditing.value = false
    originalJournal.value = null
    editedJournal.value = null
    modificationDescription.value = ''
    
    // 显示成功提示
    alert(`修改已成功发送，稿件将重新提交到${rejectedStage}环节进行审稿`)
  } else {
    // 显示失败提示
    alert('发送修改失败，请稍后重试')
  }
}

// 取消修改，恢复原始内容
const cancelEdit = () => {
  isEditing.value = false
  originalJournal.value = null
  editedJournal.value = null
  modificationDescription.value = ''
}

// 检查是否可以修改稿件
const canModify = computed(() => {
  // 只有稿件作者可以修改
  if (journal.value?.author !== currentUsername.value) return false
  
  // 只有未通过或修改再审状态的稿件可以修改
  return ['已拒稿', '未通过', '修改再审'].includes(journal.value?.status || '')
})

// 保存新的审稿记录
const saveReviewRecord = () => {
  if (!journal.value) return
  
  // 设置期刊作者
  newRecord.value.journalAuthor = journal.value.author
  
  // 生成唯一ID
  newRecord.value.id = Date.now().toString()
  
  // 创建审核记录，使用与journal.reviewHistory相同的格式
  const newReviewHistoryRecord = {
    stage: newRecord.value.reviewStage,
    status: newRecord.value.reviewResult,
    reviewer: newRecord.value.reviewerId,
    date: new Date().toISOString().split('T')[0], // 使用与现有记录相同的日期格式
    comment: newRecord.value.reviewComments,
    type: '完全保密' // 默认类型
  }
  
  // 添加到期刊的reviewHistory中
  const updatedJournal = {
    ...journal.value,
    reviewHistory: [...(journal.value.reviewHistory || []), newReviewHistoryRecord]
  }
  
  // 更新期刊
  userStore.updateJournal(updatedJournal)
  
  // 关闭表单
  showAddRecordForm.value = false
  
  // 重置表单
  newRecord.value = {
    journalId: journalId.value,
    reviewerId: currentUsername.value,
    reviewStage: '',
    reviewResult: '',
    reviewComments: '',
    reviewDate: new Date().toISOString(),
    journalAuthor: ''
  }
}

// 格式化日期
const formatDate = (dateString) => {
  // 检查是否已经是YYYY-MM-DD格式
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return dateString
  }
  
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}
</script>

<template>
  <div class="review-records-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="userStore.user"
      :current-page="'review-records'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 审稿记录内容 -->
    <main class="review-records-content">
      <div class="review-records-wrapper">
        <!-- 标题和返回按钮 -->
        <div class="page-header">
          <button class="back-btn" @click="goBack">&larr; 返回</button>
          <h1 class="page-title">审稿记录</h1>
          <!-- 只有管理员和审核员可以添加记录 -->
          <button 
            v-if="currentRole === 'admin' || currentRole === 'reviewer'" 
            class="add-record-btn" 
            @click="showAddRecordForm = !showAddRecordForm"
          >
            添加审稿记录
          </button>
        </div>
        
        <!-- 稿件内容显示 -->
        <div v-if="journal" class="journal-content">
          <div class="content-header">
            <h2>稿件详情</h2>
            <!-- 修改按钮 -->
            <button 
              v-if="canModify && !isEditing" 
              class="modify-btn" 
              @click="initializeEdit"
            >
              修改稿件
            </button>
            
            <!-- 编辑状态下的取消按钮 -->
            <button 
              v-if="isEditing" 
              class="cancel-btn" 
              @click="cancelEdit"
            >
              取消修改
            </button>
          </div>
          
          <div class="journal-meta">
            <div class="meta-item">
              <strong>标题：</strong>
              <input 
                v-if="isEditing" 
                v-model="editedJournal.title" 
                type="text" 
                class="meta-input"
              >
              <span v-else>{{ journal.title }}</span>
            </div>
            <div class="meta-item">
              <strong>作者：</strong>{{ journal.author }}
            </div>
            <div class="meta-item">
              <strong>模块：</strong>
              <select 
                v-if="isEditing" 
                v-model="editedJournal.module" 
                class="meta-select"
              >
                <option v-for="module in userStore.modules" :key="module" :value="module">
                  {{ module }}
                </option>
              </select>
              <span v-else>{{ journal.module }}</span>
            </div>
            <div class="meta-item">
              <strong>状态：</strong>
              <span class="status-badge" :class="journal.status.toLowerCase().replace(/\s/g, '-')">
                {{ journal.status }}
              </span>
            </div>
            <div class="meta-item">
              <strong>提交时间：</strong>{{ journal.submitDate }}
            </div>
            <div class="meta-item">
              <strong>关键词：</strong>
              <input 
                v-if="isEditing" 
                v-model="editedJournal.keywords" 
                type="text" 
                class="meta-input"
                placeholder="请输入关键词，用逗号分隔"
              >
              <span v-else>{{ journal.keywords || '无' }}</span>
            </div>
          </div>
          
          <!-- 稿件摘要 -->
          <div class="journal-abstract">
            <h3>摘要</h3>
            <textarea 
              v-if="isEditing" 
              v-model="editedJournal.abstract" 
              class="abstract-textarea"
              rows="4"
              placeholder="请输入摘要"
            ></textarea>
            <p v-else>{{ journal.abstract || '暂无摘要' }}</p>
          </div>
          
          <!-- 稿件正文 -->
          <div class="journal-main-content">
            <h3>正文内容</h3>
            <textarea 
              v-if="isEditing" 
              v-model="editedJournal.content" 
              class="content-textarea"
              rows="10"
              placeholder="请输入正文内容"
            ></textarea>
            <div v-else-if="journal.content" class="content-display">
              {{ journal.content }}
            </div>
            <div v-else class="no-content">
              <p>暂无正文内容</p>
            </div>
          </div>
          
          <!-- 修改说明 -->
          <div v-if="isEditing" class="modification-description">
            <h3>修改说明</h3>
            <textarea 
              v-model="modificationDescription" 
              class="description-textarea"
              rows="4"
              placeholder="请简要说明本次修改的内容和原因"
            ></textarea>
            
            <!-- 发送按钮 -->
            <div class="send-section">
              <button 
                class="send-btn" 
                @click="saveModifications"
                :disabled="!modificationDescription.trim()"
              >
                发送修改
              </button>
              <p class="send-info">
                点击发送后，稿件将重新提交到当前环节进行审稿
              </p>
              <p v-if="!modificationDescription.trim()" class="required-info">
                <span class="required-icon">*</span> 请填写修改说明后再发送
              </p>
            </div>
          </div>
        </div>
        
        <!-- 添加记录表单 -->
        <div v-if="showAddRecordForm" class="add-record-form">
          <h2>添加审稿记录</h2>
          <div class="form-row">
            <div class="form-group">
              <label for="reviewStage">审核阶段</label>
              <select id="reviewStage" v-model="newRecord.reviewStage">
                <option value="">请选择审核阶段</option>
                <option value="初审">初审</option>
                <option value="复审">复审</option>
                <option value="终审">终审</option>
              </select>
            </div>
            <div class="form-group">
              <label for="reviewResult">审核结果</label>
              <select id="reviewResult" v-model="newRecord.reviewResult">
                <option value="">请选择审核结果</option>
                <option value="通过">通过</option>
                <option value="修改后通过">修改后通过</option>
                <option value="退回">退回</option>
                <option value="驳回">驳回</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group full-width">
              <label for="reviewComments">审核意见</label>
              <textarea 
                id="reviewComments" 
                v-model="newRecord.reviewComments" 
                rows="4" 
                placeholder="请输入审核意见"
              ></textarea>
            </div>
          </div>
          <div class="form-actions">
            <button class="save-btn" @click="saveReviewRecord">保存</button>
            <button class="cancel-btn" @click="showAddRecordForm = false">取消</button>
          </div>
        </div>
        
        <!-- 审稿记录列表 -->
        <div class="records-list">
          <h2>记录列表</h2>
          
          <!-- 没有记录时显示 -->
          <div v-if="reviewRecords.length === 0" class="no-records">
            <p>暂无审稿记录</p>
          </div>
          
          <!-- 有记录时显示 -->
          <div v-else class="records-container">
            <!-- 只有管理员或相关人员可以查看完整记录 -->
            <div v-if="canViewFullRecords()" class="full-records">
              <div 
                v-for="record in reviewRecords" 
                :key="record.id" 
                class="record-item full-record"
              >
                <div class="record-header">
                  <div class="record-meta">
                    <h3>{{ record.reviewStage }} - {{ record.reviewResult }}</h3>
                    <p class="reviewer-info">审核人：{{ record.reviewerId }}</p>
                    <p class="review-date">审核时间：{{ formatDate(record.reviewDate) }}</p>
                  </div>
                </div>
                <div class="record-content">
                  <h4>审核意见：</h4>
                  <p>{{ record.reviewComments }}</p>
                </div>
              </div>
            </div>
            
            <!-- 投稿人只能查看半公开信息 -->
            <div v-else-if="canViewPartialRecords()" class="partial-records">
              <div 
                v-for="record in reviewRecords" 
                :key="record.id" 
                class="record-item partial-record"
              >
                <div class="record-header">
                  <div class="record-meta">
                    <h3>{{ record.reviewStage }} - {{ record.reviewResult }}</h3>
                    <p class="review-date">审核时间：{{ formatDate(record.reviewDate) }}</p>
                  </div>
                </div>
                <div class="record-content">
                  <!-- 半公开信息只显示最终结论，不显示详细意见和审核人信息 -->
                  <div v-if="record.reviewStage === '终审'" class="final-conclusion">
                    <h4>最终结论：</h4>
                    <p>{{ record.reviewResult }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 无权限查看 -->
            <div v-else class="no-permission">
              <p>您没有权限查看此审稿记录</p>
            </div>
          </div>
        </div>
      </div>
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
.review-records-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.review-records-content {
  flex: 1;
  padding: 2rem;
  background-color: #f5f5f5;
}

.review-records-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #357abd;
}

.page-title {
  margin: 0;
  color: #333;
}

.add-record-btn {
  padding: 0.5rem 1rem;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.add-record-btn:hover {
  background-color: #229954;
}

.add-record-form {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #ddd;
}

.add-record-form h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
}

.form-group.full-width {
  flex: 1 1 100%;
  min-width: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4a90e2;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.save-btn:hover {
  background-color: #229954;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.cancel-btn:hover {
  background-color: #c0392b;
}

.records-list h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.no-records {
  text-align: center;
  padding: 2rem;
  color: #777;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.records-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.record-item {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #ddd;
}

.record-header {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.record-meta h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.reviewer-info,
.review-date {
  margin: 0.25rem 0;
  color: #666;
  font-size: 0.9rem;
}

.record-content h4 {
  margin: 0 0 0.5rem 0;
  color: #555;
}

.record-content p {
  margin: 0;
  color: #333;
  line-height: 1.5;
}

.final-conclusion {
  background-color: #e8f4f8;
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid #4a90e2;
}

/* 稿件内容样式 */
.journal-content {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #ddd;
  margin-bottom: 2rem;
}

.journal-content h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.5rem;
}

.journal-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f0f0f0;
  border-radius: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.meta-item strong {
  font-weight: 600;
  color: #555;
  min-width: 60px;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.已投稿 {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.审核中 {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.已录用 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.已拒稿 {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-badge.修改再审 {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.journal-abstract {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f0f8ff;
  border-radius: 6px;
  border-left: 4px solid #4a90e2;
}

.journal-abstract h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.journal-main-content {
  margin-bottom: 1.5rem;
}

.journal-main-content h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.content-display {
  background-color: white;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  min-height: 200px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.no-content {
  text-align: center;
  padding: 2rem;
  color: #777;
  background-color: white;
  border-radius: 6px;
  border: 1px dashed #ddd;
}

.no-content p {
  margin: 0;
  font-style: italic;
}

/* 编辑功能样式 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ddd;
}

.modify-btn {
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.modify-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.edit-actions {
  display: flex;
  gap: 1rem;
}

.save-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.save-btn {
  background-color: #27ae60;
  color: white;
}

.save-btn:hover {
  background-color: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.cancel-btn {
  background-color: #e74c3c;
  color: white;
}

.cancel-btn:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 编辑输入框样式 */
.meta-input, .meta-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  width: 100%;
  max-width: 300px;
  margin-top: 0.25rem;
}

.meta-select {
  cursor: pointer;
}

.abstract-textarea, .content-textarea, .description-textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
}

.abstract-textarea:focus, .content-textarea:focus, .description-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.content-textarea {
  min-height: 300px;
}

.description-textarea {
  margin-top: 1rem;
}

/* 修改说明部分样式 */
.modification-description {
  background-color: #f0f8ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-top: 1.5rem;
}

.modification-description h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .edit-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .save-btn, .cancel-btn, .modify-btn {
    width: 48%;
    padding: 0.6rem;
  }
  
  .meta-input, .meta-select {
  max-width: 100%;
}
}

/* 发送按钮样式 */
.send-section {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.send-btn {
  padding: 0.75rem 1.5rem;
  background-color: #e67e22;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.send-btn:hover {
  background-color: #d35400;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 126, 34, 0.3);
}

.send-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-info {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
  line-height: 1.4;
}

.required-info {
  margin: 0.5rem 0 0 0;
  color: #e74c3c;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required-icon {
  font-weight: bold;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>