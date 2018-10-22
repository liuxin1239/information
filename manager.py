import logging

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


if __name__ == '__main__':
    manager.run()
