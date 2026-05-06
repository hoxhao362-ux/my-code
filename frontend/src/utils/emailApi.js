<<<<<<< HEAD
import { mockRequest } from './api'

export const emailApi = {
  // Send single email
  sendEmail: (data) => {
    // data: { to, subject, content, template?, manuscriptId? }
=======
import http from './http'
import { mockRequest } from './api'

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

export const emailApi = {
  // Send single email
  sendEmail: (data) => {
    if (!USE_MOCK) return http.post('/notifications/email', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true, messageId: Date.now() })
  },
  
  // Send batch emails
  sendBatchEmails: (data) => {
<<<<<<< HEAD
    // data: { recipients: [{email, subject, content}], template? }
=======
    if (!USE_MOCK) return http.post('/notifications/email/batch', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true, sentCount: data.recipients?.length || 0 })
  },
  
  // Send reviewer invitation (using template)
  sendReviewerInvitation: (data) => {
<<<<<<< HEAD
    // data: { reviewerEmail, reviewerName, manuscriptId, manuscriptTitle, dueDate, abstract }
=======
    if (!USE_MOCK) return http.post('/notifications/reviewer-invitation', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true })
  },
  
  // Send decision notification
  sendDecisionNotification: (data) => {
<<<<<<< HEAD
    // data: { authorEmail, manuscriptId, decisionType, comments? }
=======
    if (!USE_MOCK) return http.post('/notifications/decision', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true })
  },
  
  // Send revision request
  sendRevisionRequest: (data) => {
<<<<<<< HEAD
    // data: { authorEmail, manuscriptId, revisionDeadline, comments }
=======
    if (!USE_MOCK) return http.post('/notifications/revision', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true })
  },
  
  // Send acceptance notification
  sendAcceptanceNotification: (data) => {
<<<<<<< HEAD
    // data: { authorEmail, manuscriptId, publicationDate? }
=======
    if (!USE_MOCK) return http.post('/notifications/acceptance', data)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true })
  },
  
  // Send test email
  sendTestEmail: (email) => {
<<<<<<< HEAD
=======
    if (!USE_MOCK) return http.post('/notifications/test', { email })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    return mockRequest({ success: true })
  }
}
