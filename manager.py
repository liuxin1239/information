import logging
import random
from datetime import datetime, timedelta

from flask import Flask, session, current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models

# 传入标记,加载对应的配置环境信息
from info.models import User

app = create_app("develop")

# 创建manager对象,管理app
manager = Manager(app)

# 关联db,app,使用Migrate
Migrate(app, db)

# 给manager添加操作命令
manager.add_command("db", MigrateCommand)


# 创建管理员方法
@manager.option('-p', '--password', dest='password')
@manager.option('-u', '--username', dest='username')
def create_superuser(username, password):
    # 创建管理员对象
    admin = User()
    # 设置属性
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True
    # 保存到数据库
    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "创建失败"
    return "创建成功"


# 添加测试用户
@manager.option('-t', '--test', dest='test')
def add_test_user(test):
    # 定义用户容器
    user_list = []

    # for循环创建1000个用户
    for i in range(0, 1000):
        # 创建用户对象,设置属性
        user = User()
        user.nick_name = "老王%d" % i
        user.mobile = "138%08d" % i
        user.password_hash = "pbkdf2:sha256:50000$c6pfEyE8$01d47af3ad401cdd4822091596c517a5fa781c346e0f85ef4348bd57fdf96176"

        # 设置用户近31天的登陆时间
        user.last_login = datetime.now() - timedelta(seconds=random.randint(0, 3600 * 24 * 31))

        # 添加到容器中
        user_list.append(user)

    # 添加到数据库
    try:
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return "添加失败"

    return "添加成功"


if __name__ == '__main__':
    manager.run()
