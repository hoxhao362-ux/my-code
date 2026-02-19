import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: []
  }),
  actions: {
    add(message, type = 'info', duration = 3000) {
      const id = Date.now()
      this.toasts.push({ id, message, type })
      if (duration > 0) {
        setTimeout(() => {
          this.remove(id)
        }, duration)
      }
    },
    remove(id) {
      const index = this.toasts.findIndex(t => t.id === id)
      if (index !== -1) {
        this.toasts.splice(index, 1)
      }
    },
    success(message, duration = 3000) {
      this.add(message, 'success', duration)
    },
    error(message, duration = 3000) {
      this.add(message, 'error', duration)
    },
    info(message, duration = 3000) {
      this.add(message, 'info', duration)
    },
    warning(message, duration = 3000) {
      this.add(message, 'warning', duration)
    }
  }
})
