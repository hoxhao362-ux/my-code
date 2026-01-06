<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const route = useRoute()
const journalId = computed(() => route.params.id)

// 获取当前期刊详情
const journal = computed(() => {
  return userStore.journals.find(j => j.id === journalId.value)
})
</script>

<template>
  <div class="journal-detail-container">
    <div v-if="journal" class="journal-detail-content">
      <header class="journal-detail-header">
        <h1 class="journal-title">{{ journal.title }}</h1>
        <div class="journal-meta">
          <p>作者：{{ journal.author }} | 投稿日期：{{ journal.date }} | 模块：{{ journal.module }}</p>
          <p>状态：<span class="journal-status" :class="journal.status.toLowerCase()">{{ journal.status }}</span></p>
        </div>
      </header>

      <section class="journal-abstract">
        <h2>摘要</h2>
        <p>{{ journal.abstract }}</p>
      </section>

      <section class="journal-keywords">
        <h2>关键词</h2>
        <div class="keywords-list">
          <span 
            v-for="(keyword, index) in journal.keywords" 
            :key="index" 
            class="keyword-tag"
          >
            {{ keyword }}
          </span>
        </div>
      </section>

      <section class="journal-content">
        <h2>正文</h2>
        <div v-html="journal.content"></div>
      </section>
    </div>
    <div v-else class="no-journal">
      <p>未找到该期刊</p>
    </div>
  </div>
</template>

<style scoped>
/* 样式可以从原 JournalDetail.vue 组件复制 */
</style>