import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'

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
    articleType: '',
    
    // Step 2
    files: [], // { id, name, type, description, fileObj (raw), url }
    referenceAnonymization: {
      file: null,
      confirmed: false
    },
    
    // Step 3
    region: '',
    classifications: [],
    
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
    coverLetter: '',
    
    // Step 6
    title: '',
    abstract: '',
    keywords: '',
    authors: [], // { id, name, institution, email, isCorresponding, isFirst }
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
        isValid = !!formData.value.articleType
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
        isValid = !!formData.value.region && formData.value.classifications.length > 0
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
        isValid = !!formData.value.coverLetter
        break
      case 6:
        const hasAuthor = formData.value.authors.length > 0
        const hasCorresponding = formData.value.authors.some(a => a.isCorresponding)
        const hasFirst = formData.value.authors.some(a => a.isFirst)
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

  // 提交
  const submitManuscript = async () => {
    // 模拟提交
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const userStore = useUserStore()
        
        // 1. Generate Mock Manuscript ID
        const manuscriptId = 20260000 + Math.floor(Math.random() * 10000)
        
        // 2. Get Author Info
        const authorId = userStore.submissionUser?.id || userStore.user?.id || 999
        const authorName = userStore.submissionUser?.username || userStore.user?.username || (formData.value.authors[0]?.name || 'Unknown Author')
        const title = formData.value.title ? formData.value.title.replace(/<[^>]*>/g, '').trim() : 'Untitled Manuscript'

        // 2.5 Create and Save Journal Entry (Fix: Ensure manuscript is added to main list)
        const newJournal = {
            id: manuscriptId,
            title: title,
            author: authorName,
            module: formData.value.classifications?.[0] || 'Others',
            status: 'pending_initial_review',
            submissionDate: new Date().toISOString().split('T')[0],
            abstract: formData.value.abstract ? formData.value.abstract.replace(/<[^>]*>/g, '').trim() : '',
            keywords: formData.value.keywords || '',
            fileUrl: '/vite.svg',
            reviews: []
        }
        userStore.addJournal(newJournal)

        // 3. Process Recommended Reviewers
        const recommended = formData.value.additionalInfo.recommendedReviewers || []
        if (recommended.length > 0) {
            // Ensure recommendedReviewers array exists in store (it should based on init)
            if (!userStore.recommendedReviewers) userStore.recommendedReviewers = []
            
            recommended.forEach((reviewer, index) => {
                const newRec = {
                    id: Date.now() + index,
                    manuscriptId: manuscriptId,
                    manuscriptTitle: title,
                    authorId: authorId,
                    authorName: authorName,
                    reviewerName: reviewer.name,
                    reviewerEmail: reviewer.email,
                    reviewerAffiliation: reviewer.institution || reviewer.affiliation || 'N/A', 
                    reviewerExpertise: ['Unknown'], 
                    recommendationReason: reviewer.reason,
                    status: 'pending',
                    recommendedAt: new Date().toISOString(),
                    reviewedAt: null,
                    reviewedBy: null,
                    submissionCount: 1, 
                    avgScore: 0,
                    riskLevel: 'low', 
                    evalStatus: 'pending'
                }
                userStore.recommendedReviewers.unshift(newRec)
            })
            // Persist to localStorage
            localStorage.setItem('recommendedReviewers', JSON.stringify(userStore.recommendedReviewers))
        }

        // 4. Process Opposed Reviewers
        const opposed = formData.value.additionalInfo.avoidedReviewers || []
        if (opposed.length > 0) {
            if (!userStore.opposedReviewers) userStore.opposedReviewers = []

            opposed.forEach((reviewer, index) => {
                const newOpp = {
                    id: Date.now() + index + 100,
                    manuscriptId: manuscriptId,
                    manuscriptTitle: title,
                    authorId: authorId,
                    authorName: authorName,
                    opposedReviewerName: reviewer.name,
                    opposedReviewerAffiliation: reviewer.institution || reviewer.affiliation || 'N/A',
                    reasonType: reviewer.reasonType || 'Other',
                    opposedReason: reviewer.reason,
                    status: 'pending',
                    requestedAt: new Date().toISOString(),
                    handledAt: null,
                    handledBy: null
                }
                 userStore.opposedReviewers.unshift(newOpp)
            })
            localStorage.setItem('opposedReviewers', JSON.stringify(userStore.opposedReviewers))
        }
        
        // 5. Add System Log
        userStore.addSystemLog({
            type: 'operation',
            user: authorName,
            action: 'Submit Manuscript',
            target: `Manuscript ID: ${manuscriptId}`,
            ip: '127.0.0.1'
        })

        // 清除草稿 (Journal Platform Standard Cleanup)
        localStorage.removeItem('submission_draft')
        
        // Reset Store State (Pure Frontend Cleanup)
        currentStep.value = 1
        steps.value.forEach(s => s.status = s.id === 1 ? 'current' : 'pending')
        formData.value = {
            articleType: '',
            files: [],
            referenceAnonymization: { file: null, confirmed: false },
            region: '',
            classifications: [],
            additionalInfo: {
                q1: '', q2: '', q3: '', q4: '', q5: '', q6: '',
                ssrn: false, socialMedia: '', conference: 'No',
                recommendedReviewers: [],
                avoidedReviewers: [],
                blindReview: { enabled: true, confirmed: false }
            },
            coverLetter: '',
            title: '',
            abstract: '',
            keywords: '',
            authors: [],
            funding: [],
            noFunding: false,
            publishingOption: ''
        }
        
        resolve(manuscriptId)
      }, 1500)
    })
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
