<script setup>
import { ref, computed } from 'vue'

// 接收App.vue传递的上下文
const props = defineProps(['user', 'navigateTo', 'journalId', 'logout'])

// 模拟稿件数据
const journalData = [
  { 
    id: 1, 
    title: '基于深度学习的医学图像分析', 
    author: '张三', 
    date: '2024-01-01', 
    status: '待审核',
    abstract: '本文提出了一种基于深度学习的医学图像分析方法，能够有效地识别和分类医学图像中的病变区域。该方法采用卷积神经网络架构，通过大量的医学图像数据进行训练，取得了较高的识别准确率。本文还探讨了该方法在临床应用中的前景和挑战。',
    keywords: '深度学习,医学图像,卷积神经网络,病变识别',
    content: '1. 引言\n医学图像分析是现代医学诊断的重要组成部分，传统的医学图像分析主要依赖于医生的经验和专业知识，存在主观性强、效率低等问题。随着人工智能技术的发展，深度学习在医学图像分析领域展现出了巨大的潜力。\n\n2. 相关工作\n近年来，深度学习在医学图像分析领域取得了一系列重要成果。卷积神经网络（CNN）在图像分类、目标检测等任务中表现出色，被广泛应用于医学图像分析。\n\n3. 方法\n本文提出的方法基于改进的卷积神经网络架构，主要包括以下几个部分：数据预处理、网络架构设计、模型训练和评估。\n\n4. 实验结果\n实验结果表明，本文提出的方法在医学图像分类任务中取得了较高的准确率，优于传统的机器学习方法和其他深度学习方法。\n\n5. 结论\n本文提出了一种基于深度学习的医学图像分析方法，通过实验验证了该方法的有效性。该方法具有较高的识别准确率和良好的泛化能力，有望在临床应用中发挥重要作用。' 
  },
  { 
    id: 2, 
    title: '新型药物研发进展', 
    author: '李四', 
    date: '2024-01-02', 
    status: '待审核',
    abstract: '本文综述了近年来新型药物研发的进展，包括小分子药物、生物制品和基因治疗药物等方面。随着科学技术的发展，药物研发的方法和手段不断创新，为重大疾病的治疗带来了新的希望。',
    keywords: '药物研发,小分子药物,生物制品,基因治疗',
    content: '1. 引言\n药物研发是医药行业的核心，对于保障人类健康具有重要意义。近年来，随着生命科学和技术的快速发展，药物研发领域发生了深刻的变化。\n\n2. 小分子药物研发\n小分子药物是传统的药物类型，具有分子量小、口服生物利用度高等优点。近年来，计算机辅助药物设计、高通量筛选等技术的应用，加速了小分子药物的研发进程。\n\n3. 生物制品研发\n生物制品包括抗体药物、疫苗、细胞治疗等，具有特异性强、疗效好等优点。近年来，单克隆抗体、CAR-T细胞治疗等生物制品在癌症治疗中取得了突破性进展。\n\n4. 基因治疗药物研发\n基因治疗是一种新兴的治疗手段，通过修复或替换缺陷基因来治疗疾病。近年来，基因编辑技术的发展为基因治疗带来了新的机遇。\n\n5. 结论\n药物研发领域正处于快速发展时期，各种新技术、新方法的应用为药物研发带来了新的活力。未来，随着科学技术的不断进步，将会有更多的创新药物问世，为人类健康事业做出更大的贡献。' 
  },
  { 
    id: 3, 
    title: '临床研究方法学探讨', 
    author: '王五', 
    date: '2024-01-03', 
    status: '待审核',
    abstract: '本文探讨了临床研究中的方法学问题，包括研究设计、样本量计算、数据收集和统计分析等方面。科学合理的研究方法是保证临床研究质量的关键。',
    keywords: '临床研究,研究设计,样本量,统计分析',
    content: '1. 引言\n临床研究是医学科学发展的重要动力，对于验证医学假设、评价治疗效果具有重要意义。临床研究的质量直接影响研究结果的可靠性和临床应用价值。\n\n2. 研究设计\n研究设计是临床研究的核心，包括随机对照试验、队列研究、病例对照研究等多种类型。不同的研究设计适用于不同的研究问题，研究者需要根据研究目的选择合适的研究设计。\n\n3. 样本量计算\n样本量计算是临床研究设计中的重要环节，直接影响研究的检验效能和结果的可靠性。样本量计算需要考虑研究设计类型、主要终点指标、预期效应大小、检验水准和检验效能等因素。\n\n4. 数据收集\n数据收集是临床研究的重要组成部分，包括研究对象的选择、基线数据的收集、随访数据的记录等。数据收集需要遵循标准化、规范化的原则，确保数据的准确性和完整性。\n\n5. 统计分析\n统计分析是临床研究的重要环节，包括描述性统计分析、推断性统计分析等。统计分析需要根据研究设计类型和数据类型选择合适的统计方法，确保分析结果的可靠性和科学性。\n\n6. 结论\n临床研究方法学是临床研究的重要基础，对于保证研究质量具有关键作用。研究者需要不断学习和掌握新的研究方法和技术，提高临床研究的质量和水平。' 
  }
]

// 根据journalId获取当前显示的稿件
const journal = computed(() => {
  return journalData.find(item => item.id === props.journalId) || journalData[0]
})

const goBack = () => {
  // 返回上一页
  props.navigateTo('home')
}
</script>

<template>
  <div class="journal-detail-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-logo">
          <h1>期刊投稿平台</h1>
        </div>
        <ul class="navbar-menu">
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('home')">首页</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('submit')">投稿</a></li>
          <li v-if="user?.role === 'admin'" class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('review')">审稿</a></li>
          <li class="nav-item"><a href="#" class="nav-link" @click.prevent="navigateTo('profile')">个人中心</a></li>
          <li class="nav-item"><a href="#" class="nav-link logout" @click.prevent="logout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <!-- 稿件详情内容 -->
    <main class="journal-detail-content">
      <div class="journal-detail-wrapper">
        <button class="back-btn" @click="goBack">← 返回</button>
        
        <div class="journal-detail-header">
          <h2 class="journal-title">{{ journal.title }}</h2>
          <div class="journal-meta">
            <span class="meta-item">作者：{{ journal.author }}</span>
            <span class="meta-item">投稿日期：{{ journal.date }}</span>
            <span class="meta-item status" :class="journal.status.toLowerCase()">{{ journal.status }}</span>
          </div>
        </div>

        <div class="journal-detail-body">
          <section class="detail-section">
            <h3 class="section-title">摘要</h3>
            <p class="section-content">{{ journal.abstract }}</p>
          </section>

          <section class="detail-section">
            <h3 class="section-title">关键词</h3>
            <p class="section-content keywords">{{ journal.keywords }}</p>
          </section>

          <section class="detail-section">
            <h3 class="section-title">正文</h3>
            <div class="section-content content">
              <pre>{{ journal.content }}</pre>
            </div>
          </section>
        </div>
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
.journal-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 导航栏样式（与其他页面保持一致） */
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

/* 稿件详情内容 */
.journal-detail-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

.journal-detail-wrapper {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.back-btn:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
}

.journal-detail-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #eee;
}

.journal-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.journal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.meta-item {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.meta-item.status {
  font-weight: 600;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
}

.meta-item.待审核 {
  background: #fff3cd;
  color: #856404;
}

.meta-item.审核中 {
  background: #cce7ff;
  color: #004085;
}

.meta-item.已通过 {
  background: #d4edda;
  color: #155724;
}

.meta-item.已拒绝 {
  background: #f8d7da;
  color: #721c24;
}

/* 详情内容 */
.journal-detail-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-section {
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.section-content {
  color: #555;
  line-height: 1.6;
  margin: 0;
  font-size: 1rem;
}

.section-content.keywords {
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 5px;
  font-weight: 500;
}

.section-content.content {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 5px;
}

.section-content pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.8;
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
</style>
