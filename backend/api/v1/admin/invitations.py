from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
from datetime import datetime

from service.admin_log_service import admin_log_service
from service.invitation_service import invitation_service
from sqlalchemy.ext.asyncio import AsyncSession
from model.invitation import (
    InvitationCodeCreateRequest,
    InvitationCodeResponse,
    InvitationCodeListResponse,
    InvitationCodeStatusUpdateRequest,
    InvitationCodeValidateResponse
)
from api import dependencies as deps

from database.dependencies import get_db_session
router = APIRouter(tags=["管理员-邀请码管理"])

@router.post("/invitation-codes", summary="创建邀请码", response_model=InvitationCodeResponse)
async def create_invitation_code(
    request: InvitationCodeCreateRequest,
    req: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """创建邀请码，仅限管理员访问"""
    # 创建邀请码
    code = await invitation_service.create_invitation_code(
        role=request.role,
        created_by=current_user["username"],
        created_by_uid=current_user["uid"],
        description=request.description,
        max_uses=request.max_uses,
        expire_time=request.expire_time,
        session=session,
    )
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="创建邀请码",
        operation_object=f"邀请码: {code}",
        operation_details=f"创建{request.role}角色邀请码，最大使用次数: {request.max_uses}",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session=session,
    )
    
    # 返回邀请码信息
    return InvitationCodeResponse(
        code=code,
        role=request.role,
        status="active",
        max_uses=request.max_uses,
        used_count=0,
        description=request.description,
        created_by=current_user["username"],
        create_time=datetime.now(),
        expire_time=request.expire_time
    )

@router.get("/invitation-codes", summary="获取邀请码列表", response_model=InvitationCodeListResponse)
async def get_invitation_codes(
    req: Request,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取邀请码列表，仅限管理员访问"""
    # 获取邀请码列表
    result = await invitation_service.get_invitation_codes(
        page=page,
        page_size=page_size,
        status=status,
        role=role,
        session=session,
    )
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="查看邀请码列表",
        operation_object=f"页码: {page}, 每页条数: {page_size}",
        operation_details=f"查询了邀请码列表，共 {result['total']} 条",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session=session,
    )
    
    return InvitationCodeListResponse(
        total=result["total"],
        codes=[InvitationCodeResponse(**code) for code in result["codes"]]
    )

@router.put("/invitation-codes/{code}/status", summary="更新邀请码状态")
async def update_invitation_code_status(
    code: str,
    request: InvitationCodeStatusUpdateRequest,
    req: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """更新邀请码状态，仅限管理员访问"""
    # 更新邀请码状态
    success = await invitation_service.update_code_status(code, request.status, session=session)
    if not success:
        raise HTTPException(status_code=404, detail="邀请码不存在")
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="更新邀请码状态",
        operation_object=f"邀请码: {code}",
        operation_details=f"将邀请码状态更新为: {request.status}",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session=session,
    )
    
    return {"message": "邀请码状态更新成功", "code": code, "status": request.status}

@router.get("/invitation-codes/validate/{code}", summary="验证邀请码")
async def validate_invitation_code(
    code: str,
    req: Request,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """验证邀请码有效性，仅限管理员访问"""
    # 验证邀请码
    result = await invitation_service.validate_invitation_code(code, session=session)
    
    # 记录管理员操作日志
    await admin_log_service.record_admin_log(
        admin_uid=current_user["uid"],
        admin_username=current_user["username"],
        operation_type="验证邀请码",
        operation_object=f"邀请码: {code}",
        operation_details=f"验证邀请码，结果: {result['message']}",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
        session=session,
    )
    
    return InvitationCodeValidateResponse(**result)
