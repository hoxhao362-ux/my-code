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

// 审稿记录
const reviewRecords = ref([])
// 当前用户角色
const currentRole = computed(() => userStore.currentRole)
// 当前用户名
const currentUsername = computed(() => userStore.user?.username || '')

// 加载审稿记录
onMounted(() => {
  reviewRecords.value = userStore.journalReviewRecords(journalId.value)
})

// 是否可以查看完整记录（管理员或相关审核人员）
const canViewFullRecords = (record) => {
  return currentRole.value === 'admin' || record.reviewerId === currentUsername.value
}

// 是否可以查看半公开记录（投稿人）
const canViewPartialRecords = (record) => {
  return reviewRecords.value.some(r => r.journalAuthor === currentUsername.value)
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

// 保存新的审稿记录
const saveReviewRecord = () => {
  // 设置期刊作者（从期刊数据中获取）
  const journal = userStore.journals.find(j => j.id === journalId.value)
  if (journal) {
    newRecord.value.journalAuthor = journal.author
  }
  
  // 生成唯一ID
  newRecord.value.id = Date.now().toString()
  
  // 添加到状态管理
  userStore.addReviewRecord(newRecord.value)
  
  // 刷新记录列表
  reviewRecords.value = userStore.journalReviewRecords(journalId.value)
  
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
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
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
            <div v-if="canViewFullRecords(reviewRecords[0])" class="full-records">
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
            <div v-else-if="canViewPartialRecords(reviewRecords[0])" class="partial-records">
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