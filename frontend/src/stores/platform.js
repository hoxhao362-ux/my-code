import { defineStore } from 'pinia'
import { platformJournalApi } from '../utils/api'

export const usePlatformStore = defineStore('platform', {
  state: () => ({
    currentJournal: null,
    journals: [],
    loading: false
  }),
  
  actions: {
    async fetchJournals() {
      this.loading = true
      try {
        const data = await platformJournalApi.getJournals()
        this.journals = data
      } finally {
        this.loading = false
      }
    },
    
    async setJournal(id) {
      this.loading = true
      try {
        if (this.journals.length === 0) {
          await this.fetchJournals()
        }
        
        const journal = this.journals.find(j => j.id === id)
        if (journal) {
          this.currentJournal = journal
          // Update document title or favicon if needed
          document.title = journal.name
        } else {
            // Try fetching single if not found in list (though list should have it)
            const data = await platformJournalApi.getJournal(id)
            if (data) {
                this.currentJournal = data
                document.title = data.name
            }
        }
      } finally {
        this.loading = false
      }
    },
    
    clearJournal() {
      this.currentJournal = null
      document.title = 'Journal Platform'
    }
  }
})
