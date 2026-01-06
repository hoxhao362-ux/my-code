import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    journals: JSON.parse(localStorage.getItem('journals')) || [],
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
      return state.reviewRecords.filter(record => record.journalId === journalId)
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
      const index = this.journals.findIndex(journal => journal.id === updatedJournal.id)
      if (index !== -1) {
        this.journals[index] = updatedJournal
        localStorage.setItem('journals', JSON.stringify(this.journals))
      }
    },

    // 删除期刊
    deleteJournal(journalId) {
      this.journals = this.journals.filter(journal => journal.id !== journalId)
      localStorage.setItem('journals', JSON.stringify(this.journals))
      // 同时删除相关的审稿记录
      this.reviewRecords = this.reviewRecords.filter(record => record.journalId !== journalId)
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
      const index = this.reviewRecords.findIndex(record => record.id === updatedRecord.id)
      if (index !== -1) {
        this.reviewRecords[index] = updatedRecord
        localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
      }
    },

    // 删除审稿记录
    deleteReviewRecord(recordId) {
      this.reviewRecords = this.reviewRecords.filter(record => record.id !== recordId)
      localStorage.setItem('reviewRecords', JSON.stringify(this.reviewRecords))
    },

    // 批量更新审稿记录
    updateReviewRecords(newRecords) {
      this.reviewRecords = newRecords
      localStorage.setItem('reviewRecords', JSON.stringify(newRecords))
    }
  }
})
