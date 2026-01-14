<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 稿件ID筛选
const selectedManuscriptId = ref('')

// 稿件列表 - 只显示当前用户的稿件
const manuscripts = computed(() => {
  return userStore.userJournals
})

// 当前选中稿件的详情
const currentManuscript = computed(() => {
  if (!selectedManuscriptId.value) return null
  return manuscripts.value.find(m => String(m.id) === String(selectedManuscriptId.value))
})

// 查看稿件详情
const viewManuscript = (id) => {
  router.push(`/admin/review-records/${id}`)
}

// 初始化时，如果有稿件，默认选择第一个
onMounted(() => {
  if (manuscripts.value.length > 0) {
    selectedManuscriptId.value = String(manuscripts.value[0].id)
  }
})
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
            v-for="(stage, index) in ['已投稿', '初审', '复审', '终审', '已发表/已拒稿']" 
            :key="stage"
            class="progress-step"
            :class="{
              'completed': (
                // 基础状态：已投稿
                (['已投稿', '待审核'].includes(currentManuscript.status) && index <= 0) ||
                // 初审相关状态
                (['审核中', '审稿中', '待初审'].includes(currentManuscript.status) && index <= 1) ||
                // 复审相关状态
                (['修改再审', '复审', '待复审'].includes(currentManuscript.status) && index <= 2) ||
                // 终审状态
                (['终审', '待终审'].includes(currentManuscript.status) && index <= 3) ||
                // 已发表/已通过状态：所有阶段完成
                (['已发表', '已通过', '通过', '已录用'].includes(currentManuscript.status) && index <= 4) ||
                // 拒稿状态：根据实际拒绝阶段显示
                (['已拒稿', '未通过'].includes(currentManuscript.status) && index <= 1)
              ),
              'current': (
                (['已投稿', '待审核'].includes(currentManuscript.status) && index === 0) ||
                (['审核中', '审稿中', '待初审'].includes(currentManuscript.status) && index === 1) ||
                (['修改再审', '复审', '待复审'].includes(currentManuscript.status) && index === 2) ||
                (['终审', '待终审'].includes(currentManuscript.status) && index === 3) ||
                (['已发表', '已通过', '通过', '已录用'].includes(currentManuscript.status) && index === 4) ||
                (['已拒稿', '未通过'].includes(currentManuscript.status) && index === 1)
              ),
              'rejected': (['已拒稿', '未通过'].includes(currentManuscript.status) && index === 1),
              'published': (['已发表', '已通过', '通过', '已录用'].includes(currentManuscript.status) && index === 4)
            }"
          >
            <div class="step-dot"></div>
            <div class="step-label">{{ stage }}</div>
          </div>
        </div>
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
  font-family: inherit;
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
  font-weight: 600;
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
  background-color: white;
}

.filter-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
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
  font-weight: 600;
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
  font-weight: 600;
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
  background-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.3);
}

.progress-step.completed .step-label {
  color: #42b883;
  font-weight: 500;
}

.progress-step.current .step-dot {
  background-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.3);
  transform: scale(1.2);
}

.progress-step.current .step-label {
  color: #42b883;
  font-weight: 600;
}

/* 拒稿状态样式 */
.progress-step.rejected .step-dot {
  background-color: #ff6b6b;
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.3);
}

.progress-step.rejected .step-dot::after {
  background-color: white;
}

.progress-step.rejected .step-label {
  color: #ff6b6b;
  font-weight: 600;
}

/* 已发表状态样式 */
.progress-step.published .step-dot {
  background-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.3);
}

.progress-step.published .step-dot::after {
  background-color: white;
}

.progress-step.published .step-label {
  color: #42b883;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
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
  background-color: #42b883;
  color: white;
}

.btn-primary:hover {
  background-color: #369f70;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 184, 131, 0.3);
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
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>