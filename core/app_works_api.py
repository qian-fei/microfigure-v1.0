#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: works.py
@Time: 2020-06-30 16:27:15
@Author: money 
"""
##################################【app作品创建模块】##################################
import sys
import os
# 将根目录添加到sys路径中
BASE_DIR1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR1)
sys.path.append(BASE_DIR2)

import time
import random
import datetime
import manage
import base64
import jieba
import hashlib
from bson.son import SON
from flask import request, g
from constant import constant
from utils.util import response, UploadSmallFile, genrate_file_number, GenerateImage



def ssh_connect_mongo():
    """ssh远程连接ME数据库"""
    # Successfully installed bcrypt-3.1.7 cryptography-3.0 paramiko-2.7.1 pynacl-1.4.0 sshtunnel-0.1.5
    from sshtunnel import SSHTunnelForwarder # pip install sshtunnel
    import pymongo
    server = SSHTunnelForwarder(
        ssh_address_or_host="120.26.218.247", # 远程服务器IP
        ssh_username = "root", # 远程服务器用户名
        ssh_password = "www.gli.cn123!!@#" , # 远程服务器密码
        remote_bind_address = ("127.0.0.1", 27017) # 远程服务器mongo绑定的端口
    ) 
    server.start()
    client = pymongo.MongoClient("127.0.0.1",server.local_bind_port)
    client_me = client["Lean"]
    return client_me


def pic_upload_api(user_id):
    """
    图片上传调用接口
    :param user_id: 用户id
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_list = request.files.getlist("pic_list[]")
        if not pic_list:
            return response(msg="Bad Request: Miss param: 'pic_list'.", code=1, status=400)
        file = UploadSmallFile(manage.app, 100 * 1024 * 1024, manage.log)
        context = file.upload_file("pic_list[]", "files", user_id)
        if context["code"] == 0:
            return response(msg=context["msg"], code=1, status=400)
        data_list = context["data"]
        return data_list
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_material_upload_common(domain=constant.DOMAIN):
    """
    素材上传通用接口
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        user_id = g.user_data["user_id"]
        # if not user_id:
        #     return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_list = request.files.getlist("pic_list[]")
        if not pic_list:
            return response(msg="Bad Request: Miss param: 'pic_list'.", code=1, status=400)
        file = UploadSmallFile(manage.app, 100 * 1024 * 1024, manage.log)
        context = file.upload_file("pic_list[]", "files", user_id)
        if context["code"] == 0:
            return response(msg=context["msg"], code=1, status=400)
        data = context["data"]
        for i in data:
            file_path = i["file_path"]
            context = GenerateImage.generate_image_origin(i, "files")
            file_path = context["file_path_b"]
            i["file_path"] = domain + file_path
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_audio_upload_common(domain=constant.DOMAIN):
    """
    音频上传通用接口
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        audio_list = request.files.getlist("audio_list[]")
        if not audio_list:
            return response(msg="Bad Request: Miss param: 'audio_list'.", code=1, status=400)
        file = UploadSmallFile(manage.app, 100 * 1024 * 1024, manage.log)
        context = file.upload_file("audio_list[]", "files", user_id)
        if context["code"] == 0:
            return response(msg=context["msg"], code=1, status=400)
        data = context["data"]
        for i in data:
            file_path = i["file_path"]
            i["file_path"] = domain + file_path
            # TODO音频写入me中me_music表
            # from dateutil import parser 
            # date = parser.parse(datetime.datetime.utcnow().isoformat()) # mongo Date格式的时间
            # condition = {"music_path": file_path, "muisc_upload_user": user_id, "createAt": date, "updateAt": date}
            # client_me = ssh_connect_mongo()
            # client_me["me_music"].insert(condition)
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_material_upload(domain=constant.DOMAIN, discount=constant.DISCOUNT):
    """
    素材上传接口
    :param domain: 域名
    :param discount: 折扣
    """
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
            context = GenerateImage.generate_image_small(obj, "files")
            condition = {"uid": uid, "user_id": user_id, "pic_url": context["file_path_o"], "big_pic_url": context["file_path_b"], "thumb_url": context["file_path_t"], "size": obj["size"],
                         "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "format": context["extension"].upper(), "label": []
            }
            temp_list.append(condition)
        cursor = manage.client["pic_material"].insert(temp_list)
        id_list = [doc for doc in cursor]
        # 上传的素材也需要S、M、L、扩大授权规格
        pipeline = [
            {"$match": {"_id": {"$in": id_list}}},
            {"$project": {"_id": 0, "uid": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "big_pic_url": {"$concat": [domain, "$big_pic_url"]}, "format": 1, "pic_url": 1}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = []
        for doc in cursor:
            # 创作S、M、L、扩大授权图
            data = {
                "file_path": doc["pic_url"],
                "file_extension": doc["format"]
            }
            context = GenerateImage.generate_image_big(data, "files")
            uid = base64.b64encode(os.urandom(16)).decode()
            spec_list = ["S", "扩大授权", "M", "L"]
            condition = []
            for i in spec_list:
                temp = {"uid": uid, "user_id": user_id, "type": 0, "pic_id": doc["uid"], "format": i, "currency": "￥", "price_unit": "元", "size_unit": "px", "discount": discount, 
                        "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
                condition.append(temp)
            file_path_s = context["file_path_s"]
            file_path_m = context["file_path_m"]
            file_path_o = context["file_path_o"]
            # S规格
            temp_s = context["s_spec"].split("x")
            w = int(temp_s[0])
            h = int(temp_s[1])
            condition[0].update({"pic_url": file_path_s if file_path_s else file_path_o, "width": w, "height": h, "state": 1})
            
            # 扩大授权
            temp_o = context["o_spec"].split("x")
            w = int(temp_o[0])
            h = int(temp_o[1])
            condition[1].update({"pic_url": file_path_o, "width": w, "height": h, "state": 1})

            # 只有M规格存在才会有L
            if file_path_m:
                # M规格
                temp_m = context["m_spec"].split("x")
                w = int(temp_m[0])
                h = int(temp_m[1])
                condition[2].update({"pic_url": file_path_m, "width": w, "height": h, "state": 1})
                # L规格
                temp_m = context["o_spec"].split("x")
                w = int(temp_m[0])
                h = int(temp_m[1])
                condition[3].update({"pic_url": file_path_o, "width": w, "height": h, "state": 1})
            else:
                condition.pop()
                condition.pop()
            manage.client["price"].insert(condition)
            del doc["pic_url"]
            data_list.append(doc)
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_pic_material(domain=constant.DOMAIN):
    """
    获取图片素材库
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        page = request.args.get("page")
        num = request.args.get("num")
        if not num:
            return response(msg="Bad Request: Miss params: 'num'.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss params: 'page'.", code=1, status=400)
        if int(page) < 1 or int(num) < 1:
            return response(msg="Bad Request: Params 'page' or 'num' is erroe.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$sort": SON([("create_time", -1)])},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$project": {"_id": 0, "uid": 1, "pic_url": {"$concat": [domain, "$pic_url"]}, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "label": 1, "title": 1, "format": 1}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_user_history_label(label_max=20):
    """
    用户历史标签
    :param label_max: 标签个数上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$project": {"_id": 0, "state": 0, "user_id": 0, "update_time": 0}},
            {"$sort": SON([("create_time", -1)])},
            {"$limit": label_max}
        ]
        cursor = manage.client["history_label"].aggregate(pipeline)
        data_list = []
        for i in cursor:
            data_list.append(i.get("label"))
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_altas_search_label():
    """图集搜索标签接口"""
    keyword_list = []
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        keyword = request.args.get("keyword")
        # 校验
        if not keyword:
            return response(msg="请输入关键词", code=1)

        # 模糊查询
        cursor = manage.client["label"].find({"label": {"$regex": keyword}, "type": "pic"}, {"_id": 0, "label": 1})
        for doc in cursor:
            keyword_list.append(doc["label"])
        if keyword in keyword_list:
            keyword_list = list(set(keyword_list))
            keyword_list.remove(keyword)
            keyword_list.insert(0, keyword)
        return response(data=keyword_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_pic_works(label_max=9, title_max=32):
    """
    创作图片
    :param length_max: 最多允许标签的上限
    :param title_max: 标题字符上限
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pic_list = request.json.get("pic_list")
        if not pic_list:
            return response(msg="Bad Request: Miss param 'pic_list'.", code=1, status=400)
        for i in pic_list:
            title = i["title"]
            label = i["label"]
            uid = i["uid"]
            format = i["format"]
            if not title:
                return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
            if len(title) > title_max:
                return response(msg=f"标题上限{title_max}个字符", code=1)
            if not label:
                return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
            if not uid:
                return response(msg="Bad Request: Miss param 'uid'.", code=1, status=400)
            if not format:
                return response(msg="Bad Request: Miss param 'format'.", code=1, status=400)
            if len(label) > label_max:
                return response(msg=f"最多允许选择{label_max}", code=1)
            # 分词
            keyword = list(jieba.cut(title))
            print(user_id,  uid)
            # 更新素材库
            doc = manage.client["pic_material"].update({"uid": uid, "user_id": user_id}, {"$set": {"title": title, "label": label, "keyword": keyword}})
            if doc["n"] == 0:
                return response(msg="Update failed", code=1, status=400)
        # 只有一张时制作图片
        if len(pic_list) == 1:
            # 制作图片作品
            title = pic_list[0]["title"]
            label = pic_list[0]["label"]
            uid = pic_list[0]["uid"] # 图片id
            format = pic_list[0]["format"]
            title = pic_list[0]["title"]
            wroks_uid = base64.b64encode(os.urandom(32)).decode()
            number = genrate_file_number()
            keyword = list(jieba.cut(title))
            # 判断该图是否已经制作过趣图作品
            doc = manage.client["works"].find_one({"pic_id": uid, "state": {"$ne": -1}, "type": "tp"})
            if doc:
                return response(msg="不能采用同一张图片制作趣图", code=1)
            temp_doc = manage.client["price"].find_one({"pic_id": uid})
            price_id = temp_doc["uid"]
            condition = {"uid": wroks_uid, "user_id": user_id, "pic_id": [uid], "type": "tp", "number": number, "format": format.upper(), "title": title, "keyword": keyword, 
                        "label": label, "state": 0, "is_recommend": False, "is_portrait": False, "is_products": False, "pic_num": 1, "like_num": 0, "comment_num": 0, "tag": "商",
                        "share_num": 0, "browse_num": 0, "sale_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "price_id": price_id,
            }
            manage.client["works"].insert(condition)
            # 更新素材表中的状态
            doc = manage.client["pic_material"].update({"user_id": user_id, "uid": uid}, {"$set": {"works_id": wroks_uid, "works_state": 0}})
            if doc["n"] == 0:
                return response(msg="'pic_material' Update failed.", code=1, status=400)
            # 更新作品数
            doc = manage.client["user"].update({"uid": user_id}, {"$inc": {"works_num": 1}})
            if doc["n"] == 0:
                return response(msg="'user' Update failed.", code=1, status=400)
            # 统计
            # 当前day天
            dtime = datetime.datetime.now()
            time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
            timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
            doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
            if doc:
                doc = manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
                if doc["n"] == 0:
                    return response(msg="Update failed.", code=1, status=400)
            else:
                condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "sale_num": 0, "browse_num": 0, "amount": float(0), "like_num": 0, "goods_num": 0, "register_num": 0,
                             "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
                manage.client["user_statistical"].insert(condition)
            # 历史标签表和标签表
            for i in label:
                # 记录历史标签
                condition = {"user_id": user_id, "label": i, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
                doc = manage.client["history_label"].find_one({"user_id": user_id, "label": i})
                if not doc:
                    manage.client["history_label"].insert(condition)
                # 更新标签works_num
                doc = manage.client["label"].update({"label": i}, {"$inc": {"works_num": 1}})
                if doc["n"] == 0:
                    id = base64.b64encode(os.urandom(16)).decode()
                    manage.client["label"].insert({"uid": id, "priority": float(0), "type": "pic", "label": i, "works_num": 1, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
                data = {
                    "pic_id": uid,
                    "works_id": wroks_uid
                }
            return response(data=data)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_pic_collect_works(label_max=9, title_max=32,pic_id_max=20, domain=constant.DOMAIN):
    """
    图集创作
    :param title_max: 标题字符上限
    :param pic_id_max: 允许选择图片的上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        cover_url = request.json.get("cover_url")
        title = request.json.get("title")
        label = request.json.get("label")
        pic_id_list = request.json.get("pic_id_list") # array
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_max:
            return response(msg=f"标题上限{title_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_max:
            return response(msg=f"最多允许选择{label_max}", code=1)
        if not pic_id_list:
            return response(msg="Bad Request: Miss param 'pic_id_list'.", code=1, status=400)
        if len(pic_id_list) <= 1:
            return response(msg="图集至少2张图片", code=1)
        if len(pic_id_list) > pic_id_max:
            return response(msg=f"最多允许选择{pic_id_max}张图片", code=1)
        # 制作图片作品
        cover_url = cover_url.replace(domain, "")
        uid = base64.b64encode(os.urandom(32)).decode()
        number = genrate_file_number()
        keyword = list(jieba.cut(title))
        condition = {"uid": uid, "user_id": user_id, "pic_id": pic_id_list, "type": "tj", "number": number, "title": title, "keyword": keyword, "cover_url": cover_url, 
                     "label": label, "state": 0, "is_recommend": False, "is_portrait": False, "is_products": False, "pic_num": len(pic_id_list), "like_num": 0, "comment_num": 0, 
                     "share_num": 0, "browse_num": 0, "sale_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        manage.client["works"].insert(condition)
        # 更新作品数
        doc = manage.client["user"].update({"uid": user_id}, {"$inc": {"works_num": 1}})
        if doc["n"] == 0:
            return response(msg="'user' Update failed.", code=1, status=400)
        # 统计
        # 当前day天
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
        if doc:
            doc = manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
        else:
            condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "sale_num": 0, "browse_num": 0, "amount": float(0), "like_num": 0, "goods_num": 0, "register_num": 0,
                         "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        # 历史标签表和标签表
        for i in label:
            # 记录历史标签
            condition = {"user_id": user_id, "label": i, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            doc = manage.client["history_label"].find_one({"user_id": user_id, "label": i})
            if not doc:
                 manage.client["history_label"].insert(condition)
            # 更新标签表中works_num
            doc = manage.client["label"].update({"label": i}, {"$inc": {"works_num": 1}})
            if doc["n"] == 0:
                id = base64.b64encode(os.urandom(16)).decode()
                manage.client["label"].insert({"uid": id, "priority": float(0), "type": "pic", "label": i, "works_num": 1, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        data = {
            "pic_id": pic_id_list[0],
            "works_id": uid
        }
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_create_article_works(domain=constant.DOMAIN):
    """
    创作图文、编辑图文
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid = request.json.get("uid")
        title = request.json.get("title")
        desc = request.json.get("desc")
        content = request.json.get("content")
        cover_url = request.json.get("cover_url")
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if not content:
            return response(msg="Bad Request: Miss param 'content'.", code=1, status=400)
        if not cover_url:
            return response(msg="Bad Request: Miss param 'cover_url'.", code=1, status=400)

        if not uid:
            # 入库
            uid = base64.b64encode(os.urandom(32)).decode()
            cover_url = cover_url.replace(domain, "")
            condition = {"uid": uid, "user_id": user_id, "cover_url": cover_url, "content": content, "title": title, "state": 0, "type": "tw", "is_recommend": False, "like_num": 0, 
                        "comment_num": 0, "share_num": 0, "browse_num": 0, "create_time": int(time.time() * 1000), "updated_time": int(time.time() * 1000), "pic_id": [], "desc": desc
            }
            manage.client["works"].insert(condition)
            # 统计
            # 当前day天
            dtime = datetime.datetime.now()
            time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
            timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
            doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
            if doc:
                doc = manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
                if doc["n"] == 0:
                    return response(msg="Update failed.", code=1, status=400)
            else:
                condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "sale_num": 0, "browse_num": 0, "amount": float(0), "like_num": 0, "goods_num": 0, "register_num": 0,
                             "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
                manage.client["user_statistical"].insert(condition)
            return response(data=uid)
        else:
            manage.client["works"].update({"uid": uid}, {"$set": {"cover_url": cover_url, "content": content, "title": title}})
            return response(data=uid)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_video_material_upload(domain=constant.DOMAIN):
    """
    影集图片上传接口
    :param domain: 域名
    """
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
            context = GenerateImage.generate_image_small(obj, "files")
            condition = {"uid": uid, "user_id": user_id, "pic_url": context["file_path_o"], "big_pic_url": context["file_path_b"], "thumb_url": context["file_path_t"], "size": obj["size"],
                         "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000), "format": context["extension"].upper(), "label": []
            }
            temp_list.append(condition)
        manage.client["pic_material"].insert(temp_list)
        id_list = [doc for doc in cursor]
        pipeline = [
            {"$match": {"_id": {"$in": id_list}}},
            {"$project": {"_id": 0, "uid": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "big_pic_url": {"$concat": [domain, "$big_pic_url"]}, "format": 1, "pic_url": 1}}
        ]
        cursor = manage.client["pic_material"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_video_search_label():
    """影集搜索标签接口"""
    keyword_list = []
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        keyword = request.args.get("keyword")
        # 校验
        if not keyword:
            return response(msg="请输入关键词", code=1)

        # 模糊查询
        cursor = manage.client["label"].find({"label": {"$regex": keyword}, "type": "video"}, {"_id": 0, "label": 1})
        for doc in cursor:
            keyword_list.append(doc["label"])
        if keyword in keyword_list:
            keyword_list = list(set(keyword_list))
            keyword_list.remove(keyword)
            keyword_list.insert(0, keyword)
        return response(data=keyword_list)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_video_collect_works(label_max=9, title_max=32,pic_id_max=20, domain=constant.DOMAIN):
    """
    影集创作
    :param title_max: 标题字符上限
    :param pic_id_max: 允许选择图片的上限
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        cover_url = request.json.get("cover_url")
        title = request.json.get("title")
        label = request.json.get("label")
        pic_id_list = request.json.get("pic_id_list") # array
        me_works_id = request.json.get("me_works_id")
        if not title:
            return response(msg="Bad Request: Miss param 'title'.", code=1, status=400)
        if len(title) > title_max:
            return response(msg=f"标题上限{title_max}个字符", code=1)
        if not label:
            return response(msg="Bad Request: Miss param 'label'.", code=1, status=400)
        if len(label) > label_max:
            return response(msg=f"最多允许选择{label_max}", code=1)
        if not pic_id_list:
            return response(msg="Bad Request: Miss param 'pic_id_list'.", code=1, status=400)
        if len(pic_id_list) <= 1:
            return response(msg="影集至少2张图片", code=1)
        if len(pic_id_list) > pic_id_max:
            return response(msg=f"最多允许选择{pic_id_max}张图片", code=1)
        if not me_works_id:
            return response(msg="Bad Request: Miss params: 'me_works_id'.", code=1, status=400)
        # 制作影集作品
        cover_url = cover_url.replace(domain, "")
        number = genrate_file_number()
        keyword = list(jieba.cut(title))
        condition = {"uid": me_works_id, "user_id": user_id, "pic_id": pic_id_list, "type": "yj", "number": number, "title": title, "keyword": keyword, "cover_url": cover_url, 
                     "label": label, "state": 0, "is_recommend": False, "is_portrait": False, "is_products": False, "pic_num": len(pic_id_list), "like_num": 0, "comment_num": 0, 
                     "share_num": 0, "browse_num": 0, "sale_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        manage.client["works"].insert(condition)
        # 更新作品数
        doc = manage.client["user"].update({"uid": user_id}, {"$inc": {"works_num": 1}})
        if doc["n"] == 0:
            return response(msg="'user' Update failed.", code=1, status=400)
        # 统计
        # 当前day天
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        today_stamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].find_one({"user_id": user_id, "date": today_stamp})
        if doc:
            doc = manage.client["user_statistical"].update({"user_id": user_id, "date": today_stamp}, {"$inc": {"works_num": 1}, "$set": {"update_time": int(time.time() * 1000)}})
            if doc["n"] == 0:
                return response(msg="Update failed.", code=1, status=400)
        else:
            condition = {"user_id": user_id, "date": today_stamp, "works_num": 1, "sale_num": 0, "browse_num": 0, "amount": float(0), "like_num": 0, "goods_num": 0, "register_num": 0,
                         "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        # 历史标签表和标签表
        for i in label:
            # 记录历史标签
            condition = {"user_id": user_id, "label": i, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            doc = manage.client["history_label"].find_one({"user_id": user_id, "label": i})
            if not doc:
                manage.client["history_label"].insert(condition)
            # 更新标签表中works_num
            doc = manage.client["label"].update({"label": i}, {"$inc": {"works_num": 1}})
            if doc["n"] == 0:
                id = base64.b64encode(os.urandom(16)).decode()
                manage.client["label"].insert({"uid": id, "priority": float(0), "type": "video", "label": i, "works_num": 1, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)})
        data = {
            "pic_id": pic_id_list[0],
            "works_id": me_works_id
        }
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_user_add_label():
    """用户添加标签"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        label = request.json.get("label") # array
        if not label:
            return response(msg="Bad Request: Miss params: 'label'.", code=1, status=400)
        # 记录标签
        for i in label:
            condition = {"user_id": user_id, "label": i, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            doc = manage.client["history_label"].find_one({"user_id": user_id, "label": i})
            if not doc:
                manage.client["history_label"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)