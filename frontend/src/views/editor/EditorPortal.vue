<script setup>
import { ref, computed, shallowRef, onMounted, watch } from 'vue'
import Navigation from '../../components/Navigation.vue'
import { useUserStore } from '../../stores/user'
import { useRoute } from 'vue-router'

// Import components
import Dashboard from '../admin/Dashboard.vue'
import Manuscripts from './Manuscripts.vue'
import Reviewers from './Reviewers.vue'
import Decisions from './Decisions.vue'
import Users from '../admin/Users.vue'
import AccountStatus from '../admin/AccountStatus.vue'
import BasicConfig from '../admin/system/BasicConfig.vue'
// For components not yet updated to support embedded prop, we might see double nav. 
// I will import them anyway.
import NotificationConfig from '../admin/system/NotificationConfig.vue'
import Modules from '../admin/Modules.vue'
import InvitationCodes from '../admin/InvitationCodes.vue'
import LogsManagement from '../admin/system/LogsManagement.vue'
import AuthorProfile from '../author/Profile.vue'
import ProfileSecurity from '../admin/ProfileSecurity.vue'
import Notifications from '../admin/Notifications.vue'
import Help from '../submission/Help.vue'
import Feedback from '../admin/help/Feedback.vue'
// Audit components
import NewSubmissions from './audit/NewSubmissions.vue'
import AssignReviewers from './audit/AssignReviewers.vue'
import ReviewMonitoring from './audit/ReviewMonitoring.vue'
import DecisionMaking from './audit/DecisionMaking.vue'
import RevisionHandling from './audit/RevisionHandling.vue'
import ReviewerManagementAudit from './audit/ReviewerManagement.vue'
import RecommendedReviewersAudit from './audit/RecommendedReviewers.vue'
import OpposedReviewersAudit from './audit/OpposedReviewers.vue'
import MyTasksHistory from './audit/MyTasksHistory.vue'
// Additional admin components
import Journals from '../admin/Journals.vue'
import ProfileSettings from '../admin/ProfileSettings.vue'
import ProfileManuscriptStatus from '../admin/ProfileManuscriptStatus.vue'
import DataStatistics from './DataStatistics.vue'
import BoardManagement from './board/BoardManagement.vue'
// Submission components
import SystemStatus from '../submission/SystemStatus.vue'

const userStore = useUserStore()
const route = useRoute()
const currentViewKey = ref('editor-dashboard')

// 根据当前路由设置初始视图
onMounted(() => {
  const path = route.path
  if (path === '/editor/dashboard') {
    currentViewKey.value = 'editor-dashboard'
  } else if (path === '/editor/manuscripts') {
    currentViewKey.value = 'editor-manuscripts'
  } else if (path === '/editor/reviewers') {
    currentViewKey.value = 'editor-reviewers'
  } else if (path === '/editor/decisions') {
    currentViewKey.value = 'editor-decisions'
  } else if (path === '/editor/users') {
    currentViewKey.value = 'editor-users'
  } else if (path === '/editor/account-status') {
    currentViewKey.value = 'editor-account-status'
  } else if (path === '/editor/system/basic') {
    currentViewKey.value = 'editor-system-basic'
  } else if (path === '/editor/system/notification') {
    currentViewKey.value = 'editor-system-notification'
  } else if (path === '/editor/system/modules') {
    currentViewKey.value = 'editor-system-modules'
  } else if (path === '/editor/system/invitation-codes') {
    currentViewKey.value = 'editor-system-invitation-codes'
  } else if (path === '/editor/system/logs') {
    currentViewKey.value = 'editor-system-logs'
  } else if (path === '/editor/settings') {
    currentViewKey.value = 'editor-settings'
  } else if (path === '/editor/audit/new-submissions') {
    currentViewKey.value = 'audit-new-submissions'
  } else if (path === '/editor/audit/assign-reviewers') {
    currentViewKey.value = 'audit-assign-reviewers'
  } else if (path === '/editor/audit/review-monitoring') {
    currentViewKey.value = 'audit-review-monitoring'
  } else if (path === '/editor/audit/decision-making') {
    currentViewKey.value = 'audit-decision-making'
  } else if (path === '/editor/audit/revision-handling') {
    currentViewKey.value = 'audit-revision-handling'
  } else if (path === '/editor/audit/reviewer-management') {
    currentViewKey.value = 'audit-reviewer-management'
  } else if (path === '/editor/audit/recommended-reviewers') {
    currentViewKey.value = 'audit-recommended-reviewers'
  } else if (path === '/editor/audit/opposed-reviewers') {
    currentViewKey.value = 'audit-opposed-reviewers'
  } else if (path === '/editor/audit/my-tasks') {
    currentViewKey.value = 'audit-my-tasks'
  } else if (path === '/editor/reviewer-management') {
    currentViewKey.value = 'editor-reviewer-management'
  } else if (path === '/editor/journals') {
    currentViewKey.value = 'editor-journals'
  } else if (path === '/editor/modules') {
    currentViewKey.value = 'editor-modules'
  } else if (path === '/editor/statistics') {
    currentViewKey.value = 'editor-statistics'
  } else if (path === '/editor/board') {
    currentViewKey.value = 'editor-board'
  } else if (path === '/admin/profile-manuscript-status') {
    currentViewKey.value = 'admin-profile-manuscript-status'
  } else if (path === '/submission/system-status') {
    currentViewKey.value = 'submission-system-status'
  }
})

// 监听路由变化
watch(() => route.path, (newPath) => {
  if (newPath === '/editor/dashboard') {
    currentViewKey.value = 'editor-dashboard'
  } else if (newPath === '/editor/manuscripts') {
    currentViewKey.value = 'editor-manuscripts'
  } else if (newPath === '/editor/reviewers') {
    currentViewKey.value = 'editor-reviewers'
  } else if (newPath === '/editor/decisions') {
    currentViewKey.value = 'editor-decisions'
  } else if (newPath === '/editor/users') {
    currentViewKey.value = 'editor-users'
  } else if (newPath === '/editor/account-status') {
    currentViewKey.value = 'editor-account-status'
  } else if (newPath === '/editor/system/basic') {
    currentViewKey.value = 'editor-system-basic'
  } else if (newPath === '/editor/system/notification') {
    currentViewKey.value = 'editor-system-notification'
  } else if (newPath === '/editor/system/modules') {
    currentViewKey.value = 'editor-system-modules'
  } else if (newPath === '/editor/system/invitation-codes') {
    currentViewKey.value = 'editor-system-invitation-codes'
  } else if (newPath === '/editor/system/logs') {
    currentViewKey.value = 'editor-system-logs'
  } else if (newPath === '/editor/settings') {
    currentViewKey.value = 'editor-settings'
  } else if (newPath === '/editor/audit/new-submissions') {
    currentViewKey.value = 'audit-new-submissions'
  } else if (newPath === '/editor/audit/assign-reviewers') {
    currentViewKey.value = 'audit-assign-reviewers'
  } else if (newPath === '/editor/audit/review-monitoring') {
    currentViewKey.value = 'audit-review-monitoring'
  } else if (newPath === '/editor/audit/decision-making') {
    currentViewKey.value = 'audit-decision-making'
  } else if (newPath === '/editor/audit/revision-handling') {
    currentViewKey.value = 'audit-revision-handling'
  } else if (newPath === '/editor/audit/reviewer-management') {
    currentViewKey.value = 'audit-reviewer-management'
  } else if (newPath === '/editor/audit/recommended-reviewers') {
    currentViewKey.value = 'audit-recommended-reviewers'
  } else if (newPath === '/editor/audit/opposed-reviewers') {
    currentViewKey.value = 'audit-opposed-reviewers'
  } else if (newPath === '/editor/audit/my-tasks') {
    currentViewKey.value = 'audit-my-tasks'
  } else if (newPath === '/editor/reviewer-management') {
    currentViewKey.value = 'editor-reviewer-management'
  } else if (newPath === '/editor/journals') {
    currentViewKey.value = 'editor-journals'
  } else if (newPath === '/editor/modules') {
    currentViewKey.value = 'editor-modules'
  } else if (newPath === '/editor/statistics') {
    currentViewKey.value = 'editor-statistics'
  } else if (newPath === '/editor/board') {
    currentViewKey.value = 'editor-board'
  } else if (newPath === '/admin/profile-manuscript-status') {
    currentViewKey.value = 'admin-profile-manuscript-status'
  } else if (newPath === '/submission/system-status') {
    currentViewKey.value = 'submission-system-status'
  }
})

const componentMap = {
  'editor-dashboard': Dashboard,
  'editor-manuscripts': Manuscripts,
  'editor-reviewers': Reviewers,
  'editor-decisions': Decisions,
  'editor-users': Users,
  'editor-account-status': AccountStatus,
  'editor-system-basic': BasicConfig,
  'editor-system-notification': NotificationConfig,
  'editor-system-modules': Modules,
  'editor-system-invitation-codes': InvitationCodes,
  'editor-system-logs': LogsManagement,
  'editor-settings': ProfileSettings,
  'editor-reviewer-management': ReviewerManagementAudit,
  'editor-journals': Journals,
  'editor-modules': Modules,
  'editor-statistics': ReviewerStats,
  'editor-board': BoardManagement,
  'audit-new-submissions': NewSubmissions,
  'audit-assign-reviewers': AssignReviewers,
  'audit-review-monitoring': ReviewMonitoring,
  'audit-decision-making': DecisionMaking,
  'audit-revision-handling': RevisionHandling,
  'audit-reviewer-management': ReviewerManagementAudit,
  'audit-recommended-reviewers': RecommendedReviewersAudit,
  'audit-opposed-reviewers': OpposedReviewersAudit,
  'audit-my-tasks': MyTasksHistory,
  'admin-profile-manuscript-status': ProfileManuscriptStatus,
  'submission-system-status': SystemStatus,
  'submission-author-profile': AuthorProfile,
  'submission-profile-security': ProfileSecurity,
  'submission-notifications': Notifications,
  'submission-help': Help,
  'submission-help-feedback': Feedback
}

const currentComponent = computed(() => componentMap[currentViewKey.value] || Dashboard)

const handleNavigate = (key) => {
  currentViewKey.value = key
  // Optional: Update URL query param without full reload if desired, 
  // but requirements say "no route jump", so internal state is fine.
}
</script>

<template>
  <div class="editor-portal">
    <Navigation 
      :user="userStore.user"
      :current-page="currentViewKey"
      :custom-navigation="true"
      @navigate="handleNavigate"
      :logout="userStore.logout"
    />
    <div class="portal-content">
      <!-- Pass embedded=true to all components. 
           Those that support it will hide their own nav. 
           Those that don't will just ignore it (and show double nav until updated). -->
      <component :is="currentComponent" :embedded="true" />
    </div>
  </div>
</template>

<style scoped>
.editor-portal {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.portal-content {
  flex: 1;
  width: 100%;
  margin-top: 80px; /* Fixed Navigation height */
}
</style>