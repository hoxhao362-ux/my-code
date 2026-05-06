<<<<<<< HEAD
import * as mockUserData from '../mocks/userData'
import * as mockJournalData from '../mocks/journalData'
import * as mockEditorAccounts from '../mocks/editorAccounts'
import * as mockReviewerAccounts from '../mocks/reviewerAccounts'

=======
import { storage } from './storage'
import http from './http'

// 环境变量控制
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
// Mock Helper
export const mockRequest = (data, delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data)
    }, delay)
  })
<<<<<<< HEAD
}

export const userApi = {
  login: (credentials) => mockRequest(mockUserData.users.find(u => u.username === credentials.username) || null),
  logout: () => mockRequest({ success: true }),
  getCurrentUser: () => mockRequest(mockUserData.users[0]),
  getUsers: () => mockRequest(mockUserData.users)
}

export const journalApi = {
  upload: (formData) => mockRequest({ id: Date.now(), ...Object.fromEntries(formData) }),
  getMyJournals: (params) => mockRequest(mockJournalData.journals),
  getJournalDetail: (jid) => mockRequest(mockJournalData.journals.find(j => String(j.id) === String(jid))),
  deleteJournal: (jid) => mockRequest({ success: true }),
  getAllJournals: () => mockRequest(mockJournalData.journals)
}

export const reviewApi = {
  getPendingJournals: () => mockRequest(mockJournalData.journals.filter(j => j.status === 'Under Review')),
  reviewJournal: (jid, data) => mockRequest({ success: true }),
  getReviewHistory: () => mockRequest([]),
  getReviewStatistics: () => mockRequest({ completed: 10, pending: 5 }),
  getRejectedJournals: () => mockRequest([])
}

export const adminApi = {
  getUsers: () => mockRequest(mockUserData.users),
  updateUserRole: (uid, role) => mockRequest({ success: true }),
  deleteUser: (uid) => mockRequest({ success: true }),
  getAllJournals: () => mockRequest(mockJournalData.journals),
  deleteJournal: (jid) => mockRequest({ success: true }),
  getAllReviewRecords: () => mockRequest([]),
  getSystemStatistics: () => mockRequest({ users: 100, journals: 50 }),
  getDeletedJournals: () => mockRequest([]),
  permanentlyDeleteJournal: (jid) => mockRequest({ success: true })
}

export const editorApi = {
  getEditorsList: () => mockRequest(mockEditorAccounts.editorAccounts),
  assignEditor: (data) => mockRequest({ success: true }),
  assignTask: (data) => mockRequest({ success: true })
}

export const messageApi = {
  getMessages: () => mockRequest([]),
  sendMessage: (data) => mockRequest({ id: Date.now(), ...data }),
  markAsRead: (id) => mockRequest({ success: true }),
  getUnreadCount: () => mockRequest(0)
=======
}

export const platformJournalApi = {
  getJournals: () => {
    if (!USE_MOCK) return http.get('/platform-journals')
    return mockRequest(storage.getAll(storage.KEYS.PLATFORM_JOURNALS))
  },
  getJournal: (id) => {
    if (!USE_MOCK) return http.get(`/platform-journals/${id}`)
    const journal = storage.getAll(storage.KEYS.PLATFORM_JOURNALS).find(j => j.id === id)
    return mockRequest(journal)
  },
  getArticlesByJournal: (journalId) => {
    // This is a mock implementation. In a real app, articles would have a 'journalId' or 'venueId'.
    // Here we will just return all journals (manuscripts) for now, or filter if we add that field.
    if (!USE_MOCK) return http.get(`/platform-journals/${journalId}/articles`)
    
    // Simulating that some manuscripts belong to this journal
    // For demo purposes, we return all published manuscripts
    const manuscripts = storage.getAll(storage.KEYS.JOURNALS)
    return mockRequest(manuscripts.filter(m => m.status === 'published' || m.status === 'accepted'))
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
    if (!USE_MOCK) return http.get('/users/current')
    const users = storage.getAll(storage.KEYS.USERS)
    return mockRequest(users[0]) 
  },
  getUsers: () => {
    if (!USE_MOCK) return http.get('/users')
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
    if (!USE_MOCK) return http.post('/manuscripts', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    
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
    if (!USE_MOCK) return http.get('/manuscripts/my')
    
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
    if (!USE_MOCK) return http.delete(`/manuscripts/${jid}`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  },
  getAllJournals: () => {
    if (!USE_MOCK) return http.get('/manuscripts')
    return mockRequest(storage.getAll(storage.KEYS.JOURNALS))
  },
  updateJournal: (jid, data) => {
    if (!USE_MOCK) return http.put(`/manuscripts/${jid}`, data)
    return mockRequest(storage.update(storage.KEYS.JOURNALS, jid, data))
  }
}

export const reviewApi = {
  getPendingJournals: () => {
    if (!USE_MOCK) return http.get('/reviews/pending')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    return mockRequest(journals.filter(j => 
      j.status === 'Under Review' || 
      j.status === 'pending_initial_review' || 
      j.status === 'under_peer_review'
    ))
  },
  reviewJournal: (jid, reviewData) => {
    if (!USE_MOCK) return http.post(`/reviews/${jid}`, reviewData)
    
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
    if (!USE_MOCK) return http.get('/reviews/history')
    
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
    if (!USE_MOCK) return http.get('/reviews/statistics')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const completed = journals.filter(j => j.status === 'published' || j.status === 'rejected').length
    const pending = journals.filter(j => j.status === 'pending_initial_review' || j.status === 'under_peer_review').length
    return mockRequest({ completed, pending })
  },
  getRejectedJournals: () => {
     if (!USE_MOCK) return http.get('/manuscripts/rejected')
     return mockRequest(storage.query(storage.KEYS.JOURNALS, j => j.status === 'rejected'))
  }
}

export const adminApi = {
  getUsers: () => {
    if (!USE_MOCK) return http.get('/users')
    return mockRequest(storage.getAll(storage.KEYS.USERS))
  },
  updateUserRole: (uid, role) => {
    if (!USE_MOCK) return http.put(`/users/${uid}/role`, { role })
    return mockRequest(storage.update(storage.KEYS.USERS, uid, { role }))
  },
  deleteUser: (uid) => {
    if (!USE_MOCK) return http.delete(`/users/${uid}`)
    return mockRequest(storage.remove(storage.KEYS.USERS, uid))
  },
  getAllJournals: () => {
    if (!USE_MOCK) return http.get('/manuscripts/all')
    return mockRequest(storage.getAll(storage.KEYS.JOURNALS))
  },
  deleteJournal: (jid) => {
    if (!USE_MOCK) return http.delete(`/manuscripts/${jid}`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  },
  getAllReviewRecords: () => {
    if (!USE_MOCK) return http.get('/reviews/all')
    return mockRequest([])
  },
  getSystemStatistics: () => {
    if (!USE_MOCK) return http.get('/admin/statistics/system')
    
    const users = storage.getAll(storage.KEYS.USERS).length
    const journals = storage.getAll(storage.KEYS.JOURNALS).length
    return mockRequest({ users, journals })
  },
  getSubmissionTrend: () => {
    if (!USE_MOCK) return http.get('/admin/statistics/trend')
    
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
    if (!USE_MOCK) return http.get('/admin/statistics/modules')
    
    const journals = storage.getAll(storage.KEYS.JOURNALS)
    const dist = {}
    journals.forEach(j => {
      const mod = j.module || 'Others'
      dist[mod] = (dist[mod] || 0) + 1
    })
    return mockRequest(Object.entries(dist).map(([name, value]) => ({ name, value })))
  },
  getJournalStatusStats: () => {
    if (!USE_MOCK) return http.get('/admin/statistics/status')
    
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
    if (!USE_MOCK) return http.get('/manuscripts/deleted')
    return mockRequest([])
  },
  permanentlyDeleteJournal: (jid) => {
    if (!USE_MOCK) return http.delete(`/manuscripts/${jid}/permanent`)
    return mockRequest(storage.remove(storage.KEYS.JOURNALS, jid))
  }
}

export const editorApi = {
  getEditorsList: () => {
    if (!USE_MOCK) return http.get('/editors')
    return mockRequest(storage.getAll(storage.KEYS.EDITOR_ACCOUNTS))
  },
  assignEditor: (data) => {
    if (!USE_MOCK) return http.post('/manuscripts/assign-editor', data)
    return mockRequest({ success: true })
  },
  assignTask: (data) => {
    if (!USE_MOCK) return http.post('/tasks/assign', data)
    return mockRequest({ success: true })
  }
}

export const messageApi = {
  getMessages: () => {
    if (!USE_MOCK) return http.get('/messages')
    return mockRequest([])
  },
  sendMessage: (data) => {
    if (!USE_MOCK) return http.post('/messages', data)
    return mockRequest({ id: Date.now(), ...data })
  },
  markAsRead: (id) => {
    if (!USE_MOCK) return http.put(`/messages/${id}/read`)
    return mockRequest({ success: true })
  },
  getUnreadCount: () => {
    if (!USE_MOCK) return http.get('/messages/unread-count')
    return mockRequest(0)
  }
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
}
