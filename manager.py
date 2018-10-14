import logging

from flask import Flask,session,current_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db,models

#传入标记,加载对应的配置环境信息
app = create_app("develop")

#创建manager对象,管理app
manager = Manager(app)

#关联db,app,使用Migrate
Migrate(app,db)

#给manager添加操作命令
manager.add_command("db",MigrateCommand)

if __name__ == '__main__':
    manager.run()