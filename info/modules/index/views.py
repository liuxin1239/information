from . import index_blue
from info import redis_store
from flask import render_template
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

