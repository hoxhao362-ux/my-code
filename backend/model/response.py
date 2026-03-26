"""统一 API 响应模型"""
from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一响应格式 {code, message, data, meta}"""
    code: int = 200
    message: str = "success"
    data: Any = None
    meta: Optional[dict] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success", meta: Optional[dict] = None) -> "ApiResponse":
        return cls(code=200, message=message, data=data, meta=meta)

    @classmethod
    def error(cls, code: int = 400, message: str = "error", data: Any = None) -> "ApiResponse":
        return cls(code=code, message=message, data=data)

    @classmethod
    def paginated(cls, items: list, total: int, page: int = 1, page_size: int = 20) -> "ApiResponse":
        return cls(
            code=200,
            message="success",
            data=items,
            meta={"total": total, "page": page, "page_size": page_size}
        )
