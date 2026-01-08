import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    journals: JSON.parse(localStorage.getItem('journals')) || [],
    // 公告数据
    announcements: JSON.parse(localStorage.getItem('announcements')) || [
      { id: 1, title: '2026年期刊投稿平台征稿启事', content: '尊敬的各位作者，2026年期刊投稿平台开始全面征稿，欢迎广大作者踊跃投稿。', date: '2026-01-01' },
      { id: 2, title: '投稿系统升级通知', content: '为了提供更好的服务，我们将于2026年1月15日进行系统升级维护，期间投稿功能将暂停使用。', date: '2026-01-10' },
      { id: 3, title: '关于调整审稿周期的通知', content: '自2026年2月1日起，我平台将调整审稿周期，一般稿件的审稿时间将缩短至1-2周。', date: '2026-01-12' }
    ],
    // 意见收纳数据（联系我们和意见反馈）
    feedbackMessages: JSON.parse(localStorage.getItem('feedbackMessages')) || [],
    // 默认审稿阶段
    reviewStages: ['初审', '复审', '终审'],
    modules: JSON.parse(localStorage.getItem('modules')) || [
      '医学影像',
      '药物研发',
      '临床研究',
      '公共卫生',
      '生物信息学',
      '人工智能',
      '其他'
    ],
    adminCode: localStorage.getItem('adminCode') || 'admin123',
    reviewerCode: localStorage.getItem('reviewerCode') || 'reviewer123',
    authorCode: localStorage.getItem('authorCode') || 'author123',
    reviewRecords: JSON.parse(localStorage.getItem('reviewRecords')) || []
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentRole: (state) => state.user?.role || 'user',
    userJournals: (state) => {
      if (!state.user) return []
      return state.journals.filter(journal => journal.author === state.user.username)
    },
    pendingJournals: (state) => {
      return state.journals.filter(journal => journal.status === '审稿中')
    },
    journalReviewRecords: (state) => (journalId) => {
      return state.reviewRecords.filter(record => String(record.journalId) === String(journalId))
    },
    userReviewRecords: (state) => {
      if (!state.user) return []
      return state.reviewRecords.filter(record => record.reviewerId === state.user.id || record.journalAuthor === state.user.username)
    }
  },

  actions: {
    // 登录
    login(userData) {
      this.user = userData
      localStorage.setItem('user', JSON.stringify(userData))
    },

    // 登出
    logout() {
      this.user = null
      localStorage.removeItem('user')
    },

    // 更新用户信息
    updateUser(userData) {
      this.user = { ...this.user, ...userData }
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    // 更新管理员辨识密码
    updateAdminCode(newCode) {
      this.adminCode = newCode
      localStorage.setItem('adminCode', newCode)
    },

    // 更新审核员邀请码
    updateReviewerCode(newCode) {
      this.reviewerCode = newCode
      localStorage.setItem('reviewerCode', newCode)
    },

    // 更新作者邀请码
    updateAuthorCode(newCode) {
      this.authorCode = newCode
      localStorage.setItem('authorCode', newCode)
    },

    // 添加期刊
    addJournal(journal) {
      this.journals.push(journal)
      localStorage.setItem('journals', JSON.stringify(this.journals))
    },

    // 更新期刊
    updateJournal(updatedJournal) {
      const index = this.journals.findIndex(journal => String(journal.id) === String(updatedJournal.id))
      if (index !== -1) {
        this.journals[index] = updatedJournal
        localStorage.setItem('journals', JSON.stringify(this.journals))
      }
    },

    // 删除期刊
    deleteJournal(journalId) {
      this.journals = this.journals.filter(journal => String(journal.id) !== String(journalId))
      localStorage.setItem('journals', JSON.stringify(this.journals))
      // 同时删除相关的审稿记录
      this.reviewRecords = this.reviewRecords.filter(record => String(record.journalId) !== String(journalId))
      localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
    },

    // 批量更新期刊
    updateJournals(newJournals) {
      this.journals = newJournals
      localStorage.setItem('journals', JSON.stringify(newJournals))
    },

    // 添加模块
    addModule(moduleName) {
      if (!this.modules.includes(moduleName)) {
        this.modules.push(moduleName)
        localStorage.setItem('modules', JSON.stringify(this.modules))
      }
    },

    // 删除模块
    removeModule(moduleName) {
      if (moduleName !== '其他') {
        this.modules = this.modules.filter(m => m !== moduleName)
        localStorage.setItem('modules', JSON.stringify(this.modules))
        // 将使用该模块的期刊转移到'其他'模块
        this.journals.forEach(journal => {
          if (journal.module === moduleName) {
            journal.module = '其他'
          }
        })
        localStorage.setItem('journals', JSON.stringify(this.journals))
      }
    },

    // 更新模块列表
    updateModules(newModules) {
      this.modules = newModules
      localStorage.setItem('modules', JSON.stringify(newModules))
    },

    // 添加审稿记录
    addReviewRecord(record) {
      this.reviewRecords.push(record)
      localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
    },

    // 更新审稿记录
    updateReviewRecord(updatedRecord) {
      const index = this.reviewRecords.findIndex(record => String(record.id) === String(updatedRecord.id))
      if (index !== -1) {
        this.reviewRecords[index] = updatedRecord
        localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
      }
    },

    // 删除审稿记录
    deleteReviewRecord(recordId) {
      this.reviewRecords = this.reviewRecords.filter(record => String(record.id) !== String(recordId))
      localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
    },

    // 批量更新审稿记录
    updateReviewRecords(newRecords) {
      this.reviewRecords = newRecords
      localStorage.setItem('reviewRecords', JSON.stringify(newRecords))
    },
    
    // 设置公告列表
    setAnnouncements(newAnnouncements) {
      this.announcements = newAnnouncements
      localStorage.setItem('announcements', JSON.stringify(newAnnouncements))
    },
    
    // 添加反馈消息
    addFeedbackMessage(message) {
      const newMessage = {
        id: Date.now(),
        ...message,
        createdAt: new Date().toISOString(),
        status: '未处理'
      }
      this.feedbackMessages.push(newMessage)
      localStorage.setItem('feedbackMessages', JSON.stringify(this.feedbackMessages))
    },
    
    // 获取所有反馈消息
    getFeedbackMessages() {
      return this.feedbackMessages
    },
    
    // 更新反馈消息状态
    updateFeedbackMessageStatus(messageId, status) {
      const message = this.feedbackMessages.find(msg => String(msg.id) === String(messageId))
      if (message) {
        message.status = status
        localStorage.setItem('feedbackMessages', JSON.stringify(this.feedbackMessages))
      }
    },
    
    // 删除反馈消息
    deleteFeedbackMessage(messageId) {
      this.feedbackMessages = this.feedbackMessages.filter(msg => String(msg.id) !== String(messageId))
      localStorage.setItem('feedbackMessages', JSON.stringify(this.feedbackMessages))
    },
    
    // 批量删除反馈消息
    deleteMultipleFeedbackMessages(messageIds) {
      this.feedbackMessages = this.feedbackMessages.filter(msg => !messageIds.includes(String(msg.id)))
      localStorage.setItem('feedbackMessages', JSON.stringify(this.feedbackMessages))
    }
  }
})
