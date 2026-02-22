<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

// 多步骤注册状态
const currentStep = ref(1)
const maxSteps = 5

// 第一步：基本信息
const firstName = ref('')
const lastName = ref('')
const email = ref('')

// 第二步：登录详情
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

// 第三步：个人信息
const title = ref('')
const middleName = ref('')
const degree = ref('')
const orcid = ref('')

// 第四步：机构信息
const position = ref('')
const institution = ref('')
const department = ref('')
const streetAddress = ref('')
const city = ref('')
const stateProvince = ref('')
const zipCode = ref('')
const country = ref('')

// 第五步：专业领域
const personalClassifications = ref([])
const personalKeywords = ref([])

const error = ref('')

// 表单验证
const isStep1Valid = computed(() => {
  return firstName.value && lastName.value && email.value
})

const isStep2Valid = computed(() => {
  return username.value && password.value && confirmPassword.value && password.value === confirmPassword.value
})

const isStep3Valid = computed(() => {
  return title.value && firstName.value && lastName.value && email.value
})

const isStep4Valid = computed(() => {
  return position.value && institution.value && department.value && country.value
})

const isStep5Valid = computed(() => {
  return personalClassifications.value.length > 0
})

const isCurrentStepValid = computed(() => {
  switch (currentStep.value) {
    case 1: return isStep1Valid.value
    case 2: return isStep2Valid.value
    case 3: return isStep3Valid.value
    case 4: return isStep4Valid.value
    case 5: return isStep5Valid.value
    default: return false
  }
})

// 导航到下一步
const goToNextStep = () => {
  if (isCurrentStepValid.value) {
    error.value = ''
    if (currentStep.value < maxSteps) {
      currentStep.value++
    }
  } else {
    error.value = 'Please fill in all required fields'
  }
}

// 导航到上一步
const goToPrevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 处理注册
const handleRegister = async () => {
  if (!isCurrentStepValid.value) {
    error.value = 'Please fill in all required fields'
    return
  }
  
  if (password.value.length < 6) {
    error.value = 'Password length must be at least 6 characters'
    return
  }
  
  // 加密密码
  const encryptedPassword = encryptPassword(password.value)
  
  // 模拟注册逻辑
  const userData = {
    username: username.value,
    password: encryptedPassword,
    role: 'writer', // 默认角色为作者
    email: email.value,
    firstName: firstName.value,
    lastName: lastName.value,
    title: title.value,
    middleName: middleName.value,
    degree: degree.value,
    orcid: orcid.value,
    position: position.value,
    institution: institution.value,
    department: department.value,
    streetAddress: streetAddress.value,
    city: city.value,
    stateProvince: stateProvince.value,
    zipCode: zipCode.value,
    country: country.value,
    personalClassifications: personalClassifications.value,
    personalKeywords: personalKeywords.value,
    avatar: ''
  }
  
  // 检查用户名是否已存在
  const isUsernameExists = false
  
  if (isUsernameExists) {
    error.value = 'This username is already registered'
    return
  }
  
  // 调用状态管理的登录方法（注册后自动登录）
  userStore.loginSubmission(userData)
  
  // 跳转到对应的后台页面
  router.push('/submission')
}

const goToLogin = () => {
  emit('go-to-login')
}

// 定义事件
const emit = defineEmits(['go-to-login'])

const useORCID = () => {
  // 模拟ORCID集成
  alert('ORCID集成功能将在未来版本中实现')
}

const selectPersonalClassifications = () => {
  // 模拟选择个人分类
  const classifications = ['Medical Imaging', 'Drug Discovery', 'Clinical Research']
  personalClassifications.value = classifications
}

const editPersonalKeywords = () => {
  // 模拟编辑个人关键词
  const keywords = ['AI', 'Machine Learning', 'Deep Learning']
  personalKeywords.value = keywords
}
</script>

<template>
  <div class="admin-register-form">
    <!-- 注册标题 -->
    <h2 class="admin-register-title">Journal Platform - Register Account</h2>
    
    <!-- 步骤指示器 -->
    <div class="step-indicator">
      <div 
        v-for="step in maxSteps" 
        :key="step"
        class="step-item"
        :class="{ active: step <= currentStep, completed: step < currentStep }"
      >
        {{ step }}
      </div>
    </div>
    
    <!-- 第一步：基本信息 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3 class="step-title">Choose a Registration Method</h3>
      
      <div class="orcid-section">
        <p>Retrieve your details from the ORCID registry:</p>
        <button class="orcid-button" @click="useORCID">
          <span class="orcid-icon">🔍</span> Use My ORCID Record
        </button>
      </div>
      
      <div class="manual-registration">
        <p>Or type in your details and continue to register without using ORCID:</p>
        
        <div class="admin-form-group required">
          <label for="firstName">Given/First Name*</label>
          <input 
            type="text" 
            id="firstName" 
            v-model="firstName" 
            placeholder="Enter your first name"
          />
        </div>
        
        <div class="admin-form-group required">
          <label for="lastName">Family/Last Name*</label>
          <input 
            type="text" 
            id="lastName" 
            v-model="lastName" 
            placeholder="Enter your last name"
          />
        </div>
        
        <div class="admin-form-group required">
          <label for="email">E-mail Address*</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="Enter your email address"
          />
        </div>
      </div>
      
      <div class="warning-section">
        <h4>WARNING</h4>
        <p>If you think you already have an existing registration of any type (Author, Reviewer, or Editor) in this system, please DO NOT register again. This will cause delays or prevent the processing of any manuscript you submit. If you are unsure if you are already registered, click the 'Forgot Your Login Details?' button.</p>
        <p>If you are registering again because you want to change your current information, changes must be made to your existing information by clicking the 'Update My Information' link on the menu bar. If you are unsure how to perform these functions, please contact the editorial office.</p>
      </div>
    </div>
    
    <!-- 第二步：登录详情 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3 class="step-title">Login Details</h3>
      
      <div class="info-section">
        <p>The username you choose must be unique within the system.</p>
        <p>If the one you choose is already in use, you will be asked for another.</p>
      </div>
      
      <div class="admin-form-group required">
        <label for="username">Enter preferred user name*</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="Enter your username"
        />
      </div>
      
      <div class="admin-form-group required">
        <label for="password">Password*</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="Enter your password"
        />
      </div>
      
      <div class="admin-form-group required">
        <label for="confirmPassword">Re-type Password*</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          placeholder="Re-enter your password"
        />
      </div>
      
      <div class="password-rules">
        <a href="#" class="password-rules-link">Password Rules</a>
      </div>
    </div>
    
    <!-- 第三步：个人信息 -->
    <div v-if="currentStep === 3" class="step-content">
      <h3 class="step-title">Personal Information</h3>
      
      <div class="admin-form-group required">
        <label for="title">Title*</label>
        <input 
          type="text" 
          id="title" 
          v-model="title" 
          placeholder="Enter your title"
        />
      </div>
      
      <div class="admin-form-group required">
        <label for="firstName3">Given/First Name*</label>
        <input 
          type="text" 
          id="firstName3" 
          v-model="firstName" 
          placeholder="Enter your first name"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="middleName">Middle Name</label>
        <input 
          type="text" 
          id="middleName" 
          v-model="middleName" 
          placeholder="Enter your middle name"
        />
      </div>
      
      <div class="admin-form-group required">
        <label for="lastName3">Family/Last Name*</label>
        <input 
          type="text" 
          id="lastName3" 
          v-model="lastName" 
          placeholder="Enter your last name"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="degree">Degree</label>
        <div class="input-with-hint">
          <input 
            type="text" 
            id="degree" 
            v-model="degree" 
            placeholder="Enter your degree"
          />
          <span class="input-hint">(Ph.D., M.D., etc.)</span>
        </div>
      </div>
      
      <div class="admin-form-group required">
        <label for="email3">E-mail Address*</label>
        <input 
          type="email" 
          id="email3" 
          v-model="email" 
          placeholder="Enter your email address"
        />
      </div>
      
      <div class="email-info">
        <p>If entering more than one e-mail address, use a semi-colon between each address (e.g., joe@example.com;joe@yahoo.com). Entering a second e-mail address from a different e-mail provider decreases the chance that SPAM filters will trap e-mails sent to you from online systems.</p>
      </div>
      
      <div class="orcid-info">
        <p>You are encouraged to link to your ORCID ID and authenticate it. This will allow you to share information with other systems, ensure you get recognition for all your contributions and reduce the risk of errors.</p>
        <p>You will only need to do this once in this journal to permanently associate your ORCID ID with your account and you can do this by clicking on the fetch/register link below.</p>
      </div>
      
      <div class="orcid-input-group">
        <label for="orcid">ORCID</label>
        <div class="orcid-input-wrapper">
          <input 
            type="text" 
            id="orcid" 
            v-model="orcid" 
            placeholder="Enter your ORCID"
          />
          <button class="orcid-fetch-button">Fetch/Register</button>
        </div>
        <a href="#" class="orcid-link">What is ORCID?</a>
      </div>
    </div>
    
    <!-- 第四步：机构信息 -->
    <div v-if="currentStep === 4" class="step-content">
      <h3 class="step-title">Institution Related Information</h3>
      
      <div class="admin-form-group">
        <label for="position">Position</label>
        <input 
          type="text" 
          id="position" 
          v-model="position" 
          placeholder="Enter your position"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="institution">Institution</label>
        <div class="input-with-hint">
          <input 
            type="text" 
            id="institution" 
            v-model="institution" 
            placeholder="Enter your institution"
          />
          <span class="input-hint">Start typing to display potentially matching institutions.</span>
        </div>
      </div>
      
      <div class="admin-form-group">
        <label for="department">Department</label>
        <input 
          type="text" 
          id="department" 
          v-model="department" 
          placeholder="Enter your department"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="streetAddress">Street Address</label>
        <input 
          type="text" 
          id="streetAddress" 
          v-model="streetAddress" 
          placeholder="Enter your street address"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="city">City</label>
        <input 
          type="text" 
          id="city" 
          v-model="city" 
          placeholder="Enter your city"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="stateProvince">State or Province</label>
        <input 
          type="text" 
          id="stateProvince" 
          v-model="stateProvince" 
          placeholder="Enter your state or province"
        />
      </div>
      
      <div class="admin-form-group">
        <label for="zipCode">Zip or Postal Code</label>
        <input 
          type="text" 
          id="zipCode" 
          v-model="zipCode" 
          placeholder="Enter your zip code"
        />
      </div>
      
      <div class="admin-form-group required">
        <label for="country">Country or Region*</label>
        <select 
          id="country" 
          v-model="country"
          class="admin-role-select"
        >
          <option value="">Select country or region</option>
          <option value="China">China</option>
          <option value="United States">United States</option>
          <option value="United Kingdom">United Kingdom</option>
          <option value="Canada">Canada</option>
          <option value="Australia">Australia</option>
          <option value="Other">Other</option>
        </select>
      </div>
    </div>
    
    <!-- 第五步：专业领域 -->
    <div v-if="currentStep === 5" class="step-content">
      <h3 class="step-title">Areas of Interest or Expertise</h3>
      
      <div class="expertise-info">
        <p>Please indicate your areas of expertise either by selecting from the pre-defined list using the "Select Personal Classifications" button or by adding your own keywords individually using the "New Keyword" field and associated "Add" button.</p>
      </div>
      
      <div class="admin-form-group required">
        <label for="personalClassifications">Personal Classifications*</label>
        <div class="classifications-section">
          <div class="selected-classifications">
            {{ personalClassifications.length > 0 ? personalClassifications.join(', ') : '(None Selected)' }}
          </div>
          <button class="classifications-button" @click="selectPersonalClassifications">
            Select Personal Classifications
          </button>
          <div class="required-note">Select 1+ Classifications</div>
        </div>
      </div>
      
      <div class="admin-form-group">
        <label for="personalKeywords">Personal Keywords</label>
        <div class="keywords-section">
          <div class="selected-keywords">
            {{ personalKeywords.length > 0 ? personalKeywords.join(', ') : '(None Defined)' }}
          </div>
          <button class="keywords-button" @click="editPersonalKeywords">
            Edit Personal Keywords
          </button>
        </div>
      </div>
      
      <div class="registration-info">
        <p>After successful registration, additional user details can be added by navigating to the Update My Information page.</p>
      </div>
    </div>
    
    <!-- 错误消息 -->
    <p v-if="error" class="admin-error-message">{{ error }}</p>
    
    <!-- 导航按钮 -->
    <div class="step-navigation">
      <button 
        v-if="currentStep > 1" 
        class="back-button"
        @click="goToPrevStep"
      >
        Back
      </button>
      
      <button 
        v-if="currentStep < maxSteps" 
        class="continue-button"
        @click="goToNextStep"
        :disabled="!isCurrentStepValid"
      >
        Continue >>
      </button>
      
      <button 
        v-if="currentStep === maxSteps" 
        class="register-button"
        @click="handleRegister"
        :disabled="!isCurrentStepValid"
      >
        Complete Registration
      </button>
    </div>
    
    <!-- 登录链接 -->
    <div class="admin-login-link">
      <span>Already have an account?</span>
      <a href="#" @click.prevent="goToLogin">Login now</a>
    </div>
    

  </div>
</template>

<style scoped>
/* 后台注册页面样式 */
.admin-register-form {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 600px;
  margin: 2rem auto;
}

.admin-register-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #343a40;
  font-size: 1.8rem;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding: 0 1rem;
}

.step-item {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #e9ecef;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: #6c757d;
  transition: all 0.3s ease;
}

.step-item.active {
  background-color: #007bff;
  color: white;
}

.step-item.completed {
  background-color: #28a745;
  color: white;
}

/* 步骤内容 */
.step-content {
  margin-bottom: 2rem;
}

.step-title {
  color: #343a40;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
}

/* 表单样式 */
.admin-form-group {
  margin-bottom: 1.2rem;
}

.admin-form-group.required label {
  color: #dc3545;
}

.admin-form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-size: 0.95rem;
  font-weight: 500;
}

.admin-form-group input,
.admin-form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background-color: white;
}

.admin-form-group input:focus,
.admin-form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* 输入框带提示 */
.input-with-hint {
  position: relative;
}

.input-hint {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: #6c757d;
}

/* ORCID 部分 */
.orcid-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.orcid-button {
  background-color: #a6ce39;
  color: #333;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.orcid-button:hover {
  background-color: #95b932;
}

.orcid-icon {
  margin-right: 0.5rem;
}

/* 手动注册部分 */
.manual-registration {
  margin-bottom: 2rem;
}

/* 警告部分 */
.warning-section {
  padding: 1.5rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  margin-bottom: 2rem;
}

.warning-section h4 {
  color: #856404;
  margin-top: 0;
}

.warning-section p {
  color: #856404;
  margin-bottom: 0.5rem;
}

/* 密码规则 */
.password-rules {
  margin-top: 1rem;
  text-align: right;
}

.password-rules-link {
  color: #007bff;
  text-decoration: none;
}

.password-rules-link:hover {
  text-decoration: underline;
}

/* 邮箱信息 */
.email-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* ORCID 信息 */
.orcid-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* ORCID 输入组 */
.orcid-input-group {
  margin: 1rem 0;
}

.orcid-input-wrapper {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.orcid-fetch-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.orcid-fetch-button:hover {
  background-color: #0056b3;
}

.orcid-link {
  color: #007bff;
  text-decoration: none;
  font-size: 0.9rem;
}

.orcid-link:hover {
  text-decoration: underline;
}

/* 机构信息部分 */
.institution-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* 专业领域部分 */
.expertise-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

.classifications-section {
  margin-top: 0.5rem;
}

.selected-classifications {
  margin-bottom: 0.5rem;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.classifications-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 0.5rem;
}

.classifications-button:hover {
  background-color: #0056b3;
}

.required-note {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.keywords-section {
  margin-top: 0.5rem;
}

.selected-keywords {
  margin-bottom: 0.5rem;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.keywords-button {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.keywords-button:hover {
  background-color: #545b62;
}

/* 注册信息 */
.registration-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* 角色选择样式 */
.admin-role-select {
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='none' stroke='%23495057' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 16px;
  padding-right: 2rem;
  appearance: none;
}

/* 错误消息样式 */
.admin-error-message {
  color: #dc3545;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* 步骤导航 */
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-button {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #545b62;
}

.continue-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.continue-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.continue-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.65;
}

.register-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
}

.register-button:hover:not(:disabled) {
  background-color: #218838;
}

.register-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.65;
}

/* 登录链接样式 */
.admin-login-link {
  text-align: center;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.8rem;
}

.admin-login-link a {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-login-link a:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* 返回主站链接样式 */
.admin-back-link {
  text-align: center;
  font-size: 0.9rem;
}

.admin-back-link a {
  color: #6c757d;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-back-link a:hover {
  color: #495057;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-register-form {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .admin-register-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .step-indicator {
    padding: 0;
  }
  
  .step-item {
    width: 25px;
    height: 25px;
  }
  
  .orcid-input-wrapper {
    flex-direction: column;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 1rem;
  }
  
  .back-button,
  .continue-button {
    width: 100%;
  }
}
</style>