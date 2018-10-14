from flask import session
from info import create_app

# 传入标记，加载对用的配置环境信息
app = create_app("product")


@app.route('/', methods=["POST"])
def HelloWorld():
    # 测试redis存储数据
    # redis_store.set("name", "laohuang")
    # print(redis_store.get("name"))
    #
    # session["age"]="20"
    # print(session.get("age"))
    return "Hello World ....."


if __name__ == '__main__':
    app.run()
