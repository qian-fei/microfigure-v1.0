#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_opinion_api.py
@Time: 2020-07-19 16:31:50
@Author: money 
"""
##################################【后台舆情监控模块】##################################
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


# 舍弃
def get_report_comment_list():
    """举报评论列表"""
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
        pipeline = [
            {"$match": {"state": 0}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account", "works_title": "$works_info.title"}},
            {"$project": {"_id": 0, "uid": 1, "user_account": 1, "works_title": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "content": 1}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_report_comment_search(search_max=32, delta_time=30):
    """
    举报评论列表搜索
    :param: search_max: 搜索内容上限字符数
    :param delta_time: 允许查询的最大区间30天
    """
    data = {}
    try:
        # 获取参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        state = request.args.get("state")  # 正常评论传1， 举报评论传0 
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
       
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if content and len(content) > search_max:
            return response(msg="搜索内容上限32个字符", code=1)
        if state == "1":
            if not start_time:
                return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
            if not end_time:
                return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
            start_time = start_time + " 00:00:00"
            end_time = end_time + " 23:59:59"
            timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
            end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
            if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
                return response(msg=f"最多可连续查询{delta_time}天以内的评论", code=1)
        pipeline = [
            {"$match": {"state": int(state), "content" if content else "null": {"$regex": content} if content else None}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account", "works_title": "$works_info.title"}},
            {"$project": {"_id": 0, "uid": 1, "user_account": 1, "works_title": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "content": 1}}
        ]
        if state == "1":
            pipeline[0]["$match"].update({"$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}]})
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 总数
        count = manage.client["comment"].find(pipeline[0]["$match"]).count()
        data["count"] = count
        data["list"] = data_list
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_report_comment_state(option_max=10):
    """
    审核举报评论
    :param option_max: 最多允许选择的个数
    """
    try:
        # 参数
        comment_list = request.json.get("comment_list") # array
        state = request.json.get("state") # -1删除，1标记正常
        if not comment_list:
            return response(msg="Bad Request: Miss params: 'comment_list'.", code=1, status=400)
        if len(comment_list) > option_max:
            return response(msg=f"最多允许选择{option_max}条评论", code=1)
        if state not in [-1, 1]:
            return response(msg="Bad Request: Params 'state' is erroe.", code=1, status=400)
        doc = manage.client["comment"].update({"uid": {"$in": comment_list}}, {"$set": {"state": int(state)}}, multi=True)
        doc = manage.client["like_records"].update({"comment_id": {"$in": comment_list}}, {"$set": {"state": int(state)}}, multi=True)
        # 删除评论时，相应减少works中comment_num
        if state == -1:
            cursor = manage.client["comment"].find({"uid": {"$in": comment_list}}, {"_id": 0, "works_id": 1})
            works_id_list = [doc["works_id"] for doc in cursor]
            works_id_list = list(set(works_id_list))
            doc = manage.client["works"].update({"uid": {"$in": works_id_list}}, {"$inc": {"comment_num": -1}})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_report_comment_top():
    """评论相关统计"""
    data = {}
    try:
        # 敏感词数
        bad_count = manage.client["bad"].find({"state": 1}).count()
        # 今日新增评论
        # 24小时
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        pipeline = [
            {"$match": {"state": 1, "$and":[{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}]}},
            {"$count": "count"}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        normal_count = data_list[0]["count"] if data_list else 0
        # 举报评论
        report_count = manage.client["comment"].find({"state": 0}).count()
        data["report_count"] = report_count
        data["normal_count"] = normal_count
        data["bad_count"] = bad_count
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_bad_keyword_list():
    """敏感词列表"""
    try:
        # 查询
        cursor = manage.client["bad"].find({"state": 1})
        data_list = [doc["keyword"] for doc in cursor]
        data_str = "、".join(data_list)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_add_bad_keyword():
    """增加敏感词"""
    try:
        # 参数
        content = request.json.get("content")
        if not content:
            return response(msg="Bad Request: Miss params: 'content'.", code=1, status=400)
        keyword_list = content.split("、")
        temp_list = []
        for i in keyword_list:
            uid = base64.b64encode(os.urandom(16)).decode()
            obj = {"keyword": i, "state": 1}
            temp_list.append(obj)
        manage.client["bad"].drop()
        manage.client["bad"].insert_many(temp_list)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)