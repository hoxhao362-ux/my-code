import http from './http'

// ================= 1. 公开展示与平台 API (/public) ================= 
export const platformJournalApi = { 
  getJournals: (params) => http.get('/public/journals', { params }), 
  getJournal: (id) => http.get(`/public/journals/${id}`), 
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
  
  // QueryParam: ?old_password=xx&new_password=xx 
  changePassword: (oldPassword, newPassword) => http.put('/auth/password', null, { 
    params: { old_password: oldPassword, new_password: newPassword } 
  }), 
  
  // --- 用户体系 (对接 users.py) --- 
  getCurrentUser: () => http.get('/users/me'), 
  
  // QueryParam: ?avatar_hash=xx 
  updateCurrentUser: (avatarHash) => http.put('/users/me', null, { 
    params: { avatar_hash: avatarHash } 
  }), 
  
  getAnnouncements: () => http.get('/public/announcements'), 
} 

// ================= 3. 稿件/文献 API (原 /journal -> 现 /manuscripts) ================= 
export const journalApi = { 
  // 核心上传 
  upload: (formData) => http.post('/manuscripts/', formData, { 
    headers: { 'Content-Type': 'multipart/form-data' } 
  }), 
  // 获取我的稿件 
  getMyJournals: (params) => http.get('/manuscripts/', { params }), 
  // 获取详情 
  getJournalDetail: (jid) => http.get(`/manuscripts/${jid}`), 
  // 稿件历史 
  getManuscriptHistory: (jid) => http.get(`/manuscripts/${jid}/history`), 
  // 工作流操作 (更新状态等) 
  updateJournal: (jid, data) => { 
    const fd = new FormData() 
    for (const key in data) fd.append(key, data[key]) 
    return http.post(`/manuscripts/${jid}/workflow`, fd) 
  }, 
  // 获取可用操作 
  getManuscriptActions: (jid) => http.get(`/manuscripts/${jid}/actions`), 
  // 文件管理 
  getManuscriptFiles: (jid) => http.get(`/manuscripts/${jid}/files`), 
  uploadManuscriptFile: (jid, file) => { 
    const fd = new FormData() 
    fd.append('file', file) 
    return http.post(`/manuscripts/${jid}/files`, fd) 
  }, 
  // 预览
  previewPdf: (data) => http.post('/manuscripts/preview-pdf', data, { responseType: 'blob' })
} 

// ================= 4. 审稿人 API (/reviews) ================= 
export const reviewApi = { 
  // 获取分配给我的任务（待审核） 
  getPendingJournals: (params) => http.get('/reviews/me/tasks', { params }), 
  
  // 提交审核意见 (支持 accept, reject, major_revision 等) 
  reviewJournal: (jid, reviewData) => http.put(`/reviews/me/tasks/${jid}`, reviewData), 
  
  // 获取历史 (通常传 status=completed) 
  getReviewHistory: () => http.get('/reviews/me/tasks', { params: { status: 'completed' } }), 
  
  // 获取统计 
  getReviewStatistics: () => http.get('/reviews/statistics'), 
  
  getReviewersList: () => http.get('/reviews/reviewers') 
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
  
  // QueryParam: ?role=xxx 
  updateUserRole: (uid, role) => http.put(`/admin/users/${uid}/role`, null, { 
    params: { role } 
  }), 
  
  deleteUser: (uid) => http.delete(`/admin/users/${uid}`), 
  
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
