from datetime import datetime
from typing import Dict, Any, Optional
from database.adapter.database_adapter import admin_log_db

async def record_admin_log(
    admin_uid: int,
    admin_username: str,
    operation_type: str,
    operation_object: str,
    operation_details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    记录管理员操作日志
    
    Args:
        admin_uid: 管理员ID
        admin_username: 管理员用户名
        operation_type: 操作类型（如：添加用户、删除文献、修改角色等）
        operation_object: 操作对象（如：用户ID、文献ID等）
        operation_details: 操作详情（可选）
        ip_address: IP地址（可选）
        user_agent: 用户代理（可选）
    """
    # 记录日志
    await admin_log_db.execute(
        """
        INSERT INTO admin_logs (
            admin_uid, admin_username, operation_time, operation_type, 
            operation_object, operation_details, ip_address, user_agent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            admin_uid,
            admin_username,
            datetime.now().isoformat(),
            operation_type,
            operation_object,
            operation_details,
            ip_address,
            user_agent
        )
    )
    await admin_log_db.commit()


async def get_admin_logs(
    page: int = 1,
    page_size: int = 10,
    operation_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取管理员操作日志列表
    
    Args:
        page: 页码
        page_size: 每页条数
        operation_type: 操作类型（可选）
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
    
    Returns:
        包含日志总数和日志列表的字典
    """
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_clause = "WHERE 1=1"
    params = []
    
    if operation_type:
        where_clause += " AND operation_type = ?"
        params.append(operation_type)
    
    if start_time:
        where_clause += " AND operation_time >= ?"
        params.append(start_time)
    
    if end_time:
        where_clause += " AND operation_time <= ?"
        params.append(end_time)
    
    # 查询日志总数
    count_sql = f"SELECT COUNT(*) FROM admin_logs {where_clause}"
    total = await admin_log_db.fetchval(count_sql, tuple(params))
    
    # 查询日志列表
    logs_sql = f"""
    SELECT log_id, admin_uid, admin_username, operation_time, operation_type,
           operation_object, operation_details, ip_address, user_agent
    FROM admin_logs
    {where_clause}
    ORDER BY operation_time DESC
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    logs = await admin_log_db.fetchall(logs_sql, tuple(params))
    
    return {
        "total": total,
        "logs": [dict(log) for log in logs]
    }