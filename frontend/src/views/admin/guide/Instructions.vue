<template>
  <div class="instructions-container">
    <h2 class="page-title">投稿须知</h2>
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="instructions-content">
      <div class="section">
        <h3>格式要求</h3>
        <ul>
          <li>稿件应使用Word或PDF格式，字数控制在5000-15000字之间</li>
          <li>标题：三号黑体，居中，加粗</li>
          <li>作者姓名：四号宋体，居中</li>
          <li>摘要：五号宋体，150-300字</li>
          <li>关键词：3-5个，五号宋体，用分号分隔</li>
          <li>正文：五号宋体，行间距1.5倍</li>
          <li>参考文献：按GB/T 7714-2015格式规范</li>
        </ul>
      </div>
      <div class="section">
        <h3>审稿流程</h3>
        <ol>
          <li>作者在线投稿</li>
          <li>编辑部初步审核（1-3个工作日）</li>
          <li>同行专家评审（15-30个工作日）</li>
          <li>编辑部终审</li>
          <li>通知作者录用结果</li>
          <li>作者修改、定稿</li>
          <li>排版、校对</li>
          <li>出版</li>
        </ol>
      </div>
      <div class="section">
        <h3>版权说明</h3>
        <ul>
          <li>作者投稿即视为同意将作品的出版权授予本刊</li>
          <li>本刊有权对来稿进行文字性修改和删节</li>
          <li>作者需保证所投稿件为原创作品，无抄袭、剽窃行为</li>
          <li>作者需保证所投稿件未在其他出版物上发表</li>
          <li>稿件发表后，作者可获得样刊2册</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.instructions-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: #333;
}

.back-button-container {
  margin-bottom: 2rem;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.back-arrow {
  font-weight: bold;
}

.instructions-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.section {
  margin-bottom: 2rem;
}

.section h3 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #3498db;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.5rem;
}

.section ul,
.section ol {
  padding-left: 1.5rem;
  line-height: 1.8;
  color: #555;
}

.section li {
  margin-bottom: 0.5rem;
}

.section ul li {
  list-style-type: disc;
}

.section ol li {
  list-style-type: decimal;
}
</style>