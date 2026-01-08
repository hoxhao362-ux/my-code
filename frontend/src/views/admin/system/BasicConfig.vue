<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = ref(userStore.user)

// 基础配置数据
const basicConfig = ref({
  platformName: '期刊投稿平台',
  platformLogo: '',
  submissionRules: '1. 投稿内容必须符合学术规范\n2. 禁止抄袭和剽窃\n3. 所有投稿将经过严格审核\n4. 审核周期一般为1-2周\n5. 最终解释权归平台所有',
  contactEmail: 'contact@example.com',
  contactPhone: '13800138000',
  copyrightInfo: '© 2026 期刊投稿平台. All rights reserved.'
})

// 保存配置
const saveConfig = () => {
  // 这里应该保存配置到服务器，目前模拟保存
  alert('基础配置已保存！')
}

// 重置配置
const resetConfig = () => {
  basicConfig.value = {
    platformName: '期刊投稿平台',
    platformLogo: '',
    submissionRules: '1. 投稿内容必须符合学术规范\n2. 禁止抄袭和剽窃\n3. 所有投稿将经过严格审核\n4. 审核周期一般为1-2周\n5. 最终解释权归平台所有',
    contactEmail: 'contact@example.com',
    contactPhone: '13800138000',
    copyrightInfo: '© 2026 期刊投稿平台. All rights reserved.'
  }
  alert('配置已重置为默认值！')
}
</script>

<template>
  <div class="admin-basic-config-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-system-basic'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 基础配置内容 -->
    <main class="content">
      <div class="header">
        <h1>系统设置 - 基础配置</h1>
        <p class="subtitle">管理平台的基础信息和规则</p>
      </div>

      <section class="config-section">
        <div class="config-form-container">
          <form class="config-form">
            <div class="form-section">
              <h3>平台基本信息</h3>
              
              <div class="form-group">
                <label for="platformName">平台名称</label>
                <input 
                  type="text" 
                  id="platformName" 
                  v-model="basicConfig.platformName" 
                  class="form-control"
                  placeholder="请输入平台名称"
                >
              </div>
              
              <div class="form-group">
                <label for="platformLogo">平台Logo</label>
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
                    <span>{{ basicConfig.platformLogo || '点击上传Logo' }}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>联系方式</h3>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="contactEmail">联系邮箱</label>
                  <input 
                    type="email" 
                    id="contactEmail" 
                    v-model="basicConfig.contactEmail" 
                    class="form-control"
                    placeholder="请输入联系邮箱"
                  >
                </div>
                
                <div class="form-group">
                  <label for="contactPhone">联系电话</label>
                  <input 
                    type="tel" 
                    id="contactPhone" 
                    v-model="basicConfig.contactPhone" 
                    class="form-control"
                    placeholder="请输入联系电话"
                  >
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <h3>投稿规则</h3>
              
              <div class="form-group">
                <label for="submissionRules">投稿规则</label>
                <textarea 
                  id="submissionRules" 
                  v-model="basicConfig.submissionRules" 
                  class="form-control textarea-large"
                  rows="8"
                  placeholder="请输入投稿规则"
                ></textarea>
              </div>
            </div>
            
            <div class="form-section">
              <h3>版权信息</h3>
              
              <div class="form-group">
                <label for="copyrightInfo">版权信息</label>
                <input 
                  type="text" 
                  id="copyrightInfo" 
                  v-model="basicConfig.copyrightInfo" 
                  class="form-control"
                  placeholder="请输入版权信息"
                >
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-reset" @click="resetConfig">重置</button>
              <button type="button" class="btn btn-save" @click="saveConfig">保存配置</button>
            </div>
          </form>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
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