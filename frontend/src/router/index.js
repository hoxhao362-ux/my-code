import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// 主站路由 - 无登录限制，所有请求仅调用主站数据库对应的接口
const mainRoutes = [
  { path: '/', name: 'main-home', component: () => import('../views/MainHome.vue') },
  { path: '/journal/:id', name: 'main-journal-detail', component: () => import('../views/MainJournalDetail.vue') },
  { path: '/search', name: 'main-search', component: () => import('../views/MainSearch.vue') }
]

// 后台管理路由 - 需登录验证，所有请求仅调用后台管理数据库对应的接口
const adminRoutes = [
  // 认证路由
  { path: '/admin/login', name: 'admin-login', component: () => import('../views/auth/AdminLogin.vue') },
  { path: '/admin/register', name: 'admin-register', component: () => import('../views/auth/AdminRegister.vue') },
  
  // 管理员路由
  { path: '/admin/dashboard', name: 'admin-dashboard', component: () => import('../views/admin/Dashboard.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/Users.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/journals', name: 'admin-journals', component: () => import('../views/admin/Journals.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/modules', name: 'admin-modules', component: () => import('../views/admin/Modules.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  
  // 审核员路由
  { path: '/admin/audit-dashboard', name: 'admin-audit-dashboard', component: () => import('../views/reviewer/Dashboard.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  { path: '/admin/audit-list', name: 'admin-audit-list', component: () => import('../views/reviewer/Pending.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  { path: '/admin/audit-history', name: 'admin-audit-history', component: () => import('../views/reviewer/History.vue'), meta: { requiresAuth: true, roles: ['reviewer', 'admin'] } },
  
  // 作者路由
  { path: '/admin/author-dashboard', name: 'admin-author-dashboard', component: () => import('../views/author/Dashboard.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-submit', name: 'admin-author-submit', component: () => import('../views/author/Submit.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-history', name: 'admin-author-history', component: () => import('../views/author/History.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  { path: '/admin/author-profile', name: 'admin-author-profile', component: () => import('../views/author/Profile.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } },
  
  // 公共后台路由
  { path: '/admin/review-records/:id', name: 'admin-review-records', component: () => import('../views/ReviewRecords.vue'), meta: { requiresAuth: true, roles: ['author', 'reviewer', 'admin'] } }
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
  const userStore = useUserStore()
  const currentUser = userStore.user
  const currentRole = currentUser?.role || 'user'
  
  // 主站路由和后台路由的登录页、注册页，直接放行
  if (to.path.startsWith('/admin/login') || to.path.startsWith('/admin/register') || !to.path.startsWith('/admin')) {
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
            userStore.logout()
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
  const userStore = useUserStore()
  const currentUser = userStore.user
  if (currentUser) {
    const currentPath = window.location.pathname
    const currentRole = currentUser.role
    
    // 检查当前页面是否需要更高权限
    if (currentPath.startsWith('/admin')) {
      // 获取当前路由信息
      const matchedRoute = router.currentRoute.value
      
      // 检查权限
      if (matchedRoute.meta.requiresAuth && !matchedRoute.meta.roles.includes(currentRole)) {
        userStore.logout()
        router.push({ name: 'admin-login' })
      }
    }
  }
}, 5000) // 每5秒检查一次

export default router
