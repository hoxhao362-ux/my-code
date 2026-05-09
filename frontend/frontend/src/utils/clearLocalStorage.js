// 清除localStorage中的用户信息，用于解决自动登录问题
const clearLocalStorage = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('adminRememberedUsername')
  localStorage.removeItem('adminRememberedPassword')
  console.log('LocalStorage中的用户信息已清除')
}

export default clearLocalStorage