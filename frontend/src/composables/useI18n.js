import { ref, computed, watch } from 'vue'
import en from '../locales/en'
import zh from '../locales/zh'

const currentLang = ref(localStorage.getItem('app_lang') || 'en')

const messages = {
  en,
  zh
}

export const useI18n = () => {
  const setLang = (lang) => {
    if (messages[lang]) {
      currentLang.value = lang
      localStorage.setItem('app_lang', lang)
    }
  }

  // Helper to access nested object properties by string path
  // e.g. t('common.back', { name: 'John' }) -> messages[lang].common.back (with replacement)
  const t = (path, params = {}) => {
    const keys = path.split('.')
    let current = messages[currentLang.value]
    
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key]
      } else {
        return path // Return path if not found
      }
    }
    
    // Simple placeholder replacement: {name} -> params.name
    if (typeof current === 'string') {
      let result = current
      Object.entries(params).forEach(([key, value]) => {
        result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value)
      })
      return result
    }
    
    return current
  }

  return {
    currentLang: computed(() => currentLang.value),
    setLang,
    t
  }
}
