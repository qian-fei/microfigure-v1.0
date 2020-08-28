#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: user_api.py
@Time: 2020-06-30 16:27:12
@Author: money 
"""
##################################【app登录注册模块】##################################
import re
import json
import string
import time
import random
import datetime
import hashlib
import base64
import manage
from bson.son import SON
from flask import request, g
from utils.util import response
from libs.captcha import captcha


def check_token(doc, token_expire=1):
    """
    校验token
    :param token_expire: token有效期 单位天
    """
    token = None
    try:
        # 判断token有效期
        date0 = datetime.datetime.fromtimestamp(doc.get("login_time") // 1000)
        # 生成token
        date1 = datetime.datetime.strptime(date0.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        date2 = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        delta = date2 - date1
        if delta.days > token_expire:
            # 生成token
            data = {"uid": doc.get("uid")}
            md5_token = hashlib.md5(str(data).encode()).hexdigest()
            data = {"md5_token": md5_token, "timestamp": int(time.time() * 1000)}
            token = base64.b64encode(json.dumps(data).encode()).decode()
            # 更新token
            manage.client["user"].update_one({"uid": doc.get("uid")}, {"$set": {"token": token}})
        return token
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def get_captcha():
    """获取图片码"""
    data = {}
    try:
        # 生成图片唯一id
        str_items = string.ascii_letters
        str_random = random.choice(str_items) + f"{int(time.time() * 1000)}"
        uid = hashlib.md5(str_random.encode()).hexdigest()
        # 获取图片验证码
        name, text, image = captcha.captcha.generate_captcha()
        print(text)

        # 图片验证码写入数据库
        condition = {"uid": uid, "type": "pic", "code": text, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
        manage.client["verify"].insert_one(condition)

        # 响应base64格式的图片验证码
        pic_b64 = "data:image/jpg;base64," + base64.b64encode(image).decode()
        # resp = make_response(image)
        # resp.headers["Content-Type"] = "image/jpg"
        data["uid"] = uid
        data["pic"] = pic_b64
        return response(data=data)

    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_sms_code():
    """发送短信"""
    try:
        # 获取参数
        uid = request.json.get("uid", None)
        mobile = request.json.get("mobile", None)
        pic_code = request.json.get("pic_code", None)

        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号", code=1)
        if not pic_code:
            return response(msg="请输入图片验证码", code=1)
        if not uid:
            return response(msg="Bad Request：Miss params: %s." % str(uid), code=1, status=400)

        # 判断手机号长度
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)

        # 判断手机格式
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)

        # 验证图片验证码
        doc = manage.client["verify"].find_one({"uid": str(uid)})
        if doc["code"].lower() != pic_code.lower():
            return response(msg="手机号或图片验证码错误", code=1)

        # 生成随机验证码并入库
        # sms_code = "%06d" % random.randint(0, 999999)
        sms_code = 1111
        condition = {"uid": str(mobile), "type": "sms", "code": str(sms_code), "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
        manage.client["verify"].insert_one(condition)

        # 调用第三方短信接口
        # sms.send_sms(int(sms_code), int(mobile))
        resp = response(msg="Send successfully.")
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_sms_verify():
    """短信校验"""
    try:
        # 获取参数
        mobile = request.json.get("mobile", None)
        sms_code = request.json.get("sms_code", None)

        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号码", code=1)
        if not sms_code:
            return response(msg="请输入短信验证码", code=1)

        # 判断手机号长度
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)

        # 判断手机格式
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)

        # 验证短信验证码
        verify_doc = manage.client["verify"].find_one({"uid": str(mobile), "type": "sms", "code": str(sms_code)})
        if not verify_doc:
            return response(msg="手机号或短信验证码错误", code=1)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_register(nick_limit=8):
    """
    用户注册
    :param nick_limit: 昵称长度上限
    """
    try:
        # 获取参数
        mobile = request.json.get("mobile", None)
        password = request.json.get("password", None)
        oauth = request.json.get("oauth", None)

        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号码", code=1)
        if not password:
            return response(msg="请输入密码", code=1)

        # 判断手机号码是否已经注册
        doc = manage.client["user"].find_one({"mobile": str(mobile)})
        if doc and oauth is None:
            return response(msg="手机号已经注册", code=1)

        # 生成用户唯一id
        str_items = string.ascii_letters
        str_random = random.choice(str_items) + f"{int(time.time() * 1000)}"
        uid = hashlib.md5(str_random.encode()).hexdigest()

        # 用户密码加密
        password_b64 = base64.b64encode(str(password).encode()).decode()

        # 条件
        condition = {
            "uid": str(uid), "nick": "微图", "sex": "保密", "age": 20, "mobile": str(mobile), "password": password_b64, "head_img_url": "", "state": 1, "account": str(mobile), "auth": 0,
            "type": "user", "balance": float(0), "works_num":0, "group": "comm", "label": [], "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "login_time": int(time.time() * 1000),
            "sign": "欢迎来使用趣图，快来更新您的签名吧！"
        }
        # 正常注册
        if not oauth:
            manage.client["user"].insert_one(condition)
        # 第三方注册
        else:
            condition.update({"oauth": {"%s" % oauth["platform"]: oauth}})
            manage.client["user"].insert_one(condition)
        # 记录日注册量
        # 凌晨时间戳
        today = datetime.date.today()
        today_stamp = int(time.mktime(today.timetuple()) * 1000)
        doc = manage.client["user_statistical"].update({"user_id": uid, "date": today_stamp}, {"$inc": {"register_num": 1}})
        if doc["n"] == 0:
            condition = {"user_id": uid, "date": today_stamp, "works_num": 0, "sale_num": 0, "browse_num": 0, "amount": float(0), "like_num": 0, "goods_num": 0, "register_num": 1,
                        "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        # 生成token
        data = {"uid": str(uid)}
        md5_token = hashlib.md5(str(data).encode()).hexdigest()
        data = {"md5_token": md5_token, "timestamp": int(time.time() * 1000)}
        token = base64.b64encode(json.dumps(data).encode()).decode()

        # token入库
        manage.client["user"].update_one({"uid": str(uid)}, {"$set": {"token": token}})
        resp = response(msg="Registered successfully.")
        resp.headers["token"] = token
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_account_login(pwd_min_limit=6, pwd_max_limit=16):
    """
    账户登录
    :param pwd_min_limit: 密码位数下限
    :param pwd_max_limit: 密码位数上限
    """
    try:
        # 获取参数
        mobile = request.json.get("mobile", None)
        password = request.json.get("password", None)
        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号码", code=1)
        if not password:
            return response(msg="请输入密码", code=1)

        # 判断密码长度
        if len(str(password)) > pwd_min_limit:
            return response("密码最小长度6位", code=1)

        if len(str(password)) > pwd_max_limit:
            return response("密码最大长度16位", code=1)

        # 用户密码检验
        password_b64 = base64.b64encode(str(password).encode()).decode()
        doc = manage.client["user"].find_one({"mobile": str(mobile), "password": password_b64})
        if not doc:
            return response(msg="用户名或密码错误", code=1)

        # 检查用户状态
        if doc["state"] == 0:
            return response(msg="您的账户已被冻结", code=1)

        token = doc["token"]
        # 校验token有效期
        sign = check_token(doc)
        if sign: token = sign

        # 记录登录时间
        manage.client["user"].update_one({"uid": doc["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})

        resp = response(msg="Login successful.")
        resp.headers["token"] = token
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_mobile_login():
    """手机登录"""
    try:
        # 获取参数
        mobile = request.json.get("mobile", None)
        sms_code = request.json.get("sms_code", None)
        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号", code=1)
        if not sms_code:
            return response(msg="请输入验证码", code=1)
        # 检验账户是否存在
        doc = manage.client["user"].find_one({"mobile": str(mobile)})
        if not doc:
            return response(msg="用户不存在", code=1)

        # 验证短信验证码
        verify_doc = manage.client["verify"].find_one({"uid": str(mobile), "type": "sms", "code": str(sms_code)})
        if not verify_doc:
            return response(msg="手机号或短信验证码错误", code=1)

        # 检查用户状态
        if doc["state"] == 0:
            return response(msg="您的账户已被冻结", code=1)

        token = doc["token"]
        # 校验token有效期
        sign = check_token(doc)
        if sign: token = sign

        # 记录登录时间
        manage.client["user"].update_one({"uid": doc["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})
        resp = response(msg="Login successful.")
        resp.headers["token"] = token
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_oauth_bind(nick_limit=8):
    """
    第三方绑定
    :param nick_limit: 昵称位数上限
    """
    try:
        # 获取参数
        mobile = request.json.get("mobile", None)
        oauth = request.json.get("oauth", None)
        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号", code=1)
        if not oauth:
            return response("Bad Request：Miss params: 'oauth'.", code=1, status=400)

        # 检验账户是否存在
        doc = manage.client["user"].find_one({"mobile": mobile})
        if not doc:
            # 生成用户唯一id
            str_items = string.ascii_letters
            str_random = random.choice(str_items) + f"{int(time.time() * 1000)}"
            uid = hashlib.md5(str_random.encode()).hexdigest()
            condition = {
                "uid": uid, "nick": mobile[:nick_limit], "sex": "保密", "age": 20, "mobile": mobile, "head_img_url": "", "account": mobile,  "state": 1,  "type": "user", "balance": 0,
                "works_num":0, "update_time": int(time.time() * 1000), "login_time": int(time.time() * 1000), "create_time": int(time.time() * 1000), "oauth": {"%s" % oauth["platform"]: oauth}
            }
            manage.client["user"].insert_one(condition)
            # 生成token
            data = {"uid": uid}
            md5_token = hashlib.md5(str(data).encode()).hexdigest()
            data = {"md5_token": md5_token, "timestamp": int(time.time() * 1000)}
            token = base64.b64encode(json.dumps(data).encode()).decode()

            # token入库
            manage.client["user"].update_one({"uid": uid}, {"$set": {"token": token}})
            resp = response(msg="Binding success.")
            resp.headers["token"] = token
            return resp

        # 检查用户状态
        if doc["state"] == 0:
            return response(msg="该手机号已被冻结", code=1)

        # 判断用户是否重复绑定
        doc1 = manage.client["user"].find_one({"mobile": mobile}).get("oauth", None)
        if doc1 and doc1.get(f"{oauth['platform']}", None):
            return response(msg="该手机号已定绑定，请更换手机号.", code=1)

        # 绑定第三方
        manage.client["user"].update_one({"mobile": mobile}, {"$set": {f"oauth.{oauth['platform']}": oauth}})

        token = doc["token"]
        # 校验token有效期
        sign = check_token(doc)
        if sign: token = sign

        # 记录登录时间
        manage.client["user"].update_one({"uid": doc["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})

        resp = response()
        resp.headers["token"] = token
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_oauth_login():
    """第三方登录"""
    try:
        # 获取参数
        userid = request.json.get("userid", None)
        platform = request.json.get("platform", None)
        if not userid:
            return response(msg="Bad Request：Miss parameter: 'userid'.", code=1, status=400)

        # 判断用户与第三方信息是否绑定
        doc1 = manage.client["user"].find_one({f"oauth.{platform}.userID": userid})
        doc2 = manage.client["user"].find_one({f"oauth.{platform}.uid": userid})
        if not any([doc1, doc2]):
            return response(data=1, msg="请绑定账号", code=1)

        doc = doc1 or doc2
        token = doc["token"]
        # 校验token有效期
        sign = check_token(doc)
        if sign: token = sign

        # 记录登录时间
        manage.client["user"].update_one({"uid": doc1["uid"] if doc1 else doc2["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})
        resp = response()
        resp.headers["token"] = token
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def get_user_logout():
    """退出登录"""
    try:
        # 用户登录状态判断
        user_id = g.user_data["user_id"]
        if not user_id: 
            return response(msg="Bad Request: User not logged in.", code=1)
        return response(msg="退出成功")

    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def get_forgot_password():
    """忘记密码"""
    try:
        # 获取参数
        mobile = request.json.get("mobile")
        sms_code = request.json.get("sms_code")
        password = request.json.get("password")

        # 判断参数是否为空
        if not password:
            return response(msg="请输入密码", code=1)
        # 校验短信码
        doc = manage.client["verify"].find_one({"uid": mobile, "type": "sms", "code": sms_code})
        if not doc:
            return response(msg="短信码或手机号错误", code=1)
        # 用户密码加密
        password_b64 = base64.b64encode(password.encode()).decode()

        # 更新密码
        client["user"].update_one({"uid": uid}, {"$set": {"password": password_b64}})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)


def post_mobile_verify():
    """校验手机是否已经注册"""
    try:
        # 获取参数
        mobile = request.json.get("mobile")
        sms_code = request.json.get("sms_code")

        # 判断参数是否为空
        if not mobile:
            return response(msg="请输入手机号码", code=1)
        if not sms_code:
            return response(msg="请输入短信验证码", code=1)

        # 判断手机号长度
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)

        # 判断手机格式
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)

        # 验证短信验证码
        verify_doc = manage.client["verify"].find_one({"uid": str(mobile), "type": "sms", "code": str(sms_code)})
        if not verify_doc:
            return response(msg="手机号或短信验证码错误", code=1)
        # 校验手机是否已经被注册
        doc = manage.client["user"].find_one({"mobile": mobile})
        if doc: 
            return response(msg="手机号已被注册", code=1)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500)