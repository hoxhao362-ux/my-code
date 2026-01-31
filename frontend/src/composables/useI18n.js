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
  // e.g. t('common.back') -> messages[lang].common.back
  const t = (path) => {
    const keys = path.split('.')
    let current = messages[currentLang.value]
    
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key]
      } else {
        return path // Return path if not found
      }
    }
    
    return current
  }

  return {
    currentLang: computed(() => currentLang.value),
    setLang,
    t
  }
}
