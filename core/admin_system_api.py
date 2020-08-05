#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_system_api.py
@Time: 2020-07-19 17:05:31
@Author: money 
"""
##################################【后台系统管理模块】##################################
import sys
import os
# 将根目录添加到解析路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2)

import re
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


# 舍弃
def get_admin_account_list():
    """管理员账号列表"""
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"state": {"$ne": -1}, "type": {"$in": ["super", "admin"]}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "role", "let": {"role_id": "$role_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$role_id"]}}}], "as": "role_item"}},
            {"$addFields": {"role_info": {"$arrayElemAt": ["$role_item", 0]}}},
            {"$addFields": {"role": "$role_info.nick"}},
            {"$project": {"_id": 0, "uid": 1, "nick": 1, "account": 1, "mobile": 1, "sole": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_admin_account_search(search_max=32):
    """
    管理员账号列表搜索
    :param: search_max: 搜索内容上限字符数
    """
    data = {}
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        type = request.args.get("type") # 账号account 昵称nick 联系电话mobile
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if type not in ["account", "nick", "mobile"]:
            return response(msg="Bad Request: Params 'type' is erroe.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg="搜索内容上限32个字符", code=1)
        # 查询
        pipeline = [
            {"$match": {"state": {"$ne": -1}, "type": "admin", f"{type}": {"$regex": content}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "role", "let": {"role_id": "$role_id"}, 
                         "pipeline":[{"$match": {"$expr": {"$in": ["$uid", "$$role_id"]}}}, {"$group": {"_id": {"uid": "$uid", "nick": "$nick"}}}, {"$project": {"_id": 0, "nick": "$_id.nick", "uid": "$_id.uid"}}], "as": "role_temp_item"}},
            {"$addFields": {"role_list": {"$map": {"input": "$role_temp_item", "as": "item", "in": {"uid": "$$item.uid", "nick": "$$item.nick"}}}}},
            {"$unset": ["role_temp_item"]},
            {"$project": {"_id": 0, "uid": 1, "nick": 1, "account": 1, "mobile": 1, "role": "$role_name", "role_list": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["user"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        condition = {"state": {"$ne": -1}, "type": {"$in": ["super", "admin"]}, f"{type}": {"$regex": content}}
        count = manage.client["user"].find(condition).count()
        data["count"] = count
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_account():
    """创建账号"""
    try:
        # 参数
        account = request.json.get("account")
        nick = request.json.get("nick")
        mobile = request.json.get("mobile")
        role = request.json.get("role") # array [{"id": , "name": , }]
        if not account:
            return response(msg="Bad Request: Miss params: 'account'.", code=1, status=400)
        if not nick:
            return response(msg="Bad Request: Miss params: 'nick'.", code=1, status=400)
        if not mobile:
            return response(msg="Bad Request: Miss params: 'mobile'.", code=1, status=400)
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)
        if not role:
            return response(msg="Bad Request: Miss params: 'role'.", code=1, status=400)
        uid = base64.b64encode(os.urandom(32)).decode()
        password = "123456"
        password_b64 = base64.b64encode(str(password).encode()).decode()
        condition = {
            "uid": uid, "type": "admin", "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "auth": 0, "sex": "保密", "age": 18, "works_num": 0,
            "account": account, "nick": nick, "mobile": mobile, "password": password_b64, "role_id": [obj["id"] for obj in role], "role_name": "、".join([obj["nick"] for obj in role]), "label": [],
            "balance": 0.0, "sign": "欢迎使用微图~", "group": "comm", "login_time": int(time.time() * 1000)
        }
        manage.client["user"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_admin_password_reset():
    """重置密码"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        password = "123456"
        password_b64 = base64.b64encode(str(password).encode()).decode()
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"password": password_b64}})
        if doc["n"] == 0:
            return response(msg="'user' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_admin_account_state():
    """管理员列表页删除操作"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_admin_permission_list():
    """权限明细列表"""
    data = {}
    try:
        # 差选
        pipeline = [
            {"$match": {"state": 1}},
            {"$unset": ["create_time", "update_time", "state", "_id"]},
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
        cursor = manage.client["permission"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_admin_account_alter(nick_length_max=32):
    """
    账号修改接口
    :param nick_length_max: 昵称最大上限
    """
    try:
        # 参数
        user_id = request.json.get("user_id")
        account = request.json.get("account")
        nick = request.json.get("nick")
        mobile = request.json.get("mobile")
        role_id = request.json.get("role_id") # array [{"id": , "name": , }]
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not account:
            return response(msg="Bad Request: Miss params: 'account'.", code=1, status=400)
        if not nick:
            return response(msg="Bad Request: Miss params: 'nick'.", code=1, status=400)
        if len(nick) > nick_length_max:
            return response(msg=f"昵称最长{nick_length_max}个字符", code=1)
        if not role_id:
            return response(msg="Bad Request: Miss params: 'role_id'.", code=1, status=400)
        if not mobile:
            return response(msg="Bad Request: Miss params: 'mobile'.", code=1, status=400)
        if len(str(mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(mobile)):
            return response(msg="请输入正确的手机号", code=1)
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"account": account, "mobile": mobile, "nick": nick, "role_id": [doc["id"] for doc in role_id]}})
        if doc["n"] == 0:
            return response(msg="'user' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_add_permissions_role(nick_length_max=32, desc_length_max=128):
    """
    创建角色
    :param nick_length_max: 昵称上限
    :param desc_length_max: 描述上限
    """
    try:
        # 参数
        nick = request.json.get("nick")
        desc = request.json.get("desc")
        permission_list = request.json.get('permission_list') # [{"module_id": "001", "permission_id": "001"}, ...] or  [{"module_id": "001", "permission_id": ["001", "002", ...]},...]
        if not nick:
            return response(msg="Bad Request: Miss params: 'nick'.", code=1, status=400)
        if len(nick) > nick_length_max:
            return response(msg=f"昵称上限{nick_length_max}个字符", code=1, status=400)
        if not desc:
            return response(msg="Bad Request: Miss params: 'desc'.", code=1, status=400)
        if len(desc) > desc_length_max:
            return response(msg=f"描述上限{desc_length_max}个字符", code=1, status=400)
        uid = base64.b64encode(os.urandom(32)).decode()
        role_list = []
        for obj in permission_list:
            temp = {"uid": uid, "nick": nick, "desc": desc, "module_id": obj["module_id"], "permission_id": obj["permission_id"], "state": 1, 
                    "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            role_list.append(temp)
        manage.client["role"].insert(role_list)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_role_list():
    """获取角色列表"""
    try:
        # 查询
        pipeline = [
            {"$match": {"state": 1, "uid": {"$ne": "super001"}}},
            {"$group": {"_id": {"uid": "$uid", "nick": "$nick", "desc": "$desc", "module_id": "$module_id", "permission_id": "$permission_id"}}},
            {"$project": {"_id": 0, "uid": "$_id.uid", "nick": "$_id.nick", "desc": "$_id.desc", "module_id": "$_id.module_id", "permission_id": "$_id.permission_id"}},
            {"$group": {"_id": {"uid": "$uid", "nick": "$nick", "desc": "$desc"}, "permission_list": {"$push": "$$ROOT"}}},
            {"$unset": ["permission_list._id", "permission_list.uid", "permission_list.nick", "permission_list.desc"]},
            {"$project": {"_id": 0, "uid": "$_id.uid", "nick": "$_id.nick", "desc": "$_id.desc", "permission_list": 1}},
        ]
        cursor = manage.client["role"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_role_state():
    """角色删除接口"""
    try:
        # 参数
        role_id = request.json.get("role_id")
        if not role_id:
            return response(msg="Bad Request: Miss params: 'role_id'.", code=1, status=400)
        doc = manage.client["role"].update({"uid": role_id}, {"$set": {"state": -1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_admin_operation_log(delta_time=30, length_max=32):
    """
    日志列表接口
    :param delta_time: 允许查询的最大区间30天
    :param length_max: 搜索上限
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        content = request.args.get('content')
        type = request.args.get("type") # account账号 nick昵称 mobile电话
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        # 校验
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if content and len(content):
            return response(msg=f"搜索内容最长{length_max}个字符", code=1)
        if type not in ["account", "nick"]:
            return response(msg="Bad Request: Params 'type' is error.", code=1, status=400)
        temp_list = (int(end_time) - int(start_time)) // (24 * 3600 * 1000)
        if  temp_list > delta_time:
            return response(msg=f"最大只能查询{delta_time}天之内的记录", code=1)
        pipeline = [
            {"$match": {"$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], type if content else "null": {"$regex": content} if content else None}},
            {"$project": {"_id": 0, "uid": 1, "nick": 1, "account": 1, "mobile": 1, "ip": 1, "content": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add": [manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["log"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        data["list"] = data_list
        # 总数
        condition = {"$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], type if content else "null": {"$regex": content} if content else None}
        count = manage.client["log"].find(condition).count()
        data["count"] = count
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_add_permissions_role_editor(nick_length_max=32, desc_length_max=128):
    """
    编辑角色
    :param nick_length_max: 昵称上限
    :param desc_length_max: 描述上限
    """
    try:
        # 参数
        uid = request.json.get("uid")
        nick = request.json.get("nick")
        desc = request.json.get("desc")
        permission_list = request.json.get('permission_list') # [{"module_id": "001", "permission_id": "001"}, ...] or  [{"module_id": "001", "permission_id": ["001", "002", ...]},...]
        if not uid:
            return response(msg="Bad Request: Miss params: 'uid'.", code=1, status=400)
        if not nick:
            return response(msg="Bad Request: Miss params: 'nick'.", code=1, status=400)
        if len(nick) > nick_length_max:
            return response(msg=f"昵称上限{nick_length_max}个字符", code=1, status=400)
        if not desc:
            return response(msg="Bad Request: Miss params: 'desc'.", code=1, status=400)
        if len(desc) > desc_length_max:
            return response(msg=f"描述上限{desc_length_max}个字符", code=1, status=400)
        manage.client["role"].delete_many({"uid": uid})
        for obj in permission_list:
            temp = {"uid": uid, "nick": nick, "desc": desc, "state": 1, "module_id": obj["module_id"], "permission_id": obj["permission_id"], "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["role"].insert(temp)
            
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)