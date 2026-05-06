<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
<<<<<<< HEAD
=======
import { useI18n } from 'vue-i18n'
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
import Navigation from '../../../components/Navigation.vue'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const user = ref(userStore.user)

// 通知配置数据
const notificationConfig = ref({
  // 邮件模板
  emailTemplates: {
    submissionSuccess: {
      subject: '投稿成功通知',
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已成功提交，我们将尽快安排审核。\n\n投稿编号：{{submissionId}}\n投稿日期：{{submissionDate}}\n\n感谢您的投稿！\n\nPeerex Peer'
    },
    reviewResult: {
      subject: '审核结果通知',
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已完成审核，结果如下：\n\n审核结果：{{result}}\n审核意见：{{comments}}\n\n感谢您的投稿！\n\nPeerex Peer'
    },
    statusUpdate: {
      subject: '稿件状态更新通知',
<<<<<<< HEAD
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》状态已更新：\n\n当前状态：{{status}}\n更新时间：{{updateTime}}\n\n感谢您的投稿！\n\n期刊投稿平台'
    },
    reviewerInvitation: {
      subject: 'Invitation to Review: {{title}}',
      content: 'Dear Dr. {{reviewerName}},\n\nWe would like to invite you to review the manuscript entitled "{{title}}" (ID: {{submissionId}}) for our journal.\n\nAbstract:\n{{abstract}}\n\nPlease click the link below to accept or decline this invitation:\n{{link}}\n\nSincerely,\n\nThe Editorial Office\nJournal Platform'
    },
    recommendationResult: {
      subject: 'Update on Recommended Reviewer for {{title}}',
      content: 'Dear {{authorName}},\n\nWe are writing to inform you about the status of the reviewer you recommended, {{reviewerName}}, for your manuscript "{{title}}" (ID: {{submissionId}}).\n\nResult: {{result}}\nReason: {{reason}}\n\nThank you for your support.\n\nSincerely,\n\nThe Editorial Office\nJournal Platform'
=======
      content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》状态已更新：\n\n当前状态：{{status}}\n更新时间：{{updateTime}}\n\n感谢您的投稿！\n\nPeerex Peer'
    },
    reviewerInvitation: {
      subject: 'Invitation to Review: {{title}}',
      content: 'Dear Dr. {{reviewerName}},\n\nWe would like to invite you to review the manuscript entitled "{{title}}" (ID: {{submissionId}}) for our journal.\n\nAbstract:\n{{abstract}}\n\nPlease click the link below to accept or decline this invitation:\n{{link}}\n\nSincerely,\n\nThe Editorial Office\nPeerex Peer'
    },
    recommendationResult: {
      subject: 'Update on Recommended Reviewer for {{title}}',
      content: 'Dear {{authorName}},\n\nWe are writing to inform you about the status of the reviewer you recommended, {{reviewerName}}, for your manuscript "{{title}}" (ID: {{submissionId}}).\n\nResult: {{result}}\nReason: {{reason}}\n\nThank you for your support.\n\nSincerely,\n\nThe Editorial Office\nPeerex Peer'
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    }
  },
  
  // 短信模板
  smsTemplates: {
    submissionSuccess: {
      content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》已成功提交，投稿编号：{{submissionId}}，我们将尽快安排审核。'
    },
    reviewResult: {
      content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》审核结果：{{result}}，详情请查看邮件。'
    },
    statusUpdate: {
      content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》状态已更新为{{status}}，详情请查看邮件。'
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
<<<<<<< HEAD
    toastStore.add({ message: '请填写完整的公告信息', type: 'warning' })
=======
    toastStore.add({ message: t('notification.actions.incomplete'), type: 'warning' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
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
  
<<<<<<< HEAD
  toastStore.add({ message: '公告添加成功！', type: 'success' })
=======
  toastStore.add({ message: t('notification.actions.addSuccess'), type: 'success' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
}

// 编辑公告
const editAnnouncement = (announcement) => {
  editingAnnouncement.value = { ...announcement }
  isEditing.value = true
}

// 保存编辑的公告
const saveEditAnnouncement = () => {
  if (!editingAnnouncement.value.title || !editingAnnouncement.value.content) {
<<<<<<< HEAD
    toastStore.add({ message: '请填写完整的公告信息', type: 'warning' })
=======
    toastStore.add({ message: t('notification.actions.incomplete'), type: 'warning' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return
  }
  
  const index = announcements.value.findIndex(a => a.id === editingAnnouncement.value.id)
  if (index !== -1) {
    announcements.value[index] = { ...editingAnnouncement.value }
    
    // 保存到userStore
    userStore.setAnnouncements(announcements.value)
    
<<<<<<< HEAD
    toastStore.add({ message: '公告编辑成功！', type: 'success' })
=======
    toastStore.add({ message: t('notification.actions.editSuccess'), type: 'success' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
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
  if (confirm(t('notification.announcement.actions.confirmDelete'))) {
    announcements.value = announcements.value.filter(a => a.id !== id)
    
    // 保存到userStore
    userStore.setAnnouncements(announcements.value)
    
<<<<<<< HEAD
    toastStore.add({ message: '公告删除成功！', type: 'success' })
=======
    toastStore.add({ message: t('notification.actions.deleteSuccess'), type: 'success' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  }
}

// 保存配置
const saveConfig = () => {
  // 这里应该保存配置到服务器，目前模拟保存
<<<<<<< HEAD
  toastStore.add({ message: '通知配置已保存！', type: 'success' })
=======
  toastStore.add({ message: t('notification.actions.saveSuccess'), type: 'success' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
}

// 重置配置
const resetConfig = () => {
  // 这里保留原始重置逻辑，因为是Mock
  notificationConfig.value = {
    // 邮件模板
    emailTemplates: {
      submissionSuccess: {
        subject: '投稿成功通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已成功提交，我们将尽快安排审核。\n\n投稿编号：{{submissionId}}\n投稿日期：{{submissionDate}}\n\n感谢您的投稿！\n\nPeerex Peer'
      },
      reviewResult: {
        subject: '审核结果通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》已完成审核，结果如下：\n\n审核结果：{{result}}\n审核意见：{{comments}}\n\n感谢您的投稿！\n\nPeerex Peer'
      },
      statusUpdate: {
        subject: '稿件状态更新通知',
        content: '尊敬的{{username}}：\n\n您的投稿《{{title}}》状态已更新：\n\n当前状态：{{status}}\n更新时间：{{updateTime}}\n\n感谢您的投稿！\n\nPeerex Peer'
      },
      reviewerInvitation: {
        subject: 'Invitation to Review: {{title}}',
        content: 'Dear Dr. {{reviewerName}},\n\nWe would like to invite you to review the manuscript entitled "{{title}}" (ID: {{submissionId}}) for our journal.\n\nAbstract:\n{{abstract}}\n\nPlease click the link below to accept or decline this invitation:\n{{link}}\n\nSincerely,\n\nThe Editorial Office\nPeerex Peer'
      },
      recommendationResult: {
        subject: 'Update on Recommended Reviewer for {{title}}',
        content: 'Dear {{authorName}},\n\nWe are writing to inform you about the status of the reviewer you recommended, {{reviewerName}}, for your manuscript "{{title}}" (ID: {{submissionId}}).\n\nResult: {{result}}\nReason: {{reason}}\n\nThank you for your support.\n\nSincerely,\n\nThe Editorial Office\nPeerex Peer'
      }
    },
    
    // 短信模板
    smsTemplates: {
      submissionSuccess: {
        content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》已成功提交，投稿编号：{{submissionId}}，我们将尽快安排审核。'
      },
      reviewResult: {
        content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》审核结果：{{result}}，详情请查看邮件。'
      },
      statusUpdate: {
        content: '【Peerex Peer】尊敬的{{username}}，您的投稿《{{title}}》状态已更新为{{status}}，详情请查看邮件。'
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
<<<<<<< HEAD
  toastStore.add({ message: '配置已重置为默认值！', type: 'success' })
=======
  toastStore.add({ message: t('notification.actions.resetSuccess'), type: 'success' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
}

// 发送测试通知
const sendTestNotification = () => {
  toastStore.add({ message: 'Test notification sent!', type: 'success' })
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
        <h1>{{ $t('notification.title') }}</h1>
        <p class="subtitle">{{ $t('notification.subtitle') }}</p>
      </div>

      <section class="config-section">
        <div class="config-form-container">
          <form class="config-form">
            <div class="form-section">
              <h3>{{ $t('notification.reminderRules.title') }}</h3>
              
              <div class="settings-grid">
                <div class="setting-item">
                  <div class="setting-info">
                    <h4>{{ $t('notification.reminderRules.enableEmail') }}</h4>
                    <p class="setting-description">{{ $t('notification.reminderRules.enableEmailDesc') }}</p>
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
                    <h4>{{ $t('notification.reminderRules.enableSMS') }}</h4>
                    <p class="setting-description">{{ $t('notification.reminderRules.enableSMSDesc') }}</p>
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
                  <label>{{ $t('notification.reminderRules.submissionReminder') }}</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.submissionReminder" 
                    class="form-control"
                    min="0"
                    :placeholder="$t('notification.reminderRules.placeholder')"
                  >
                </div>
                
                <div class="form-group">
                  <label>{{ $t('notification.reminderRules.reviewReminder') }}</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.reviewReminder" 
                    class="form-control"
                    min="0"
                    :placeholder="$t('notification.reminderRules.placeholder')"
                  >
                </div>
                
                <div class="form-group">
                  <label>{{ $t('notification.reminderRules.statusUpdateReminder') }}</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.statusUpdateReminder" 
                    class="form-control"
                    min="0"
                    :placeholder="$t('notification.reminderRules.placeholder')"
                  >
                </div>
                
                <div class="form-group">
                  <label>{{ $t('notification.reminderRules.reviewInterval') }}</label>
                  <input 
                    type="number" 
                    v-model="notificationConfig.reminderRules.reviewInterval" 
                    class="form-control"
                    min="1"
                    :placeholder="$t('notification.reminderRules.placeholder')"
                  >
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>{{ $t('notification.emailTemplates.title') }}</h3>
              
              <div class="template-group">
                <h4>{{ $t('notification.emailTemplates.submissionSuccess') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.subject') }}</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.submissionSuccess.subject" 
                    class="form-control"
                    :placeholder="$t('notification.emailTemplates.placeholderSubject')"
                  >
                </div>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.submissionSuccess.content" 
                    class="form-control textarea-large"
                    rows="8"
                    :placeholder="$t('notification.emailTemplates.placeholderContent')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{submissionId}}, {{submissionDate}}</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>{{ $t('notification.emailTemplates.reviewResult') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.subject') }}</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.reviewResult.subject" 
                    class="form-control"
                    :placeholder="$t('notification.emailTemplates.placeholderSubject')"
                  >
                </div>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.reviewResult.content" 
                    class="form-control textarea-large"
                    rows="8"
                    :placeholder="$t('notification.emailTemplates.placeholderContent')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{result}}, {{comments}}</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>{{ $t('notification.emailTemplates.statusUpdate') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.subject') }}</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.statusUpdate.subject" 
                    class="form-control"
                    :placeholder="$t('notification.emailTemplates.placeholderSubject')"
                  >
                </div>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.statusUpdate.content" 
                    class="form-control textarea-large"
                    rows="8"
                    :placeholder="$t('notification.emailTemplates.placeholderContent')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{status}}, {{updateTime}}</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>{{ $t('notification.emailTemplates.reviewerInvitation') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.subject') }}</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.reviewerInvitation.subject" 
                    class="form-control"
                    :placeholder="$t('notification.emailTemplates.placeholderSubject')"
                  >
                </div>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.reviewerInvitation.content" 
                    class="form-control textarea-large"
                    rows="8"
                    :placeholder="$t('notification.emailTemplates.placeholderContent')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{reviewerName}}, {{title}}, {{submissionId}}, {{abstract}}, {{link}}</p>
                  </div>
                </div>
              </div>

              <div class="template-group">
                <h4>{{ $t('notification.emailTemplates.recommendationResult') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.subject') }}</label>
                  <input 
                    type="text" 
                    v-model="notificationConfig.emailTemplates.recommendationResult.subject" 
                    class="form-control"
                    :placeholder="$t('notification.emailTemplates.placeholderSubject')"
                  >
                </div>
                <div class="form-group">
                  <label>{{ $t('notification.emailTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.emailTemplates.recommendationResult.content" 
                    class="form-control textarea-large"
                    rows="8"
                    :placeholder="$t('notification.emailTemplates.placeholderContent')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{authorName}}, {{reviewerName}}, {{title}}, {{submissionId}}, {{result}}, {{reason}}</p>
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
                    <p>可用变量：{{authorName}}（作者姓名）、{{reviewerName}}（评审人姓名）、{{title}}（稿件标题）、{{submissionId}}（投稿编号）、{{result}}（结果）、{{reason}}（原因）</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>{{ $t('notification.smsTemplates.title') }}</h3>
              
              <div class="template-group">
                <h4>{{ $t('notification.smsTemplates.submissionSuccess') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.smsTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.submissionSuccess.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    :placeholder="$t('notification.smsTemplates.placeholder')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{submissionId}}</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>{{ $t('notification.smsTemplates.reviewResult') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.smsTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.reviewResult.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    :placeholder="$t('notification.smsTemplates.placeholder')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{result}}</p>
                  </div>
                </div>
              </div>
              
              <div class="template-group">
                <h4>{{ $t('notification.smsTemplates.statusUpdate') }}</h4>
                <div class="form-group">
                  <label>{{ $t('notification.smsTemplates.content') }}</label>
                  <textarea 
                    v-model="notificationConfig.smsTemplates.statusUpdate.content" 
                    class="form-control textarea-medium"
                    rows="3"
                    :placeholder="$t('notification.smsTemplates.placeholder')"
                  ></textarea>
                  <div class="template-tips">
                    <p>{{ $t('notification.emailTemplates.tips') }} {{username}}, {{title}}, {{status}}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 公告设置部分 -->
            <div class="form-section">
              <h3>{{ $t('notification.announcement.title') }}</h3>
              <p class="section-description">{{ $t('notification.announcement.desc') }}</p>
              
              <!-- 新增公告表单 -->
              <div class="announcement-form-container">
                <h4>{{ $t('notification.announcement.addTitle') }}</h4>
                <div class="announcement-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>{{ $t('notification.announcement.form.title') }}</label>
                      <input 
                        type="text" 
                        v-model="newAnnouncement.title" 
                        class="form-control"
                        :placeholder="$t('notification.announcement.form.titlePlaceholder')"
                      >
                    </div>
                  </div>
                  <div class="form-group">
                    <label>{{ $t('notification.announcement.form.content') }}</label>
                    <textarea 
                      v-model="newAnnouncement.content" 
                      class="form-control textarea-large"
                      rows="5"
                      :placeholder="$t('notification.announcement.form.contentPlaceholder')"
                    ></textarea>
                  </div>
                  <div class="form-actions-small">
                    <button type="button" class="btn btn-save" @click="addAnnouncement">{{ $t('notification.announcement.actions.add') }}</button>
                  </div>
                </div>
              </div>
              
              <!-- 编辑公告表单 -->
              <div class="announcement-form-container" v-if="isEditing">
                <h4>{{ $t('notification.announcement.editTitle') }}</h4>
                <div class="announcement-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>{{ $t('notification.announcement.form.title') }}</label>
                      <input 
                        type="text" 
                        v-model="editingAnnouncement.title" 
                        class="form-control"
                        :placeholder="$t('notification.announcement.form.titlePlaceholder')"
                      >
                    </div>
                  </div>
                  <div class="form-group">
                    <label>{{ $t('notification.announcement.form.content') }}</label>
                    <textarea 
                      v-model="editingAnnouncement.content" 
                      class="form-control textarea-large"
                      rows="5"
                      :placeholder="$t('notification.announcement.form.contentPlaceholder')"
                    ></textarea>
                  </div>
                  <div class="form-actions-small">
                    <button type="button" class="btn btn-reset" @click="cancelEditAnnouncement">{{ $t('notification.announcement.actions.cancel') }}</button>
                    <button type="button" class="btn btn-save" @click="saveEditAnnouncement">{{ $t('notification.announcement.actions.saveEdit') }}</button>
                  </div>
                </div>
              </div>
              
              <!-- 公告列表 -->
              <div class="announcements-list-container">
                <h4>{{ $t('notification.announcement.listTitle') }}</h4>
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
                        {{ $t('notification.announcement.actions.edit') }}
                      </button>
                      <button 
                        type="button" 
                        class="btn btn-delete-small" 
                        @click="deleteAnnouncement(announcement.id)"
                      >
                        {{ $t('notification.announcement.actions.delete') }}
                      </button>
                    </div>
                  </div>
                  
                  <div v-if="announcements.length === 0" class="empty-announcements">
                    <p>{{ $t('notification.announcement.empty') }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-reset" @click="resetConfig">{{ $t('notification.actions.reset') }}</button>
              <button type="button" class="btn btn-save" @click="saveConfig">{{ $t('notification.actions.save') }}</button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
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