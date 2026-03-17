import * as mockUserData from '../mocks/userData'
import * as mockJournalData from '../mocks/journalData'
import * as mockEditorAccounts from '../mocks/editorAccounts'
import * as mockReviewerAccounts from '../mocks/reviewerAccounts'

// Mock Helper
export const mockRequest = (data, delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data)
    }, delay)
  })
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
}
