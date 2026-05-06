export const announcements = [
  { id: 1, title: 'Call for Papers: 2026 Submission Open', content: 'Dear authors, the 2026 Peerex Peer Platform is now open for submissions. We welcome your contributions.', date: '2026-01-01' },
  { id: 2, title: 'System Update: New Review Reminder Feature Added', content: 'To better serve you, we have added a new review reminder feature. Please check your dashboard for details.', date: '2026-01-10' },
  { id: 3, title: 'Notice: Review Cycle Adjustment', content: 'Starting from Feb 1, 2026, the review cycle for general manuscripts will be shortened to 1-2 weeks.', date: '2026-01-12' }
]

export const basicConfig = {
  platformName: 'Peerex Peer',
  platformLogo: '',
  submissionRules: '1. Content must comply with academic standards\n2. Plagiarism is strictly prohibited\n3. All submissions undergo strict review\n4. Review cycle is typically 1-2 weeks\n5. Platform reserves all rights',
  contactEmail: 'contact@example.com',
  contactPhone: '13800138000',
  copyrightInfo: '© 2026 Peerex Peer. All rights reserved.'
}

export const reviewStages = ['Initial Review', 'Peer Review', 'Final Decision']

export const modules = [
  'Medical Imaging',
  'Drug Discovery',
  'Clinical Research',
  'Public Health',
  'Bioinformatics',
  'Artificial Intelligence',
  'Others'
]

// Status constants for mock data
const STATUS = {
  PENDING_INITIAL_REVIEW: 'pending_initial_review',
  UNDER_PEER_REVIEW: 'under_peer_review',
  PUBLISHED: 'published',
  ACCEPTED: 'accepted',
<<<<<<< HEAD
  REJECTED: 'rejected'
}

export const journals = [
=======
  REJECTED: 'rejected',
  TRANSFER_SUGGESTED: 'transfer_suggested'
}

export const journals = [
  // Test data for Transfer functionality
  {
    id: 'MS2026-TRANSFER-01',
    title: 'Genomic Profiling of Rare Tumors',
    author: 'Dr. Alan Turing',
    module: 'Oncology',
    status: STATUS.TRANSFER_SUGGESTED,
    submissionDate: '2026-03-01',
    date: '2026-03-01',
    abstract: 'This paper discusses genomic profiling...',
    keywords: ['Genomics', 'Tumors'],
    fileUrl: '/vite.svg',
    reviews: [],
    transferTo: 'lancet-oncology',
    transferReason: 'While your manuscript is of high quality, it is highly specialized in oncology and would be a better fit for our sister journal, The Lancet Oncology.'
  },
  {
    id: 'MS2026-TRANSFER-IN-02',
    title: 'New approach to neurological disorder',
    author: 'Dr. Grace Hopper',
    module: 'Neurology',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-03-05',
    date: '2026-03-05',
    abstract: 'This paper was transferred from another journal.',
    keywords: ['Neurology'],
    fileUrl: '/vite.svg',
    reviews: [],
    transferredFrom: 'lancet',
    transferredDate: '2026-03-05'
  },
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  // Test data for Publication module
  {
    id: 1001,
    title: 'Novel Therapeutic Approaches for Alzheimer\'s Disease',
    author: 'John Doe',
    module: 'Clinical Research',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-02-10',
    date: '2026-02-10',
    abstract: 'This study explores innovative therapeutic strategies for the treatment of Alzheimer\'s disease, including targeted drug delivery systems and non-pharmacological interventions.',
    keywords: ['Alzheimer\'s Disease', 'Therapeutics', 'Drug Delivery'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer1', status: 'Reviewed', comment: 'Novel approach with significant potential', rating: 5 },
      { reviewer: 'reviewer2', status: 'Reviewed', comment: 'Well-designed study with robust methodology', rating: 4 }
    ]
  },
  {
    id: 1002,
    title: 'Genomic Biomarkers in Cancer Diagnosis',
    author: 'Jane Smith',
    module: 'Bioinformatics',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-02-08',
    date: '2026-02-08',
    abstract: 'This research identifies key genomic biomarkers for early detection of various cancer types, improving diagnostic accuracy and patient outcomes.',
    keywords: ['Genomics', 'Biomarkers', 'Cancer Diagnosis'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer3', status: 'Reviewed', comment: 'Groundbreaking findings with clinical relevance', rating: 5 },
      { reviewer: 'reviewer4', status: 'Reviewed', comment: 'Comprehensive analysis with validated results', rating: 4 }
    ]
  },
  {
    id: 1003,
    title: 'Artificial Intelligence in Medical Imaging',
    author: 'David Johnson',
    module: 'Artificial Intelligence',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-02-05',
    date: '2026-02-05',
    abstract: 'This paper evaluates the effectiveness of AI algorithms in interpreting medical images, including X-rays, MRIs, and CT scans, compared to board-certified radiologists.',
    keywords: ['AI', 'Medical Imaging', 'Diagnostic Accuracy'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer5', status: 'Reviewed', comment: 'Innovative application of AI in healthcare', rating: 4 },
      { reviewer: 'reviewer6', status: 'Reviewed', comment: 'Thorough evaluation with clinical validation', rating: 5 }
    ]
  },
  // Test data for New Submissions - Pending Screening
  {
    id: 20260001,
    title: 'Efficacy of New Antiviral Drugs in COVID-19 Treatment',
    author: 'Jane Smith',
    module: 'Clinical Research',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-02-18',
    date: '2026-02-18',
    abstract: 'This randomized controlled trial evaluates the efficacy and safety of novel antiviral drugs in the treatment of patients with moderate to severe COVID-19.',
    keywords: ['Antiviral Drugs', 'COVID-19', 'Clinical Trial'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 20260002,
    title: 'Public Health Interventions During Pandemics: A Systematic Review',
    author: 'Michael Brown',
    module: 'Public Health',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-02-18',
    date: '2026-02-18',
    abstract: 'This systematic review examines the effectiveness of various public health interventions implemented during recent pandemics, including social distancing, mask mandates, and vaccination campaigns.',
    keywords: ['Public Health', 'Pandemics', 'Interventions'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 20260003,
    title: 'AI-Powered Diagnostic Tools in Radiology: Clinical Validation',
    author: 'David Chen',
    module: 'Medical Imaging',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-02-18',
    date: '2026-02-18',
    abstract: 'This study validates the performance of AI-powered diagnostic tools in radiology practice, comparing accuracy rates with board-certified radiologists across different imaging modalities.',
    keywords: ['AI', 'Radiology', 'Diagnostic Tools'],
    fileUrl: '/vite.svg',
    reviews: []
  },
<<<<<<< HEAD
=======
  {
    id: 'MS2024-0001',
    title: 'Novel Biomarkers for Early Detection of Lung Cancer: A Prospective Cohort Study',
    articleType: 'original',
    author: 'Dr. John Smith',
    module: 'Clinical Research',
    status: STATUS.UNDER_PEER_REVIEW,
    submissionDate: '2026-01-15',
    date: '2026-01-15',
    abstract: 'Background: Lung cancer remains the leading cause of cancer-related mortality. Methods: We conducted a prospective cohort study involving 5,000 high-risk individuals. Findings: We identified a panel of three circulating microRNAs that demonstrated high sensitivity and specificity. Interpretation: These biomarkers could significantly improve early detection rates and patient survival.',
    wordCount: 3250,
    referenceCount: 32,
    keywords: ['lung cancer', 'biomarkers', 'early detection'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 'MS2024-0002',
    title: 'Efficacy and Safety of a Novel Monoclonal Antibody in Rheumatoid Arthritis',
    articleType: 'clinical',
    author: 'Dr. Emily Chen',
    module: 'Clinical Research',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-02-20',
    date: '2026-02-20',
    abstract: 'This phase III, double-blind, randomized controlled trial evaluated the efficacy and safety of mAb-X in patients with moderate-to-severe rheumatoid arthritis who had an inadequate response to methotrexate.',
    wordCount: 4100,
    referenceCount: 45,
    keywords: ['rheumatoid arthritis', 'monoclonal antibody', 'clinical trial'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 'MS2024-0003',
    title: 'Global Burden of Antimicrobial Resistance in 2025: A Systematic Analysis',
    articleType: 'review',
    author: 'Dr. Sarah Johnson',
    module: 'Public Health',
    status: STATUS.ACCEPTED,
    submissionDate: '2025-11-05',
    date: '2025-11-05',
    abstract: 'We present comprehensive estimates of the global burden of antimicrobial resistance (AMR) for 2025, analyzing data from 204 countries and territories. Our findings highlight the urgent need for coordinated international action.',
    wordCount: 6500,
    referenceCount: 120,
    keywords: ['antimicrobial resistance', 'global health', 'systematic analysis'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer1', status: 'Reviewed', comment: 'Excellent comprehensive analysis.', rating: 5 }
    ]
  },
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  {
    id: 1,
    title: 'Development Trends in Medical Imaging Technology',
    author: 'author1',
    module: 'Medical Imaging',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-01-10',
    date: '2026-01-10',
    publicationDate: '2026-01-15',
    abstract: 'This paper details the latest trends in medical imaging technology, including AI-assisted diagnosis and 3D printing applications.',
    keywords: ['Medical Imaging', 'AI Diagnosis', '3D Printing'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 2,
    title: 'Deep Learning Approaches in Drug Discovery',
    author: 'author2',
    module: 'Drug Discovery',
    status: STATUS.PENDING_INITIAL_REVIEW,
    submissionDate: '2026-01-12',
    date: '2026-01-12',
    abstract: 'This paper explores the application of deep learning in drug discovery, including molecular structure prediction and target identification.',
    keywords: ['Deep Learning', 'Drug Discovery', 'Molecular Structure'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 3,
    title: 'Big Data Analysis Methods in Clinical Research',
    author: 'author3',
    module: 'Clinical Research',
    status: STATUS.UNDER_PEER_REVIEW,
    reviewStage: 'Peer Review',
    submissionDate: '2026-01-08',
    date: '2026-01-08',
    abstract: 'This paper introduces common methods and tools for big data analysis in clinical research.',
    keywords: ['Clinical Research', 'Big Data', 'Data Processing'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer1', status: 'Reviewed', comment: 'Content is solid, methods are feasible.', rating: 4 }
    ]
  },
  {
    id: 4,
    title: 'Construction of Public Health Emergency Management Systems',
    author: 'author4',
    module: 'Public Health',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-01-05',
    date: '2026-01-05',
    publicationDate: '2026-01-10',
    abstract: 'This paper analyzes the current status of public health emergency management systems and proposes improvements.',
    keywords: ['Public Health', 'Emergency Management', 'System Construction'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer2', status: 'Reviewed', comment: 'Significant practical importance.', rating: 5 }
    ]
  },
  {
    id: 5,
    title: 'Applications of Bioinformatics in Gene Sequencing',
    author: 'author1',
    module: 'Bioinformatics',
    status: STATUS.PUBLISHED,
    submissionDate: '2026-01-03',
    date: '2026-01-03',
    publicationDate: '2026-01-08',
    abstract: 'This paper reviews applications of bioinformatics in gene sequencing, including sequence alignment and variant detection.',
    keywords: ['Bioinformatics', 'Gene Sequencing', 'Sequence Alignment'],
    fileUrl: '/vite.svg',
    reviews: [
      { reviewer: 'reviewer3', status: 'Reviewed', comment: 'Comprehensive content, rich references.', rating: 4 }
    ]
  },
  // Test Data for Dr. Jane Smith (Reviewer)
  {
    id: 6,
    title: 'Epidemiology of Cardiovascular Diseases in Urban Populations',
    author: 'author2',
    module: 'Public Health',
    status: STATUS.UNDER_PEER_REVIEW,
    reviewStage: 'Initial Review',
    date: '2026-02-05',
    submissionDate: '2026-02-05',
    abstract: 'A comprehensive study on the prevalence and risk factors of cardiovascular diseases in major urban centers.',
    keywords: ['Epidemiology', 'Cardiovascular', 'Urban Health'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 7,
    title: 'Public Health Policy Analysis: A Global Perspective',
    author: 'author3',
    module: 'Public Health',
    status: STATUS.UNDER_PEER_REVIEW,
    reviewStage: 'Initial Review',
    date: '2026-01-20',
    submissionDate: '2026-01-20',
    abstract: 'An analysis of public health policies across different continents and their effectiveness.',
    keywords: ['Public Health', 'Policy', 'Global Health'],
    fileUrl: '/vite.svg',
    reviews: []
  },
  {
    id: 8,
    title: 'Advanced Cardiac Imaging Techniques: A Clinical Study',
    author: 'author4',
    module: 'Medical Imaging',
    status: STATUS.UNDER_PEER_REVIEW,
    reviewStage: 'Peer Review',
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
    author: 'author5',
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
    author: 'author6',
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
    author: 'author11',
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
    author: 'author7',
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
    author: 'author12',
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
    author: 'author13',
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
    author: 'author8',
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
    author: 'author9',
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
    author: 'author10',
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
    author: 'author14',
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
    author: 'author15',
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
    author: 'author16',
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
