import { storage } from './storage'
import http from './http'

// 环境变量控制
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

// Mock Helper
export const mockRequest = (data, delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data)
    }, delay)
  })
}

export const platformJournalApi = {
  getJournals: () => {
    if (!USE_MOCK) return http.get('/public/journals')
    return mockRequest(storage.getAll(storage.KEYS.PLATFORM_JOURNALS))
  },
  getJournal: (id) => {
    if (!USE_MOCK) return http.get('/public/info')
    const journal = storage.getAll(storage.KEYS.PLATFORM_JOURNALS).find(j => j.id === id)
    return mockRequest(journal)
  },
  getArticlesByJournal: (journalId) => {
    if (!USE_MOCK) return http.get('/public/articles')
    
    // Simulating that some manuscripts belong to this journal
    // For demo purposes, we return all published manuscripts
    const manuscripts = storage.getAll(storage.KEYS.JOURNALS)
    return mockRequest(manuscripts.filter(m => m.status === 'published' || m.status === 'accepted'))
  },
  getArticleDetail: (articleId) => {
    if (!USE_MOCK) return http.get(`/public/articles/${articleId}`)
    const manuscripts = storage.getAll(storage.KEYS.JOURNALS)
    return mockRequest(manuscripts.find(m => m.id === articleId || m.manuscript_id === articleId) || null)
  },
  searchArticles: (params) => {
    if (!USE_MOCK) return http.get('/public/search', { params })
    return mockRequest({ items: [], total: 0 })
  }
}

export const userApi = {
  login: (credentials) => {
    if (!USE_MOCK) return http.post('/auth/login', credentials)
    
    const users = storage.getAll(storage.KEYS.USERS)
    const user = users.find(u => u.username === credentials.username)
    return mockRequest(user || null)
  },
  logout: () => {
    if (!USE_MOCK) return http.post('/auth/logout')
    return mockRequest({ success: true })
  },
  getCurrentUser: () => {
    if (!USE_MOCK) return http.get('/users/me')
    const users = storage.getAll(storage.KEYS.USERS)
    return mockRequest(users[0]) 
  },
  updateCurrentUser: (data) => {
    if (!USE_MOCK) return http.put('/users/me', null, { params: data })
    return mockRequest({ success: true })
  },
  changePassword: (oldPassword, newPassword) => {
    if (!USE_MOCK) return http.put('/auth/password', null, { params: { old_password: oldPassword, new_password: newPassword } })
    return mockRequest({ success: true })
  },
  getUsers: () => {
    if (!USE_MOCK) return http.get('/admin/users')
    return mockRequest(storage.getAll(storage.KEYS.USERS))
  },
  
  // 公告相关
  getAnnouncements: () => {
    if (!USE_MOCK) return http.get('/announcements')
    return mockRequest(storage.getAll(storage.KEYS.ANNOUNCEMENTS))
  },
  addAnnouncement: (data) => {
    if (!USE_MOCK) return http.post('/announcements', data)
    return mockRequest(storage.add(storage.KEYS.ANNOUNCEMENTS, data))
  },
  updateAnnouncement: (id, data) => {
    if (!USE_MOCK) return http.put(`/announcements/${id}`, data)
    return mockRequest(storage.update(storage.KEYS.ANNOUNCEMENTS, id, data))
  },
  deleteAnnouncement: (id) => {
    if (!USE_MOCK) return http.delete(`/announcements/${id}`)
    return mockRequest(storage.remove(storage.KEYS.ANNOUNCEMENTS, id))
  }
}

export const journalApi = {
  upload: (formData) => {
    if (!USE_MOCK) return http.post('/manuscripts/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    
    const data = Object.fromEntries(formData)
    const newJournal = {
      ...data,
      submissionDate: new Date().toISOString().split('T')[0],
      date: new Date().toISOString().split('T')[0],
      status: 'pending_initial_review',
      reviews: []
    }
    return mockRequest(storage.add(storage.KEYS.JOURNALS, newJournal))
  },
  getMyJournals: (username) => {
    if (!USE_MOCK) return http.get('/manuscripts/')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    if (username) {
        return mockRequest(journals.filter(j => j.author === username))
    }
    return mockRequest(journals)
  },
  getJournalDetail: (jid) => {
    if (!USE_MOCK) return http.get(`/manuscripts/${jid}`)
    return mockRequest(storage.find(storage.KEYS.JOURNALS, jid))
  },
  deleteJournal: (jid) => {
    if (!USE_MOCK) return http.delete(`/admin/journals/${jid}`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  },
  getAllJournals: () => {
    if (!USE_MOCK) return http.get('/admin/journals/all')
    return mockRequest(storage.getAll(storage.KEYS.JOURNALS))
  },
  updateJournal: (jid, data) => {
    if (!USE_MOCK) {
      const fd = new FormData()
      for (const key in data) {
        fd.append(key, data[key])
      }
      return http.post(`/manuscripts/${jid}/workflow`, fd)
    }
    return mockRequest(storage.update(storage.KEYS.JOURNALS, jid, data))
  },
  getManuscriptActions: (jid) => {
    if (!USE_MOCK) return http.get(`/manuscripts/${jid}/actions`)
    return mockRequest(['save', 'submit', 'withdraw'])
  },
  getManuscriptFiles: (jid) => {
    if (!USE_MOCK) return http.get(`/manuscripts/${jid}/files`)
    return mockRequest({ manuscript_id: jid, files: [] })
  },
  uploadManuscriptFile: (jid, file) => {
    if (!USE_MOCK) {
      const fd = new FormData()
      fd.append('file', file)
      return http.post(`/manuscripts/${jid}/files`, fd)
    }
    return mockRequest({ success: true })
  },
  getManuscriptHistory: (jid) => {
    if (!USE_MOCK) return http.get(`/manuscripts/${jid}/history`)
    return mockRequest({ manuscript_id: jid, history: [] })
  },
  previewPdf: (data) => {
    if (!USE_MOCK) return http.post('/manuscripts/preview-pdf', data)
    return mockRequest({ success: true, url: '#' })
  }
}

export const reviewApi = {
  getPendingJournals: () => {
    if (!USE_MOCK) return http.get('/reviews/me/tasks')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    return mockRequest(journals.filter(j => 
      j.status === 'Under Review' || 
      j.status === 'pending_initial_review' || 
      j.status === 'under_peer_review'
    ))
  },
  reviewJournal: (jid, reviewData) => {
    if (!USE_MOCK) return http.put(`/reviews/me/tasks/${jid}`, null, { params: reviewData })
    
    const journal = storage.find(storage.KEYS.JOURNALS, jid)
    if (!journal) return mockRequest({ success: false, message: 'Journal not found' })
    
    const reviews = journal.reviews || []
    reviews.push({
      ...reviewData,
      date: new Date().toISOString().split('T')[0]
    })
    
    let updates = { reviews }
    if (reviewData.decision) {
        if (reviewData.decision === 'accept') updates.status = 'accepted'
        else if (reviewData.decision === 'reject') updates.status = 'rejected'
        else if (reviewData.decision === 'major_revision' || reviewData.decision === 'minor_revision') updates.status = 'revision_requested'
    }

    storage.update(storage.KEYS.JOURNALS, jid, updates)
    return mockRequest({ success: true })
  },
  getReviewHistory: (reviewerName) => {
    if (!USE_MOCK) return http.get('/reviews/me/tasks?status=completed')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const history = []
    journals.forEach(j => {
        if (j.reviews && Array.isArray(j.reviews)) {
            const myReview = j.reviews.find(r => r.reviewer === reviewerName)
            if (myReview) {
                history.push({
                    journalId: j.id,
                    journalTitle: j.title,
                    ...myReview
                })
            }
        }
    })
    return mockRequest(history)
  },
  getReviewStatistics: () => {
    if (!USE_MOCK) {
       return http.get('/reviews/me/tasks').then(res => {
         const items = Array.isArray(res) ? res : (res.items || [])
         const completed = items.filter(j => j.status === 'published' || j.status === 'rejected' || j.status === 'completed').length
         const pending = items.filter(j => !j.status || j.status.includes('pending') || j.status.includes('review')).length
         return { completed, pending }
       }).catch(() => ({ completed: 0, pending: 0 }))
    }
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const completed = journals.filter(j => j.status === 'published' || j.status === 'rejected').length
    const pending = journals.filter(j => j.status === 'pending_initial_review' || j.status === 'under_peer_review').length
    return mockRequest({ completed, pending })
  },
  getRejectedJournals: () => {
     if (!USE_MOCK) return http.get('/admin/journals/all?status=rejected')
     return mockRequest(storage.query(storage.KEYS.JOURNALS, j => j.status === 'rejected'))
  }
}

export const adminApi = {
  adminLogin: (credentials) => {
    if (!USE_MOCK) return http.post('/admin/login', credentials)
    
    const users = storage.getAll(storage.KEYS.USERS)
    const user = users.find(u => u.username === credentials.username && u.role === 'admin')
    return mockRequest(user || null)
  },
  getUsers: () => {
    if (!USE_MOCK) return http.get('/admin/users')
    return mockRequest(storage.getAll(storage.KEYS.USERS))
  },
  getDashboard: () => {
    if (!USE_MOCK) return http.get('/admin/dashboard')
    return mockRequest({ users_count: 0, journals_count: 0, review_count: 0 })
  },
  getUserDetail: (uid) => {
    if (!USE_MOCK) return http.get(`/users/${uid}`)
    return mockRequest(storage.getAll(storage.KEYS.USERS).find(u => u.id === uid) || null)
  },
  updateUser: (uid, data) => {
    if (!USE_MOCK) return http.put(`/users/${uid}`, null, { params: data })
    return mockRequest(storage.update(storage.KEYS.USERS, uid, data))
  },
  updateUserRole: (uid, role) => {
    if (!USE_MOCK) return http.put(`/admin/users/${uid}/role`, null, { params: { role } })
    return mockRequest(storage.update(storage.KEYS.USERS, uid, { role }))
  },
  deleteUser: (uid) => {
    if (!USE_MOCK) return http.delete(`/admin/users/${uid}`)
    return mockRequest(storage.remove(storage.KEYS.USERS, uid))
  },
  getAllJournals: () => {
    if (!USE_MOCK) return http.get('/admin/journals/all')
    return mockRequest(storage.getAll(storage.KEYS.JOURNALS))
  },
  deleteJournal: (jid) => {
    if (!USE_MOCK) return http.delete(`/admin/journals/${jid}`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  },
  getAllReviewRecords: () => {
    if (!USE_MOCK) return http.get('/admin/review-records')
    return mockRequest([])
  },
  getSystemStatistics: () => {
    if (!USE_MOCK) return http.get('/admin/statistics').then(res => ({ users: res.total_users || 0, journals: res.total_journals || 0 }))
    
    const users = storage.getAll(storage.KEYS.USERS).length
    const journals = storage.getAll(storage.KEYS.JOURNALS).length
    return mockRequest({ users, journals })
  },
  getSubmissionTrend: () => {
    if (!USE_MOCK) {
      return http.get('/admin/statistics').then(res => {
        // Backend doesn't provide trend yet, return mock format to prevent UI crash
        return [{ date: new Date().toISOString().split('T')[0], count: res.total_journals || 0 }]
      })
    }
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const trend = {}
    journals.forEach(j => {
      if (!j.submissionDate) return
      const date = new Date(j.submissionDate)
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      trend[key] = (trend[key] || 0) + 1
    })
    return mockRequest(Object.entries(trend).map(([date, count]) => ({ date, count })).sort((a, b) => a.date.localeCompare(b.date)))
  },
  getModuleDistribution: () => {
    if (!USE_MOCK) {
      return http.get('/admin/statistics').then(res => {
         // Backend doesn't provide module distribution yet, return a mock format based on total
         return [{ name: 'General', value: res.total_journals || 0 }]
      })
    }
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const dist = {}
    journals.forEach(j => {
      const mod = j.module || 'Others'
      dist[mod] = (dist[mod] || 0) + 1
    })
    return mockRequest(Object.entries(dist).map(([name, value]) => ({ name, value })))
  },
  getJournalStatusStats: () => {
    if (!USE_MOCK) {
       return http.get('/admin/statistics').then(res => {
         const statuses = res.journal_status || {}
         return {
           pending: statuses.pending_initial_review || 0,
           underReview: statuses.under_peer_review || 0,
           accepted: statuses.final_decision_accepted || 0,
           rejected: statuses.final_decision_rejected || 0,
           published: statuses.published || 0
         }
       })
    }
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const stats = {
      pending: 0,
      underReview: 0,
      accepted: 0,
      rejected: 0,
      published: 0
    }
    journals.forEach(j => {
      const s = (j.status || '').toLowerCase()
      if (s === 'published') stats.published++
      else if (s === 'accepted') stats.accepted++
      else if (s === 'rejected') stats.rejected++
      else if (s.includes('review') || s.includes('pending')) stats.underReview++ // Adjusted logic for demo
      else stats.pending++
    })
    return mockRequest(stats)
  },
  getDeletedJournals: () => {
    if (!USE_MOCK) return http.get('/admin/journals/deleted')
    return mockRequest([])
  },
  permanentlyDeleteJournal: (jid) => {
    if (!USE_MOCK) return http.delete(`/admin/journals/deleted/${jid}`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  },
  // 邀请码相关预留接口
  createInvitationCodes: (data) => {
    if (!USE_MOCK) return http.post('/admin/invitation-codes', data)
    return mockRequest({ success: true })
  },
  getInvitationCodes: (params) => {
    if (!USE_MOCK) return http.get('/admin/invitation-codes', { params })
    return mockRequest({ items: [], total: 0 })
  },
  updateInvitationCodeStatus: (code, status) => {
    if (!USE_MOCK) return http.put(`/admin/invitation-codes/${code}/status`, { status })
    return mockRequest({ success: true })
  },
  validateInvitationCode: (code) => {
    if (!USE_MOCK) return http.get(`/admin/invitation-codes/validate/${code}`)
    return mockRequest({ valid: true, role: 'author' })
  }
}

export const editorApi = {
  getEditorsList: () => {
    if (!USE_MOCK) return http.get('/admin/users?role=editor')
    return mockRequest(storage.getAll(storage.KEYS.EDITOR_ACCOUNTS))
  },
  getReviewers: () => {
    if (!USE_MOCK) return http.get('/reviews/reviewers')
    return mockRequest(storage.getAll(storage.KEYS.USERS).filter(u => u.role === 'reviewer'))
  },
  getDashboard: () => {
    if (!USE_MOCK) return http.get('/editorial/dashboard')
    return mockRequest({ pending_count: 0, reviewing_count: 0, statistics: {} })
  },
  getBoardMembers: () => {
    if (!USE_MOCK) return http.get('/editorial/board')
    return mockRequest([])
  },
  addBoardMember: (data) => {
    if (!USE_MOCK) return http.post('/editorial/board', null, { params: data })
    return mockRequest({ success: true })
  },
  assignEditor: (data) => {
    if (!USE_MOCK) {
      const fd = new FormData()
      for (const key in data) {
        if (key !== 'manuscript_id' && key !== 'jid' && key !== 'id') {
          fd.append(key, data[key])
        }
      }
      return http.post(`/manuscripts/${data.manuscript_id || data.jid || data.id}/workflow`, fd)
    }
    return mockRequest({ success: true })
  },
  assignTask: (data) => {
    if (!USE_MOCK) {
      const fd = new FormData()
      for (const key in data) {
        if (key !== 'manuscript_id' && key !== 'jid' && key !== 'id') {
          fd.append(key, data[key])
        }
      }
      return http.post(`/manuscripts/${data.manuscript_id || data.jid || data.id}/workflow`, fd)
    }
    return mockRequest({ success: true })
  }
}

export const messageApi = {
  getMessages: () => {
    if (!USE_MOCK) return http.get('/users/me/notifications')
    return mockRequest([])
  },
  sendMessage: (data) => {
    if (!USE_MOCK) return http.post('/messages', data) // Warning: No backend endpoint for sending messages currently
    return mockRequest({ id: Date.now(), ...data })
  },
  markAsRead: (id) => {
    if (!USE_MOCK) return http.put(`/users/me/notifications/${id}`)
    return mockRequest({ success: true })
  },
  getUnreadCount: () => {
    if (!USE_MOCK) return http.get('/users/me/notifications').then(res => res.filter(n => !n.is_read).length).catch(() => 0)
    return mockRequest(0)
  }
}

export const captchaApi = {
  getImage: () => {
    if (!USE_MOCK) return http.get('/captcha/image')
    return mockRequest({ id: 'mock-id', image_base64: 'mock-base64' })
  },
  verify: (data) => {
    if (!USE_MOCK) return http.post('/captcha/verify', data)
    return mockRequest({ success: true })
  }
}
