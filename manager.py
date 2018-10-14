from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# 配置信息
class Config(object):
    # 调试模式
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)
# 创建SQLAlchemy对象关联app
db = SQLAlchemy(app)


@app.route('/')
def HelloWorld():
    return "Hello World ....."


if __name__ == '__main__':
    app.run()
