// 简单的清除localStorage脚本
console.log('清除LocalStorage数据...');

// 模拟浏览器环境的localStorage
const localStorage = {
  data: {},
  setItem(key, value) {
    this.data[key] = value;
  },
  getItem(key) {
    return this.data[key] || null;
  },
  removeItem(key) {
    delete this.data[key];
  },
  clear() {
    this.data = {};
    console.log('LocalStorage已清除');
  }
};

// 清除localStorage
localStorage.clear();
console.log('清除完成');
