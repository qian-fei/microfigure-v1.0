import multiprocessing

# 项目根目录 必须以/结尾
chdir = '/usr/share/nginx/www/tuqu.cn/microfigure_v1.0/'
# 绑定IP和端口 采用nginx将请求转发到该端口
bind = '127.0.0.1:4040'
# 工作处理的进程数 cpu * 2 +1
workers = multiprocessing.cpu_count() * 2 + 1
# 等待服务的客户端数量
backlog = 2048
# 工作模式gevent实现高并发
worker_class = 'gevent'
# 每个进程开启的线程数
threads = 2
# 是否调试
debug = True
# 日志等级
loglevel = 'info'
# 超时杀掉进程并重启
timeout = 60
# 进程日志 被自动拼接上工作目录 chdir
pidfile = 'gunicorn/pid.log'
# 请求输出日志  需要将logger中disable_existing_logers设置为false，否则会屏蔽掉gunicorn的logger，从而导致access.log无法记录请求
accesslog = 'gunicorn/access.log'
# 日志的格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s'
# 错误输出日志
errorlog = 'gunicorn/error.log'

# 启动gunicorn命令：gunicorn -c gunicorn.py manage:app -D
# 注意：服务器502时，就是请求处理不过来，需要增加woker；服务器504时，就是请求超时，需要增加timeout
"""
    注意需要事先在虚拟环境下：
    pip install gevent  版本大于1.4
    pip install gunicorn
    在gunicorn.py的同级目录： mkdir log
"""
