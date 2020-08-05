#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_front_api.py
@Time: 2020-07-19 15:18:19
@Author: money 
"""
##################################【后台前台设置模块】##################################
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
from app_works_api import pic_upload_api

def get_banner(domain=constant.DOMAIN):
    """
    获取banner
    :param domain: 域名
    """
    try:
        # 获取数据
        pipeline = [
            {"$match": {"state": 1}},
            {"$project": {"_id": 0, "uid": 1, "link": 1, "order": 1, "pic_url": {"$concat": [domain, "$pic_url"]}, 
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "update_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$update_time"]}}}}}
        ]
        cursor = manage.client["banner"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        if not data_list:
            raise Exception("No data in the database")
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_banner_link():
    """修改banner链接"""
    try:
        # 获取数据
        link = request.json.get("link")
        banner_id = request.json.get("banner_id")
        if not link:
            return response(msg="Bad Request: Miss params: 'link'.", code=1, status=400)
        if not banner_id:
            return response(msg="Bad Request: Miss params: 'banner_id'", code=1, status=400)
        # 更新link
        doc = manage.client["banner"].update({"uid": banner_id}, {"$set": {"link": link}})
        if doc == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_banner_order():
    """修改banner的序号"""
    try:
        # 获取参数
        inc = request.json.get("inc") # 向上传1， 向下传-1
        banner_id = request.json.get("banner_id")
        if not banner_id:
            return response(msg="Bad Request: Miss params: 'banner_id'", code=1, status=400)
        # 更新
        doc = manage.client["banner"].update({"uid": banner_id}, {"$inc": {"order": inc}})
        if doc == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_banner_state():
    """删除banner"""
    try:
        # 获取banner_id
        banner_id = request.json.get("banner_id")
        if not banner_id:
            return response(msg="Bad Request: Miss params: 'banner_id'", code=1, status=400)
        # 更新
        doc = manage.client["banner"].update({"uid": banner_id}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_upload_banner():
    """上传banner图"""
    try:
        user_id = g.user_data["user_id"]
        data_list = pic_upload_api(user_id)
        file_path = data_list[0]["file_path"]
        # 入库
        uid = base64.b64encode(os.urandom(16)).decode()
        manage.client["banner"].insert({"uid": uid, "order": 0, "state": 1, "pic_url": file_path, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_hot_keyword_list(limit=10):
    """
    热搜词列表页
    :param limit: 前一日关键词热搜前10
    """
    try:
        # 获取数据
        pipeline = [
            {"$match": {"state": {"$ne": -1}}},
            {"$group": {"_id": {"keyword": "$keyword", "state": "$state"}, "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "keyword": "$_id.keyword", "count": 1}},
            {"$sort": SON([("count", -1)])},
            {"$limit": limit}
        ]
        cursor = manage.client["user_search"].aggregate(pipeline)
        hot_list = [doc["keyword"] for doc in cursor]
        # 推荐关键词
        cursor = manage.client["user_search"].find({"state": 0}, {"_id": 0, "keyword": 1})
        recomm_list = [doc["keyword"] for doc in cursor]
        data_list = hot_list + recomm_list
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_add_keyword():
    """添加关键词"""
    try:
        # 获取参数
        keyword = request.json.get("keyword")
        user_id = g.user_data["user_id"]
        if not keyword:
            return response(msg="Bad Request: Miss params: 'keyword'", code=1, status=400)
        # 添加
        manage.client["user_search"].insert({"user_id": user_id, "keyword": keyword, "state": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_delete_keyword():
    """删除关键词"""
    try:
        # 获取参数
        keyword = request.json.get("keyword")
        if not keyword:
            return response(msg="Bad Request: Miss params: 'keyword'", code=1, status=400)
        doc = manage.client["user_search"].update({"keyword": keyword}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_label_list():
    """可选栏目列表"""
    data = {}
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        type = request.args.get("type") # 图集传pic， 影集传video
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if type not in ["pic", "video"]:
            return response(msg="Bad Request: Params 'type' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"state": {"$ne": -1}, "type": type}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "create_time": 0, "update_time": 0}}
        ]
        cursor = manage.client["label"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        condition = {"state": {"$ne": -1}, "type": type}
        count = manage.client["label"].find(condition).count()
        data["count"] = count
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


# def get_label_state():
#     """可选栏目列表（隐藏、显示）"""
#     try:
#         # 参数
#         num = request.args.get("num")
#         page = request.args.get("page")
#         type = request.args.get("type") # 图集传pic， 影集传video
#         state = request.args.get("state") # 显示传1， 隐藏传0， 默认传-1
#         # 校验参数
#         if not num:
#             return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
#         if not page:
#             return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
#         if int(page) < 1 or int(num) < 1:
#             return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
#         if type not in ["pic", "video"]:
#             return response(msg="Bad Request: Params 'type' is error.", code=1, status=400)
#         if state not in ["-1", "0", "1"]:
#             return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
#         # 查询
#         pipeline = [
#             {"$match": {"state": {"$ne": -1} if int(state) == -1 else {"$eq": int(state)} , "type": type}},
#             {"$skip": (int(page) - 1) * int(num)},
#             {"$limit": int(num)},
#             {"$project": {"_id": 0}}
#         ]
#         cursor = manager.client["label"].aggregate(pipeline)
#         data_list = [doc for doc in cursor]
#         if not data_list:
#             raise Exception("No data in the database")
#         return response(data=data_list)
#     except Exception as e:
#         manage.log.error(e)
#         return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_lable_priority():
    """设置标签优先级"""
    try:
        # 参数
        priority = request.json.get("priority")
        label_id = request.json.get("label_id")
        if not priority:
            return response(msg="Bad Request: Miss params: 'priority'.", code=1, status=400)
        if not label_id:
            return response(msg="Bad Request: Miss params: 'label_id'.", code=1, status=400)
        doc = manage.client["label"].update({"uid": label_id}, {"$set": {"priority": priority}})
        if doc["n"] == 0:
            return response(msg="Updated failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_show_label(option_max=20):
    """
    设置标签是显示、隐藏、删除
    :param option_max: 允许选择关键词的上限
    """
    try:
        # 参数
        keyword = request.json.get("keyword") # array
        state = request.json.get("state") # 显示传1，隐藏传0， 删除传-1
        if not keyword:
            return response(msg="Bad Request: Miss params: 'keyword'.", code=1, status=400)
        if len(keyword) > option_max:
            return response(msg=f"最多允许选择{option_max}个关键词", code=1)
        if state not in [-1, 0, 1]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        doc = manage.client["label"].update({"label": {"$in": keyword}}, {"$set": {"state": int(state)}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)

