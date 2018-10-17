import logging
import redis


# 配置信息
class Config(object):
    # 调试模式
    DEBUG = True
    SECRET_KEY = "sadasdasfad"
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2

    # 默认设置日志等级logging.DEBUG
    LEVEL = logging.DEBUG


# 开发模式的配置信息
class DevelopConfig(Config):
    pass


# 生产模式（线上模式）
class ProductConfig(Config):
    DEBUG = True
    LEVEL = logging.ERROR


# 测试模式
class TestingConfig(Config):
    TESTING = True


# 给外界提供各种配置访问入口
config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestingConfig
}
