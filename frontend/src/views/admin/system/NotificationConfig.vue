<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 通知配置数据
const notificationConfig = ref({
  // 邮件模板
  emailTemplates: {
    submissionSuccess: {
      subject: '投稿成功通知',
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已成功提交，我们将尽快安排审核。\n\n投稿编号：{{submissionId}}\n投稿日期：{{submissionDate}}\n\n感谢您的投稿！\n\n期刊投稿平台'
    },
    reviewResult: {
      subject: '审核结果通知',
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已完成审核，结果如下：\n\n审核结果：{{result}}\n审核意见：{{comments}}\n\n感谢您的投稿！\n\n期刊投稿平台'
    },
    statusUpdate: {
      subject: '稿件状态更新通知',
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》状态已更新：\n\n当前状态：{{status}}\n更新时间：{{updateTime}}\n\n感谢您的投稿！\n\n期刊投稿平台'
    },
    reviewerInvitation: {
      subject: 'Invitation to Review: {{title}}',
      content: 'Dear Dr. {{reviewerName}},\n\nWe would like to invite you to review the manuscript entitled "{{title}}" (ID: {{submissionId}}) for our journal.\n\nAbstract:\n{{abstract}}\n\nPlease click the link below to accept or decline this invitation:\n{{link}}\n\nSincerely,\n\nThe Editorial Office\nJournal Platform'
    },
    recommendationResult: {
      subject: 'Update on Recommended Reviewer for {{title}}',
      content: 'Dear {{writerName}},\n\nWe are writing to inform you about the status of the reviewer you recommended, {{reviewerName}}, for your manuscript "{{title}}" (ID: {{submissionId}}).\n\nResult: {{result}}\nReason: {{reason}}\n\nThank you for your support.\n\nSincerely,\n\nThe Editorial Office\nJournal Platform'
    }
  },
  
  // 短信模板
  smsTemplates: {
    submissionSuccess: {
      content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》已成功提交，投稿编号：{{submissionId}}，我们将尽快安排审核。'
    },
    reviewResult: {
      content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》审核结果：{{result}}，详情请查看邮件。'
    },
    statusUpdate: {
      content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》状态已更新为{{status}}，详情请查看邮件。'
    }
  },
  
  // 提醒规则
  reminderRules: {
    enableEmail: true,
    enableSMS: false,
    submissionReminder: 1, // 小时
    reviewReminder: 24, // 小时
    statusUpdateReminder: 1, // 小时
    reviewInterval: 7 // 天
  }
})

// 公告数据 - 从userStore加载，确保数据同步
const announcements = ref([...userStore.announcements])

// 新公告表单
const newAnnouncement = ref({
  title: '',
  content: ''
})

// 编辑中的公告
const editingAnnouncement = ref(null)
const isEditing = ref(false)

// 添加公告
const addAnnouncement = () => {
  if (!newAnnouncement.value.title || !newAnnouncement.value.content) {
    alert('请填写完整的公告信息')
    return
  }
  
  const now = new Date()
  const dateStr = now.toISOString().split('T')[0]
  
  const announcement = {
    id: Date.now(),
    title: newAnnouncement.value.title,
    content: newAnnouncement.value.content,
    date: dateStr
  }
  
  announcements.value.unshift(announcement)
  
  // 清空表单
  newAnnouncement.value = {
    title: '',
    content: ''
  }
  
  // 保存到userStore，以便在主页显示
  userStore.setAnnouncements(announcements.value)
  
  alert('公告添加成功！')
}

// 编辑公告
const editAnnouncement = (announcement) => {
  editingAnnouncement.value = { ...announcement }
  isEditing.value = true
}

// 保存编辑的公告
const saveEditAnnouncement = () => {
  if (!editingAnnouncement.value.title || !editingAnnouncement.value.content) {
    alert('请填写完整的公告信息')
    return
  }
  
  const index = announcements.value.findIndex(a => a.id === editingAnnouncement.value.id)
  if (index !== -1) {
    announcements.value[index] = { ...editingAnnouncement.value }
    
    // 保存到userStore
    userStore.setAnnouncements(announcements.value)
    
    alert('公告编辑成功！')
    cancelEditAnnouncement()
  }
}

// 取消编辑
const cancelEditAnnouncement = () => {
  editingAnnouncement.value = null
  isEditing.value = false
}

// 删除公告
const deleteAnnouncement = (id) => {
  if (confirm('确定要删除这条公告吗？')) {
    announcements.value = announcements.value.filter(a => a.id !== id)
    
    // 保存到userStore
    userStore.setAnnouncements(announcements.value)
    
    alert('公告删除成功！')
  }
}

// 保存配置
const saveConfig = () => {
  // 这里应该保存配置到服务器，目前模拟保存
  alert('通知配置已保存！')
}

// 重置配置
const resetConfig = () => {
  notificationConfig.value = {
    // 邮件模板
    emailTemplates: {
      submissionSuccess: {
        subject: '投稿成功通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已成功提交，我们将尽快安排审核。\n\n投稿编号：{{submissionId}}\n投稿日期：{{submissionDate}}\n\n感谢您的投稿！\n\n期刊投稿平台'
      },
      reviewResult: {
        subject: '审核结果通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已完成审核，结果如下：\n\n审核结果：{{result}}\n审核意见：{{comments}}\n\n感谢您的投稿！\n\n期刊投稿平台'
      },
      statusUpdate: {
        subject: '稿件状态更新通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》状态已更新：\n\n当前状态：{{status}}\n更新时间：{{updateTime}}\n\n感谢您的投稿！\n\n期刊投稿平台'
      }
    },
    
    // 短信模板
    smsTemplates: {
      submissionSuccess: {
        content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》已成功提交，投稿编号：{{submissionId}}，我们将尽快安排审核。'
      },
      reviewResult: {
        content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》审核结果：{{result}}，详情请查看邮件。'
      },
      statusUpdate: {
        content: '【期刊投稿平台】尊敬的{{username}}，您的投稿《{{title}}》状态已更新为{{status}}，详情请查看邮件。'
      }
    },
    
    // 提醒规则
    reminderRules: {
      enableEmail: true,
      enableSMS: false,
      submissionReminder: 1, // 小时
      reviewReminder: 24, // 小时
      statusUpdateReminder: 1, // 小时
      reviewInterval: 7 // 天
    }
  }
  alert('配置已重置为默认值！')
}
</script>

<template>
  <div class="admin-notification-config-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-system-notification'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 通知配置内容 -->
    <main class="content">
      <div class="header">
        <h1>系统设置 - 通知设置</h1>
        <p class="subtitle">管理平台的通知模板和提醒规则</p>
      </div>

      <section class="config-section">
        <div class="config-form-container">
          <form class="config-form">
            <div class="form-section">
              <h3>提醒规则</h3>
              
              <div class="settings-grid">
                <div class="setting-item">
                  <div class="setting-info">
                    <h4>启用邮件通知</h4>
                    <p class="setting-description">是否通过邮件发送通知</p>
                  </div>
                  <div class="setting-control">
                    <label class="toggle-switch">
                      <input 
                        type="checkbox" 
                        v-model="notificationConfig.reminderRules.enableEmail"
                      >
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>
                
                <div class="setting-item">
                  <div class="setting-info">
                    <h4>启用短信通知</h4>
                    <p class="setting-description">是否通过短信发送通知</p>
                  </div>
                  <div class="setting-control">
                    <label class="toggle-switch">
                      <input 
                        type="checkbox" 
                        v-model="notificationConfig.reminderRules.enableSMS"
                      >
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>投稿后通知时间（小时）</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.submissionReminder" 
                    class="form-control"
                    min="0"
                    placeholder="请输入通知时间"
                  >
                </div>
                
                <div class="form-group">
                  <label>审核后通知时间（小时）</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.reviewReminder" 
                    class="form-control"
                    min="0"
                    placeholder="请输入通知时间"
                  >
                </div>
                
                <div class="form-group">
                  <label>状态更新后通知时间（小时）</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.statusUpdateReminder" 
                    class="form-control"
                    min="0"
                    placeholder="请输入通知时间"
                  >
                </div>
                
                <div class="form-group">
                  <label>审核周期提醒（天）</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.reviewInterval" 
                    class="form-control"
                    min="1"
                    placeholder="请输入审核周期"
                  >
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>邮件模板</h3>
              
              <div class="template-group">
                <h4>投稿成功通知</h4>
                <div class="form-group">
                  <label>邮件主题</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.submissionSuccess.subject" 
                    class="form-control"
                    placeholder="请输入邮件主题"
                  >
                </div>
                <div class="form-group">
                  <label>邮件内容</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.submissionSuccess.content" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入邮件内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{submissionId}}（投稿编号）、{{submissionDate}}（投稿日期）</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>审核结果通知</h4>
                <div class="form-group">
                  <label>邮件主题</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.reviewResult.subject" 
                    class="form-control"
                    placeholder="请输入邮件主题"
                  >
                </div>
                <div class="form-group">
                  <label>邮件内容</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.reviewResult.content" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入邮件内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{result}}（审核结果）、{{comments}}（审核意见）</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>状态更新通知</h4>
                <div class="form-group">
                  <label>邮件主题</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.statusUpdate.subject" 
                    class="form-control"
                    placeholder="请输入邮件主题"
                  >
                </div>
                <div class="form-group">
                  <label>邮件内容</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.statusUpdate.content" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入邮件内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{status}}（当前状态）、{{updateTime}}（更新时间）</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>评审邀请通知（Reviewer Invitation）</h4>
                <div class="form-group">
                  <label>邮件主题</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.reviewerInvitation.subject" 
                    class="form-control"
                    placeholder="请输入邮件主题"
                  >
                </div>
                <div class="form-group">
                  <label>邮件内容</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.reviewerInvitation.content" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入邮件内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{reviewerName}}（评审人姓名）、{{title}}（稿件标题）、{{submissionId}}（投稿编号）、{{abstract}}（摘要）、{{link}}（接受链接）</p>
                  </div>
                </div>
              </div>

              <div class="template-group">
                <h4>作者推荐结果通知（Recommendation Result）</h4>
                <div class="form-group">
                  <label>邮件主题</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.recommendationResult.subject" 
                    class="form-control"
                    placeholder="请输入邮件主题"
                  >
                </div>
                <div class="form-group">
                  <label>邮件内容</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.recommendationResult.content" 
                    class="form-control textarea-large"
                    rows="8"
                    placeholder="请输入邮件内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{writerName}}（撰稿人姓名）、{{reviewerName}}（评审人姓名）、{{title}}（稿件标题）、{{submissionId}}（投稿编号）、{{result}}（结果）、{{reason}}（原因）</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>短信模板</h3>
              
              <div class="template-group">
                <h4>投稿成功通知</h4>
                <div class="form-group">
                  <label>短信内容</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.submissionSuccess.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    placeholder="请输入短信内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{submissionId}}（投稿编号）</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>审核结果通知</h4>
                <div class="form-group">
                  <label>短信内容</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.reviewResult.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    placeholder="请输入短信内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{result}}（审核结果）</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>状态更新通知</h4>
                <div class="form-group">
                  <label>短信内容</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.statusUpdate.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    placeholder="请输入短信内容"
                  ></textarea>
                  <div class="template-tips">
                    <p>可用变量：{{username}}（用户名）、{{title}}（稿件标题）、{{status}}（当前状态）</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 公告设置部分 -->
            <div class="form-section">
              <h3>公告设置</h3>
              <p class="section-description">管理平台的公告信息，发布的公告将在主页展示</p>
              
              <!-- 新增公告表单 -->
              <div class="announcement-form-container">
                <h4>新增公告</h4>
                <div class="announcement-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>公告标题</label>
                      <input 
                        type="text" 
                        v-model="newAnnouncement.title" 
                        class="form-control"
                        placeholder="请输入公告标题"
                      >
                    </div>
                  </div>
                  <div class="form-group">
                    <label>公告内容</label>
                    <textarea 
                      v-model="newAnnouncement.content" 
                      class="form-control textarea-large"
                      rows="5"
                      placeholder="请输入公告内容"
                    ></textarea>
                  </div>
                  <div class="form-actions-small">
                    <button type="button" class="btn btn-save" @click="addAnnouncement">添加公告</button>
                  </div>
                </div>
              </div>
              
              <!-- 编辑公告表单 -->
              <div class="announcement-form-container" v-if="isEditing">
                <h4>编辑公告</h4>
                <div class="announcement-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>公告标题</label>
                      <input 
                        type="text" 
                        v-model="editingAnnouncement.title" 
                        class="form-control"
                        placeholder="请输入公告标题"
                      >
                    </div>
                  </div>
                  <div class="form-group">
                    <label>公告内容</label>
                    <textarea 
                      v-model="editingAnnouncement.content" 
                      class="form-control textarea-large"
                      rows="5"
                      placeholder="请输入公告内容"
                    ></textarea>
                  </div>
                  <div class="form-actions-small">
                    <button type="button" class="btn btn-reset" @click="cancelEditAnnouncement">取消</button>
                    <button type="button" class="btn btn-save" @click="saveEditAnnouncement">保存编辑</button>
                  </div>
                </div>
              </div>
              
              <!-- 公告列表 -->
              <div class="announcements-list-container">
                <h4>公告列表</h4>
                <div class="announcements-list">
                  <div 
                    v-for="announcement in announcements" 
                    :key="announcement.id" 
                    class="announcement-item"
                  >
                    <div class="announcement-info">
                      <div class="announcement-header">
                        <h5 class="announcement-title">{{ announcement.title }}</h5>
                        <span class="announcement-date">{{ announcement.date }}</span>
                      </div>
                      <p class="announcement-content">{{ announcement.content }}</p>
                    </div>
                    <div class="announcement-actions">
                      <button 
                        type="button" 
                        class="btn btn-edit-small" 
                        @click="editAnnouncement(announcement)"
                      >
                        编辑
                      </button>
                      <button 
                        type="button" 
                        class="btn btn-delete-small" 
                        @click="deleteAnnouncement(announcement.id)"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                  
                  <div v-if="announcements.length === 0" class="empty-announcements">
                    <p>暂无公告，请添加第一条公告</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-reset" @click="resetConfig">重置</button>
              <button type="button" class="btn btn-save" @click="saveConfig">保存配置</button>
            </div>
          </form>
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
.admin-notification-config-container {
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

.content.embedded-content {
  margin-top: 0;
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

/* 配置区域样式 */
.config-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

.config-form-container {
  max-width: 900px;
}

/* 表单样式 */
.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

/* 设置项样式 */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.setting-info h4 {
  font-size: 1rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.setting-description {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin: 0;
}

/* 切换开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #3498db;
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px #3498db;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* 表单行样式 */
.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.95rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.textarea-large {
  resize: vertical;
  min-height: 150px;
  font-family: inherit;
}

.textarea-medium {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* 模板组样式 */
.template-group {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.template-group h4 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.template-tips {
  background-color: #e3f2fd;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.template-tips p {
  margin: 0;
  font-size: 0.85rem;
  color: #3498db;
}

/* 按钮样式 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
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

.btn-save {
  background-color: #2ecc71;
  color: white;
}

.btn-save:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

/* 公告设置样式 */
.section-description {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0 0 1.5rem 0;
  font-weight: 400;
}

.announcement-form-container {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.announcement-form-container h4 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.announcement-form {
  max-width: 600px;
}

.form-actions-small {
  display: flex;
  justify-content: flex-start;
  margin-top: 1rem;
  gap: 1rem;
}

.form-actions-small .btn {
  min-width: 100px;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
}

.announcements-list-container {
  margin-bottom: 1rem;
}

.announcements-list-container h4 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.announcement-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  gap: 1rem;
}

.announcement-info {
  flex: 1;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.announcement-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

.announcement-date {
  font-size: 0.9rem;
  color: #7f8c8d;
  background: white;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  border: 1px solid #e9ecef;
}

.announcement-content {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.announcement-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
}

.btn-edit-small,
.btn-delete-small {
  min-width: 80px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit-small {
  background-color: #3498db;
  color: white;
}

.btn-edit-small:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(52, 152, 219, 0.3);
}

.btn-delete-small {
  background-color: #e74c3c;
  color: white;
}

.btn-delete-small:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);
}

.empty-announcements {
  text-align: center;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
  color: #7f8c8d;
}

.empty-announcements p {
  margin: 0;
  font-size: 1rem;
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
  
  .config-section {
    padding: 1.5rem;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .template-group {
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .announcement-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .announcement-actions {
    flex-direction: row;
    align-items: center;
    margin-top: 1rem;
    width: 100%;
    justify-content: flex-start;
  }
  
  .btn-edit-small,
  .btn-delete-small {
    min-width: 120px;
  }
  
  .announcement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .form-actions-small {
    flex-direction: column;
  }
  
  .form-actions-small .btn {
    width: 100%;
  }
}
</style>