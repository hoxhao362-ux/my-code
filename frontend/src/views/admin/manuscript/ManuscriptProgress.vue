<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 稿件ID筛选
const selectedManuscriptId = ref('')

// 稿件列表 - 只显示当前用户的稿件
const manuscripts = computed(() => {
  return userStore.journals.filter(journal => journal.author === userStore.user?.username)
})

// 当前选中稿件的详情
const currentManuscript = computed(() => {
  if (!selectedManuscriptId.value) return null
  return manuscripts.value.find(m => String(m.id) === String(selectedManuscriptId.value))
})

// 当前稿件的审核记录
const manuscriptReviewRecords = computed(() => {
  if (!selectedManuscriptId.value) return []
  return userStore.reviewRecords.filter(record => String(record.journalId) === String(selectedManuscriptId.value))
})

// 查看稿件详情
const viewManuscript = (id) => {
  router.push(`/admin/review-records/${id}`)
}
</script>

<template>
  <div class="manuscript-progress-container">
    <div class="page-header">
      <button class="btn btn-secondary" @click="router.back()">返回</button>
      <h1>稿件进度</h1>
    </div>
    
    <div class="filters-section">
      <div class="filter-group">
        <label for="manuscript-filter">选择稿件：</label>
        <select id="manuscript-filter" v-model="selectedManuscriptId" class="filter-control">
          <option value="">请选择稿件</option>
          <option v-for="manuscript in manuscripts" :key="manuscript.id" :value="manuscript.id">
            {{ manuscript.title }}
          </option>
        </select>
      </div>
    </div>
    
    <div v-if="currentManuscript" class="manuscript-detail-section">
      <div class="manuscript-header">
        <h2>{{ currentManuscript.title }}</h2>
        <div class="manuscript-meta">
          <span class="meta-item">模块：{{ currentManuscript.module }}</span>
          <span class="meta-item">状态：<span class="status-badge" :class="currentManuscript.status.toLowerCase().replace(/\s/g, '-')">{{ currentManuscript.status }}</span></span>
          <span class="meta-item">提交时间：{{ currentManuscript.submitDate }}</span>
        </div>
      </div>
      
      <div class="progress-section">
        <h3>审核进度</h3>
        <div class="progress-timeline">
          <div 
            v-for="stage in ['已投稿', '初审', '复审', '终审', '已录用/已拒稿']" 
            :key="stage"
            class="progress-step"
            :class="{
              'completed': ['已投稿', '审核中', '已录用', '已拒稿', '修改再审'].includes(currentManuscript.status) || 
                        (stage === '已投稿' && currentManuscript.status),
              'current': currentManuscript.status === stage
            }"
          >
            <div class="step-dot"></div>
            <div class="step-label">{{ stage }}</div>
          </div>
        </div>
      </div>
      
      <div v-if="manuscriptReviewRecords.length > 0" class="review-records-section">
        <h3>审核记录</h3>
        <div class="review-records-list">
          <div v-for="record in manuscriptReviewRecords" :key="record.id" class="review-record-item">
            <div class="record-header">
              <div class="record-meta">
                <span class="record-stage">{{ record.stage }}</span>
                <span class="record-date">{{ record.reviewDate }}</span>
                <span class="reviewer-name">审核人：{{ record.reviewerName || '系统' }}</span>
              </div>
              <span class="record-result" :class="record.result.toLowerCase().replace(/\s/g, '-')">
                {{ record.result }}
              </span>
            </div>
            <div v-if="record.comment" class="record-comment">
              <h4>审核意见：</h4>
              <p>{{ record.comment }}</p>
            </div>
            <div v-if="record.modificationRequirements" class="record-modifications">
              <h4>修改要求：</h4>
              <p>{{ record.modificationRequirements }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="no-records">
        <p>暂无审核记录</p>
      </div>
      
      <div class="action-buttons">
        <button class="btn btn-primary" @click="viewManuscript(currentManuscript.id)">
          查看详细信息
        </button>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <p>请选择要查看进度的稿件</p>
    </div>
  </div>
</template>

<style scoped>
.manuscript-progress-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

.filters-section {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  min-width: 300px;
}

.filter-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.manuscript-detail-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.manuscript-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.manuscript-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.manuscript-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.95rem;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.progress-section {
  margin-bottom: 2rem;
}

.progress-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.progress-timeline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  padding: 0 1rem;
}

.progress-timeline::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e9ecef;
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
}

.step-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #e9ecef;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e9ecef;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.85rem;
  color: #666;
  text-align: center;
  transition: all 0.3s ease;
}

.progress-step.completed .step-dot {
  background-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

.progress-step.completed .step-label {
  color: #3498db;
  font-weight: 500;
}

.progress-step.current .step-dot {
  background-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
  transform: scale(1.2);
}

.progress-step.current .step-label {
  color: #3498db;
  font-weight: 600;
}

.review-records-section {
  margin-bottom: 2rem;
}

.review-records-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.review-records-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-record-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.review-record-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.record-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.record-stage {
  font-weight: 600;
  color: #2c3e50;
}

.record-date {
  color: #666;
  font-size: 0.9rem;
}

.reviewer-name {
  color: #666;
  font-size: 0.9rem;
}

.record-result {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.record-result.通过 {
  background-color: #e8f5e8;
  color: #388e3c;
}

.record-result.修改 {
  background-color: #fff3e0;
  color: #f57c00;
}

.record-result.不通过 {
  background-color: #ffebee;
  color: #d32f2f;
}

.record-comment, .record-modifications {
  margin-bottom: 1rem;
}

.record-comment h4, .record-modifications h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.record-comment p, .record-modifications p {
  margin: 0;
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap;
  background-color: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.no-records {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  color: #999;
  font-size: 1.1rem;
}

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

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .manuscript-progress-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters-section {
    padding: 1rem;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-control {
    min-width: auto;
  }
  
  .manuscript-detail-section {
    padding: 1rem;
  }
  
  .manuscript-meta {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .progress-timeline {
    padding: 0 0.5rem;
  }
  
  .step-label {
    font-size: 0.75rem;
  }
  
  .record-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .record-meta {
    gap: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>