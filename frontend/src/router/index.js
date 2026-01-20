import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// 主站路由 - 无登录限制，所有请求仅调用主站数据库对应的接口
const mainRoutes = [
  { path: '/', redirect: '/login' },
  { path: '/home', name: 'main-home', component: () => import('../views/MainHome.vue') },
  { path: '/directory', name: 'main-directory', component: () => import('../views/MainDirectory.vue') },
  { path: '/journal/:id', name: 'main-journal-detail', component: () => import('../views/MainJournalDetail.vue') },
  { path: '/search', name: 'main-search', component: () => import('../views/MainSearch.vue') },
  { path: '/submit', name: 'main-submit', component: () => import('../views/MainSubmit.vue') },
  { path: '/submission-rules', name: 'main-submission-rules', component: () => import('../views/MainSubmit.vue') },
  { path: '/profile', name: 'main-profile', component: () => import('../views/MainProfile.vue') },
  { path: '/account-security', name: 'account-security', component: () => import('../views/MainAccountSecurity.vue') },
  // 帮助中心相关路由
  { path: '/faq', name: 'main-faq', component: () => import('../views/MainFaq.vue') },
  { path: '/contact', name: 'main-contact', component: () => import('../views/MainContact.vue') },
  { path: '/feedback', name: 'main-feedback', component: () => import('../views/MainFeedback.vue') },
  // 主站登录注册路由
  { path: '/login', name: 'main-login', component: () => import('../views/auth/Login.vue') },
  { path: '/register', name: 'main-register', component: () => import('../views/auth/Register.vue') }
]

// 后台主页路由 - 需登录验证，所有请求仅调用后台主页数据库对应的接口
const adminRoutes = [
  // 认证路由
  { path: '/admin/login', name: 'admin-login', component: () => import('../views/auth/AdminLogin.vue') },
  { path: '/admin/register', name: 'admin-register', component: () => import('../views/auth/AdminRegister.vue') },
  
  // 管理员路由
  { path: '/admin/dashboard', name: 'admin-dashboard', component: () => import('../views/admin/Dashboard.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/Users.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/reviewer-management', name: 'admin-reviewer-management', component: () => import('../views/admin/ReviewerManagement.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/account-status', name: 'admin-account-status', component: () => import('../views/admin/AccountStatus.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/journals', name: 'admin-journals', component: () => import('../views/admin/Journals.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/modules', name: 'admin-modules', component: () => import('../views/admin/Modules.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  // 系统设置路由
  { path: '/admin/system/basic', name: 'admin-system-basic', component: () => import('../views/admin/system/BasicConfig.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/notification', name: 'admin-system-notification', component: () => import('../views/admin/system/NotificationConfig.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/logs', name: 'admin-system-logs', component: () => import('../views/admin/system/LogsManagement.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/modules', name: 'admin-system-modules', component: () => import('../views/admin/Modules.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/invitation-codes', name: 'admin-system-invitation-codes', component: () => import('../views/admin/InvitationCodes.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  
  // 审核员路由
  { path: '/admin/audit-dashboard', name: 'admin-audit-dashboard', component: () => import('../views/reviewer/Dashboard.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  { path: '/admin/audit-list', name: 'admin-audit-list', component: () => import('../views/reviewer/Pending.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  { path: '/admin/audit-history', name: 'admin-audit-history', component: () => import('../views/reviewer/History.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  
  // 作者路由
  { path: '/admin/author-dashboard', name: 'admin-author-dashboard', component: () => import('../views/author/Dashboard.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-submit', name: 'admin-author-submit', component: () => import('../views/author/Submit.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/submission-rules', name: 'admin-submission-rules', component: () => import('../views/author/Submit.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-history', name: 'admin-author-history', component: () => import('../views/author/History.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-profile', name: 'admin-author-profile', component: () => import('../views/author/Profile.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  
  // 稿件管理子路由
  { path: '/admin/manuscript/my', name: 'admin-manuscript-my', component: () => import('../views/admin/manuscript/MyManuscripts.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/manuscript/progress', name: 'admin-manuscript-progress', component: () => import('../views/admin/manuscript/ManuscriptProgress.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/manuscript/history', name: 'admin-manuscript-history', component: () => import('../views/admin/manuscript/ManuscriptHistory.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  
  // 个人中心子路由
  { path: '/admin/profile-security', name: 'admin-profile-security', component: () => import('../views/admin/ProfileSecurity.vue'), meta: { requiresAuth: true, roles: ['admin', 'reviewer', 'author'] } },
  { path: '/admin/profile-logs', name: 'admin-profile-logs', component: () => import('../views/admin/ProfileLogs.vue'), meta: { requiresAuth: true, roles: ['admin', 'reviewer', 'author'] } },
  { path: '/admin/notifications', name: 'admin-notifications', component: () => import('../views/admin/Notifications.vue'), meta: { requiresAuth: true, roles: ['admin', 'reviewer', 'author'] } },
  { path: '/admin/profile-manuscript-status', name: 'admin-profile-manuscript-status', component: () => import('../views/admin/ProfileManuscriptStatus.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/feedback-management', name: 'admin-feedback-management', component: () => import('../views/admin/AdminFeedbackManagement.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  
  // 投稿指南路由
  { path: '/admin/guide/instructions', name: 'admin-guide-instructions', component: () => import('../views/admin/guide/Instructions.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/guide/faq', name: 'admin-guide-faq', component: () => import('../views/admin/guide/FAQ.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  
  // 帮助中心路由
  { path: '/admin/help/consultation', name: 'admin-help-consultation', component: () => import('../views/admin/help/Consultation.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/help/feedback', name: 'admin-help-feedback', component: () => import('../views/admin/help/Feedback.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  
  // 公共后台路由
  { path: '/admin/review-records/:id', name: 'admin-review-records', component: () => import('../views/ReviewRecords.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  // 后台稿件详情路由
  { path: '/admin/journal/:id', name: 'admin-journal-detail', component: () => import('../views/AdminJournalDetail.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...mainRoutes,
    ...adminRoutes
  ]
})

// 导航守卫 - 实现权限控制和路由隔离
router.beforeEach((to, from, next) => {
  // 从localStorage直接获取用户信息，避免在路由初始化时使用useUserStore()
  let currentUser = null
  let currentRole = 'user'
  
  try {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      currentUser = JSON.parse(storedUser)
      currentRole = currentUser?.role || 'user'
    }
  } catch (error) {
    console.error('解析用户信息失败:', error)
    localStorage.removeItem('user')
  }
  
  // 根路径处理：未登录用户显示登录页，已登录用户显示对应首页
  if (to.path === '/') {
    if (currentUser) {
      // 已登录用户根据角色跳转到对应首页
      if (currentRole === 'admin') {
        next({ name: 'admin-dashboard' })
      } else if (currentRole === 'reviewer') {
        next({ name: 'admin-audit-dashboard' })
      } else if (currentRole === 'author') {
        next({ name: 'admin-author-dashboard' })
      } else {
        next({ name: 'main-home' })
      }
    } else {
      // 未登录用户显示登录页
      next({ name: 'main-login' })
    }
    return
  }
  
  // 已登录用户访问主站登录页，重定向到首页
  if (to.path === '/login' && currentUser) {
    next({ name: 'main-home' })
    return
  }
  
  // 已登录用户访问后台登录页，重定向到对应角色的后台首页
  if (to.path === '/admin/login' && currentUser) {
    switch (currentRole) {
      case 'admin':
        next({ name: 'admin-dashboard' })
        break
      case 'reviewer':
        next({ name: 'admin-audit-dashboard' })
        break
      case 'author':
        next({ name: 'admin-author-dashboard' })
        break
      default:
        // 普通用户重定向到主站首页，避免无限重定向
        next({ name: 'main-home' })
    }
    return
  }
  
  // 主站路由（除登录页外）和后台注册页，直接放行
  if (!to.path.startsWith('/admin') || to.path.startsWith('/admin/register')) {
    next()
    return
  }
  
  // 后台路由访问控制
  if (to.path.startsWith('/admin')) {
    // 未登录用户，重定向到后台登录页
    if (!currentUser) {
      next({ name: 'admin-login' })
      return
    }
    
    // 权限检查 - 验证是否有权限访问该路由
    if (to.meta.requiresAuth) {
      // 权限逻辑：高权限角色可以访问低权限角色的路由
      // 检查当前角色是否包含在允许的角色列表中
      if (to.meta.roles.includes(currentRole)) {
        next()
      } else {
        // 权限不足，根据角色跳转到对应首页
        switch (currentRole) {
          case 'admin':
            next({ name: 'admin-dashboard' })
            break
          case 'reviewer':
            next({ name: 'admin-audit-dashboard' })
            break
          case 'author':
            next({ name: 'admin-author-dashboard' })
            break
          default:
            // 清除localStorage中的用户信息
            localStorage.removeItem('user')
            next({ name: 'admin-login' })
        }
      }
    } else {
      next()
    }
  }
})

// 看门狗功能 - 定期检查用户权限
setInterval(() => {
  try {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      const currentUser = JSON.parse(storedUser)
      const currentRole = currentUser.role || 'user'
      const currentPath = window.location.pathname
      
      // 检查当前页面是否需要更高权限
      if (currentPath.startsWith('/admin')) {
        // 获取当前路由信息
        const matchedRoute = router.currentRoute.value
        
        // 检查权限 - 高权限角色可以访问低权限角色的路由
        if (matchedRoute.meta.requiresAuth && !matchedRoute.meta.roles.includes(currentRole)) {
          // 清除localStorage中的用户信息并跳转到登录页
          localStorage.removeItem('user')
          router.push({ name: 'admin-login' })
        }
      }
    }
  } catch (error) {
    console.error('看门狗检查失败:', error)
    // 出错时清除用户信息，避免无限循环
    localStorage.removeItem('user')
  }
}, 5000) // 每5秒检查一次

export default router
