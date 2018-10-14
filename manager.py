from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)


# 配置信息
class Config(object):
    # 调试模式
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

app.config.from_object(Config)

# 创建SQLAlchemy对象,关联app
db = SQLAlchemy(app)

# 创建redis对象,关联app
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

@app.route('/')
def HelloWorld():
    # 测试redis存储数据
    redis_store.set("name","laohuang")
    print(redis_store.get("name"))

    return "Hello World ....."


if __name__ == '__main__':
    app.run()
