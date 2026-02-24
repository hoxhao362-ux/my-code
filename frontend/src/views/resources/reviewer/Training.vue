<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-reviewer-training'"
      :logout="userStore.logout"
    />
    <div class="guide-area">
      <h1>Reviewer Training Course</h1>
      
      <div class="module">
        <h2>Module 1: Core Principles</h2>
        <p>Peer review is the cornerstone of scientific publishing. It ensures that published research is valid, significant, and original.</p>
        <div class="image-box">
          [Schematic: The Peer Review Cycle]
        </div>
      </div>

      <div class="module">
        <h2>Module 2: Methodology Assessment</h2>
        <p>Reviewers must rigorously evaluate the study design. Common pitfalls include:</p>
        <ul>
          <li><strong>Selection Bias:</strong> Is the sample representative?</li>
          <li><strong>Confounding Variables:</strong> Were they controlled?</li>
          <li><strong>Statistical Power:</strong> Is the sample size sufficient?</li>
        </ul>
        <div class="case-study error">
          <strong>Wrong:</strong> "The study is good." (Too vague)
        </div>
        <div class="case-study correct">
          <strong>Right:</strong> "The study addresses a key gap, but the sample size (n=10) is insufficient to draw robust conclusions."
        </div>
      </div>

      <div class="module">
        <h2>Module 3: Writing the Report</h2>
        <p>Structure your report clearly:</p>
        <ol>
          <li><strong>Summary:</strong> Brief overview of the paper.</li>
          <li><strong>Major Comments:</strong> Critical flaws or concerns.</li>
          <li><strong>Minor Comments:</strong> Typos, formatting, clarification.</li>
        </ol>
      </div>

      <div class="action-box">
        <label>
          <input type="checkbox" v-model="guideCompleted" />
          I have read and understood the training materials.
        </label>
      </div>
    </div>

    <div class="quiz-area">
      <div v-if="!guideCompleted" class="quiz-locked">
        <h3>Quiz Locked</h3>
        <p>Please complete the training guide to unlock the assessment.</p>
      </div>

      <div v-else class="quiz-content">
        <h2>Certification Quiz</h2>
        <p class="quiz-info">Pass mark: 80% (8/10)</p>

        <div v-if="!quizSubmitted">
          <div v-for="(q, index) in questions" :key="q.id" class="question-item">
            <p class="question-text">{{ index + 1 }}. {{ q.text }}</p>
            <div class="options">
              <label v-for="opt in q.options" :key="opt.value" class="option-label">
                <input type="radio" :name="'q'+q.id" :value="opt.value" v-model="answers[q.id]" />
                {{ opt.text }}
              </label>
            </div>
          </div>
          <button class="btn-submit" @click="submitQuiz">Submit Answers</button>
        </div>

        <div v-else class="quiz-result">
          <div class="score-circle" :class="{ pass: score >= 80, fail: score < 80 }">
            {{ score }}%
          </div>
          <h3>{{ score >= 80 ? 'Congratulations!' : 'Please Try Again' }}</h3>
          <p>{{ score >= 80 ? 'You have passed the reviewer training.' : 'You need 80% to pass.' }}</p>
          
          <div class="review-answers">
            <div v-for="(q, index) in questions" :key="q.id" class="review-item">
              <p><strong>{{ index + 1 }}. {{ q.text }}</strong></p>
              <p :class="{ correct: answers[q.id] === q.correct, incorrect: answers[q.id] !== q.correct }">
                Your answer: {{ getOptionText(q, answers[q.id]) }}
                <span v-if="answers[q.id] !== q.correct"> (Correct: {{ getOptionText(q, q.correct) }})</span>
              </p>
              <p class="explanation">{{ q.explanation }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const guideCompleted = ref(false)
const quizSubmitted = ref(false)
const score = ref(0)
const answers = reactive({})

const questions = [
  {
    id: 1,
    text: "What is the primary purpose of peer review?",
    options: [
      { value: 'a', text: 'To correct grammar mistakes' },
      { value: 'b', text: 'To ensure validity and quality' },
      { value: 'c', text: 'To delay publication' }
    ],
    correct: 'b',
    explanation: "Peer review acts as a quality control filter for scientific literature."
  },
  {
    id: 2,
    text: "How should you handle a Conflict of Interest?",
    options: [
      { value: 'a', text: 'Ignore it if it is minor' },
      { value: 'b', text: 'Decline the invitation' },
      { value: 'c', text: 'Mention it in the report but review anyway' }
    ],
    correct: 'b',
    explanation: "Any potential bias compromises the integrity of the review."
  },
  // Adding placeholders for 3-10 to meet the "10 questions" requirement
  { id: 3, text: "Is the reviewer's identity revealed to the author?", options: [{value:'a', text:'Yes'}, {value:'b', text:'No (Double-blind)'}], correct: 'b', explanation: "Journal Platform uses double-blind peer review." },
  { id: 4, text: "What should be the tone of the report?", options: [{value:'a', text:'Aggressive'}, {value:'b', text:'Constructive and professional'}], correct: 'b', explanation: "Comments should be helpful, not hostile." },
  { id: 5, text: "Can you share the manuscript with a colleague?", options: [{value:'a', text:'Yes, for help'}, {value:'b', text:'No, it is confidential'}], correct: 'b', explanation: "Manuscripts are confidential documents." },
  { id: 6, text: "Which section explains the study design?", options: [{value:'a', text:'Methods'}, {value:'b', text:'Discussion'}], correct: 'a', explanation: "Methods section details how the study was conducted." },
  { id: 7, text: "If you suspect plagiarism, what should you do?", options: [{value:'a', text:'Accuse the author'}, {value:'b', text:'Notify the editor confidentially'}], correct: 'b', explanation: "Let the editor investigate potential misconduct." },
  { id: 8, text: "Should you recommend acceptance based on language alone?", options: [{value:'a', text:'Yes'}, {value:'b', text:'No, science comes first'}], correct: 'b', explanation: "Scientific content is more important than language proficiency." },
  { id: 9, text: "What is a 'Major Revision'?", options: [{value:'a', text:'Typos'}, {value:'b', text:'Fundamental flaws or missing experiments'}], correct: 'b', explanation: "Major revisions require significant work." },
  { id: 10, text: "Is the reviewer responsible for copy-editing?", options: [{value:'a', text:'Yes'}, {value:'b', text:'No'}], correct: 'b', explanation: "Copy-editing is done by the publisher." }
]

const getOptionText = (q, val) => {
  const opt = q.options.find(o => o.value === val)
  return opt ? opt.text : 'No Answer'
}

const submitQuiz = () => {
  let correctCount = 0
  questions.forEach(q => {
    if (answers[q.id] === q.correct) {
      correctCount++
    }
  })
  score.value = (correctCount / questions.length) * 100
  quizSubmitted.value = true
  
  // Save result mock
  console.log('Quiz saved to profile:', score.value)
}
</script>

<style scoped>
.page-container {
  display: flex;
  min-height: 100vh;
  padding-top: 0;
  margin-top: 80px;
}

.guide-area {
  width: 70%;
  padding: 48px;
  background-color: white;
}

.module {
  margin-bottom: 40px;
}

.module h2 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}

.module p, .module li {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.image-box {
  background-color: #F5F5F5;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 16px 0;
  color: #999;
}

.case-study {
  padding: 12px;
  border-radius: 4px;
  margin-top: 12px;
  font-size: 14px;
}

.case-study.error {
  background-color: #FFF0F0;
  color: #dc3545;
}

.case-study.correct {
  background-color: #F0FFF0;
  color: #2E8B57;
}

.action-box {
  margin-top: 40px;
  padding: 20px;
  background-color: #F9F9F9;
  border: 1px solid #E5E5E5;
}

.quiz-area {
  width: 30%;
  padding: 48px 24px;
  background-color: #F5F5F5;
  border-left: 1px solid #E5E5E5;
  position: fixed;
  right: 0;
  height: calc(100vh - 80px);
  top: 80px;
  overflow-y: auto;
}

.quiz-locked {
  text-align: center;
  color: #999;
  margin-top: 100px;
}

.quiz-content h2 {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
}

.quiz-info {
  font-size: 12px;
  color: #666;
  margin-bottom: 24px;
}

.question-item {
  margin-bottom: 24px;
}

.question-text {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 8px;
}

.option-label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
  cursor: pointer;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background-color: #0056B3;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 24px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 20px;
  border: 4px solid;
}

.score-circle.pass {
  border-color: #2E8B57;
  color: #2E8B57;
}

.score-circle.fail {
  border-color: #dc3545;
  color: #dc3545;
}

.quiz-result {
  text-align: center;
}

.review-answers {
  text-align: left;
  margin-top: 32px;
}

.review-item {
  margin-bottom: 20px;
  border-bottom: 1px solid #E5E5E5;
  padding-bottom: 12px;
}

.correct { color: #2E8B57; }
.incorrect { color: #dc3545; }
.explanation { font-size: 12px; color: #666; margin-top: 4px; font-style: italic; }

@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }
  .quiz-area {
    width: 100%;
    position: relative;
    height: auto;
    top: 0;
  }
  .guide-area {
    width: 100%;
  }
}
</style>
