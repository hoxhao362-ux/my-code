<script setup>
import { stripHtmlTags } from '../utils/helpers'
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
  // 确保attachments数组存在
  if (!editedJournal.value.attachments) {
    editedJournal.value.attachments = []
  }
  // 确保attachments中的每个对象都有正确的size属性
  editedJournal.value.attachments = editedJournal.value.attachments.map(attachment => {
    // 如果size为0或undefined，设置一个默认值
    if (!attachment.size || attachment.size === 0) {
      // 尝试从file对象获取大小
      if (attachment.file) {
        attachment.size = attachment.file.size
      } else {
        // 否则设置为0
        attachment.size = 0
      }
    }
    return attachment
  })
  isEditing.value = true
  modificationDescription.value = ''
}

// 触发文件上传
const triggerFileUpload = () => {
  document.getElementById('attachment-upload').click()
}

// 附件上传处理
const handleFileUpload = (event) => {
  // 阻止事件冒泡和默认行为，防止表单提交
  event.stopPropagation()
  event.preventDefault()
  
  const file = event.target.files[0]
  if (file) {
    // 检查文件大小（限制10MB）
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      alert('文件大小不能超过10MB')
      return
    }
    
    // 检查文件类型
    const allowedTypes = ['.doc', '.docx', '.pdf', '.txt']
    const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`
    if (!allowedTypes.includes(fileExtension)) {
      alert('只支持上传.doc, .docx, .pdf, .txt文件')
      return
    }
    
    // 添加到附件列表
    const attachment = {
      id: Date.now().toString(),
      name: file.name,
      type: file.type,
      size: file.size,
      // 先使用文件名作为临时URL，后续会被实际URL替换
      url: file.name,
      file: file // 保存原始文件对象，用于预览
    }
    
    editedJournal.value.attachments.push(attachment)
    
    // 清空文件输入
    event.target.value = ''
  }
}

// 删除附件
const removeAttachment = (attachmentId) => {
  // 从附件列表中移除
  const index = editedJournal.value.attachments.findIndex(att => att.id === attachmentId)
  if (index !== -1) {
    editedJournal.value.attachments.splice(index, 1)
  }
}

// 预览附件
const previewAttachment = (attachment) => {
  const fileExtension = `.${attachment.name.split('.').pop().toLowerCase()}`
  const previewableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
  
  if (previewableExtensions.includes(fileExtension)) {
    // 创建一个新的预览窗口
    const previewWindow = window.open('', '_blank', 'width=1000,height=800')
    if (previewWindow) {
      // 显示加载状态
      previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>预览：${attachment.name}</title>
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body, html {
              height: 100%;
              overflow: hidden;
              font-family: Arial, sans-serif;
              background-color: #f5f5f5;
            }
            .preview-header {
              padding: 15px 20px;
              background: #ffffff;
              border-bottom: 1px solid #e0e0e0;
              display: flex;
              justify-content: space-between;
              align-items: center;
              box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .preview-title {
              font-weight: bold;
              color: #2c3e50;
              font-size: 16px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              max-width: 60%;
            }
            .header-actions {
              display: flex;
              gap: 10px;
              align-items: center;
            }
            .btn {
              padding: 8px 16px;
              border: none;
              border-radius: 4px;
              font-size: 14px;
              font-weight: 500;
              cursor: pointer;
              text-decoration: none;
              transition: all 0.3s ease;
              display: inline-block;
              text-align: center;
            }
            .btn-primary {
              background: #3498db;
              color: white;
            }
            .btn-primary:hover {
              background: #2980b9;
            }
            .btn-secondary {
              background: #95a5a6;
              color: white;
            }
            .btn-secondary:hover {
              background: #7f8c8d;
            }
            .preview-container {
              height: calc(100% - 60px);
              width: 100%;
              background: white;
              overflow: auto;
              position: relative;
            }
            .preview-content {
              width: 100%;
              height: 100%;
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
              padding: 20px;
            }
            .loading {
              font-size: 18px;
              color: #666;
              text-align: center;
            }
            .error {
              font-size: 18px;
              color: #e74c3c;
              text-align: center;
              padding: 20px;
            }
            iframe {
              width: 100%;
              height: 100%;
              border: none;
              background: white;
            }
            img {
              max-width: 100%;
              max-height: 100%;
            }
            pre {
              width: 100%;
              height: 100%;
              overflow: auto;
              padding: 20px;
              margin: 0;
              font-family: monospace;
              font-size: 14px;
              background: white;
              border: 1px solid #eee;
            }
            object {
              width: 100%;
              height: 100%;
              background: white;
            }
          </style>
        </head>
        <body>
          <div class="preview-header">
            <div class="preview-title">${attachment.name}</div>
            <div class="header-actions">
              <a href="${attachment.url}" download="${attachment.name}" class="btn btn-primary">下载</a>
              <button class="btn btn-secondary" onclick="window.close()">关闭</button>
            </div>
          </div>
          <div class="preview-container">
            <div class="preview-content">
              <div class="loading">正在加载预览...</div>
            </div>
          </div>
        </body>
        </html>
      `)
      previewWindow.document.close()
      
      // 定义更新预览内容的函数
      const updatePreviewContent = (content) => {
        // 根据文件类型构建预览HTML
        let previewContent = ''
        if (fileExtension === '.pdf') {
          previewContent = `<object data="${content}" type="application/pdf" width="100%" height="100%">
                            <p>您的浏览器不支持PDF预览。<a href="${content}" download="${attachment.name}">点击下载</a></p>
                          </object>`
        } else if (['.jpg', '.jpeg', '.png', '.gif'].includes(fileExtension)) {
          previewContent = `<img src="${content}" alt="${attachment.name}">`
        } else if (fileExtension === '.txt') {
          previewContent = `<pre>${content}</pre>`
        } else {
          // 对于文档类型，使用iframe尝试预览
          previewContent = `<iframe src="${content}" width="100%" height="100%"></iframe>`
        }
        
        // 更新预览窗口内容
        const previewContainer = previewWindow.document.querySelector('.preview-content')
        if (previewContainer) {
          previewContainer.innerHTML = previewContent
        }
      }
      
      // 定义显示错误信息的函数
      const showError = (message) => {
        const previewContainer = previewWindow.document.querySelector('.preview-content')
        if (previewContainer) {
          previewContainer.innerHTML = `<div class="error">${message}<br><a href="${attachment.url}" download="${attachment.name}">点击下载文件</a></div>`
        }
      }
      
      // 定义读取文件内容的函数
      const readFileContent = (blob) => {
        const reader = new FileReader()
        
        reader.onload = (e) => {
          const content = e.target.result
          updatePreviewContent(content)
        }
        
        reader.onerror = () => {
          showError('读取文件失败')
        }
        
        // 根据文件类型选择读取方式
        if (fileExtension === '.txt') {
          reader.readAsText(blob)
        } else {
          reader.readAsDataURL(blob)
        }
      }
      
      // 检查attachment对象中是否有file属性
      if (attachment.file) {
        // 直接使用本地文件
        readFileContent(attachment.file)
      } else if (attachment.url) {
        // 检查URL是否是Blod URL
        if (attachment.url.startsWith('blob:')) {
          // Blob URL可能已经失效，显示友好提示
          showError('预览链接已失效，您可以重新上传文件或直接下载')
        } else {
          // 从服务器获取文件
          fetch(attachment.url)
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok')
              }
              return response.blob()
            })
            .then(blob => {
              readFileContent(blob)
            })
            .catch(error => {
              console.error('Error fetching file:', error)
              showError('获取文件失败，您可以重新上传文件或直接下载')
            })
        }
      } else {
        showError('文件信息不完整，您可以重新上传文件')
      }
    }
  } else {
    // 不支持预览的文件类型，直接下载
    window.open(attachment.url, '_blank')
  }
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
            <div v-else-if="journal.abstract" v-html="journal.abstract"></div>
            <p v-else>暂无摘要</p>
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
          
          <!-- 附件上传 -->
          <div class="journal-attachments">
            <h3>附件</h3>
            
            <!-- 编辑状态下显示上传按钮 -->
            <div v-if="isEditing" class="attachment-upload-section">
              <input 
                type="file" 
                id="attachment-upload" 
                style="display: none;" 
                @change="handleFileUpload"
              >
              <button 
                type="button" 
                class="upload-btn" 
                @click="triggerFileUpload"
              >
                上传附件
              </button>
              <p class="upload-hint">支持.doc, .docx, .pdf, .txt格式，单个文件不超过10MB</p>
            </div>
            
            <!-- 附件列表 -->
            <div class="attachments-list">
              <div 
                v-for="attachment in (isEditing ? (editedJournal.attachments || []) : (journal.attachments || []))" 
                :key="attachment.id" 
                class="attachment-item"
              >
                <div class="attachment-info">
                  <span class="attachment-name">{{ attachment.name }}</span>
                  <span class="attachment-size">({{ (attachment.size / 1024 / 1024).toFixed(2) }} MB)</span>
                </div>
                <div class="attachment-actions">
                  <!-- 预览按钮 -->
                  <button 
                    type="button" 
                    class="preview-btn" 
                    @click="previewAttachment(attachment)"
                  >
                    预览
                  </button>
                  
                  <!-- 编辑状态下显示删除按钮 -->
                  <button 
                    v-if="isEditing" 
                    type="button" 
                    class="delete-btn" 
                    @click="removeAttachment(attachment.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
              
              <!-- 无附件提示 -->
              <div v-if="(!isEditing && (!journal.attachments || journal.attachments.length === 0)) || (isEditing && (!editedJournal.attachments || editedJournal.attachments.length === 0))" class="no-attachments">
                <p>暂无附件</p>
              </div>
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
  background-color: #f5f5f5;
  padding: 2rem 0;
}

.review-records-content {
  flex: 1;
  padding: 0 2rem;
}

.review-records-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-top: 80px; /* 为固定导航栏留出空间 */
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

/* 附件样式 */
.journal-attachments {
  margin-top: 1.5rem;
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.journal-attachments h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
}

.attachment-upload-section {
  margin-bottom: 1.5rem;
}

.upload-btn {
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.upload-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.upload-hint {
  margin: 0.5rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.attachments-list {
  margin-top: 1rem;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #eee;
  margin-bottom: 0.75rem;
  transition: all 0.3s ease;
}

.attachment-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.attachment-name {
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  color: #666;
  font-size: 0.9rem;
}

.attachment-actions {
  display: flex;
  gap: 0.75rem;
}

.preview-btn, .delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.preview-btn {
  background-color: #27ae60;
  color: white;
}

.preview-btn:hover {
  background-color: #229954;
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.no-attachments {
  text-align: center;
  padding: 1.5rem;
  color: #666;
  font-style: italic;
  background-color: white;
  border-radius: 6px;
  border: 1px dashed #ddd;
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