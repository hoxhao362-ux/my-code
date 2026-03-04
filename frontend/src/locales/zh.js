export default {
  common: {
    back: '返回',
    next: '下一步',
    proceed: '继续',
    select: '请选择...',
    saveLater: '暂存 & 稍后提交',
    cancel: '取消',
    submit: '提交',
    required: '必填',
    optional: '选填',
    delete: '删除',
    edit: '编辑',
    confirm: '确认',
    close: '关闭',
    add: '添加',
    remove: '移除',
    download: '下载',
    preview: '预览',
    loading: '加载中...',
    success: '成功',
    error: '错误',
    warning: '警告',
    switchLang: 'Switch to English'
  },
  progress: {
    step1: '文章类型',
    step2: '上传文件',
    step3: '基本信息',
    step4: '补充信息',
    step5: '附言',
    step6: '稿件数据',
  },
  articleTypeSelection: {
    title: '文章类型选择',
    label: '文章类型',
    placeholder: '请选择文章类型',
    types: {
      invited: '特邀论文',
      correspondence: '通信',
      comments: '评论',
      clinical: '临床巡查',
      original: '原创研究',
      review: '综述文章'
    },
    guidelinesTitle: '选定类型的投稿指南',
    guidelines: {
      general: '投稿指南',
      wordCount: '字数限制',
      references: '参考文献数量要求',
    },
    errors: {
      required: '请选择文章类型',
    },
  },
  attachFiles: {
    title: '上传文件',
    dragDrop: '拖拽文件至此，或点击浏览上传',
    browse: '浏览',
    bulkUpdate: '批量更新文件类型',
    fileType: '文件类型',
    fileName: '文件名',
    description: '描述',
    actions: '操作',
    types: {
      manuscript: '稿件正文',
      contribution: '撰稿人贡献声明',
      conflict: '利益冲突声明',
      figure: '图表',
      table: '表格',
      supplementary: '补充材料'
    },
    placeholders: {
      description: '输入自定义文件描述（选填）',
      selectType: '选择类型'
    },
    confirmDelete: '确定要删除此文件吗？此操作无法撤销。',
    errors: {
      noFile: '请至少上传一个稿件相关文件',
    },
    requiredFiles: {
      title: '核心必交文件',
      description: '以下文件为投稿必交文件，请确保每种类型至少上传一份文件。',
      descriptions: {
        manuscript: '包含标题、摘要、正文、参考文献、表格（可嵌入正文或单独上传），是投稿的核心文件，必须提交。',
        contribution: '按 ICMJE 规范明确每位撰稿人的具体贡献，是学术诚信的重要组成部分，必须提交。',
        conflict: '披露所有潜在的竞争利益，确保研究的客观性，必须提交。'
      },
      missingWarning: '缺少必交文件：',
      missingError: '请上传所有必交文件：稿件正文、撰稿人贡献声明和利益冲突声明。',
      allUploaded: '所有必交文件已上传完成。'
    }
  },
  generalInformation: {
    title: '基本信息',
    regionLabel: '稿件来源地区',
    regionPlaceholder: '选择地区',
    classificationsLabel: '医学专业分类',
    addClassification: '添加分类',
    selectedClassifications: '已选分类',
    popupTitle: '分类选择',
    searchPlaceholder: '搜索分类...',
    noResults: '未找到结果',
    errors: {
      regionRequired: '请选择稿件来源地区',
      classificationRequired: '请至少选择一个医学专业分类',
    },
  },
  additionalInformation: {
    title: '补充信息',
    questions: {
      q1: '确认数据访问和提交责任',
      q2: '所有撰稿人是否已审阅并同意提交？',
      q3: '是否有医学写作人/编辑参与，并提供相关资助信息',
      q4: '哪些撰稿人访问并验证了研究数据，谁负责提交决定？',
      q5: '是否使用了生成式 AI，请说明具体用途',
      q6: '提供稿件字数、参考文献数量和图表数量',
    },
    ssrn: '同意在 SSRN 预印本平台上发布研究文章',
    socialMedia: "通讯撰稿人的社交媒体账号",
    conference: '未来会议同期提交确认',
    errors: {
      incomplete: '请完成所有补充信息问卷',
      limitExceeded: '输入超过字符限制，请缩短内容',
    },
  },
  comments: {
    title: '附言',
    coverLetter: '投稿信（给期刊的说明，内容不会在最终稿件中显示）',
    placeholder: '请输入给期刊的说明，如稿件亮点、投稿说明等。',
    errors: {
      required: '请输入给期刊的投稿信',
    },
  },
  manuscriptData: {
    title: '稿件数据',
    manuscriptTitle: '标题（稿件标题）',
    abstract: '摘要',
    keywords: '关键词',
    keywordsPlaceholder: '请输入关键词，多个关键词用分号分隔',
    authors: {
      title: '作者',
      add: '添加作者',
      name: '姓名',
      institution: '机构',
      email: '邮箱',
      corresponding: '通讯作者',
      first: '第一作者',
    },
    funding: {
      title: '资助信息',
      add: '添加资助来源',
      noFunding: '无资助信息',
      body: '资助机构',
      selectBody: '选择资助机构',
      number: '项目编号',
    },
    buildPDF: '生成 PDF 用于审批',
    previewTitle: 'PDF 预览',
    publishingOption: {
      title: '出版选项',
      subscription: '订阅（订阅模式）',
      openAccess: '开放获取（开放获取模式）',
    },
    errors: {
      incomplete: '请完成所有必填项',
      noAuthor: '请至少添加一位作者',
      noCorresponding: '请选择通讯作者',
      noFirst: '请选择第一作者',
      noFunding: '请添加资助信息或选择"无资助信息"',
    },
    successMessage: '投稿已成功提交。请等待期刊初审',
  },
  submissionRules: {
    title: '投稿指南',
    intro: '提交前请仔细阅读以下指南...',
    format: '格式',
    formatDesc: 'PDF, Word, 或 LaTeX。',
    authors: '作者',
    authorsDesc: '确保列出所有作者并经其批准。',
    originality: '原创性',
    originalityDesc: '内容必须是原创的。',
    start: '开始投稿'
  },
  nav: {
    logo: '期刊投稿平台',
    home: '首页',
    directory: '目录',
    submissionCenter: '投稿中心',
    submissionRules: '投稿须知',
    onlineSubmission: '在线投稿',
    profile: '个人中心',
    profileInfo: '个人信息',
    accountSecurity: '账号安全',
    messages: '消息通知',
    operationLogs: '操作记录',
    manuscriptStatus: '稿件状态查询',
    feedbackManagement: '意见收纳',
    helpCenter: '帮助中心',
    faq: '常见问题',
    contact: '联系我们',
    feedback: '意见反馈',
    adminLogin: '登录后台',
    logout: '退出登录',
    login: '登录',
    readOnly: '只读',
    readOnlyMode: '只读模式',
    submitSystem: '投稿系统',
    userRole: '用户角色',
    register: '注册',
    dashboard: '后台主页',
    roleSwitch: '角色切换',
    roles: {
      admin: '编辑工作台',
      associate_editor: '副编辑工作台',
      ea_ae: '助理/顾问编辑工作台',
      reviewer: '审核员工作台',
      author: '投稿人工作台'
    },
    tasks: '审核任务',
    history: '审核记录',
    returnMain: '返回主站',
    roleManagement: '角色管理',
    userList: '用户列表',
    reviewerManagement: '审核员管理',
    auditReviewerManagement: '评审人管理',
    auditRecommendedReviewers: '推荐评审人',
    auditOpposedReviewers: '回避评审人',
    auditMyTasks: '我的任务',
    accountStatus: '账号状态',
    systemSettings: '系统设置',
    basicConfig: '基础配置',
    notificationSettings: '通知设置',
    logManagement: '日志管理',
    moduleManagement: '模块管理',
    inviteCodeManagement: '邀请码管理',
    manuscriptManagement: '稿件管理',
    newSubmission: '新增投稿',
    myManuscripts: '我的稿件',
    manuscriptProgress: '稿件进度',
    historySubmission: '历史投稿',
    submissionGuide: '投稿指南',
    onlineConsultation: '在线咨询',
    permissionDenied: '权限不足，无法登录后台',
    authorResources: '投稿人资源',
    guideForAuthors: '投稿指南',
    templates: '模板',
    checkStatus: '状态查询',
    letters: '信件中心',
    lettersAndInvitations: '信件与邀请',
    profileSettings: '个人设置',
    helpSupport: '帮助与支持'
  },
  submission: {
    login: {
      title: '请输入以下信息',
      username: '用户名',
      password: '密码',
      btn: {
        author: '作者登录',
        reviewer: '审稿人登录',
        editor: '总编辑登录'
      },
      orcid: {
        label: '或通过以下方式登录',
        help: '什么是 ORCID?',
        info: 'ORCID 提供了一个持久的数字标识符，将您与其他研究人员区分开来。'
      },
      link: {
        sendDetails: '发送登录详情',
        register: '立即注册',
        help: '登录帮助'
      },
      error: {
        required: '用户名和密码为必填项',
        failed: '登录失败，请检查您的凭据。'
      }
    }
  },
  review: {
    title: '同行评审',
    dimensions: {
      novelty: '创新性 (Novelty)',
      scientificMerit: '科学价值 (Scientific Merit)',
      relevance: '临床/公共卫生意义 (Clinical/Public Health Relevance)',
      clarity: '表达与规范性 (Clarity & Compliance)',
      rigour: '方法学完整性 (Methodological Rigour)',
    },
    levels: {
      excellent: '优秀 (Excellent)',
      good: '良好 (Good)',
      fair: '一般 (Fair)',
      poor: '较差 (Poor)',
    },
    actions: {
      accept: '直接接受 (Accept as is)',
      reviseMinor: '小修 (Revise - Minor)',
      reviseMajor: '大修 (Revise - Major)',
      reject: '拒稿 (Reject)',
    },
    rules: {
      title: '核心审稿规则',
      priority: '创新性为最高优先级维度。',
      screening: '编辑初筛（1-3工作日）：70-80%退稿率。',
      peerReview: '同行评审（2-4周）：2-3位审稿人。',
      rejection: '退稿标准：创新性不足、致命缺陷、学术不端。',
      resubmission: '重投限制：拒稿后6个月内不可重投。',
    },
    screening: {
      title: '初筛与分配',
      searchPlaceholder: '搜索标题或投稿人...',
      allModules: '所有模块',
      noJournals: '暂无待初筛稿件。',
      actions: {
        assign: '分配审稿人',
        reject: '拒稿',
        confirm: '确认'
      },
      assignReviewer: '分配审稿人',
      errors: {
        selectReviewer: '请至少选择一位审稿人。'
      },
      success: {
        assigned: '审稿人分配成功。'
      },
      confirmReject: '确定要拒绝该稿件吗？此操作不可撤销。'
    },
    manuscriptProgress: {
      title: '稿件进度',
      select: '选择稿件',
      placeholder: '请选择稿件',
      auditProgress: '审核进度',
      details: '查看详情',
      stages: {
        submitted: '已投稿',
        initial: '初审',
        peer: '复审',
        final: '终审',
        published: '已发表/已拒稿'
      }
    },
    dashboard: {
      title: '工作台',
      welcome: '欢迎，{name}',
      stats: {
        totalJournals: '总投稿量',
        pendingJournals: '待审核',
        totalUsers: '总用户',
        recentSubmissions: '近期投稿'
      },
      recentJournals: {
        title: '近期投稿',
        author: '作者',
        date: '日期',
        status: '状态'
      }
    },
    comparison: {
      title: '与国内核心期刊差异',
      scoring: '打分体系：等级 + 详细评语（无数值打分）',
      efficiency: '退稿效率：初筛最快1天，无冗余',
      priority: '优先级：创新性 > 方法学',
      response: '修回要求：必须逐条回应意见',
    },
    placeholders: {
      comment: '请输入详细的评审意见...',
      confidential: '给编辑的保密意见...',
    },
    errors: {
      noveltyRequired: '必须评价创新性',
      commentRequired: '评审意见为必填项',
      allDimensionsRequired: '请评价所有维度',
      decisionRequired: '请选择推荐意见',
    },
  },
  auth: {
    adminLogin: {
      title: {
        admin: '主编/编辑后台登录',
        reviewer: '审稿人工作台登录',
        author: '作者工作台登录',
        default: '系统后台登录'
      },
      username: '用户名',
      password: '密码',
      rememberMe: '记住我',
      role: '角色',
      selectRole: '请选择角色',
      roles: {
        admin: '系统管理员',
        editor: '总编辑/编辑',
        reviewer: '审稿人',
        author: '作者'
      },
      loginBtn: '立即登录',
      noAccount: "没有账号？",
      registerNow: '立即注册',
      backToHome: '返回首页',
      error: {
        required: '请输入用户名和密码',
        authorized: '您仅被授权访问 [{role} 工作台]',
        failed: '登录失败，请稍后重试'
      }
    },
    register: {
      title: '创建账号',
      subtitle: '加入我们的学术社区',
      desc: '提交您的研究成果并参与同行评审过程。',
      usernameLabel: '用户名',
      usernamePlaceholder: '请输入用户名',
      emailLabel: '邮箱',
      emailPlaceholder: '请输入电子邮箱',
      passwordLabel: '密码',
      passwordPlaceholder: '请输入密码',
      confirmPasswordLabel: '确认密码',
      confirmPasswordPlaceholder: '请再次输入密码',
      error: {
        emailFormat: '邮箱格式不正确',
        passwordLength: '密码长度至少为 6 位',
        passwordMatch: '两次输入的密码不一致'
      }
    }
  },
  dashboard: {
    roles: {
      admin: '编辑工作台',
      editor: '编辑工作台',
      associate_editor: '副编辑工作台',
      editorial_assistant: '编辑助理工作台',
      advisory_editor: '顾问编辑工作台',
      default: '工作台'
    },
    welcome: '欢迎，{name}',
    stats: {
      totalJournals: '总投稿量',
      pendingJournals: '待审核稿件',
      totalUsers: '总用户数',
      recentSubmissions: '近期投稿',
      authorRecommendations: '作者推荐审稿人',
      pendingApproval: '待审批',
      avoidanceRequests: '回避请求',
      pendingReview: '待审核'
    },
    recentJournals: {
      title: '近期投稿',
      author: '作者',
      date: '日期'
    }
  },
  review: {
    title: '审稿表单',
    dimensions: {
      addressingPreviousConcerns: '对之前问题的回应',
      qualityOfRevisions: '修改质量',
      newIssuesIdentified: '发现的新问题',
      originality: '原创性',
      methodology: '方法论',
      ethicalCompliance: '伦理合规性',
      readability: '可读性',
      importance: '重要性'
    },
    levels: {
      excellent: '优秀',
      good: '良好',
      fair: '一般',
      poor: '较差'
    },
    comments: {
      toAuthor: '审稿意见（给作者）',
      toEditor: '保密意见（给编辑）',
      placeholder: '请输入您的审稿意见...'
    },
    decision: {
      label: '推荐意见',
      accept: '接受',
      minorRevision: '小修',
      majorRevision: '大修',
      reject: '拒绝'
    },
    actions: {
      submit: '提交审稿',
      cancel: '取消',
      saveDraft: '保存草稿'
    },
    validation: {
      required: '此项为必填项',
      selectAllDimensions: '请为所有必填评审维度选择评分',
      provideComments: '请提供给作者的审稿意见',
      selectDecision: '请选择对稿件的最终推荐意见'
    },
    confirmation: {
      title: '确认提交',
      message: '您确定要提交此审稿吗？此操作无法撤销，审稿内容将立即对编辑团队可见。'
    }
  },
  history: {
    title: {
      allHistory: '所有历史记录',
      manuscriptHistory: '稿件历史',
      operationHistory: '操作历史',
      submissionHistory: '投稿历史',
      reviewHistory: '审稿记录'
    },
    noRecords: '暂无记录',
    filters: {
      module: '模块筛选',
      status: '状态筛选',
      timeRange: '时间范围',
      keyword: '关键词搜索',
      searchPlaceholder: '搜索标题、作者或关键词...',
      allModules: '全部模块',
      allStatus: '全部状态',
      allTime: '全部时间',
      today: '今日',
      week: '本周',
      month: '本月',
      year: '本年'
    },
    table: {
      title: '标题',
      author: '作者',
      module: '模块',
      status: '状态',
      submitDate: '投稿日期',
      reviewDate: '审核日期',
      date: '日期',
      actions: '操作',
      viewDetail: '查看详情',
      operator: '操作人',
      action: '动作',
      notes: '备注'
    },
    status: {
      accepted: '已通过',
      rejected: '未通过',
      pending: '待审核',
      underReview: '审稿中',
      revisionRequested: '需修改',
      published: '已发表',
      submitted: '已投稿',
      initial: '初审',
      peer: '复审',
      final: '终审',
      statusChangedTo: '状态变更为',
      submissionSuccess: '稿件提交成功。'
    },
    action: {
      statusUpdate: '状态更新'
    },
    reviewComment: '审稿建议',
    noComment: '无审稿建议',
    expandAll: '展开全部',
    collapse: '收起',
    export: '导出数据',
    reset: '重置筛选',
    pagination: {
      total: '共 {total} 条记录',
      page: '第 {current} / {total} 页',
      prev: '上一页',
      next: '下一页'
    }
  }
}
