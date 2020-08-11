#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: list_api.py
@Time: 2020-07-02 09:10:59
@Author: money 
"""
##################################【app列表页、详情页模块】##################################
import os
import sys
# 将根目录添加到sys路径中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

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




def total_list_api(user_id, page, num, sort_field, sort_way, recommend, is_recommend=False, like_max=1, recomm_max=1, domain=constant.DOMAIN):
    """
    综合页推荐查询调用接口
    :param user_id: 用户id
    :param page: 页码
    :param num: 页数
    :param sort_field: 排序字段
    :param sort_way: 排序方式
    :param recommend: 是否推荐查询
    :param recomm_max: 每页插入推荐作品个数
    :param like_max: 点赞数
    :param domain: 域名
    """
    try:
        # 24小时
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        # 推荐作品
        cursor = manage.client["works"].find({"is_recommend": True, "state": 2, "like_num": {"$gt": like_max}}, {"_id": 0}).skip(int(page) - 1).limit(1)
        doc = [doc for doc in cursor]
        # 综合作品 "$and":[{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}],
        pipeline = [
            {"$match": {"state": 2, "is_recommend": True if recommend else False}}, # "like_num": {"$gt": like_max}
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "video_material", "let": {"video_id": "$video_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$video_id"]}}}], "as": "video_item"}},
            {"$lookup": {"from": "audio_material", "let": {"audio_id": "$audio_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$audio_id"]}}}], "as": "audio_item"}},
            {"$lookup": {"from": "like_records", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "browse_records", "let": {"works_id": "$uid", "user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]},
                                                                                                                                                   {"$eq": ["$user_id", user_id]}]}}}], "as": "browse_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "user_info": {"$arrayElemAt": ["$user_item", 0]}, "browse_info": {"$arrayElemAt": ["$browse_item", 0]}, "video_info": {"$arrayElemAt": ["$video_item", 0]},
                            "audio_info": {"$arrayElemAt": ["$audio_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "works_num": "$user_info.works_num", "video_url": "$video_info.video_url", 
                            "audio_url": "$audio_info.audio_url", "count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}}, "cover_url": {"$concat": [domain, "$cover_url"]},
                            "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}}},
            {"$unset": ["pic_temp_item", "user_item", "user_info", "browse_info", "video_item", "audio_item", "video_info", "audio_info", "like_item", "like_info"]},
            {"$project": {"_id": 0}}
        ]
        # 是否推荐
        if not recommend:
            skip = {"$skip": (int(page) - 1) * ((int(num) - 1) if doc else (int(page) - 1) * int(num))}
            limit = {"$limit": ((int(num) - 1) if doc else int(num))}
            pipeline.insert(1, skip)
            pipeline.insert(2, limit)
        else:
            limit = {"$limit": recomm_max}
            pipeline.append(limit)
        # 排序
        if sort_field != "default": pipeline.append({"$sort": SON([("create_time", int(sort_way))])})
        cursor = manage.client["works"].aggregate(pipeline)
        return cursor, doc
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def pic_list_api(user_id, page, num, label, sort_way, recommend, is_recommend=False, like_max=1, recomm_max=1, domain=constant.DOMAIN):
    """
    图集推荐查询调用接口
    :param user_id: 用户id
    :param page: 页码
    :param num: 页数
    :param label: 排序字段
    :param sort_way: 排序方式
    :param recommend: 是否推荐查询
    :param recomm_max: 每页插入推荐作品个数
    :param like_max: 点赞数
    :param domain: 域名
    """
    try:

        # 24小时
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        # 推荐作品
        condition = {"type": {"$in": ["tp", "tj"]}, "state": 2, "is_recommend": True, "like_num": {"$gt": like_max}}
        if label != "default": condition.update({"label": label})
        cursor = manage.client["works"].find(condition, {"_id": 0}).skip(int(page) - 1).limit(1)
        doc = [doc for doc in cursor]
        # 图集数据
        pipeline = [
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "like_records", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "browse_records", "let": {"works_id": "$uid", "user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]},
                                                                                                                                                   {"$eq": [user_id, "$$user_id"]}]}}}], "as": "browse_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "browse_info": {"$arrayElemAt": ["$browse_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}}, "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}}},
            {"$unset": ["pic_temp_item", "browse_info", "browse_item", "like_item", "like_info"]},
            {"$project": {"_id": 0}}
        ]

        # 是否推荐
        if not recommend:
            skip = {"$skip": (int(page) - 1) * ((int(num) - 1) if doc else (int(page) - 1) * int(num))}
            limit = {"$limit": ((int(num) - 1) if doc else int(num))}
            pipeline.insert(1, skip)
            pipeline.insert(2, limit)
            # "$and": [{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}], 
            match_data = {"$match": {"type": {"$in": ["tp", "tj"]}, "state": 2, "is_recommend": False, "like_num": {"$gt": like_max}}}
            if label != "default": 
                match_data["$match"].update({"label": label})
                pipeline.append({"$sort": SON([("browse_num", int(sort_way))])})
        else:
            match_data = {"$match": {"type": {"$in": ["tp", "tj"]}, "state": 2, "is_recommend": True, "like_num": {"$gt": like_max}}}
            if label != "default": 
                match_data["$match"].update({"label": label})
            pipeline.append({"$skip": int(page) - 1})
            pipeline.append({"$limit": recomm_max})
        # 排序
        pipeline.insert(0, match_data)
        cursor = manage.client["works"].aggregate(pipeline)
        return cursor, doc
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def video_list_api(user_id, page, num, label, sort_way, recommend, is_recommend=False, like_max=1, recomm_max=1, domain=constant.DOMAIN):
    """
    影集推荐查询接口
    :param user_id: 用户id
    :param page: 页码
    :param num: 页数
    :param label: 排序字段
    :param sort_way: 排序方式
    :param recommend: 是否推荐查询
    :param recomm_max: 每页插入推荐作品个数
    :param like_max: 点赞数
    :param domain: 域名
    """
    try:
        # 24小时
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        # 推荐作品
        condition = {"type": {"$in": ["tp", "tj"]}, "state": 2, "is_recommend": True, "like_num": {"$gt": like_max}}
        if label != "default": condition.update({'label': label})
        cursor = manage.client["works"].find(condition, {"_id": 0}).skip(int(page) - 1).limit(1)
        doc = [doc for doc in cursor]
        # 图集数据
        pipeline = [
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "video_material", "let": {"video_id": "$video_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$video_id"]}}}], "as": "video_item"}},
            {"$lookup": {"from": "audio_material", "let": {"audio_id": "$audio_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$audio_id"]}}}], "as": "audio_item"}},
            {"$lookup": {"from": "like_records", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "browse_records", "let": {"works_id": "$uid", "user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]},
                                                                                                                                                   {"$eq": [user_id, "$$user_id"]}]}}}], "as": "browse_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "browse_info": {"$arrayElemAt": ["$browse_item", 0]}, "video_info": {"$arrayElemAt": ["$video_item", 0]}, "audio_info": {"$arrayElemAt": ["$audio_item", 0]}, 
                            "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}}, "video_url": "$video_info.video_url", "audio_url": "$audio_info.audio_url", 
                            "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}}},
            {"$unset": ["pic_temp_item", "browse_info", "browse_item", "video_item", "audio_item", "video_info", "audio_info", "like_item", "like_info"]},
            {"$project": {"_id": 0}}
        ]
                # 是否推荐
        if not recommend:
            skip = {"$skip": (int(page) - 1) * ((int(num) - 1) if doc else (int(page) - 1) * int(num))}
            limit = {"$limit": ((int(num) - 1) if doc else int(num))}
            pipeline.insert(1, skip)
            pipeline.insert(2, limit)
            # "$and": [{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}], 
            match_data = {"$match": {"type": {"$eq": "yj"}, "state": 2, "is_recommend": False, "like_num": {"$gt": like_max}}}
            if label != "default": 
                match_data["$match"].update({"label": label})
                pipeline.append({"$sort": SON([("browse_num", int(sort_way))])})
        else:
            match_data = {"$match": {"type": {"$eq": "yj"}, "state": 2, "is_recommend": True, "like_num": {"$gt": like_max}}}
            if label != "default": 
                match_data["$match"].update({"label": label})
            pipeline.append({"$skip": int(page) - 1})
            pipeline.append({"$limit": recomm_max})
        # 排序
        pipeline.insert(0, match_data)
        cursor = manage.client["works"].aggregate(pipeline)
        return cursor, doc
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_browse_records():
    """浏览记录"""
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取参数
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        works_id_list = request.json.get("works_id", None) # array
        for works_id in works_id_list:
            if not works_id:
                return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
            if not user_id:
                return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
            doc = manage.client["works"].find_one({"uid": works_id})
            if not doc:
                return response(msg="Bad Request: 'works_id' data does not exist.", code=1, status=400)
            type = doc.get("type")
            # 记录
            condition = {"user_id": user_id, "works_id": works_id, "type": type, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["browse_records"].insert(condition)
            # 浏览量+1
            doc = manage.client["works"].update({"uid": works_id}, {"$inc": {"browse_num": 1}})
            if doc["n"] == 0:
                return response(msg="Bad Request: Params 'works_id' is error.", code=1, status=400)
            # 凌晨时间戳
            today = datetime.date.today()
            today_stamp = int(time.mktime(today.timetuple())*1000)
            doc = manage.client["works"].find_one({"works_id": works_id})
            author_id = doc.get("user_id")
            doc = manage.client["user_statistical"].find_one({"user_id": author_id, "date": today_stamp})
            if doc:
                manage.client["user_statistical"].update({"user_id": author_id, "date": today_stamp}, {"$inc": {"browse_num": 1}})
            else:
                manage.client["user_statistical"].insert({"user_id": author_id, "date": today_stamp, "browse_num": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return resposne(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_banner(banner_max=3, domain=constant.DOMAIN):
    """
    轮播图接口
    :param banner_max: 轮播图数量
    :param domain: 域名
    """
    try:
        pipeline =[
            {"$match": {"state": 1}},
            {"$sort": SON([("order", 1)])},
            {"$limit": banner_max},
            {"$project": {"_id": 0, "pic_url": {"$concat": [domain, "$pic_url"]}, "order": 1, "link": 1}}
        ]
        cursor = manage.client["banner"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Eexception as e:
        manage.log.error(e)
        return resposne(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_label_kw(kw_max=5, label_max=5):
    """
    获取标签、热搜词
    :param kw_max： 推荐一个小时内的热搜词个数
    :param label_max: 栏目标签最大个数
    """
    data = {}
    try:
        # 参数
        type = request.args.get("type", None) # pic图集 video影集
        user_id = g.user_data["user_id"]  # 用户登录时, 必须传type; 未登录时可不传
        # 校验
        if not type:
            return response(msg="Bad Request: Miss params: 'type'.", code=1, status=400)
        if type not in ["pic", "video"]:
            return response(msg="Bad Request: The parameter 'type' is incorrect", code=1, status=400)
        # 查询数据
        if type == "pic":
            # 热搜词
            now_time = datetime.datetime.now()
            last_one_time = now_time - datetime.timedelta(hours=1)
            now_time_timestamp = int(time.mktime(now_time.timetuple())) * 1000
            last_one_timestamp = int(time.mktime(last_one_time.timetuple())) * 1000
            # 查询条件
            pipeline = [
                # {"$match": {"$and":[{"create_time": {"$gte": last_one_timestamp}}, {"create_time": {"$lte": now_time_timestamp}}]}},
                {"$group": {"_id": "$keyword", "count": {"$sum": 1}}},
                {"$project": {"_id": 0, "keyword": "$_id", "count": 1}},
                {"$sort": SON([("count", -1)])},
                {"$limit": kw_max}
            ]
            cursor = manage.client["user_search"].aggregate(pipeline)
            hot_kw = [doc["keyword"] for doc in cursor]
            data["hot_kw"] = hot_kw
        # 标签栏目
        # 查询条件
        doc = manage.client["custom_label"].find_one({"user_id": user_id})
        if not doc:
            pipeline = [
                {"$match": {"priority": {"$gt": 0}, "state": 1, "type": type}},
                {"$sort": SON([("priority", -1)])},
                {"$limit": label_max},
                {"$project": {"_id": 0, "label": 1}},
            ]
            cursor = manage.client["label"].aggregate(pipeline)
            label = [doc["label"] for doc in cursor]
        else:
            doc = manage.client["custom_label"].find_one({"user_id": user_id, "type": type, "state": 1}, {"_id": 0})
            label = doc.get("label")
        data["label"] = label
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error %s." % str(e), code=1, status=500)


def get_total_list():
    """
    发现列表页
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        sort_way = request.args.get("sort_way", None)  # 正序传1，倒序传-1
        sort_field = request.args.get("sort_field", None)
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if sort_way and sort_way not in ["-1", "1"]:
            return response(msg="Bad Request: Parameter error: 'sort_way'.", code=1, status=400)
        if sort_field not in ["default", "time"]:
            return response(msg="Bad Request: Parameter error: 'sort_field'.", code=1, status=400)

        recommend = False
        # 未推荐作品
        cursor, doc = total_list_api(user_id, page, num, sort_field, sort_way, recommend)
        data_list = [doc for doc in cursor]
        # 推荐作品
        if doc and data_list:
            recommend = True
            cursor, _ = total_list_api(user_id, page, num, sort_field, sort_way, recommend)
            doc = [doc for doc in cursor][0]
            random_num = random.randint(0, int(num))
            data_list.insert(random_num, doc)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error：%s." % str(e), code=1, status=500) 


def get_hot_article_list(hot_max=10):
    """
    图文列表页热点文章
    :param hot_max: 热点文章最大数量
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 24小时
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        # 热点文章
        pipeline = [
            {"$match": {"$and":[{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}], "state": 2}},
            {"$lookup": {"from": "blacklist", "let": {"user": user_id, "uid": "$uid"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$user_id","$$user"]}, {"$in": ["$black_id", ["$$uid", "$$user"]]}]}}}], "as": "black_item"}},
            {"$match": {"black_item": {"$eq": None}}},
            {"$sort": SON([("browse_num", -1)])},
            {"$limit": hot_max},
            {"$project": {"_id": 0}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error : %s." % str(e), code=1, status=500)


def get_article_list(domain=constant.DOMAIN):
    """"
    图文列表页
    :param domain: 域名
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        sort_way = request.args.get("sort_way", None)  # 正序传1，倒序传-1
        sort_field = request.args.get("sort_field", None)
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if sort_way and sort_way not in ["-1", "1"]:
            return response(msg="Bad Request: Parameter error: 'sort_way'.", code=1, status=400)
        if sort_field:
            return response(msg="Bad Request: Parameter error: 'sort_field'.", code=1, status=400)
        # 24小时
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        # 图文作品
        pipeline = [
            {"$match": {"state": 2}},
            {"$lookup": {"from": "blacklist", "let": {"user": user_id, "uid": "$uid"}, 
                         "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$user_id","$$user"]}, {"$in": ["$black_id", ["$$uid", "$$user"]]}]}}}], "as": "black_item"}},
            {"$match": {"black_item": {"$eq": None}}},                                                                                                      
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "like_records", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "browse_records", "let": {"works_id": "$uid", "user_id": "$user_id"}, 
                         "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]}, {"$eq": ["$user_id", user_id]}]}}}], "as": "browse_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "works_num": "$user_info.works_num", 
                            "count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}},
                            "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}}},
            {"$unset": ["pic_item._id", "pic_item.pic_url", "user_item", "user_info", "browse_info", "video_item", "audio_item", "video_info", "audio_info", "like_item", "like_info"]},
            {"$project": {"_id": 0}}
        ]
        # 排序
        if sort_field != "default": pipeline.append({"$sort": SON([("create_time", int(sort_way))])})
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_list():
    """
    图集、图片列表页
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        sort_way = request.args.get("sort_way", None)  # 正序传1，倒序传-1
        label = request.args.get("label", None)
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if sort_way and sort_way not in ["-1", "1"]:
            return response(msg="Bad Request: Parameter error: 'sort_way'.", code=1, status=400)

        recommend = False
        # 未推荐作品
        cursor, doc = pic_list_api(user_id, page, num, label, sort_way, recommend)
        data_list = [doc for doc in cursor]
        # 推荐作品
        if doc and data_list:
            recommend = True
            cursor, _ = pic_list_api(user_id, page, num, label, sort_way, recommend)
            doc = [doc for doc in cursor][0]
            random_num = random.randint(0, int(num))
            data_list.insert(random_num, doc)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_video_top_list(video_top_max=10):
    """
    影集置顶列表
    :param video_top_max: 置顶影集个数
    """
    try:
        # 置顶影集
        pipeline = [
            {"$match": {"order": {"$ne": None}}},
            {"$sort": SON([("order", 1)])},
            {"$limit": video_top_max},
            {"$project": {"_id": 0, "uid": 1, "cover_url": 1, "titel": 1, "like_num": 1, "browse_num": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error : %s." % str(e), code=1, status=500)


def get_video_list():
    """
    影集列表页
    """
    data = {}
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        sort_way = request.args.get("sort_way", None)  # 正序传1，倒序传-1
        label = request.args.get("label", None)
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if sort_way and sort_way not in ["-1", "1"]:
            return response(msg="Bad Request: Parameter error: 'sort_way'.", code=1, status=400)

        recommend = False
        # 未推荐作品
        cursor, doc = video_list_api(user_id, page, num, label, sort_way, recommend)
        data_list = [doc for doc in cursor]
        # 推荐作品
        if doc and data_list:
            recommend = True
            cursor, _ = video_list_api(user_id, page, num, label, sort_way, recommend)
            doc = [doc for doc in cursor][0]
            random_num = random.randint(0, int(num))
            data_list.insert(random_num, doc)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_detail(domain=constant.DOMAIN):
    """
    图片、图集详情页
    :param domain: 域名
    """
    data = {}
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取图片uid
        uid = request.args.get("uid")
        works_id = request.args.get("works_id")
        if not uid:
            return response(msg="Bad Request: Miss params: 'uid'.", code=1, status=400)
        # 查询数据
        # 图片详情信息
        pipeline = [
            {"$match": {"uid": works_id, "pic_id": uid, "type": {"$in": ["tp", "tj"]}}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline":[{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "follow", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}, "state": 1}}], "as": "follow_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "works_num": "$user_info.works_num", "is_follow": {"$cond": {"if": {"$in": [user_id, "$follow_item.fans_id"]}, "then": True, "else": False}}}},
            {"$unset": ["user_item", "user_info", "pic_temp_item", "follow_item"]},
            {"$project": {"_id": 0}}
        ]
        
        cursor = manage.client["works"].aggregate(pipeline)
        pic_data = [doc for doc in cursor]
        if not pic_data:
            return response(msg="Bad Request: The picture doesn't exist.", code=1, status=400)
        data["pic_data"] = pic_data[0]

        # TODO 筛选与此作品对应的价格信息，并满足state=1
        price_data = []
        if pic_data[0].get("price_id"):
            cursor = manage.client["price"].find({"uid": pic_data[0]["price_id"]}, {"_id": 0})
            price_data = [doc for doc in cursor]
        data["price_data"] = price_data

        # 图集信息
        pipeline = [
            {"$match": {"type": "tj", "pic_id": uid}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$unset": ["pic_item._id", "pic_item.pic_url"]},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}}},
            {"$project": {"_id": 0, "pic_item": {"$filter": {"input": "$pic_item", "as": "pic", "cond": {"$ne": ["$$pic.uid", uid]}}}}},
            {"$project": {"pic_item": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        altas_data = [doc for doc in cursor]
        data["altas_data"] = altas_data[0]["pic_item"] if altas_data else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_video_detail(domain=constant.DOMAIN):
    """
    影集详情页
    :param domain: 域名
    """
    data = {}
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取uid
        uid= request.args.get("works_id", None)
        if not uid:
            return response(msg="Bad Request: Miss params: 'uid'.", code=1, status=400)
       
        # 影集详情
        pipeline = [
            {"$match": {"uid": uid}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "video_material", "let": {"video_id": "$video_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$video_id"]}}}], "as": "video_item"}},
            {"$lookup": {"from": "audio_material", "let": {"audio_id": "$audio_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$audio_id"]}}}], "as": "audio_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "user_info": {"$arrayElemAt": ["$user_item", 0]}, "video_info": {"$arrayElemAt": ["$video_item", 0]}, "audio_info": {"$arrayElemAt": ["$audio_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "works_num": "$user_info.works_num", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "video_url": "$video_info.video_url", 
                            "audio_url": "$audio_info.audio_url", "is_follow": {"$cond": {"if": {"$eq": ["$user_info.uid", user_id]}, "then": True, "else": False}}}},
            {"$unset": ["pic_temp_item", "user_item", "user_info", "video_item", "audio_item", "video_info", "audio_info"]},
            {"$project": {"_id": 0}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data = [doc for doc in cursor]
        return response(data=data[0] if data else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_article_detail(domain=constant.DOMAIN):
    """
    图文详情页
    :param domain: 域名
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取uid
        uid = request.args.get("uid", None)
        if not uid:
            return response(msg="Bad Request: Miss params: 'uid'.", code=1, status=400)
        pipeline = [
            {"$match": {"uid": uid}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "is_follow": {"$cond": {"if": {"$eq": ["$user_info.uid", user_id]}, "then": True, "else": False}}}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data = [doc for doc in cursor]
        if not data : raise Exception("Article data does not exist")
        return response(data=data[0])
    except Exception as e:
        lgo.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_hot_keyword(kw_max=10):
    """
    热搜关键词
    :param kw_max: 热搜词个数
    """
    try:
        # 24小时
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        today_timestamp = int(time.mktime(today.timetuple())) * 1000
        yesterday_timestamp = int(time.mktime(yesterday.timetuple())) * 1000
        pipeline = [
            # todo 移除注释
            {"$match": {"$and":[{"create_time": {"$gte": yesterday_timestamp}}, {"create_time": {"$lte": today_timestamp}}], "state": {"$gt": 0}}},
            {"$group": {"_id": "$keyword", "count": {"$sum": 1}}},
            {"$project": {"count": 1, "keyword": "$_id"}},
            {"$sort": SON([("count", -1)])},
            {"$limit": kw_max}
        ]
        cursor = manage.client["user_search"].aggregate(pipeline)
        data_list_1 = []
        for i in cursor:
            data_list_1.append(i.get("keyword"))
        cursor = manage.client["user_search"].find({"state": 0})
        data_list_2 = []
        for i in cursor:
            data_list_2.append(i.get("keyword"))
        data_list = data_list_1 + data_list_2
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_search_keyword():
    """关键词搜索接口"""
    keyword_list = []
    try:
        # 获取关键词
        keyword = request.args.get("keyword", None)
        # 校验
        if not keyword:
            return response(msg="请输入关键词", code=1)

        # 模糊查询
        cursor = manage.client["keyword"].find({"keyword": {"$regex": f"{keyword}"}}, {"_id": 0})
        keyword_list.append(keyword)
        for doc in cursor:
            keyword_list += doc["related"]
        if keyword in keyword_list:
            keyword_list = list(set(keyword_list))
            keyword_list.remove(keyword)
            keyword_list.insert(0, keyword)
        return response(data=keyword_list)
    except Exception as e:
        lgo.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_search_works(search_max=100, domain=constant.DOMAIN):
    """
    搜索获取作品
    :param search_max: 返回搜索作品最大个数
    :param domain: 域名
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取关键词
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        keyword = request.args.get("keyword", None)
        sort_way = request.args.get("sort_way", None)  # 正序传1，倒序传-1
        filter_field = request.args.get("filter_field", None) # default默认  tj图集 yj影集 tw图文
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        # 校验
        if not keyword:
            return response(msg="请输入关键词", status=1)
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if sort_way and sort_way not in ["-1", "1"]:
            return response(msg="Bad Request: Parameter error: 'sort_way'.", code=1, status=400)
        if not filter_field:
            return response(msg="Bad Request: Miss params: 'filter_field'.", code=1, status=400)
        # 统计用户搜索关键词
        manage.client["user_search"].insert_one({"user_id": user_id, "keyword": keyword, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "state": 1})

        # 查询话题
        temp_list = []
        num = int(num) if num else search_max
        while True:
            pipeline = [
                {"$match": {"null" if filter_field == "default" else "type": None if filter_field == "default" else {"$in": ["tj", "tp"]} if filter_field == "tj" else filter_field, 
                            "state": 2, "title": {"$regex": f"{keyword}"}}},
                {"$skip": (int(page) - 1) * int(num)},
                {"$limit": int(num)},
                {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
                {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
                {"$lookup": {"from": "video_material", "let": {"video_id": "$video_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$video_id"]}}}], "as": "video_item"}},
                {"$lookup": {"from": "audio_material", "let": {"audio_id": "$audio_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$audio_id"]}}}], "as": "audio_item"}},
                {"$lookup": {"from": "browse_records", "let": {"works_id": "$uid", "user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]},
                                                                                                                                                       {"$eq": ["$user_id", user_id]}]}}}], "as": "browse_item"}},
                {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                                "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                                "user_info": {"$arrayElemAt": ["$user_item", 0]}, "browse_info": {"$arrayElemAt": ["$browse_item", 0]}, "video_info": {"$arrayElemAt": ["$video_item", 0]}, 
                                "audio_info": {"$arrayElemAt": ["$audio_item", 0]}}},
                {"$addFields": {"nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "works_num": "$user_info.works_num", "video_url": "$video_info.video_url",
                                "audio_url": "$audio_info.audio_url", "count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}}}},
                {"$unset": ["pic_temp_item", "user_item", "user_info", "browse_info", "video_item", "audio_item", "video_info", "audio_info"]},
                {"$project": {"_id": 0}}
            ]
            cursor = manage.client["works"].aggregate(pipeline)
            # 判断查询个数
            query_topic = [doc for doc in cursor]
            query_num = len(query_topic)
            n = 1
            works_list = []
            if query_num <= int(num):
                # 遍历将每次查询结果放入列表中
                for doc in query_topic:
                    if doc.get("uid") not in temp_list:
                        temp_list.append(doc.get("uid"))
                        works_list.append(doc)
                # 判断关键词词的长度，只有大于1时才能切片
                if len(keyword) > 2:
                    num = int(num) - query_num
                    # 当查询个数满足请求个数时终止查询
                    if num <= 0:
                        break
                    # 将关键词切片
                    keyword = keyword[:-n]
                    n += 1
                    continue
                else:
                    break
            else:
                break
        return response(data=works_list)

    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_works_like():
    """作品点赞接口"""
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        # 作品uid
        wokrs_id = request.json.get("wokrs_id", None)
        if not wokrs_id:
            return response(msg="Bad Request: Miss params: 'wokrs_id'.", code=1, status=400)
        # 点赞量+1
        doc = manage.client["works"].update({"uid": wokrs_id}, {"$inc": {"like_num": 1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'wokrs_id' is error.", code=1, status=400)
        # 点赞统计
        # 凌晨时间戳
        today = datetime.date.today()
        today_stamp = int(time.mktime(today.timetuple()) * 1000)
        doc = manage.client["works"].find_one({"works_id": works_id})
        author_id = doc.get("user_id")
        doc = manage.client["user_statistical"].find_one({"user_id": author_id, "date": today_stamp})
        if doc:
            manage.client["user_statistical"].update({"user_id": author_id, "date": today_stamp}, {"$inc": {"like_num": 1}})
        else:
            manage.client["user_statistical"].insert({"user_id": author_id, "date": today_stamp, "like_num": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        # 记录点赞记录
        doc = manage.client["like_records"].find_one({"user_id": user_id, "wokrs_id":  wokrs_id, "type": "zp"})
        if doc:
            manage.client["like_records"].update({"user_id": user_id, "wokrs_id": wokrs_id, "type": "zp"}, {"$set": {"state": 0, "update_time": int(time.time() * 1000)}})
        else:
            condition = {"user_id": user_id, "works_id": works_id, "type": "zp", "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["like_records"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_comment_list(domain=constant.DOMAIN):
    """
    评论列表页
    :param domain: 域名
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        wokrs_uid = request.args.get("wokrs_uid", None)
        # 校验
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not wokrs_uid:
            return response(msg="Bad Request: Miss params: 'wokrs_uid'.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"works_id": wokrs_uid, "state": 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "like_records", "let": {"category_id": "$uid"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$category_id", "$$category_id"]}}}], "as": "like_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}, 
                            "nick": "$user_info.nick", "like_num": {"$size": "$like_item"}}},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def  post_comment_records():
    """添加评论"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        # 参数
        content = request.json.get("content", None)
        works_id = request.json.get("works_id", None)
        if not content:
            return response(msg="请输入内容", code=1)
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # 评论入库
        keyword = list(jieba.cut(content))
        doc = manage.client["bad"].find({"keyword": {"$in": keyword}})
        data_list = [doc for doc in cursor]
        if data_list: 
            return response(msg="您输入的内容包含铭感词汇, 请重新输入", code=1)
        uid = base64.b64encode(os.urandom(32)).decode()
        condition = {"uid": uid, "user_id": user_id, "works_id": works_id, "content": content, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
        manage.client["comment"].insert(condition)
        # works表评论量+1
        doc = manage.client["works"].update({"uid": works_id}, {"$inc": {"comment_num": 1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'works_id' is error.", code=1, status=400)
        # 评论统计
        # 凌晨时间戳
        today = datetime.date.today()
        today_stamp = int(time.mktime(today.timetuple())*1000)
        doc = manage.client["works"].find_one({"works_id": works_id})
        author_id = doc.get("user_id")
        doc = manage.client["user_statistical"].find_one({"user_id": author_id, "date": today_stamp})
        if doc:
            manage.client["user_statistical"].update({"user_id": author_id, "date": today_stamp}, {"$inc": {"comment_num": 1}})
        else:
            manage.client["user_statistical"].insert({"user_id": author_id, "date": today_stamp, "comment_num": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_comment_like():
    """评论点赞"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        works_id = request.json.get("works_id", None)
        comment_id = request.json.get("comment_id", None)
        if not comment_id:
            return response(msg="Bad Request: Miss params: 'comment_id'.", code=1, status=400)
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # comment表点赞量+1
        doc =  manage.client["comment"].update({"uid": comment_id}, {"$inc": {"like_num": 1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'comment_id' is error.", code=1, status=400)
        # 写入点赞记录表
        doc = manage.client["like_records"].find_one({"user_id": user_id, "works_id":  works_id, "comment_id": comment_id, "type": "pl"})
        if doc:
            condition = {"user_id": author_id, "works_id": works_id, "comment_id": comment_id, "type": "pl", "update_time": int(time.time() * 1000)}
            manage.client["like_records"].update(condition, {"$set": {"state": 0}})
        else:
            condition = {"user_id": author_id, "works_id": works_id, "comment_id": comment_id, "type": "pl", "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["like_records"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_delete_comment():
    """删除评论"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        comment_id = request.json.get("comment_id", None)
        if not comment_id:
            return response(msg="Bad Request: Miss params: 'comment_id'.", code=1, status=400)
        # 将state改为-1
        doc =  manage.client["comment"].update({"uid": comment_id}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'comment_id' is error.", code=1, status=400)
        # 更新works中的comment_num
        doc = manage.client["comment"].find_one({"uid": comment_id})
        works_id = doc["works_id"]
        doc = manage.client["works"].update({"uid": works_id}, {"$inc": {"comment_num": -1}})
        if doc["n"] == 0:
            return response(msg="'works' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_comment_report():
    """评论举报"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        comment_id = request.json.get("comment_id", None)
        if not comment_id:
            return response(msg="Bad Request: Miss params: 'comment_id'.", code=1, status=400)
        # comment表state更改为0
        doc = manage.client["comment"].update({"uid": comment_id}, {"$set": {"state": 0}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'comment_id' is error.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_follow_user():
    """作者关注接口"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        # 作者uid
        author_id = request.args.get("author_id", None)
        if not author_id:
            return response(msg="Bad Request: Miss params: 'author_id'.", code=1, status=400)
        doc = manage.client["follow"].find_one({"user_id": author_id, "fans_id": user_id})
        if doc:
            # 取消关注
            manage.client["follow"].update({"user_id": author_id, "fans_id": user_id}, {"$set": {"state": 0}})
        else:
            # 关注
            condition = {"user_id": author_id, "fans_id": user_id, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["follow"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_option_label(label_max=20):
    """
    自定义供选标签
    :param label_max: 供选择的标签上限
    """
    try:
        # 参数
        type = request.args.get("type", None)
        # 校验
        if not type:
            return response(msg="Bad Request: Miss params: 'type'.", code=1, status=400)
        if type not in ["pic", "video"]:
            return response(msg="Bad Request: The parameter 'type' is incorrect", code=1, status=400)
        # 查询数据库
        cursor = manage.client["label"].find({"priOrity": 0, "state": 1, "type": type}, {"_id": 0, "label": 1}).limit(label_max)
        data_list = [doc["label"] for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_custom_label(label_max=6):
    """
    自定义标签
    :param label_max: 自定义标签上限
    """
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 参数
        type = request.args.get("type", None) # pic图集， video影集
        label_list = request.json.get("label_list", None)
        visitor_id = request.headers.get("user_id", None)
        user_id = user_id if user_id else visitor_id
        # 校验
        if not type:
            return response(msg="Bad Request: Miss params: 'type'.", code=1, status=400)
        if type not in ["pic", "video"]:
            return response(msg="Bad Request: The parameter 'type' is incorrect", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if label_list:
            return response(msg="请选择标签", code=1)
        if len(label_list) > label_max:
            return response(msg="标签上限6个", code=1)
        # 入库
        manage.client["custom_label"].insert({"user_id": user_id, "type": type, "label": label, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_follow_user():
    """作者关注接口"""
    try:
        # 用户是否登录
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: Please log in.", code=1, status=400)
        # 作者uid
        author_id = request.json.get("author_id")
        if not author_id:
            return response(msg="Bad Request: Miss params: 'author_id'.", code=1, status=400)
        doc = manage.client["follow"].find_one({"user_id": author_id, "fans_id": user_id})
        if doc:
            if doc["state"] == 1:
                # 取消关注
                manage.client["follow"].update({"user_id": author_id, "fans_id": user_id}, {"$set": {"state": 0}})
            else:
                # 重新关注
                manage.client["follow"].update({"user_id": author_id, "fans_id": user_id}, {"$set": {"state": 1}})
        else:
            # 新增关注
            condition = {"user_id": author_id, "fans_id": user_id, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["follow"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)