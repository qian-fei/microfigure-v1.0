#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: admin_finance_api.py
@Time: 2020-07-25 15:07:38
@Author: money 
"""
##################################【后台财务管理模块】##################################
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
from utils.util import response, ExportExcle
from constant import constant
from app_login_api import check_token


def get_order_list(delta_time=30):
    """
    订单列表页
    :param delta_time: 允许查询的最大区间30天
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account账号
        state = request.args.get("state") # 1未付款，2已完成，3全部
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "order"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["1", "2", "3"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        pipeline = [
            {"$group": {"_id": {"order": "$order", "user_id": "$user_id", "state": "$state", "create_time": "$create_time"}, "amount": {"$sum": "$price"}}},
            {"$project": {"_id": 0, "order": "$_id.order", "user_id": "$_id.user_id", "state": "$_id.state", "create_time": "$_id.create_time", "amount": 1}},
            {"$match": {"state": {"$gte": 1} if state == "3" else int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "state": 1, "user_id": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # 总数
        pipeline = [
            {"$group": {"_id": {"order": "$order", "user_id": "$user_id", "state": "$state", "create_time": "$create_time"}, "amount": {"$sum": "$price"}}},
            {"$project": {"_id": 0, "order": "$_id.order", "user_id": "$_id.user_id", "state": "$_id.state", "create_time": "$_id.create_time", "amount": 1}},
            {"$match": {"state": {"$gte": 1} if state == "3" else int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        count = [doc for doc in cursor]
        data["count"] = count[0]["count"] if count else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_order_refund():
    """订单退款"""
    try:
        # 参数
        user_id = request.json.get("user_id")
        amount = request.json.get("amount")
        order = request.json.get("order")
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        if not amount:
            return response(msg="Bad Request: Miss params: 'amount'.", code=1, status=400)
        if amount <= 0:
            return response(msg="Bad Request: Params: 'amount' is error.", code=1, status=400)
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        doc = manage.client["user"].update({"uid": user_id}, {"$inc": {"balance": amount}})
        if doc["n"] == 0:
            return response(msg="'user' update failed.", code=1, status=400)
        doc = manage.client["order"].update({"order": order}, {"$set": {"state": 3}})
        if doc["n"] == 0:
            return response(msg="'order' update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_order_detail(domain=constant.DOMAIN):
    """
    订单详情
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        order = request.args.get('order')
        user_id = request.args.get('user_id') # 买家id
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        if not user_id:
            return response(msg="Bad Request: Miss params: 'user_id'.", code=1, status=400)
        # 商品信息
        pipeline = [
            {"$match": {"order": order}},
            {"$project": {"_id": 0, "title": 1, "spec": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "currency": 1, "order": 1, "state": 1,
                          "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "update_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$update_time"]}}}}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = []
        amount = 0
        order_info = {}
        for doc in cursor:
            if amount == 0:
                order_info["order"] = doc["order"]
                order_info["create_time"] = doc["create_time"]
                order_info["state"] = doc["state"]
                order_info["update_time"] = doc["update_time"]
            amount += doc["price"]
            data_list.append(doc)
        count = len(data_list)
        # 用户信息
        doc = manage.client["user"].find_one({"uid": user_id}, {"_id": 0, "nick": 1, "account": 1, "mobile": 1})
        data["user_info"] = doc
        data["works_list"] = data_list
        order_info["count"] = count
        order_info["amount"] = amount
        data["order_info"] = order_info
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_withdrawal_records(delta_time=30):
    """
    提现记录
    :param delta_time: 允许查询的最大区间30天
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account账号
        state = request.args.get("state") # 1驳回，2已完成
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "order"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["1", "2"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        pipeline = [
            {"$match": {"state": int(state), "$and": [ {"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "state": 1, "trade_name": 1, "trade_id": 1, "update_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$update_time"]}}}, "channel": 1}}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"state": int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        count = [doc for doc in cursor]
        data["count"] = count[0]["count"] if count else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_recharge_channel():
    """充值全部渠道"""
    try:
        # 查询
        pipeline = [
            {"$group": {"_id": "$channel"}},
            {"$project": {"_id": 0, "channel": "$_id"}}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        data_list = []
        for doc in cursor:
            data_list.append(doc.get("channel"))
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_order_recharge(delta_time=30):
    """
    充值记录
    :param delta_time: 允许查询的最大区间30天
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account充值账号，trade交易号
        state = request.args.get("state") # 0未支付，1已支付完成, 2全部
        channel = request.args.get("channel") # 支付宝/微信 全部default
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "order", "trade"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["2", "1", "0"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        if channel not in ["支付宝", "微信", "default"]:
            return response(msg="Bad Request: Params 'channel' is error.", code=1, status=400)
        pipeline = [
            {"$match": {"state": {"$in": [1, 0]} if state == "2" else int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else ("trade_id" if category == "trade" and content else "null"): {"$regex": content} if category != "account" and content else None, 
                        "channel": {"$in": ["支付宝", "微信"]} if channel == "default" else channel}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "state": 1, "channel": 1, "trade_id": 1}}
        ]
        cursor = manage.client["recharge_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"state": {"$in": [1, 0]} if state == "2" else int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else ("trade_id" if category == "trade" and content else "null"): {"$regex": content} if category != "account" and content else None, 
                        "channel": {"$in": ["支付宝", "微信"]} if channel == "default" else channel}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["recharge_records"].aggregate(pipeline)
        count = [doc for doc in cursor]
        data["count"] = count[0]["count"] if count else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_withdrawal_records_audit(delta_time=30):
    """
    提现审核列表
    :param delta_time: 允许查询的最大区间30天
    """
    data = {}
    try:
        # 参数
        num = request.args.get("num")
        page = request.args.get("page")
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account申请账号
        channel = request.args.get("channel") # 全部传default, 其余对应传，如支付宝
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        if category not in ["account", "order", "trade"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        if not channel:
            return response(msg="Bad Request: Miss params: 'channel'.", code=1, status=400)
        pipeline = [
            {"$match": {"state": 1, "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None, 
                        "channel" if channel != "default" else "null": channel if channel != "default" else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "trade_name": 1, "trade_id": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "channel": 1}}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"state": 1, "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None, 
                        "channel" if channel != "default" else "null": channel if channel != "default" else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$count": "count"}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        count = [doc for doc in cursor]
        data["count"] = count[0]["count"] if count else 0
        data["list"] = data_list if data_list else []
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def put_withdrawal_records_state():
    """
    提现审核接口
    """
    try:
        # 参数
        order_list = request.json.get("order_list") # array
        state = request.json.get("state") # 完成传2 驳回传0
        if not order_list:
            return response(msg="Bad Request: Miss param 'order_list'.", code=1, status=400)
        if state not in [0, 2]:
            return response(msg="Bad Request: Param 'state' is error.", code=1, status=400)
        doc = manage.client["withdrawal_records"].update({"order": {"$in": order_list}}, {"$set": {"state": state}}, multi=True)
        if doc["n"] == 0:
            return response(msg="'withdrawal_records' is update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_withdrawal_records_export(delta_time=30, domain=constant.DOMAIN):
    """
    提现记录导出
    :param delta_time: 允许查询的最大区间30天
    """
    try:
        # 参数
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account账号
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        state = request.args.get("state") # 1驳回，2已完成
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if category not in ["account", "order"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["1", "2"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        pipeline = [
            {"$match": {"state": int(state), "$and": [ {"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "state": {"$cond": {"if": {"$eq": ["$state", 0]}, "then": "驳回", "else": "完成"}}, "trade_name": 1, "trade_id": 1, "update_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$update_time"]}}}, "channel": 1}}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        temp = {
            "order": "提现单号", 
            "create_time": "申请时间",
            "amount": "提现金额",
            "account": "申请账号",
            "state": "订单状态",
            "update_time": "处理时间",
            "channel": "提现渠道",
            "trade_id": "支付号码",
            "trade_name": "支付姓名",
        }
        if not data_list:
            return response(msg="当前记录为空，无法导出")
        export = ExportExcle(temp, "提现记录")
        path = export.export_excle(data_list, "export", "order")
        return response(data=domain + path)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_order_recharge_export(delta_time=30, domain=constant.DOMAIN):
    """
    充值记录导出
    :param delta_time: 允许查询的最大区间30天
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account充值账号，trade交易号
        state = request.args.get("state") # 0未支付，1已支付完成, 2全部
        channel = request.args.get("channel") # 支付宝/微信 全部default
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if category not in ["account", "order", "trade"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if state not in ["2", "1", "0"]:
            return response(msg="Bad Request: Params 'state' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        if channel not in ["支付宝", "微信", "default"]:
            return response(msg="Bad Request: Params 'channel' is error.", code=1, status=400)
        pipeline = [
            {"$match": {"state": {"$in": [1, 0]} if state == "2" else int(state), "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else ("trade_id" if category == "trade" and content else "null"): {"$regex": content} if category != "account" and content else None, 
                        "channel": {"$in": ["支付宝", "微信"]} if channel == "default" else channel}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "state": {"$cond": {"if": {"$eq": ["$state", 0]}, "then": "未支付", "else": "已支付"}}, "channel": 1, "trade_id": 1}}
        ]
        cursor = manage.client["recharge_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        temp = {
            "order": "充值单号", 
            "create_time": "充值时间",
            "amount": "充值金额",
            "account": "充值账号",
            "state": "订单状态",
            "channel": "充值渠道",
            "trade_id": "支付交易号",
        }
        if not data_list:
            return response(msg="当前记录为空，无法导出")
        export = ExportExcle(temp, "充值记录")
        path = export.export_excle(data_list, "export", "order")
        return response(data=domain + path)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_withdrawal_records_audit_export(delta_time=30, domain=constant.DOMAIN):
    """
    提现审核列表
    :param delta_time: 允许查询的最大区间30天
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        content = request.args.get("content")
        category = request.args.get("category") # order订单号，account申请账号
        channel = request.args.get("channel") # 全部传default, 其余对应传，如支付宝
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        timeArray1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        timeArray2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
        start_time = int(time.mktime(timeArray1.timetuple()) * 1000)
        end_time = int(time.mktime(timeArray2.timetuple()) * 1000)
        if category not in ["account", "order", "trade"]:
            return response(msg="Bad Request: Params 'category' is error.", code=1, status=400)
        if not start_time:
            return response(msg="Bad Request: Miss params: 'start_time'.", code=1, status=400)
        if not end_time:
            return response(msg="Bad Request: Miss params: 'end_time'.", code=1, status=400)
        if (int(end_time) - int(start_time)) // (24 * 3600 * 1000) > delta_time:
            return response(msg=f"最多可连续查询{delta_time}天以内的记录", code=1)
        if not channel:
            return response(msg="Bad Request: Miss params: 'channel'.", code=1, status=400)
        pipeline = [
            {"$match": {"state": 1, "$and": [{"create_time": {"$gte": int(start_time)}}, {"create_time": {"$lte": int(end_time)}}], 
                        "order" if category == "order" and content else "null": {"$regex": content} if category == "order" and content else None, 
                        "channel" if channel != "default" else "null": channel if channel != "default" else None}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"user_account": "$user_info.account"}},
            {"$match": {"account" if category == "account" and content else "null": {"$regex": content} if category == "account" and content else None}},
            {"$unset": ["user_item", "user_info"]},
            {"$sort": SON([("create_time", -1)])},
            {"$project": {"_id": 0, "order": 1, "amount": 1, "account": 1, "trade_name": 1, "trade_id": 1, "create_time": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": {"$add":[manage.init_stamp, "$create_time"]}}}, 
                          "channel": 1}}
        ]
        cursor = manage.client["withdrawal_records"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        temp = {
            "order": "提现单号", 
            "create_time": "申请时间",
            "amount": "提现金额",
            "account": "申请账号",
            "update_time": "处理时间",
            "channel": "提现渠道",
            "trade_id": "支付号码",
            "trade_name": "支付姓名",
        }
        if not data_list:
            return response(msg="当前记录为空，无法导出")
        export = ExportExcle(temp, "申请提现记录")
        path = export.export_excle(data_list, "export", "order")
        return response(data=domain + path)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)