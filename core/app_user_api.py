#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: userinfo_api.py
@Time: 2020-07-12 16:31:01
@Author: money 
"""
##################################【app用户中心模块】##################################
import sys
import os
# 将根目录添加到sys路径中
# 将根目录添加到sys路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2)

import re
import string
import time
import random
import datetime
import hashlib
import base64
import manage
import jieba
from bson.son import SON
from flask import request, g
from utils.util import response, UploadSmallFile, genrate_file_number, IdCardAuth
from constant import constant
from app_works_api import pic_upload_api


def follow_list_api(user_id, domain=constant.DOMAIN):
    """
    我的/他的关注调用接口
    :param user_id: 用户id
    :param  domain: 域名
    """
    try:
        # 查询数据
        pipeline = [
            {"$match": {"fans_id": user_id, "state": 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$replaceRoot": {"$newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_item", 0]}]}}},
            {"$project": {"_id": 0, "user_id": 1, "nick": 1, "head_img_url": {"$concat": [domain, "$head_img_url"]}, "works_num": 1}}
        ]
        cursor = manage.client["follow"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return data_list
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def fans_list_api(user_id, domain=constant.DOMAIN):
    """
    我的/他的关注调用接口
    :param user_id: 用户id
    :param  domain: 域名
    """
    try:
        # 查询数据
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$replaceRoot": {"$newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_item", 0]}]}}},
            {"$project": {"_id": 0, "user_id": 1, "nick": 1, "head_img_url": {"$concat": [domain, "$head_img_url"]}, "login_time": 1}}
        ]
        cursor = manage.client["follow"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return data_list
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def user_works_api(user_id, page, num, domain=constant.DOMAIN):
    """
    用户作品调用接口
    :param user_id: 用户id
    :param page: 页码
    :param num: 页数
    :param domain: 域名
    """
    try:
        # 用户作品
        pipeline = [
            {"$match": {"user_id": user_id, "state": {"$ne": -1}}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "video_material", "let": {"video_id": "$video_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$video_id"]}}}], "as": "video_item"}},
            {"$lookup": {"from": "audio_material", "let": {"audio_id": "$audio_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$audio_id"]}}}], "as": "audio_item"}},
            {"$lookup": {"from": "like_records", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "browse_records", "let": {"works_id": "$u id", "user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$works_id", "$$works_id"]},
                                                                                                                                                    {"$eq": ["$user_id", user_id]}]}}}], "as": "browse_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "browse_info": {"$arrayElemAt": ["$browse_item", 0]}, "video_info": {"$arrayElemAt": ["$video_item", 0]}, "audio_info": {"$arrayElemAt": ["$audio_item", 0]}, 
                            "like_info": {"$arrayElemAt": ["$like_item", 0]}}},
            {"$addFields": {"video_url": "$video_info.video_url", "audio_url": "$audio_info.audio_url", "count": {"$cond": {"if": {"$in": [user_id, "$browse_item.user_id"]}, "then": 1, "else": 0}}, 
                            "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}}},
            {"$unset": ["pic_temp_item", "browse_info", "video_item", "audio_item", "video_info", "audio_info", "like_item", "like_info", "browse_item"]},
            {"$project": {"_id": 0}},
            {"$sort": SON([("create_time", -1)])}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        works_list = [doc for doc in cursor]
        return works_list
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_message():
    """我的消息"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询数据
        cursor = manage.client["message"].find({"user_id": user_id, "state": 1}, {"_id": 0, "state": 0})
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_message_alter():
    """删除我的消息"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        msg_uid = request.json.get("uid", None)
        if not msg_uid:
            return response(msg="Bad Request: Miss params 'uid'.", code=1, status=400)
        # 更改state为-1
        doc = manage.client["message"].update({"uid": msg_uid, "user_id": user_id}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'msg_uid' is error.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_follow_search():
    """搜索我的关注"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        search_kw = request.args.get("search_kw", None) 
        if not search_kw:
            return response(msg="请输入内容", code=1)
        
        # 查询数据
        pipeline = [
            {"$match": {"fans_id": user_id, "state": 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$replaceRoot": {"$newRoot": {"$mergeObjects": [{"$arrayElemAt": ["$user_item", 0]}]}}},
            {"$match": {"nick": {"$regex": search_kw}}},
            {"$project": {"_id": 0, "user_id": 1, "nick": 1, "head_img_url": 1, "works_num": 1}}
        ]
        cursor = manage.client["follow"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_follow_state():
    """取消关注"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 作者author_id
        author_id = request.json.get("author_id", None)
        if not author_id:
            return response(msg="Bad Request: Miss params 'author_id'.", code=1, status=400)
        # 更改state为-1
        doc = manage.client["follow"].update({"user_id": author_id, "fans_id": user_id}, {"$set": {"state": -1}}) # 更新成功doc["n"] = 1, 失败doc["n"] = 0
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'author_id' is error.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_follow_works():
    """我的关注作品动态"""
    data = {}
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"fans_id": user_id, "state": 1}},
            {"$lookup": {"from": "works", "let": {"user_id": "$user_id", "last_time": "$last_look_time"}, 
                         "pipeline": [{"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}, "$create_time": {"$gte": "$$last_time"}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$unset": ["works_item._id"]},
            {"$project": {"_id": 0, "works_item": 1}}
        ]
        cursor = manage.client["follow"].aggregate(pipeline)
        data_list = []
        for doc in cursor:
            for i in doc.get("works_item"):
                data_list.append(i)
        count = len(data_list)
        data["count"] = count
        data["works_list"] = data_list
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_userinfo():
    """用户基本信息"""

    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        user_info = g.user_data["user_info"]
        # 计算注册时长
        register_time = user_info["create_time"]
        login_time = user_info["login_time"]
        delta_time = (login_time - register_time) // (24 * 3600 * 1000)
        user_info["day"] = delta_time
        # 待付款订单数
        order_count = manage.client["order"].find({"user_id": user_id, "state": 0}).count()
        # 关注用户的作品动态数
        # 查询数据
        pipeline = [
            {"$match": {"fans_id": user_id, "state": 1}},
            {"$lookup": {"from": "works", "let": {"user_id": "$user_id", "last_time": "$last_look_time"}, 
                         "pipeline": [{"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}, "create_time": {"$gte": "$$last_time"}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$unset": ["works_item._id"]},
            {"$count": "count"}
        ]
        cursor = manage.client["follow"].aggregate(pipeline)
        data = [doc for doc in cursor]
        dynamic_count = 0
        if data:
            dynamic_count = data[0]["count"]
        user_info["order_count"] = order_count
        user_info["dynamic_count"] = dynamic_count
        return response(data=user_info)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_interest_label():
    """用户推荐兴趣标签"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        doc = manage.client["user"].find_one({"uid": user_id})
        label = doc.get("label")
        cursor = manage.client["interest_label"].find({}, {"_id": 0, "label": 1, "related": 1})
        data_list = []
        for doc in cursor:
            data_list.append(doc.get("label"))
            data_list += doc.get("related")
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_head_img():
    """修改用户头像"""
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        data_list = pic_upload_api(user_id)
        obj = data_list[0]
        head_img_url = obj.get("file_path")
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"head_img_url": head_img_url}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_user_background_img():
    """修改用户背景图"""
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        data_list = pic_upload_api(user_id)
        obj = data_list[0]
        background_img_url = obj.get("file_path")
        doc = manage.client["user"].update({"uid": user_id}, {"$set": {"background_url": background_img_url}})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_alter_userinfo(nick_max=10, label_max=20, sign_max=60):
    """
    修改用户信息
    :param: nick_max: 昵称上限
    :param: label_max: 标签上限
    :param: sign_max: 签名上限
    """

    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 校验参数
        user_info = request.get_json()  # nick昵称 sign签名 label标签 sex性别
        if not user_info.keys():
            return response(msg="Bad Request: Please upload the field name of the modification item.", code=1, status=400)
        if user_info.get("nick") and len(user_info.get("nick")) > nick_max:
            return response(msg="昵称上限10个字符", code=1)
        if user_info.get("sign") and len(user_info.get("sign")) > sign_max:
            return response(msg="签名上限60个字符", code=1)
        if user_info.get("sex") and user_info.get("sex") not in ["男", "女", "保密"]:
            return response(msg="Bad Request: Parameter error: 'sex'", code=1, status=400)
        if user_info.get("label") and len(user_info.get("label")) > label_max:
            return response(msg="标签上限20个", code=1)
        # 入库
        doc = manage.client["user"].update({"uid": user_id}, {"$set": user_info})
        if doc["n"] == 0:
            return response(msg="Bad Request: Params 'user_id' is error.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_sales_records():
    """销售记录"""
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 获取参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        # 校验参数
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "amount": 1, "create_time": 1}},
            {"$sort": SON([("create_time", -1)])}
        ]
        cursor = manage.client["sales_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_data_statistic():
    """商品概况"""
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$groud": {"_id": "$user_id", "browse_num": {"$sum": "$browse_num"}, "sale_num": {"$sum": "$sale_num"}, "comment_num": {"$sum": "$comment_num"}, "amount_num": {"$sum": "$amount"}, 
                        "share_num": {"$sum": "$share_num"}, "like_num": {"$sum": "$like_num"}}},
            {"$project": {"_id": 0, "browse_num": 1, "comment_num": 1, "amount_num": 1, "share_num": 1, "like_num": 1, "sale_num": 1}}
        ]
        cursor = manage.client["user_statistical"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_paymethod_show():
    """我的账户提现方式展示"""
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询数据
        cursor = manage.client["support_method"].find({"state": 1}, {"_id": 0, "channel": 1, "ico_url": 1, "fees": 1})
        data_list = [doc for doc in cursor]
        if not data_list:
            return response(msg="Internal Server Error: Lack of data in database.", code=1, status=500)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_balance():
    """余额"""
    data = {}
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询数据
        # 当前与昨天时间
        today = datetime.datetime.now()
        date = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
        yesterday_stamp = int(time.mktime((timeArray - datetime.timedelta(days=1)).timetuple())) * 1000
        doc = manage.client["user"].find_one({"uid": user_id, "state": 1}, {"_id": 0, "balance": 1})
        data["balance"] = doc.get("balance")
        doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": yesterday_stamp}, {"_id": 0, "amount": 1})
        data["amount"] = doc.get("amount")
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_withdrawal_apply():
    """提现申请"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        channel = request.json.get("channel")
        trade_name = request.json.get("trade_name") # 提现账户名
        trade_id = request.json.get("trade_id") # 提现账号
        amount = request.json.get("amount")
        if not channel:
            return response(msg="Bad Request: Miss params: 'channel'.", code=1, status=400)
        if not trade_name:
            return response(msg="请填写账户名", code=1)
        if not trade_id:
            return response(msg="请填写账号", code=1)
        if not amount:
            return response(msg="请填写提现金额", code=1)
        if amount < 0:
            return response(msg="请填写正确的金额", code=1)
        doc = manage.client["user"].find_one({"uid": user_id})
        balance = doc["balance"]
        if amount > balance:
            return response(msg="余额不足", code=1)
        order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        condition = {
            "order": order, "channel": channel, "user_id": user_id, "trade_name": trade_name, "trade_id": trade_id, "amount": amount, "state": 1,
            "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        manage.client["withdrawal_records"].insert(condition)
        return response(msg="将在7-14个工作日到账，届时注意查收")
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_home_page():
    """用户主页"""
    data = {}
    try:
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        user_id = request.args.get("user_id", None)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params 'user_id'.", code=1, status=400)
        # 查询数据
        # 用户信息
        doc = manage.client["user"].find_one({"uid": user_id, "stat": 1}, {"_id": 0, "nick": 1, "head_img_url": {"$concat": [domain, "$head_img_url"]}, "sign": 1})
        if not doc:
            return response(msg="Bad Request: The user does not exist.", code=1, status=400)
        data["user_info"] = doc
        # 用户作品
        data_list = user_works_api(user_id, page, num)
        data["works_list"] = works_list
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_follow_list():
    """用户的关注列表"""
    try:
        # 参数
        user_id = request.args.get("user_id", None)
        if not user_id:
            return response(msg="Bad Request: Miss params 'user_id'.", code=1, status=400)
        data_list = follow_list_api(user_id)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error %s." % str(e), code=1, status=500)


def get_user_fans_list(domain=constant.DOMAIN):
    """
    用户的粉丝列表
    :param  domain: 域名
    """
    try:
        # 参数
        user_id = request.args.get("user_id", None)
        if not user_id:
            return response(msg="Bad Request: Miss params 'user_id'.", code=1, status=400)
        data_list = fans_list_api(user_id)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error %s." % str(e), code=1, status=500)


def get_works_manage(domain=constant.DOMAIN):
    """
    我的作品
    :param  domain: 域名
    """
    data = {}
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询数据
        data_list = user_works_api(user_id, page, num)
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_comment_history(domain=constant.DOMAIN):
    """
    我的评论历史
    :param  domain: 域名
    """
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        # 校验
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "like_records", "let": {"comment_id": "$uid"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$comment_id", "$$comment_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}, "like_num": {"$size": "$like_item"}, 
                            "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "title": {"$works_info.title"}}},
            {"$unset": ["user_info", "user_item", "works_item"]},
            {"$project": {"_id": 0, "nick": 1, "is_like": 1, "like_num": 1, "head_img_url": 1, "title": 1}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_like_history(domain=constant.DOMAIN):
    """
    我的点赞历史
    :param  domain: 域名
    """
    try:
        # 用户id
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        num = request.args.get("num", None)
        page = request.args.get("page", None)
        # 校验
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询数据
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$lookup": {"from": "like_records", "let": {"comment_id": "$uid"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$comment_id", "$$comment_id"]}}}], "as": "like_item"}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$works_id"]}}}], "as": "works_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}, "like_info": {"$arrayElemAt": ["$like_item", 0]}, "works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"nick": "$user_info.nick", "is_like": {"$cond": {"if": {"$eq": [user_id, "$like_info.user_id"]}, "then": True, "else": False}}, "like_num": {"$size": "$like_item"}, 
                            "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "title": {"$works_info.title"}}},
            {"$unset": ["user_info", "user_item", "works_item"]},
            {"$match": {"is_like": True}},
            {"$project": {"_id": 0, "nick": 1, "is_like": 1, "like_num": 1, "head_img_url": 1, "title": 1}}
        ]
        cursor = manage.client["comment"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_goods_list(domain=constant.DOMAIN):
    """
    获取用户商品列表
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        content = request.args.get("content") # 默认default
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$lookup": {"from": "works", "let": {"works_id": "$works_id"}, "pipeline": [{"$match": {"$expr": {"$eq": {"$uid", "$$works_id"}}}}], "as": "works_item"}},
            {"$addFields": {"works_info": {"$arrayElemAt": ["$works_item", 0]}}},
            {"$addFields": {"title": "$works_info.title", "pic_id": "$works_info.pic_id", "price_id": "$works_info.price_id", "lable": "$works_info.lable"}},
            {"$match": {"$or": [{"title" if content != "default" else "null": content if content != "default" else None}, 
                                {"label" if content != "default" else "null": content if content != "default" else None}]}},
            {"$unset": ["works_item", "works_info"]},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_item"}},
            {"$lookup": {"from": "price", "let": {"price_id": "$price_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$price_id"]}}}], "as": "price_temp_item"}},
            {"$addFields": {"spec_list": {"$map": {"input": "$price_temp_item", "as": "item", "in": {"pic_url": {"$concat": [domain, "$$item.pic_url"]}, "format": "$$item.format"}}}}}, 
            {"$addFields": {"pic_info": {"$arrayElemAt": ["$pic_item", 0]}}},
            {"$addFields": {"thumb_url": "$pic_item.thumb_url"}},
            {"$unset": ["pic_item", "pic_info", "price_temp_item"]},
            {"$project": {"_id": 0, "thumb_url": {"$concat": [domain, "thumb_url"]}, "title": 1, "works_id": 1, "spec_list": 1}}
        ]
        cursor = manage.client["goods"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_goods_detail():
    """购买图片详情页"""
    try:
        # 用户uid
        user_id = g.user_data["user_id"]
        # 获取图片uid
        uid = request.args.get("uid")
        if not uid:
            return response(msg="Bad Request: Miss params: 'uid'.", code=1, status=400)
        # 查询数据
        # 图片详情信息
        pipeline = [
            {"$match": {"pic_id": uid, "type": {"$in": ["tp", "tj"]}}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline":[{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "title": "$$item.title", "desc":"$$item.desc", "keyword": "$$item.keyword", "label": "$$item.label", "uid": "$$item.uid", "works_id": "$$item.works_id"}}}, 
                            "nick": "$user_info.nick", "head_img_url": {"$concat": [domain, "$user_info.head_img_url"]}, "works_num": "$user_info.works_num", "is_follow": {"$cond": {"if": {"$eq": ["$user_info.uid", user_id]}, "then": True, "else": False}}}},
            {"$unset": ["user_item", "user_info", "pic_temp_item"]},
            {"$project": {"_id": 0}}
        ]
        
        cursor = manage.client["works"].aggregate(pipeline)
        pic_data = [doc for doc in cursor]
        if not pic_data:
            return response(msg="Bad Request: The picture doesn't exist.", code=1, status=400)
        data["pic_data"] = pic_data[0]

        # 规格
        price_data = []
        if pic_data[0].get("price_id"):
            pipeline = [
                {"$match": {"uid": pic_data[0].get("price_id")}},
                {"$lookup": {"from": "goods", "let": {"works_id": "$works_id"}, "pipeline":[{"$match": {"$expr": {"$in": ["$works_id", "$$works_id"]}}}], "as": "goods_item"}},
                {"$addFields": {"goods_info": {"$arrayElemAt": ["$goods_item", 0]}}},
                {"$addFields": {"spec": "$goods_info.spec"}},
                {"$project": {"_id": 0, "pic_url": {"$cond": {"if": {"format": {"$in": "$spec"}}, "then": "$pic_url", "else": None}}, "format": 1, "height": 1, "width": 1, "price": 1, "currency": 1}}
            ]
            cursor = manage.client["price"].aggregate(pipeline)
            price_data = [doc for doc in cursor]
        data["price_data"] = price_data
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_material_list(domain=constant.DOMAIN, length_max=32):
    """
    图片素材库列表
    :param domain: 域名
    :param length_max: 长度上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        page = request.args.get("page")
        num = request.args.get("num")
        content = request.args.get("content")
        if not page:
            return response(msg="Bad Request: Miss param 'page'.", code=1, status=400)
        if not num:
            return response(msg="Bad Request: Miss param 'num'.", code=1, status=400)
        if int(num) < 1 or int(page) < 1:
            return response(msg="Bad Request: Param 'page' or 'num' is error.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Param 'content'.", code=1, status=400)
        if content and len(content) > length_max:
            return response(msg=f"搜索内容最多{length_max}个字符", code=1)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": {"$gte": 0}, "title" if content != "default" else "null": {"$regex": content} if content != "default" else None}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "label": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "big_pic_url": {"$concat": [domain, "$big_pic_url"]}, "create_time": 1}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_material_title(length_max=32):
    """
    修改标题接口
    :param length_max: 长度上限
    """
    try:
         # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_id = request.json.get("pic_id")
        title = request.json.get("title")
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > length_max:
            return response(msg=f"标题上限{length_max}个字符", code=1)
        doc = manage.client["pic_material"].update({"uid": pic_id}, {"$set": {"title": title}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'pic_id' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_material_label(length_max=20):
    """
    修改标签接口
    :param length_max: 长度上限
    """
    try:
         # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_id = request.json.get("pic_id")
        label = request.json.get("label")
        if not pic_id:
            return response(msg="Bad Request: Miss param 'pic_id'.", code=1, status=400)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > length_max:
            return response(msg=f"标签最多选择{length_max}个", code=1)
        doc = manage.client["pic_material"].update({"uid": pic_id}, {"$set": {"label": label}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'pic_id' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_material_state(length_max=20):
    """
    删除图片接口
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_id_list = request.json.get("pic_id_list") # array
        if not pic_id_list:
            return response(msg="Bad Request: Miss param 'pic_id_list'.", code=1, status=400)
        doc = manage.client["pic_material"].update({"uid": {"$in": pic_id_list}}, {"$set": {"state": -1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'pic_id_list' is error.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_material_upload():
    """素材库上传图片接口"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        data_list = pic_upload_api(user_id)
        # 入库
        temp_list = []
        for obj in data_list:
            uid = base64.b64encode(os.urandom(32)).decode()
            condition = {"uid": uid, "user_id": user_id, "pic_url": obj["file_path"], "big_pic_url": obj["file_path"], "thumb_url": obj["file_path"], "size": obj["size"],
                         "state": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
            }
            temp_list.append(condition)
        manage.client["pic_material"].insert(temp_list)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_audio_material_list(domain=constant.DOMAIN, length_max=32):
    """
    音频素材库列表
    :param domain: 域名
    :param length_max: 长度上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        page = request.args.get("page")
        num = request.args.get("num")
        content = request.args.get("content")
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Param 'content'.", code=1, status=400)
        if len(content) > length_max:
            return response(msg=f"搜索内容最多{length_max}个字符", code=1)
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1, "title" if content != "default" else "null": {"$regex": content} if content != "default" else None}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "cover_url": {"$concat": [domain, "$cover_url"]}, "audio_url": {"$concat": [domain, "$audio_url"]}, "label": 1, "create_time": 1}}
        ]
        cursor = manage.client["audio_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_audio_material_title(length_max=32):
    """
    修改音频标题接口
    :param length_max: 长度上限
    """
    try:
         # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        audio_id = request.json.get("audio_id")
        title = request.json.get("title")
        if not audio_id:
            return response(msg="Bad Request: Miss param 'audio_id'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > length_max:
            return response(msg=f"标题上限{length_max}个字符", code=1)
        doc = manage.client["audio_material"].update({"uid": audio_id}, {"$set": {"title": title}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'audio_id' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_audio_material_label(length_max=20):
    """
    修改音频标签接口
    :param length_max: 长度上限
    """
    try:
         # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        audio_id = request.json.get("audio_id")
        label = request.json.get("label")
        if not audio_id:
            return response(msg="Bad Request: Miss param 'audio_id'.", code=1, status=400)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > length_max:
            return response(msg=f"标签最多选择{length_max}个", code=1)
        doc = manage.client["audio_material"].update({"uid": audio_id}, {"$set": {"label": label}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'audio_id' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_audio_material_state(length_max=20):
    """
    删除音频接口
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        audio_id_list = request.json.get("audio_id_list") # array
        if not audio_id_list:
            return response(msg="Bad Request: Miss param 'audio_id_list'.", code=1, status=400)
        doc = manage.client["audio_material"].update({"uid": {"$in": audio_id_list}}, {"$set": {"state": -1}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'audio_id_list' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_audio_material_upload_pic(length_max=32, label_max=20, domain=constant.DOMAIN):
    """
    音频库上传图片接口
    :param length_max: 长度上限
    :param label_max: 标题上限
    :domain domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        cover_url = request.json.get("cover_url")
        audio_url = request.json.get("audio_url")
        audio_size = request.json.get("audio_size")
        title = request.json.get("title")
        label = request.json.get("label")
        if not cover_url:
            return response(msg="Bad Request: Miss param 'cover_url'.", code=1, status=400)
        if not audio_url:
            return response(msg="Bad Request: Miss param 'audio_url'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if not audio_size:
            return response(msg="Bad Request: Miss param 'audio_size'.", code=1, status=400)
        if len(title) > length_max:
            return response(msg=f"标题最长允许{length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_max:
            return response(msg=f"最多只允许选择{label_max}个标签", code=1)
        uid = base64.b64encode(os.urandom(32)).decode()
        cover_url = cover_url.replace(domain, "")
        audio_url = audio_url.replace(domain, "")
        keyword = list(jieba.cut(title))
        condition = {"uid": uid, "user_id": user_id, "size": audio_size, "state": 1, "cover_url": cover_url, "thumb_url": cover_url, "audio_url": audio_url, "title": title,
                     "keyword": keyword, "label": label, "create_time": int(time.time()) * 1000, "update_time": int(time.time()) * 1000
        }
        manage.client["audio_material"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_wokrs_list(domain=constant.DOMAIN, length_max=32):
    """
    图片、图集作品列表
    :param domain: 域名
    :param length_max: 长度上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        page = request.args.get("page")
        num = request.args.get("num")
        content = request.args.get("content")
        state = request.args.get("state") # 0未审核，1审核中，2已上架, 3违规下架，4全部
        type = request.args.get("type") # tp图片，tj图集, yj影集
        if not page:
            return response(msg="Bad Request: Miss param 'page'.", code=1, status=400)
        if not num:
            return response(msg="Bad Request: Miss param 'num'.", code=1, status=400)
        if int(num) < 1 or int(page) < 1:
            return response(msg="Bad Request: Param 'page' or 'num' is error.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Param 'content'.", code=1, status=400)
        if len(content) > length_max:
            return response(msg=f"搜索内容最多{length_max}个字符", code=1)
        if state not in ["1", "2", "3", "4", "0"]:
            return response(msg="Bad Request: Param 'state' is error.", code=1, status=400)
        if type not in ["tp", "tj"]:
            return response(msg="Bad Request: Param 'type' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": {"$gte": 0}, "type": type, "title" if content != "default" else "null": {"$regex": content} if content != "default" else None, 
                        "state": {"$ne": -1} if state == "4" else int(state)}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}}}}}},
            {"$addFields": {"temp_item": {"$arrayElemAt": ["$pic_item", 0]}}},
            {"$addFields": {"big_pic_url": "$temp_item.big_pic_url"}},
            {"$project": {"_id": 0, "uid": 1, "pic_id":1, "title": 1, "big_pic_url": 1, "label": 1, "state": 1, "create_time": 1, "pic_item": 1, "cover_url": {"$concat": [domain, "$cover_url"]}}},
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_works_state():
    """删除作品"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id_list = request.json.get("works_id_list") # array
        if not works_id_list:
            return response(msg="Bad Request: Miss param 'works_id_list'.", code=1, status=400)
        doc = manage.client["works"].update({"uid": {"$in": works_id_list}}, {"$set": {"state": -1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'works_id_list' is error.", code=1, status=500)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_works_details(domain=constant.DOMAIN):
    """
    图片上架详情页
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        group = g.user_data["user_info"]["group"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        if group == "comm":
            return response(msg="只有认证摄影师才能申请上架哦，快前往认证吧", code=1)
        works_id = request.args.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss param 'works_id'.", code=1, status=400)
        pipeline = [
            {"$match": {"user_id": user_id, "uid": works_id}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$lookup": {"from": "price", "let": {"price_id": "$price_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$price_id"]}}}], "as": "price_temp_item"}},
            {"$addFields": {"price_item": {"$map": {"input": "$price_temp_item", "as": "item", "in": {"format": {"$cond": {"if": {"$in": ["$$item.format", ["S", "M", "L"]]}, 
                                                                                                                           "then": {"$concat": ["$$item.format", "级分辨率售价"]}, 
                                                                                                                           "else": {"$concat": ["$$item.format", "售价"]}}}, "price": "$$item.price", "type":"$$item.type"}}}}},
            {"$addFields": {"temp_item": {"$arrayElemAt": ["$pic_temp_item", 0]}}},
            {"$addFields": {"big_pic_url": "$temp_item.big_pic_url"}},
            {"$unset": ["pic_temp_item", "price_temp_item", "temp_item"]},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "code": {"$cond": {"if": {"$in": [1, "$price_item.type"]}, "then": 1, "else": 0}},"state": 1, 
                          "label": 1, "big_pic_url": {"$concat": [domain, "$big_pic_url"]}, "format": 1, "number": 1, "tag": 1, "price_item": 1}}
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list[0] if data_list else {})
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)

# 弃用
def post_pic_portrait(domain=constant.DOMAIN, home_length_max=128, nick_length_max=64):
    """
    肖像权接口
    :param home_length_max: 地址长度上限
    :param nick_length_max: 昵称长度上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        pic_url = request.json.get("pic_url")
        shoot_addr = request.json.get("shoot_addr")
        shoot_time = request.json.get("shoot_time")
        authorizer = request.json.get("authorizer")
        b_name = request.json.get("b_name")
        b_id_card = request.json.get("b_id_card")
        b_mobile = request.json.get("b_mobile")
        b_home_addr = request.json.get("b_home_addr")
        check = IdCardAuth()
        # 校验
        if not works_id:
            return response(msg="Bad Request: Miss Param 'works_id'.", code=1, status=400)
        if not pic_url:
            return response(msg="请上传参考肖像图", code=1)
        if not shoot_addr:
            return response(msg="请输入拍摄地点", code=1)
        if len(shoot_addr) > home_length_max:
            return response(msg=f"拍摄地址最多允许{home_length_max}个字符", code=1)
        if not shoot_time:
            return response(msg="请输入拍摄时间", code=1)
        if not authorizer:
            return response(msg="请输入授权人信息.", code=1)
        if not b_name:
            return response(msg="请输入乙方姓名", code=1)
        if len(b_name) > nick_length_max:
            return response(msg=f"乙方姓名最多允许{nick_length_max}个字符", code=1)
        if not b_id_card:
            return response(msg="请输入乙方身份证号", code=1)
        if not check.check_true(b_id_card):
            return response(msg="请输入乙方正确的身份证号", code=1)
        if not b_home_addr:
            return response(msg="请输入乙方地址", code=1)
        if not b_mobile:
            return response(msg="请输入乙方电话", code=1)
        for i in authorizer:
            if "name" not in i:
                return response(msg="请输入授权人姓名", code=1)
            if len(i["name"]) > nick_length_max:
                return response(msg=f"授权人姓名最多允许{nick_length_max}个字符", code=1)
            if "id_card" not in i:
                return response(msg="请输入授权人身份证号", code=1)
            if not check.check_true(i["id_card"]):
                return response(msg="请输入授权人正确的身份证号", code=1)
            if "sex" not in i:
                return response(msg="请输入授权人性别", code=1)
            if "mobile" not in i:
                return response(msg="请输入授权人电话", code=1)
            if len(str(i["mobile"])) != 11:
                return response(msg="请输入授权人正确的手机号", code=1)
            if not re.match(r"1[35678]\d{9}", str(i["mobile"])):
                return response(msg="请输入授权人正确的手机号", code=1)
            if "home_addre" not in i:
                return response(msg="请输入授权人地址", code=1)
            if "is_adult" not in i:
                return response(msg="请选择授权人是否成年", code=1)
            if not i["is_adult"]:
                if "g_name" not in i:
                    return response(msg="请输入监护人姓名", code=1)
                if "g_id_card" not in i:
                    return response(msg="请输入监护人身份证", code=1)
                if not check.check_true(i["g_id_card"]):
                    return response(msg="请输入监护人正确的身份证号", code=1)
                if "g_mobile" not in i:
                    return response(msg="请输入监护人手机", code=1)
                if len(str(i["g_mobile"])) != 11:
                    return response(msg="请输入监护人正确的手机号", code=1)
                if not re.match(r"1[35678]\d{9}", str(i["g_mobile"])):
                    return response(msg="请输入监护人正确的手机号", code=1)
        pic_url = pic_url.replace(domain, "")
        uid = base64.b64encode(os.urandom(32)).decode()
        # 入库
        condition = {
            "uid": uid, "user_id": user_id, "works_id": works_id, "pic_url": pic_url, "shoot_addr": shoot_addr, "shoot_time": shoot_time, "authorizer": authorizer, 
            "b_name": b_name, "b_id_card": b_id_card, "b_mobile": b_mobile, "b_home_addr": b_home_addr, "create_time": int(time.time()) * 1000, "update_time": int(time.time()) * 1000
        }
        manage.client["portrait"].insert(condition)
        return response(data=1) # 1已上传，0未上传
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)

# 弃用
def post_pic_property(domain=constant.DOMAIN, home_length_max=128, nick_length_max=64):
    """
    物产权
    :param home_length_max: 地址长度上限
    :param nick_length_max: 昵称长度上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        a_name = request.json.get("a_name")
        a_id_card = request.json.get("a_id_card")
        a_mobile = request.json.get("a_mobile")
        a_home_addr = request.json.get("a_home_addr")
        a_email = request.json.get("a_email")
        a_property_desc = request.json.get("a_property_desc")
        a_property_addr = request.json.get("a_property_addr")
        pic_url = request.json.get("pic_url")
        b_name = request.json.get("b_name")
        b_id_card = request.json.get("b_id_card")
        b_mobile = request.json.get("b_mobile")
        b_email = request.json.get("b_email")
        b_home_addr = request.json.get("b_home_addr")

        check = IdCardAuth()
        # rst = re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", test)
        # 校验
        if not works_id:
            return response(msg="Bad Request: Miss Param 'works_id'.", code=1, status=400)
        if not a_name:
            return response(msg="请输入甲方姓名", code=1)
        if len(a_name) > nick_length_max:
            return response(msg=f"甲方姓名最多允许{nick_length_max}个字符", code=1)
        if not a_mobile:
            return response(msg="请输入甲方手机号", code=1)
        if len(str(a_mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(a_mobile)):
            return response(msg="请输入正确的手机号", code=1)
        if not a_email:
            return response(msg="请输入甲方邮箱", code=1)
        if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", a_email):
            return response(msg="请输入甲方正确的邮箱", code=1)
        if not a_id_card:
            return response(msg="请输入甲方身份证号", code=1)
        if not check.check_true(a_id_card):
            return response(msg="请输入甲方正确的身份证号", code=1)
        if not a_home_addr:
            return response(msg="请输入甲方地址", code=1)
        if len(a_home_addr) > home_length_max:
            return response(msg=f"家庭地址最多允许{home_length_max}个字符", code=1)
        if not b_property_desc:
            return response(msg="请输入财产描述", code=1)
        if not b_property_addr:
            return response(msg="请输入财产地址", code=1)
        if not pic_url:
            return response(msg="请上传参考肖像图", code=1)
        if not authorizer:
            return response(msg="请输入授权人信息.", code=1)
        if not b_name:
            return response(msg="请输入乙方姓名", code=1)
        if len(a_name) > nick_length_max:
            return response(msg=f"乙方姓名最多允许{nick_length_max}个字符", code=1)
        if not b_id_card:
            return response(msg="请输入乙方身份证号", code=1)
        if not check.check_true(b_id_card):
            return response(msg="请输入乙方正确的身份证号", code=1)
        if not b_home_addr:
            return response(msg="请输入乙方地址", code=1)
        if not b_email:
            return response(msg="请输入乙方邮箱", code=1)
        if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", b_email):
            return respbonse(msg="请输入乙方正确的邮箱", code=1)
        if len(str(b_mobile)) != 11:
            return response(msg="请输入乙方正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(b_mobile)):
            return response(msg="请输入乙方正确的手机号", code=1)
        pic_url = pic_url.replace(domain, "")
        uid = base64.b64encode(os.urandom(32)).decode()
        # 入库
        condition = {
            "uid": uid, "user_id": user_id, "works_id": works_id, "a_name": a_name, "a_id_card": a_id_card, "a_mobile": a_mobile, "a_home_addr": a_home_addr, "pic_url": pic_url, 
            "a_email": a_email, "b_email": b_mobile, "a_property_desc": a_property_desc, "b_name": b_name, "b_id_card": b_id_card, "b_mobile": b_mobile, "b_home_addr": b_home_addr, 
            "a_property_addr": a_property_addr, "create_time": int(time.time()) * 1000, "update_time": int(time.time()) * 1000
        }
        manage.client["property"].insert(condition)
        return response(data=1) # 1已上传，0未上传
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_portrait_detail(domain=constant.DOMAIN):
    """
    图片作品肖像权信息详情
    :param domain: 域名
    """
    try:
        # 参数
        works_id = request.args.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"works_id": works_id}},
            {"$project": {"_id": 0, "works_id": "$uid", "user_id": 1, "works_id": 1, "pic_url": {"$concat": [domain, "$pic_url"]}, "shoot_addr": 1, "shoot_time": 1, 
                          "authorizer": 1, "b_name": 1, "b_id_card": 1, "b_mobile": 1, "b_home_addr": 1}}
        ]
        cursor = manage.client["portrait"].aggregate(pipeline)
        data = [doc for doc in cursor]
        return response(data=data[0] if data else None)
    except Exception as e:
        manage.log.error(e)


def get_pic_products_detail(domain=constant.DOMAIN):
    """
    图片作品物产权信息详情
    :param domain: 域名
    """
    try:
        # 参数
        works_id = request.args.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"works_id": works_id}},
            {"$project": {"_id": 0, "works_id": "$uid", "user_id": 1, "works_id": 1, "a_name": 1, "a_id_card": 1, "a_mobile": 1, "a_home_addr": 1, "pic_url": {"$concat": [domain, "$pic_url"]},
                          "a_email": 1, "b_name": 1, "a_property_addr": 1, "a_property_desc": 1, "b_id_card": 1, "b_mobile": 1, "b_home_addr": 1,
                          "b_email": 1}}
        ]
        cursor = manage.client["products"].aggregate(pipeline)
        data = [doc for doc in cursor]
        return response(data=data[0] if data else None)
    except Exception as e:
        manage.log.error(e)


def put_pic_portrait_editor(domain=constant.DOMAIN, home_length_max=128, nick_length_max=64):
    """
    肖像权编辑接口
    :param home_length_max: 地址长度上限
    :param nick_length_max: 昵称长度上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        pic_url = request.json.get("pic_url")
        shoot_addr = request.json.get("shoot_addr")
        shoot_time = request.json.get("shoot_time")
        authorizer = request.json.get("authorizer")
        b_name = request.json.get("b_name")
        b_id_card = request.json.get("b_id_card")
        b_mobile = request.json.get("b_mobile")
        b_home_addr = request.json.get("b_home_addr")
        check = IdCardAuth()
        # 校验
        if not works_id:
            return response(msg="Bad Request: Miss Param 'works_id'.", code=1, status=400)
        if not pic_url:
            return response(msg="请上传参考肖像图", code=1)
        if not shoot_addr:
            return response(msg="请输入拍摄地点", code=1)
        if len(shoot_addr) > home_length_max:
            return response(msg=f"拍摄地址最多允许{home_length_max}个字符", code=1)
        if not shoot_time:
            return response(msg="请输入拍摄时间", code=1)
        if not authorizer:
            return response(msg="请输入授权人信息.", code=1)
        if not b_name:
            return response(msg="请输入乙方姓名", code=1)
        if len(b_name) > nick_length_max:
            return response(msg=f"乙方姓名最多允许{nick_length_max}个字符", code=1)
        if not b_id_card:
            return response(msg="请输入乙方身份证号", code=1)
        if not check.check_true(b_id_card):
            return response(msg="请输入乙方正确的身份证号", code=1)
        if not b_home_addr:
            return response(msg="请输入乙方地址", code=1)
        if not b_mobile:
            return response(msg="请输入乙方电话", code=1)
        for i in authorizer:
            if "name" not in i:
                return response(msg="请输入授权人姓名", code=1)
            if len(i["name"]) > nick_length_max:
                return response(msg=f"授权人姓名最多允许{nick_length_max}个字符", code=1)
            if "id_card" not in i:
                return response(msg="请输入授权人身份证号", code=1)
            if not check.check_true(i["id_card"]):
                return response(msg="请输入授权人正确的身份证号", code=1)
            if "sex" not in i:
                return response(msg="请输入授权人性别", code=1)
            if "mobile" not in i:
                return response(msg="请输入授权人电话", code=1)
            if len(str(i["mobile"])) != 11:
                return response(msg="请输入正确授权人的手机号", code=1)
            if not re.match(r"1[35678]\d{9}", str(i["mobile"])):
                return response(msg="请输入正确授权人的手机号", code=1)
            if "home_addre" not in i:
                return response(msg="请输入授权人地址", code=1)
            if "is_adult" not in i:
                return response(msg="请选择授权人是否成年", code=1)
            if not i["is_adult"]:
                if "g_name" not in i:
                    return response(msg="请输入监护人姓名", code=1)
                if "g_id_card" not in i:
                    return response(msg="请输入监护人身份证", code=1)
                if not check.check_true(i["g_id_card"]):
                    return response(msg="请输入监护人正确的身份证号", code=1)
                if "g_mobile" not in i:
                    return response(msg="请输入监护人手机", code=1)
                if len(str(i["g_mobile"])) != 11:
                    return response(msg="请输入监护人正确的手机号", code=1)
                if not re.match(r"1[35678]\d{9}", str(i["g_mobile"])):
                    return response(msg="请输入监护人正确的手机号", code=1)
        pic_url = pic_url.replace(domain, "")
        # 入库
        condition = {
            "pic_url": pic_url, "shoot_addr": shoot_addr, "shoot_time": shoot_time, "authorizer": authorizer, "b_name": b_name, "b_id_card": b_id_card, 
            "b_mobile": b_mobile, "b_home_addr": b_home_addr, "update_time": int(time.time()) * 1000
        }
        doc = manage.client["portrait"].update({"works_id": works_id}, {"$set": condition})
        if doc["n"] == 0:
            uid = base64.b64encode(os.urandom(32)).decode()
            condition.update({"uid": uid, "user_id": user_id, "works_id": works_id, "create_time": int(time.time()) * 1000})
            manage.client["portrait"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_property_editor(domain=constant.DOMAIN, home_length_max=128, nick_length_max=64):
    """
    物产权编辑
    :param home_length_max: 地址长度上限
    :param nick_length_max: 昵称长度上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        a_name = request.json.get("a_name")
        a_id_card = request.json.get("a_id_card")
        a_mobile = request.json.get("a_mobile")
        a_home_addr = request.json.get("a_home_addr")
        a_email = request.json.get("a_email")
        a_property_desc = request.json.get("a_property_desc")
        a_property_addr = request.json.get("a_property_addr")
        pic_url = request.json.get("pic_url")
        b_name = request.json.get("b_name")
        b_id_card = request.json.get("b_id_card")
        b_mobile = request.json.get("b_mobile")
        b_email = request.json.get("b_email")
        b_home_addr = request.json.get("b_home_addr")

        check = IdCardAuth()
        # rst = re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$",test)
        # 校验
        if not works_id:
            return response(msg="Bad Request: Miss Param 'works_id'.", code=1, status=400)
        if not a_name:
            return response(msg="请输入甲方姓名", code=1)
        if len(a_name) > nick_length_max:
            return response(msg=f"甲方姓名最多允许{nick_length_max}个字符", code=1)
        if not a_mobile:
            return response(msg="请输入甲方手机号", code=1)
        if len(str(a_mobile)) != 11:
            return response(msg="请输入正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(a_mobile)):
            return response(msg="请输入正确的手机号", code=1)
        if not a_email:
            return response(msg="请输入甲方邮箱", code=1)
        if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", a_email):
            return response(msg="请输入甲方正确的邮箱", code=1)
        if not a_id_card:
            return response(msg="请输入甲方身份证号", code=1)
        if not check.check_true(a_id_card):
            return response(msg="请输入甲方正确的身份证号", code=1)
        if not a_home_addr:
            return response(msg="请输入甲方地址", code=1)
        if len(a_home_addr) > home_length_max:
            return response(msg=f"家庭地址最多允许{home_length_max}个字符", code=1)
        if not a_property_desc:
            return response(msg="请输入财产描述", code=1)
        if not a_property_addr:
            return response(msg="请输入财产地址", code=1)
        if not pic_url:
            return response(msg="请上传财产参考图", code=1)
        if not b_name:
            return response(msg="请输入乙方姓名", code=1)
        if len(a_name) > nick_length_max:
            return response(msg=f"乙方姓名最多允许{nick_length_max}个字符", code=1)
        if not b_id_card:
            return response(msg="请输入乙方身份证号", code=1)
        if not check.check_true(b_id_card):
            return response(msg="请输入乙方正确的身份证号", code=1)
        if not b_home_addr:
            return response(msg="请输入乙方地址", code=1)
        if not b_email:
            return response(msg="请输入乙方邮箱", code=1)
        if not re.match(r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", b_email):
            return response(msg="请输入乙方正确的邮箱", code=1)
        if len(str(b_mobile)) != 11:
            return response(msg="请输入乙方正确的手机号", code=1)
        if not re.match(r"1[35678]\d{9}", str(b_mobile)):
            return response(msg="请输入乙方正确的手机号", code=1)
        pic_url = pic_url.replace(domain, "")
        # 入库
        condition = {
            "a_name": a_name, "a_id_card": a_id_card, "a_mobile": a_mobile, "a_home_addr": a_home_addr, "pic_url": pic_url, "a_email": a_email, "b_email": b_email,
            "a_property_desc": a_property_desc, "b_name": b_name, "b_id_card": b_id_card, "b_mobile": b_mobile, "b_home_addr": b_home_addr, "a_property_addr": a_property_addr, 
            "update_time": int(time.time()) * 1000
        }
        doc = manage.client["products"].update({"works_id": works_id}, {"$set": condition})
        if doc["n"] == 0:
            uid = base64.b64encode(os.urandom(32)).decode()
            condition.update({"uid": uid, "user_id": user_id, "works_id": works_id, "create_time": int(time.time()) * 1000})
            manage.client["products"].insert(condition)
        return response(data=1)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_apply(label_length_max=20, title_length_max=32):
    """
    图片上架申请
    :param label_length_max: 标签上限
    :param title_length_max: 标题上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid = request.json.get("uid")
        title = request.json.get("title")
        label = request.json.get("label")
        tag = request.json.get("tag") # 商/编
        code = request.json.get("code") # 0代表平台定价，1代表自定义定价。
        price_item = request.json.get("price_item") # 价格信息

        # 校验
        if not uid:
            return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题上限{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"最多允许上传{label_length_max}个", code=1)
        if code not in [1, 0]:
            return response(msg="Bad Request: Params 'code' is error.", code=1, status=400)
        if tag not in ["商", "编"]:
            return response(msg="Bad Request: Params 'tag' is error.", code=1, status=400)
        # 更新图片作品信息
        temp_doc1 = manage.client["portrait"].find_one({"works_id": uid})
        temp_doc2 = manage.client["products"].find_one({"works_id": uid})
        condition = {"$set": {"title": title, "label": label, "state": 1, "tag": tag, "is_portrait": True if temp_doc1 else False, "is_products": True if temp_doc2 else False}}
        doc = manage.client["works"].update({"uid": uid, "user_id": user_id}, condition)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 为S、M、L、扩大授权添加价格
        doc = manage.client["pic_material"].find_one({"works_id": uid})
        if code == 1:
            for i in price_item:
                if len(i["format"]) == 7:
                    manage.client["price"].update({"format": i["format"][:1], "pic_id": doc.get("uid")}, {"$set": {"price": i["price"], "type": code}})
                else:
                    manage.client["price"].update({"format": "扩大授权", "pic_id": doc.get("uid")}, {"$set": {"price": i["price"]}})
        else:
            cursor = manage.client["price"].find({"uid": "001"})
            for i in cursor:
                manage.client["price"].update({"format": i.get("format"), "pic_id": doc.get("uid")}, {"$set": {"price": i.get("price"), "type": code}})
        # 改变素材库中works_state
        manage.client["pic_material"].update({"works_id": uid}, {"$set": {"works_state": 1}})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_pic_works_editor(label_length_max=20, title_length_max=32):
    """
    图片作品编辑
    :param label_length_max: 标签上限
    :param title_length_max: 标题上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid = request.json.get("uid")
        title = request.json.get("title")
        label = request.json.get("label")
        tag = request.json.get("tag") # 商/编
        code = request.json.get("code") # 0代表平台定价，1代表自定义定价。
        price_item = request.json.get("price_item") # 价格信息

        # 校验
        if not uid:
            return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题上限{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"最多允许上传{label_length_max}个", code=1)
        if code not in [1, 0]:
            return response(msg="Bad Request: Params 'code' is error.", code=1, status=400)
        
        if tag not in ["商", "编"]:
            return response(msg="Bad Request: Params 'tag' is error.", code=1, status=400)
        condition = {
            "$set": {"title": title, "label": label, "tag": tag}
        }
        doc = manage.client["works"].update({"uid": uid, "user_id": user_id}, condition)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 为S、M、L、扩大授权添加价格
        doc = manage.client["pic_material"].find_one({"works_id": uid})
        if code == 1:
            for i in price_item:
                if len(i["format"]) == 7:
                    manage.client["price"].update({"format": i["format"][:1], "pic_id": doc.get("uid")}, {"$set": {"price": i["price"], "type": code}})
                else:
                    manage.client["price"].update({"format": "扩大授权", "pic_id": doc.get("uid")}, {"$set": {"price": i["price"]}})
        else:
            cursor = manage.client["price"].find({"uid": "001"})
            for i in cursor:
                manage.client["price"].update({"format": i.get("format"), "pic_id":  doc.get("uid")}, {"$set": {"price": i.get("price"), "type": code}})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_altas_detail(domain=constant.DOMAIN):
    """
    图集上架申请详情
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.args.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss param 'works_id'.", code=1, status=400)
        pipeline = [
            {"$match": {"user_id": user_id, "uid": works_id}},
            {"$lookup": {"from": "pic_material", "let": {"pic_id": "$pic_id"}, "pipeline": [{"$match": {"$expr": {"$in": ["$uid", "$$pic_id"]}}}], "as": "pic_temp_item"}},
            {"$addFields": {"pic_item": {"$map": {"input": "$pic_temp_item", "as": "item", "in": {"big_pic_url": {"$concat": [domain, "$$item.big_pic_url"]}, "thumb_url": {"$concat": [domain, "$$item.thumb_url"]},
                            "uid": "$$item.uid", "works_state": "$$item.works_state"}}}}},
            {"$project": {"_id": 0, "uid": 1, "pic_item": 1, "title": 1, "state": 1, "label": 1, "cover_url": {"$concat": [domain, "$cover_url"]}}},
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list[0] if data_list else {})
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_works_shelvers_apply():
    """
    作品批量上架申请
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        group = g.user_data["user_info"]["group"]
        uid = request.json.get("uid") # array
        is_article = request.json.get("is_article") # 是图文true，不是false
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        if not is_article:
            if group == "comm":
                return response(msg="只有认证摄影师才能申请上架哦，快前往认证吧", code=1)
        if not uid:
            return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
        doc = manage.client["works"].update({"user_id": user_id, "uid": {"$in": uid}}, {"$set": {"state": 1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Bad Request: Param 'uid' is error.", code=1, status=500)
        return response()

    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_altas_apply(label_length_max=20, title_length_max=32, domain=constant.DOMAIN):
    """
    图集上架申请
    :param label_length_max: 标签上限
    :param title_length_max: 标题上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid = request.json.get("uid")
        title = request.json.get("title")
        label = request.json.get("label")
        cover_url = request.json.get("cover_url")
        # 校验
        if not uid:
            return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题上限{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"最多允许上传{label_length_max}个", code=1)
        cover_url = cover_url.replace(domain, "")
        doc = manage.client["works"].update({"uid": uid, "user_id": user_id}, {"$set": {"state": 1, "title": title, "label": label, "cover_url": cover_url}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_altas_detail_editor(label_length_max=20, title_length_max=32, domain=constant.DOMAIN):
    """
    图集上架申请编辑
    :param label_length_max: 标签上限
    :param title_length_max: 标题上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid = request.json.get("uid")
        title = request.json.get("title")
        label = request.json.get("label")
        cover_url = request.json.get("cover_url")
        # 校验
        if not uid:
            return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_length_max:
            return response(msg=f"标题上限{title_length_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_length_max:
            return response(msg=f"最多允许上传{label_length_max}个", code=1)
        cover_url = cover_url.replace(domain, "")
        doc = manage.client["works"].update({"uid": uid, "user_id": user_id}, {"$set": {"title": title, "label": label, "cover_url": cover_url}})
        if doc["n"] == 0:
            return response(msg="Bad Request: Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_article_wokrs_list(domain=constant.DOMAIN, length_max=32):
    """
    图文作品列表
    :param domain: 域名
    :param length_max: 长度上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        page = request.args.get("page")
        num = request.args.get("num")
        content = request.args.get("content")
        state = request.args.get("state") # 0未审核，1审核中，2已上架, 3违规下架，4全部
        if not page:
            return response(msg="Bad Request: Miss param 'page'.", code=1, status=400)
        if not num:
            return response(msg="Bad Request: Miss param 'num'.", code=1, status=400)
        if int(num) < 1 or int(page) < 1:
            return response(msg="Bad Request: Param 'page' or 'num' is error.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Param 'content'.", code=1, status=400)
        if len(content) > length_max:
            return response(msg=f"搜索内容最多{length_max}个字符", code=1)
        if state not in ["0", "1", "2", "3", "4"]:
            return response(msg="Bad Request: Param 'state' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": {"$gte": 0}, "type": "tw", "title" if content != "default" else "null": {"$regex": content} if content != "default" else None, 
                        "state": {"$ne": -1} if state == "4" else int(state)}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "content": 1, "cover_url": {"$concat": [domain, "$cover_url"]}, "state": 1, "create_time": 1}},
        ]
        cursor = manage.client["works"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_area_list():
    """获取地址"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 参数
        step = request.args.get("step") # 一级传1，二级传2，三级传3
        area_id = request.args.get("area_id") # 一级默认传default, 二级、三级传对应的id
        if not step:
            return response(msg="Bad Request: Miss params 'step'.", code=1, status=400)
        if not area_id:
            return response(msg="Bad Request: Miss params 'area_id'.", code=1, status=400)
        condition = {"uid": {"$regex": "0000"}}
        if step == "2":
            str_temp = area_id[:3]
            print(str_temp)
            # condition = {"$and": [{"uid": {"$regex": str_temp}}, {"uid": {"$regex": "00"}}]}
            condition = {"uid": {"$regex": f"{str_temp}.00"}}
        if step == "3":
            str_temp = area_id[:4]
            condition = {"uid": {"$regex": str_temp}}
        # 查询
        cursor = manage.client["area"].aggregate([
            {"$match": condition},
            {"$project": {"_id": 0}}
        ])
        data_list = [doc for doc in cursor]
        return response(data=list(filter(lambda x: x.get("uid") != area_id, data_list)))
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_user_auth_cameraman(title_length_max=32, addr_length_max=128, domain=constant.DOMAIN):
    """
    摄影师认证
    :param title_length_max: 标题上限
    :param addr_length_max: 地址上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        auth = g.user_data["user_info"]["auth"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        if auth == 1:
            return response(msg="您已提交认证申请，请耐心等待", code=1)
        if auth == 2:
            return response(msg="您已成功通过摄影师认证", code=1)
        name = request.json.get("name")
        id_card= request.json.get("id_card")
        addr = request.json.get("addr")
        id_card_a_url = request.json.get("id_card_a_url")
        id_card_b_url = request.json.get("id_card_b_url")
        repre_works = request.json.get("repre_works")
        check = IdCardAuth()
        if not name:
            return response(msg="请输入姓名", code=1, status=400)
        if len(name) > title_length_max:
            return response(msg=f"名字最长允许{title_length_max}个字符", code=1)
        if not check.check_true(id_card):
            return response(msg="请输入正确的身份证号", code=1)
        if not addr:
            return response(msg="请输入地址", code=1, status=400)
        if len(addr) > addr_length_max:
            return response(msg=f"地址最长允许{addr_length_max}个字符", code=1)
        if not all([id_card_b_url, id_card_a_url]):
            return response(msg="请上传身份证正反两面", code=1)
        if len(repre_works) < 5:
            return response(msg="请上传至少五张代表作品", code=1)
        id_card_a_url = id_card_a_url.replace(domain, "")
        id_card_b_url = id_card_b_url.replace(domain, "")
        temp_list = []
        for i in repre_works:
            pic = i.replace(domain, "")
            temp_list.append(pic)
        # 入库
        condition = {"id_card_name": name, "id_card": id_card, "id_card_a_url": id_card_a_url, "id_card_b_url": id_card_b_url, "repre_works": temp_list, "auth": 1, "id_card_addr": addr}
        doc = manage.client["user"].update({"uid": user_id}, {"$set": condition})
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_share_works():
    """作品分享"""
    try:
        # 参数
        works_id = request.json.get("works_id")
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        # 更新数据
        doc = manage.client["works"].update({"uid": works_id}, {"$inc": {"share_num": 1}})
        if doc["n"] == 0:
            return response(msg="'share_num' update failed.", code=1, status=400)
        user_id = manage.client["works"].find_one({"uid": works_id}).get("user_id")
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].update({"user_id": user_id, "date": timestamp}, {"$inc": {"share_num": 1}})
        if doc["n"] == 0:
            manage.client["user_statistical"].insert({"user_id": user_id, "date": timestamp, "share_num": 1, "create_time": int(time.time() * 1000),
                                                      "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)