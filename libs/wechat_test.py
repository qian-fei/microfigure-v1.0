#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: wechat.py
@Time: 2020-08-01 14:48:47
@Author: money 
"""
import hashlib
import json
import optparse
import time
import requests
import xmltodict
import xml.etree.ElementTree as ET
from urllib.parse import quote
from xml.etree import ElementTree



class WeiXinPay(object):
    """配置账号信息"""
 
    # ==================【基本信息设置】======================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    APPID = ""
    # JSAPI接口中获取openid，审核后在公众平台开启开发模式后可查看
    APPSECRET = ""
    # 受理商ID，身份标识
    MCHID = ""
    # 异步通知url，商户根据实际开发过程设定
    NOTIFY_URL = "http://~/v1.0.1/order/payment"
    # trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
    TRADE_TYPE = "APP"
    # 密钥
    APIKEY = ""
 
    def __init__(self, order_id, body, total_fee, spbill_create_ip):
        self.params = {
            "appid": self.APPID,  # appid
            "mch_id": self.MCHID,  # 商户号
            "nonce_str": self.getNonceStr(),
            "body": body,  # 商品描述
            "out_trade_no": str(order_id),  # 商户订单号
            "total_fee": str(int(total_fee)),
            "spbill_create_ip": spbill_create_ip,  # 127.0.0.1
            "trade_type": self.TRADE_TYPE,  # 交易类型
            # "openid": openid,  # trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
            "notify_url": self.NOTIFY_URL  # 微信支付结果异步通知地址
        }
        # 开发者调用支付统一下单API生成预交易单
        self.url = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 微信请求url
        self.error = None
 
    def getNonceStr(self, length=32):
        """生成随机字符串"""
        import random
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)
 
    def getOpenID(self, code):
        """获取 openid"""
        param = {
            "code": code,  # 用户点击按钮跳转到微信授权页, 微信处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            "appid": self.params["appid"],
            "secret": self.params["APPSECRET"],
            "grant_type": self.params["JSAPI"],
        }
        # 通过code获取access_token
        openIdUrl = "https://api.weixin.qq.com/sns/oauth2/access_token"
        resp = requests.get(openIdUrl, params=param)
        openId = json.loads(resp.text)["openid"]
        return openId
 
    def key_value_url(self, value, urlencode):
        """
        将键值对转为 key1=value1&key2=value2
        对参数按照key=value的格式，并按照参数名ASCII字典序排序
        """
        slist = sorted(value)
        buff = []
        for k in slist:
            v = quote(value[k]) if urlencode else value[k]
            buff.append("{0}={1}".format(k, v))
 
        return "&".join(buff)
 
    def get_sign(self, params):
        """
        生成sign
        拼接API密钥
        """
        stringA = self.key_value_url(params, False)
        stringSignTemp = stringA + "&key=" + self.APIKEY  # APIKEY, API密钥，需要在商户后台设置
        sign = (hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()).upper()
        params["sign"] = sign
        return self.params
 
    def get_req_xml(self):
        """
        拼接XML
        """
        self.get_sign(self.params)
        xml = "<xml>"
        for k, v in self.params.items():
            xml += "<" + k + ">" + v + "</" + k + ">"
        xml += "</xml>"
        return xml.encode("utf-8")
 
    def get_prepay_id(self):
        """
        请求获取prepay_id
        """
        xml = self.get_req_xml()
        respone = requests.post(self.url, xml, headers={"Content-Type": "application/xml"})
        msg = respone.text.encode("ISO-8859-1").decode("utf-8")
        xmlresp = xmltodict.parse(msg)
        if xmlresp["xml"]["return_code"] == "SUCCESS":
            if xmlresp["xml"]["result_code"] == "SUCCESS":
                prepay_id = xmlresp["xml"]["prepay_id"]
                self.params["prepay_id"] = prepay_id
                self.params["package"] = "prepay_id={}".format(prepay_id)
                self.params["timestamp"] = str(int(time.time()))
            else:
                return
        else:
            return
 
    def re_finall(self):
        """
        得到prepay_id后再次签名，返回给终端参数
        """
        self.get_prepay_id()
        if self.error:
            return
        sign_again_params = {
            "appid": self.params["appid"],
            "noncestr": self.params["nonce_str"],
            "package": self.params["package"],
            "partnerid": self.params["mch_id"],
            "timestamp": self.params["timestamp"],
            "prepayid": self.params["prepay_id"]
        }
        self.get_sign(sign_again_params)
        self.params["sign"] = sign_again_params["sign"]
        return self.params  # 返回给app