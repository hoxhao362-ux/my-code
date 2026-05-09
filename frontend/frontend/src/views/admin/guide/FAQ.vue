<template>
  <div class="faq-container">
    <h2 class="page-title">常见问题</h2>
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <span class="back-arrow">←</span> 返回上一页
      </button>
    </div>
    <div class="faq-content">
      <div class="faq-section">
        <h3>投稿流程</h3>
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(0)">
            <span class="faq-title">如何在线投稿？</span>
            <span class="faq-toggle">{{ faqOpen[0] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[0]">
            <p>1. 登录作者后台管理系统</p>
            <p>2. 点击左侧菜单栏中的"稿件管理"</p>
            <p>3. 选择"新增投稿"</p>
            <p>4. 按照系统提示填写稿件信息并上传稿件</p>
            <p>5. 确认无误后提交稿件</p>
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(1)">
            <span class="faq-title">投稿后多久能收到审核结果？</span>
            <span class="faq-toggle">{{ faqOpen[1] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[1]">
            <p>一般情况下，稿件审核周期为15-30个工作日。初审结果会在3个工作日内通知作者，外审结果需要15-20个工作日，终审结果会在5个工作日内通知作者。</p>
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(2)">
            <span class="faq-title">如何查询稿件状态？</span>
            <span class="faq-toggle">{{ faqOpen[2] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[2]">
            <p>登录作者后台管理系统，点击"稿件管理"-"我的稿件"，可以查看所有稿件的状态。对于正在审核的稿件，可以点击"稿件进度"查看详细的审核节点和意见。</p>
          </div>
        </div>
      </div>
      
      <div class="faq-section">
        <h3>格式问题</h3>
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(3)">
            <span class="faq-title">稿件应使用什么格式？</span>
            <span class="faq-toggle">{{ faqOpen[3] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[3]">
            <p>稿件应使用Word或PDF格式，推荐使用Word格式，方便后续编辑和排版。</p>
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(4)">
            <span class="faq-title">参考文献格式有什么要求？</span>
            <span class="faq-toggle">{{ faqOpen[4] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[4]">
            <p>参考文献应按照GB/T 7714-2015格式规范编写，包括作者、文章标题、期刊名称、出版年份、卷号、期号、页码等信息。</p>
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question" @click="toggleFaq(5)">
            <span class="faq-title">图表格式有什么要求？</span>
            <span class="faq-toggle">{{ faqOpen[5] ? '▼' : '▶' }}</span>
          </div>
          <div class="faq-answer" v-if="faqOpen[5]">
            <p>1. 图表应清晰、准确，分辨率不低于300dpi</p>
            <p>2. 图表应包含标题和编号</p>
            <p>3. 图表中的文字应清晰可辨，建议使用Arial或Times New Roman字体</p>
            <p>4. 图表应在正文中相应位置提及</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const faqOpen = ref([false, false, false, false, false, false])

const goBack = () => {
  router.back()
}

const toggleFaq = (index) => {
  faqOpen.value[index] = !faqOpen.value[index]
}
</script>

<style scoped>
.faq-container {
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

.faq-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.faq-section {
  margin-bottom: 2rem;
}

.faq-section h3 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #3498db;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.5rem;
}

.faq-item {
  margin-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 0.5rem;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.8rem 0;
  font-weight: 500;
  color: #333;
  transition: color 0.3s ease;
}

.faq-question:hover {
  color: #3498db;
}

.faq-toggle {
  font-size: 0.8rem;
  transition: transform 0.3s ease;
}

.faq-answer {
  padding: 0.5rem 0 1rem 0;
  color: #555;
  line-height: 1.6;
}

.faq-answer p {
  margin-bottom: 0.5rem;
}
</style>