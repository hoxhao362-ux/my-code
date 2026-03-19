<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import { useI18n } from 'vue-i18n'
import Navigation from '../../../components/Navigation.vue'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const user = ref(userStore.user)

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

// 基础配置数据 - 使用ref存储表单数据
const basicConfig = ref({
  platformName: '',
  platformLogo: '',
  submissionRules: '',
  contactEmail: '',
  contactPhone: '',
  copyrightInfo: ''
})

// 组件挂载时，从userStore加载配置数据
onMounted(() => {
  // 从userStore获取配置数据
  basicConfig.value = {
    ...userStore.basicConfig
  }
})

const saveConfig = () => {
  userStore.setBasicConfig(basicConfig.value)
  toastStore.add({ message: t('notification.basicConfig.actions.saveSuccess'), type: 'success' })
}

const resetConfig = () => {
  const defaultConfig = {
    platformName: 'Peerex Peer',
    platformLogo: '',
    submissionRules: '1. Content must comply with academic standards\n2. Plagiarism is strictly prohibited\n3. All submissions undergo strict review\n4. Review cycle is typically 1-2 weeks\n5. Platform reserves all rights',
    contactEmail: 'contact@example.com',
    contactPhone: '13800138000',
    copyrightInfo: '© 2026 Peerex Peer. All rights reserved.'
  }
  basicConfig.value = {
    ...defaultConfig
  }
  userStore.setBasicConfig(defaultConfig)
  toastStore.add({ message: t('notification.basicConfig.actions.resetSuccess'), type: 'success' })
}
</script>

<template>
  <div class="admin-basic-config-container">
    <!-- 导航栏 -->
    <Navigation 
      v-if="!embedded"
      :user="user"
      :current-page="'admin-system-basic'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 基础配置内容 -->
    <main class="content" :class="{ 'embedded-content': embedded }">
      <div class="header">
        <h1>{{ $t('notification.basicConfig.title') }}</h1>
        <p class="subtitle">{{ $t('notification.basicConfig.subtitle') }}</p>
      </div>

      <section class="config-section">
        <div class="config-form-container">
          <form class="config-form">
            <div class="form-section">
              <h3>{{ $t('notification.basicConfig.platformInfo.title') }}</h3>
              
              <div class="form-group">
                <label for="platformName">{{ $t('notification.basicConfig.platformInfo.name') }}</label>
                <input 
                  type="text" 
                  id="platformName" 
                  v-model="basicConfig.platformName" 
                  class="form-control"
                  :placeholder="$t('notification.basicConfig.platformInfo.placeholderName')"
                >
              </div>
              
              <div class="form-group">
                <label for="platformLogo">{{ $t('notification.basicConfig.platformInfo.logo') }}</label>
                <div class="file-upload">
                  <input 
                    type="file" 
                    id="platformLogo" 
                    @change="(e) => basicConfig.platformLogo = e.target.files[0]?.name || ''" 
                    class="file-input"
                  >
                  <label for="platformLogo" class="file-label">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 1a7 7 0 1 1 0 14A7 7 0 0 1 8 1zm0 13a6 6 0 1 0 0-12 6 6 0 0 0 0 12z"/>
                      <path d="M8 6a.5.5 0 0 1 .5.5v2.5h2.5a.5.5 0 0 1 0 1H8.5V11a.5.5 0 0 1-1 0V9.5H4a.5.5 0 0 1 0-1H7.5V6.5A.5.5 0 0 1 8 6z"/>
                    </svg>
                    <span>{{ basicConfig.platformLogo || $t('notification.basicConfig.platformInfo.placeholderLogo') }}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>{{ $t('notification.basicConfig.contact.title') }}</h3>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="contactEmail">{{ $t('notification.basicConfig.contact.email') }}</label>
                  <input 
                    type="email" 
                    id="contactEmail" 
                    v-model="basicConfig.contactEmail" 
                    class="form-control"
                    :placeholder="$t('notification.basicConfig.contact.placeholderEmail')"
                  >
                </div>
                
                <div class="form-group">
                  <label for="contactPhone">{{ $t('notification.basicConfig.contact.phone') }}</label>
                  <input 
                    type="tel" 
                    id="contactPhone" 
                    v-model="basicConfig.contactPhone" 
                    class="form-control"
                    :placeholder="$t('notification.basicConfig.contact.placeholderPhone')"
                  >
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>{{ $t('notification.basicConfig.rules.title') }}</h3>
              
              <div class="form-group">
                <label for="submissionRules">{{ $t('notification.basicConfig.rules.label') }}</label>
                <textarea 
                  id="submissionRules" 
                  v-model="basicConfig.submissionRules" 
                  class="form-control textarea-large"
                  rows="8"
                  :placeholder="$t('notification.basicConfig.rules.placeholder')"
                ></textarea>
              </div>
            </div>
            
            <div class="form-section">
              <h3>{{ $t('notification.basicConfig.copyright.title') }}</h3>
              
              <div class="form-group">
                <label for="copyrightInfo">{{ $t('notification.basicConfig.copyright.label') }}</label>
                <input 
                  type="text" 
                  id="copyrightInfo" 
                  v-model="basicConfig.copyrightInfo" 
                  class="form-control"
                  :placeholder="$t('notification.basicConfig.copyright.placeholder')"
                >
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-reset" @click="resetConfig">{{ $t('notification.basicConfig.actions.reset') }}</button>
              <button type="button" class="btn btn-save" @click="saveConfig">{{ $t('notification.basicConfig.actions.save') }}</button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer" v-if="!embedded">
      <div class="footer-content">
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.admin-basic-config-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.content.embedded-content {
  margin-top: 0;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 配置区域样式 */
.config-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

.config-form-container {
  max-width: 800px;
}

/* 表单样式 */
.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  flex: 1;
}

.form-group label {
  display: block;
  font-size: 0.95rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.textarea-large {
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

/* 文件上传样式 */
.file-upload {
  position: relative;
  display: inline-block;
  width: 100%;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem;
  border: 2px dashed #ddd;
  border-radius: 6px;
  font-size: 1rem;
  color: #555;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.file-label:hover {
  border-color: #3498db;
  background-color: #e3f2fd;
  color: #3498db;
}

.file-label svg {
  width: 20px;
  height: 20px;
}

/* 按钮样式 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-reset {
  background-color: #95a5a6;
  color: white;
}

.btn-reset:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.btn-save {
  background-color: #2ecc71;
  color: white;
}

.btn-save:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

/* 页脚样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.footer-content p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .config-section {
    padding: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>