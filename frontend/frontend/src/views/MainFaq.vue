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
    category: 'Submission Process',
    questions: [
      {
        question: 'How to submit a manuscript?',
        answer: 'After logging in, click "Submission Center" -> "Online Submission" in the top navigation bar, fill in the paper information and submit.'
      },
      {
        question: 'What format is required for submission?',
        answer: 'Please refer to the format requirements in "Submission Center" -> "Submission Guidelines", including title, abstract, keywords, main text and other format specifications.'
      },
      {
        question: 'Can I submit multiple papers at the same time?',
        answer: 'Yes, the platform supports submitting multiple papers at the same time, each paper needs to be submitted separately.'
      },
      {
        question: 'Can I modify my submission after submission?',
        answer: 'After submission, you can check the manuscript status in your personal center during the review process, and modifications are supported in some cases.'
      }
    ]
  },
  {
    id: 2,
    category: 'Manuscript Tracking',
    questions: [
      {
        question: 'How to check manuscript status?',
        answer: 'After logging in, enter "Personal Center" and you can check the status of all submissions in "My Submissions".'
      },
      {
        question: 'What is the typical review period?',
        answer: 'The review period is generally 1-2 weeks, the specific time depends on the manuscript situation and reviewer arrangement.'
      },
      {
        question: 'If my manuscript is rejected, can I submit it again?',
        answer: 'Yes, after modifying according to the review comments, you can submit it again.'
      },
      {
        question: 'How to view review comments?',
        answer: 'In "My Submissions" in your personal center, click on the corresponding manuscript to view detailed review comments.'
      }
    ]
  },
  {
    id: 3,
    category: 'Account Management',
    questions: [
      {
        question: 'How to register an account?',
        answer: 'Click the "Register" button in the upper right corner of the platform and fill in the relevant information to register an account.'
      },
      {
        question: 'What to do if I forget my password?',
        answer: 'Click "Forgot Password" on the login page and follow the instructions to reset your password.'
      },
      {
        question: 'How to modify personal information?',
        answer: 'After logging in, enter "Personal Center" -> "Personal Information", click "Edit Information" to modify.'
      },
      {
        question: 'How to upgrade account role?',
        answer: 'Contact the platform administrator, provide relevant qualification certificates, and the role can be upgraded after approval.'
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
          <h1>Frequently Asked Questions</h1>
          <p class="subtitle">Answers to common questions you may encounter while using the platform</p>
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
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
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
  margin: 100px auto 0;
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