#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: util.py
@Time: 2020-07-01 14:37:16
@Author: money 
"""
import sys
import os
import re
import time
import base64
import datetime
import json
import random
import string
import hashlib
import logging
import logging.config
import pymongo
import flask
import xlwt
import whatimage # heic转jpg  pip install whatimage
# import pyheif # heic转jpg pip install pyheif
import traceback # heic转jpg
from manage import *
from PIL import Image, ImageFile
# 图片太大超过ImageFile设置的MAXBLOCK上限，需要截掉一部分
ImageFile.LOAD_TRUNCATED_IMAGES = True
# ImageFile.MAXBLOCK = 999999999999 # 需要将Image能处理的文件上限设置非常大

def response(data=None, msg="Request successful.", code=0, status=200):
    """
    统一响应格式
    :param data: 响应数据
    :param msg: 响应信息
    :param code: 状态码 1错误 0正常 默认0
    :param status: http状态码 默认200
    :return json格式的对象
    """
    return flask.make_response(flask.jsonify({"data": data, "msg": msg, "code": code}), status)


def genrate_file_number():
    """
    生成文件编号
    规则: 2位字母 + 6位数字
    """
    n = 0
    m = 0
    random_str = ""
    # 随机生成2位字符
    while n < 2:
        a_str = random.choice(string.ascii_lowercase)
        random_str += a_str
        n += 1
    # 随机生成6位数字
    while m < 6:
        n_int = random.randint(0, 9)
        random_str += str(n_int)
        m += 1
    return random_str


def generate_uid(num=16):
    """
    生成uid
    :param num: uid位数
    """
    uid = hashlib.md5(base64.b64encode(os.urandom(num))).hexdigest()
    return uid


def generate_timestamp(d=1, h=0):
    """
    生成时间戳
    :param d: 某天
    :param h: 某时
    """
    dtime = datetime.datetime.now()
    dtime_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(h)
    timeArray = datetime.datetime.strptime(dtime_str, "%Y-%m-%d %H:%M:%S")
    now_timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
    before_timestamp = int(time.mktime((timeArray - datetime.timedelta(days=d)).timetuple()) * 1000)
    return now_timestamp, before_timestamp


class Logger(object):
    """创建日志器"""

    def __new__(cls, logname: str = "log_debug", folder: str = "logs"):
        """
        创建日志
        :param logname: 日志名称
        :param folder: 存放日志目录
        :return 返回一个日志器
        """
        # 获取当前文件所在路径
        module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        logger_path = os.path.join(module_path, folder)

        # 创建目录
        if not os.path.exists(logger_path):
            os.makedirs(logger_path)

        # 拼接配置文件所在路径
        logger_file = os.path.join(module_path, "conf", "logger.json")

        # 获取配置信息
        with open(logger_file, "r", encoding="utf-8-sig") as file:
            logger_config = json.load(file)
            logger_config["handlers"]["file"]["filename"] = os.path.join(logger_path, logger_config["handlers"]["file"]["filename"])
            logging.config.dictConfig(logger_config)
        return logging.getLogger(logname)


class MongoDB(object):
    """创建Mongo连接"""

    def __init__(self, log: logging.Logger):
        """
        初始化
        :param log: 日志器
        """
        self.logger = log
        self.client = {}
        # 获取当前文件所在路径
        module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        mongo_file = os.path.join(module_path, "conf", "mongo.json")
        
        # 获取mongo配置文件内容
        with open(mongo_file, "r", encoding="utf-8-sig") as file:
            mongo_config = json.load(file)
            for name in mongo_config.keys():
                self.client[name] = pymongo.MongoClient(**mongo_config[name])

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        if type is not None:
            self.logger.error("line %s. %s" % (trace.tb_lineno, value))
        self.close()

    def close(self):
        """关闭mongo连接"""
        try:
            for name in self.client.keys():
                self.client[name].close()
        except Exception as err:
            self.logger.error(err)


class UploadSmallFile(object):
    """小文件上传"""

    def __init__(self, application, allow_max_size: int, log: logging.Logger):
        """
        :param application: 应用名
        :param allow_file_extension: 允许的拓展名
        :param allow_max_size: 文件最大上传量
        :param log: 日志器
        """
        self.log = log
        self.app = application
        # self.file_extension = allow_file_extension
        # 限制文件上传大小
        self.app.config["MAX_CONTENT_LENGTH"] = allow_max_size

    def upload_file(self, request_param_name: str, storage_folder: str, user: str):
        """
        :param request_param_name: 文件上传时对应的参数名
        :param storage_folder: 存储文件夹
        """
        code = {
            "succ": 1,  # 上传成功
            "fail": 0  # 上传失败
        }
        msg = {
            "empty_msg": "文件不能为空",
            "succ_msg": "文件上传成功",
            "fail_msg": "拓展名不符合要求"
        }
        data_list = []
        try:
            # 获取文件
            files = flask.request.files.getlist(f"{request_param_name}", None)
            if not files:
                context = {
                    "msg": msg["empty_msg"],
                    "code": code["fail"]
                }
                return context
            if not isinstance(files, list):
                files = [files]
            for file in files:
                # 文件拓展名
                file_extension = file.filename.rsplit(".")[-1].rsplit("\"")[0]
                # 文件名
                file_name = ".".join(re.split("\.", file.filename)[:-1])
                # 校验文件类型
                # if all([file, (file_extension not in self.file_extension) if file else None]):
                #     context = {
                #         "msg": msg["fail_msg"],
                #         "code": code["fail"]
                #     }
                #     return context

                # 创建父文件夹
                path_p = os.getcwd() + f"/statics/{storage_folder}"
                if not os.path.exists(path_p):
                    os.makedirs(path_p)
                # 创建子文件夹
                date = datetime.datetime.now()
                year_str = f"{date.year}"
                month_str = f"{date.month}"
                path_s = path_p + f"/{user}/{year_str}/{month_str}"
                if not os.path.exists(path_s):
                    os.makedirs(path_s)
                # 存储文件
                uid = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()
                file_path = os.path.join(path_s, uid + file_name + f".{file_extension}")
                # 将heic格式转成jpg
                if file_extension == "HEIC":
                    file_content = file.read()
                    b_content = pyheif.read_heif(file_content)
                    out = Image.frombytes(mode=b_content.mode, size=b_content.size, data=b_content.data)
                    file_path = file_path.replace(file_extension, "jpg")
                    out.save(file_path, "JPEG")
                    file_extension = "jpg"
                else:
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                size = os.path.getsize(file_path) // 1024
                temp_path = f"/{user}/{year_str}/{month_str}/" + uid + file_name + f".{file_extension}"
                obj = {}
                obj["file_path"] = temp_path
                obj["size"] = size
                obj["file_extension"] = file_extension
                data_list.append(obj)
            context = {
                "msg": msg["succ_msg"],
                "code": code["succ"],
                "data": data_list,
            }
            return context
        except Exception as e:
            self.log.error(e)
            return None


class UploadLargeFile(object):
    """大文件分片上传"""

    def __init__(self, user_id, file_name, file_size, chunk_index, chunk_size):
        """
        初始化
        :param user_id: 用户id
        :param file_name: 文件名
        :param file_size: 文件大小
        :param chunk_index: 文件块的序号
        :param chunk_size: 文件块的大小
        """
        self.user_id = user_id
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_index = chunk_index
        self.chunk_size = chunk_size
        self.context = {
            "path": None,
            "msg": "Successful.",
            "code": 0  # 0正常 1错误
        }
        # 校验参数
        if not self.file_name:
            context["msg"] = "Please pass in params 'file_name'."
            context["code"] = 1
            return context
        if not self.file_size:
            context["msg"] = "Please pass in params 'file_size'."
            context["code"] = 1
            return context
        if not self.chunk_index:
            context["msg"] = "Please pass in params 'chunk_index'."
            context["code"] = 1
            return context
        if not self.chunk_size:
            context["msg"] = "Please pass in params 'chunk_size'."
            context["code"] = 1
            return context

    def create_folder(self):
        """创建目录"""
        try:
            # 文件拓展名
            file_data = flask.request.files.get(f"{self.file_name}")
            file_ext = file_data.filename.rsplit(".")[-1].rsplit("\"")[0]
            # 生成目录
            now = datetime.datetime.now()
            ymd = f"{now.year}{now.month}{now.day}"
            file_path = os.getcwd() + f"/statics/userFile/{self.user_id}/{ymd}/{self.file_name}.{file_ext}"
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            # 生成8位uuid
            # uuid = base64.b64encode(os.urandom(8)).decode().lower()
            self.context["path"] = file_path
        except Exception as e:
            log.error(e)
            self.context["msg"] = str(e)
            self.context["code"] = 1
        finally:
            return self.context

    def upload_file(self, chunk_xor=0):
        """
        上传文件
        :param chunk_xor: 异或运算初始值
        """
        try:
            params = {"chunk_xor": chunk_xor}
			# 表单数据
            form_data = flask.request.form.to_dict()
            if form_data:
                params.update(form_data)
			# json数据
            if flask.request.is_json:
                params.update(flask.request.get_json())
			# 上传文件
            rest = self.create_folder()
            file_path = rest["path"]
            with open(file_path, "rb+") as f:
				# 文件指针偏移量
                offset = int(params["chunk_index"]) * int(params["chunk_size"])
                f.seek(offset, 0)
				# 读取每片文件
                chunk_blob = flask.request.files.get("chunk_blob").read()
				# 异或运算
                chunk_xor = int(params["chunk_xor"])
                if chunk_xor != 0:
                    chunk_array = bytearray(chunk_blob)
                    for i in range(len(chunk_array)):
                        chunk_array[i] ^= chunk_xor
                    f.write(chunk_array)
                else:
                    f.write(chunk_blob)
                f.flush()
            rest["path"] = file_path
        except Exception as e:
            log.error(e)
            rest["msg"] = str(e)
            rest["code"] = 1
        finally:
            return rest


class IdCardAuth(object):
    """身份证校验"""

    def __init__(self):
        self.t = []
        self.w = []
        for i in range(0,18):
            t1 = i + 1
            self.t.append(t1)
            w1 = (2 ** (t1-1)) % 11
            self.w.append(w1)
        #队列w要做一个反序
        self.w = self.w[::-1]  

    def for_check(self, n):
        """
        根据前17位的余数，计算第18位校验位的值
        """
        for i in range(0,12):
            if (n + i) % 11 == 1:
                t = i % 11
        if t == 10:
            t = 'X'
        return t
        
    def for_mod(self, id):
        """
        根据身份证的前17位，求和取余，返回余数
        :param id: 身份证号
        """
        sum = 0
        for i in range(0,17):
            sum += int(id[i]) * int(self.w[i])
        sum = sum % 11
        return sum

    def check_true(self, id: str):
        """
        校验
        :param id: 身份证号
        """
        int_range = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for i in id[:18]:
            if i not in int_range:
                return False
        if id[-1] == 'X':
            if self.for_check(self.for_mod(id[:-1])) == 'X':
                return True
            else:
                return False
        else:
            if self.for_check(self.for_mod(id[:-1])) == int(id[-1]):
                return True
            else:
                return False


class GenerateImage(object):
    """生成不同规格的图片"""

    @staticmethod
    def generate_image_origin(data, storage_folder):
        """原图转换"""
        # 原图路径、尺寸、格式
        constant_path = os.getcwd() + f"/statics/{storage_folder}"
        file_path = data["file_path"]
        extension = data["file_extension"].lower()
        temp_str = file_path.replace(f".{extension}", "")
        # 读取原图
        im = Image.open(constant_path + file_path)
        w, h = im.size # 原图大小
        p = w / h  # 宽高比
        
        # 大图
        w_b = 1080
        h_b = int(w_b / p)
        out = im.resize((w_b, h_b), Image.ANTIALIAS)
        file_path_b = temp_str + "_b." + extension
        out.save(constant_path + file_path_b)
        context = {
            "file_path_b": file_path_b, # 大图
            "file_path_o": file_path, # 原图
            "extension": extension # 原图格式
        }
        return context

    @staticmethod
    def generate_image_small(data, storage_folder):
        """缩略图、大图"""
        # 原图路径、尺寸、格式
        constant_path = os.getcwd() + f"/statics/{storage_folder}"
        file_path = data["file_path"]
        extension = data["file_extension"].lower()
        temp_str = file_path.replace(f".{extension}", "")
        # 读取原图
        im = Image.open(constant_path + file_path)
        w, h = im.size # 原图大小
        p = w / h  # 宽高比
        
        # 缩略图
        w_t = 200
        h_t = int(w_t / p)
        out = im.resize((w_t, h_t), Image.ANTIALIAS)
        file_path_t = temp_str + "_t." + extension
        out.save(constant_path + file_path_t)
        # 大图
        w_b = 1080
        h_b = int(w_b / p)
        out = im.resize((w_b, h_b), Image.ANTIALIAS)
        file_path_b = temp_str + "_b." + extension
        out.save(constant_path + file_path_b)
        context = {
            "file_path_t": file_path_t, # 缩略图
            "file_path_b": file_path_b, # 大图
            "file_path_o": file_path, # 原图
            "extension": extension # 原图格式
        }
        return context

    @staticmethod
    def generate_image_big(data, storage_folder):
        """生成S、M、缩略图、大图"""
        # 原图路径、尺寸、格式
        constant_path = os.getcwd() + f"/statics/{storage_folder}"
        file_path = data["file_path"]
        extension = data["file_extension"].lower()
        temp_str = "/".join(file_path.split("/")[:-1])
        # 读取原图
        im = Image.open(constant_path + file_path)
        w, h = im.size # 原图大小
        p = w / h  # 宽高比
        extension = "jpg"
        # S规格
        w_s = 800
        h_s = int(w_s / p)
        file_path_s = ""
        if w > w_s:
            out = im.resize((w_s, h_s), Image.ANTIALIAS)
            uid = base64.b64encode(os.urandom(32)).decode().lower().replace("/", "")
            file_path_s = temp_str + f"/{uid}." + extension
            out.save(constant_path + file_path_s)
        # M规格
        w_m = 1600
        h_m = int(w_m / p)
        file_path_m = ""
        file_path_l = ""
        if w > w_m:
            out = im.resize((w_m, h_m), Image.ANTIALIAS)
            uid = base64.b64encode(os.urandom(32)).decode().lower().replace("/", "")
            file_path_m = temp_str + f"/{uid}." + extension
            file_path_l = file_path
            out.save(constant_path + file_path_m)
        context = {
            "file_path_o": file_path, # 原图
            "file_path_s": file_path_s, # S图
            "file_path_m": file_path_m, # M图
            "file_path_l": file_path_l, # L图
            "s_spec": f"{w_s}x{h_s}", # S规格
            "m_spec": f"{w_m}x{h_m}", # M规格
            "l_spec": f"{w}x{h}", # L规格
            "o_spec": f"{w}x{h}", # 原图规格
        }
        return context


class ExportExcle(object):
    """导出excel"""

    def __init__(self, fieldname: dict, tabelname: str):
        """
        初始化
        :param key: 字段名
        :param tabelname: 表名
        """
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet(tabelname)
        self.c = 0
        self.fieldname = fieldname
        for i in self.fieldname:
            self.ws.write(0, self.c, self.fieldname[i])
            self.c += 1
    def export_excle(self, data: list, foldername: str, filename: str):
        """
        导出
        :param data: 数据
        :param foldername: 目录名
        :param filename: 文件名
        """
        n = 1
        for doc in data:
            for (i, field) in enumerate(self.fieldname):
                self.ws.write(n, i, doc.get(field))
            n += 1
        DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = DIRNAME + f"/statics/files/{foldername}/"
        if not os.path.exists(path):
            os.makedirs(path)
        self.wb.save(path + f"{filename}.xls")
        # 返回路径
        return f"/{foldername}/{filename}.xls"


if __name__ == "__main__":
    check = IdCardAuth()
    t = check.check_true("50022819941129655x")
    print(t)
    