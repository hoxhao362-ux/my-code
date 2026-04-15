"""
频率限制服务模块

提供内存级频率限制功能。
"""
import time
from typing import Dict, Tuple
from collections import defaultdict

class RateLimitService:
    """简单的内存频率限制服务"""
    def __init__(self):
        # 存储请求记录: {key: [(timestamp, count), ...]}
        self.requests: Dict[str, list[Tuple[float, int]]] = defaultdict(list)
    
    def check_rate(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """检查请求频率是否超过限制
        
        Args:
            key: 请求标识（如IP地址、用户ID等）
            limit: 时间窗口内允许的最大请求数
            window_seconds: 时间窗口大小（秒）
            
        Returns:
            Tuple[bool, int]: (是否允许请求, 剩余请求数)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # 清理过期的请求记录
        self.requests[key] = [
            (timestamp, count) 
            for timestamp, count in self.requests[key] 
            if timestamp >= window_start
        ]
        
        # 计算当前窗口内的请求总数
        total_requests = sum(count for _, count in self.requests[key])
        
        if total_requests >= limit:
            return False, 0
        
        # 记录新请求
        self.requests[key].append((now, 1))
        return True, limit - total_requests - 1
    
    def add_request(self, key: str, count: int = 1):
        """添加请求记录
        
        Args:
            key: 请求标识
            count: 请求次数，默认为1
        """
        now = time.time()
        self.requests[key].append((now, count))

# 创建全局频率限制服务实例
rate_limit_service = RateLimitService()
