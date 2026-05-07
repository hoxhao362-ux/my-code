"""
支付服务工具模块 - 统一管理支付对接功能

本模块提供了支付服务的通用接口和实现，主要功能包括：
1. 定义统一的支付接口规范（发起支付、查询订单、退款、验签）。
2. 提供 Mock 支付实现，用于开发和测试环境。
3. 提供支付宝（Alipay）对接实现（基于 python-alipay-sdk）。
4. 提供 PayPal 对接实现（占位/模拟）。
5. 提供微信支付（Wechat）对接实现（基于 wechatpayv3）。
6. 通过 PaymentManager 根据配置动态加载支付提供商。

依赖库（可选）：
- python-alipay-sdk: 用于支付宝对接
  安装: pip install python-alipay-sdk
- wechatpayv3: 用于微信支付对接
  安装: pip install wechatpayv3
"""
import abc
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

from core.config import config
from utils.log import global_logger

# 尝试导入 python-alipay-sdk，如果未安装则降级处理
try:
    from alipay import AliPay
    from alipay.utils import AliPayConfig
    ALIPAY_INSTALLED = True
except ImportError:
    ALIPAY_INSTALLED = False
    global_logger.warning("Payment", "未检测到 python-alipay-sdk 库，支付宝功能将不可用。")

# 尝试导入 wechatpayv3，如果未安装则降级处理
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
        """
        创建支付订单
        
        Args:
            order_id: 商户订单号（唯一）
            amount: 支付金额（单位：元）
            subject: 订单标题/商品名称
            **kwargs: 其他可选参数
            
        Returns:
            PaymentResult: 包含支付链接或参数的结果对象
        """
        pass

    @abc.abstractmethod
    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        """
        查询订单状态
        
        Args:
            order_id: 商户订单号
            transaction_id: 支付平台流水号（可选）
            
        Returns:
            PaymentResult: 包含订单状态的结果对象
        """
        pass

    @abc.abstractmethod
    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        """
        发起退款
        
        Args:
            order_id: 商户订单号
            refund_amount: 退款金额
            reason: 退款原因
            
        Returns:
            PaymentResult: 退款结果
        """
        pass
    
    @abc.abstractmethod
    def verify_notify(self, data: Dict[str, Any]) -> bool:
        """
        验证异步通知签名
        
        Args:
            data: 通知数据字典
            
        Returns:
            bool: 验证是否通过
        """
        pass

class MockPaymentProvider(BasePaymentProvider):
    """
    Mock 支付实现
    用于开发测试，不进行实际支付交互。
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "mock"
        self.logger.info("Payment", "初始化 Mock 支付提供商")

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        self.logger.info("Payment", f"[Mock] 创建订单: {order_id}, 金额: {amount}, 标题: {subject}")
        
        # 模拟生成一个支付链接
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
    支付宝支付实现
    基于 python-alipay-sdk
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "alipay"
        
        if not ALIPAY_INSTALLED:
            raise RuntimeError("未安装 python-alipay-sdk，无法使用支付宝功能")
            
        self.app_id = config.get("app_id")
        self.debug = config.get("debug", False)
        
        # 加载密钥文件内容
        private_key_path = config.get("app_private_key_path")
        public_key_path = config.get("alipay_public_key_path")
        
        app_private_key_string = self._read_key_file(private_key_path)
        alipay_public_key_string = self._read_key_file(public_key_path)
        
        if not app_private_key_string or not alipay_public_key_string:
            self.logger.error("Payment", "支付宝密钥文件读取失败")
            # 这里不抛出异常，允许实例化但功能受限，或者选择抛出
        
        self.client = AliPay(
            appid=self.app_id,
            app_notify_url=config.get("notify_url"),
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type=config.get("sign_type", "RSA2"),
            debug=self.debug,
            verbose=False,
            config=AliPayConfig(timeout=15)
        )
        self.logger.info("Payment", f"初始化支付宝提供商 (AppID: {self.app_id}, Sandbox: {self.debug})")

    def _read_key_file(self, path: str) -> Optional[str]:
        """读取密钥文件"""
        if not path:
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error("Payment", f"读取密钥文件失败 {path}: {e}")
            return None

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        try:
            # 电脑网站支付 (alipay.trade.page.pay)
            order_string = self.client.api_alipay_trade_page_pay(
                out_trade_no=order_id,
                total_amount=str(amount), # 支付宝要求字符串格式
                subject=subject,
                return_url=self.config.get("return_url"),
                notify_url=self.config.get("notify_url")
            )
            
            # 构造跳转 URL
            gateway = "https://openapi-sandbox.dl.alipaydev.com/gateway.do" if self.debug else "https://openapi.alipay.com/gateway.do"
            pay_url = f"{gateway}?{order_string}"
            
            return PaymentResult(
                success=True,
                message="订单创建成功",
                pay_url=pay_url,
                order_id=order_id,
                status=PaymentStatus.PENDING
            )
        except Exception as e:
            self.logger.error("Payment", f"支付宝创建订单失败: {e}")
            return PaymentResult(success=False, message=f"支付请求失败: {str(e)}")

    def query_order(self, order_id: str, transaction_id: Optional[str] = None) -> PaymentResult:
        try:
            result = self.client.api_alipay_trade_query(
                out_trade_no=order_id,
                trade_no=transaction_id
            )
            
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
                return PaymentResult(success=False, message=result.get("sub_msg", "查询失败"))
                
        except Exception as e:
            self.logger.error("Payment", f"支付宝查询订单失败: {e}")
            return PaymentResult(success=False, message=f"查询异常: {str(e)}")

    def refund(self, order_id: str, refund_amount: float, reason: str = "") -> PaymentResult:
        try:
            result = self.client.api_alipay_trade_refund(
                out_trade_no=order_id,
                refund_amount=str(refund_amount),
                refund_reason=reason
            )
            
            if result.get("code") == "10000":
                return PaymentResult(
                    success=True,
                    message="退款成功",
                    order_id=order_id,
                    status=PaymentStatus.REFUNDED,
                    data=result
                )
            else:
                return PaymentResult(success=False, message=result.get("sub_msg", "退款失败"))
        except Exception as e:
            self.logger.error("Payment", f"支付宝退款失败: {e}")
            return PaymentResult(success=False, message=f"退款异常: {str(e)}")

    def verify_notify(self, data: Dict[str, Any]) -> bool:
        signature = data.pop("sign", None)
        if not signature:
            return False
        return self.client.verify(data, signature)

class WechatPaymentProvider(BasePaymentProvider):
    """
    微信支付实现 (V3)
    基于 wechatpayv3
    """
    
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
            # 允许继续初始化，但在调用时可能会失败
        
        try:
            with open(self.key_path, 'r') as f:
                private_key = f.read()
            
            # 初始化微信支付客户端
            # 注意：实际使用时可能需要根据 wechatpayv3 的最新 API 调整参数
            self.client = WeChatPay(
                wechatpay_type=WeChatPayType.NATIVE, # 默认为 Native 支付，具体根据 create_order 指定
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
            # 构造 Native 支付请求
            amount_fen = int(amount * 100) # 转换为分
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
                code_url = result.get("code_url")
                return PaymentResult(
                    success=True,
                    message="订单创建成功",
                    pay_url=code_url, # Native 支付返回二维码链接
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
        # 实现退款逻辑（需要原始订单金额等信息，这里简化处理）
        return PaymentResult(success=False, message="微信支付退款接口暂未实现")

    def verify_notify(self, data: Dict[str, Any]) -> bool:
        if not self.client:
            return False
        # 微信支付 V3 验签逻辑较复杂，通常由库处理
        # 这里假设传入的 data 包含了 headers 和 body
        try:
            headers = data.get("headers")
            body = data.get("body")
            signature = headers.get("Wechatpay-Signature")
            timestamp = headers.get("Wechatpay-Timestamp")
            nonce = headers.get("Wechatpay-Nonce")
            serial = headers.get("Wechatpay-Serial")
            
            return self.client.verify(headers, body)
        except Exception:
            return False

class PaypalProvider(BasePaymentProvider):
    """
    PayPal 支付实现
    模拟实现，用于展示逻辑结构
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "paypal"
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.mode = config.get("mode", "sandbox")
        
        if not self.client_id or not self.client_secret:
            self.logger.warning("Payment", "PayPal 配置缺失 client_id 或 client_secret")
            
        self.logger.info("Payment", f"初始化 PayPal 提供商 (Mode: {self.mode})")

    def create_order(self, order_id: str, amount: float, subject: str, **kwargs) -> PaymentResult:
        # 模拟调用 PayPal REST API /v2/checkout/orders
        self.logger.info("Payment", f"[PayPal] 创建订单: {order_id}, 金额: {amount}")
        
        # 构造模拟的 PayPal 批准链接
        # 实际开发中应调用 PayPal SDK 或 HTTP API 创建订单并获取 approve 链接
        base_url = "https://www.sandbox.paypal.com" if self.mode == "sandbox" else "https://www.paypal.com"
        # 模拟的 token
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
        # PayPal Webhook 验证通常涉及校验 HTTP 头和证书，比较复杂
        # 这里仅作占位
        self.logger.info("Payment", f"[PayPal] 验证通知: {data}")
        return True

class PaymentManager:
    """支付服务管理器"""
    
    def __init__(self):
        self.provider: Optional[BasePaymentProvider] = None
        self._initialized = False
        
    def initialize(self):
        """根据配置初始化支付提供商"""
        if self._initialized:
            return

        # 读取配置 (从 payment.toml)
        # 注意：配置键名根据 toml 文件名变为 'payment.payment'
        payment_config = config.get("payment.payment", {})
        if not payment_config.get("enabled", False):
            global_logger.info("Payment", "支付功能未启用")
            return

        provider_type = payment_config.get("provider", "mock")
        global_logger.info("Payment", f"正在初始化支付服务，提供商: {provider_type}")
        
        # 获取通用配置
        common_config = {
            "notify_url": payment_config.get("notify_url"),
            "return_url": payment_config.get("return_url")
        }
        
        try:
            if provider_type == "alipay":
                # 读取 payment.toml 中的 [alipay] section
                alipay_config = config.get("payment.alipay", {})
                full_config = {**common_config, **alipay_config}
                self.provider = AlipayProvider(full_config)
            
            elif provider_type == "paypal":
                # 读取 payment.toml 中的 [paypal] section
                paypal_config = config.get("payment.paypal", {})
                full_config = {**common_config, **paypal_config}
                self.provider = PaypalProvider(full_config)
                
            elif provider_type == "mock":
                self.provider = MockPaymentProvider(common_config)
                
            elif provider_type == "wechat":
                # 读取 payment.toml 中的 [wechat] section
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
            # 初始化失败不应影响主程序启动，只是支付功能不可用
            self.provider = None

    def get_provider(self) -> BasePaymentProvider:
        """获取当前的支付提供商实例"""
        if not self._initialized:
            self.initialize()
            
        if not self.provider:
            # 如果初始化失败或未启用，返回一个临时的 Mock 提供商以防报错
            global_logger.warning("Payment", "支付服务未就绪，使用临时 Mock 提供商")
            return MockPaymentProvider({})
            
        return self.provider

# 全局支付管理器单例
payment_manager = PaymentManager()
