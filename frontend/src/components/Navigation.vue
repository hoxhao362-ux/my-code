<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useToastStore } from '../stores/toast'
import { useMessageStore } from '../stores/messages'
import NotificationBadge from './NotificationBadge.vue'

const router = useRouter()
const route = useRoute()
const { t, currentLang, setLang } = useI18n()
const toastStore = useToastStore()
const messageStore = useMessageStore()

const props = defineProps({
  user: Object,
  currentPage: String,
  toggleDirectory: Function,
  logout: Function,
  customNavigation: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['navigate'])

const handleNav = (key, path) => {
  if (props.customNavigation) {
    emit('navigate', key, path)
  } else {
    router.push(path)
  }
}

const toggleLang = () => {
  setLang(currentLang.value === 'en' ? 'zh' : 'en')
}

// 控制角色管理子菜单的显示状态
const showRoleMenu = ref(false)

// 控制期刊子菜单
const showJournalsMenu = ref(false)
// 控制资源子菜单 (聚合 Author/Reviewer/News)
const showResourcesMenu = ref(false)
// 控制更多子菜单 (聚合 Journal Info)
const showMoreMenu = ref(false)

// 控制个人资料子菜单
const showProfileMenu = ref(false)
// 控制系统设置子菜单
const showSystemMenu = ref(false)
// 控制帮助子菜单
const showHelpMenu = ref(false)
// 控制投稿子菜单
const showSubmissionMenu = ref(false)
// 控制稿件管理子菜单
const showManuscriptMenu = ref(false)
// 控制指南子菜单
const showGuideMenu = ref(false)
// 控制作者帮助子菜单
const showAuthorHelpMenu = ref(false)
const showAuditTasksMenu = ref(false)
// Control Reviewer Menu
const showReviewerMenu = ref(false)
// Control User Menu (Icon)
const showUserMenu = ref(false)
// Control Mobile Menu
const showMobileMenu = ref(false)
// Control Review Process Menu
const showReviewProcessMenu = ref(false)
// Control Publication & Analytics Menu
const showPubAnalyticsMenu = ref(false)
// Control Admin Tools Menu
const showAdminToolsMenu = ref(false)
// User Menu Ref
const userMenuRef = ref(null)

// Hover Timers
let hoverTimer = null
let closeTimer = null

// 搜索查询
const searchQuery = ref('')
// 订阅模态框
const showSubscribeModal = ref(false)
// Logout Modal
const showLogoutModal = ref(false)

// 处理鼠标悬停 (仅PC端)
const handleHover = (menu, isOpen) => {
  if (window.innerWidth > 768) {
    if (isOpen) {
      // Clear any pending close timer
      if (closeTimer) clearTimeout(closeTimer)
      
      // Delay open by 0.1s (100ms)
      hoverTimer = setTimeout(() => {
        // 打开时关闭其他菜单
        closeOtherMenus(menu)
        switch (menu) {
          case 'resources': showResourcesMenu.value = true; break;
          case 'more': showMoreMenu.value = true; break;
          case 'reviewer': showReviewerMenu.value = true; break; // Added Reviewer
          case 'profile': showProfileMenu.value = true; break;
          case 'help': showHelpMenu.value = true; break;
          case 'journals': showJournalsMenu.value = true; break;
          // Admin menus
          case 'role': showRoleMenu.value = true; break;
          case 'system': showSystemMenu.value = true; break;
          case 'submission': showSubmissionMenu.value = true; break;
          case 'manuscript': showManuscriptMenu.value = true; break;
          case 'guide': showGuideMenu.value = true; break;
          case 'authorHelp': showAuthorHelpMenu.value = true; break;
          case 'auditTasks': showAuditTasksMenu.value = true; break;
        }
      }, 100)
    } else {
      // Delay close by 0.2s (200ms)
      if (hoverTimer) clearTimeout(hoverTimer)
      
      closeTimer = setTimeout(() => {
        // 关闭
        switch (menu) {
          case 'resources': showResourcesMenu.value = false; break;
          case 'more': showMoreMenu.value = false; break;
          case 'reviewer': showReviewerMenu.value = false; break; // Added Reviewer
          case 'profile': showProfileMenu.value = false; break;
          case 'help': showHelpMenu.value = false; break;
          case 'journals': showJournalsMenu.value = false; break;
          // Admin menus
          case 'role': showRoleMenu.value = false; break;
          case 'system': showSystemMenu.value = false; break;
          case 'submission': showSubmissionMenu.value = false; break;
          case 'manuscript': showManuscriptMenu.value = false; break;
          case 'guide': showGuideMenu.value = false; break;
          case 'authorHelp': showAuthorHelpMenu.value = false; break;
          case 'auditTasks': showAuditTasksMenu.value = false; break;
        }
      }, 200)
    }
  }
}

// 切换Reviewer子菜单
const toggleReviewerMenu = (event) => {
  if (event) event.stopPropagation()
  showReviewerMenu.value = !showReviewerMenu.value
  closeOtherMenus('reviewer')
}

// 切换User子菜单
const toggleUserMenu = (event) => {
  if (event) event.stopPropagation()
  showUserMenu.value = !showUserMenu.value
  closeOtherMenus('user')
}

// Handle My Reviews Click
const handleMyReviewsClick = () => {
  if (props.user?.status === 'active') {
    // Check if we need to bridge the session to submission system
    import('../stores/user').then(({ useUserStore }) => {
      const userStore = useUserStore()
      // If not logged in to submission system, or logged in but context is different
      if (!userStore.submissionUser && props.user.role === 'reviewer') {
         // Silently login to submission system
         userStore.loginSubmission({ 
           username: props.user.username, 
           role: 'reviewer' 
         }).then(() => {
           router.push('/reviewer/assignments')
         }).catch(err => {
           console.error('Auto-login failed', err)
           router.push('/submission/login') // Fallback
         })
      } else {
         router.push('/reviewer/assignments')
      }
    })
    closeAllMenus()
  }
  // If not active, do nothing (tooltip handles message)
}

// 切换资源子菜单
const toggleResourcesMenu = (event) => {
  event.stopPropagation()
  showResourcesMenu.value = !showResourcesMenu.value
  closeOtherMenus('resources')
}

// 切换更多子菜单
const toggleMoreMenu = (event) => {
  event.stopPropagation()
  showMoreMenu.value = !showMoreMenu.value
  closeOtherMenus('more')
}

// 切换期刊子菜单
const toggleJournalsMenu = (event) => {
  if (event) event.stopPropagation()
  showJournalsMenu.value = !showJournalsMenu.value
  closeOtherMenus('journals')
}

// 切换个人资料子菜单
const toggleProfileMenu = (event) => {
  if (event) event.stopPropagation()
  showProfileMenu.value = !showProfileMenu.value
  closeOtherMenus('profile')
}

// 切换系统设置子菜单
const toggleSystemMenu = (event) => {
  if (event) event.stopPropagation()
  showSystemMenu.value = !showSystemMenu.value
  closeOtherMenus('system')
}

// 切换帮助子菜单
const toggleHelpMenu = (event) => {
  if (event) event.stopPropagation()
  showHelpMenu.value = !showHelpMenu.value
  closeOtherMenus('help')
}

// 切换投稿子菜单
const toggleSubmissionMenu = (event) => {
  if (event) event.stopPropagation()
  showSubmissionMenu.value = !showSubmissionMenu.value
  closeOtherMenus('submission')
}

// 切换稿件管理子菜单
const toggleManuscriptMenu = (event) => {
  if (event) event.stopPropagation()
  showManuscriptMenu.value = !showManuscriptMenu.value
  closeOtherMenus('manuscript')
}

// 切换指南子菜单
const toggleGuideMenu = (event) => {
  if (event) event.stopPropagation()
  showGuideMenu.value = !showGuideMenu.value
  closeOtherMenus('guide')
}

// 切换作者帮助子菜单
const toggleAuthorHelpMenu = (event) => {
  if (event) event.stopPropagation()
  showAuthorHelpMenu.value = !showAuthorHelpMenu.value
  closeOtherMenus('authorHelp')
}

// 切换审核任务子菜单
const toggleAuditTasksMenu = (event) => {
  if (event) event.stopPropagation()
  showAuditTasksMenu.value = !showAuditTasksMenu.value
  closeOtherMenus('auditTasks')
}

// 切换Review Process子菜单
const toggleReviewProcessMenu = (event) => {
  if (event) event.stopPropagation()
  showReviewProcessMenu.value = !showReviewProcessMenu.value
  closeOtherMenus('reviewProcess')
}

// 切换Publication & Analytics子菜单
const togglePubAnalyticsMenu = (event) => {
  if (event) event.stopPropagation()
  showPubAnalyticsMenu.value = !showPubAnalyticsMenu.value
  closeOtherMenus('pubAnalytics')
}

// 切换Admin Tools子菜单
const toggleAdminToolsMenu = (event) => {
  if (event) event.stopPropagation()
  showAdminToolsMenu.value = !showAdminToolsMenu.value
  closeOtherMenus('adminTools')
}

// 关闭其他菜单
const closeOtherMenus = (current) => {
  if (current !== 'journals') showJournalsMenu.value = false
  if (current !== 'resources') showResourcesMenu.value = false
  if (current !== 'more') showMoreMenu.value = false
  if (current !== 'reviewer') showReviewerMenu.value = false // Added
  if (current !== 'user') showUserMenu.value = false // Added
  if (current !== 'profile') showProfileMenu.value = false
  if (current !== 'help') showHelpMenu.value = false
  if (current !== 'role') showRoleMenu.value = false
  if (current !== 'system') showSystemMenu.value = false
  if (current !== 'submission') showSubmissionMenu.value = false
  if (current !== 'manuscript') showManuscriptMenu.value = false
  if (current !== 'guide') showGuideMenu.value = false
  if (current !== 'authorHelp') showAuthorHelpMenu.value = false
  if (current !== 'auditTasks') showAuditTasksMenu.value = false
  if (current !== 'reviewProcess') showReviewProcessMenu.value = false
  if (current !== 'pubAnalytics') showPubAnalyticsMenu.value = false
  if (current !== 'adminTools') showAdminToolsMenu.value = false
}

// 关闭所有子菜单
const closeAllMenus = () => {
  showJournalsMenu.value = false
  showResourcesMenu.value = false
  showMoreMenu.value = false
  showReviewerMenu.value = false // Added
  showUserMenu.value = false // Added
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
  showAuditTasksMenu.value = false
  showReviewProcessMenu.value = false
  showPubAnalyticsMenu.value = false
  showAdminToolsMenu.value = false
}

// 点击页面其他部分关闭子菜单
const handleClickOutside = () => {
  closeAllMenus()
}

// 监听点击事件
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 检查当前是否在后台
const isAdminRoute = () => {
  return window.location.pathname.startsWith('/admin') || window.location.pathname.startsWith('/submission') || window.location.pathname.startsWith('/editor') || window.location.pathname.startsWith('/reviewer')
}

const applicationStatus = ref('')

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  applicationStatus.value = localStorage.getItem('reviewer_application_status') || ''
})

const goToSubmit = () => {
  router.push('/submission')
}

const goToProfile = () => {
  if (isAdminRoute()) {
    router.push('/admin/author-profile')
  } else {
    router.push('/profile')
  }
}

const goToHome = () => {
  router.push('/home')
}

const goToAdminDashboard = () => {
  if (props.user?.role === 'reviewer') {
    router.push('/reviewer/dashboard')
  } else if (props.user?.role === 'author') {
    router.push('/admin/author-dashboard')
  } else {
    router.push('/editor/dashboard')
  }
}

const goToAuditList = () => {
  router.push('/admin/audit-list')
}

const goToAuditHistory = () => {
  router.push('/admin/audit-history')
}

const handleClearSubmit = () => {
  // 1. Remove from LocalStorage
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith('submit_')) {
      localStorage.removeItem(key)
    }
  })
  
  // 2. Also ensure store state is cleared via action
  import('../stores/user').then(({ useUserStore }) => {
    const userStore = useUserStore()
    userStore.logoutSubmission()
  })

  // 3. Feedback
  toastStore.success('Submit login status cleared successfully!')
}

const showClearSubmitButton = computed(() => {
  // Only show on Become Reviewer page as requested
  return route.path === '/resources/reviewer/become'
})

function handleSearch() {
  if (searchQuery.value && searchQuery.value.trim()) {
    console.log('Searching for:', searchQuery.value)
    router.push({ path: '/search', query: { q: searchQuery.value } })
  }
}

// 处理订阅
const handleSubscribe = () => {
  console.log('Subscribing...')
  toastStore.add({ message: t('common.success'), type: 'success' })
  showSubscribeModal.value = false
}

const confirmLogout = () => {
  showLogoutModal.value = true
  closeAllMenus()
}

const goToLogin = () => {
  console.log('Navigating to login page...')
  router.push('/login').catch(err => {
    console.error('Login navigation failed:', err)
  })
}

const goToMessages = () => {
  if (props.user?.role === 'author') {
    router.push('/author/messages')
  } else if (props.user?.role === 'reviewer') {
    router.push('/reviewer/messages')
  } else {
    router.push('/editor/messages')
  }
}

const handleLogout = () => {
  showLogoutModal.value = false
  
  // Check if we are in the submission/admin system context
  if (isAdminRoute()) {
    // If so, use submission logout logic
    import('../stores/user').then(({ useUserStore }) => {
      const userStore = useUserStore()
      userStore.logoutSubmission()
      
      // Show Success Toast
      const toast = document.createElement('div')
      toast.className = 'logout-toast'
      toast.textContent = 'Successfully logged out of submit system'
      toast.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #4caf50;
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        z-index: 9999;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        animation: fadeIn 0.3s ease;
      `
      document.body.appendChild(toast)
      
      setTimeout(() => {
        toast.style.opacity = '0'
        setTimeout(() => document.body.removeChild(toast), 300)
        
        // Return to submission login page instead of main site
        router.push('/submission')
      }, 1500)
    })
  } else {
    // Reviewer Logout Special Case (Logged in as submissionUser but in Main Site context - likely impossible now due to strict guards, but kept for safety)
    if (props.user?.role === 'reviewer') {
       // This branch might be dead code now if strict isolation works, but if they managed to get here:
       import('../stores/user').then(({ useUserStore }) => {
         const userStore = useUserStore()
         userStore.logoutSubmission()
         window.location.href = '/?clearSubmitState=true'
       })
       return
    }

    // Otherwise, standard main site logout (Read-Only)
    if (props.logout) {
      props.logout()
    }
    // Also clear store manually just in case
    import('../stores/user').then(({ useUserStore }) => {
       const userStore = useUserStore()
       userStore.logout()
       router.push('/login')
    })
  }
}
</script>

<template>
  <!-- System Status Banners -->
  <div v-if="!isAdminRoute() && user" class="system-banner read-only">
    {{ t('nav.readOnlyMode') }} | {{ t('submission.welcome.platform') }}
  </div>
  <div v-if="isAdminRoute() && user" class="system-banner submit-mode">
    {{ t('nav.submitSystem') }} - [{{ t('nav.userRole') }}: {{ user.role }}]
  </div>

  <nav class="navbar" :class="{ 'reviewer-navbar': user?.role === 'reviewer', 'has-banner': user }" role="navigation" :aria-label="t('nav.mainNavigation')">
    <div class="navbar-container" :class="{ 'reviewer-container': user?.role === 'reviewer' }">
      <!-- 第一行：期刊名字、用户信息、Logout -->
      <div class="navbar-top-row">
        <div class="navbar-logo">
          <h1>{{ t('nav.logo') }}</h1>
        </div>
        <div class="navbar-top-right">
          <span v-if="user" class="user-info">
            <span class="user-name">{{ user.username }}</span>
            <span class="divider">|</span>
            <a href="#" @click.prevent="handleLogout" class="logout-link" role="button" tabindex="0" @keydown.enter="handleLogout">{{ t('nav.logout') }}</a>
          </span>
        </div>
      </div>
      
      <!-- 第二行：导航菜单 -->
      <div class="nav-wrapper">
        <!-- 主站导航 -->
        <template v-if="!isAdminRoute()">
          <!-- Mobile Hamburger -->
          <div class="hamburger-menu mobile-only" @click="showMobileMenu = true" role="button" :aria-label="t('nav.toggleNavigation')" tabindex="0" @keydown.enter="showMobileMenu = true">
             ☰
          </div>

          <!-- Desktop Menu -->
          <ul class="navbar-menu desktop-only" role="menubar">
            <!-- 1. Home -->
            <li class="nav-item" role="none">
              <a href="#" class="nav-link" :class="{ active: currentPage === 'home' }" @click.prevent="goToHome" role="menuitem">
                {{ t('nav.home') }}
              </a>
            </li>

          <!-- 2. Journals -->
          <li class="nav-item" role="none">
            <a href="#" class="nav-link journals-link" :class="{ active: currentPage === 'journals' }" @click.prevent="$router.push('/journals/all')" role="menuitem">
              {{ t('nav.journals') }}
            </a>
          </li>

          <!-- 3. Submit (No Change) -->
          <li class="nav-item" role="none">
            <a href="#" class="nav-link btn-submit-nav" @click.prevent="goToSubmit()" role="menuitem">
              {{ t('nav.submit') }}
            </a>
          </li>

          <!-- 4. Resources (Aggregated) -->
          <li class="nav-item dropdown" @mouseenter="handleHover('resources', true)" @mouseleave="handleHover('resources', false)" role="none">
            <div class="dropdown-toggle" @click="toggleResourcesMenu" role="button" aria-haspopup="true" :aria-expanded="showResourcesMenu" tabindex="0" @keydown.enter="toggleResourcesMenu">
              <a href="#" class="nav-link">{{ t('nav.resources') }} ▼</a>
            </div>
            <ul class="dropdown-menu" v-if="showResourcesMenu" role="menu">
              <li class="dropdown-header" role="presentation">{{ t('nav.authorResources') }}</li>
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/resources/author/guide'); closeAllMenus()" role="menuitem">{{ t('nav.guideForAuthors') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/author/templates'); closeAllMenus()">{{ t('nav.templates') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/author/status'); closeAllMenus()">{{ t('nav.checkStatus') }}</a></li>
              <li><div class="dropdown-divider"></div></li>
              <li class="dropdown-header">{{ t('nav.reviewerResources') }}</li>
              <li>
                <a 
                  href="#" 
                  class="nav-link" 
                  :class="{ 'disabled-link': applicationStatus === 'pending_review' }"
                  :title="applicationStatus === 'pending_review' ? 'Your application is currently under review' : ''"
                  @click.prevent="$router.push('/resources/reviewer/become'); closeAllMenus()"
                >
                  {{ t('nav.becomeReviewer') }}
                </a>
              </li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/guidelines'); closeAllMenus()">{{ t('nav.reviewerGuidelines') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/training'); closeAllMenus()">{{ t('nav.reviewerTraining') }}</a></li>
              
              <li><div class="dropdown-divider"></div></li>
              <li class="dropdown-header">{{ t('nav.newsEvents') }}</li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/news/latest'); closeAllMenus()">{{ t('nav.latestArticles') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/news/calls'); closeAllMenus()">{{ t('nav.callForPapers') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="$router.push('/resources/news/events'); closeAllMenus()">{{ t('nav.upcomingEvents') }}</a></li>
            </ul>
          </li>

          <!-- 5. Reviewer Dropdown (Visible for Reviewers OR Applicants) -->
          <li v-if="user && (user.role === 'reviewer' || applicationStatus)" class="nav-item dropdown" @mouseenter="handleHover('reviewer', true)" @mouseleave="handleHover('reviewer', false)" role="none">
            <div class="dropdown-toggle" @click="toggleReviewerMenu" role="button" aria-haspopup="true" :aria-expanded="showReviewerMenu" tabindex="0" @keydown.enter="toggleReviewerMenu">
              <a href="#" class="nav-link">{{ t('nav.reviewer') }} ▼</a>
            </div>
            <ul class="dropdown-menu reviewer-menu" v-if="showReviewerMenu" role="menu">
              <li role="none">
                <a 
                  href="#" 
                  class="nav-link" 
                  :class="{ 'disabled-link': applicationStatus === 'pending_review' }"
                  :title="applicationStatus === 'pending_review' ? 'Your application is currently under review' : ''"
                  @click.prevent="$router.push('/resources/reviewer/become'); closeAllMenus()"
                  role="menuitem"
                >
                  {{ t('nav.becomeReviewer') }}
                </a>
              </li>
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/guidelines'); closeAllMenus()" role="menuitem">{{ t('nav.reviewerGuidelines') }}</a></li>
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/training'); closeAllMenus()" role="menuitem">{{ t('nav.reviewerTraining') }}</a></li>
              <li role="separator"><div class="dropdown-divider"></div></li>
              
              <!-- My Reviews -->
              <li v-if="user.role === 'reviewer'" role="none">
                <a 
                  href="#" 
                  class="nav-link" 
                  :class="{ 'disabled-link': user?.status !== 'active' }"
                  @click.prevent="handleMyReviewsClick"
                  role="menuitem"
                >
                  {{ t('nav.myReviews') }}
                </a>
              </li>
              
              <!-- My Profile -->
              <li v-if="user.role === 'reviewer'" role="none">
                <a 
                  href="#" 
                  class="nav-link" 
                  @click.prevent="$router.push('/reviewer/profile'); closeAllMenus()"
                  role="menuitem"
                >
                  {{ t('nav.myProfile') }}
                </a>
              </li>
            </ul>
          </li>

          <!-- 6. Help (Simplified) -->
          <li class="nav-item" role="none">
            <a href="#" class="nav-link" @click.prevent="$router.push('/faq')" role="menuitem">
              {{ t('nav.help') }}
            </a>
          </li>

          <!-- 6. About (Aggregated) -->
          <li class="nav-item dropdown" @mouseenter="handleHover('more', true)" @mouseleave="handleHover('more', false)" role="none">
            <div class="dropdown-toggle" @click="toggleMoreMenu" role="button" aria-haspopup="true" :aria-expanded="showMoreMenu" tabindex="0" @keydown.enter="toggleMoreMenu">
              <a href="#" class="nav-link">{{ t('nav.more') }} ▼</a>
            </div>
            <ul class="dropdown-menu" v-if="showMoreMenu" role="menu">
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/about/editorial-board'); closeAllMenus()" role="menuitem">{{ t('nav.editorialBoard') }}</a></li>
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/about/journal-info'); closeAllMenus()" role="menuitem">{{ t('nav.journalInfo') }}</a></li>
              <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/about/history'); closeAllMenus()" role="menuitem">{{ t('nav.history') }}</a></li>
            </ul>
          </li>

          <!-- Spacer to push secondary nav to right -->
          <li class="nav-spacer" role="separator"></li>

          <!-- 7. Search Icon (Hover to expand) -->
          <li class="nav-item search-item" role="search">
            <div class="search-container">
              <div class="search-icon" role="button" :aria-label="t('nav.search')" tabindex="0">🔍</div>
              <div class="search-input-wrapper">
                 <input type="text" v-model="searchQuery" @keyup.enter="handleSearch" :placeholder="t('nav.searchPlaceholder')" :aria-label="t('nav.searchPlaceholder')" />
              </div>
            </div>
          </li>

          <!-- 7.5 Messages Icon -->
          <li v-if="user" class="nav-item" role="none">
            <a href="#" class="nav-link icon-link" @click.prevent="goToMessages" title="Messages">
              <span class="icon">✉️</span>
              <NotificationBadge :count="messageStore.unreadCount" />
            </a>
          </li>

          <!-- 8. Login / User Dropdown -->
          <template v-if="user">
             <!-- Modified for Reviewer: Click only, no hover -->
             <li class="nav-item dropdown" 
                 @mouseenter="user.role !== 'reviewer' && handleHover('profile', true)" 
                 @mouseleave="user.role !== 'reviewer' && handleHover('profile', false)">
              <div class="dropdown-toggle" @click="toggleProfileMenu">
                <a href="#" class="nav-link login-btn">{{ user.username }} ▼</a>
              </div>
              <ul class="dropdown-menu" v-if="showProfileMenu">
                <template v-if="user.role === 'reviewer'">
                  <li>
                    <a 
                      href="#" 
                      class="nav-link" 
                      :class="{ 'disabled-link': user?.status !== 'active' }"
                      @click.prevent="handleMyReviewsClick"
                    >
                      {{ t('nav.myReviews') }}
                    </a>
                  </li>
                  <li><a href="#" class="nav-link" @click.prevent="$router.push('/reviewer/profile'); closeAllMenus()">{{ t('nav.profile') }}</a></li>
                  <li><a href="#" class="nav-link" @click.prevent="handleLogout" :title="t('nav.logoutSubmit')">{{ t('nav.logoutSubmit') }}</a></li>
                </template>
                <template v-else>
                  <li><a href="#" class="nav-link" @click.prevent="$router.push('/profile'); closeAllMenus()">{{ t('nav.profile') }}</a></li>
                  <li><a href="#" class="nav-link" @click.prevent="$router.push('/account-security'); closeAllMenus()">{{ t('nav.settings') }}</a></li>
                  <li><div class="dropdown-divider"></div></li>
                  <li><a href="#" class="nav-link logout" @click.prevent="confirmLogout">{{ t('nav.logout') }}</a></li>
                </template>
              </ul>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
               <a href="#" class="nav-link login-btn" @click.prevent="goToLogin">{{ t('nav.login') }} ({{ t('nav.readOnly') }})</a>
            </li>
          </template>

           <!-- Language Switcher -->
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent="toggleLang">
              {{ currentLang === 'en' ? '中文' : 'En' }}
            </a>
          </li>
          </ul>
        </template>
        
        <!-- 审核员后台导航 (Reviewer Navigation - Standardized) -->
        <template v-else-if="user?.role === 'reviewer'">
          <!-- 第二行：导航菜单 -->
          <div class="nav-wrapper">
            <!-- Mobile Hamburger (Visible < 1024px) -->
            <div class="hamburger-menu" @click="showMobileMenu = true" role="button" :aria-label="t('nav.toggleNavigation')" tabindex="0" @keydown.enter="showMobileMenu = true">
              ☰
            </div>

            <!-- Desktop Menu -->
            <ul class="navbar-menu desktop-only" role="menubar">
              <!-- 1. Dashboard -->
              <li class="nav-item" role="none">
                <a href="#" class="nav-link" :class="{ active: currentPage === 'reviewer-dashboard' }" @click.prevent="router.push('/reviewer/dashboard')" role="menuitem">
                  {{ t('nav.dashboard') }}
                </a>
              </li>

              <!-- 2. My Assignments -->
              <li class="nav-item" role="none">
                <a href="#" class="nav-link" :class="{ active: currentPage === 'reviewer-assignments' }" @click.prevent="router.push('/reviewer/assignments')" role="menuitem">
                  {{ t('nav.myAssignments') }}
                </a>
              </li>

              <!-- 2.5 Letters & Invitations -->
              <li class="nav-item" role="none">
                <a href="#" class="nav-link" :class="{ active: currentPage === 'reviewer-letters' }" @click.prevent="router.push('/reviewer/letters')" role="menuitem">
                  {{ t('nav.lettersAndInvitations') }}
                </a>
              </li>

              <!-- 3. Profile -->
              <li class="nav-item" role="none">
                <a href="#" class="nav-link" :class="{ active: currentPage === 'reviewer-profile' }" @click.prevent="router.push('/reviewer/profile')" role="menuitem">
                  {{ t('nav.profile') }}
                </a>
              </li>

              <!-- 4. Resources -->
              <li class="nav-item dropdown" @mouseenter="handleHover('resources', true)" @mouseleave="handleHover('resources', false)" role="none">
                <div class="dropdown-toggle" @click="toggleResourcesMenu" role="button" aria-haspopup="true" :aria-expanded="showResourcesMenu" tabindex="0" @keydown.enter="toggleResourcesMenu">
                  <a href="#" class="nav-link">{{ t('nav.resources') }} ▼</a>
                </div>
                <ul class="dropdown-menu" v-if="showResourcesMenu" role="menu">
                  <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/guidelines'); closeAllMenus()" role="menuitem">{{ t('nav.reviewerGuidelines') }}</a></li>
                  <li role="none"><a href="#" class="nav-link" @click.prevent="$router.push('/resources/reviewer/training'); closeAllMenus()" role="menuitem">{{ t('nav.reviewerTraining') }}</a></li>
                </ul>
              </li>

              <!-- Language -->
              <li class="nav-item" role="none">
                 <a href="#" class="nav-link" @click.prevent="toggleLang" role="menuitem">
                   {{ currentLang === 'en' ? '中文' : 'En' }}
                 </a>
               </li>
            </ul>
          </div>
        </template>
        
        <!-- Unified Editor Navigation (Shared for all editor roles) -->
        <template v-else-if="['editor', 'admin', 'associate_editor', 'editorial_assistant', 'advisory_editor'].includes(user?.role)">
          <div class="hamburger-menu mobile-only" @click="showMobileMenu = true">☰</div>
          <ul class="navbar-menu desktop-only">
          <!-- Core Navigation -->
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'editor-dashboard' }"
              @click.prevent="handleNav('editor-dashboard', '/editor/dashboard')"
            >
              {{ t('nav.dashboard') }}
            </a>
          </li>
          
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'editor-manuscripts' }"
              @click.prevent="handleNav('editor-manuscripts', '/editor/manuscripts')"
            >
              {{ t('nav.manuscripts') }}
            </a>
          </li>

          <!-- Audit Tasks Menu (Top-level) -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleAuditTasksMenu">
              <a href="#" class="nav-link" :class="{ active: currentPage.startsWith('audit-') }">
                {{ t('nav.auditTasks') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showAuditTasksMenu">
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-new-submissions', '/editor/audit/new-submissions'); closeAllMenus()">{{ t('nav.auditNewSubmissions') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-assign-reviewers', '/editor/audit/assign-reviewers'); closeAllMenus()">{{ t('nav.auditAssignReviewers') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-review-monitoring', '/editor/audit/review-monitoring'); closeAllMenus()">{{ t('nav.auditReviewMonitoring') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-decision-making', '/editor/audit/decision-making'); closeAllMenus()">{{ t('nav.auditDecisionMaking') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-revision-handling', '/editor/audit/revision-handling'); closeAllMenus()">{{ t('nav.auditRevisionHandling') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-reviewer-management', '/editor/audit/reviewer-management'); closeAllMenus()">{{ t('nav.auditReviewerManagement') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-recommended-reviewers', '/editor/audit/recommended-reviewers'); closeAllMenus()">{{ t('nav.auditRecommendedReviewers') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-opposed-reviewers', '/editor/audit/opposed-reviewers'); closeAllMenus()">{{ t('nav.auditOpposedReviewers') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('audit-my-tasks', '/editor/audit/my-tasks'); closeAllMenus()">{{ t('nav.auditMyTasks') }}</a></li>
            </ul>
          </li>

          <!-- Review Process Dropdown -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleReviewProcessMenu">
              <a href="#" class="nav-link" :class="{ active: currentPage === 'editor-reviewers' || currentPage === 'editor-decisions' }">
                {{ t('nav.reviewProcess') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showReviewProcessMenu">
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-reviewers', '/editor/reviewers'); closeAllMenus()">{{ t('nav.reviewers') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-decisions', '/editor/decisions'); closeAllMenus()">{{ t('nav.decisionsLetters') }}</a></li>
            </ul>
          </li>

          <!-- Publication & Analytics Dropdown -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="togglePubAnalyticsMenu">
              <a href="#" class="nav-link" :class="{ active: currentPage === 'editor-publication-management' || currentPage === 'editor-statistics' }">
                {{ t('nav.publicationAnalytics') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showPubAnalyticsMenu">
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-publication-management', '/editor/publication'); closeAllMenus()">{{ t('nav.publication') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-statistics', '/editor/statistics'); closeAllMenus()">{{ t('nav.dataStatistics') }}</a></li>
            </ul>
          </li>

          <!-- Board Management (Editor Only) -->
          <li class="nav-item" v-if="['editor', 'admin'].includes(user?.role)">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'editor-board' }"
              @click.prevent="handleNav('editor-board', '/editor/board')"
            >
              {{ t('nav.boardManagement') }}
            </a>
          </li>

          <!-- Admin Only Menu Items -->
          <template v-if="user?.role === 'admin'">
            <li class="nav-item dropdown">
              <div class="dropdown-toggle" @click="toggleAdminToolsMenu">
                <a href="#" class="nav-link" :class="{ active: currentPage === 'editor-users' || currentPage.startsWith('editor-system') }">
                  {{ t('nav.adminTools') }} ▼
                </a>
              </div>
              <ul class="dropdown-menu" v-if="showAdminToolsMenu">
                <!-- Editor Management -->
                <li class="dropdown-submenu">
                  <div class="dropdown-toggle" @click.stop="toggleRoleMenu">
                    <a href="#" class="nav-link">{{ t('nav.editorManagement') }} ▶</a>
                  </div>
                  <ul class="dropdown-menu submenu-level-2" v-if="showRoleMenu">
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-users', '/editor/users'); closeAllMenus()">{{ t('nav.userList') }}</a></li>
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-account-status', '/editor/account-status'); closeAllMenus()">{{ t('nav.accountStatus') }}</a></li>
                  </ul>
                </li>
                <!-- Journal Settings -->
                <li class="dropdown-submenu">
                  <div class="dropdown-toggle" @click.stop="toggleSystemMenu">
                    <a href="#" class="nav-link">{{ t('nav.journalSettings') }} ▶</a>
                  </div>
                  <ul class="dropdown-menu submenu-level-2" v-if="showSystemMenu">
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-system-basic', '/editor/system/basic'); closeAllMenus()">{{ t('nav.basicConfig') }}</a></li>
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-system-notification', '/editor/system/notification'); closeAllMenus()">{{ t('nav.notificationSettings') }}</a></li>
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-system-modules', '/editor/system/modules'); closeAllMenus()">{{ t('nav.moduleManagement') }}</a></li>
                    <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-system-invitation-codes', '/editor/system/invitation-codes'); closeAllMenus()">{{ t('nav.inviteCodeManagement') }}</a></li>
                  </ul>
                </li>
                <!-- Log Management -->
                <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-system-logs', '/editor/system/logs'); closeAllMenus()">{{ t('nav.logManagement') }}</a></li>
              </ul>
            </li>
          </template>

          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleProfileMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'editor-settings' }"
              >
                {{ t('nav.profileSettings') }} ▼
              </a>
            </div>
             <ul class="dropdown-menu" v-if="showProfileMenu">
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=profile'); closeAllMenus()">{{ t('nav.profileInfo') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=security'); closeAllMenus()">{{ t('nav.accountSecurity') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=notifications'); closeAllMenus()">{{ t('nav.notificationSettings') }}</a></li>
              <li v-if="user?.role === 'editor' || user?.role === 'admin'"><a href="#" class="nav-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=preferences'); closeAllMenus()">{{ t('nav.editorPreferences') }}</a></li>
              <li v-if="user?.role === 'editor' || user?.role === 'admin'"><a href="#" class="nav-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=api'); closeAllMenus()">{{ t('nav.apiAccess') }}</a></li>
            </ul>
          </li>

           <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleHelpMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('submission-help') || currentPage.startsWith('submission-system') }"
              >
                {{ t('nav.helpSupport') }} ▼
              </a>
            </div>
             <ul class="dropdown-menu" v-if="showHelpMenu">
              <li><a href="#" class="nav-link" @click.prevent="handleNav('submission-help', '/submission/help'); closeAllMenus()">{{ t('nav.helpCenter') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('submission-help-feedback', '/submission/help/feedback'); closeAllMenus()">{{ t('nav.feedback') }}</a></li>
              <li><a href="#" class="nav-link" @click.prevent="handleNav('submission-system-status', '/submission/system-status'); closeAllMenus()">{{ t('nav.systemStatus') }}</a></li>
            </ul>
          </li>
          </ul>
        </template>
        
        <!-- 投稿人后台导航 -->
        <template v-else-if="user?.role === 'author'">
          <div class="hamburger-menu mobile-only" @click="showMobileMenu = true">☰</div>
          <ul class="navbar-menu desktop-only">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'author-dashboard' || currentPage === 'admin-author-dashboard' || currentPage === 'submission-author-dashboard' }"
              @click.prevent="goToAdminDashboard"
            >
              {{ t('nav.dashboard') }}
            </a>
          </li>
          
          <!-- 稿件管理菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleManuscriptMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-manuscript') || currentPage.startsWith('submission-manuscript') }"
              >
                {{ t('nav.manuscriptManagement') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showManuscriptMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-author-submit' || currentPage === 'submission-author-submit' }"
                  @click.prevent="router.push('/admin/author-submit'); closeAllMenus()"
                >
                  {{ t('nav.newSubmission') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-my' || currentPage === 'submission-manuscript-my' }"
                  @click.prevent="router.push('/admin/manuscript/my'); closeAllMenus()"
                >
                  {{ t('nav.myManuscripts') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-progress' || currentPage === 'submission-manuscript-progress' }"
                  @click.prevent="router.push('/admin/manuscript/progress'); closeAllMenus()"
                >
                  {{ t('nav.manuscriptProgress') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-history' || currentPage === 'submission-manuscript-history' }"
                  @click.prevent="router.push('/admin/manuscript/history'); closeAllMenus()"
                >
                  {{ t('nav.historySubmission') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'author-letters' }"
                  @click.prevent="router.push('/author/letters'); closeAllMenus()"
                >
                  {{ t('nav.letters') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 个人中心菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleProfileMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' || currentPage.startsWith('admin-profile') || currentPage === 'admin-notifications' || currentPage.startsWith('submission-profile') || currentPage === 'submission-notifications' }"
              >
                {{ t('nav.profile') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showProfileMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' || currentPage === 'submission-author-profile' }"
                  @click.prevent="router.push('/admin/author-profile'); closeAllMenus()"
                >
                  {{ t('nav.profileInfo') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-security' || currentPage === 'submission-profile-security' }"
                  @click.prevent="router.push('/account-security'); closeAllMenus()"
                >
                  {{ t('nav.accountSecurity') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-notifications' || currentPage === 'submission-notifications' }"
                  @click.prevent="router.push('/submission/notifications'); closeAllMenus()"
                >
                  {{ t('nav.messages') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 投稿指南菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleGuideMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-guide') || currentPage.startsWith('submission-guide') }"
              >
                {{ t('nav.submissionGuide') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showGuideMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-submission-rules' || currentPage === 'submission-rules' }"
                  @click.prevent="router.push('/submission/submission-rules'); closeAllMenus()"
                >
                  {{ t('nav.submissionRules') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-guide-faq' || currentPage === 'submission-guide-faq' }"
                  @click.prevent="router.push('/admin/guide/faq'); closeAllMenus()"
                >
                  {{ t('nav.faq') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 帮助中心菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleAuthorHelpMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-help') || currentPage.startsWith('submission-help') || currentPage.startsWith('submission-system') }"
              >
                {{ t('nav.helpCenter') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showAuthorHelpMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'submission-help' }"
                  @click.prevent="router.push('/submission/help'); closeAllMenus()"
                >
                  {{ t('nav.helpCenter') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-help-consultation' || currentPage === 'submission-help-consultation' }"
                  @click.prevent="router.push('/admin/help/consultation'); closeAllMenus()"
                >
                  {{ t('nav.onlineConsultation') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-help-feedback' || currentPage === 'submission-help-feedback' }"
                  @click.prevent="router.push('/admin/help/feedback'); closeAllMenus()"
                >
                  {{ t('nav.feedback') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'submission-system-status' }"
                  @click.prevent="router.push('/submission/system-status'); closeAllMenus()"
                >
                  {{ t('nav.systemStatus') }}
                </a>
              </li>
            </ul>
          </li>
          
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              @click.prevent="goToHome"
            >
              {{ t('nav.returnMain') }}
            </a>
          </li>
           <!-- Logout -->
           <li class="nav-item">
            <a href="#" class="nav-link logout" @click.prevent="handleLogout" :title="t('nav.logoutSubmit')">
              {{ t('nav.logoutSubmit') }}
            </a>
          </li>
          <!-- Language -->
          <li class="nav-item">
             <a href="#" class="nav-link" @click.prevent="toggleLang">
               {{ currentLang === 'en' ? '中文' : 'En' }}
             </a>
           </li>
           </ul>
        </template>
        

      </div>
    </div>
  </nav>

  <!-- Unified Mobile Sidebar -->
  <div class="mobile-sidebar-overlay" v-if="showMobileMenu" @click="showMobileMenu = false">
    <div class="mobile-sidebar" @click.stop>
      <div class="sidebar-header">
        <span class="close-btn" @click="showMobileMenu = false">×</span>
      </div>
      <ul class="sidebar-menu">
        
        <!-- 1. Main Site / Reviewer Navigation -->
        <template v-if="!isAdminRoute() || user?.role === 'reviewer'">
          <li class="sidebar-item">
            <a href="#" class="sidebar-link" @click.prevent="goToHome; showMobileMenu = false">{{ t('nav.home') }}</a>
          </li>
          <li class="sidebar-item">
            <a href="#" class="sidebar-link" @click.prevent="$router.push('/journals/all'); showMobileMenu = false">{{ t('nav.journals') }}</a>
          </li>
          <li class="sidebar-item">
            <a href="#" class="sidebar-link btn-submit-sidebar" @click.prevent="goToSubmit(); showMobileMenu = false">{{ t('nav.submit') }}</a>
          </li>
          <!-- Resources -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleResourcesMenu">{{ t('nav.resources') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showResourcesMenu">
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/author/guide'); showMobileMenu = false">{{ t('nav.guideForAuthors') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/author/templates'); showMobileMenu = false">{{ t('nav.templates') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/author/status'); showMobileMenu = false">{{ t('nav.checkStatus') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/reviewer/become'); showMobileMenu = false">{{ t('nav.becomeReviewer') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/reviewer/guidelines'); showMobileMenu = false">{{ t('nav.reviewerGuidelines') }}</a></li>
            </ul>
          </li>
          <!-- Reviewer -->
          <li class="sidebar-item has-submenu" v-if="user && (user.role === 'reviewer' || applicationStatus)">
            <div class="sidebar-link" @click="toggleReviewerMenu">{{ t('nav.reviewer') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showReviewerMenu">
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/reviewer/become'); showMobileMenu = false">{{ t('nav.becomeReviewer') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/reviewer/guidelines'); showMobileMenu = false">{{ t('nav.reviewerGuidelines') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/resources/reviewer/training'); showMobileMenu = false">{{ t('nav.reviewerTraining') }}</a></li>
              <template v-if="user.role === 'reviewer'">
                 <li><a href="#" class="submenu-link" :class="{ 'disabled': user?.status !== 'active' }" @click.prevent="handleMyReviewsClick; if(user?.status==='active') showMobileMenu = false">{{ t('nav.myReviews') }}</a></li>
                 <li><a href="#" class="submenu-link" @click.prevent="$router.push('/reviewer/profile'); showMobileMenu = false">{{ t('nav.myProfile') }}</a></li>
              </template>
            </ul>
          </li>
          <!-- More -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleMoreMenu">{{ t('nav.more') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showMoreMenu">
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/about/editorial-board'); showMobileMenu = false">{{ t('nav.editorialBoard') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/about/journal-info'); showMobileMenu = false">{{ t('nav.journalInfo') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="$router.push('/about/history'); showMobileMenu = false">{{ t('nav.history') }}</a></li>
            </ul>
          </li>
          <!-- Login/Logout -->
          <li class="sidebar-item" v-if="!user">
            <a href="#" class="sidebar-link" @click.prevent="goToLogin(); showMobileMenu = false">{{ t('nav.login') }} (Read-Only)</a>
          </li>
          <li class="sidebar-item" v-else>
            <a href="#" class="sidebar-link logout" @click.prevent="handleLogout">{{ t('nav.logout') }} (Read-Only)</a>
          </li>
        </template>

        <!-- 2. Editor / Admin Navigation -->
        <template v-else-if="['editor', 'admin', 'associate_editor', 'editorial_assistant', 'advisory_editor'].includes(user?.role)">
          <li class="sidebar-item">
             <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-dashboard', '/editor/dashboard'); showMobileMenu = false">{{ t('nav.dashboard') }}</a>
          </li>
          <li class="sidebar-item">
             <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-manuscripts', '/editor/manuscripts'); showMobileMenu = false">{{ t('nav.manuscripts') }}</a>
          </li>
          <!-- Audit Tasks -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleAuditTasksMenu">Audit Tasks <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showAuditTasksMenu">
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-new-submissions', '/editor/audit/new-submissions'); showMobileMenu = false">{{ t('nav.auditNewSubmissions') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-assign-reviewers', '/editor/audit/assign-reviewers'); showMobileMenu = false">{{ t('nav.auditAssignReviewers') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-review-monitoring', '/editor/audit/review-monitoring'); showMobileMenu = false">{{ t('nav.auditReviewMonitoring') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-decision-making', '/editor/audit/decision-making'); showMobileMenu = false">{{ t('nav.auditDecisionMaking') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-revision-handling', '/editor/audit/revision-handling'); showMobileMenu = false">{{ t('nav.auditRevisionHandling') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-reviewer-management', '/editor/audit/reviewer-management'); showMobileMenu = false">{{ t('nav.auditReviewerManagement') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-recommended-reviewers', '/editor/audit/recommended-reviewers'); showMobileMenu = false">{{ t('nav.auditRecommendedReviewers') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-opposed-reviewers', '/editor/audit/opposed-reviewers'); showMobileMenu = false">{{ t('nav.auditOpposedReviewers') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('audit-my-tasks', '/editor/audit/my-tasks'); showMobileMenu = false">{{ t('nav.auditMyTasks') }}</a></li>
            </ul>
          </li>
           <li class="sidebar-item">
             <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-reviewers', '/editor/reviewers'); showMobileMenu = false">{{ t('nav.reviewers') }}</a>
          </li>
           <li class="sidebar-item">
             <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-decisions', '/editor/decisions'); showMobileMenu = false">{{ t('nav.decisionsLetters') }}</a>
          </li>
          
           <!-- Board Management (Sidebar) -->
           <li class="sidebar-item" v-if="['editor', 'admin'].includes(user?.role)">
             <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-board', '/editor/board'); showMobileMenu = false">Board Management</a>
          </li>
          
          <!-- Admin Only -->
          <template v-if="user?.role === 'admin'">
             <li class="sidebar-item has-submenu">
                <div class="sidebar-link" @click="toggleRoleMenu">{{ t('nav.editorManagement') }} <span class="arrow">▼</span></div>
                <ul class="sidebar-submenu" v-if="showRoleMenu">
                   <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-users', '/editor/users'); showMobileMenu = false">{{ t('nav.userList') }}</a></li>
                   <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-account-status', '/editor/account-status'); showMobileMenu = false">{{ t('nav.accountStatus') }}</a></li>
                </ul>
             </li>
             <li class="sidebar-item has-submenu">
                <div class="sidebar-link" @click="toggleSystemMenu">{{ t('nav.journalSettings') }} <span class="arrow">▼</span></div>
                <ul class="sidebar-submenu" v-if="showSystemMenu">
                  <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-system-basic', '/editor/system/basic'); showMobileMenu = false">{{ t('nav.basicConfig') }}</a></li>
                  <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-system-notification', '/editor/system/notification'); showMobileMenu = false">{{ t('nav.notificationSettings') }}</a></li>
                  <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-system-modules', '/editor/system/modules'); showMobileMenu = false">{{ t('nav.moduleManagement') }}</a></li>
                  <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-system-invitation-codes', '/editor/system/invitation-codes'); showMobileMenu = false">{{ t('nav.inviteCodeManagement') }}</a></li>
                </ul>
             </li>
              <li class="sidebar-item">
                 <a href="#" class="sidebar-link" @click.prevent="handleNav('editor-system-logs', '/editor/system/logs'); showMobileMenu = false">{{ t('nav.statistics') }}</a>
              </li>
          </template>

          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleProfileMenu">{{ t('nav.profileSettings') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showProfileMenu">
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=profile'); showMobileMenu = false">{{ t('nav.profileInfo') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=security'); showMobileMenu = false">{{ t('nav.accountSecurity') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('editor-settings', '/editor/settings?tab=notifications'); showMobileMenu = false">{{ t('nav.notificationSettings') }}</a></li>
            </ul>
          </li>
          
           <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleHelpMenu">{{ t('nav.helpSupport') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showHelpMenu">
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('submission-help', '/submission/help'); showMobileMenu = false">{{ t('nav.helpCenter') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('submission-help-feedback', '/submission/help/feedback'); showMobileMenu = false">{{ t('nav.feedback') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="handleNav('submission-system-status', '/submission/system-status'); showMobileMenu = false">{{ t('nav.systemStatus') }}</a></li>
            </ul>
          </li>
          
          <li class="sidebar-item">
            <a href="#" class="sidebar-link logout" @click.prevent="handleLogout" title="Logout from submit system (Reviewer access)">Logout (Submit System)</a>
          </li>
        </template>

        <!-- 3. Author Navigation -->
        <template v-else-if="user?.role === 'author'">
          <li class="sidebar-item">
            <a href="#" class="sidebar-link" @click.prevent="goToAdminDashboard; showMobileMenu = false">{{ t('nav.dashboard') }}</a>
          </li>
          <!-- Manuscripts -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleManuscriptMenu">{{ t('nav.manuscriptManagement') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showManuscriptMenu">
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/author-submit'); showMobileMenu = false">{{ t('nav.newSubmission') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/manuscript/my'); showMobileMenu = false">{{ t('nav.myManuscripts') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/manuscript/progress'); showMobileMenu = false">{{ t('nav.manuscriptProgress') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/manuscript/history'); showMobileMenu = false">{{ t('nav.historySubmission') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/author/letters'); showMobileMenu = false">{{ t('nav.letters') }}</a></li>
            </ul>
          </li>
           <!-- Profile -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleProfileMenu">{{ t('nav.profile') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showProfileMenu">
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/author-profile'); showMobileMenu = false">{{ t('nav.profileInfo') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/account-security'); showMobileMenu = false">{{ t('nav.accountSecurity') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/submission/notifications'); showMobileMenu = false">{{ t('nav.messages') }}</a></li>
            </ul>
          </li>
           <!-- Guide -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleGuideMenu">{{ t('nav.submissionGuide') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showGuideMenu">
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/submission/submission-rules'); showMobileMenu = false">{{ t('nav.submissionRules') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/guide/faq'); showMobileMenu = false">{{ t('nav.faq') }}</a></li>
            </ul>
          </li>
          <!-- Help -->
          <li class="sidebar-item has-submenu">
            <div class="sidebar-link" @click="toggleAuthorHelpMenu">{{ t('nav.helpCenter') }} <span class="arrow">▼</span></div>
            <ul class="sidebar-submenu" v-if="showAuthorHelpMenu">
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/submission/help'); showMobileMenu = false">{{ t('nav.helpCenter') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/help/consultation'); showMobileMenu = false">{{ t('nav.onlineConsultation') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/admin/help/feedback'); showMobileMenu = false">{{ t('nav.feedback') }}</a></li>
              <li><a href="#" class="submenu-link" @click.prevent="router.push('/submission/system-status'); showMobileMenu = false">{{ t('nav.systemStatus') }}</a></li>
            </ul>
          </li>
          
           <li class="sidebar-item">
            <a href="#" class="sidebar-link" @click.prevent="goToHome; showMobileMenu = false">{{ t('nav.returnMain') }}</a>
          </li>
          <li class="sidebar-item">
            <a href="#" class="sidebar-link logout" @click.prevent="handleLogout" title="Logout from submit system">Logout (Submit System)</a>
          </li>
        </template>

      </ul>
    </div>
  </div>

  <!-- Subscribe Modal -->
  <div v-if="showSubscribeModal" class="modal-overlay" @click="showSubscribeModal = false">
    <div class="modal-content" @click.stop>
      <h3>{{ t('nav.subscribe') }}</h3>
      <p>Stay updated with the latest research and journal news.</p>
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" placeholder="Enter your email" class="modal-input" />
      </div>
      <div class="form-group">
        <label>Interests</label>
        <div class="checkbox-group">
          <label><input type="checkbox"> Highly Cited Papers</label>
          <label><input type="checkbox"> Event Notifications</label>
          <label><input type="checkbox"> Newsletters</label>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="showSubscribeModal = false">{{ t('common.cancel') }}</button>
        <button class="btn-confirm" @click="handleSubscribe">{{ t('nav.subscribe') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* System Banners */
.system-banner {
  width: 100%;
  text-align: center;
  font-size: 0.85rem;
  padding: 4px 0;
  font-weight: 500;
  position: fixed;
  top: 0;
  z-index: 1001;
}

.system-banner.read-only {
  background-color: #f0f0f0;
  color: #666;
  border-bottom: 1px solid #ddd;
}

.system-banner.submit-mode {
  background-color: #0056B3;
  color: white;
}

/* Navbar adjustments for banner */
.navbar.has-banner {
  top: 28px; /* Height of banner approx */
}

/* 导航栏样式 - 固定在顶部 */
.navbar {
  background: white;
  color: #333;
  border-bottom: 1px solid #eee;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  outline: none;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
}

/* 双层导航栏 - 第一行 */
.navbar-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.navbar-top-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.user-info .user-name {
  color: #666;
  font-weight: 500;
}

.user-info .logout-link {
  color: #dc3545;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}

.user-info .logout-link:hover {
  text-decoration: underline;
}

.user-info .divider {
  color: #ccc;
}

/* 双层导航栏 - 第二行 */
.nav-wrapper {
  width: 100%;
  padding: 0.5rem 0;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
  justify-content: flex-start;
  gap: 0.5rem;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.navbar-logo h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.logo-logout-area {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #666;
  margin-left: 5px;
}

.logo-logout-area .user-name {
  color: #666;
  font-weight: 500;
}

.logo-logout-area .logout-link {
  color: #dc3545;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}

.logo-logout-area .logout-link:hover {
  text-decoration: underline;
}

.logo-logout-area .divider {
  color: #ccc;
}


/* Clear Submit Button */
.btn-clear-submit {
  margin-left: 15px;
  padding: 4px 10px;
  font-size: 12px;
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-clear-submit:hover {
  background-color: #e0e0e0;
  color: #000;
}

.nav-item {
  margin-left: 0.5rem;
  flex-shrink: 0;
}

.nav-link {
  color: #333;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  display: inline-block;
  border-radius: 5px;
  transition: all 0.3s ease;
  min-width: 70px;
  text-align: center;
}

/* Navigation Item Highlight Style */
.nav-link.active {
  color: #0056B3;
  background: transparent;
  border-bottom: 2px solid #0056B3;
  border-radius: 0;
}

.nav-link:hover {
  color: #333;
  background: #f5f5f5;
}

/* Ensure no shadows on hover */
.nav-link:hover, .nav-link.active {
  box-shadow: none;
}

.nav-link.icon-link {
  position: relative;
  padding: 0.5rem;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-link.logout {
  color: #dc3545;
}

.nav-link.logout:hover {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

/* 下拉菜单样式 */
.nav-item.dropdown {
  position: relative;
}

.dropdown-toggle {
  cursor: pointer;
}

/* Updated Dropdown Menu for Content Fit */
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border-radius: 5px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  z-index: 1001;
  min-width: max-content; /* Fit content */
  margin-top: 0.1rem;
  list-style: none;
  padding: 0.5rem 0;
}

.dropdown-menu li {
  margin: 0;
}

.dropdown-menu .dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 0.5rem 0;
  padding: 0;
}

.dropdown-menu .nav-link {
  display: block;
  padding: 0.5rem 1.5rem;
  color: #333;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-align: left;
  min-width: auto;
  white-space: nowrap; /* Prevent wrapping */
}

.dropdown-menu .nav-link:hover,
.dropdown-menu .nav-link.active {
  background: rgba(0, 86, 179, 0.1);
  color: #0056B3;
}

/* Hamburger Menu Global */
.hamburger-menu {
  display: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar-container {
    flex-direction: row; /* Change to row to align Logo and Hamburger */
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-menu.desktop-only {
    display: none; /* Hide desktop menu */
  }

  .hamburger-menu.mobile-only {
    display: block; /* Show hamburger */
    font-size: 24px;
    cursor: pointer;
  }

  /* Hide old mobile menu styles if any remain active */
  .nav-item {
    margin-left: 0;
  }
  
  .navbar-logo h1 {
    font-size: 1.3rem;
  }
}

/* New Styles for Main Site Navigation */
.nav-spacer {
  flex-grow: 1;
}

.btn-submit-nav {
  color: white !important;
  background: #C93737 !important;
  font-weight: normal;
  border-radius: 4px;
}
.btn-submit-nav:hover {
  color: white !important;
  background: #C93737 !important;
  opacity: 0.9;
  transform: none;
}

/* Updated Search Styles (Icon + Hover Expand) */
.search-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 40px; /* Match nav height */
}

.search-icon {
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 10px;
  color: #333;
  transition: color 0.3s;
}

.search-icon:hover {
  color: #e74c3c;
}

.search-input-wrapper {
  width: 0;
  overflow: hidden;
  transition: width 0.4s ease;
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  border: 1px solid #eee;
}

.search-container:hover .search-input-wrapper,
.search-input-wrapper:focus-within {
  width: 250px;
  padding: 0 5px;
}

.search-input-wrapper input {
  border: none;
  outline: none;
  padding: 8px 10px;
  width: 100%;
  font-size: 0.9rem;
  color: #333;
}

/* Simplified Login Button */
.login-btn {
  color: #666 !important; /* Grey text */
  font-weight: 500;
}
.login-btn:hover {
  color: #e74c3c !important; /* Brand color on hover */
  background: transparent !important;
}

/* Dropdown Header Style */
.dropdown-header {
  padding: 0.5rem 1.5rem;
  font-size: 0.8rem;
  font-weight: bold;
  color: #95a5a6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  pointer-events: none;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  color: #333;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.modal-content h3 {
  margin-top: 0;
  color: #2c3e50;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.modal-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.checkbox-group label {
  font-weight: normal;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn-cancel {
  background: #f1f1f1;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
}
.btn-confirm {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-confirm:hover {
  background: #2980b9;
}

.btn-danger {
  background: #C93737;
}

.btn-danger:hover {
  background: #B02E2E;
}

/* Reviewer Dropdown Specific */
.reviewer-menu {
  top: 100%;
  margin-top: 0.1rem;
  border: 1px solid #E5E5E5;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  min-width: 200px;
  padding: 8px 0;
}

.reviewer-menu .nav-link {
  font-size: 14px;
  color: #333333; /* Dark Grey */
  padding: 8px 16px;
  height: auto;
  display: block;
  text-align: left;
  border: none;
}

.reviewer-menu .nav-link:hover {
  background-color: #F5F5F5; /* Light Grey Hover */
  color: #333333;
}

.disabled-link {
  color: #999999 !important; /* Light Grey #999 */
  cursor: not-allowed;
  pointer-events: none; /* Unclickable */
  background-color: transparent !important;
}

/* User Icon */
.user-container {
  position: relative;
  cursor: pointer;
  height: 40px;
  display: flex;
  align-items: center;
}

.user-icon {
  font-size: 16px;
  color: #333333;
  transition: color 0.3s;
}

.user-container:hover .user-icon {
  color: #0056B3;
}

.user-menu {
  right: 0;
  left: auto;
  width: 150px; /* Fixed width */
  border: 1px solid #E5E5E5;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  top: 100%;
  margin-top: 10px; /* Spacing */
}

/* Mobile Adaptation for Reviewer */
@media (max-width: 1024px) {
  /* Add Hamburger Menu Logic here */
  .hamburger-menu {
    display: block; /* Visible on mobile */
    font-size: 16px;
    color: #333333;
    cursor: pointer;
    padding: 10px;
  }
  .hamburger-menu:hover {
    color: #C93737;
  }
}

/* Sidebar Styles */
.mobile-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  justify-content: flex-start;
}

.mobile-sidebar {
  width: 250px;
  background: white;
  height: 100%;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  padding: 20px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

.sidebar-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #333;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-item {
  margin-bottom: 15px;
}

.sidebar-link {
  font-size: 14px;
  color: #333;
  text-decoration: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  cursor: pointer;
}

.sidebar-link:hover {
  color: #0056B3;
}

.btn-submit-sidebar {
  background-color: #C93737;
  color: white !important;
  text-align: center;
  border-radius: 4px;
  padding: 8px 16px;
  display: block;
}

.sidebar-submenu {
  list-style: none;
  padding-left: 15px;
  margin-top: 5px;
  border-left: 1px solid #eee;
}

.submenu-link {
  font-size: 12px;
  color: #666;
  text-decoration: none;
  display: block;
  padding: 5px 0;
}

.submenu-link:hover {
  color: #0056B3;
}

.submenu-link.disabled {
  color: #999;
  cursor: not-allowed;
}

/* Dropdown Submenu Styles */
.dropdown-submenu {
  position: relative;
}

.dropdown-submenu .dropdown-menu.submenu-level-2 {
  position: absolute;
  left: 100%;
  top: 0;
  margin-top: -1px;
  min-width: 200px;
  display: block;
}

.dropdown-submenu:hover .dropdown-menu.submenu-level-2 {
  display: block;
}

/* Hamburger default hidden on PC */
.hamburger-menu {
  display: none;
}

@media (max-width: 1024px) {
  .hamburger-menu {
    display: block;
  }
  
  /* Mobile Icon Updates */
  .reviewer-nav-layout .icon-nav-section {
    gap: 20px;
  }
  .reviewer-nav-layout .search-icon,
  .user-icon {
    font-size: 18px;
  }
}

/* Strict Reviewer Navbar Overrides */
.navbar.reviewer-navbar {
  padding: 0;
  height: 60px;
  background: white;
  border-bottom: 1px solid #eee; /* Ensure border is present */
}

.navbar-container.reviewer-container {
  padding: 0 16px;
  height: 100%;
  display: flex;
  flex-direction: row; /* Override column */
  align-items: center;
  gap: 0;
  max-width: 100%; /* Layout handles 1200px min-width */
}
</style>