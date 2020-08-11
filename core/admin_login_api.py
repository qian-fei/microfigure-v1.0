#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_login_api.py
@Time: 2020-07-19 15:20:23
@Author: money 
"""
##################################【后台登录退出模块】##################################
import os
import sys
# 将根目录添加到解析路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2) 

import base64
import string
import time
import random
import datetime
import manage
from bson.son import SON
from flask import request, g
from utils.util import response
from constant import constant
from app_login_api import check_token


def post_admin_login():
    """管理员登录接口"""
    data = {}
    try:
        # 获取参数
        account = request.json.get("account", None)
        password = request.json.get("password", None)
        # 校验
        if not account:
            return response(msg="请输入账号", code=1)
        if not password:
            return response(msg="请输入密码", code=1)
        condition = {"_id": 0, "uid": 1, "type":1, "role_id": 1, "token": 1, "nick": 1, "sex": 1, "sign": 1, "mobile": 1, "login_time": 1}
        password_b64 = base64.b64encode(str(password).encode()).decode()
        doc = manage.client["user"].find_one({"account": account, "password": password_b64}, condition)
        if not doc:
            return response(msg="账户名或密码错误", code=1)
        if doc.get("state") == 0:
            return response(msg="您的账号已被冻结，请联系超级管理员", code=1)
        if doc.get("type") not in ["super", "admin"]:
            return response(msg="您没有权限，请联系超级管理员", code=1)
        # 角色权限
        pipeline = [
            {"$match": {"uid": {"$in": doc.get("role_id")}, "state": 1}},
            {"$lookup": {"from": "module", "let": {"module_id": "$module_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$module_id"]}}}], "as": "module_item"}},
            {"$lookup": {"from": "permission", "let": {"permission_id": "$permission_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$permission_id"]}}}], "as": "permission_item"}},
            {"$addFields": {"module_info": {"$arrayElemAt": ["$module_item", 0]}, "permission_info": {"$arrayElemAt": ["$permission_item", 0]}}},
            {"$addFields": {"module_name": "$module_info.name", "permission_name": "$permission_info.name", "menu": "$permission_info.menu"}},
            # {"$unset": ["module_item", "permission_item", "permission_info", "module_info"]},
            # {"$group": {"_id": "$module_id", "module_name": {"$first": "$module_name"}, "permission_list": {"$push": "$$ROOT"}}},
            # {"$project": {"module_id": "$_id", "module_name": 1, "permission_list": 1}},
            # {"$unset": ["_id", "permission_list._id", "permission_list.state", "permission_list.create_time", "permission_list.update_time", "permission_list.nick", "permission_list.uid", 
            #             "permission_list.desc", "permission_list.module_id", "permission_list.module_name"
            # ]},
            {"$unset": ["create_time", "update_time", "state", "_id", "module_item", "permission_item", "permission_info", "module_info", "desc", "module_name", "nick", "uid"]},
            {"$group": {"_id": {"menu": "$menu", "module_id": "$module_id"}, "permission_item": {"$push": "$$ROOT"}}},
            {"$unset": ["permission_item.module_id", "permission_item.menu"]},
            {"$project": {"_id": 0, "menu": "$_id.menu", "module_id": "$_id.module_id", "permission_item": 1}},
            {"$lookup": {"from": "module", "let": {"module_id": "$module_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$module_id"]}}}], "as": "module_item"}},
            {"$addFields": {"module_info": {"$arrayElemAt": ["$module_item", 0]}}},
            {"$addFields": {"module_name": "$module_info.name"}},
            {"$unset": ["module_info", "module_item"]},
            {"$group": {"_id": {"module_name": "$module_name", "module_id": "$module_id"}, "item": {"$push": "$$ROOT"}}},
            {"$unset": ["item.module_name", "item.module_id"]},
            {"$project": {"_id": 0, "module_id": "$_id.module_id", "module_name": "$_id.module_name", "item": 1}}
        ]
        cursor = manage.client["role"].aggregate(pipeline)
        role_info = [doc for doc in cursor]
        # role_info = {}
        # module_list = []
        # permission_list = []
        # c = 0
        # for i in cursor:
        #     module_dict = {}
        #     permission_dict = {}
        #     if c == 0:
        #         role_info["uid"] = i.get("uid")
        #         role_info["nick"] = i.get("nick")
        #         role_info["desc"] = i.get("desc")
        #     module_dict["module_id"] = i.get("module_id")
        #     module_dict["module_name"] = i.get("module_name")
        #     permission_dict["module_id"] = i.get("module_id")
        #     permission_dict["permission_id"] = i.get("permission_id")
        #     permission_dict["permission_name"] = i.get("permission_name")
        #     module_list.append(module_dict)
        #     permission_list.append(permission_dict)
        # role_info["module_list"] = module_list
        # role_info["permission_list"] = permission_list
        data["role_info"] = role_info

        # 校验token有效期
        token = doc["token"]

        sign = check_token(doc)
        if sign: token = sign
        data["user_info"] = doc
        # 记录登录时间
        manage.client["user"].update_one({"uid": doc["uid"]}, {"$set": {"login_time": int(time.time() * 1000)}})
        resp = response(data=data)
        resp.headers["token"] = token
        
        return resp
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)


def put_admin_password(pwd_length_min=6, pwd_length_max=16):
    """
    修改管理员密码
    """
    try:
        # 参数
        user_id = request.json.get("user_id")
        old_password = request.json.get("old_password")
        new_password = request.json.get("new_password")
        if not old_password:
            return response(msg="请输入旧密码")
        if not new_password:
            return response(msg="请输入新密码")
        if len(new_password) < pwd_length_min and len(new_password) > pwd_length_max:
            return response(msg="密码6-16位")
        password_b64 = base64.b64encode(str(old_password).encode()).decode()
        doc = manage.client["user"].find_one({"uid": user_id, "password": password_b64})
        if not doc:
            return response(msg="旧密码错误")
        if old_password == new_password:
            return response(msg="新密码不能和旧密码相同")
        password_b64 = base64.b64encode(str(new_password).encode()).decode()
        manage.client["user"].update({"uid": user_id}, {"$set": {"password": password_b64}})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)