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
            {"$group": {"_id": {"keyword": "$keyword"}, "count": {"$sum": 1}}},
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
        doc = manage.client["user_search"].find_one({"user_id": user_id, "keyword": keyword})
        if not doc:
            manage.client["user_search"].insert({"user_id": user_id, "keyword": keyword, "state": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        else:
            return response(msg="关键词已存在，请勿重复添加", code=1)
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
        doc = manage.client["user_search"].update({"keyword": keyword}, {"$set": {"state": -1}}, multi=True)
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


def get_video_top_list(domain=constant.DOMAIN):
    """
    置顶影集列表
    :param domain: 域名
    """
    try:
        pipeline = [
            {"$match": {"type": "yj", "order": {"$ne": None}}},
            {"$project": {"_id": 0, "uid": 1, "top_title": 1, "browse_num": 1, "comment_num": 1, "like_num": 1, "share_num": 1, "top_cover_url": {"$concat": [domain, "$top_cover_url"]}, "update_time": 1, "order": 1}},
            {"$sort": SON([("order", -1)])}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_video_order_sort():
    """置顶影集排序"""
    try:
        # 参数
        works_id = request.json.get("works_id")
        order = request.json.get("order") # 升序 1  降序 -1
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'", code=1, status=400)
        if order not in [-1, 1]:
            return response(msg="Bad Request: Params 'order' is error", code=1, status=400)
        doc = manage.client["works"].update({"uid": works_id}, {"$inc": {"order": order}})
        if doc["n"] == 0:
            return response(msg="Bad Request: 'order' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def delete_video_works():
    """删除置顶影集"""
    try:
        # 参数
        works_id = request.json.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'", code=1, status=400)
        doc = manage.client["works"].update({"uid": works_id}, {"$set": {"order": None}})
        if doc["n"] == 0:
            return response(msg="Bad Request: 'order' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_option_video_list():
    """提供选择的影集列表"""
    data = {}
    try:
        # 参数
        content = request.args.get('content')
        page = request.args.get("page")
        num = request.args.get("num")
        type = request.args.get("type") #添加add 编辑editor
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not type:
            return response(msg="Bad Request: Miss params: 'type'.", code=1, status=400)
        pipeline = [
            {"$match": {"type": "yj", "order" if type == "add" else "null": {"$eq": None} if type == "add" else None, 
                        "title" if content else "null": {"$regex": content} if content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "localField": "user_id", "foreignField": "uid", "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "account": "$user_info.account"}},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("order", -1)])}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"type": "yj", "order" if type == "add" else "null": {"$eq": None} if type == "add" else None, 
                        "title" if content else "null": {"$regex": content} if content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        temp_list = [doc for doc in cursor]
        count = temp_list[0]["count"] if temp_list else 0
        data["list"] = data_list
        data["count"] = count
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_video_works(limit=20, domain=constant.DOMAIN):
    """
    编辑置顶影集接口
    :param limit: 置顶影集数上限
    :param domain: 域名
    """
    try:
        # 校验
        count = manage.client["works"].find({"order": {"$ne": None}, "type": "yj"}).count()
        if count >= limit:
            return response(msg="置顶影集数，已超上限", code=1)
        # 参数
        video_info = request.get_json() # works_id top_title top_cover_url video_id
        if "works_id" not in video_info:
            if "top_title" not in video_info:
                return response(msg="Bad Request: Miss params 'top_title'.", code=1, status=400)
            if "top_cover_url" not in video_info:
                return response(msg="Bad Request: Miss params 'top_cover_url'.", code=1, status=400)
            if "video_id" not in video_info:
                return response(msg="Bad Request: Miss params 'video_id'.", code=1, status=400)
            video_id = video_info["video_id"]
            video_info.pop("video_id")
            video_info.update({"order": 1})
            video_info["top_cover_url"] = video_info["top_cover_url"].replace(domain, "")
            manage.client["works"].update({"uid": video_id}, {"$set": video_info})
        else:
            if not video_info.values():
                return response(msg="请填写影集相关信息", code=1, status=400)
            works_id = video_info["works_id"]
            video_id = video_info["video_id"]
            video_info.pop("works_id")
            if "top_cover_url" in video_info:
                video_info["top_cover_url"] = video_info["top_cover_url"].replace(domain, "")
            if video_id != works_id:
                video_info.pop("video_id")
                video_info.update({"order": 1})
                manage.client["works"].update({"uid": works_id}, {"$set": {"order": None, "top_title": None, "top_cover_url": None}})
                manage.client["works"].update({"uid": video_id}, {"$set": video_info})
            else:
                manage.client["works"].update({"uid": works_id}, {"$set": video_info})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)
