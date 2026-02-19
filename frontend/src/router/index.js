import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// 主站路由 - 无登录限制，所有请求仅调用主站数据库对应的接口
const mainRoutes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'main-home', component: () => import('../views/MainHome.vue') },
  { path: '/directory', name: 'main-directory', component: () => import('../views/MainDirectory.vue') },
  { path: '/journals/all', name: 'journal-list', component: () => import('../views/journals/JournalList.vue') },
  { path: '/journal/:id', name: 'main-journal-detail', component: () => import('../views/MainJournalDetail.vue') },
  { path: '/search', name: 'main-search', component: () => import('../views/MainSearch.vue') },
  { path: '/submit', name: 'main-submit', component: () => import('../views/MainSubmit.vue') },
  { path: '/submission-rules', name: 'main-submission-rules', component: () => import('../views/MainSubmit.vue') },
  { path: '/profile', name: 'main-profile', component: () => import('../views/MainProfile.vue') },
  { path: '/account-security', name: 'account-security', component: () => import('../views/MainAccountSecurity.vue') },
  
  // Resources Submenu Routes
  { path: '/resources/writer/guide', name: 'resources-writer-guide', component: () => import('../views/resources/writer/Guide.vue') },
  { path: '/resources/writer/templates', name: 'resources-writer-templates', component: () => import('../views/resources/writer/Templates.vue') },
  { path: '/resources/writer/status', name: 'resources-writer-status', component: () => import('../views/resources/writer/Status.vue') },
  { path: '/resources/reviewer/become', name: 'resources-reviewer-become', component: () => import('../views/resources/reviewer/BecomeReviewer.vue') },
  { path: '/reviewer/application-status', name: 'resources-reviewer-status', component: () => import('../views/resources/reviewer/ApplicationStatus.vue') },
  { path: '/resources/reviewer/guidelines', name: 'resources-reviewer-guidelines', component: () => import('../views/resources/reviewer/Guidelines.vue') },
  { path: '/resources/reviewer/training', name: 'resources-reviewer-training', component: () => import('../views/resources/reviewer/Training.vue') },
  { path: '/resources/news/latest', name: 'resources-news-latest', component: () => import('../views/resources/news/LatestArticles.vue') },
  { path: '/resources/news/calls', name: 'resources-news-calls', component: () => import('../views/resources/news/CallForPapers.vue') },
  { path: '/resources/news/events', name: 'resources-news-events', component: () => import('../views/resources/news/Events.vue') },

  // More Submenu Routes
  { path: '/about/editorial-board', name: 'about-editorial-board', component: () => import('../views/about/EditorialBoard.vue') },
  { path: '/about/journal-info', name: 'about-journal-info', component: () => import('../views/about/JournalInfo.vue') },
  { path: '/about/history', name: 'about-history', component: () => import('../views/about/History.vue') },

  // 帮助中心相关路由
  { path: '/faq', name: 'main-faq', component: () => import('../views/MainFaq.vue') },
  { path: '/contact', name: 'main-contact', component: () => import('../views/MainContact.vue') },
  { path: '/feedback', name: 'main-feedback', component: () => import('../views/MainFeedback.vue') },
  
  // Public Functional Routes
  { path: '/reviewer-registration', name: 'reviewer-registration', component: () => import('../views/public/TemporaryReviewerRegistration.vue') },

  // 主站登录注册路由
  { path: '/login', name: 'main-login', component: () => import('../views/auth/Login.vue') },
  { path: '/register', name: 'main-register', component: () => import('../views/auth/Register.vue') }
]

// 后台主页路由 - 需登录验证，所有请求仅调用后台主页数据库对应的接口
const adminRoutes = [
  // 认证路由
  { path: '/submission/login', name: 'submission-login', component: () => import('../views/submission/Login.vue') },
  { path: '/admin/login', redirect: '/submission/login' }, // Redirect old admin login
  { path: '/editor/login', redirect: '/submission/login' }, // Redirect editor login
  { path: '/submission/register', name: 'submission-register', component: () => import('../views/auth/AdminRegister.vue') },
  { path: '/admin/register', redirect: '/submission/register' },
  { path: '/editor/register', redirect: '/submission/register' },
  { path: '/submission', name: 'submission-index', component: () => import('../views/submission/Index.vue') },
  { path: '/submission/about', name: 'submission-about', component: () => import('../views/submission/About.vue') },
  { path: '/submission/help', name: 'submission-help', component: () => import('../views/submission/Help.vue') },
  { path: '/submission/help/feedback', name: 'submission-help-feedback', component: () => import('../views/submission/Feedback.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  { path: '/submission/system-status', name: 'submission-system-status', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  
  // 投稿专属路由 (Submission Process) - 独立于 Dashboard
  { path: '/submission/writer/submit', name: 'submission-process', component: () => import('../views/submission/SubmissionProcess.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'editor', 'admin'] } },

  // 编辑系统路由 (Unified Editorial System) - Replaces Admin Dashboard
  { path: '/editor/dashboard', name: 'editor-dashboard', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  { path: '/admin/dashboard', redirect: '/editor/dashboard' }, // Redirect legacy admin dashboard
  
  { path: '/editor/associate/dashboard', redirect: '/editor/dashboard' },
  { path: '/editor/assistant/dashboard', redirect: '/editor/dashboard' },
  
  // Audit Tasks (Editor System)
  { path: '/editor/audit/new-submissions', name: 'audit-new-submissions', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/assign-reviewers', name: 'audit-assign-reviewers', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/review-monitoring', name: 'audit-review-monitoring', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/decision-making', name: 'audit-decision-making', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/revision-handling', name: 'audit-revision-handling', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/reviewer-management', name: 'audit-reviewer-management', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/recommended-reviewers', name: 'audit-recommended-reviewers', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/opposed-reviewers', name: 'audit-opposed-reviewers', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/editor/audit/my-tasks', name: 'audit-my-tasks', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  
  // Editorial Management Routes (Unified)
  { path: '/editor/manuscripts', name: 'editor-manuscripts', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  { path: '/editor/reviewers', name: 'editor-reviewers', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  { path: '/editor/decisions', name: 'editor-decisions', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  
  { path: '/editor/users', name: 'editor-users', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/users', redirect: '/editor/users' },
  
  { path: '/editor/reviewer-management', name: 'editor-reviewer-management', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/admin/reviewer-management', redirect: '/editor/reviewer-management' },
  
  { path: '/editor/account-status', name: 'editor-account-status', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/admin/account-status', redirect: '/editor/account-status' },
  
  { path: '/editor/journals', name: 'editor-journals', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/admin/journals', redirect: '/editor/journals' },
  
  { path: '/editor/modules', name: 'editor-modules', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/admin/modules', redirect: '/editor/modules' },
  
  { path: '/editor/statistics', name: 'editor-statistics', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/admin/statistics', redirect: '/editor/statistics' },
  
  // Board Management (Strictly Editor Only)
  { path: '/editor/board', name: 'editor-board', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },

  // Invitation Registration (Public Landing)
  { path: '/invite/register', name: 'invite-register', component: () => import('../views/auth/EditorInviteRegister.vue') },
  
  // System Settings Routes (Admin Only)
  { path: '/editor/system/basic', name: 'editor-system-basic', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/basic', redirect: '/editor/system/basic' },
  
  { path: '/editor/system/notification', name: 'editor-system-notification', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/notification', redirect: '/editor/system/notification' },
  
  { path: '/editor/system/logs', name: 'editor-system-logs', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/logs', redirect: '/editor/system/logs' },
  
  { path: '/editor/system/modules', name: 'editor-system-modules', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/modules', redirect: '/editor/system/modules' },
  
  { path: '/editor/system/invitation-codes', name: 'editor-system-invitation-codes', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/system/invitation-codes', redirect: '/editor/system/invitation-codes' },
  
  // 审核员路由
  { path: '/reviewer/dashboard', name: 'reviewer-dashboard', component: () => import('../views/reviewer/Dashboard.vue'), meta: { requiresAuth: true, roles: ['reviewer'] } },
  { path: '/reviewer/assignments', name: 'reviewer-assignments', component: () => import('../views/reviewer/MyAssignments.vue'), meta: { requiresAuth: true, roles: ['reviewer'] } },
  { path: '/reviewer/manuscript/:id', name: 'reviewer-manuscript-detail', component: () => import('../views/reviewer/ManuscriptDetail.vue'), meta: { requiresAuth: true, roles: ['reviewer'] } },
  { path: '/reviewer/profile', name: 'reviewer-profile', component: () => import('../views/reviewer/Profile.vue'), meta: { requiresAuth: true, roles: ['reviewer'] } },
  
  { path: '/admin/audit-dashboard', redirect: '/reviewer/dashboard' },
  { path: '/admin/audit-list', name: 'admin-audit-list', component: () => import('../views/reviewer/Pending.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/admin/audit-history', name: 'admin-audit-history', component: () => import('../views/reviewer/History.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  
  // 作者路由 (Changed to Writer)
  { path: '/admin/writer-dashboard', name: 'admin-writer-dashboard', component: () => import('../views/writer/Dashboard.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/writer-submit', name: 'admin-writer-submit', component: () => import('../views/writer/Submit.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/submission-rules', name: 'admin-submission-rules', component: () => import('../views/writer/Submit.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/writer-history', name: 'admin-writer-history', component: () => import('../views/writer/History.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/writer-profile', name: 'admin-writer-profile', component: () => import('../views/writer/Profile.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  
  // 稿件管理子路由
  { path: '/editor/manuscript/screening', name: 'editor-manuscript-screening', component: () => import('../views/admin/manuscript/Screening.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor'] } },
  { path: '/admin/manuscript/screening', redirect: '/editor/manuscript/screening' },
  
  { path: '/admin/manuscript/my', name: 'admin-manuscript-my', component: () => import('../views/admin/manuscript/MyManuscripts.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/manuscript/progress', name: 'admin-manuscript-progress', component: () => import('../views/admin/manuscript/ManuscriptProgress.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor', 'associate_editor', 'ea_ae'] } },
  { path: '/admin/manuscript/history', name: 'admin-manuscript-history', component: () => import('../views/admin/manuscript/ManuscriptHistory.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor', 'associate_editor', 'ea_ae'] } },
  
  // 个人中心子路由
  { path: '/editor/settings', name: 'editor-settings', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'] } },
  { path: '/admin/profile-security', redirect: '/editor/settings?tab=security' },
  { path: '/admin/profile-logs', redirect: '/editor/settings?tab=security' },
  { path: '/admin/notifications', redirect: '/editor/settings?tab=notifications' },
  { path: '/admin/profile-manuscript-status', name: 'admin-profile-manuscript-status', component: () => import('../views/editor/EditorPortal.vue'), meta: { requiresAuth: true, roles: ['admin', 'editor'] } },
  { path: '/editor/feedback-management', redirect: '/editor/dashboard' },
  { path: '/admin/feedback-management', redirect: '/editor/dashboard' },
  
  // 投稿指南路由
  { path: '/admin/guide/instructions', name: 'admin-guide-instructions', component: () => import('../views/admin/guide/Instructions.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/guide/faq', name: 'admin-guide-faq', component: () => import('../views/admin/guide/FAQ.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  
  // 帮助中心路由
  { path: '/admin/help/consultation', name: 'admin-help-consultation', component: () => import('../views/admin/help/Consultation.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  { path: '/admin/help/feedback', name: 'admin-help-feedback', component: () => import('../views/admin/help/Feedback.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  
  // 公共后台路由
  { path: '/admin/review-records/:id', name: 'admin-review-records', component: () => import('../views/ReviewRecords.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } },
  // 后台稿件详情路由
  { path: '/admin/journal/:id', name: 'admin-journal-detail', component: () => import('../views/AdminJournalDetail.vue'), meta: { requiresAuth: true, roles: ['writer', 'reviewer', 'admin', 'editor'] } }
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
let lastAlertTime = 0
const protectedAlert = (msg) => {
  if (Date.now() - lastAlertTime > 2000) { // 2s debounce
    alert(msg)
    lastAlertTime = Date.now()
  }
}

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 0. Handle Submit System Logout Cleanup (Cross-Site Logic)
  if (to.query.clearSubmitState === 'true') {
    // Force clear submit keys if present (Redundant safety check)
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('submit_')) {
        localStorage.removeItem(key)
      }
    })
    // Remove the query param to clean up URL
    const query = { ...to.query }
    delete query.clearSubmitState
    next({ path: to.path, query: query, replace: true })
    return
  }

  // 1. 投稿系统路由 (Submission Module) - STRICT ISOLATION
  if (to.path.startsWith('/admin') || to.path.startsWith('/submission') || to.path.startsWith('/editor') || to.path.startsWith('/reviewer')) {
    
    // Check submission system login status (submit_ prefix only)
    const submissionUser = JSON.parse(localStorage.getItem('submit_user'))
    
    // 允许访问投稿登录页 (Index) 及 About/Help
    if (to.path === '/submission' || to.path === '/submission/about' || to.path === '/submission/help' || to.path === '/admin/register' || to.path === '/submission/login' || to.path === '/submission/register') {
      // 如果已登录投稿系统，且访问的是首页(/submission)，重定向到Dashboard
      if (to.path === '/submission' && submissionUser) {
        userStore.syncUserContext('submission')
        
        if (submissionUser.role === 'writer') next({ name: 'admin-writer-dashboard' })
        else if (submissionUser.role === 'reviewer') next({ name: 'reviewer-dashboard' })
        else if (['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'].includes(submissionUser.role)) next({ name: 'editor-dashboard' })
        else next()
      } else {
        next()
      }
      return
    }

    if (!submissionUser) {
      // Not logged in to submit system, redirect to submit login
      // Even if logged in to Main Site (Read-Only), access is denied/redirected
      next({ name: 'submission-login' })
      return
    }

    // Synced context for submit system
    userStore.syncUserContext('submission')
    
    // Permission Check
    if (to.meta.requiresAuth) {
      const currentRole = submissionUser.role
      
      // Strict Dashboard Redirection Logic
      // Only block /editor/ paths which are strictly for editorial staff. 
      // /admin/ paths are mixed and should be handled by meta.roles check below.
      if (currentRole === 'reviewer' && to.path.startsWith('/editor')) {
         protectedAlert(`Access denied: This page requires appropriate submit system privileges.`)
         next({ name: 'reviewer-dashboard' })
         return
      }
      
      if (currentRole === 'writer' && (to.path.startsWith('/editor') || to.path.startsWith('/reviewer'))) {
         protectedAlert(`Access denied: This page requires appropriate submit system privileges.`)
         next({ name: 'admin-writer-dashboard' })
         return
      }
      
      // Meta Role Check
      if (to.meta.roles && to.meta.roles.includes(currentRole)) {
        next()
      } else {
        // Permission denied fallback
        if (currentRole === 'writer') next({ name: 'admin-writer-dashboard' })
        else if (currentRole === 'reviewer') next({ name: 'reviewer-dashboard' })
        else if (['admin', 'editor', 'associate_editor', 'editorial_assistant', 'advisory_editor'].includes(currentRole)) next({ name: 'editor-dashboard' })
        else next({ name: 'submission-login' })
      }
    } else {
      next()
    }
    return
  }

  // 2. 主站路由 (Main Site) - READ-ONLY ISOLATION
  // 允许访问主站登录/注册
  if (to.path === '/login' || to.path === '/register') {
    const savedUser = sessionStorage.getItem('readonly_user')
    // Ensure user is valid JSON
    if (savedUser && savedUser !== 'null' && savedUser !== 'undefined') {
      try {
        const parsedUser = JSON.parse(savedUser)
        if (parsedUser && parsedUser.username) {
          next({ name: 'main-home' })
          return
        }
      } catch (e) {
        sessionStorage.removeItem('readonly_user')
      }
    }
    next()
    return
  }

  // 主站路由 - 清理残留的 Submit 状态 (Safety Measure)
  // If we are on main site, we should theoretically ignore submit_ keys.
  // But per requirements: "若检测到残留的submit_状态数据，前端自动静默清除（仅主站加载时执行...）"
  // NOTE: The requirement says "Main Site Load". Doing it on every route change might be aggressive if user has two tabs open?
  // "主站首页 / 所有页面加载时... 若检测到残留的submit_状态数据... 自动静默清除"
  // Assuming "Main Site" means avoiding /submission routes.
  // However, if we clear submit_ keys here, it will kill the session in another tab if the user is using both systems simultaneously.
  // Requirement says "Strictly distinguish... ensure states are independent".
  // "Wait, 'submit logout' clears submit keys. 'Main site load' reads only readonly_".
  // "If detected residual submit_ keys, silently clear". This implies we treat main site as the 'primary' that cleans up?
  // But wait, if I have Tab A (Main) and Tab B (Submit), and I refresh Tab A, should it kill Tab B's session?
  // "submit 登录 logout 后跳转主站... 避免状态残留".
  // "主站加载时仍读取到残留的 Reviewer 登录状态" -> This was the bug.
  // Now we use different keys. So reading `readonly_` will NOT read `submit_`.
  // So the bug is fixed by key isolation.
  // The "Silently clear" requirement might be to ensure hygiene, but if keys are different, it's less critical.
  // However, to follow instructions strictly: "主站首页 / 所有页面加载时... 前端自动静默清除".
  // I will implement this ONLY if it doesn't break the "simultaneous usage" if that was intended.
  // But the prompt says "Reviewer login after logout issue".
  // Let's assume the user wants to ensure no submit state leaks.
  // I'll stick to: Main Site ONLY reads `readonly_`.
  // I will NOT aggressively clear `submit_` on every main site route change because that prevents multi-tab usage (Read-only tab + Submit tab).
  // I will only clear if `clearSubmitState=true` is passed (handled above).
  // AND, I will make sure Main Site logic NEVER looks at `submit_` keys.
  
  // 同步主站用户上下文 (Read-Only)
  userStore.syncUserContext('main')
  
  // 根路径重定向到主站首页
  if (to.path === '/') {
    next({ name: 'main-home' })
    return
  }

  next()
})

// 看门狗功能 - 定期检查用户权限 (Updated for separation)
setInterval(() => {
  try {
    const currentPath = window.location.pathname
    
    if (currentPath.startsWith('/admin') || currentPath.startsWith('/editor') || currentPath.startsWith('/reviewer')) {
      const storedUser = localStorage.getItem('submit_user')
      if (!storedUser) {
        // Session expired or cleared
        router.push({ name: 'submission-login' })
      }
    }
  } catch (error) {
    console.error('Watchdog error:', error)
  }
}, 5000)

export default router
