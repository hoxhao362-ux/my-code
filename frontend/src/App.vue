<script setup>
import { ref, computed, watch } from 'vue'

// 导入所有组件
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Home from './components/Home.vue'
import Submit from './components/Submit.vue'
import Review from './components/Review.vue'
import Profile from './components/Profile.vue'
import JournalDetail from './components/JournalDetail.vue'

// 应用状态管理
const currentPage = ref('login') // 当前页面
const user = ref(JSON.parse(localStorage.getItem('user')) || null) // 当前用户
const journalId = ref(null) // 当前查看的稿件ID
// 管理员辨识密码，默认值为'admin123'，存储在localStorage中
const adminCode = ref(localStorage.getItem('adminCode') || 'admin123')
// 目录状态
const showDirectory = ref(false)
// 目录相关状态
const sortBy = ref('date') // 'date' 或 'viewCount'
const timeRange = ref('all') // 'all', 'today', 'week', 'month', 'year'
const selectedModule = ref('all') // 'all' 或具体模块名称
const filteredJournals = ref([])

// 在线阅读相关状态
const selectedJournal = ref(null)
const showJournalContent = ref(false)

// 期刊数据管理
let initialJournals = [
  { 
    id: 1, 
    title: '基于深度学习的医学图像分析', 
    author: '张三', 
    date: '2024-01-01', 
    status: '已通过',
    abstract: '本文探讨了深度学习在医学图像分析中的应用，包括图像分类、目标检测和分割等技术，并通过实验验证了其有效性。',
    keywords: ['深度学习', '医学图像', '图像分析'],
    module: '医学影像',
    content: '<h3>摘要</h3><p>本文探讨了深度学习在医学图像分析中的应用，包括图像分类、目标检测和分割等技术，并通过实验验证了其有效性。</p><h3>引言</h3><p>医学图像分析是医学领域的重要研究方向，随着深度学习技术的发展，其在医学图像分析中的应用越来越广泛。</p><h3>方法</h3><p>本文采用卷积神经网络（CNN）进行医学图像分析，包括数据预处理、模型训练和评估等步骤。</p><h3>结果</h3><p>实验结果表明，深度学习方法在医学图像分析中取得了良好的效果，准确率达到了95%以上。</p><h3>结论</h3><p>深度学习技术在医学图像分析中具有广阔的应用前景，未来可以进一步提高模型的性能和泛化能力。</p>',
    viewCount: 0
  },
  { 
    id: 2, 
    title: '新型药物研发进展', 
    author: '李四', 
    date: '2024-01-02', 
    status: '已通过',
    abstract: '本文综述了近年来新型药物研发的进展，包括小分子药物、生物药物和基因治疗等领域，并展望了未来的发展方向。',
    keywords: ['药物研发', '小分子药物', '生物药物', '基因治疗'],
    module: '药物研发',
    content: '<h3>摘要</h3><p>本文综述了近年来新型药物研发的进展，包括小分子药物、生物药物和基因治疗等领域，并展望了未来的发展方向。</p><h3>引言</h3><p>药物研发是医药行业的核心环节，随着科学技术的发展，新型药物不断涌现，为疾病治疗提供了更多选择。</p><h3>小分子药物</h3><p>小分子药物是传统的药物类型，具有分子量小、易于合成和口服给药等优点，近年来在靶点发现和药物设计方面取得了重要进展。</p><h3>生物药物</h3><p>生物药物包括抗体药物、蛋白质药物和核酸药物等，具有特异性强、疗效好等优点，是当前药物研发的热点领域。</p><h3>基因治疗</h3><p>基因治疗是一种新兴的治疗方法，通过修复或替换缺陷基因来治疗疾病，具有广阔的应用前景。</p><h3>结论</h3><p>新型药物研发的进展为疾病治疗带来了新的希望，未来需要进一步加强基础研究和临床转化，推动药物研发的发展。</p>',
    viewCount: 0
  },
  { 
    id: 3, 
    title: '临床研究方法学探讨', 
    author: '王五', 
    date: '2024-01-03', 
    status: '已通过',
    abstract: '本文系统介绍了临床研究的基本方法和设计原则，包括随机对照试验、队列研究、病例对照研究等，并讨论了临床研究中的伦理问题。',
    keywords: ['临床研究', '方法学', '随机对照试验', '伦理'],
    module: '临床研究',
    content: '<h3>摘要</h3><p>本文系统介绍了临床研究的基本方法和设计原则，包括随机对照试验、队列研究、病例对照研究等，并讨论了临床研究中的伦理问题。</p><h3>引言</h3><p>临床研究是验证药物和治疗方法有效性和安全性的重要手段，其方法学的科学性直接影响研究结果的可靠性。</p><h3>临床研究设计</h3><p>临床研究设计包括研究类型、样本量计算、随机化方法、盲法设计等，不同的研究设计适用于不同的研究目的。</p><h3>随机对照试验</h3><p>随机对照试验是临床研究的金标准，通过随机分组和盲法设计，减少偏倚，提高研究结果的可靠性。</p><h3>队列研究</h3><p>队列研究是一种观察性研究方法，通过随访暴露组和非暴露组，观察疾病的发生情况，用于研究病因和预后。</p><h3>病例对照研究</h3><p>病例对照研究是一种回顾性研究方法，通过比较病例组和对照组的暴露情况，探讨疾病的危险因素。</p><h3>伦理问题</h3><p>临床研究中的伦理问题包括知情同意、隐私保护、风险受益比等，需要严格遵循伦理原则。</p><h3>结论</h3><p>临床研究方法学的不断完善和发展，为提高临床研究质量和推动医学进步提供了重要保障。</p>',
    viewCount: 0
  },
  { 
    id: 4, 
    title: '公共卫生政策分析', 
    author: '赵六', 
    date: '2024-01-04', 
    status: '审稿中',
    abstract: '本文分析了当前公共卫生政策的现状和存在的问题，并提出了相应的改进建议，旨在提高公共卫生服务的质量和可及性。',
    keywords: ['公共卫生', '政策分析', '卫生服务', '改进建议'],
    module: '公共卫生',
    content: '<h3>摘要</h3><p>本文分析了当前公共卫生政策的现状和存在的问题，并提出了相应的改进建议，旨在提高公共卫生服务的质量和可及性。</p><h3>引言</h3><p>公共卫生政策是保障公众健康的重要手段，其制定和实施直接影响公共卫生服务的质量和效果。</p><h3>公共卫生政策现状</h3><p>当前公共卫生政策在疾病预防控制、卫生监督、健康教育等方面取得了一定成绩，但仍存在一些问题，如政策执行不到位、资源分配不均等。</p><h3>存在的问题</h3><p>公共卫生政策存在的问题包括政策制定缺乏科学性、政策执行机制不完善、公众参与度不高等。</p><h3>改进建议</h3><p>针对存在的问题，提出了加强政策科学性、完善执行机制、提高公众参与度等改进建议。</p><h3>结论</h3><p>公共卫生政策的不断完善和优化，对于提高公共卫生服务质量、保障公众健康具有重要意义。</p>',
    viewCount: 0
  },
  { 
    id: 5, 
    title: '生物信息学在医学研究中的应用', 
    author: '孙七', 
    date: '2024-01-05', 
    status: '未通过',
    abstract: '本文介绍了生物信息学在医学研究中的应用，包括基因组学、蛋白质组学和代谢组学等领域，并讨论了其在疾病诊断和治疗中的潜力。',
    keywords: ['生物信息学', '基因组学', '蛋白质组学', '代谢组学', '疾病诊断'],
    module: '生物信息学',
    content: '<h3>摘要</h3><p>本文介绍了生物信息学在医学研究中的应用，包括基因组学、蛋白质组学和代谢组学等领域，并讨论了其在疾病诊断和治疗中的潜力。</p><h3>引言</h3><p>生物信息学是一门新兴的交叉学科，通过整合生物学、计算机科学和统计学等知识，分析和解读生物数据，为医学研究提供了新的方法和思路。</p><h3>基因组学应用</h3><p>基因组学研究通过分析基因组序列，揭示疾病的遗传基础，为个性化医疗提供了基础。</p><h3>蛋白质组学应用</h3><p>蛋白质组学研究通过分析蛋白质的表达和功能，探讨疾病的发病机制，为药物研发提供了靶点。</p><h3>代谢组学应用</h3><p>代谢组学研究通过分析代谢物的变化，监测疾病的进展和治疗效果，为临床诊断提供了新的 biomarkers。</p><h3>结论</h3><p>生物信息学在医学研究中的应用前景广阔，未来将在疾病诊断、治疗和预防等方面发挥越来越重要的作用。</p>',
    viewCount: 0
  },
  { 
    id: 6, 
    title: '人工智能在医疗领域的应用现状与挑战', 
    author: '周八', 
    date: '2024-01-06', 
    status: '审稿中',
    abstract: '本文综述了人工智能在医疗领域的应用现状，包括医学影像分析、辅助诊断、药物研发等方面，并分析了其面临的挑战和未来发展方向。',
    keywords: ['人工智能', '医疗领域', '医学影像', '辅助诊断', '药物研发'],
    module: '人工智能',
    content: '<h3>摘要</h3><p>本文综述了人工智能在医疗领域的应用现状，包括医学影像分析、辅助诊断、药物研发等方面，并分析了其面临的挑战和未来发展方向。</p><h3>引言</h3><p>人工智能技术的快速发展为医疗领域带来了新的机遇和挑战，其在医学影像分析、辅助诊断、药物研发等方面的应用不断深入。</p><h3>医学影像分析</h3><p>人工智能在医学影像分析中的应用包括图像分类、目标检测和分割等，能够提高诊断效率和准确性。</p><h3>辅助诊断</h3><p>人工智能辅助诊断系统通过分析患者的临床数据和影像资料，提供诊断建议，有助于提高诊断的准确性和一致性。</p><h3>药物研发</h3><p>人工智能在药物研发中的应用包括靶点发现、药物设计和临床试验优化等，能够缩短药物研发周期，降低研发成本。</p><h3>挑战与展望</h3><p>人工智能在医疗领域的应用面临着数据质量、算法可解释性、伦理和法律等挑战，未来需要加强跨学科合作，推动人工智能技术在医疗领域的健康发展。</p><h3>结论</h3><p>人工智能技术在医疗领域的应用前景广阔，将为医疗行业带来革命性的变化，但需要克服一系列挑战，确保其安全、有效和可持续发展。</p>',
    viewCount: 0
  }
]

// 为当前用户添加10篇虚拟投稿
const addVirtualJournals = () => {
  const virtualJournals = [
    { 
      id: 1001, 
      title: '基于机器学习的疾病预测模型研究', 
      author: 'admin', 
      date: '2025-12-30', 
      status: '已通过',
      abstract: '本文研究了基于机器学习的疾病预测模型，通过分析大量医疗数据，实现了对多种疾病的准确预测。',
      keywords: ['机器学习', '疾病预测', '医疗数据'],
      module: '医学影像',
      content: '<h3>摘要</h3><p>本文研究了基于机器学习的疾病预测模型...</p>',
      viewCount: 15
    },
    { 
      id: 1002, 
      title: '新型冠状病毒疫苗研发进展', 
      author: 'admin', 
      date: '2025-12-28', 
      status: '已通过',
      abstract: '本文综述了新型冠状病毒疫苗的研发进展，包括不同技术路线的疫苗特点和临床试验结果。',
      keywords: ['冠状病毒', '疫苗研发', '临床试验'],
      module: '药物研发',
      content: '<h3>摘要</h3><p>本文综述了新型冠状病毒疫苗的研发进展...</p>',
      viewCount: 23
    },
    { 
      id: 1003, 
      title: '临床路径管理在医院中的应用研究', 
      author: 'admin', 
      date: '2025-12-25', 
      status: '审稿中',
      abstract: '本文探讨了临床路径管理在医院中的应用，分析了其对医疗质量和效率的影响。',
      keywords: ['临床路径', '医院管理', '医疗质量'],
      module: '临床研究',
      content: '<h3>摘要</h3><p>本文探讨了临床路径管理在医院中的应用...</p>',
      viewCount: 8
    },
    { 
      id: 1004, 
      title: '公共卫生应急管理体系建设', 
      author: 'admin', 
      date: '2025-12-20', 
      status: '已通过',
      abstract: '本文分析了公共卫生应急管理体系的建设现状和存在的问题，并提出了相应的改进建议。',
      keywords: ['公共卫生', '应急管理', '体系建设'],
      module: '公共卫生',
      content: '<h3>摘要</h3><p>本文分析了公共卫生应急管理体系的建设现状...</p>',
      viewCount: 12
    },
    { 
      id: 1005, 
      title: '基因组学数据分析方法研究', 
      author: 'admin', 
      date: '2025-12-15', 
      status: '未通过',
      abstract: '本文研究了基因组学数据的分析方法，包括序列比对、变异检测和功能注释等。',
      keywords: ['基因组学', '数据分析', '序列比对'],
      module: '生物信息学',
      content: '<h3>摘要</h3><p>本文研究了基因组学数据的分析方法...</p>',
      viewCount: 5
    },
    { 
      id: 1006, 
      title: '人工智能辅助诊断系统的设计与实现', 
      author: 'admin', 
      date: '2025-12-10', 
      status: '已通过',
      abstract: '本文设计并实现了一个人工智能辅助诊断系统，用于帮助医生提高诊断准确性和效率。',
      keywords: ['人工智能', '辅助诊断', '系统设计'],
      module: '人工智能',
      content: '<h3>摘要</h3><p>本文设计并实现了一个人工智能辅助诊断系统...</p>',
      viewCount: 31
    },
    { 
      id: 1007, 
      title: '医学图像处理技术研究进展', 
      author: 'admin', 
      date: '2025-11-30', 
      status: '已通过',
      abstract: '本文综述了医学图像处理技术的研究进展，包括图像分割、配准和三维重建等。',
      keywords: ['医学图像', '图像处理', '图像分割'],
      module: '医学影像',
      content: '<h3>摘要</h3><p>本文综述了医学图像处理技术的研究进展...</p>',
      viewCount: 20
    },
    { 
      id: 1008, 
      title: '药物临床试验设计与统计分析', 
      author: 'admin', 
      date: '2025-11-25', 
      status: '审稿中',
      abstract: '本文介绍了药物临床试验的设计原则和统计分析方法，包括样本量计算和随机化设计等。',
      keywords: ['临床试验', '统计分析', '样本量计算'],
      module: '药物研发',
      content: '<h3>摘要</h3><p>本文介绍了药物临床试验的设计原则...</p>',
      viewCount: 14
    },
    { 
      id: 1009, 
      title: '循证医学在临床实践中的应用', 
      author: 'admin', 
      date: '2025-11-20', 
      status: '已通过',
      abstract: '本文探讨了循证医学在临床实践中的应用，强调了基于证据的医疗决策的重要性。',
      keywords: ['循证医学', '临床实践', '医疗决策'],
      module: '临床研究',
      content: '<h3>摘要</h3><p>本文探讨了循证医学在临床实践中的应用...</p>',
      viewCount: 18
    },
    { 
      id: 1010, 
      title: '健康管理系统的设计与实现', 
      author: 'admin', 
      date: '2025-11-15', 
      status: '已通过',
      abstract: '本文设计并实现了一个健康管理系统，用于帮助用户跟踪健康数据和制定健康计划。',
      keywords: ['健康管理', '系统设计', '健康数据'],
      module: '其他',
      content: '<h3>摘要</h3><p>本文设计并实现了一个健康管理系统...</p>',
      viewCount: 25
    }
  ]
  
  return [...initialJournals, ...virtualJournals]
}

// 从localStorage获取数据，只在数据足够时使用，否则使用初始数据 + 虚拟投稿
const storedJournals = JSON.parse(localStorage.getItem('journals'))
const journals = ref(storedJournals && storedJournals.length > 3 ? storedJournals : addVirtualJournals())

// 模块管理
const modules = ref(JSON.parse(localStorage.getItem('modules')) || [
  '医学影像',
  '药物研发',
  '临床研究',
  '公共卫生',
  '生物信息学',
  '人工智能',
  '其他'
])

// 页面导航方法
const navigateTo = (page, id = null) => {
  currentPage.value = page
  if (id) {
    journalId.value = id
  }
}

// 切换目录显示
const toggleDirectory = () => {
  showDirectory.value = !showDirectory.value
}

// 在线阅读期刊
const readJournal = (journal) => {
  selectedJournal.value = journal
  showJournalContent.value = true
  showDirectory.value = false // 关闭目录
}

// 关闭在线阅读
const closeJournalContent = () => {
  showJournalContent.value = false
  selectedJournal.value = null
}

// 目录相关状态
const selectedStatus = ref('all') // 'all', '已通过', '未通过', '审稿中' 

// 过滤和排序期刊
const filterAndSortJournals = () => {
  let result = [...journals.value]
  
  // 状态筛选
  if (selectedStatus.value !== 'all') {
    result = result.filter(journal => journal.status === selectedStatus.value)
  }
  
  // 模块筛选
  if (selectedModule.value !== 'all') {
    result = result.filter(journal => journal.module === selectedModule.value)
  }
  
  // 时间范围筛选
  const now = new Date()
  let startDate
  switch (timeRange.value) {
    case 'today':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      break
    case 'week':
      startDate = new Date(now.setDate(now.getDate() - 7))
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
      break
    case 'year':
      startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
      break
    default:
      startDate = null
  }
  
  if (startDate) {
    result = result.filter(journal => new Date(journal.date) >= startDate)
  }
  
  // 排序
  if (sortBy.value === 'date') {
    result.sort((a, b) => new Date(b.date) - new Date(a.date))
  } else {
    result.sort((a, b) => b.viewCount - a.viewCount)
  }
  
  filteredJournals.value = result
}

// 监听相关状态变化，重新过滤和排序
watch([sortBy, timeRange, selectedModule, selectedStatus, journals], () => {
  filterAndSortJournals()
}, { immediate: true, deep: true })

// 登录方法
const login = (userData) => {
  user.value = userData
  localStorage.setItem('user', JSON.stringify(userData))
  navigateTo('home')
}

// 更新用户信息方法
const updateUser = (userData) => {
  user.value = userData
  localStorage.setItem('user', JSON.stringify(userData))
}

// 登出方法
const logout = () => {
  user.value = null
  localStorage.removeItem('user')
  navigateTo('login')
}

// 更新管理员辨识密码的方法
const updateAdminCode = (newCode) => {
  adminCode.value = newCode
  localStorage.setItem('adminCode', newCode)
}

// 期刊管理方法
const updateJournals = (newJournals) => {
  journals.value = newJournals
  localStorage.setItem('journals', JSON.stringify(newJournals))
}

const addJournal = (journal) => {
  journals.value.push(journal)
  localStorage.setItem('journals', JSON.stringify(journals.value))
}

// 增加期刊阅读量
const incrementJournalView = (id) => {
  const journal = journals.value.find(j => j.id === id)
  if (journal) {
    journal.viewCount += 1
    localStorage.setItem('journals', JSON.stringify(journals.value))
  }
}

// 模块管理方法
const updateModules = (newModules) => {
  modules.value = newModules
  localStorage.setItem('modules', JSON.stringify(newModules))
}

const addModule = (moduleName) => {
  if (!modules.value.includes(moduleName)) {
    modules.value.push(moduleName)
    localStorage.setItem('modules', JSON.stringify(modules.value))
  }
}

const removeModule = (moduleName) => {
  if (moduleName !== '其他') { // 不能删除'其他'模块
    modules.value = modules.value.filter(m => m !== moduleName)
    localStorage.setItem('modules', JSON.stringify(modules.value))
    // 将使用该模块的期刊转移到'其他'模块
    journals.value.forEach(journal => {
      if (journal.module === moduleName) {
        journal.module = '其他'
      }
    })
    localStorage.setItem('journals', JSON.stringify(journals.value))
  }
}

// 计算当前应该显示的组件
const CurrentComponent = computed(() => {
  switch (currentPage.value) {
    case 'login': return Login
    case 'register': return Register
    case 'home': return Home
    case 'submit': return Submit
    case 'review': return Review
    case 'profile': return Profile
    case 'journal': return JournalDetail
    default: return Login
  }
})

// 提供给子组件使用的方法和状态
const appContext = computed(() => {
  return {
    user: user.value,
    currentPage: currentPage.value,
    journalId: journalId.value,
    journals: journals.value,
    modules: modules.value,
    adminCode: adminCode.value,
    showDirectory: showDirectory.value,
    updateAdminCode,
    updateUser,
    updateJournals,
    addJournal,
    incrementJournalView,
    updateModules,
    addModule,
    removeModule,
    toggleDirectory,
    navigateTo,
    login,
    logout
  }
})
</script>

<template>
  <div class="app-container">
    <!-- 使用动态组件渲染当前页面 -->
    <component 
      :is="CurrentComponent" 
      v-bind="appContext"
    />
    
    <!-- 全局目录功能 -->
    <section v-if="showDirectory" class="directory-section">
      <div class="directory-container">
        <div class="directory-header">
          <h2 class="section-title">期刊目录</h2>
          <button class="close-btn" @click="toggleDirectory">×</button>
        </div>
        
        <!-- 筛选和排序控件 -->
<div class="filters-container">
  <div class="filter-group">
    <label for="status-filter">状态筛选：</label>
    <select 
      id="status-filter" 
      v-model="selectedStatus"
      class="filter-select"
    >
      <option value="all">全部状态</option>
      <option value="已通过">已通过</option>
      <option value="审稿中">审稿中</option>
      <option value="未通过">未通过</option>
    </select>
  </div>
  
  <div class="filter-group">
    <label for="module-filter">模块筛选：</label>
    <select 
      id="module-filter" 
      v-model="selectedModule"
      class="filter-select"
    >
      <option value="all">全部模块</option>
      <option 
        v-for="module in modules" 
        :key="module"
        :value="module"
      >
        {{ module }}
      </option>
    </select>
  </div>
  
  <div class="filter-group">
    <label for="time-filter">时间范围：</label>
    <select 
      id="time-filter" 
      v-model="timeRange"
      class="filter-select"
    >
      <option value="all">全部时间</option>
      <option value="today">今日</option>
      <option value="week">本周</option>
      <option value="month">本月</option>
      <option value="year">本年</option>
    </select>
  </div>
  
  <div class="filter-group">
    <label for="sort-filter">排序方式：</label>
    <select 
      id="sort-filter" 
      v-model="sortBy"
      class="filter-select"
    >
      <option value="date">按时间排序</option>
      <option value="viewCount">按阅读量排序</option>
    </select>
  </div>
</div>
        
        <!-- 期刊列表 -->
        <div class="journals-directory">
          <div 
  v-for="journal in filteredJournals" 
  :key="journal.id" 
  class="journal-directory-item"
>
  <div class="journal-directory-info">
    <h3 class="journal-directory-title" @click="() => { incrementJournalView(journal.id); navigateTo('journal', journal.id); }">
      {{ journal.title }}
    </h3>
    <p class="journal-directory-meta">
  作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }} | 状态：
  <span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span> | 阅读量：{{ journal.viewCount }}
</p>
    <p class="journal-directory-abstract">{{ journal.abstract }}</p>
    <div class="journal-directory-keywords">
      <span 
        v-for="(keyword, index) in journal.keywords" 
        :key="index" 
        class="keyword-tag"
      >
        {{ keyword }}
      </span>
    </div>
  </div>
  <div class="journal-directory-actions">
    <button class="action-btn read-btn" @click="readJournal(journal)">
      在线阅读
    </button>
    <button class="action-btn detail-btn" @click="() => { incrementJournalView(journal.id); navigateTo('journal', journal.id); }">
      查看详情
    </button>
  </div>
</div>
          
          <div v-if="filteredJournals.length === 0" class="no-journals">
            <p>暂无符合条件的期刊</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 在线阅读内容 -->
    <section v-if="showJournalContent && selectedJournal" class="journal-content-section">
      <div class="journal-content-container">
        <div class="journal-content-header">
          <h2 class="section-title">{{ selectedJournal.title }}</h2>
          <button class="close-btn" @click="closeJournalContent">×</button>
        </div>
        <div class="journal-content-meta">
          <p>作者：{{ selectedJournal.author }} | 投稿日期：{{ selectedJournal.date }} | 模块：{{ selectedJournal.module }} | 阅读量：{{ selectedJournal.viewCount }}</p>
          <div class="journal-content-keywords">
            <span 
              v-for="(keyword, index) in selectedJournal.keywords" 
              :key="index" 
              class="keyword-tag"
            >
              {{ keyword }}
            </span>
          </div>
        </div>
        <div class="journal-content-body" v-html="selectedJournal.content"></div>
      </div>
    </section>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  line-height: 1.6;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 全局目录样式 */
.directory-section {
  position: fixed;
  top: 0;
  right: 0;
  width: 100%;
  max-width: 800px;
  height: 100vh;
  background: white;
  box-shadow: -5px 0 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow-y: auto;
  padding: 2rem;
}

.directory-container {
  max-width: 100%;
}

.directory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.directory-header .section-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.directory-header .close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.directory-header .close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eee;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.journals-directory {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.journal-directory-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #eee;
  transition: all 0.3s ease;
}

.journal-directory-item:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.journal-directory-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.75rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-directory-title:hover {
  color: #3498db;
}

.journal-directory-meta {
  font-size: 0.85rem;
  color: #777;
  margin: 0 0 0.75rem 0;
}

.journal-directory-abstract {
  font-size: 0.9rem;
  color: #555;
  margin: 0 0 0.75rem 0;
  line-height: 1.5;
}

.journal-directory-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.no-journals {
  text-align: center;
  padding: 3rem;
  color: #999;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
}

/* 滚动条样式 */
.directory-section::-webkit-scrollbar {
  width: 8px;
}

.directory-section::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.directory-section::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.directory-section::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 半透明背景遮罩 */
.directory-section::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 800px;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: -1;
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .directory-section {
    max-width: 100%;
  }
  
  .directory-section::before {
    display: none;
  }
  
  .filters-container {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
}

/* 期刊状态样式 */
.journal-status {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  display: inline-block;
  margin: 0 0.25rem;
}

.journal-status.已通过 {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.journal-status.审稿中 {
  background: #cce7ff;
  color: #004085;
  border: 1px solid #b3d7ff;
}

.journal-status.未通过 {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 目录期刊项操作按钮样式 */
.journal-directory-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.read-btn {
  background: #3498db;
  color: white;
}

.read-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.detail-btn {
  background: #2ecc71;
  color: white;
}

.detail-btn:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

/* 在线阅读内容样式 */
.journal-content-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 1001;
  overflow-y: auto;
  padding: 2rem;
}

.journal-content-container {
  max-width: 800px;
  margin: 0 auto;
}

.journal-content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.journal-content-header .section-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.journal-content-header .close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.journal-content-header .close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.journal-content-meta {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eee;
}

.journal-content-meta p {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 0.9rem;
}

.journal-content-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.journal-content-body {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #eee;
  line-height: 1.8;
  color: #333;
}

.journal-content-body h1, .journal-content-body h2, .journal-content-body h3, .journal-content-body h4 {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.journal-content-body p {
  margin-bottom: 1rem;
  text-align: justify;
}

.journal-content-body ul, .journal-content-body ol {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.journal-content-body li {
  margin-bottom: 0.5rem;
}
</style>