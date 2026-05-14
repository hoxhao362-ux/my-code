import http from './http'

// ================= 1. 公开展示与平台 API (/public) ================= 
export const platformJournalApi = { 
  getJournals: (params) => http.get('/public/journals', { params }), 
  getJournal: (id) => http.get(`/public/journals/${id}`), 
  getArticles: (params) => http.get('/public/articles', { params }), 
  getArticlesByJournal: (journalId) => http.get('/public/articles', { params: { journal_id: journalId } }), 
  getArticleDetail: (articleId) => http.get(`/public/articles/${articleId}`), 
  searchArticles: (params) => http.get('/public/search', { params }) 
}

// ================= 2. 用户与认证 API (/auth & /users) ================= 
export const userApi = { 
  // --- 认证体系 (对接 auth.py) --- 
  // RequestBody: {username, email, password, invite_code} 
  register: (data) => http.post('/auth/register', data), 
  
  // RequestBody: {username, password, is_remember} 
  login: (credentials) => http.post('/auth/login', credentials), 
  
  // Token 直接在 Header 携带即可 
  logout: () => http.post('/auth/logout'), 
  
  changePassword: (data) => http.put('/auth/password', data),

  // [新增] 请求发送密码重置验证码
  sendResetCode: (data) => http.post('/auth/password/forgot', data),

  // [新增] 使用验证码重置密码
  resetPasswordWithCode: (data) => http.post('/auth/password/reset', data),

  // --- 用户体系 (对接 users.py) --- 
  getCurrentUser: () => http.get('/users/me'), 
  
  // QueryParam: ?avatar_hash=xx 
  updateCurrentUser: (avatarHash) => http.put('/users/me', null, { 
    params: { avatar_hash: avatarHash } 
  }), 
  
  getAnnouncements: () => http.get('/public/announcements'), 
} 

// ================= 3. 稿件中心 API (重构自 journalApi) =================
export const manuscriptApi = {
  /**
   * 核心投稿接口
   * 适配后端: POST /api/v1/manuscripts/
   * Content-Type: multipart/form-data
   */
  upload: (formData) => http.post('/manuscripts/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  /**
   * 获取我的稿件列表
   * 适配后端: GET /api/v1/manuscripts/
   * params: { status, page, page_size }
   */
  getMyManuscripts: (params) => http.get('/manuscripts/', { params }),

  /**
   * 获取稿件详情
   * 适配后端: GET /api/v1/manuscripts/{manuscript_id}
   */
  getManuscriptDetail: (id) => http.get(`/manuscripts/${id}`),

  /**
   * 稿件历史流转记录
   * 适配后端: GET /api/v1/manuscripts/{id}/history
   */
  getManuscriptHistory: (id) => http.get(`/manuscripts/${id}/history`),

  /**
   * 工作流状态流转 (审核、退修、分配等核心逻辑)
   * 适配后端: POST /api/v1/manuscripts/{id}/workflow
   * Payload: FormData or JSON depending on the action
   */
  updateWorkflow: (id, data) => {
    // 后端工作流接口适配，支持附加文件或表单数据
    const fd = data instanceof FormData ? data : new FormData()
    if (!(data instanceof FormData)) {
      for (const key in data) fd.append(key, data[key])
    }
    return http.post(`/manuscripts/${id}/workflow`, fd)
  },

  /**
   * 获取当前稿件可用的操作指令
   * 适配后端: GET /api/v1/manuscripts/{id}/actions
   */
  getAvailableActions: (id) => http.get(`/manuscripts/${id}/actions`),

  /**
   * 稿件关联文件列表
   * 适配后端: GET /api/v1/manuscripts/{id}/files
   */
  getManuscriptFiles: (id) => http.get(`/manuscripts/${id}/files`),

  /**
   * 为指定稿件补充上传文件
   * 适配后端: POST /api/v1/manuscripts/{id}/files
   */
  uploadManuscriptFile: (id, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post(`/manuscripts/${id}/files`, fd)
  },

  /**
   * PDF 预览 (处理 Blob)
   * 适配后端: POST /api/v1/manuscripts/preview-pdf
   */
  previewPdf: (data) => http.post('/manuscripts/preview-pdf', data, {
    responseType: 'blob'
  }),
  
  // 导出稿件
  exportManuscripts: (params = {}) => http.get('/manuscripts/export', { 
    params,
    responseType: 'blob'
  })
} 

// ================= 4. 审稿人 API (/reviews) ================= 
export const reviewApi = {
  getMyTasks(params = {}) {
    return http.get('/reviews/me/tasks', { params })
  },
  submitReview(taskId, data) {
    return http.put(`/reviews/me/tasks/${taskId}`, null, { params: data })
  },
  getReviewersList(params = {}) {
    return http.get('/reviews/reviewers', { params })
  }
}

// ================= 5. 管理员 API (/admin) ================= 
export const adminApi = { 
  // [新增] 管理员独立登录 
  adminLogin: (credentials) => http.post('/admin/login', credentials), 

  // 面板与统计 
  getDashboard: () => http.get('/admin/dashboard'), 
  getSystemStatistics: () => http.get('/admin/statistics'), 
  
  // 用户管理 
  getUsers: (params) => http.get('/admin/users', { params }), 
  
  // QueryParam: ?role=xxx&is_verified=true
  updateUserRole: (uid, role, is_verified = true) => http.put(`/admin/users/${uid}/role`, null, { 
    params: { role, is_verified } 
  }), 
  
  deleteUser: (uid) => http.delete(`/admin/users/${uid}`),
  
  // [新增] 管理员强制重置用户密码
  resetUserPassword: (uid) => http.post(`/admin/users/${uid}/reset-password`),

  // 稿件管理 (全局) 
  getAllJournals: (params) => http.get('/admin/journals/all', { params }), 
  deleteJournal: (jid) => http.delete(`/admin/journals/${jid}`), 
  getDeletedJournals: (params) => http.get('/admin/journals/deleted', { params }), 
  permanentlyDeleteJournal: (jid) => http.delete(`/admin/journals/deleted/${jid}`), 
  
  // 邀请码管理 
  createInvitationCodes: (data) => http.post('/admin/invitations', data), 
  getInvitationCodes: (params) => http.get('/admin/invitations', { params }), 
  updateInvitationCodeStatus: (code, status) => http.put(`/admin/invitations/${code}/status`, { status }), 
  validateInvitationCode: (code) => http.get(`/admin/invitations/validate/${code}`) 
} 

// ================= 6. 编辑 API (/editorial) ================= 
export const editorApi = { 
  getDashboard: () => http.get('/editorial/dashboard'), 
  getBoardMembers: () => http.get('/editorial/board'), 
  addBoardMember: (data) => http.post('/editorial/board', data), 
  removeBoardMember: (id) => http.delete(`/editorial/board/${id}`), 
  assignEditor: (data) => { 
    // 适配后端工作流 
    const fd = new FormData() 
    for (const key in data) if (key !== 'id' && key !== 'jid') fd.append(key, data[key]) 
    return http.post(`/manuscripts/${data.id || data.jid}/workflow`, fd) 
  } 
} 

// ================= 7. 验证码 API (/captcha) ================= 
export const captchaApi = { 
  getImage: () => http.get('/captcha/image'), 
  verify: (data) => http.post('/captcha/verify', data) 
} 
