import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'
import { manuscriptApi } from '../utils/api'

export const useSubmissionStore = defineStore('submission', () => {
  // 当前步骤 (1-6)
  const currentStep = ref(1)
  
  // 步骤状态
  const steps = ref([
    { id: 1, name: 'progress.step1', status: 'current' }, // pending, current, completed, error
    { id: 2, name: 'progress.step2', status: 'pending' },
    { id: 3, name: 'progress.step3', status: 'pending' },
    { id: 4, name: 'progress.step4', status: 'pending' },
    { id: 5, name: 'progress.step5', status: 'pending' },
    { id: 6, name: 'progress.step6', status: 'pending' },
  ])

  // 表单数据
  const formData = ref({
    // Step 1
    article_type: '',
    section_category: '',
    
    // Step 2
    files: [], // { id, name, type, description, fileObj (raw), url }
    referenceAnonymization: {
      file: null,
      confirmed: false
    },
    
    // Step 3
    subject: '',
    keywords: '',
    
    // Step 4
    additionalInfo: {
      q1: '',
      q2: '',
      q3: '',
      q4: '',
      q5: '',
      q6: '',
      ssrn: false,
      socialMedia: '',
      conference: 'No',
      recommendedReviewers: [],
      avoidedReviewers: [],
      blindReview: {
        enabled: true,
        confirmed: false
      }
    },
    
    // Step 5
    cover_letter: '',
    comments: '',
    
    // Step 6
    title: '',
    abstract: '',
    structuredAbstract: {
      background: '',
      methods: '',
      findings: '',
      interpretation: ''
    },
    authors: [], // { id, name, institution, email, orcid, is_corresponding, is_first }
    funding: [], // { id, body, number }
    noFunding: false,
    publishingOption: '' // Subscription / Open Access
  })

  // 初始化：从 localStorage 读取草稿
  const init = () => {
    const draft = localStorage.getItem('submission_draft')
    if (draft) {
      try {
        const parsed = JSON.parse(draft)
        // 恢复数据
        formData.value = { ...formData.value, ...parsed.formData }
        // 恢复步骤
        currentStep.value = parsed.currentStep || 1
        steps.value = parsed.steps || steps.value
      } catch (e) {
        console.error('Failed to load draft', e)
      }
    }
  }

  // 保存草稿
  const saveDraft = () => {
    // 序列化时去掉 fileObj 和 url (blob url 会失效)
    const dataToSave = {
      formData: JSON.parse(JSON.stringify(formData.value)), // Deep copy & remove non-serializable
      currentStep: currentStep.value,
      steps: steps.value
    }
    // Files 特殊处理：只存元数据
    dataToSave.formData.files = formData.value.files.map(f => ({
      id: f.id,
      name: f.name,
      type: f.type,
      description: f.description,
      size: f.size
    }))
    
    localStorage.setItem('submission_draft', JSON.stringify(dataToSave))
    return true
  }

  // 验证指定步骤
  const validateStep = (step) => {
    let isValid = true

    switch (step) {
      case 1:
        isValid = !!formData.value.article_type
        break
      case 2:
        isValid = formData.value.files.length > 0
        if (isValid && formData.value.referenceAnonymization) {
            if (!formData.value.referenceAnonymization.confirmed) {
                isValid = false
            }
        }
        if (isValid) {
          const requiredTypes = ['manuscript', 'contribution', 'conflict']
          const hasAllRequired = requiredTypes.every(type => 
            formData.value.files.some(f => f.type === type)
          )
          if (!hasAllRequired) {
            isValid = false
          }
        }
        break
      case 3:
        isValid = !!formData.value.subject && !!formData.value.keywords
        break
      case 4:
        const { q1, q2, q3, q4, q5, q6, recommendedReviewers, avoidedReviewers } = formData.value.additionalInfo
        isValid = !!q1 && !!q2 && !!q3 && !!q4 && !!q5 && !!q6
        if (isValid) {
          const limit = 500
          if (q1.length > limit || q2.length > limit || q3.length > limit || 
              q4.length > limit || q5.length > limit || q6.length > limit) {
            isValid = false
          }
        }

        // Validate Recommended Reviewers
        if (isValid && recommendedReviewers && recommendedReviewers.length > 0) {
           if (recommendedReviewers.length > 3) {
             isValid = false
           }
           const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
           for (const reviewer of recommendedReviewers) {
             if (!reviewer.name || !reviewer.email || !emailRegex.test(reviewer.email) || !reviewer.reason || reviewer.reason.length < 50) {
               isValid = false
               break
             }
             if (!reviewer.coiDeclared) {
               isValid = false
               break
             }
           }
        }

        // Validate Avoided Reviewers
        if (isValid && avoidedReviewers && avoidedReviewers.length > 0) {
           for (const reviewer of avoidedReviewers) {
             if (!reviewer.name || !reviewer.reason || reviewer.reason.length < 80) {
               isValid = false
               break
             }
           }
        }

        // Validate Blind Review Confirmation
        if (isValid && formData.value.additionalInfo.blindReview && !formData.value.additionalInfo.blindReview.confirmed) {
          isValid = false
        }
        break
      case 5:
        isValid = !!formData.value.cover_letter
        break
      case 6:
        const hasAuthor = formData.value.authors.length > 0
        const hasCorresponding = formData.value.authors.some(a => a.is_corresponding)
        const hasFirst = formData.value.authors.some(a => a.is_first)
        const hasFunding = formData.value.noFunding || formData.value.funding.length > 0
        
        const cleanTitle = formData.value.title.replace(/<[^>]*>/g, '').trim()
        const cleanAbstract = formData.value.abstract.replace(/<[^>]*>/g, '').trim()
        
        isValid = !!cleanTitle && !!cleanAbstract && !!formData.value.keywords &&
                  hasAuthor && hasCorresponding && hasFirst && hasFunding
        break
    }
    return isValid
  }

  // 验证当前步骤并更新状态
  const validateCurrentStep = () => {
    const step = currentStep.value
    const isValid = validateStep(step)

    // 更新步骤状态
    if (isValid) {
      steps.value[step - 1].status = 'completed'
    } else {
      steps.value[step - 1].status = 'error'
    }
    
    return isValid
  }

  // 验证所有步骤
  const validateAllSteps = () => {
    let allValid = true
    for (const step of steps.value) {
      const isValid = validateStep(step.id)
      if (!isValid) {
        step.status = 'error'
        allValid = false
      } else {
        step.status = 'completed'
      }
    }
    return allValid
  }

  // 导航
  const nextStep = () => {
    // Save draft regardless of validation
    saveDraft()
    
    // Validate current step to update status, but DO NOT block navigation
    // Per requirements: "Trigger full process mandatory item verification only after clicking 'Submit Manuscript'"
    validateCurrentStep() 
    
    if (currentStep.value < 6) {
      currentStep.value++
      // Set new step as current
      steps.value.forEach(s => {
         if (s.id === currentStep.value) s.status = 'current'
         // Previous steps remain as they were (completed or error or pending)
      })
      window.scrollTo(0, 0)
      return true
    }
    return false
  }

  const prevStep = () => {
    if (currentStep.value > 1) {
      // Save draft
      saveDraft()
      
      // Update status of current step before leaving
      validateCurrentStep()
      
      currentStep.value--
      steps.value.forEach(s => {
         if (s.id === currentStep.value) s.status = 'current'
      })
      window.scrollTo(0, 0)
    }
  }
  
  const goToStep = (targetStep) => {
    saveDraft()
    validateCurrentStep()
    currentStep.value = targetStep
    
    steps.value.forEach((s) => {
       if (s.id === targetStep) {
         s.status = 'current'
       }
    })
    
    window.scrollTo(0, 0)
  }

  // 提取重置表单状态的辅助函数
  const resetForm = () => {
    currentStep.value = 1
    steps.value.forEach(s => s.status = s.id === 1 ? 'current' : 'pending')
    formData.value = {
      article_type: '',
      section_category: '',
      files: [],
      referenceAnonymization: { file: null, confirmed: false },
      subject: '',
      keywords: '',
      additionalInfo: {
        q1: '', q2: '', q3: '', q4: '', q5: '', q6: '',
        ssrn: false, socialMedia: '', conference: 'No',
        recommendedReviewers: [],
        avoidedReviewers: [],
        blindReview: { enabled: true, confirmed: false }
      },
      cover_letter: '', comments: '', title: '', abstract: '',
      structuredAbstract: { background: '', methods: '', findings: '', interpretation: '' },
      authors: [],
      funding: [],
      noFunding: false,
      publishingOption: ''
    }
  }

  // 真实的提交逻辑
  const submitManuscript = async () => {
    try {
      const fd = new FormData()
      
      // 1. 附加基础文本字段
      fd.append('title', formData.value.title.replace(/<[^>]*>/g, '').trim())
      fd.append('abstract', formData.value.abstract.replace(/<[^>]*>/g, '').trim())
      fd.append('article_type', formData.value.article_type)
      fd.append('section_category', formData.value.section_category)
      fd.append('subject', formData.value.subject)
      fd.append('keywords', formData.value.keywords)
      
      // 2. 第一作者 & 通讯作者（后端必需字段）
      const firstAuthor = formData.value.authors.find(a => a.is_first)
      const correspondingAuthor = formData.value.authors.find(a => a.is_corresponding)
      fd.append('first_author', firstAuthor ? firstAuthor.name : '')
      fd.append('corresponding_author', correspondingAuthor ? correspondingAuthor.name : '')
      fd.append('order_of_authors', JSON.stringify(formData.value.authors.map((a, i) => ({ id: a.id, name: a.name, order: i + 1 }))))
      
      fd.append('cover_letter', formData.value.cover_letter)
      fd.append('comments', formData.value.comments)
      fd.append('publishing_option', formData.value.publishingOption)
      
      // 3. 附加复杂对象（对于 FastAPI 的 Form(...)，复杂结构需要转为 JSON 字符串）
      fd.append('authors', JSON.stringify(formData.value.authors))
      fd.append('funding', JSON.stringify(formData.value.funding))
      fd.append('additional_info', JSON.stringify(formData.value.additionalInfo))
      
      if (formData.value.structuredAbstract) {
        fd.append('structured_abstract', JSON.stringify(formData.value.structuredAbstract))
      }

      // 3. 附加文件对象
      if (formData.value.files && formData.value.files.length > 0) {
        formData.value.files.forEach(f => {
          if (f.fileObj) {
            fd.append('files', f.fileObj)
          }
        })
        // 传递文件元数据（如文件类型是 manuscript 还是 conflict），以便后端一一对应
        const fileMeta = formData.value.files.map(f => ({ name: f.name, type: f.type, description: f.description }))
        fd.append('files_meta', JSON.stringify(fileMeta))
      }

      // 4. 发起真实请求
      const response = await manuscriptApi.upload(fd)
      
      // 5. 提交成功后清理本地草稿和状态
      localStorage.removeItem('submission_draft')
      resetForm()
      
      // 返回后端真实的稿件 ID
      return response.id || response.manuscript_id
      
    } catch (error) {
      console.error('Submission failed:', error)
      throw error
    }
  }

  return {
    currentStep,
    steps,
    formData,
    init,
    saveDraft,
    validateCurrentStep,
    validateAllSteps,
    nextStep,
    prevStep,
    goToStep,
    submitManuscript
  }
})
