// 简单的路由系统，适合初学者理解
// 不依赖vue-router，手动实现路由功能

export class SimpleRouter {
  constructor(app) {
    this.app = app;
    this.routes = {};
    this.currentPath = '';
    
    // 监听浏览器历史变化
    window.addEventListener('popstate', () => {
      this.handleRouteChange();
    });
  }

  // 添加路由
  addRoute(path, component) {
    this.routes[path] = component;
  }

  // 初始化路由
  init() {
    this.handleRouteChange();
  }

  // 处理路由变化
  handleRouteChange() {
    const path = window.location.pathname || '/';
    this.currentPath = path;
    
    // 渲染对应的组件
    this.renderComponent();
  }

  // 渲染组件
  renderComponent() {
    const component = this.routes[this.currentPath];
    if (component) {
      // 这里使用简单的方式渲染组件
      // 实际项目中会更复杂
      this.app.currentComponent = component;
    } else {
      // 如果没有匹配的路由，重定向到首页
      this.push('/login');
    }
  }

  // 导航到指定路径
  push(path) {
    window.history.pushState({}, '', path);
    this.handleRouteChange();
  }

  // 返回上一页
  back() {
    window.history.back();
  }
}

// 导出路由实例
let routerInstance = null;

export function createRouter() {
  return routerInstance;
}

export function useRouter() {
  return routerInstance;
}
