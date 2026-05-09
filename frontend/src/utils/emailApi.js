// 邮件 API 工具类
// 注意：后端暂无独立的邮件通知 API 路由
// 邮件由工作流自动触发，通过 email_service.py 服务层调用
// 待后端实现后，再适配以下接口

import http from './http'

export const emailApi = {
  // TODO: 等待后端实现 /notifications/email 接口
  // sendEmail: (data) => http.post('/notifications/email', data),
  
  // TODO: 等待后端实现 /notifications/email/batch 接口
  // sendBatchEmails: (data) => http.post('/notifications/email/batch', data),
  
  // TODO: 等待后端实现 /notifications/reviewer-invitation 接口
  // sendReviewerInvitation: (data) => http.post('/notifications/reviewer-invitation', data),
}
