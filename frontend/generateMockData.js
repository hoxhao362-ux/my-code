// 生成虚拟数据脚本
// 运行方式：在浏览器控制台中执行或通过Node.js运行

// 生成随机字符串
function generateRandomString(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// 生成随机日期
function generateRandomDate(start = new Date('2024-01-01'), end = new Date()) {
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString().split('T')[0];
}

// 生成随机模块
const modules = ['医学影像', '药物研发', '临床研究', '公共卫生', '生物信息学', '人工智能', '其他'];
function getRandomModule() {
  return modules[Math.floor(Math.random() * modules.length)];
}

// 生成随机状态
const statuses = ['已通过', '已发表', '审稿中', '未通过'];
function getRandomStatus() {
  // 增加已通过和已发表的概率，确保期刊目录有足够数据显示
  const weights = [0.4, 0.3, 0.2, 0.1]; // 权重：已通过40%，已发表30%，审稿中20%，未通过10%
  const random = Math.random();
  let cumulative = 0;
  for (let i = 0; i < statuses.length; i++) {
    cumulative += weights[i];
    if (random < cumulative) {
      return statuses[i];
    }
  }
  return statuses[0]; // 默认返回已通过
}

// 生成随机作者
const writers = ['张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十'];
function getRandomAuthor() {
  return writers[Math.floor(Math.random() * writers.length)];
}

// 生成随机关键词
const keywordsList = [
  ['深度学习', '医学图像', '人工智能'],
  ['药物研发', '临床试验', '新药'],
  ['临床研究', '循证医学', '医学统计'],
  ['公共卫生', '流行病学', '健康管理'],
  ['生物信息学', '基因组学', '蛋白质组学'],
  ['人工智能', '机器学习', '大数据'],
  ['其他', '医学教育', '医院管理']
];
function getRandomKeywords() {
  return keywordsList[Math.floor(Math.random() * keywordsList.length)];
}

// 生成虚拟账号
function generateUsers() {
  return [
    {
      username: 'admin',
      password: btoa('admin123'), // 加密密码
      role: 'admin',
      email: 'admin@example.com',
      phone: '13800138000',
      avatar: ''
    },
    {
      username: 'reviewer',
      password: btoa('reviewer123'), // 加密密码
      role: 'reviewer',
      email: 'reviewer@example.com',
      phone: '13800138001',
      avatar: ''
    },
    {
      username: 'author',
      password: btoa('author123'), // 加密密码
      role: 'author',
      email: 'author@example.com',
      phone: '13800138002',
      avatar: ''
    },
    {
      username: 'user',
      password: btoa('user123'), // 加密密码
      role: 'user',
      email: 'user@example.com',
      phone: '13800138003',
      avatar: ''
    }
  ];
}

// 生成随机审稿阶段
const reviewStages = ['初审', '复审', '终审'];
function getRandomReviewStage() {
  return reviewStages[Math.floor(Math.random() * reviewStages.length)];
}

// 生成虚拟投稿
function generateJournals(count = 50) {
  const journals = [];
  for (let i = 1; i <= count; i++) {
    const status = getRandomStatus();
    const journal = {
      id: i + 1000, // 避免与现有ID冲突
      title: `虚拟投稿 ${i}：${generateRandomString(10)} 的研究`,
      author: getRandomAuthor(),
      date: generateRandomDate(),
      status: status,
      reviewStage: status === '已通过' || status === '未通过' ? getRandomReviewStage() : '初审',
      abstract: `这是虚拟投稿 ${i} 的摘要内容，介绍了研究的背景、方法、结果和结论。该研究涉及 ${getRandomModule()} 领域，使用了先进的研究方法和技术。`,
      keywords: getRandomKeywords(),
      module: getRandomModule(),
      content: `<h3>摘要</h3><p>这是虚拟投稿 ${i} 的摘要内容，介绍了研究的背景、方法、结果和结论。</p><h3>引言</h3><p>研究背景和意义...</p><h3>方法</h3><p>研究方法和实验设计...</p><h3>结果</h3><p>研究结果和数据分析...</p><h3>讨论</h3><p>结果讨论和结论...</p>`,
      viewCount: Math.floor(Math.random() * 1000)
    };
    journals.push(journal);
  }
  return journals;
}

// 生成虚拟审稿记录
function generateReviewRecords(journals) {
  const records = [];
  journals.forEach((journal, index) => {
    // 为每篇期刊生成1-3条审稿记录
    const recordCount = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < recordCount; i++) {
      const record = {
        id: `record_${index}_${i}`,
        journalId: journal.id,
        reviewerId: i % 2 === 0 ? 'admin' : 'reviewer',
        reviewStage: i === 0 ? '初审' : i === 1 ? '复审' : '终审',
        reviewResult: i === recordCount - 1 ? getRandomStatus() : '通过',
        reviewComments: `这是对虚拟投稿 ${journal.id} 的第 ${i + 1} 次审核意见，包括修改建议和评价。`,
        reviewDate: generateRandomDate(new Date(journal.date), new Date()),
        journalAuthor: journal.author
      };
      records.push(record);
    }
  });
  return records;
}

// 清除所有生成的数据
function clearAllData() {
  if (confirm('确定要清除所有虚拟数据吗？')) {
    // 清除相关数据
    localStorage.removeItem('journals');
    localStorage.removeItem('reviewRecords');
    console.log('虚拟数据已清除！');
    alert('虚拟数据已清除！');
  }
}

// 执行数据生成
function generateAllData() {
  console.log('开始生成虚拟数据...');
  
  // 生成期刊数据
  const journals = generateJournals(50);
  console.log('生成了 50 篇虚拟投稿');
  
  // 生成审稿记录
  const reviewRecords = generateReviewRecords(journals);
  console.log('生成了', reviewRecords.length, '条审稿记录');
  
  // 合并现有数据（如果有）
  const existingJournals = JSON.parse(localStorage.getItem('journals') || '[]');
  const existingReviewRecords = JSON.parse(localStorage.getItem('reviewRecords') || '[]');
  
  // 合并并去重
  // 使用Set和map确保id唯一
  const journalMap = new Map();
  [...existingJournals, ...journals].forEach(journal => {
    journalMap.set(journal.id, journal);
  });
  const allJournals = Array.from(journalMap.values());
  
  const reviewRecordMap = new Map();
  [...existingReviewRecords, ...reviewRecords].forEach(record => {
    reviewRecordMap.set(record.id, record);
  });
  const allReviewRecords = Array.from(reviewRecordMap.values());
  
  // 保存到localStorage
  localStorage.setItem('journals', JSON.stringify(allJournals));
  localStorage.setItem('reviewRecords', JSON.stringify(allReviewRecords));
  
  console.log('虚拟数据生成完成！');
  console.log('\n虚拟账号：');
  console.log('1. 管理员：用户名 admin，密码任意');
  console.log('2. 审核员：用户名 reviewer，密码任意');
  console.log('3. 作者：用户名 author，密码任意');
  console.log('4. 普通用户：任意用户名，密码任意');
  console.log('\n数据已保存到 localStorage 中，刷新页面即可使用。');
  
  // 显示成功提示
  alert('虚拟数据生成成功！请刷新前端应用页面查看生成的期刊。');
}

// 如果在浏览器环境中运行
if (typeof window !== 'undefined') {
  // 延迟执行，确保页面加载完成
  setTimeout(generateAllData, 1000);
} 
// 如果在Node.js环境中运行
else if (typeof module !== 'undefined' && module.exports) {
  // 导出函数供外部使用
  module.exports = {
    generateAllData,
    generateUsers,
    generateJournals,
    generateReviewRecords
  };
}
