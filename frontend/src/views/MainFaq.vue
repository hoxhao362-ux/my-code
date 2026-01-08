<script setup>
import { ref } from 'vue'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { useDirectoryStore } from '../stores/directory'

const userStore = useUserStore()
const directoryStore = useDirectoryStore()
const user = ref(userStore.user)

// 切换目录显示
const toggleDirectory = () => {
  directoryStore.toggleDirectory()
}

// 常见问题数据
const faqs = ref([
  {
    id: 1,
    category: '投稿流程',
    questions: [
      {
        question: '如何进行投稿？',
        answer: '登录平台后，点击顶部导航栏的"投稿中心"->"在线投稿"，填写论文信息并提交即可。'
      },
      {
        question: '投稿需要什么格式？',
        answer: '请参考"投稿中心"->"投稿须知"中的格式要求，包括标题、摘要、关键词、正文等格式规范。'
      },
      {
        question: '可以同时投稿多篇论文吗？',
        answer: '可以，平台支持同时投稿多篇论文，每篇论文需要单独提交。'
      },
      {
        question: '投稿后可以修改吗？',
        answer: '投稿后在审核状态下，您可以在个人中心查看稿件状态，部分情况下支持修改。'
      }
    ]
  },
  {
    id: 2,
    category: '查稿流程',
    questions: [
      {
        question: '如何查询稿件状态？',
        answer: '登录平台后，进入"个人中心"，在"我的投稿"中可以查看所有投稿的状态。'
      },
      {
        question: '审稿周期一般是多久？',
        answer: '审稿周期一般为1-2周，具体时间根据稿件情况和审稿人安排而定。'
      },
      {
        question: '如果稿件被拒，还可以再次投稿吗？',
        answer: '可以，根据审稿意见修改后，可以再次投稿。'
      },
      {
        question: '如何查看审稿意见？',
        answer: '在个人中心的"我的投稿"中，点击对应稿件，即可查看详细的审稿意见。'
      }
    ]
  },
  {
    id: 3,
    category: '账号管理',
    questions: [
      {
        question: '如何注册账号？',
        answer: '点击平台右上角的"注册"按钮，填写相关信息即可注册账号。'
      },
      {
        question: '忘记密码怎么办？',
        answer: '在登录页面点击"忘记密码"，按照提示重置密码。'
      },
      {
        question: '如何修改个人信息？',
        answer: '登录后进入"个人中心"->"个人信息"，点击"编辑信息"即可修改。'
      },
      {
        question: '如何升级账号角色？',
        answer: '联系平台管理员，提供相关资质证明，审核通过后可以升级角色。'
      }
    ]
  }
])

// 当前展开的问题ID
const expandedQuestion = ref(null)

// 切换问题展开状态
const toggleQuestion = (id) => {
  expandedQuestion.value = expandedQuestion.value === id ? null : id
}
</script>

<template>
  <div class="faq-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'faq'"
      :toggle-directory="toggleDirectory"
      :logout="userStore.logout"
    />

    <!-- 常见问题内容 -->
    <main class="main-content">
      <div class="faq-wrapper">
        <div class="header">
          <h1>常见问题</h1>
          <p class="subtitle">解答您在使用平台过程中遇到的常见问题</p>
        </div>

        <section class="faq-section">
          <div class="faq-content">
            <div 
              v-for="faqCategory in faqs" 
              :key="faqCategory.id" 
              class="faq-category"
            >
              <h2 class="category-title">{{ faqCategory.category }}</h2>
              <div class="faq-list">
                <div 
                  v-for="(question, index) in faqCategory.questions" 
                  :key="index" 
                  class="faq-item"
                >
                  <div class="faq-question" @click="toggleQuestion(`${faqCategory.id}-${index}`)">
                    <h3 class="question-text">{{ question.question }}</h3>
                    <span class="toggle-icon" :class="{ 'expanded': expandedQuestion === `${faqCategory.id}-${index}` }">
                      ▼
                    </span>
                  </div>
                  <div class="faq-answer" v-if="expandedQuestion === `${faqCategory.id}-${index}`">
                    <p>{{ question.answer }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.faq-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 主内容样式 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  text-align: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 1rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* FAQ 部分样式 */
.faq-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.faq-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

/* 分类标题样式 */
.faq-category {
  margin-bottom: 2.5rem;
}

.category-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

/* FAQ 列表样式 */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* FAQ 项样式 */
.faq-item {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.faq-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 问题样式 */
.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.faq-question:hover {
  background-color: #e3f2fd;
}

.question-text {
  font-size: 1.1rem;
  color: #2c3e50;
  margin: 0;
  font-weight: 500;
  flex: 1;
}

/* 切换图标样式 */
.toggle-icon {
  font-size: 0.9rem;
  color: #7f8c8d;
  transition: transform 0.3s ease;
  margin-left: 1rem;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
  color: #3498db;
}

/* 答案样式 */
.faq-answer {
  padding: 1.5rem;
  background-color: white;
  border-top: 1px solid #e9ecef;
}

.faq-answer p {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

/* 页脚样式 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.6rem;
  }
  
  .faq-section {
    padding: 1.5rem;
  }
  
  .category-title {
    font-size: 1.3rem;
  }
  
  .faq-question {
    padding: 1.2rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .question-text {
    font-size: 1rem;
  }
  
  .toggle-icon {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .faq-answer {
    padding: 1.2rem;
  }
}
</style>