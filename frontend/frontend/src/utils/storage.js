// Mock storage utility - Deprecated in favor of real backend API
// This file is kept for backward compatibility but should not be used

const KEYS = {
  USERS: 'journal_platform_users',
  JOURNALS: 'journal_platform_journals',
  PLATFORM_JOURNALS: 'journal_platform_platform_journals',
  ANNOUNCEMENTS: 'journal_platform_announcements',
  CONFIG: 'journal_platform_config',
  INVITATIONS: 'journal_platform_invitations',
  EDITOR_ACCOUNTS: 'journal_platform_editor_accounts'
}

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
  getAll: (key) => {
    return storage.get(key)
  },
  find: (key, id) => {
    const list = storage.get(key)
    return list.find(item => String(item.id) === String(id))
  },
  query: (key, predicate) => {
    const list = storage.get(key)
    return list.filter(predicate)
  },
  add: (key, item) => {
    const list = storage.get(key)
    if (!item.id) {
      item.id = Date.now()
    }
    list.unshift(item)
    storage.set(key, list)
    return item
  },
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
  remove: (key, id) => {
    const list = storage.get(key)
    const newList = list.filter(item => String(item.id) !== String(id))
    storage.set(key, newList)
    return newList.length < list.length
  },
  KEYS
}
