#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_works_api.py
@Time: 2020-07-23 14:18:52
@Author: money 
"""
##################################【后台内容管理模块】##################################
import os
import sys
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
from app_works_api import pic_upload_api


def get_admin_pic_material_list(search_max=32, domain=constant.DOMAIN):
    """
    图片素材列表接口
    :param search_max: 搜索内容最大字符数
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 标题title, 昵称传nick, 标签label
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["title", "nick", "label"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg=f"搜索内容最长{search_max}个字符，请重新输入", code=1)
        # 查询
        pipeline = [
            {"$match": {"state": 1, ("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$unset": ["user_item", "user_info"]},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "nick": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "big_pic_url": {"$concat": [domain, "$big_pic_url"]}}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        condition = pipeline = [
            {"$match": {"state": 1, ("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        temp_data = [doc for doc in cursor]
        data["count"] = temp_data[0]["count"] if temp_data else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)


def put_pic_material_state(length_max=20):
    """
    删除图片接口
    """
    try:
        # 参数
        pic_id_list = request.json.get("pic_id_list") # array
        if not pic_id_list:
            return response(msg="Bad Request: Miss param 'pic_id_list'.", code=1, status=400)
        doc = manage.client["pic_material"].update({"uid": {"$in": pic_id_list}}, {"$set": {"state": -1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'pic_id_list' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_material_detail(domain=constant.DOMAIN):
    """
    图片素材详情
    :param domain: 域名
    """
    try:
        # 参数
        pic_id = request.args.get("pic_id")
        if not pic_id:
            return response(msg="Bad Request: Miss params: 'pic_id'.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"uid": pic_id}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "nick": 1, "account": 1, "format": 1, "size": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "big_pic_url": {"$concat": [domain, "$big_pic_url"]}}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 查询规格
        pipeline = [
            {"$match": {"pic_id": pic_id, "state": 1}},
            {"$project": {"_id": 0, "format": 1, "pic_url": {"$concat": [domain, "$pic_url"]}}}
        ]
        cursor = manage.client["price"].aggregate(pipeline)
        spec_list = [doc for doc in cursor]
        data = data_list[0] if data_list else {}
        if data:
            data["spec_list"] = spec_list
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)


def put_pic_material(title_length_max=32, label_length_max=20):
    """
    编辑图片素材
    :param title_length_max: 标题上限
    :param label_length_max: 标签上限
    """
    try:
        # 参数
        title = request.json.get("title")
        label = request.json.get("label")
        pic_id = request.json.get("pic_id")
        if not pic_id:
            return response(msg="Bad Request: Miss params: 'pic_id'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss params: 'title'.", code=1, status=400)
        if not label:
            return response(msg="Bad Request: Miss params: 'label'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题允许最长{title_length_max}个字符", code=1)
        if len(label) > label_length_max:
            return response(msg=f"标签最多允许{label_length_max}个", code=1)
        doc = manage.client["pic_material"].update({"uid": pic_id}, {"$set": {"title": title, "label": label}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_audio_material_list(search_max=32, domain=constant.DOMAIN):
    """
    音频素材列表接口
    :param search_max: 搜索内容最大字符数
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 标题title, 昵称传nick, 标签label
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["title", "nick", "label"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg=f"搜索内容最长{search_max}个字符，请重新输入", code=1)
        # 查询
        pipeline = [
            {"$match": {"state": 1, ("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": "$user_info.head_img_url"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$unset": ["user_item", "user_info"]},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "nick": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "cover_url": {"$concat": [domain, "$cover_url"]}, "head_img_url": {"$concat": [domain, "$head_img_url"]}, "audio_url": {"$concat": [domain, "$audio_url"]}}}
        ]
        cursor = manage.client["audio_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 统计总数用于分页
        pipeline = [
            {"$match": {"state": 1, ("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": "$user_info.head_img_url"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$count": "count"},
        ]
        cursor = manage.client["audio_material"].aggregate(pipeline)
        count = len([doc for doc in cursor])
        data["count"] = count
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)


def put_audio_material_state(length_max=20):
    """
    删除音频接口
    """
    try:
        # 参数
        audio_id_list = request.json.get("audio_id_list") # array
        if not audio_id_list:
            return response(msg="Bad Request: Miss param 'audio_id_list'.", code=1, status=400)
        doc = manage.client["audio_material"].update({"uid": {"$in": audio_id_list}}, {"$set": {"state": -1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'audio_id_list' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_audio_material_detail(domain=constant.DOMAIN):
    """
    音频素材详情
    :param domain: 域名
    """
    try:
        # 参数
        audio_id = request.args.get("audio_id")
        if not audio_id:
            return response(msg="Bad Request: Miss params: 'audio_id'.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"uid": audio_id}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "nick": 1, "account": 1, "format": 1, "size": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "cover_url": {"$concat": [domain, "$cover_url"]}, "audio_url": {"$concat": [domain, "$audio_url"]}}}
        ]
        cursor = manage.client["audio_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list[0] if data_list else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s" % str(e), code=1, status=500)


def put_audio_material(title_length_max=32, label_length_max=20):
    """
    编辑音频素材
    :param title_length_max: 标题上限
    :param label_length_max: 标签上限
    """
    try:
        # 参数
        title = request.json.get("title")
        label = request.json.get("label")
        audio_id = request.json.get("audio_id")
        if not audio_id:
            return response(msg="Bad Request: Miss params: 'audio_id'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss params: 'title'.", code=1, status=400)
        if not label:
            return response(msg="Bad Request: Miss params: 'label'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题允许最长{title_length_max}个字符", code=1)
        if len(label) > label_length_max:
            return response(msg=f"标签最多允许{label_length_max}个", code=1)
        doc = manage.client["audio_material"].update({"uid": audio_id}, {"$set": {"title": title, "label": label}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_audio_material_cover(domain=constant.DOMAIN):
    """
    更换音频封面接口
    :param domain: 域名
    """
    try:
        # 参数
        audio_id = request.form.get("audio_id")
        if not audio_id:
            return response(msg="Bad Request: Miss params: 'audio_id'.", code=1, status=400)
        doc = manage.client["audio_material"].find_one({"uid": works_id})
        if not doc:
            return response(msg="Bad Request: Params 'audio_id' if error.", code=1, status=400)
        user_id = doc.get("user_id")
        data_list = pic_upload_api(user_id)
        file_path = data_list[0]["file_path"]
        doc = manage.client["audio_material"].update({"uid": audio_id}, {"$set": {"cover_url": cover_url}})
        cover_url = domain + file_path
        return response(data=cover_url)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_all_works_list(domain=constant.DOMAIN, search_max=32):
    """
    图片/图集/图文作品接口
    :param domain: 域名
    :param search_max: 搜索上限
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 标题title, 昵称传nick, 标签label
        state = request.args.get("state") # 0未审核，1审核中，2已上架, 3违规下架，4全部
        content = request.args.get("content")
        type = request.args.get("type") # 图片传tp， 图集传tj, "tw"
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["title", "nick", "label"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["0", "1", "2", "3", "4"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg=f"搜索内容最长{search_max}个字符，请重新输入", code=1)
        if type not in ["tp", "tj", "tw"]:
            return response(msg="Bad Request: Params 'type' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None, "type": type,
                        "state": int(state) if state != "4" else {"$ne": -1}}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$addFields": {"pic_info": {"$arrayElemAt": ["$pic_item", 0]}}}, 
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"thumb_url": {"$concat": [domain, "$$item.thumb_url"]}}}}}},
            {"$unset": ["user_item", "user_info", "pic_temp_item", "pic_info"]},
            {"$project": {"_id": 0, "uid": 1, "pic_item": 1, "title": 1, "number": 1, "label": 1, "cover_url": {"$concat": [domain, "$cover_url"]}, "state": 1, "nick": 1, 
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 统计总数用于分页
        pipeline = pipeline = [
            {"$match": {("title" if category == "title" else "nick") if content else "null": {"$regex": content} if content else None, "type": type,
                        "state": int(state) if state != "4" else {"$ne": -1}}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick"}},
            {"$match": {"nick" if category == "nick" else "null": {"$regex": content} if content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        temp_data = [doc for doc in cursor]
        data["count"] = temp_data[0]["count"] if temp_data else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_works_state():
    """
    更改图片作品状态
    :param length_max: 作品选择上限
    """
    try:
        # 参数
        pic_id = request.json.get('pic_id') # array
        state = request.json.get('state') # 删除传-1, 恢复传2, 下架传3, 
        if not pic_id:
            return response(msg="Bad Request: Miss params: 'pic_id'.", code=1, status=400)
        if state not in [-1, 2, 3]:
            return response(msg="Bad Request: Param 'state' is error.", code=1, status=400)
        # 更新
        doc = manage.client["works"].update({"uid": {"$in": pic_id}}, {"$set": {"state": state}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_works_info(title_length_max=32, label_length_max=20):
    """
    图片编辑
    :param title_length_max: 标题上限
    :param label_length_max: 标签上限
    """
    try:
        # 参数
        works_id = request.json.get("works_id")
        title = request.json.get("title")
        label = request.json.get("label")
        state = request.json.get("state") # 0未审核，1审核中，2已上架, 3违规下架
        tag = request.json.get("tag") # 编/商
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss params: 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题最多允许{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss params: 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"标签最多允许{label_length_max}个", code=1)
        if state not in [3, 0, 1, 2]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if tag not in ["商", "编"]:
            return response(msg="Bad Request: Params 'tag' is error.", code=1, status=400)
        # 更新
        doc = manage.client["works"].update({"uid": works_id}, {"$set": {"title": title, "state": state, "label": label, "tag": tag}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_works_audit_list(search_max=32, domain=constant.DOMAIN):
    """
    待审核作品列表
    :param domain: 域名
    :param search_max: 搜索最长字符
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        category = request.args.get("category") # 标题title, 账号account
        content = request.args.get("content")
        type = request.args.get("type") # 图片传tp， 图集传tj, 图文传tw
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["title", "account"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg=f"搜索内容最长{search_max}个字符，请重新输入", code=1)
        if type not in ["tp", "tj", "tw"]:
            return response(msg="Bad Request: Params 'type' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {("title" if category == "title" else "account") if content else "null": {"$regex": content} if content else None, "type": type, "state": 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$addFields": {"pic_info": {"$arrayElemAt": ["$pic_item", 0]}, "user_info": {"$arrayElemAt": ["$user_item", 0]}}}, 
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]}}}}, 
                            "account": "$user_info.account", "nick": "$user_info.nick"}},
            {"$unset": ["user_item", "user_info", "pic_temp_item", "pic_info"]},
            {"$project": {"_id": 0, "uid": 1, "pic_item": 1, "title": 1, "format": 1, "label": 1, "cover_url": {"$concat": [domain, "$cover_url"]}, "type": 1, "account": 1, "nick": 1, 
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        condition = {("title" if category == "title" else "account") if content else "null": {"$regex": content} if content else None, "type": type, "state": 1}
        count = manage.client["works"].find(condition).count()
        data["count"] = count
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_works_autio_state():
    """作品审核"""
    try:
        # 参数
        works_id = request.json.get("works_id") # array
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        state = request.json.get("state") # 通过2 驳回0
        if state not in [2, 0]:
            return response(msg="Bad Request: Params 'state' if error.", code=1, status=400)
        doc = manage.client["works"].update({"uid": {"$in": works_id}}, {"$set": {"state": state}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 更新数据
        if state == 2:
            cursor = manage.client["works"].find({"uid": {"$in": works_id}})
            today = datetime.date.today()
            today_stamp = int(time.mktime(today.timetuple()) * 1000)
            for i in cursor:
                doc = manage.client["user_statistical"].update({"user_id": i["user_id"], "date": today_stamp}, {"$inc": {"works_num": 1}})
                if doc["n"] == 0:
                    manage.client["user_statistical"].insert({"user_id": i["user_id"], "date": today_stamp, "works_num": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_works_detail(domain=constant.DOMAIN):
    """
    图片作品详情
    :param domain: 域名
    """
    try:
        # 参数
        pic_id = request.args.get("pic_id")
        if not pic_id:
            return response(msg="Bad Request: Miss params: 'pic_id'.", code=1, status=400)
        pipeline = [
            {"$match": {"uid": pic_id}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "portrait", "let": {"works_id": "$uid"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$works_id", "$$works_id"]}}}], "as": "portrait_item"}},
            {"$lookup": {"from": "products", "let": {"works_id": "$uid"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$works_id", "$$works_id"]}}}], "as": "products_item"}},
            {"$lookup": {"from": "price", "let": {"price_id": "$price_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$price_id"]}}}, 
                                                                                         {"$project": {"_id": 0, "format": 1, "price": 1, "pic_url": {"$concat": [domain, "$pic_url"]}}}], "as": "price_item"}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}, 
                                                                                            {"$project": {"_id": 0, "format": 1, "big_pic_url": 1, "pic_url": 1}}], "as": "pic_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "portrait": {"$arrayElemAt": ["$portrait_item", 0]}, "product": {"$arrayElemAt": ["$products_item", 0]}, "pic_info": {"$arrayElemAt": ["$pic_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "account": "$user_info.account", "pic_url": "$pic_info.pic_url", "size": "$pic_info.size", "big_pic_url": "$pic_info.big_pic_url"}},
            {"$unset": ["user_item", "user_info", "pic_item", "pic_info", "portrait._id", "products._id"]},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "format": 1, "size": "$size", "portrait": {"$ifNull": ["$portrait", "无"]}, "product": {"$ifNull": ["$product", "无"]}, "price_item": 1, "pic_url": {"$concat": [domain, "$pic_url"]},
                          "nick": 1, "account": 1, "tag": 1, "state": 1, "big_pic_url": {"$concat": [domain, "$big_pic_url"]}, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list[0] if data_list else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_atals_detail(domain=constant.DOMAIN):
    """
    图集详情页
    :param domain: 域名
    """
    try:
        # 参数
        works_id = request.args.get('works_id')
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        pipeline = [
            {"$match": {"uid": works_id, "type": "tj"}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline":[{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"thumb_url": {"$concat": [domain, "$$item.thumb_url"]}, "title": "$$item.title", 
                            "uid": "$$item.uid", "works_state": "$$item.works_state"}}}, "nick": "$user_info.nick", "account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info", "pic_temp_item"]},
            {"$project": {"_id": 0, "cover_url": {"$concat": [domain, "$cover_url"]}, "title": 1, "label": 1, "state": 1, "account": 1, "nick": 1, "user_id": 1,
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, "pic_item": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list[0] if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_altas_deital_material_list(search_max=32, domain=constant.DOMAIN):
    """
    图片素材库列表接口
    :param search_max: 搜索内容最大字符数
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        user_id = request.args.get("user_id")
        num = request.args.get("num") # ≥1
        page = request.args.get("page") # ≥1
        content = request.args.get("content")
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg=f"搜索内容最长{search_max}个字符，请重新输入", code=1)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info"]},
            {"$match": {"$or": [{"title" if content else "null": {"$regex": content} if content else None}, 
                                {"label" if content else "null": content if content else None},
                                {"account" if content else "null": {"$regex": content} if content else None}]}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "account": 1, "create_time": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 统计总数用于分页
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info"]},
            {"$match": {"$or": [{"title" if content else "null": {"$regex": content} if content else None}, 
                                {"label" if content else "null": content if content else None},
                                {"account" if content else "null": {"$regex": content} if content else None}]}},
            {"$count": "count"}
        ]
        temp_cursor = manage.client["pic_material"].aggregate(pipeline)
        temp_data_list = [doc for doc in temp_cursor]
        data["count"] = temp_data_list[0]["count"] if temp_data_list else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_altas_works_pic_id(pic_length_max=20):
    """
    图集作品添加图片
    :param pic_length_max: 最多允许选择的图片数
    """
    try:
        # 参数
        works_id = request.json.get("works_id")
        pic_id = request.json.get("pic_id") # array
        if not works_id:
            return response("Bad Request: Miss params 'works_id'.", code=1, status=400)
        if len(pic_id) > pic_length_max:
            return response(msg=f"最多允许选择{pic_length_max}张图片", code=1)
        doc = manage.client["works"].find_one({"uid": works_id})
        temp_list = doc.get("pic_id") + pic_id
        doc = manage.client["works"].update({"uid": works_id}, {"$set": {"pic_id": temp_list}})
        if doc["n"] == 0:
            return response(msg="'works' update failed.", code=1, status=400)
        return response()
    except AttributeError as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_altas_works_editor(title_length_max=32, label_length_max=20):
    """
    图集编辑作品
    :param title_length_max: 标题上限
    :param label_length_max: 标签上限
    """
    try:
        # 参数
        works_id = request.json.get("works_id")
        title = request.json.get("title")
        label = request.json.get("label")
        state = request.json.get("state") # 0未审核，1审核中，2已上架, 3违规下架
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss params: 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题最多允许{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss params: 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"标签最多允许{label_length_max}个", code=1)
        if state not in [3, 0, 1, 2]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        # 更新
        doc = manage.client["works"].update({"uid": works_id}, {"$set": {"title": title, "state": state, "label": label}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_article_works_detail(domain=constant.DOMAIN):
    """
    图文详情页
    :param domain: 域名
    """
    try:
        # 获取uid
        works_id = request.args.get("works_id", None)
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        pipeline = [
            {"$match": {"uid": works_id}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "content": 1, "nick": 1, "head_img_url": 1, "browse_num": 1, "comment_num": 1, "like_num": 1, "share_num": 1, "format": 1,
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data = [doc for doc in cursor]
        if not data:
            return response(msg="Article data does not exist", code=1, status=400)
        return response(data=data[0])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_altas_works_pic_delete():
    """图集详情删除图片接口"""
    try:
        # 参数
        works_id = request.json.get("works_id")
        pic_id = request.json.get("pic_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        if not pic_id:
            return response(msg="Bad Request: Miss params: 'pic_id'.", code=1, status=400)
        # 更新数据库
        doc = manage.client["works"].update({"uid": works_id}, {"$pull": {"pic_id": pic_id}})
        if doc["n"] == 0:
            return response(msg="'works' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)