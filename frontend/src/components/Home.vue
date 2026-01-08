<script setup>
import { ref, watch } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'logout', 'journals', 'modules', 'incrementJournalView', 'showDirectory', 'toggleDirectory'])

// 虚拟数据模拟平台统计
const stats = ref({
  totalJournals: 1256,
  pendingReviews: 89,
  totalUsers: 2345,
  recentSubmissions: 45
})

// 模拟论文数据库，用于搜索功能
const allJournals = ref([
  { 
    id: 1, 
    title: '基于深度学习的医学图像分析', 
    author: '张三', 
    date: '2024-01-01', 
    status: '待审核',
    abstract: '本文探讨了深度学习在医学图像分析中的应用，包括图像分类、目标检测和分割等技术，并通过实验验证了其有效性。',
    keywords: ['深度学习', '医学图像', '图像分析'],
    content: '<h3>摘要</h3><p>本文探讨了深度学习在医学图像分析中的应用，包括图像分类、目标检测和分割等技术，并通过实验验证了其有效性。</p><h3>引言</h3><p>医学图像分析是医学领域的重要研究方向，随着深度学习技术的发展，其在医学图像分析中的应用越来越广泛。</p><h3>方法</h3><p>本文采用卷积神经网络（CNN）进行医学图像分析，包括数据预处理、模型训练和评估等步骤。</p><h3>结果</h3><p>实验结果表明，深度学习方法在医学图像分析中取得了良好的效果，准确率达到了95%以上。</p><h3>结论</h3><p>深度学习技术在医学图像分析中具有广阔的应用前景，未来可以进一步提高模型的性能和泛化能力。</p>'
  },
  { 
    id: 2, 
    title: '新型药物研发进展', 
    author: '李四', 
    date: '2024-01-02', 
    status: '审核中',
    abstract: '本文综述了近年来新型药物研发的进展，包括小分子药物、生物药物和基因治疗等领域，并展望了未来的发展方向。',
    keywords: ['药物研发', '小分子药物', '生物药物', '基因治疗'],
    content: '<h3>摘要</h3><p>本文综述了近年来新型药物研发的进展，包括小分子药物、生物药物和基因治疗等领域，并展望了未来的发展方向。</p><h3>引言</h3><p>药物研发是医药行业的核心环节，随着科学技术的发展，新型药物不断涌现，为疾病治疗提供了更多选择。</p><h3>小分子药物</h3><p>小分子药物是传统的药物类型，具有分子量小、易于合成和口服给药等优点，近年来在靶点发现和药物设计方面取得了重要进展。</p><h3>生物药物</h3><p>生物药物包括抗体药物、蛋白质药物和核酸药物等，具有特异性强、疗效好等优点，是当前药物研发的热点领域。</p><h3>基因治疗</h3><p>基因治疗是一种新兴的治疗方法，通过修复或替换缺陷基因来治疗疾病，具有广阔的应用前景。</p><h3>结论</h3><p>新型药物研发的进展为疾病治疗带来了新的希望，未来需要进一步加强基础研究和临床转化，推动药物研发的发展。</p>'
  },
  { 
    id: 3, 
    title: '临床研究方法学探讨', 
    author: '王五', 
    date: '2024-01-03', 
    status: '已通过',
    abstract: '本文系统介绍了临床研究的基本方法和设计原则，包括随机对照试验、队列研究、病例对照研究等，并讨论了临床研究中的伦理问题。',
    keywords: ['临床研究', '方法学', '随机对照试验', '伦理'],
    content: '<h3>摘要</h3><p>本文系统介绍了临床研究的基本方法和设计原则，包括随机对照试验、队列研究、病例对照研究等，并讨论了临床研究中的伦理问题。</p><h3>引言</h3><p>临床研究是验证药物和治疗方法有效性和安全性的重要手段，其方法学的科学性直接影响研究结果的可靠性。</p><h3>临床研究设计</h3><p>临床研究设计包括研究类型、样本量计算、随机化方法、盲法设计等，不同的研究设计适用于不同的研究目的。</p><h3>随机对照试验</h3><p>随机对照试验是临床研究的金标准，通过随机分组和盲法设计，减少偏倚，提高研究结果的可靠性。</p><h3>队列研究</h3><p>队列研究是一种观察性研究方法，通过随访暴露组和非暴露组，观察疾病的发生情况，用于研究病因和预后。</p><h3>病例对照研究</h3><p>病例对照研究是一种回顾性研究方法，通过比较病例组和对照组的暴露情况，探讨疾病的危险因素。</p><h3>伦理问题</h3><p>临床研究中的伦理问题包括知情同意、隐私保护、风险受益比等，需要严格遵循伦理原则。</p><h3>结论</h3><p>临床研究方法学的不断完善和发展，为提高临床研究质量和推动医学进步提供了重要保障。</p>'
  },
  { 
    id: 4, 
    title: '公共卫生政策分析', 
    author: '赵六', 
    date: '2024-01-04', 
    status: '已拒绝',
    abstract: '本文分析了当前公共卫生政策的现状和存在的问题，并提出了相应的改进建议，旨在提高公共卫生服务的质量和可及性。',
    keywords: ['公共卫生', '政策分析', '卫生服务', '改进建议'],
    content: '<h3>摘要</h3><p>本文分析了当前公共卫生政策的现状和存在的问题，并提出了相应的改进建议，旨在提高公共卫生服务的质量和可及性。</p><h3>引言</h3><p>公共卫生政策是保障公众健康的重要手段，其制定和实施直接影响公共卫生服务的质量和效果。</p><h3>公共卫生政策现状</h3><p>当前公共卫生政策在疾病预防控制、卫生监督、健康教育等方面取得了一定成绩，但仍存在一些问题，如政策执行不到位、资源分配不均等。</p><h3>存在的问题</h3><p>公共卫生政策存在的问题包括政策制定缺乏科学性、政策执行机制不完善、公众参与度不高等。</p><h3>改进建议</h3><p>针对存在的问题，提出了加强政策科学性、完善执行机制、提高公众参与度等改进建议。</p><h3>结论</h3><p>公共卫生政策的不断完善和优化，对于提高公共卫生服务质量、保障公众健康具有重要意义。</p>'
  },
  { 
    id: 5, 
    title: '生物信息学在医学研究中的应用', 
    author: '孙七', 
    date: '2024-01-05', 
    status: '已通过',
    abstract: '本文介绍了生物信息学在医学研究中的应用，包括基因组学、蛋白质组学和代谢组学等领域，并讨论了其在疾病诊断和治疗中的潜力。',
    keywords: ['生物信息学', '基因组学', '蛋白质组学', '代谢组学', '疾病诊断'],
    content: '<h3>摘要</h3><p>本文介绍了生物信息学在医学研究中的应用，包括基因组学、蛋白质组学和代谢组学等领域，并讨论了其在疾病诊断和治疗中的潜力。</p><h3>引言</h3><p>生物信息学是一门新兴的交叉学科，通过整合生物学、计算机科学和统计学等知识，分析和解读生物数据，为医学研究提供了新的方法和思路。</p><h3>基因组学应用</h3><p>基因组学研究通过分析基因组序列，揭示疾病的遗传基础，为个性化医疗提供了基础。</p><h3>蛋白质组学应用</h3><p>蛋白质组学研究通过分析蛋白质的表达和功能，探讨疾病的发病机制，为药物研发提供了靶点。</p><h3>代谢组学应用</h3><p>代谢组学研究通过分析代谢物的变化，监测疾病的进展和治疗效果，为临床诊断提供了新的 biomarkers。</p><h3>结论</h3><p>生物信息学在医学研究中的应用前景广阔，未来将在疾病诊断、治疗和预防等方面发挥越来越重要的作用。</p>'
  },
  { 
    id: 6, 
    title: '人工智能在医疗领域的应用现状与挑战', 
    author: '周八', 
    date: '2024-01-06', 
    status: '审核中',
    abstract: '本文综述了人工智能在医疗领域的应用现状，包括医学影像分析、辅助诊断、药物研发等方面，并分析了其面临的挑战和未来发展方向。',
    keywords: ['人工智能', '医疗领域', '医学影像', '辅助诊断', '药物研发'],
    content: '<h3>摘要</h3><p>本文综述了人工智能在医疗领域的应用现状，包括医学影像分析、辅助诊断、药物研发等方面，并分析了其面临的挑战和未来发展方向。</p><h3>引言</h3><p>人工智能技术的快速发展为医疗领域带来了新的机遇和挑战，其在医学影像分析、辅助诊断、药物研发等方面的应用不断深入。</p><h3>医学影像分析</h3><p>人工智能在医学影像分析中的应用包括图像分类、目标检测和分割等，能够提高诊断效率和准确性。</p><h3>辅助诊断</h3><p>人工智能辅助诊断系统通过分析患者的临床数据和影像资料，提供诊断建议，有助于提高诊断的准确性和一致性。</p><h3>药物研发</h3><p>人工智能在药物研发中的应用包括靶点发现、药物设计和临床试验优化等，能够缩短药物研发周期，降低研发成本。</p><h3>挑战与展望</h3><p>人工智能在医疗领域的应用面临着数据质量、算法可解释性、伦理和法律等挑战，未来需要加强跨学科合作，推动人工智能技术在医疗领域的健康发展。</p><h3>结论</h3><p>人工智能技术在医疗领域的应用前景广阔，将为医疗行业带来革命性的变化，但需要克服一系列挑战，确保其安全、有效和可持续发展。</p>'
  }
])

// 近期投稿列表（取前4条）
const recentJournals = ref(allJournals.value.slice(0, 4))

// 搜索相关状态
const searchKeyword = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const selectedJournal = ref(null)
const showJournalContent = ref(false)

// 搜索处理函数
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  searchResults.value = allJournals.value.filter(journal => 
    journal.title.toLowerCase().includes(keyword) ||
    journal.author.toLowerCase().includes(keyword) ||
    journal.abstract.toLowerCase().includes(keyword) ||
    journal.keywords.some(k => k.toLowerCase().includes(keyword))
  )
  showSearchResults.value = true
  showJournalContent.value = false
  selectedJournal.value = null
}

// 在线阅读论文
const readJournal = (journal) => {
  selectedJournal.value = journal
  showJournalContent.value = true
  showSearchResults.value = false
}

// 关闭论文内容
const closeJournalContent = () => {
  showJournalContent.value = false
  selectedJournal.value = null
}

const goToSubmit = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('submit')
}

const goToReview = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('review')
}

const goToProfile = () => {
  // 调用父组件传递的导航方法
  props.navigateTo('profile')
}

const handleLogout = () => {
  // 调用父组件传递的登出方法
  props.logout()
}





// 查看论文详情（更新阅读量）
const viewJournalDetail = (id) => {
  props.incrementJournalView(id)
  props.navigateTo('journal', id)
}
</script>

<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link active">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="toggleDirectory">目录</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goToSubmit">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="goToReview">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="goToProfile">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 首页内容 -->
    <main class="main-content">
      <!-- 平台统计 -->
      <section class="stats-section">
        <h2 class="section-title">平台统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalJournals }}</h3>
              <p class="stat-label">总投稿量</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.pendingReviews }}</h3>
              <p class="stat-label">待审核稿件</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.totalUsers }}</h3>
              <p class="stat-label">注册用户</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <h3 class="stat-number">{{ stats.recentSubmissions }}</h3>
              <p class="stat-label">近期投稿</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 论文检索 -->
      <section class="search-section">
        <div class="search-container">
          <h2 class="section-title">论文检索</h2>
          <div class="search-bar">
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="请输入关键词搜索论文..."
              class="search-input"
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">
              <span class="search-icon">🔍</span> 搜索
            </button>
          </div>
          
          <!-- 搜索结果展示 -->
          <div v-if="showSearchResults" class="search-results">
            <div class="results-header">
              <h3>搜索结果 ({{ searchResults.length }})</h3>
              <button class="close-btn" @click="showSearchResults = false">×</button>
            </div>
            <div v-if="searchResults.length > 0" class="results-list">
              <div 
                v-for="journal in searchResults" 
                :key="journal.id" 
                class="result-item"
              >
                <div class="result-info">
                  <h4 class="result-title">{{ journal.title }}</h4>
                  <p class="result-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
                  <p class="result-abstract">{{ journal.abstract }}</p>
                  <div class="result-keywords">
                    <span 
                      v-for="(keyword, index) in journal.keywords" 
                      :key="index" 
                      class="keyword-tag"
                    >
                      {{ keyword }}
                    </span>
                  </div>
                </div>
                <div class="result-actions">
                  <button 
                    class="action-btn read-btn" 
                    @click="readJournal(journal)"
                  >
                    在线阅读
                  </button>
                  <button 
                    class="action-btn detail-btn" 
                    @click="viewJournalDetail(journal.id)"
                  >
                    查看详情
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="no-results">
              <p>没有找到匹配的论文</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 论文在线阅读 -->
      <section v-if="showJournalContent && selectedJournal" class="journal-content-section">
        <div class="journal-content-container">
          <div class="journal-header">
            <h2 class="journal-title">{{ selectedJournal.title }}</h2>
            <button class="close-btn" @click="closeJournalContent">×</button>
          </div>
          <div class="journal-meta">
            <p>作者：{{ selectedJournal.author }} | 投稿日期：{{ selectedJournal.date }}</p>
            <div class="journal-keywords">
              <span 
                v-for="(keyword, index) in selectedJournal.keywords" 
                :key="index" 
                class="keyword-tag"
              >
                {{ keyword }}
              </span>
            </div>
          </div>
          <div class="journal-content" v-html="selectedJournal.content"></div>
        </div>
      </section>

      <!-- 近期投稿 -->
      <section class="journals-section">
        <div class="section-header">
          <h2 class="section-title">近期投稿</h2>
          <button class="submit-btn" @click="goToSubmit">+ 新投稿</button>
        </div>
        <div class="journals-list">
          <div 
            v-for="journal in recentJournals" 
            :key="journal.id" 
            class="journal-item"
          >
            <div class="journal-info">
              <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h3>
              <p class="journal-meta">作者：{{ journal.author }} | 投稿日期：{{ journal.date }}</p>
            </div>
            <div class="journal-status" :class="journal.status.toLowerCase()">
              {{ journal.status }}
            </div>
          </div>
        </div>
      </section>

      <!-- 平台介绍 -->
      <section class="intro-section">
        <h2 class="section-title">关于我们</h2>
        <div class="intro-content">
          <p>本平台是一个专业的期刊投稿系统，致力于为科研人员提供便捷、高效的投稿体验。我们支持多种类型的学术论文投稿，包括基础研究、临床研究、综述等。</p>
          <p>平台拥有严格的审稿流程，确保每一篇投稿都能得到专业、公正的评审。同时，我们提供实时的投稿状态查询，让作者能够随时了解稿件的处理进展。</p>
        </div>
      </section>
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
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo h1 {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #3498db;
}

.nav-link.logout {
  color: #e74c3c;
}

.nav-link.logout:hover {
  color: #c0392b;
}

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

/* 统计部分 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.stat-label {
  color: #7f8c8d;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

/* 近期投稿 */
.journals-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.submit-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.journals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.journal-item:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.journal-info {
  flex: 1;
}

.journal-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.journal-meta {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
}

.journal-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  min-width: 80px;
}

.journal-status.待审核 {
  background: #f39c12;
  color: white;
}

.journal-status.审核中 {
  background: #3498db;
  color: white;
}

.journal-status.已通过 {
  background: #2ecc71;
  color: white;
}

.journal-status.已拒绝 {
  background: #e74c3c;
  color: white;
}

/* 论文检索样式 */
.search-section {
  margin-bottom: 2rem;
}

.search-container {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.search-icon {
  font-size: 1.1rem;
}

/* 搜索结果样式 */
.search-results {
  margin-top: 1.5rem;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  background: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 1rem;
  transition: all 0.3s ease;
}

.result-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

.result-info {
  flex: 1;
}

.result-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.result-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

.result-abstract {
  font-size: 0.95rem;
  color: #555;
  margin: 0 0 0.75rem 0;
  line-height: 1.5;
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 3;
  -moz-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
}

.result-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.keyword-tag {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
  justify-content: flex-start;
  min-width: 120px;
}

.action-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.read-btn {
  background: #27ae60;
  color: white;
}

.read-btn:hover {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.detail-btn {
  background: #95a5a6;
  color: white;
}

.detail-btn:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  font-style: italic;
}

/* 论文在线阅读样式 */
.journal-content-section {
  margin-bottom: 2rem;
}

.journal-content-container {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.journal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.journal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  line-height: 1.3;
}

.journal-meta {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.journal-meta p {
  font-size: 1rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

.journal-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.journal-content {
  color: #333;
  line-height: 1.8;
  font-size: 1rem;
}

.journal-content h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin: 1.5rem 0 1rem 0;
  font-weight: 600;
}

.journal-content p {
  margin: 0 0 1rem 0;
  text-align: justify;
}

/* 平台介绍 */
.intro-section {
  margin-bottom: 2rem;
}

.intro-content {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.intro-content p {
  margin-bottom: 1rem;
  color: #555;
  line-height: 1.6;
}

/* 目录功能样式 */
.directory-section {
  margin-bottom: 2rem;
}

.directory-container {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.filters-container {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
  background: white;
}

.filter-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.journals-directory {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.journal-directory-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.journal-directory-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #3498db;
}

.journal-directory-info {
  flex: 1;
}

.journal-directory-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.journal-directory-title:hover {
  color: #3498db;
  text-decoration: underline;
}

.journal-directory-meta {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.75rem 0;
}

.journal-directory-abstract {
  font-size: 0.95rem;
  color: #555;
  margin: 0 0 1rem 0;
  line-height: 1.5;
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 3;
  -moz-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
}

.journal-directory-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.journal-directory-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
  justify-content: flex-start;
  min-width: 120px;
}

.no-journals {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #e0e0e0;
}

/* 页脚 */
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
</style>
