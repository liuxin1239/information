from flask import session

from info.models import User
from . import index_blue
from info import redis_store
from flask import render_template,current_app


@index_blue.route('/')
def HelloWorld():
    # 获取用户的编号,从session
    user_id =session.get("user_id")
    # 判断用户是否存在
    user=None
    if user_id:
        try:
            user=User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 将用户信息转成字典
    dict_data={
        # 如果user存在,返回左边,否则返回右边
        "user_info":user.to_dict() if user else ""
    }
    return render_template("news/index.html",data=dict_data)

# 页面logo /favicon.ico
@index_blue.route('/favicon.ico')
def web_log():
    return current_app.send_static_file("news/favicon.ico")