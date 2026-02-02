import { defineStore } from 'pinia'
import { userApi, journalApi, reviewApi, adminApi } from '../utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息 - 从localStorage加载，保留登录状态
    user: JSON.parse(localStorage.getItem('user')) || null,
    // 公告数据 - 从localStorage加载，保留公告状态
    announcements: JSON.parse(localStorage.getItem('announcements')) || [
      { id: 1, title: '2026年期刊投稿平台征稿启事', content: '尊敬的各位作者，2026年期刊投稿平台开始全面征稿，欢迎广大作者踊跃投稿。', date: '2026-01-01' },
      { id: 2, title: '投稿系统升级通知', content: '为了提供更好的服务，我们将于2026年1月15日进行系统升级维护，期间投稿功能将暂停使用。', date: '2026-01-10' },
      { id: 3, title: '关于调整审稿周期的通知', content: '自2026年2月1日起，我平台将调整审稿周期，一般稿件的审稿时间将缩短至1-2周。', date: '2026-01-12' }
    ],
    // 基础配置数据 - 从localStorage加载，保留配置状态
    basicConfig: JSON.parse(localStorage.getItem('basicConfig')) || {
      platformName: '期刊投稿平台',
      platformLogo: '',
      submissionRules: '1. 投稿内容必须符合学术规范\n2. 禁止抄袭和剽窃\n3. 所有投稿将经过严格审核\n4. 审核周期一般为1-2周\n5. 最终解释权归平台所有',
      contactEmail: 'contact@example.com',
      contactPhone: '13800138000',
      copyrightInfo: '© 2026 期刊投稿平台. All rights reserved.'
    },
    // 审稿阶段
    reviewStages: ['初审', '复审', '终审'],
    // 模块列表 - 从localStorage加载，保留模块状态
    modules: JSON.parse(localStorage.getItem('modules')) || [
      '医学影像',
      '药物研发',
      '临床研究',
      '公共卫生',
      '生物信息学',
      '人工智能',
      '其他'
    ],
    // 邀请码设置 - 从localStorage加载，保留邀请码状态
    invitationCodes: JSON.parse(localStorage.getItem('invitationCodes')) || {
      admin: 'ADMIN2026',
      reviewer: 'REVIEWER2026'
    },
    // 期刊列表（用于首页显示）
    journals: JSON.parse(localStorage.getItem('journals')) || [
      {
        id: 1,
        title: '医学影像技术的发展趋势',
        author: 'author1',
        module: '医学影像',
        status: '已发表',
        submissionDate: '2026-01-10',
        publicationDate: '2026-01-15',
        abstract: '本文详细介绍了医学影像技术的最新发展趋势，包括AI辅助诊断、3D打印技术在医学影像中的应用等。',
        keywords: '医学影像,AI辅助诊断,3D打印',
        fileUrl: '/vite.svg',
        reviews: []
      },
      {
        id: 2,
        title: '基于深度学习的药物研发方法',
        author: 'author2',
        module: '药物研发',
        status: '待审核',
        submissionDate: '2026-01-12',
        abstract: '本文探讨了深度学习在药物研发中的应用，包括分子结构预测、药物靶点识别等方面。',
        keywords: '深度学习,药物研发,分子结构',
        fileUrl: '/vite.svg',
        reviews: []
      },
      {
        id: 3,
        title: '临床研究中的大数据分析方法',
        author: 'author3',
        module: '临床研究',
        status: '审稿中',
        submissionDate: '2026-01-08',
        abstract: '本文介绍了临床研究中大数据分析的常用方法和工具，以及如何处理和分析海量临床数据。',
        keywords: '临床研究,大数据分析,数据处理',
        fileUrl: '/vite.svg',
        reviews: [
          { reviewer: 'reviewer1', status: '已审核', comment: '文章内容详实，方法可行', rating: 4 }
        ]
      },
      {
        id: 4,
        title: '公共卫生应急管理体系建设',
        author: 'author4',
        module: '公共卫生',
        status: '已发表',
        submissionDate: '2026-01-05',
        publicationDate: '2026-01-10',
        abstract: '本文分析了当前公共卫生应急管理体系的现状和存在的问题，并提出了相应的改进建议。',
        keywords: '公共卫生,应急管理,体系建设',
        fileUrl: '/vite.svg',
        reviews: [
          { reviewer: 'reviewer2', status: '已审核', comment: '文章具有重要的现实意义', rating: 5 }
        ]
      },
      {
        id: 5,
        title: '生物信息学在基因测序中的应用',
        author: 'author1',
        module: '生物信息学',
        status: '已发表',
        submissionDate: '2026-01-03',
        publicationDate: '2026-01-08',
        abstract: '本文综述了生物信息学在基因测序中的应用，包括序列比对、基因注释、变异检测等方面。',
        keywords: '生物信息学,基因测序,序列比对',
        fileUrl: '/vite.svg',
        reviews: [
          { reviewer: 'reviewer3', status: '已审核', comment: '文章内容全面，参考文献丰富', rating: 4 }
        ]
      }
    ],
    // 反馈消息列表
    feedbackMessages: [],
    // 用户列表（用于管理员角色管理）
    users: JSON.parse(localStorage.getItem('users')) || [
      { id: 1, username: 'admin', role: 'admin', email: 'admin@example.com', phone: '13800138000', status: 'active' },
      { id: 2, username: 'reviewer1', role: 'reviewer', email: 'reviewer1@example.com', phone: '13800138001', status: 'active' },
      { id: 3, username: 'author1', role: 'author', email: 'author1@example.com', phone: '13800138002', status: 'active' },
      { id: 4, username: 'user1', role: 'user', email: 'user1@example.com', phone: '13800138003', status: 'active' },
      { id: 5, username: 'user2', role: 'user', email: 'user2@example.com', phone: '13800138004', status: 'inactive' },
      { id: 6, username: 'reviewer2', role: 'reviewer', email: 'reviewer2@example.com', phone: '13800138005', status: 'active' },
      { id: 7, username: 'author2', role: 'author', email: 'author2@example.com', phone: '13800138006', status: 'active' },
      { id: 8, username: 'author3', role: 'author', email: 'author3@example.com', phone: '13800138007', status: 'active' },
      { id: 9, username: 'user3', role: 'user', email: 'user3@example.com', phone: '13800138008', status: 'active' },
      { id: 10, username: 'reviewer3', role: 'reviewer', email: 'reviewer3@example.com', phone: '13800138009', status: 'active' },
      { id: 11, username: 'user4', role: 'user', email: 'user4@example.com', phone: '13800138010', status: 'inactive' },
      { id: 12, username: 'author4', role: 'author', email: 'author4@example.com', phone: '13800138011', status: 'active' }
    ]
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentRole: (state) => state.user?.role || 'user',
    userJournals: (state) => {
      if (!state.user) return []
      return state.journals.filter(journal => journal.author === state.user.username)
    },
    pendingJournals: (state) => {
      return state.journals.filter(journal => journal.status === '待审核' || journal.status === '审稿中')
    },
    // 角色优先级：admin > reviewer > author > user
    // 检查用户是否具有指定角色的权限（高权限角色包含低权限角色的所有权限）
    hasRolePermission: (state) => (requiredRole) => {
      const rolePriority = {
        admin: 3,
        reviewer: 2,
        author: 1,
        user: 0
      }
      const userRole = state.user?.role || 'user'
      return rolePriority[userRole] >= rolePriority[requiredRole]
    }
  },

  actions: {
    // 登录
    async login(credentials) {
      try {
        const response = await userApi.login(credentials)
        let userData = null
        
        if (!response) {
          // API请求失败，根据提供的角色或用户名自动判断角色
          // 角色优先级：1. credentials中提供的role 2. 根据用户名判断 3. 默认角色
          let role = credentials.role || 
                    (credentials.username === 'admin' ? 'admin' : 
                     credentials.username === 'reviewer' ? 'reviewer' : 
                     credentials.username === 'author' ? 'author' : 
                     'user')
          
          // 从用户列表中查找完整用户信息
          const fullUserInfo = this.users.find(u => u.username === credentials.username)
          
          userData = {
            username: credentials.username,
            role: role,
            // 添加完整的用户信息
            email: fullUserInfo?.email || `${credentials.username}@example.com`,
            phone: fullUserInfo?.phone || '13800138000'
          }
        } else {
          // API请求成功，使用返回的数据
          userData = {
            ...response,
            username: credentials.username,
            role: response.role || 'user'
          }
        }
        
        this.user = userData
        localStorage.setItem('user', JSON.stringify(userData))
        // 登录时刷新期刊数据，确保从localStorage获取最新数据
        this.refreshJournals()
        return userData
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },
    
    // 刷新期刊数据，从localStorage重新读取
    refreshJournals() {
      try {
        const journalsFromStorage = JSON.parse(localStorage.getItem('journals') || '[]')
        this.journals = journalsFromStorage
      } catch (error) {
        console.error('刷新期刊数据失败:', error)
        this.journals = []
      }
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
      if (moduleName === '其他') return // 不允许删除'其他'模块
      this.modules = this.modules.filter(module => module !== moduleName)
      localStorage.setItem('modules', JSON.stringify(this.modules))
    },
    
    // 更新邀请码
    updateInvitationCode(type, code) {
      this.invitationCodes[type] = code
      localStorage.setItem('invitationCodes', JSON.stringify(this.invitationCodes))
    },
    
    // 更新所有邀请码
    updateAllInvitationCodes(codes) {
      this.invitationCodes = { ...this.invitationCodes, ...codes }
      localStorage.setItem('invitationCodes', JSON.stringify(this.invitationCodes))
    },

    // 登出
    async logout() {
      try {
        if (this.user) {
          await userApi.logout()
        }
      } catch (error) {
        console.error('登出API请求失败:', error)
        // 即使API调用失败，也要清除本地用户信息
      } finally {
        // 无论API请求是否成功，都要清除本地用户信息
        this.user = null
        localStorage.removeItem('user')
      }
    },

    // 更新用户信息
    async updateUser(userData) {
      try {
        const updatedUser = { ...this.user, ...userData }
        this.user = updatedUser
        localStorage.setItem('user', JSON.stringify(updatedUser))
        return updatedUser
      } catch (error) {
        console.error('更新用户信息失败:', error)
        throw error
      }
    },

    // 获取当前用户信息
    async fetchCurrentUser() {
      try {
        const userData = await userApi.getCurrentUser()
        this.user = userData
        localStorage.setItem('user', JSON.stringify(userData))
        return userData
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },

    // 上传文献
    async uploadJournal(formData) {
      try {
        const response = await journalApi.upload(formData)
        return response
      } catch (error) {
        console.error('上传文献失败:', error)
        throw error
      }
    },

    // 获取我的文献列表
    async fetchMyJournals(params = {}) {
      try {
        const response = await journalApi.getMyJournals(params)
        return response
      } catch (error) {
        console.error('获取我的文献列表失败:', error)
        throw error
      }
    },

    // 获取文献详情
    async fetchJournalDetail(jid) {
      try {
        const response = await journalApi.getJournalDetail(jid)
        return response
      } catch (error) {
        console.error('获取文献详情失败:', error)
        throw error
      }
    },

    // 删除文献
    async deleteJournal(jid) {
      try {
        const response = await journalApi.deleteJournal(jid)
        return response
      } catch (error) {
        console.error('删除文献失败:', error)
        throw error
      }
    },

    // 获取待审核文献列表
    async fetchPendingJournals(params = {}) {
      try {
        const response = await reviewApi.getPendingJournals(params)
        return response
      } catch (error) {
        console.error('获取待审核文献列表失败:', error)
        throw error
      }
    },

    // 审核文献
    async reviewJournal(jid, reviewData) {
      try {
        const response = await reviewApi.reviewJournal(jid, reviewData)
        return response
      } catch (error) {
        console.error('审核文献失败:', error)
        throw error
      }
    },

    // 获取审核历史记录
    async fetchReviewHistory(params = {}) {
      try {
        const response = await reviewApi.getReviewHistory(params)
        return response
      } catch (error) {
        console.error('获取审核历史记录失败:', error)
        throw error
      }
    },

    // 获取审核统计信息
    async fetchReviewStatistics() {
      try {
        const response = await reviewApi.getReviewStatistics()
        return response
      } catch (error) {
        console.error('获取审核统计信息失败:', error)
        throw error
      }
    },

    // 获取被拒绝的文献列表
    async fetchRejectedJournals(params = {}) {
      try {
        const response = await reviewApi.getRejectedJournals(params)
        return response
      } catch (error) {
        console.error('获取被拒绝的文献列表失败:', error)
        throw error
      }
    },

    // 获取用户列表（管理员）
    async fetchUsers(params = {}) {
      try {
        const response = await adminApi.getUsers(params)
        return response
      } catch (error) {
        console.error('获取用户列表失败:', error)
        throw error
      }
    },

    // 修改用户角色（管理员API）
    async updateUserRoleApi(uid, role) {
      try {
        const response = await adminApi.updateUserRole(uid, role)
        return response
      } catch (error) {
        console.error('修改用户角色失败:', error)
        throw error
      }
    },

    // 删除用户（管理员API）
    async deleteUserApi(uid) {
      try {
        const response = await adminApi.deleteUser(uid)
        return response
      } catch (error) {
        console.error('删除用户失败:', error)
        throw error
      }
    },

    // 获取所有文献列表（管理员）
    async fetchAllJournals(params = {}) {
      try {
        const response = await adminApi.getAllJournals(params)
        return response
      } catch (error) {
        console.error('获取所有文献列表失败:', error)
        throw error
      }
    },

    // 删除文献（管理员）
    async adminDeleteJournal(jid) {
      try {
        const response = await adminApi.deleteJournal(jid)
        return response
      } catch (error) {
        console.error('管理员删除文献失败:', error)
        throw error
      }
    },

    // 获取所有审核记录（管理员）
    async fetchAllReviewRecords(params = {}) {
      try {
        const response = await adminApi.getAllReviewRecords(params)
        return response
      } catch (error) {
        console.error('获取所有审核记录失败:', error)
        throw error
      }
    },

    // 获取系统统计信息（管理员）
    async fetchSystemStatistics() {
      try {
        const response = await adminApi.getSystemStatistics()
        return response
      } catch (error) {
        console.error('获取系统统计信息失败:', error)
        throw error
      }
    },

    // 获取已删除文献列表（管理员）
    async fetchDeletedJournals(params = {}) {
      try {
        const response = await adminApi.getDeletedJournals(params)
        return response
      } catch (error) {
        console.error('获取已删除文献列表失败:', error)
        throw error
      }
    },

    // 彻底删除文献（管理员）
  async permanentlyDeleteJournal(jid) {
    try {
      const response = await adminApi.permanentlyDeleteJournal(jid)
      return response
    } catch (error) {
      console.error('彻底删除文献失败:', error)
      throw error
    }
  },
  
  // 加载反馈消息
  loadFeedbackMessages() {
    try {
      const storedFeedbacks = localStorage.getItem('feedbacks')
      if (storedFeedbacks) {
        const parsedFeedbacks = JSON.parse(storedFeedbacks)
        // 为每个反馈消息添加默认状态
        this.feedbackMessages = parsedFeedbacks.map(feedback => ({
          ...feedback,
          status: feedback.status || '未处理'
        }))
      }
    } catch (error) {
      console.error('加载反馈消息失败:', error)
      localStorage.removeItem('feedbacks')
      this.feedbackMessages = []
    }
  },
  
  // 设置公告列表
  setAnnouncements(announcements) {
    this.announcements = announcements
    // 保存公告到localStorage，确保刷新后不会丢失
    localStorage.setItem('announcements', JSON.stringify(this.announcements))
  },
  
  // 设置基础配置
  setBasicConfig(config) {
    this.basicConfig = config
    // 保存基础配置到localStorage，确保刷新后不会丢失
    localStorage.setItem('basicConfig', JSON.stringify(this.basicConfig))
  },
  
  // 添加反馈消息
  addFeedbackMessage(feedbackData) {
    const newFeedback = {
      ...feedbackData,
      status: '未处理',
      createdAt: new Date().toISOString()
    }
    
    this.feedbackMessages.push(newFeedback)
    
    // 保存到localStorage
    localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
    return newFeedback
  },
  
  // 更新反馈消息状态
  updateFeedbackMessageStatus(messageId, status) {
    const messageIndex = this.feedbackMessages.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      this.feedbackMessages[messageIndex].status = status
      
      // 保存到localStorage
      localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
      return true
    }
    return false
  },
  
  // 删除反馈消息
  deleteFeedbackMessage(messageId) {
    const messageIndex = this.feedbackMessages.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      this.feedbackMessages.splice(messageIndex, 1)
      
      // 保存到localStorage
      localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
      return true
    }
    return false
  },
  
  // 批量删除反馈消息
  deleteMultipleFeedbackMessages(messageIds) {
    this.feedbackMessages = this.feedbackMessages.filter(msg => !messageIds.includes(msg.id))
    
    // 保存到localStorage
    localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
    return true
  },
  
  // 更新用户角色
  updateUserRole(userId, newRole) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex].role = newRole
      // 保存到localStorage
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // 更新用户状态
  updateUserStatus(userId, newStatus) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex].status = newStatus
      // 保存到localStorage
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // 更新用户信息
  updateUserInfo(userId, userInfo) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex] = {
        ...this.users[userIndex],
        ...userInfo
      }
      // 保存到localStorage
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // 添加用户
  addUser(userData) {
    const id = Math.max(...this.users.map(u => u.id), 0) + 1
    const newUser = {
      id,
      status: 'active',
      ...userData
    }
    this.users.push(newUser)
    // 保存到localStorage
    localStorage.setItem('users', JSON.stringify(this.users))
    return newUser
  },
  
  // 删除用户
  deleteUser(userId) {
    this.users = this.users.filter(user => user.id !== userId)
    // 保存到localStorage
    localStorage.setItem('users', JSON.stringify(this.users))
    return true
  },
  
  // 添加期刊投稿
  addJournal(journalData) {
    // 添加新期刊到journals数组
    this.journals.push(journalData)
    // 保存期刊列表到localStorage，确保刷新后不会丢失
    localStorage.setItem('journals', JSON.stringify(this.journals))
    return journalData
  },
  
  // 更新期刊信息（用于审核记录通过/拒绝操作）
  updateJournal(updatedJournal) {
    const journalIndex = this.journals.findIndex(journal => journal.id === updatedJournal.id)
    if (journalIndex !== -1) {
      // 更新期刊信息
      this.journals[journalIndex] = updatedJournal
      // 保存到localStorage，确保数据持久化
      localStorage.setItem('journals', JSON.stringify(this.journals))
      return true
    }
    return false
  }
}
})
