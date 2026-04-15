import http from './http'
import { mockRequest } from './api'

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

export const emailApi = {
  // Send single email
  sendEmail: (data) => {
    if (!USE_MOCK) return http.post('/notifications/email', data)
    return mockRequest({ success: true, messageId: Date.now() })
  },
  
  // Send batch emails
  sendBatchEmails: (data) => {
    if (!USE_MOCK) return http.post('/notifications/email/batch', data)
    return mockRequest({ success: true, sentCount: data.recipients?.length || 0 })
  },
  
  // Send reviewer invitation (using template)
  sendReviewerInvitation: (data) => {
    if (!USE_MOCK) return http.post('/notifications/reviewer-invitation', data)
    return mockRequest({ success: true })
  },
  
  // Send decision notification
  sendDecisionNotification: (data) => {
    if (!USE_MOCK) return http.post('/notifications/decision', data)
    return mockRequest({ success: true })
  },
  
  // Send revision request
  sendRevisionRequest: (data) => {
    if (!USE_MOCK) return http.post('/notifications/revision', data)
    return mockRequest({ success: true })
  },
  
  // Send acceptance notification
  sendAcceptanceNotification: (data) => {
    if (!USE_MOCK) return http.post('/notifications/acceptance', data)
    return mockRequest({ success: true })
  },
  
  // Send test email
  sendTestEmail: (email) => {
    if (!USE_MOCK) return http.post('/notifications/test', { email })
    return mockRequest({ success: true })
  }
}
