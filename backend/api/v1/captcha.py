"""
验证码相关 API 接口

提供图形验证码的生成与校验，用于基础的人机验证场景（如登录、注册前校验）。
基于异步架构，调用底层服务确保高并发下的性能表现。
"""

from api import dependencies as deps
from fastapi import APIRouter, Depends
from model.captcha import CaptchaVerifyRequest
from model.response import ApiResponse
from service.captcha_service import captcha_service
from utils.log import global_logger

# 实例化验证码路由器
router = APIRouter(
    prefix="/captcha",
    tags=["验证码相关接口"],
    responses={
        500: {"description": "服务器内部错误，例如 Redis 缓存不可用"},
    },
)


@router.get(
    "/image", summary="获取图形验证码", dependencies=[Depends(deps.captcha_rate_limit)]
)
async def get_image_captcha():
    """
    生成并获取一张图形验证码。

    **流程说明**:
    1. 底层通过异步线程池生成验证码图片和对应的文本
    2. 生成唯一请求ID (req_id)
    3. 将 req_id 与验证码文本存入 Redis 缓存，默认 5 分钟有效期
    4. 将 req_id 和图片的 Base64 编码返回给前端

    **返回参数**:
    - `req_id`: 验证码对应的请求ID，后续验证时需一并提交
    - `image`: 图片的 Data URL (Base64) 格式，可直接用于前端 img 标签的 src 属性
    """
    global_logger.info("API", "前端请求获取图形验证码")
    try:
        req_id, image_b64 = await captcha_service.generate_captcha()

        # 封装并返回标准格式数据
        return ApiResponse.success(
            data={"req_id": req_id, "image": image_b64}, message="验证码获取成功"
        )
    except Exception as e:
        global_logger.error("API", f"处理获取图形验证码请求异常: {e}")
        # 如果 Redis 未连接等导致异常，返回 500
        return ApiResponse.error(code=500, message="获取验证码失败，服务内部异常")


@router.post(
    "/verify", summary="校验图形验证码", dependencies=[Depends(deps.captcha_rate_limit)]
)
async def verify_image_captcha(request: CaptchaVerifyRequest):
    """
    校验用户提交的图形验证码。

    **安全机制**:
    为防止重放攻击和暴力破解，系统规定验证码属于**一次性消耗品**。
    前端一旦发起本接口校验请求，后端比对后**立刻销毁**该请求ID对应的验证码缓存记录。
    如果验证失败或过期，前端需重新调用获取接口获取新验证码。

    **校验规则**:
    - 验证码不区分大小写

    **返回参数**:
    - `data`: bool 类型。`true` 验证通过，`false` 验证失败或已过期
    """
    global_logger.info("API", f"前端请求校验图形验证码: req_id={request.req_id}")
    try:
        # 调用验证码服务进行比对，服务内部负责销毁逻辑
        is_valid = await captcha_service.verify_captcha(
            req_id=request.req_id, code=request.code
        )

        if is_valid:
            return ApiResponse.success(data=True, message="验证码校验通过")
        else:
            # 对于验证不通过的情况，我们在统一结构中的 data 返回 False，也可以视情况抛出 HttpException(400)
            # 这里为了对标普遍的业务场景，使用 data=False，由前端决定处理方式
            return ApiResponse.success(data=False, message="验证码错误或已失效")

    except Exception as e:
        global_logger.error("API", f"处理校验图形验证码请求异常: {e}")
        return ApiResponse.error(code=500, message="校验验证码异常，请稍后再试")
