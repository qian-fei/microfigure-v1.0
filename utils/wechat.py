#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: wechat_pay.py
@Time: 2020-08-01 23:55:20
@Author: money 
"""
import uuid
import requests
import json
import time
from hashlib import md5
import xmltodict # pip install xmltodict

class WechatPay(object):
    """移动端微信支付"""

    # 应用ID
    APP_ID = "wx5acd37bbc91c9f66"
    # 商户号
    MCH_ID = "1511417071"
    # 加密类型
    SIGN_TYPE = "MD5"
    # 微信商户平台设置的密钥
    SECRET_KEY = "ba8622ab8e7e0068c3fa1c406a6784db"
    # 商户服务器IP
    SPBILL_CREATE_IP = "101.132.136.180"
    # 商品描述
    BODY = "微图--余额充值"
    # 微信统一下单URL
    UNIFIED_ORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    # 回调地址
    NOTIFY_URL = "xxxxxxxx"
    def __init__(self, out_trade_no, total_fee):
        """
        初始化配置
        :param out_trade_no: 商户订单号
        :param total_fee: 总金额
        """
        self.order_info = {
            "appid": self.APP_ID, # 应用ID
            "mch_id": self.MCH_ID, # 商户号
            "device_info": "WEB", # 设备号 默认传WEB
            "nonce_str": "", # 随机字符串
            "sign_type": self.SIGN_TYPE, # 加密类型
            "body": self.BODY, # 商品描述
            "out_trade_no": str(out_trade_no), # 商户订单号
            "total_fee": total_fee, # 总金额 单位分
            "spbill_create_ip": self.SPBILL_CREATE_IP, # 商户服务器IP
            "notify_url": self.NOTIFY_URL, # 支付结果回调地址
            "trade_type": "APP" # 交易类型 默认传APP
        }

    def generate_nonce_str(self):
        """
        生成随机字符串
        :return 返回随机字符串
        """
        nonce_str = str(uuid.uuid4()).replace("-", "")
        return nonce_str

    def generate_xml_data(self, json_data):
        """
        生成xml格式数据
        :param json_data: json格式数据
        :return 返回xml格式数据
        """
        xml_data = xmltodict.unparse({"xml": json_data}, pretty=True, full_document=False).encode("utf-8")
        return xml_data

    @staticmethod
    def generate_sign(params):
        """
        生成md5签名
        :param params: 向微信支付发送的请求参数
        :return 返回签名
        """
        if "sign" in params:
            params.pop("sign")
        src = "&".join(["%s=%s" % (k, v) for k, v in sorted(params.items())]) + "&key=%s" % WechatPay.SECRET_KEY
        sign = md5(src.encode("utf-8")).hexdigest().upper()
        return sign

    def wechat_payment_request(self):
        """
        请求统一下单接口
        :param order_info: 向微信支付请求的订单信息
        :return 返回预支付交易标识
        """
        # 生成xml数据
        self.order_info["nonce_str"] = self.generate_nonce_str()
        self.order_info["sign"] = WechatPay.generate_sign(self.order_info)
        xml_data = self.generate_xml_data(self.order_info)
        # 向微信支付发送请求
        context = {}
        resp = requests.post(self.UNIFIED_ORDER_URL, data=xml_data, headers={"Content-Type": "application/xml"})
        if resp.status_code == 200:
            rest = json.loads(json.dumps(xmltodict.parse(resp.content)))
            if rest["xml"]["return_code"] == "SUCCESS": # 请求成功SUCCESS，请求失败FAIL
                prepay_id = rest["xml"]["prepay_id"]
                print(prepay_id)
                return prepay_id
            else:
                err_code = rest["xml"]["return_code"] # 错误码FAIL
                err_msg = rest["xml"]["return_msg"]
                print(err_code, err_msg)
                return False
        return False

    def generate_app_call_data(self, prepay_id):
        """
        客户端APP请求所需参数
        :param prepay_id: 预支付交易标识
        :return 返回app请求微信的参数
        """
        app_request_info = {
            "appid": self.APP_ID, # 应用ID
            "partnerid": self.MCH_ID, # 商户号
            "prepayid": prepay_id, # 预交易标识
            "package": "Sign=WXPay", # 扩展字段 默认WXPay
            "noncestr": self.generate_nonce_str(), # 随机字符串
            "timestamp": str(int(time.time())) # 时间戳 秒级
        }
        app_request_info["sign"] = WechatPay.generate_sign(app_request_info)
        return app_request_info
    
    @staticmethod
    def verify_wechat_call_back(request_body):
        """
        校验微信回调参数
        :param request_body: 微信回调请求体数据
        :return: 返回校验微信支付回调通知的结果
        """
        # xml to dict
        dict_params = xmltodict.parse(request_body)["xml"]
        # 校验返回码
        return_code = dict_params.get("return_code")
        if return_code == "SUCCESS":
            # 校验签名
            if "sign" not in request_params:
                return False, False
            backcall_sign = request_params["sign"]
            sign = WechatPay.generate_sign(request_params)
            if sign == backcall_sign:
                return dict_params["out_trade_no"], dict_params["total_fee"]
            else:
                return False, False
        else:
            return False, False


if __name__ == "__main__":
    demo = WechatPay("20200701412141241", 0.01)
    demo.wechat_payment_request()