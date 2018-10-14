from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import redis

app = Flask(__name__)


# 配置信息
class Config(object):
    # 调试模式
    DEBUG = True
    SECRET_KEY = "sadasdasfad"
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2


app.config.from_object(Config)

# 创建SQLAlchemy对象,关联appd
db = SQLAlchemy(app)

# 创建redis对象,关联app
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# 初始化Session,读取app身上session配置信息哦
Session(app)


@app.route('/')
def HelloWorld():
    # 测试redis存储数据
    redis_store.set("name", "laohuang")
    print(redis_store.get("name"))

    session["age"]="20"
    print(session.get("age"))
    return "Hello World ....."


if __name__ == '__main__':
    app.run()
