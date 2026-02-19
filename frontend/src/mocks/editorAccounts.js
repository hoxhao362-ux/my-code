// 编辑虚拟账号
// 三类编辑：主编、副主编、EA&AE
export const editorAccounts = [
  {
    id: 101,
    username: 'chief_editor',
    role: 'editor',
    email: 'chief.editor@journal.com',
    phone: '13800138101',
    status: 'active',
    fullName: 'Prof. John Wang',
    orcid: '0000-0001-8135-3489',
    researchAreas: 'Medicine, Public Health, Epidemiology',
    institution: 'National Medical Center'
  },
  {
    id: 102,
    username: 'associate_editor',
    role: 'associate_editor',
    email: 'associate.editor@journal.com',
    phone: '13800138102',
    status: 'active',
    fullName: 'Dr. Sarah Chen',
    orcid: '0000-0002-7890-1234',
    researchAreas: 'Biomedical Science, Genetics',
    institution: 'Research Institute of Medicine'
  },
  {
    id: 103,
    username: 'ea_ae',
    role: 'ea_ae',
    email: 'ea.ae@journal.com',
    phone: '13800138103',
    status: 'active',
    fullName: 'Ms. Lisa Zhang',
    researchAreas: 'Editorial Management, Publishing',
    institution: 'Journal Editorial Office'
  }
]

// 登录信息（供测试使用）
export const editorLoginInfo = {
  chief_editor: {
    username: 'chief_editor',
    password: 'editor123',
    role: 'editor'
  },
  associate_editor: {
    username: 'associate_editor',
    password: 'associate_editor123',
    role: 'associate_editor'
  },
  ea_ae: {
    username: 'ea_ae',
    password: 'editorial_assistant123',
    role: 'ea_ae'
  }
}
