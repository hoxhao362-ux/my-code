import { defineStore } from 'pinia'

export const useDirectoryStore = defineStore('directory', {
  state: () => ({
    showDirectory: false,
    scrollPosition: 0 // 目录滚动位置
  }),
  
  actions: {
    toggleDirectory() {
      this.showDirectory = !this.showDirectory
    },
    openDirectory() {
      this.showDirectory = true
    },
    closeDirectory() {
      this.showDirectory = false
    },
    // 保存滚动位置
    saveScrollPosition(position) {
      this.scrollPosition = position
    },
    // 恢复滚动位置
    restoreScrollPosition() {
      return this.scrollPosition
    }
  }
})
