// 更新现有用户数据，添加邮箱和手机号
function updateExistingUser() {
    try {
        const currentUser = localStorage.getItem('user');
        if (currentUser) {
            const user = JSON.parse(currentUser);
            
            // 检查是否已经有邮箱和手机号
            if (!user.email || !user.phone) {
                // 从用户列表中查找完整信息
                const users = JSON.parse(localStorage.getItem('users') || '[]');
                const fullUser = users.find(u => u.username === user.username);
                
                // 更新用户数据
                const updatedUser = {
                    ...user,
                    email: user.email || fullUser?.email || `${user.username}@example.com`,
                    phone: user.phone || fullUser?.phone || '13800138000'
                };
                
                // 保存到localStorage
                localStorage.setItem('user', JSON.stringify(updatedUser));
                console.log('用户数据已更新:', updatedUser);
                return updatedUser;
            }
        }
    } catch (error) {
        console.error('更新用户数据失败:', error);
    }
}

// 立即执行更新
updateExistingUser();

// 导出函数，方便在浏览器控制台调用
window.updateUser = updateExistingUser;