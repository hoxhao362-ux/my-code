import { mockRequest } from './api'

export const emailApi = {
  // Send single email
  sendEmail: (data) => {
    // data: { to, subject, content, template?, manuscriptId? }
    return mockRequest({ success: true, messageId: Date.now() })
  },
  
  // Send batch emails
  sendBatchEmails: (data) => {
    // data: { recipients: [{email, subject, content}], template? }
    return mockRequest({ success: true, sentCount: data.recipients?.length || 0 })
  },
  
  // Send reviewer invitation (using template)
  sendReviewerInvitation: (data) => {
    // data: { reviewerEmail, reviewerName, manuscriptId, manuscriptTitle, dueDate, abstract }
    return mockRequest({ success: true })
  },
  
  // Send decision notification
  sendDecisionNotification: (data) => {
    // data: { authorEmail, manuscriptId, decisionType, comments? }
    return mockRequest({ success: true })
  },
  
  // Send revision request
  sendRevisionRequest: (data) => {
    // data: { authorEmail, manuscriptId, revisionDeadline, comments }
    return mockRequest({ success: true })
  },
  
  // Send acceptance notification
  sendAcceptanceNotification: (data) => {
    // data: { authorEmail, manuscriptId, publicationDate? }
    return mockRequest({ success: true })
  },
  
  // Send test email
  sendTestEmail: (email) => {
    return mockRequest({ success: true })
  }
}
