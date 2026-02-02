<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'

const router = useRouter()
const { t, currentLang, setLang } = useI18n()

const props = defineProps({
  user: Object,
  currentPage: String,
  toggleDirectory: Function,
  logout: Function
})

const toggleLang = () => {
  setLang(currentLang.value === 'en' ? 'zh' : 'en')
}

// 控制角色管理子菜单的显示状态
const showRoleMenu = ref(false)

// 控制系统设置子菜单的显示状态
const showSystemMenu = ref(false)

// 控制个人中心子菜单的显示状态
const showProfileMenu = ref(false)

// 控制投稿中心子菜单的显示状态
const showSubmissionMenu = ref(false)

// 控制帮助中心子菜单的显示状态
const showHelpMenu = ref(false)

// 控制稿件管理子菜单的显示状态
const showManuscriptMenu = ref(false)

// 控制投稿指南子菜单的显示状态
const showGuideMenu = ref(false)

// 控制作者帮助中心子菜单的显示状态
const showAuthorHelpMenu = ref(false)

// 控制角色切换菜单的显示状态
const showRoleSwitchMenu = ref(false)

// 角色切换相关
const rolePriority = {
  admin: 3,
  reviewer: 2,
  author: 1
}

// 获取当前用户可以切换到的角色列表
const availableRoles = computed(() => {
  if (!props.user) return []
  
  // 获取用户的原始角色，用于确定可切换的角色范围
  // 这里假设用户的原始角色是其最高权限角色
  let originalRole = props.user.originalRole || props.user.role
  
  // 确定用户的最高权限优先级
  let maxPriority = 0
  
  switch (originalRole) {
    case 'admin':
      maxPriority = rolePriority.admin
      break
    case 'reviewer':
      maxPriority = rolePriority.reviewer
      break
    case 'author':
      maxPriority = rolePriority.author
      break
  }
  
  // 高权限角色可以切换到低权限角色
  const roles = []
  if (maxPriority >= rolePriority.admin) {
    roles.push({ value: 'admin', label: t('nav.roles.admin') })
  }
  if (maxPriority >= rolePriority.reviewer) {
    roles.push({ value: 'reviewer', label: t('nav.roles.reviewer') })
  }
  if (maxPriority >= rolePriority.author) {
    roles.push({ value: 'author', label: t('nav.roles.author') })
  }
  
  return roles
})

// 切换角色
const switchRole = (role) => {
  if (!props.user) return
  
  // 导入 userStore
  import('../stores/user').then(({ useUserStore }) => {
    const userStore = useUserStore()
    
    // 保存用户的原始角色（仅在首次切换时保存）
    const updatedUser = {
      ...props.user,
      role
    }
    
    // 如果用户没有原始角色，保存当前角色作为原始角色
    if (!updatedUser.originalRole) {
      updatedUser.originalRole = props.user.role
    }
    
    // 更新用户角色
    userStore.updateUser(updatedUser)
    
    // 根据选择的角色跳转到对应后台主页
    switch (role) {
      case 'admin':
        router.push('/admin/dashboard')
        break
      case 'reviewer':
        router.push('/admin/audit-dashboard')
        break
      case 'author':
        router.push('/admin/author-dashboard')
        break
    }
    closeAllMenus()
  })
}

// 切换角色切换菜单
const toggleRoleSwitchMenu = (event) => {
  event.stopPropagation()
  showRoleSwitchMenu.value = !showRoleSwitchMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换角色管理子菜单
const toggleRoleMenu = (event) => {
  event.stopPropagation()
  showRoleMenu.value = !showRoleMenu.value
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换系统设置子菜单
const toggleSystemMenu = (event) => {
  event.stopPropagation()
  showSystemMenu.value = !showSystemMenu.value
  showRoleMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换个人中心子菜单
const toggleProfileMenu = (event) => {
  event.stopPropagation()
  showProfileMenu.value = !showProfileMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换投稿中心子菜单
const toggleSubmissionMenu = (event) => {
  event.stopPropagation()
  showSubmissionMenu.value = !showSubmissionMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换帮助中心子菜单
const toggleHelpMenu = (event) => {
  event.stopPropagation()
  showHelpMenu.value = !showHelpMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换稿件管理子菜单
const toggleManuscriptMenu = (event) => {
  event.stopPropagation()
  showManuscriptMenu.value = !showManuscriptMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换投稿指南子菜单
const toggleGuideMenu = (event) => {
  event.stopPropagation()
  showGuideMenu.value = !showGuideMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showAuthorHelpMenu.value = false
}

// 切换作者帮助中心子菜单
const toggleAuthorHelpMenu = (event) => {
  event.stopPropagation()
  showAuthorHelpMenu.value = !showAuthorHelpMenu.value
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
}

// 关闭所有子菜单
const closeAllMenus = () => {
  showRoleMenu.value = false
  showSystemMenu.value = false
  showProfileMenu.value = false
  showSubmissionMenu.value = false
  showHelpMenu.value = false
  showManuscriptMenu.value = false
  showGuideMenu.value = false
  showAuthorHelpMenu.value = false
  showRoleSwitchMenu.value = false
}

// 点击页面其他部分关闭子菜单
const handleClickOutside = () => {
  closeAllMenus()
}

// 监听点击事件
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 检查当前是否在后台
const isAdminRoute = () => {
  return window.location.pathname.startsWith('/admin')
}

const goToSubmit = () => {
  router.push('/submit')
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
  if (props.user?.role === 'admin') {
    router.push('/admin/dashboard')
  } else if (props.user?.role === 'reviewer') {
    router.push('/admin/audit-dashboard')
  } else if (props.user?.role === 'author') {
    router.push('/admin/author-dashboard')
  }
}

// 处理登录后台点击事件
const handleAdminLogin = () => {
  if (props.user) {
    // 已登录用户，检查角色权限
    if (props.user.role === 'admin' || props.user.role === 'reviewer' || props.user.role === 'author') {
      // 有权限，跳转到后台登录页
      router.push('/admin/login')
    } else {
      // 普通用户，显示权限不足提示
      alert(t('nav.permissionDenied'))
    }
  } else {
    // 未登录用户，跳转到后台登录页
    router.push('/admin/login')
  }
}

const goToAuditList = () => {
  router.push('/admin/audit-list')
}

const goToAuditHistory = () => {
  router.push('/admin/audit-history')
}

const handleLogout = () => {
  props.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo">
        <h1>{{ t('nav.logo') }}</h1>
      </div>
      <ul class="navbar-menu">
        <!-- 主站导航 -->
        <template v-if="!isAdminRoute()">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link" 
              :class="{ active: currentPage === 'home' }"
              @click.prevent="goToHome"
            >
              {{ t('nav.home') }}
            </a>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              @click.prevent="$router.push('/directory')"
            >
              {{ t('nav.directory') }}
            </a>
          </li>
          <!-- 普通用户、作者和管理员都可以投稿 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleSubmissionMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'submit' }"
              >
                {{ t('nav.submissionCenter') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showSubmissionMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'submission-rules' }"
                  @click.prevent="router.push('/submission-rules'); closeAllMenus()"
                >
                  {{ t('nav.submissionRules') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'submit' }"
                  @click.prevent="goToSubmit(); closeAllMenus()"
                >
                  {{ t('nav.onlineSubmission') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 个人中心入口 - 仅对已登录用户显示 -->
          <li v-if="user" class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleProfileMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'profile' }"
              >
                {{ t('nav.profile') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showProfileMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'profile' }"
                  @click.prevent="router.push('/profile'); closeAllMenus()"
                >
                  {{ t('nav.profileInfo') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'account-security' }"
                  @click.prevent="router.push('/account-security'); closeAllMenus()"
                >
                  {{ t('nav.accountSecurity') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 帮助中心 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleHelpMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'help' }"
              >
                {{ t('nav.helpCenter') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showHelpMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'faq' }"
                  @click.prevent="router.push('/faq'); closeAllMenus()"
                >
                  {{ t('nav.faq') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'contact' }"
                  @click.prevent="router.push('/contact'); closeAllMenus()"
                >
                  {{ t('nav.contact') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'feedback' }"
                  @click.prevent="router.push('/feedback'); closeAllMenus()"
                >
                  {{ t('nav.feedback') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 后台主页入口 -->
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              @click.prevent="handleAdminLogin"
            >
              {{ t('nav.adminLogin') }}
            </a>
          </li>
        </template>
        
        <!-- 审核员后台导航 -->
        <template v-else-if="user?.role === 'reviewer'">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'reviewer-dashboard' || currentPage === 'admin-audit-dashboard' }"
              @click.prevent="goToAdminDashboard"
            >
              {{ t('nav.dashboard') }}
            </a>
          </li>
          <!-- 角色切换菜单 -->
          <li v-if="availableRoles.length > 1" class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleRoleSwitchMenu">
              <a href="#" class="nav-link">
                {{ t('nav.roleSwitch') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showRoleSwitchMenu">
              <li v-for="role in availableRoles" :key="role.value">
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: user.role === role.value }"
                  @click.prevent="switchRole(role.value)"
                >
                  {{ role.label }}
                </a>
              </li>
            </ul>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'reviewer-pending' || currentPage === 'admin-audit-list' }"
              @click.prevent="goToAuditList"
            >
              {{ t('nav.tasks') }}
            </a>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'reviewer-history' || currentPage === 'admin-audit-history' }"
              @click.prevent="goToAuditHistory"
            >
              {{ t('nav.history') }}
            </a>
          </li>
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleProfileMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' || currentPage.startsWith('admin-profile') }"
              >
                {{ t('nav.profile') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showProfileMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' }"
                  @click.prevent="router.push('/admin/author-profile'); closeAllMenus()"
                >
                  {{ t('nav.profileInfo') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-security' }"
                  @click.prevent="router.push('/admin/profile-security'); closeAllMenus()"
                >
                  {{ t('nav.accountSecurity') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-notifications' }"
                  @click.prevent="router.push('/admin/notifications'); closeAllMenus()"
                >
                  {{ t('nav.messages') }}
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
        </template>
        
        <!-- 管理员后台导航 -->
        <template v-else-if="user?.role === 'admin'">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'admin-dashboard' }"
              @click.prevent="goToAdminDashboard"
            >
              {{ t('nav.dashboard') }}
            </a>
          </li>
          <!-- 角色切换菜单 -->
          <li v-if="availableRoles.length > 1" class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleRoleSwitchMenu">
              <a href="#" class="nav-link">
                {{ t('nav.roleSwitch') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showRoleSwitchMenu">
              <li v-for="role in availableRoles" :key="role.value">
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: user.role === role.value }"
                  @click.prevent="switchRole(role.value)"
                >
                  {{ role.label }}
                </a>
              </li>
            </ul>
          </li>
          <!-- 审核功能菜单 -->
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'reviewer-pending' || currentPage === 'admin-audit-list' }"
              @click.prevent="goToAuditList"
            >
              {{ t('nav.tasks') }}
            </a>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'reviewer-history' || currentPage === 'admin-audit-history' }"
              @click.prevent="goToAuditHistory"
            >
              {{ t('nav.history') }}
            </a>
          </li>
          <!-- 角色管理菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleRoleMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-users') }"
              >
                {{ t('nav.roleManagement') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showRoleMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-users' }"
                  @click.prevent="router.push('/admin/users'); closeAllMenus()"
                >
                  {{ t('nav.userList') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-reviewer-management' }"
                  @click.prevent="router.push('/admin/reviewer-management'); closeAllMenus()"
                >
                  {{ t('nav.reviewerManagement') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-account-status' }"
                  @click.prevent="router.push('/admin/account-status'); closeAllMenus()"
                >
                  {{ t('nav.accountStatus') }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 系统设置菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleSystemMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-system') }"
              >
                {{ t('nav.systemSettings') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showSystemMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-system-basic' }"
                  @click.prevent="router.push('/admin/system/basic'); closeAllMenus()"
                >
                  {{ t('nav.basicConfig') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-system-notification' }"
                  @click.prevent="router.push('/admin/system/notification'); closeAllMenus()"
                >
                  {{ t('nav.notificationSettings') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-system-logs' }"
                  @click.prevent="router.push('/admin/system/logs'); closeAllMenus()"
                >
                  {{ t('nav.logManagement') }}
                </a>
              </li>
              <li class="dropdown-divider"></li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-system-modules' || currentPage === 'admin-modules' }"
                  @click.prevent="router.push('/admin/system/modules'); closeAllMenus()"
                >
                  {{ t('nav.moduleManagement') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-system-invitation-codes' }"
                  @click.prevent="router.push('/admin/system/invitation-codes'); closeAllMenus()"
                >
                  {{ t('nav.inviteCodeManagement') }}
                </a>
              </li>
            </ul>
          </li>
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleProfileMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' || currentPage.startsWith('admin-profile') }"
              >
                {{ t('nav.profile') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showProfileMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' }"
                  @click.prevent="router.push('/admin/author-profile'); closeAllMenus()"
                >
                  {{ t('nav.profileInfo') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-security' }"
                  @click.prevent="router.push('/admin/profile-security'); closeAllMenus()"
                >
                  {{ t('nav.accountSecurity') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-notifications' }"
                  @click.prevent="router.push('/admin/notifications'); closeAllMenus()"
                >
                  {{ t('nav.messages') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-logs' }"
                  @click.prevent="router.push('/admin/profile-logs'); closeAllMenus()"
                >
                  {{ t('nav.operationLogs') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-manuscript-status' }"
                  @click.prevent="router.push('/admin/profile-manuscript-status'); closeAllMenus()"
                >
                  {{ t('nav.manuscriptStatus') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-feedback-management' }"
                  @click.prevent="router.push('/admin/feedback-management'); closeAllMenus()"
                >
                  {{ t('nav.feedbackManagement') }}
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
        </template>
        
        <!-- 作者后台导航 -->
        <template v-else-if="user?.role === 'author'">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              :class="{ active: currentPage === 'author-dashboard' || currentPage === 'admin-author-dashboard' }"
              @click.prevent="goToAdminDashboard"
            >
              {{ t('nav.dashboard') }}
            </a>
          </li>
          <!-- 角色切换菜单 -->
          <li v-if="availableRoles.length > 1" class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleRoleSwitchMenu">
              <a href="#" class="nav-link">
                {{ t('nav.roleSwitch') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showRoleSwitchMenu">
              <li v-for="role in availableRoles" :key="role.value">
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: user.role === role.value }"
                  @click.prevent="switchRole(role.value)"
                >
                  {{ role.label }}
                </a>
              </li>
            </ul>
          </li>
          
          <!-- 稿件管理菜单 -->
          <li class="nav-item dropdown">
            <div class="dropdown-toggle" @click="toggleManuscriptMenu">
              <a 
                href="#" 
                class="nav-link"
                :class="{ active: currentPage.startsWith('admin-manuscript') }"
              >
                {{ t('nav.manuscriptManagement') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showManuscriptMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-author-submit' }"
                  @click.prevent="router.push('/admin/author-submit'); closeAllMenus()"
                >
                  {{ t('nav.newSubmission') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-my' }"
                  @click.prevent="router.push('/admin/manuscript/my'); closeAllMenus()"
                >
                  {{ t('nav.myManuscripts') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-progress' }"
                  @click.prevent="router.push('/admin/manuscript/progress'); closeAllMenus()"
                >
                  {{ t('nav.manuscriptProgress') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-manuscript-history' }"
                  @click.prevent="router.push('/admin/manuscript/history'); closeAllMenus()"
                >
                  {{ t('nav.historySubmission') }}
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
                :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' || currentPage.startsWith('admin-profile') || currentPage === 'admin-notifications' }"
              >
                {{ t('nav.profile') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showProfileMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'author-profile' || currentPage === 'admin-author-profile' }"
                  @click.prevent="router.push('/admin/author-profile'); closeAllMenus()"
                >
                  {{ t('nav.profileInfo') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-profile-security' }"
                  @click.prevent="router.push('/admin/profile-security'); closeAllMenus()"
                >
                  {{ t('nav.accountSecurity') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-notifications' }"
                  @click.prevent="router.push('/admin/notifications'); closeAllMenus()"
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
                :class="{ active: currentPage.startsWith('admin-guide') }"
              >
                {{ t('nav.submissionGuide') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showGuideMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-submission-rules' }"
                  @click.prevent="router.push('/admin/submission-rules'); closeAllMenus()"
                >
                  {{ t('nav.submissionRules') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-guide-faq' }"
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
                :class="{ active: currentPage.startsWith('admin-help') }"
              >
                {{ t('nav.helpCenter') }} ▼
              </a>
            </div>
            <ul class="dropdown-menu" v-if="showAuthorHelpMenu">
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-help-consultation' }"
                  @click.prevent="router.push('/admin/help/consultation'); closeAllMenus()"
                >
                  {{ t('nav.onlineConsultation') }}
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  class="nav-link"
                  :class="{ active: currentPage === 'admin-help-feedback' }"
                  @click.prevent="router.push('/admin/help/feedback'); closeAllMenus()"
                >
                  {{ t('nav.feedback') }}
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
        </template>
        
        <!-- 登录状态导航 -->
        <template v-if="user">
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link logout"
              @click.prevent="handleLogout"
            >
              {{ t('nav.logout') }}
            </a>
          </li>
        </template>
        <template v-else-if="!isAdminRoute()">
          <!-- 未登录用户：登录和注册 -->
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              @click.prevent="router.push('/login')"
            >
              {{ t('nav.login') }}
            </a>
          </li>
          <li class="nav-item">
            <a 
              href="#" 
              class="nav-link"
              @click.prevent="router.push('/register')"
            >
              {{ t('nav.register') }}
            </a>
          </li>
        </template>
        
        <!-- Language Switcher -->
        <li class="nav-item">
          <a href="#" class="nav-link" @click.prevent="toggleLang">
            {{ currentLang === 'en' ? '中文' : 'En' }}
          </a>
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped>
/* 导航栏样式 - 固定在顶部 */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  border: none;
  outline: none;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  min-width: 600px;
  justify-content: flex-end;
}

.nav-item {
  margin-left: 0.5rem;
  flex-shrink: 0;
}

.nav-link {
  color: white;
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

.nav-link:hover,
.nav-link.active {
  color: #3498db;
  background: rgba(52, 152, 219, 0.1);
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
  background: rgba(231, 76, 60, 0.1);
}

/* 下拉菜单样式 */
.nav-item.dropdown {
  position: relative;
}

.dropdown-toggle {
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: #2c3e50;
  border-radius: 5px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  z-index: 1001;
  min-width: 150px;
  margin-top: 0.5rem;
  list-style: none;
  padding: 0.5rem 0;
}

.dropdown-menu li {
  margin: 0;
}

.dropdown-menu .dropdown-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  margin: 0.5rem 0;
  padding: 0;
}

.dropdown-menu .nav-link {
  display: block;
  padding: 0.5rem 1.5rem;
  color: white;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-align: left;
  min-width: auto;
}

.dropdown-menu .nav-link:hover,
.dropdown-menu .nav-link.active {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .nav-item {
    margin-left: 0;
  }
  
  .nav-link {
    font-size: 0.9rem;
    padding: 0.5rem 1rem;
    min-width: 70px;
  }
  
  .navbar-logo h1 {
    font-size: 1.3rem;
  }
  
  /* 移动端下拉菜单调整 */
  .dropdown-menu {
    position: static;
    width: 100%;
    box-shadow: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 0.5rem;
  }
  
  .nav-item.dropdown:hover .dropdown-menu {
    display: block;
  }
  
  .dropdown-menu .nav-link {
    text-align: center;
  }
}
</style>