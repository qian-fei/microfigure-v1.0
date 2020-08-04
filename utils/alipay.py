import rsa
import base64
import urllib
import requests

class AliPay(object):
    """移动端支付宝支付"""
    # 应用ID
    APP_ID = "2016102100730287"
    # 接口名称
    METHOD = "alipay.trade.app.pay"
    # 编码
    CHARSET = "utf-8"
    # 加密类型
    SIGN_TYPE = "RSA"
    # 版本
    VERSION = "1.0"
    # 支付宝请求地址
    SERVER_URL = "https://openapi.alipay.com/gateway.do"
    # 支付宝回调地址
    NOTIFY_URL = ""
    # 支付宝公钥
    ALIPAY_PUBLIC = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA111wd3/TikY9hXtvmDsW
    2IPuIq8Y/kl5iidEuHhxVq8w/vEOyodaKfq9CJ0GaII8IlVV75bMKSL3Z7mgQaFU
    W3CYoYg+qXxY98AqrAlWrNfb86EMkg+40K8rXH5TMtNDuQMiZq2HN+1hOUDRN94f
    w2CsY/Z6NqWnwEZTFGdyFlOU+hJ9IHtgpB0XPM+3A/MeuakcMQYifozA4iBRzwR5
    PcmuOV6Ar1fk9Q7AwyKXZi5icy1uGEiyjZVzy6L6IoyC9sXiw00e0r5TDRqdUxXC
    2cpR6T+RUqVY84gFpg4Y2+pMs3OpQgSRZzgrAA+QTLtZa3HLMKXd3x7Mf9e8/1w2
    CQIDAQAB
    -----END PUBLIC KEY-----"""
    # 商户RSA2私钥
    PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
    MIIEqQIBAAKCAQEA3FqomGVlH/sRheBi5Bopa1V4rvcKWg7BZBbulWxOVwj7KLOm
    KlMjxj3dSHyxYqUVx/50sK1ptbo3dVp2VoV1quP7t8r8RQN5LDMkKD7eevUtkn6t
    D4+Z1oIQLx93LCHCCBc+n0SkDkWrqKRIJJG1kGAeHoiEywW2wL23rQAMjEmsMROg
    R7JIqo371NyvupqMnP/Pq0+DIA7LQE4gSLDlr+2GB4W4Eyleke+BkpUzs7Qq7iqz
    +/m5U6zBsdA1JcQnrz1pnxlTCapvvVUVwt//esIpKzwNTr89qfc7WTxxfwrfC4KA
    pURzRS0oRrm7sajRdh3nW52igjMQeGJf6Ve6hQIDAQABAoIBAE31PQR9iuNfnflx
    Q0tT/iddG88600y9P6o7erkekjC0mrbxp+39cACozmrgwpkVsrkIyxvenjGO6iP4
    lzlRCiolcl65z7pS2kHK7hXW+DskFrVnX67LrS944GTriuvwHYdjQeJzFF+AQpTt
    WiCl9EhZ2Q4QWnrBUHCHSsY7poFogKza2m26j5FEyexKvLU1haGknKshxd0UUuvq
    6UrghkAL9kCGLO6er92oi4zXdZ09ZYLKveTQ7OYHa9K4Xs1qpMyvUmqvW/xMS6LU
    k1XQbZ43Gnd43lWF8otP/AlzBnRHXS/OEPzod08ttjs+423uTveogSB7+QDFrvqb
    ySb/XkECgYkA4oeq8IXtALdxWXhq5pb0J8c7LvgXXE/JnX1A5e33kxSq3INf0wTV
    svuVch+cXc3d4mEx36oaxXd/MJyXIuu91k+0TfOK/hOyQE7CqzH4szjM7q8K6WLl
    gtJsTqJIpXIUbaENAX+w2a+dPgAjOsdn4Gnxb/xVLOJR+MOmuyoN2OY8u5ldoAwu
    2QJ5APkFT+AJArx/kWeuG85mWs3UVfLAZU+oXySG6hoQFZikp2zSO+2FerxGsJcM
    ZsUMN7C5Ru6Zy16NmUjj7AAwJGb+NyloeWOf70WyUnYQM1WvIPiJhtlk8iN7quR3
    v9ewngK6ucy31rQdmWcjzGe6afA9IgvPfQc1jQKBiQCUmWiSFViOYsfRaEO/9gA9
    49y4B/jTDmf0jsi2zC7e5ezbcLa4Z3CD07OKRKA/jJ9kNFwSG7UqGiRuUBp4xuom
    HuzpQbzIxUTmGIRs5v/9GWKdpGflB4IFGmIAB0beeQJblA1DEW+CrUfZ9x8lHM/Q
    j87Ypk99fQ1GwZmrJ4Aj64ylh4q6RaOpAnhnt26tQROCrx9Ar6OlM7xePjIOCVQo
    +VenPwoCEPDtwqZ5DJcpNo8IG+kxAFlNeOk5EfIZLrUljJRrZ4LEEUkYHImdFYZ5
    mANwY/U0d0rqRSbWXXFs2j5/yOJEhhvBGi61tE/ulCM4oZti+eYIzfuRs+SaRrEs
    b4ECgYhyTSan2DF4DSaMpqh33AqxnJ1/ghNau2+Ti3whfQDqpUsXyiDXgomXlzKR
    jjAr5f0168+MkVd0BlgjmHSb6txv8w9InuYk+FxCUg6XjIJH5v59oGi/+73QCPMp
    uoyS44PYMCVJ1gCGyF79EtH1ledUbiTSeLaV+Y9IKeQF6lTlghfUup+WpYXq
    -----END RSA PRIVATE KEY-----"""
    # 商户RSA2公钥
    PUBLICE_KEY = """-----BEGIN RSA PUBLIC KEY-----
    MIIBCgKCAQEA3FqomGVlH/sRheBi5Bopa1V4rvcKWg7BZBbulWxOVwj7KLOmKlMj
    xj3dSHyxYqUVx/50sK1ptbo3dVp2VoV1quP7t8r8RQN5LDMkKD7eevUtkn6tD4+Z
    1oIQLx93LCHCCBc+n0SkDkWrqKRIJJG1kGAeHoiEywW2wL23rQAMjEmsMROgR7JI
    qo371NyvupqMnP/Pq0+DIA7LQE4gSLDlr+2GB4W4Eyleke+BkpUzs7Qq7iqz+/m5
    U6zBsdA1JcQnrz1pnxlTCapvvVUVwt//esIpKzwNTr89qfc7WTxxfwrfC4KApURz
    RS0oRrm7sajRdh3nW52igjMQeGJf6Ve6hQIDAQAB
    -----END RSA PUBLIC KEY-----"""

    def __init__(self, out_trade_no, total_amount, sign, timestamp):
        """
        初始化配置
        :param out_trade_no: 商户订单号
        :param total_amount: 订单总金额
        :param sign: 签名
        :param timestamp: 时间 格式："yyyy-MM-dd HH:mm:ss"
        """
        self.order_info = {
            "body": "微图app--余额充值", # 商品描述
            "subject": "余额充值", # 订单标题
            "out_trade_no": "", # 商户订单号
            "total_amount": "", # 订单总额
            "product_code": "QUICK_MSECURITY_PAY" # 产品码 默认QUICK_MSECURITY_PAY
        }
        self.public_param = {
            "appid": self.APP_ID, # 应用ID
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
        message = message.encode("utf-8")
        sign = rsa.sign(message, private_key, "SHA-1")
        b64_sign = base64.b64encode(sign)
        return b64_sign
    
    def generate_str(self, param):
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
        self.public_param["sign"] = self.genreate_sign(self.order_info)
        request_param = self.generate_str(self.public_param)
        return request_param
    
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
        param_str = self.generate_str(param_dict)
        content = param_str.encode("utf-8")
        public_key = rsa.PublicKey.load_pkcs1_openssl_pem(self.ALIPAY_PUBLIC)
        try:
            rest = rsa.verify(content, call_sign, public_key)
        except Exception as e:
            rest = False
        finally:
            return rest