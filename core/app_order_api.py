#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: order.py
@Time: 2020-07-14 17:24:23
@Author: money 
"""
##################################【app订单模块】##################################
import os
import base64
import string
import time
import random
import datetime
import manage
from bson.son import SON
from flask import request, g, jsonify, Response
from utils.util import response
from constant import constant
from utils.alipay import AliPay
from utils.wechat import WechatPay


def post_add_car():
    """加入购物车"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        price = request.json.get("price")
        is_buy = request.json.get("is_buy") # true购买 false加入购物车
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        if not price:
            return response(msg="Bad Request: Miss params: 'price'.", code=1, status=400)
        if price < 0:
            return response(msg="Bad Request: Params 'price' is error.", code=1, status=400)
        if is_buy not in [True, False]:
            return response(msg="Bad Request: Params 'is_buy' is error.", code=1, status=400)
        # 查询
        doc = manager.client["works"].find_one({"uid": works_id, "state": 2})
        if not doc:
            return response(msg="Bad Request: Param 'works_id' if error.", code=1, status=400)
        pic_id = doc.get("pic_id")[0]
        title = doc.get("title")
        price_id = doc.get("price_id")
        # 图片路径
        doc = manage.client["pic_material"].find_one({"uid": pic_id})
        pic_url = doc.get("pic_url")
        thumb_url = doc.get("thumb_url")
        # 规格
        doc = manage.client["price"].find_one({"uid": price_id})
        spec = doc.get("format")
        currency = doc.get("currency")
        price_unit = doc.get("price_unit")
        uid = base64.b64encode(os.urandom(32)).decode()
        # 插入订单
        condition = {
            "uid": uid, "user_id": user_id, "works_id": works_id, "title": title, "pic_url": pic_url, "spec": spec, "currency": currency, "price_unit": price_unit, "thumb_url": thumb_url,
            "price": price, "state": 1 if is_buy else 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        if is_buy:
            # 订单号
            order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
            condition.update({"order": order, "order_time": int(time.time() * 1000)})
        manage.client["order"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_user_car_list(domain=constant.DOMAIN):
    """
    获取用户购物车列表
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 0}},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "spec": 1, "currency": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_car_generate_order(domain=constant.DOMAIN):
    """
    购物车合并订单
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid_list = request.json.get("uid_list") # array
        if not uid_list:
            return response(msg="Bad Request: Miss params: 'uid_list'.", code=1, status=400)
        # 订单号
        order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        doc = manage.client["order"].update({"uid": {"$in": uid_list}}, {"$set": {"order": order, "state": 1, "create_time": int(time.time() * 1000)}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 返回订单信息
        pipeline = [
            {"$match": {"user_id": user_id, "order": order}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"balance": "$user_info.balance"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "order": 1, "title": 1, "spec": 1, "currency": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "create_time": 1}},
            {"$group": {"_id": {"order": "$order", "update_time": "$update_time"}, "total_amount": {"$sum": "$price", "works_item": {"$push": "$$ROOT"}}}},
            {"$project": {"_id": 0, "order": "$_id.order", "create_time": "$_id.create_time", "works_item": 1, "total_amount": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_listp[0] if data_list else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_user_order_list():
    """用户订单列表"""
    data = {}
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        is_complete = request.json.get("is_complete") # true完成 false待付款
        if is_complete not in [True, False]:
            return response(msg="Bad Request: Params 'is_complete' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 2 if is_complete else 1}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"balance": "$user_info.balance"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "order": 1, "title": 1, "spec": 1, "currency": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "update_time": 1, "create_time": 1}},
            {"$group": {"_id": {"order": "$order", "update_time": "$update_time", "create_time": "$create_time"}, "total_amount": {"$sum": "$price", "works_item": {"$push": "$$ROOT"}}}},
            {"$project": {"_id": 0, "order": "$_id.order", "create_time": "$_id.create_time", "update_time": "$_id.update_time", "works_item": 1, "total_amount": 1, "balance": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        # data_list = []
        # total_amount = 0
        # order = 0
        # create_time = 0
        # update_time = 0
        # for doc in cursor:
        #     if total_amount == 0:
        #         order = doc["uid"]
        #         create_time = doc["create_time"]
        #         update_time = doc["update_time"]
        #     total_amount += doc["price"]
        #     data_list.append(doc)
        # data["order"] = order
        # data["total_amount"] = total_amount
        # data["data_list"] = data_list if data_list else []
        # data["create_time"] = create_time
        # data["update_time"] = update_time
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def put_user_order():
    """取消订单"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        order_id = request.json.get("order_id")
        if not order_id:
            return response(msg="Bad Request: Miss params: 'order_id'.", code=1, status=400)
        # 更新
        doc = manage.client["order"].update({"order": order_id, "user_id": user_id, "state": 1}, {"$set": {"state": 0, "update_time": 1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_order_payment():
    """订单支付"""
    request_param = ""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        order = request.json.get("order")
        pay_method = request.json.get("pay_method") # 余额 支付宝 微信
        total_amount = request.json.get("total_amount")
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        if pay_method not in ["微信", "支付宝", "余额"]:
            return response(msg="Bad Request: Params 'pay_method' is error.", code=1, status=400)
        if not total_amount:
            return response(msg="Bad Request: Miss params: 'total_amount'.", code=1, status=400)
        if total_amount < 0 or type(total_amount) != float:
            return response(msg="Bad Request: Parmas 'total_amount' is error.", code=1, status=400)
        # 余额支付
        if pay_method == "余额":
            doc = manage.client["user"].find_one({ "uid": user_id})
            balance = doc.get("balance")
            if balance < total_amount:
                # 支付
                doc = manage.client["user"].find_one({ "uid": user_id}, {"$inc": {"balance": -total_amount}})
                if doc["n"] == 0:
                    return response(msg="支付失败", code=1)
                # 支付完成
                doc = manage.client["order"].update({"order": order}, {"$set": {"state": 2}}, multi=True)
                if doc["n"] == 0:
                    raise Exception("'order' state update failed")
                # 卖家balance更新
                doc = manage.client["order"].find({"order": order})
                data_list = [doc for doc in cursor]
                works_id = data_list[0]["works_id"]
                doc = manage.client["works"].find_one({"uid": works_id})
                seller_id = doc["user_id"]
                doc = manage.client["user"].update({ "uid": user_id}, {"$inc": {"balance": total_amount}})
                if doc["n"] == 0:
                    raise Exception(f"seller '{seller_id}' balance update failed")
                return response()
        # 支付宝支付
        if pay_method == "支付宝":
            alipay = AliPay(order, total_amount)
            request_param = alipay.generate_request_param()
        # 微信支付
        if pay_method == "微信":
            wechatpay = WechatPay(order, total_amount * 100)
            prepay_id = wechatpay.wechat_payment_request()
            if not prepay_id:
                return response(msg="请求微信失败", code=1)
            request_param = wechatpay.generate_app_call_data(prepay_id)
        return response(data=request_param)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_alipay_callback_verify():
    """支付宝回调验证"""
    try:
        data = request.args
        out_trade_no, total_amount = AliPay.callback_verify_sign(data)
        if not out_trade_no:
            return Response("failure")
        cursor = manage.client["order"].find({"order": out_trade_no})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc.get("price")
        if not data_list:
            return Response("failure")
        if temp_amount != total_amount:
            return Response("failure")
        return Response("success")
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_wechat_callback_verify():
    """微信支付回调验证"""
    try:
        data = request.args
        out_trade_no, total_fee = WechatPay.verify_wechat_call_back(data)
        if not all([out_trade_no, total_fee]):
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        cursor = manage.client["order"].find({"order": out_trade_no})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc.get("price")
        if not data_list:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        if temp_amount != total_fee / 100:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        xml_data = wxpay.generate_xml_data({"return_code": "SUCCESS", "return_msg": "OK"})
        return Response(xml_data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_app_callback():
    """支付成功后app回调"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1)
        # 参数
        order = request.json.get("order")
        total_amount = request.json.get("total_amount")
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        if not total_amount:
            return response(msg="Bad Request: Miss params: 'total_amount'.", code=1, status=400)
        cursor = manage.client["order"].find({"order": order})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc["price"]
        if temp_amount != total_amount:
            return response(msg="Bad Request: Params 'total_amount' is error.", code=1, status=400)
        if not data_list:
            return response(msg="Bad Request: Params 'order' is error.", code=1, status=400)
        works_id = data_list[0]["works_id"]
        doc = manage.client["works"].find_one({"uid": works_id})
        seller_id = doc["user_id"]
        doc = manage.client["user"].update({"uid": seller_id}, {"$set": {"balance": total_amount}})
        if doc["n"] == 0:
            raise Exception("User balance update failed")
        # 统计
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].update({"user_id": user_id, "date": timestamp}, {"$inc": {"sale_num": 1, "amount": total_amount}})
        if doc["n"] == 0:
            manage.client["user_statistical"].insert({"user_id": user_id, "date": timestamp, "amount": total_amount, "sale_num": 1, "create_time": int(time.time() * 1000),
                                                      "update_time": int(time.time() * 1000)})
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)