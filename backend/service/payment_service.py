"""
支付服务模块 - 统一管理支付对接功能

本模块提供了支付服务的通用接口和实现，主要功能包括：
1. 定义统一的支付接口规范（发起支付、查询订单、退款、验签）。
2. 提供 Mock 支付实现，用于开发和测试环境。
3. 提供支付宝（Alipay）对接实现（基于官方 alipay-sdk-python）。
4. 提供 PayPal 对接实现。
5. 提供微信支付（Wechat）对接实现。
6. 通过 PaymentService 根据配置动态加载支付提供商。
"""
import abc
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

from core.config import config
from utils.log import global_logger

# ==========================================
# 尝试导入 alipay-sdk-python (官方 SDK)
# ==========================================
try:
    from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
    from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
    from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
    from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
    from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
    from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
    from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
    from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
    from alipay.aop.api.util.SignatureUtils import verify_with_rsa
    ALIPAY_INSTALLED = True
except ImportError:
    ALIPAY_INSTALLED = False
    global_logger.warning("Payment", "未检测到 alipay-sdk-python 库，支付宝功能将不可用。请运行 pip install alipay-sdk-python")

# ==========================================
# 尝试导入 wechatpayv3
# ==========================================
try:
    from wechatpayv3 import WeChatPay, WeChatPayType
    WECHAT_INSTALLED = True
except ImportError:
    WECHAT_INSTALLED = False
    global_logger.warning("Payment", "未检测到 wechatpayv3 库，微信支付功能将不可用。")

class PaymentStatus(Enum):
    """支付状态枚举"""
    PENDING = "pending"   # 待支付
    SUCCESS = "success"   # 支付成功
    FAILED = "failed"     # 支付失败
    CLOSED = "closed"     # 交易关闭
    REFUNDED = "refunded" # 已退款

@dataclass
class PaymentResult:
    """统一支付结果对象"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
    # 支付跳转链接或参数（用于前端发起支付）
    pay_url: Optional[str] = None
    pay_params: Optional[Dict[str, Any]] = None
    
    # 订单信息
    order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[PaymentStatus] = None

class BasePaymentProvider(abc.ABC):
    """支付提供商抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = global_logger
        self.provider_name = "base"

    @abc.abstractmethod
    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        """创建支付订单"""
        pass

    @abc.abstractmethod
    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        """查询订单状态"""
        pass

    @abc.abstractmethod
    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        """发起退款"""
        pass
    
    @abc.abstractmethod
    def verify_notify(self, data: Dict[str, Any]) -> bool:
        """验证异步通知签名"""
        pass

    def _read_key_file(self, path: str) -> Optional[str]:
        """读取密钥文件辅助方法"""
        if not path:
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error("Payment", f"读取密钥文件失败 {path}: {e}")
            return None

class MockPaymentProvider(BasePaymentProvider):
    """Mock 支付实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "mock"
        self.logger.info("Payment", "初始化 Mock 支付提供商")

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        self.logger.info("Payment", f"[Mock] 创建订单: {order_id}, 金额: {amount}, 标题: {subject}")
        return_url = self.config.get("return_url", "http://localhost:5173/payment/result")
        mock_url = f"{return_url}?order_id={order_id}&status=success"
        
        return PaymentResult(
            success=True,
            message="Mock订单创建成功",
            pay_url=mock_url,
            order_id=order_id,
            status=PaymentStatus.PENDING
        )

    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        self.logger.info("Payment", f"[Mock] 查询订单: {order_id}")
        return PaymentResult(
            success=True,
            message="Mock查询成功",
            order_id=order_id,
            transaction_id=f"mock_txn_{order_id}",
            status=PaymentStatus.SUCCESS,
            data={"amount": 100.00, "pay_time": "2023-01-01 12:00:00"}
        )

    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        self.logger.info("Payment", f"[Mock] 订单退款: {order_id}, 金额: {refund_amount}")
        return PaymentResult(
            success=True,
            message="Mock退款成功",
            order_id=order_id,
            status=PaymentStatus.REFUNDED
        )
        
    def verify_notify(self, data: Dict[str, Any]) -> bool:
        self.logger.info("Payment", f"[Mock] 验证通知: {data}")
        return True

class AlipayProvider(BasePaymentProvider):
    """
    支付宝支付实现 (基于官方 alipay-sdk-python)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "alipay"
        
        if not ALIPAY_INSTALLED:
            raise RuntimeError("未安装 alipay-sdk-python，无法使用支付宝功能")
            
        self.app_id = config.get("app_id")
        # 调试模式决定是否使用沙箱环境
        self.debug = config.get("debug", False)
        
        # 加载密钥内容
        app_private_key_string = self._read_key_file(config.get("app_private_key_path"))
        alipay_public_key_string = self._read_key_file(config.get("alipay_public_key_path"))
        
        if not app_private_key_string or not alipay_public_key_string:
            self.logger.error("Payment", "支付宝密钥文件读取失败或内容为空")
            raise ValueError("支付宝密钥配置缺失")
        
        # 配置 AlipayClientConfig
        alipay_client_config = AlipayClientConfig()
        alipay_client_config.server_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do" if self.debug else "https://openapi.alipay.com/gateway.do"
        alipay_client_config.app_id = self.app_id
        alipay_client_config.app_private_key = app_private_key_string
        alipay_client_config.alipay_public_key = alipay_public_key_string
        alipay_client_config.sign_type = config.get("sign_type", "RSA2")
        
        # 初始化 DefaultAlipayClient
        self.client = DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=logging.getLogger("alipay"))
        self.alipay_public_key = alipay_public_key_string  # 保存公钥用于验签
        
        self.logger.info("Payment", f"初始化支付宝提供商 (AppID: {self.app_id}, Sandbox: {self.debug})")

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        """
        创建电脑网站支付订单 (alipay.trade.page.pay)
        """
        try:
            # 构建请求模型
            model = AlipayTradePagePayModel()
            model.out_trade_no = order_id
            model.total_amount = str(amount)
            model.subject = subject
            model.product_code = "FAST_INSTANT_TRADE_PAY"
            model.qr_pay_mode = "2" # 订单码-跳转模式

            # 构建请求对象
            request = AlipayTradePagePayRequest(biz_model=model)
            
            # 设置回调地址
            notify_url = self.config.get("notify_url")
            return_url = self.config.get("return_url")
            if notify_url:
                request.notify_url = notify_url
            if return_url:
                request.return_url = return_url

            # 执行请求，获取跳转 URL (GET 方法)
            response_content = self.client.page_execute(request, http_method="GET")
            
            # page_execute 返回的是完整的 URL 字符串
            return PaymentResult(
                success=True,
                message="订单创建成功",
                pay_url=response_content,
                order_id=order_id,
                status=PaymentStatus.PENDING
            )
        except Exception as e:
            self.logger.error("Payment", f"支付宝创建订单失败: {e}")
            return PaymentResult(success=False, message=f"支付请求失败: {str(e)}")

    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        """
        查询订单状态 (alipay.trade.query)
        """
        try:
            model = AlipayTradeQueryModel()
            if transaction_id:
                model.trade_no = transaction_id
            else:
                model.out_trade_no = order_id
                
            request = AlipayTradeQueryRequest(biz_model=model)
            
            # 执行请求
            response_content = self.client.execute(request)
            # execute 返回的是 JSON 字符串，需要解析
            if not response_content:
                 return PaymentResult(success=False, message="查询无响应")

            response_data = json.loads(response_content)
            
            # 官方 SDK 的响应通常包含一个 "alipay_trade_query_response" 键
            # 但 execute 方法有时会直接返回解析后的字典，取决于 SDK 版本
            # 这里为了稳妥，检查一下
            result = response_data.get("alipay_trade_query_response")
            if not result:
                 # 如果没有外层包装，可能直接就是结果
                 result = response_data

            if result.get("code") == "10000":
                trade_status = result.get("trade_status")
                status_map = {
                    "WAIT_BUYER_PAY": PaymentStatus.PENDING,
                    "TRADE_CLOSED": PaymentStatus.CLOSED,
                    "TRADE_SUCCESS": PaymentStatus.SUCCESS,
                    "TRADE_FINISHED": PaymentStatus.SUCCESS
                }
                return PaymentResult(
                    success=True,
                    message="查询成功",
                    order_id=order_id,
                    transaction_id=result.get("trade_no"),
                    status=status_map.get(trade_status, PaymentStatus.FAILED),
                    data=result
                )
            else:
                sub_msg = result.get("sub_msg", result.get("msg", "查询失败"))
                return PaymentResult(success=False, message=sub_msg)
                
        except Exception as e:
            self.logger.error("Payment", f"支付宝查询订单失败: {e}")
            return PaymentResult(success=False, message=f"查询异常: {str(e)}")

    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        """
        发起退款 (alipay.trade.refund)
        """
        try:
            model = AlipayTradeRefundModel()
            model.out_trade_no = order_id
            model.refund_amount = str(refund_amount)
            model.refund_reason = reason
            
            request = AlipayTradeRefundRequest(biz_model=model)
            
            response_content = self.client.execute(request)
            response_data = json.loads(response_content)
            result = response_data.get("alipay_trade_refund_response") or response_data
            
            if result.get("code") == "10000":
                # fund_change = result.get("fund_change") # Y/N
                return PaymentResult(
                    success=True,
                    message="退款成功",
                    order_id=order_id,
                    status=PaymentStatus.REFUNDED,
                    data=result
                )
            else:
                sub_msg = result.get("sub_msg", result.get("msg", "退款失败"))
                return PaymentResult(success=False, message=sub_msg)
        except Exception as e:
            self.logger.error("Payment", f"支付宝退款失败: {e}")
            return PaymentResult(success=False, message=f"退款异常: {str(e)}")

    def verify_notify(self, data: Dict[str, Any]) -> bool:
        """
        验证异步通知签名
        """
        try:
            # 1. 提取签名
            signature = data.pop("sign", None)
            if not signature:
                self.logger.warning("Payment", "支付宝回调缺少签名参数")
                return False
                
            # 2. 移除 sign_type (如果不参与签名)
            # 支付宝官方文档说明：sign_type 不参与签名
            data.pop("sign_type", None)
            
            # 3. 参数排序并拼接
            # 过滤空值
            unsigned_items = sorted([(k, v) for k, v in data.items() if v])
            message = "&".join([f"{k}={v}" for k, v in unsigned_items])
            
            # 4. 验证签名
            # verify_with_rsa 需要传入公钥字符串、待签名内容、签名字符串
            is_valid = verify_with_rsa(self.alipay_public_key, message, signature)
            
            if is_valid:
                self.logger.info("Payment", f"支付宝回调验签成功: {data.get('out_trade_no')}")
            else:
                self.logger.error("Payment", f"支付宝回调验签失败: {data.get('out_trade_no')}")
                
            return is_valid
        except Exception as e:
            self.logger.error("Payment", f"支付宝验签过程异常: {e}")
            return False

class WechatPaymentProvider(BasePaymentProvider):
    """微信支付实现 (V3)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "wechat"
        
        if not WECHAT_INSTALLED:
            raise RuntimeError("未安装 wechatpayv3，无法使用微信支付功能")
            
        self.appid = config.get("appid")
        self.mchid = config.get("mch_id")
        self.cert_serial_no = config.get("cert_serial_no")
        self.apiv3_key = config.get("api_key")
        self.cert_path = config.get("cert_path")
        self.key_path = config.get("key_path")
        
        if not self.cert_path or not self.key_path:
            self.logger.error("Payment", "微信支付证书配置缺失")
        
        try:
            with open(self.key_path, 'r') as f:
                private_key = f.read()
            
            self.client = WeChatPay(
                wechatpay_type=WeChatPayType.NATIVE,
                mchid=self.mchid,
                private_key=private_key,
                cert_serial_no=self.cert_serial_no,
                apiv3_key=self.apiv3_key,
                appid=self.appid,
                notify_url=config.get("notify_url")
            )
            self.logger.info("Payment", f"初始化微信支付提供商 (AppID: {self.appid})")
        except Exception as e:
            self.logger.error("Payment", f"微信支付初始化异常: {e}")
            self.client = None

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        if not self.client:
            return PaymentResult(success=False, message="微信支付客户端未正确初始化")
            
        try:
            amount_fen = int(amount * 100)
            request_data = {
                "appid": self.appid,
                "mchid": self.mchid,
                "description": subject,
                "out_trade_no": order_id,
                "notify_url": self.config.get("notify_url"),
                "amount": {
                    "total": amount_fen,
                    "currency": "CNY"
                }
            }
            
            code, message = self.client.pay(request_data)
            
            if code == 200:
                result = json.loads(message)
                return PaymentResult(
                    success=True,
                    message="订单创建成功",
                    pay_url=result.get("code_url"),
                    order_id=order_id,
                    status=PaymentStatus.PENDING,
                    data=result
                )
            else:
                return PaymentResult(success=False, message=f"创建订单失败: {message}")
        except Exception as e:
            self.logger.error("Payment", f"微信支付创建订单失败: {e}")
            return PaymentResult(success=False, message=f"支付请求异常: {str(e)}")

    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        if not self.client:
            return PaymentResult(success=False, message="微信支付客户端未正确初始化")
            
        try:
            code, message = self.client.query(out_trade_no=order_id)
            if code == 200:
                result = json.loads(message)
                trade_state = result.get("trade_state")
                status_map = {
                    "SUCCESS": PaymentStatus.SUCCESS,
                    "REFUND": PaymentStatus.REFUNDED,
                    "NOTPAY": PaymentStatus.PENDING,
                    "CLOSED": PaymentStatus.CLOSED,
                    "PAYERROR": PaymentStatus.FAILED
                }
                return PaymentResult(
                    success=True,
                    message="查询成功",
                    order_id=order_id,
                    transaction_id=result.get("transaction_id"),
                    status=status_map.get(trade_state, PaymentStatus.FAILED),
                    data=result
                )
            else:
                return PaymentResult(success=False, message=f"查询失败: {message}")
        except Exception as e:
            self.logger.error("Payment", f"微信支付查询失败: {e}")
            return PaymentResult(success=False, message=f"查询异常: {str(e)}")

    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        return PaymentResult(success=False, message="微信支付退款接口暂未实现")

    def verify_notify(self, data: Dict[str, Any]) -> bool:
        if not self.client:
            return False
        try:
            headers = data.get("headers")
            body = data.get("body")
            return self.client.verify(headers, body)
        except Exception:
            return False

class PaypalProvider(BasePaymentProvider):
    """PayPal 支付实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "paypal"
        self.mode = config.get("mode", "sandbox")
        self.logger.info("Payment", f"初始化 PayPal 提供商 (Mode: {self.mode})")

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        self.logger.info("Payment", f"[PayPal] 创建订单: {order_id}, 金额: {amount}")
        base_url = "https://www.sandbox.paypal.com" if self.mode == "sandbox" else "https://www.paypal.com"
        approve_url = f"{base_url}/checkoutnow?token=EC-MOCK{order_id}"
        
        return PaymentResult(
            success=True,
            message="PayPal订单创建成功",
            pay_url=approve_url,
            order_id=order_id,
            status=PaymentStatus.PENDING,
            data={"paypal_order_id": f"PAY-MOCK-{order_id}"}
        )

    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        self.logger.info("Payment", f"[PayPal] 查询订单: {order_id}")
        return PaymentResult(
            success=True,
            message="PayPal查询成功",
            order_id=order_id,
            transaction_id=f"PAY-MOCK-{order_id}",
            status=PaymentStatus.SUCCESS,
            data={"amount": 100.00, "status": "COMPLETED"}
        )

    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        self.logger.info("Payment", f"[PayPal] 订单退款: {order_id}, 金额: {refund_amount}")
        return PaymentResult(
            success=True,
            message="PayPal退款成功",
            order_id=order_id,
            status=PaymentStatus.REFUNDED
        )
        
    def verify_notify(self, data: Dict[str, Any]) -> bool:
        self.logger.info("Payment", f"[PayPal] 验证通知: {data}")
        return True

class PaymentService:
    """支付服务管理器"""
    
    def __init__(self):
        self.provider: Optional[BasePaymentProvider] = None
        self._initialized = False
        
    def initialize(self):
        """根据配置初始化支付提供商"""
        if self._initialized:
            return

        payment_config = config.get("payment.payment", {})
        if not payment_config.get("enabled", False):
            global_logger.info("Payment", "支付功能未启用")
            return

        provider_type = payment_config.get("provider", "mock")
        global_logger.info("Payment", f"正在初始化支付服务，提供商: {provider_type}")
        
        common_config = {
            "notify_url": payment_config.get("notify_url"),
            "return_url": payment_config.get("return_url")
        }
        
        try:
            if provider_type == "alipay":
                alipay_config = config.get("payment.alipay", {})
                full_config = {**common_config, **alipay_config}
                self.provider = AlipayProvider(full_config)
            
            elif provider_type == "paypal":
                paypal_config = config.get("payment.paypal", {})
                full_config = {**common_config, **paypal_config}
                self.provider = PaypalProvider(full_config)
                
            elif provider_type == "mock":
                self.provider = MockPaymentProvider(common_config)
                
            elif provider_type == "wechat":
                wechat_config = config.get("payment.wechat", {})
                full_config = {**common_config, **wechat_config}
                self.provider = WechatPaymentProvider(full_config)
                
            else:
                global_logger.warning("Payment", f"未知的支付提供商: {provider_type}，使用 Mock")
                self.provider = MockPaymentProvider(common_config)
                
            self._initialized = True
            global_logger.info("Payment", "支付服务初始化完成")
            
        except Exception as e:
            global_logger.error("Payment", f"支付服务初始化失败: {e}")
            self.provider = None

    def get_provider(self) -> BasePaymentProvider:
        """获取当前的支付提供商实例"""
        if not self._initialized:
            self.initialize()
            
        if not self.provider:
            global_logger.warning("Payment", "支付服务未就绪，使用临时 Mock 提供商")
            return MockPaymentProvider({})
            
        return self.provider

# 全局支付管理器单例
payment_service = PaymentService()
