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
          <li><strong>标题格式：</strong>简洁明了，使用编辑器提供的标题样式（H1-H6）</li>
          <li><strong>作者信息：</strong>请填写真实姓名，多个作者之间用逗号分隔</li>
          <li><strong>摘要要求：</strong>200-500字，概述论文的研究目的、方法、结果和结论，可使用加粗、斜体等强调重要内容</li>
          <li><strong>关键词：</strong>3-5个，用逗号分隔，反映论文的核心内容</li>
          <li><strong>正文格式：</strong>使用编辑器提供的样式，结构清晰，包括引言、方法、结果、讨论和结论等部分，可使用列表、加粗、斜体等格式</li>
          <li><strong>参考文献：</strong>采用标准格式，注明作者、标题、期刊名称、年份、卷号、页码等信息，可使用列表格式排列</li>
          <li><strong>图片要求：</strong>可直接在编辑器中插入图片，确保图片清晰可读</li>
        </ul>
      </div>
      <div class="section">
        <h3>版权要求</h3>
        <ul>
          <li><strong>原创性声明：</strong>投稿者需确保所投论文为原创作品，未在其他期刊或平台发表过</li>
          <li><strong>版权转让：</strong>论文发表后，版权归 Peerex Peer 所有，平台有权对论文进行编辑、修改和传播</li>
          <li><strong>引用规范：</strong>论文中引用他人成果需注明出处，避免抄袭和剽窃行为</li>
          <li><strong>保密要求：</strong>涉及国家机密、商业秘密或个人隐私的内容不得投稿</li>
          <li><strong>法律责任：</strong>投稿者需对论文内容的真实性和合法性负责，如因侵权等问题产生法律纠纷，由投稿者承担全部责任</li>
          <li><strong>退稿政策：</strong>平台有权根据审稿结果拒绝不符合要求的稿件，退稿后投稿者可自行处理稿件</li>
        </ul>
      </div>
      <div class="section">
        <h3>投稿流程</h3>
        <ol>
          <li>登录 Peerex Peer 作者后台</li>
          <li>进入在线投稿页面，填写论文基本信息</li>
          <li>使用富文本编辑器编写论文摘要和正文</li>
          <li>选择论文所属模块，输入关键词</li>
          <li>提交投稿，系统自动生成投稿ID</li>
          <li>等待审稿结果，可通过个人中心查看稿件状态</li>
          <li>根据审稿意见修改论文（如需）</li>
          <li>论文发表，可在期刊目录中查看</li>
        </ol>
      </div>
      <div class="section">
        <h3>审稿流程</h3>
        <ol>
          <li>稿件提交后进入待审核状态</li>
          <li>系统自动分配到初审阶段</li>
          <li>审核员进行评审，给出评审意见</li>
          <li>根据审核结果，稿件进入下一阶段或返回修改</li>
          <li>最终审核通过后，稿件状态更新为已发表</li>
          <li>作者可在个人中心查看完整的审核记录</li>
        </ol>
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