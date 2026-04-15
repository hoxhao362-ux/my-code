// 完整的reviewer虚拟账号
// 已通过become a reviewer申请流程，可直接审稿
export const reviewerAccounts = [
  {
    id: 201,
    username: 'senior_reviewer',
    role: 'reviewer',
    email: 'senior.reviewer@university.edu',
    phone: '13800138201',
    status: 'active',
    fullName: 'Prof. Michael Johnson',
    orcid: '0000-0003-4567-8901',
    researchAreas: 'Medicine, Clinical Research, Healthcare Policy',
    institution: 'Harvard Medical School',
    education: 'Ph.D. in Medical Science, Harvard University',
    expertiseLevel: 'senior',
    reviewCount: 150,
    averageRating: 4.8,
    specialties: ['Clinical Trials', 'Evidence-Based Medicine', 'Healthcare Economics'],
    languages: ['English', 'Spanish'],
    availability: 'high',
    responseTime: '2-3 days',
    bio: 'Professor of Medicine at Harvard Medical School with over 20 years of experience in clinical research and healthcare policy. Published over 100 peer-reviewed articles in top medical journals.',
    reviewHistory: [
      { manuscriptId: 101, rating: 5, feedback: 'Excellent research with rigorous methodology' },
      { manuscriptId: 102, rating: 4, feedback: 'Good study design, minor revisions needed' },
      { manuscriptId: 103, rating: 5, feedback: 'Outstanding contribution to the field' }
    ],
    certifications: [
      'Board Certified in Internal Medicine',
      'Certified Clinical Research Professional'
    ],
    memberships: [
      'American Medical Association',
      'International Society for Pharmacoepidemiology'
    ],
    preferences: {
      reviewLoad: 'moderate',
      notificationFrequency: 'weekly',
      doubleBlindOnly: true
    }
  },
  {
    id: 202,
    username: 'expert_reviewer',
    role: 'reviewer',
    email: 'expert.reviewer@research.org',
    phone: '13800138202',
    status: 'active',
    fullName: 'Dr. Emily Chen',
    orcid: '0000-0004-1234-5678',
    researchAreas: 'Biomedical Science, Genetics, Molecular Biology',
    institution: 'Stanford Research Institute',
    education: 'Ph.D. in Molecular Biology, Stanford University',
    expertiseLevel: 'expert',
    reviewCount: 85,
    averageRating: 4.9,
    specialties: ['Genomics', 'Proteomics', 'Gene Editing'],
    languages: ['English', 'Mandarin'],
    availability: 'medium',
    responseTime: '3-4 days',
    bio: 'Research Scientist at Stanford Research Institute specializing in genomics and gene editing technologies. Co-author of several groundbreaking papers on CRISPR applications.',
    reviewHistory: [
      { manuscriptId: 104, rating: 5, feedback: 'Innovative approach with significant potential' },
      { manuscriptId: 105, rating: 4, feedback: 'Solid work, some technical issues to address' }
    ],
    certifications: [
      'Certified Genetic Counselor',
      'Advanced Molecular Biology Techniques'
    ],
    memberships: [
      'American Society of Human Genetics',
      'International Society for Stem Cell Research'
    ],
    preferences: {
      reviewLoad: 'light',
      notificationFrequency: 'biweekly',
      doubleBlindOnly: false
    }
  }
]

// 登录信息（供测试使用）
export const reviewerLoginInfo = {
  senior_reviewer: {
    username: 'senior_reviewer',
    password: 'reviewer123',
    role: 'reviewer'
  },
  expert_reviewer: {
    username: 'expert_reviewer',
    password: 'reviewer123',
    role: 'reviewer'
  }
}
