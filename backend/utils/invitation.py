"""
邀请码工具模块
提供邀请码生成、验证、管理等功能
"""
import secrets
import string
from datetime import datetime
from typing import Optional, Dict, Any

from database import db_manager

# 获取数据库服务实例
invitation_db = db_manager.get_service('invitation_code')

class InvitationCodeUtil:
    """邀请码工具类"""
    
    @staticmethod
    def generate_code(length: int = 8) -> str:
        """
        生成邀请码
        
        Args:
            length: 邀请码长度，默认为8位
            
        Returns:
            str: 生成的邀请码
        """
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    async def create_invitation_code(
        role: str, 
        created_by: str,
        created_by_uid: int,
        description: Optional[str] = None,
        max_uses: int = 1,
        expire_time: Optional[datetime] = None
    ) -> str:
        """
        创建邀请码
        
        Args:
            role: 邀请码对应的角色
            created_by: 创建者用户名
            created_by_uid: 创建者用户ID
            description: 邀请码描述
            max_uses: 最大使用次数
            expire_time: 过期时间
            
        Returns:
            str: 生成的邀请码
        """
        code = InvitationCodeUtil.generate_code()
        create_time = datetime.now().isoformat()
        expire_time_str = expire_time.isoformat() if expire_time else None
        
        await invitation_db.execute(
            """
            INSERT INTO invitation_codes (
                code, role, status, max_uses, used_count, description,
                created_by, created_by_uid, create_time, expire_time
            ) VALUES ($1, $2, 'active', $3, 0, $4, $5, $6, $7, $8)
            """,
            (code, role, max_uses, description, created_by, created_by_uid, create_time, expire_time_str)
        )
        
        return code
    
    @staticmethod
    async def validate_invitation_code(code: str) -> Dict[str, Any]:
        """
        验证邀请码
        
        Args:
            code: 邀请码
            
        Returns:
            Dict[str, Any]: 验证结果，包含valid、role、message
        """
        # 查询邀请码
        invitation = await invitation_db.fetchone(
            """
            SELECT code, role, status, max_uses, used_count, expire_time
            FROM invitation_codes 
            WHERE code = $1
            """,
            (code,)
        )
        
        if not invitation:
            return {"valid": False, "role": None, "message": "邀请码不存在"}
        
        # 检查状态
        if invitation["status"] != "active":
            return {"valid": False, "role": None, "message": "邀请码已失效"}
        
        # 检查使用次数
        if invitation["used_count"] >= invitation["max_uses"]:
            return {"valid": False, "role": None, "message": "邀请码已达到最大使用次数"}
        
        # 检查过期时间
        if invitation["expire_time"]:
            expire_time = datetime.fromisoformat(invitation["expire_time"])
            if datetime.now() > expire_time:
                return {"valid": False, "role": None, "message": "邀请码已过期"}
        
        return {
            "valid": True, 
            "role": invitation["role"], 
            "message": "邀请码有效"
        }
    
    @staticmethod
    async def use_invitation_code(code: str, used_by_uid: int, used_by_username: str) -> bool:
        """
        使用邀请码
        
        Args:
            code: 邀请码
            used_by_uid: 使用者用户ID
            used_by_username: 使用者用户名
            
        Returns:
            bool: 是否使用成功
        """
        # 验证邀请码
        validation_result = await InvitationCodeUtil.validate_invitation_code(code)
        if not validation_result["valid"]:
            return False
        
        # 更新使用次数
        await invitation_db.execute(
            "UPDATE invitation_codes SET used_count = used_count + 1 WHERE code = $1",
            (code,)
        )
        
        # 记录使用记录
        use_time = datetime.now().isoformat()
        await invitation_db.execute(
            """
            INSERT INTO invitation_code_usage (
                code, used_by_uid, used_by_username, use_time
            ) VALUES ($1, $2, $3, $4)
            """,
            (code, used_by_uid, used_by_username, use_time)
        )
        
        # 检查是否达到最大使用次数，如果是则更新状态
        invitation = await invitation_db.fetchone(
            "SELECT used_count, max_uses FROM invitation_codes WHERE code = $1",
            (code,)
        )
        
        if invitation["used_count"] >= invitation["max_uses"]:
            await invitation_db.execute(
                "UPDATE invitation_codes SET status = 'inactive' WHERE code = $1",
                (code,)
            )
        
        return True
    
    @staticmethod
    async def update_code_status(code: str, status: str) -> bool:
        """
        更新邀请码状态
        
        Args:
            code: 邀请码
            status: 新状态
            
        Returns:
            bool: 是否更新成功
        """
        status_str = await invitation_db.execute(
            "UPDATE invitation_codes SET status = $1 WHERE code = $2",
            (status, code)
        )
        
        # 解析 asyncpg 的状态字符串，例如 "UPDATE 1"
        return "UPDATE 1" in status_str
    
    @staticmethod
    async def get_invitation_codes(
        page: int = 1, 
        page_size: int = 10,
        status: Optional[str] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取邀请码列表
        
        Args:
            page: 页码
            page_size: 每页条数
            status: 状态筛选
            role: 角色筛选
            
        Returns:
            Dict[str, Any]: 邀请码列表和总数
        """
        offset = (page - 1) * page_size
        
        # 构建查询条件
        where_clause = "WHERE 1=1"
        params = []
        
        if status:
            where_clause += f" AND status = ${len(params) + 1}"
            params.append(status)
        
        if role:
            where_clause += f" AND role = ${len(params) + 1}"
            params.append(role)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM invitation_codes {where_clause}"
        total = await invitation_db.fetchval(count_sql, tuple(params))
        
        # 查询列表
        limit_idx = len(params) + 1
        offset_idx = limit_idx + 1
        
        list_sql = f"""
            SELECT code, role, status, max_uses, used_count, description,
                   created_by, create_time, expire_time
            FROM invitation_codes
            {where_clause}
            ORDER BY create_time DESC
            LIMIT ${limit_idx} OFFSET ${offset_idx}
        """
        params.extend([page_size, offset])
        
        codes = await invitation_db.fetchall(list_sql, tuple(params))
        
        return {
            "total": total,
            "codes": [dict(code) for code in codes]
        }

invitation_util = InvitationCodeUtil()