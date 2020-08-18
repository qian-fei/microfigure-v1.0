import rsa
import base64
import urllib
import datetime
import requests

class AliPay(object):
    """移动端支付宝支付"""
    # 应用ID
    APP_ID = "2021000120602549"
    # 接口名称
    METHOD = "alipay.trade.app.pay"
    # 编码
    CHARSET = "utf-8"
    # 加密类型
    SIGN_TYPE = "RSA2"
    # 版本
    VERSION = "1.0"
    # 支付宝请求地址
    # SERVER_URL = "https://openapi.alipay.com/gateway.do"
    SERVER_URL = "https://openapi.alipaydev.com/gateway.do"
    # 支付宝回调地址
    NOTIFY_URL = "http://wt.test.frp.jethro.fun:8080/api/v1/alipay/callback" # http://wt.test.frp.jethro.fun:8080/api/v1/alipay/callback
    # 支付宝公钥
    ALIPAY_PUBLIC = """-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIgHnOn7LLILlKETd6BFRJ0GqgS2Y3mn1wMQmyh9zEyWlz5p1zrahRahbXAfCfSqshSNfqOmAQzSHRVjCqjsAw1jyqrXaPdKBmr90DIpIxmIyKXv4GGAkPyJ/6FTFY99uhpiq0qadD/uSzQsefWo0aTvP/65zi3eof7TcZ32oWpwIDAQAB
    -----END PUBLIC KEY-----"""
    # 商户RSA2私钥jj
    # PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
    # MIICWwIBAAKBgQCjZlzbNXC1DAFMTyoQ6yt76uI5UE6BFXfvnY0A59zJidN8oAPwcu60iTntQ/4V3vpBd6jnl8jbQM/6VS380ywBpmnzA9NyDtb64Pz9RLVNkGJKo9MkxUbvndQiwCoqt5UphA9MfmLtwwucJvy82dziKLHIjUh+B8v6LFGhg5fVPwIDAQABAoGAFskoe70ZCXYyHCUR9agFuVMI1vs251NKFVUAG7c5l7Urk75wrjAoz24vcMHBheVBOq3oFNuau9Bu8Da+ofoEscDyrIipHCf1LbTKi2APvaluooPdhqlNzDSIbXCJIdGkuCnUttLOR5y3CvDsQxLaErOa3gaB8vws/YrDKO7pKWECQQDfWtCggXmzJSIS3LN0SNn8XNNjtzpZHfK6AWVpPzJbJ1+Fbpk1+uuc1VLTOgfT3d5rxZ/snqKjKTyj1uJGTbYvAkEAu0g8p1fGEzgBQU2/Mdhx3VkVI5eEYVWuMgrgRXNSXortPwCYLkvfcVlzbg7X5Rst0hyLo4ynpts4WAcCvvQd8QJAOG1sGbC8O0sdUaCaYb1p/PzClwWaYxtS0DU8FpvVr/vBgSdQ47dRwRyPwTd+9MKvx5B098WYFxp67HWEUvidFwJAExeNH14iUik+b4LWf+VZzj/bmNJEa4vJg056iHn2Jq8w+mA8I1QWxj5hNxIKTk/T/vxr+9NF8AufFdI5JHBMcQJAX0aNCQX8UgsSQtnUA/4/1xA/MZS4WZAwv2EPHGORJrHmjNBA2xCRuMaiJtHQg2B1qy9/Kz1A5wwgDKulfEhMfQ==
    # -----END RSA PRIVATE KEY-----"""
    PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAt8QcIn+hbP0+XMJje8nsT3q6qXmsforaBC7G+1WEZ9mlucffzQ6QleXWhWZD6Awy2Wtr7bUsR0rOcEraSJNx2BQ4g9na6TgF6XsjP8zhJDe88pu8eO93sIqbauc+W4Q9EN1Z64g0lA/CJnCpfso2c4YR/AJqWm2Jj1JQ09gEHN6cVA8R1gPgiK53qo/LN9Dy69vLapghKmlrDhCC6xtrDzd8QbHuZBhRFeTMxanScFcyiMRxje/MqD61KzC2Xo52a2pi/64KRhLMiZNtTkeKCzZVBhND6fC9U5esB3fb1QiEJMRh+vjrpoFvGalAmFqP/ObsWIVbF999ym+izxbaWwIDAQABAoIBAB+e6ixxg8hqRynU9SNe2n/OoYH6Atl/cQZZOjoTPAZWqDKwlu0E/ZIdi21G7JZoSvOojVjI3Qajc6RU7PyiCmvhBtyBRy7sSfAkFSusSG1f/e5NKAAzTIgfQaECi3NZ7NwTCp8Bv/JeR80vg6rihr4YKs4PaFeJE6uKwYfCWurQhIzCJbJvZUZJzz6oPofMSOCXPp90qsGVwNXrJEr3vzvejFUrfZ/7twLvICtfijs9UGjkZBALMHUYTyqV6ZuHzwRpT88NyTPQgM7bVcxw4vS4Jt9heNmmCvgjzXe9u7gY3lyUxIGp+cdk3VB7UjEr/CoVLDambBuyfKPzK2XJ58kCgYEA58usQTtsl0j5aUk7n6D1VePCu9kwA1Kth/R1kbllS4MddOD8TFj6kmaYnudrGkV3rW1KMQR8V/ub0+ZR3Cv1teOsZxeu0U6vJkVUF7lrzdJnDVDFfmxyZ/M4ctW6fGV7S4rjApeqrdzJjvlCc4eGN3tGW99As6cfvOXl1nEtpt0CgYEAyvSEoQ36eUTQJi7aa49ZFvBwy60G/x9YIQk3MFiY8qFsRS0unJWbk7g3SrW67QsUSQNOMLojms5DB7RO7FNj6gumjS9Pa2rO5d3oX9MicKizaZa9hgm4byklOygtkuFWumVHb0TUcKcVozYz73JZaWrIQwWL33D2aPYom2ydRpcCgYAOErybnUsDiGe0L8ER+QjMNS7ejtouaXeluH7m4RW4VvaT4REQZZqZBuefRjenea5BdlA516bhBKK6Y9J2hqi9aVxPSg3QIXHa5fysEBLuhSbClTPYcCcmDotP1ZAj+1lYBc+wmZrAQZZvOs0BDKpmdfKYo15fSfdQVbj1oxt9dQKBgEe02sNYf/2mrXBAL5W/IPf03bVoncc32NhbPC+NrgRTukA6tXRHe59Wf9qamL+1oWYmj9KxgXDpnU80ion+8Jc5pI/PflzycMVQgRCSNWHeiP0ucCnSd2J3BBuBl5CEozLaI8IRbImczw1KUlEwcpzHSJg9dmzsqXLuPeykFHFjAoGBANlXXe3+Y29uEQg+2vPXuO0Hj4NSN28yRpbX0uFMPVME6MIdKK9yDnshchLKTfUQ/l96dhlPWV5fl+iQcEJ2WMkM2w4fkP1ZqcPrYtYFpfAOGJ5xXUy5nVMZWWCkKGx4CA1WghIW7dplCvCc7Z0VgErl6T19OpjzcAL2g3XF+DC/
    -----END RSA PRIVATE KEY-----"""
    # 商户RSA2公钥
    # PUBLICE_KEY = """-----BEGIN RSA PUBLIC KEY-----
    # MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCjZlzbNXC1DAFMTyoQ6yt76uI5UE6BFXfvnY0A59zJidN8oAPwcu60iTntQ/4V3vpBd6jnl8jbQM/6VS380ywBpmnzA9NyDtb64Pz9RLVNkGJKo9MkxUbvndQiwCoqt5UphA9MfmLtwwucJvy82dziKLHIjUh+B8v6LFGhg5fVPwIDAQAB
    # -----END RSA PUBLIC KEY-----"""
    PUBLICE_KEY = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt8QcIn+hbP0+XMJje8nsT3q6qXmsforaBC7G+1WEZ9mlucffzQ6QleXWhWZD6Awy2Wtr7bUsR0rOcEraSJNx2BQ4g9na6TgF6XsjP8zhJDe88pu8eO93sIqbauc+W4Q9EN1Z64g0lA/CJnCpfso2c4YR/AJqWm2Jj1JQ09gEHN6cVA8R1gPgiK53qo/LN9Dy69vLapghKmlrDhCC6xtrDzd8QbHuZBhRFeTMxanScFcyiMRxje/MqD61KzC2Xo52a2pi/64KRhLMiZNtTkeKCzZVBhND6fC9U5esB3fb1QiEJMRh+vjrpoFvGalAmFqP/ObsWIVbF999ym+izxbaWwIDAQAB
    -----END PUBLIC KEY-----"""
    def __init__(self, out_trade_no, total_amount):
        """
        初始化配置
        :param out_trade_no: 商户订单号
        :param total_amount: 订单总金额
        """
        self.order_info = {
            "body": "微图app--余额充值", # 商品描述
            "subject": "余额充值", # 订单标题
            "out_trade_no": "", # 商户订单号
            "total_amount": "", # 订单总额
            "product_code": "QUICK_MSECURITY_PAY" # 产品码 默认QUICK_MSECURITY_PAY
        }
        self.public_param = {
            "app_id": self.APP_ID, # 应用ID
            "method": self.METHOD, # 接口名称
            "format": "JSON", # 参数格式
            "charset": self.CHARSET, # 编码
            "sign_type": self.SIGN_TYPE, # 加密类型
            "sign": "", # 签名
            "timestamp": "", # 时间
            "version": self.VERSION, # 接口版本
            "notify_url": self.NOTIFY_URL, # 回调地址
            "biz_content": "", # 除公共参数外，其余参数必须存放在该参数中
        }
    
    def genreate_sign(self, content):
        """
        生成SHA-256签名
        :param content: 参与签名的内容
        :return 签名
        """
        # # 生成公钥和私钥
        # public_key, private_key  = rsa.newkeys(2048) # 1024为SHA-1 2048为SHA-256
        # PRIVATE_KEY = private_key.save_pkcs1()
        # PUBLICE_KEY = public_key.save_pkcs1()
        private_key = rsa.PrivateKey._load_pkcs1_pem(self.PRIVATE_KEY)
        content = content.encode("utf-8")
        sign = rsa.sign(content, private_key, "SHA-256")
        b64_sign = base64.b64encode(sign)
        return b64_sign
    
    @staticmethod
    def generate_str(param):
        """
        字典生成字符串
        :param param: 字典参数
        :return 返回字符串
        """
        str = "&".join(["%s=%s" % (k, v) for k, v in sorted(param.items())])
        return str

    def generate_request_param(self, out_trade_no, total_amount):
        """
        生成请求参数返回给商户app
        :param out_trade_no: 商户订单号
        :param total_amount: 订单总金额
        :return 返回请求参数
        """
        self.order_info["out_trade_no"] = out_trade_no
        self.order_info["total_amount"] = total_amount
        dtime = datetime.datetime.now()
        timestamp = dtime.strftime("%Y-%m-%d %H:%M:%S")
        self.public_param["timestamp"] = timestamp
        self.public_param["biz_content"] = f"{self.order_info}"
        self.public_param.pop("sign")
        self.public_param["sign"] = self.genreate_sign(AliPay.generate_str(self.order_info))
        request_param = AliPay.generate_str(self.public_param)
        return request_param
    
    @staticmethod
    def callback_verify_sign(self, callback_param):
        """
        支付宝回调验证
        :param callback_param: 支付宝回调参数
        """
        # # url参数转成字典
        # url = "www.baidu.com?id=123&name=mu&re=mmm&some=ooooo"
        # query = urllib.parse.urlparse(url).query
        param_dict = dict([(k, v[0]) for k, v in urllib.parse.parse_qs(callback_param).items()])
        # 回调sign
        sign = param_dict["sign"]
        call_sign = base64.b64decode(sign)
        # 除sign、sign_type参数外，其余参数皆是待验签参数
        param_dict.pop("sign_type")
        param_dict.pop("sign")
        param_str = AliPay.generate_str(param_dict)
        content = param_str.encode("utf-8")
        public_key = rsa.PublicKey.load_pkcs1_openssl_pem(AliPay.ALIPAY_PUBLIC)
        try:
            rest = rsa.verify(content, call_sign, public_key)
            return param_dict["out_trade_no"], param_dict["total_amount"], param_dict["trade_no"]
        except Exception as e:
            return False, False, False
