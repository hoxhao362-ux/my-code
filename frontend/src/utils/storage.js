import * as mockUserData from '../mocks/userData'
import * as mockJournalData from '../mocks/journalData'
import * as mockEditorAccounts from '../mocks/editorAccounts'
import * as mockPlatformJournals from '../mocks/platformJournals'

const KEYS = {
  USERS: 'journal_platform_users',
  JOURNALS: 'journal_platform_journals', // Manuscripts/Articles
  PLATFORM_JOURNALS: 'journal_platform_platform_journals', // Journal Venues (e.g., Lancet)
  ANNOUNCEMENTS: 'journal_platform_announcements',
  CONFIG: 'journal_platform_config',
  INVITATIONS: 'journal_platform_invitations',
  EDITOR_ACCOUNTS: 'journal_platform_editor_accounts'
}

// 初始化数据
const initData = () => {
  if (!localStorage.getItem(KEYS.USERS)) {
    localStorage.setItem(KEYS.USERS, JSON.stringify(mockUserData.users))
  }
  if (!localStorage.getItem(KEYS.JOURNALS)) {
    localStorage.setItem(KEYS.JOURNALS, JSON.stringify(mockJournalData.journals))
  }
  if (!localStorage.getItem(KEYS.PLATFORM_JOURNALS)) {
    localStorage.setItem(KEYS.PLATFORM_JOURNALS, JSON.stringify(mockPlatformJournals.platformJournals))
  }
  if (!localStorage.getItem(KEYS.ANNOUNCEMENTS)) {
    localStorage.setItem(KEYS.ANNOUNCEMENTS, JSON.stringify(mockJournalData.announcements))
  }
  if (!localStorage.getItem(KEYS.CONFIG)) {
    localStorage.setItem(KEYS.CONFIG, JSON.stringify(mockJournalData.basicConfig))
  }
  if (!localStorage.getItem(KEYS.INVITATIONS)) {
    localStorage.setItem(KEYS.INVITATIONS, JSON.stringify(mockJournalData.invitations))
  }
  if (!localStorage.getItem(KEYS.EDITOR_ACCOUNTS)) {
    localStorage.setItem(KEYS.EDITOR_ACCOUNTS, JSON.stringify(mockEditorAccounts.editorAccounts))
  }
}

// 确保初始化
initData()

export const storage = {
  get: (key) => {
    try {
      return JSON.parse(localStorage.getItem(key) || '[]')
    } catch (e) {
      return []
    }
  },
  set: (key, value) => {
    localStorage.setItem(key, JSON.stringify(value))
  },
  // 获取所有记录
  getAll: (key) => {
    return storage.get(key)
  },
  // 根据ID获取单条记录
  find: (key, id) => {
    const list = storage.get(key)
    return list.find(item => String(item.id) === String(id))
  },
  // 查找符合条件的记录
  query: (key, predicate) => {
    const list = storage.get(key)
    return list.filter(predicate)
  },
  // 添加记录
  add: (key, item) => {
    const list = storage.get(key)
    // 如果没有ID，生成一个
    if (!item.id) {
      item.id = Date.now()
    }
    list.unshift(item) // 新增在最前
    storage.set(key, list)
    return item
  },
  // 更新记录
  update: (key, id, updates) => {
    const list = storage.get(key)
    const index = list.findIndex(item => String(item.id) === String(id))
    if (index !== -1) {
      list[index] = { ...list[index], ...updates }
      storage.set(key, list)
      return list[index]
    }
    return null
  },
  // 删除记录
  remove: (key, id) => {
    const list = storage.get(key)
    const newList = list.filter(item => String(item.id) !== String(id))
    storage.set(key, newList)
    return newList.length < list.length
  },
  
  // 暴露 KEYS
  KEYS
}
