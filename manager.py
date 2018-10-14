import logging
from flask import session
from info import create_app

# 传入标记，加载对用的配置环境信息
app = create_app("develop")


@app.route('/')
def HelloWorld():
    # 测试redis存储数据
    # redis_store.set("name", "laohuang")
    # print(redis_store.get("name"))
    #
    # session["age"]="20"
    # print(session.get("age"))
    logging.debug("调试信息1")
    logging.info("详细信息1")
    logging.warning("警告信息1")
    logging.error("错误信息1")

    return "Hello World ....."


if __name__ == '__main__':
    app.run()
