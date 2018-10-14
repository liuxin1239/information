from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import config_dict
import redis


def create_app(config_name):
    app = Flask(__name__)

    # 根据传入的配置名称，获取对应的配置类
    config = config_dict.get(config_name)
    # 加载配置类信息
    app.config.from_object(config)

    # 创建SQLAlchemy对象,关联appd
    db = SQLAlchemy(app)

    # 创建redis对象,关联app
    redis_store = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 初始化Session,读取app身上session配置信息哦
    Session(app)

    # 对app做保护
    CSRFProtect(app)

    return app
