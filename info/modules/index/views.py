from info.utils.captcha.captcha import captcha
from . import index_blue
from info import redis_store
from flask import render_template,current_app

# 获取返回一张图片
@index_blue.route('/image_code')
def image_code():
    name,text,image_data =captcha.generate_captcha()
    return image_data


@index_blue.route('/')
def HelloWorld():
    # 测试redis存储数据
    # redis_store.set("name", "laohuang")
    # print(redis_store.get("name"))
    #
    # session["age"] = "20"
    # print(session.get("age"))

    # logging.debug("调试信息1")
    # logging.info("详细信息1")
    # logging.warning("警告信息1")
    # logging.error("错误信息1")

    return render_template("news/index.html")

# 页面logo /favicon.ico
@index_blue.route('/favicon.ico')
def web_log():
    return current_app.send_static_file("news/favicon.ico")