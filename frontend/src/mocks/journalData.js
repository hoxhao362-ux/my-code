export const announcements = [
  { id: 1, title: 'Call for Papers: 2026 Submission Open', content: 'Dear writers, the 2026 Journal Submission Platform is now open for submissions. We welcome your contributions.', date: '2026-01-01' },
  { id: 2, title: 'System Update: New Review Reminder Feature Added', content: 'To better serve you, we have added a new review reminder feature. Please check your dashboard for details.', date: '2026-01-10' },
  { id: 3, title: 'Notice: Review Cycle Adjustment', content: 'Starting from Feb 1, 2026, the review cycle for general manuscripts will be shortened to 1-2 weeks.', date: '2026-01-12' }
]

export const basicConfig = {
  platformName: 'Journal Submission Platform',
  platformLogo: '',
  submissionRules: '1. Content must comply with academic standards\n2. Plagiarism is strictly prohibited\n3. All submissions undergo strict review\n4. Review cycle is typically 1-2 weeks\n5. Platform reserves all rights',
  contactEmail: 'contact@example.com',
  contactPhone: '13800138000',
  copyrightInfo: '© 2026 Journal Submission Platform. All rights reserved.'
}

export const reviewStages = ['Initial Review', 'Re-review', 'Final Decision']

export const modules = [
  'Medical Imaging',
  'Drug Discovery',
  'Clinical Research',
  'Public Health',
  'Bioinformatics',
  'Artificial Intelligence',
  'Others'
]

export const journals = [
  // Test data for New Submissions - Pending Screening
  {
    id: 20260001,
    title: 'Efficacy of New Antiviral Drugs in COVID-19 Treatment',
    writer: 'Jane Smith',
    module: 'Clinical Research',
    status: 'Pending Screening',
    submissionDate: '2026-02-18',
    abstract: 'This randomized controlled trial evaluates the efficacy and safety of novel antiviral drugs in the treatment of patients with moderate to severe COVID-19.',
    keywords: 'Antiviral Drugs, COVID-19, Clinical Trial',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 20260002,
    title: 'Public Health Interventions During Pandemics: A Systematic Review',
    writer: 'Michael Brown',
    module: 'Public Health',
    status: 'Pending Screening',
    submissionDate: '2026-02-18',
    abstract: 'This systematic review examines the effectiveness of various public health interventions implemented during recent pandemics, including social distancing, mask mandates, and vaccination campaigns.',
    keywords: 'Public Health, Pandemics, Interventions',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 20260003,
    title: 'AI-Powered Diagnostic Tools in Radiology: Clinical Validation',
    writer: 'David Chen',
    module: 'Medical Imaging',
    status: 'Pending Screening',
    submissionDate: '2026-02-18',
    abstract: 'This study validates the performance of AI-powered diagnostic tools in radiology practice, comparing accuracy rates with board-certified radiologists across different imaging modalities.',
    keywords: 'AI, Radiology, Diagnostic Tools',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 1,
    title: 'Development Trends in Medical Imaging Technology',
    writer: 'writer1',
    module: 'Medical Imaging',
    status: 'Published',
    submissionDate: '2026-01-10',
    publicationDate: '2026-01-15',
    abstract: 'This paper details the latest trends in medical imaging technology, including AI-assisted diagnosis and 3D printing applications.',
    keywords: 'Medical Imaging, AI Diagnosis, 3D Printing',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 2,
    title: 'Deep Learning Approaches in Drug Discovery',
    writer: 'writer2',
    module: 'Drug Discovery',
    status: 'Pending',
    submissionDate: '2026-01-12',
    abstract: 'This paper explores the application of deep learning in drug discovery, including molecular structure prediction and target identification.',
    keywords: 'Deep Learning, Drug Discovery, Molecular Structure',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 3,
    title: 'Big Data Analysis Methods in Clinical Research',
    writer: 'writer3',
    module: 'Clinical Research',
    status: 'Under Review',
    submissionDate: '2026-01-08',
    abstract: 'This paper introduces common methods and tools for big data analysis in clinical research.',
    keywords: 'Clinical Research, Big Data, Data Processing',
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer1', status: 'Reviewed', comment: 'Content is solid, methods are feasible.', rating: 4 }
    ]
  },
  {
    id: 4,
    title: 'Construction of Public Health Emergency Management Systems',
    writer: 'writer4',
    module: 'Public Health',
    status: 'Published',
    submissionDate: '2026-01-05',
    publicationDate: '2026-01-10',
    abstract: 'This paper analyzes the current status of public health emergency management systems and proposes improvements.',
    keywords: 'Public Health, Emergency Management, System Construction',
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer2', status: 'Reviewed', comment: 'Significant practical importance.', rating: 5 }
    ]
  },
  {
    id: 5,
    title: 'Applications of Bioinformatics in Gene Sequencing',
    writer: 'writer1',
    module: 'Bioinformatics',
    status: 'Published',
    submissionDate: '2026-01-03',
    publicationDate: '2026-01-08',
    abstract: 'This paper reviews applications of bioinformatics in gene sequencing, including sequence alignment and variant detection.',
    keywords: 'Bioinformatics, Gene Sequencing, Sequence Alignment',
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer3', status: 'Reviewed', comment: 'Comprehensive content, rich references.', rating: 4 }
    ]
  },
  // Test Data for Dr. Jane Smith (Reviewer)
  {
    id: 6,
    title: 'Epidemiology of Cardiovascular Diseases in Urban Populations',
    writer: 'writer2',
    module: 'Public Health',
    status: 'Under Review', // Under Review
    reviewStage: 'Initial Review',
    date: '2026-02-05', // Pending (Not Overdue)
    submissionDate: '2026-02-05',
    abstract: 'A comprehensive study on the prevalence and risk factors of cardiovascular diseases in major urban centers.',
    keywords: 'Epidemiology, Cardiovascular, Urban Health',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 7,
    title: 'Public Health Policy Analysis: A Global Perspective',
    writer: 'writer3',
    module: 'Public Health',
    status: 'Under Review', // Under Review
    reviewStage: 'Initial Review',
    date: '2026-01-20', // Overdue (> 14 days)
    submissionDate: '2026-01-20',
    abstract: 'An analysis of public health policies across different continents and their effectiveness.',
    keywords: 'Public Health, Policy, Global Health',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 8,
    title: 'Advanced Cardiac Imaging Techniques: A Clinical Study',
    writer: 'writer4',
    module: 'Medical Imaging',
    status: 'Under Review', // Under Review
    reviewStage: 'Re-review', // Re-review
    date: '2026-02-01',
    submissionDate: '2026-01-10',
    abstract: 'Clinical evaluation of new cardiac imaging modalities for early detection of heart failure.',
    keywords: 'Cardiology, Imaging, Heart Failure',
    fileUrl: '/vite.svg',
    reviews: [
       { reviewer: 'jane_smith', status: 'Reviewed', comment: 'Initial review completed. Revision required.', rating: 3 }
    ]
  },
  // New Mock Data - Pending Reviews
  {
    id: 9,
    title: 'R&D and Application of mRNA Vaccines',
    writer: 'writer5',
    module: 'Drug Discovery',
    status: 'Under Review',
    reviewStage: 'Initial Review',
    date: '2026-02-01',
    submissionDate: '2026-02-01',
    abstract: 'This paper reviews the R&D history of mRNA vaccines and their application in infectious disease control.',
    keywords: 'mRNA Vaccines, Drug Discovery, Infectious Diseases',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 10,
    title: 'Development and Challenges of Telemedicine',
    writer: 'writer6',
    module: 'Clinical Research',
    status: 'Under Review',
    reviewStage: 'Initial Review',
    date: '2026-02-02',
    submissionDate: '2026-02-02',
    abstract: 'This paper analyzes the current status of telemedicine, its technical applications, and challenges.',
    keywords: 'Telemedicine, Clinical Research, Technology Application',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 11,
    title: 'AI Applications in Drug Discovery',
    writer: 'writer11',
    module: 'Artificial Intelligence',
    status: 'Under Review',
    reviewStage: 'Initial Review',
    date: '2026-02-04',
    submissionDate: '2026-02-04',
    abstract: 'This paper explores AI technology in drug discovery, including virtual screening and molecular design.',
    keywords: 'AI, Drug Discovery, Virtual Screening',
    fileUrl: '/vite.svg',
    reviews: []
  },
  // New Mock Data - Pending Re-reviews
  {
    id: 12,
    title: 'Microbiome and Human Health',
    writer: 'writer7',
    module: 'Bioinformatics',
    status: 'Under Review',
    reviewStage: 'Re-review',
    date: '2026-02-03',
    submissionDate: '2026-02-03',
    abstract: 'This paper explores the composition and function of the human microbiome and its relationship with health.',
    keywords: 'Microbiome, Human Health, Bioinformatics',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 13,
    title: 'Clinical Applications of Precision Medicine',
    writer: 'writer12',
    module: 'Clinical Research',
    status: 'Under Review',
    reviewStage: 'Re-review',
    date: '2026-02-05',
    submissionDate: '2026-02-05',
    abstract: 'This paper reviews the application of precision medicine in clinical practice, including genomics and proteomics.',
    keywords: 'Precision Medicine, Clinical Application, Genomics',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 14,
    title: 'Recent Advances in Regenerative Medicine',
    writer: 'writer13',
    module: 'Medical Imaging',
    status: 'Under Review',
    reviewStage: 'Re-review',
    date: '2026-02-06',
    submissionDate: '2026-02-06',
    abstract: 'This paper introduces recent advances in regenerative medicine, including stem cell technology and tissue engineering.',
    keywords: 'Regenerative Medicine, Stem Cells, Tissue Engineering',
    fileUrl: '/vite.svg',
    reviews: []
  },
  // New Mock Data - Overdue Reviews
  {
    id: 15,
    title: 'Impact of Climate Change on Public Health',
    writer: 'writer8',
    module: 'Public Health',
    status: 'Under Review',
    reviewStage: 'Initial Review',
    date: '2026-01-15',
    submissionDate: '2026-01-15',
    abstract: 'This paper studies the impact of climate change on global public health, including disease spread and food safety.',
    keywords: 'Climate Change, Public Health, Disease Spread',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 16,
    title: 'Nanotechnology in Drug Delivery',
    writer: 'writer9',
    module: 'Drug Discovery',
    status: 'Under Review',
    reviewStage: 'Initial Review',
    date: '2026-01-10',
    submissionDate: '2026-01-10',
    abstract: 'This paper reviews nanotechnology in drug delivery systems, including targeted delivery and controlled release.',
    keywords: 'Nanotechnology, Drug Delivery, Targeted Therapy',
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 17,
    title: 'Efficacy of CBT in Depression Treatment',
    writer: 'writer10',
    module: 'Clinical Research',
    status: 'Under Review',
    reviewStage: 'Re-review',
    date: '2026-01-05',
    submissionDate: '2026-01-05',
    abstract: 'This paper systematically evaluates the efficacy and prospects of Cognitive Behavioral Therapy in treating depression.',
    keywords: 'CBT, Depression, Clinical Research',
    fileUrl: '/vite.svg',
    reviews: []
  },
  // New Mock Data - Completed Reviews
  {
    id: 18,
    title: 'Ethical Considerations of Gene Editing',
    writer: 'writer14',
    module: 'Bioinformatics',
    status: 'Published',
    reviewStage: 'Final Decision',
    date: '2026-01-20',
    submissionDate: '2026-01-20',
    publicationDate: '2026-01-25',
    abstract: 'This paper discusses ethical issues in gene editing, including human embryo editing and genetic enhancement.',
    keywords: 'Gene Editing, Ethics, Human Embryo',
    fileUrl: '/vite.svg',
    reviewHistory: [
      { reviewer: 'jane_smith', status: 'Reviewed', comment: 'Comprehensive content, in-depth ethical analysis.', rating: 5 }
    ]
  },
  {
    id: 19,
    title: 'Development Trends in Digital Health',
    writer: 'writer15',
    module: 'Artificial Intelligence',
    status: 'Published',
    reviewStage: 'Final Decision',
    date: '2026-01-18',
    submissionDate: '2026-01-18',
    publicationDate: '2026-01-23',
    abstract: 'This paper analyzes trends in digital health, including EHR and remote monitoring.',
    keywords: 'Digital Health, EHR, Remote Monitoring',
    fileUrl: '/vite.svg',
    reviewHistory: [
      { reviewer: 'jane_smith', status: 'Reviewed', comment: 'Novel research content, in-depth analysis.', rating: 4 }
    ]
  },
  {
    id: 20,
    title: 'Global Challenge of Antibiotic Resistance',
    writer: 'writer16',
    module: 'Drug Discovery',
    status: 'Published',
    reviewStage: 'Final Decision',
    date: '2026-01-15',
    submissionDate: '2026-01-15',
    publicationDate: '2026-01-20',
    abstract: 'This paper studies the global status, causes, and response strategies for antibiotic resistance.',
    keywords: 'Antibiotic Resistance, Global Health, Strategies',
    fileUrl: '/vite.svg',
    reviewHistory: [
      { reviewer: 'jane_smith', status: 'Reviewed', comment: 'Solid data, feasible suggestions.', rating: 5 }
    ]
  }
]

export const invitations = [
  { id: 101, title: 'AI in Healthcare: A Comprehensive Review', module: 'AI', date: '2026-02-01', status: 'Invited' },
  { id: 102, title: 'Sustainable Energy Solutions for 2030', module: 'Energy', date: '2026-02-02', status: 'Invited' },
  { id: 103, title: 'CRISPR-Cas9 Applications in Genetic Diseases', module: 'Genetics', date: '2026-02-03', status: 'Invited' },
  { id: 104, title: 'Blockchain Technology in Medical Records Management', module: 'Healthcare IT', date: '2026-02-04', status: 'Invited' },
  { id: 105, title: 'Neuroplasticity in Aging: Mechanisms and Interventions', module: 'Neuroscience', date: '2026-02-05', status: 'Invited' }
]
