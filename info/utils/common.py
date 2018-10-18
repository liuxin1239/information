# 自定义过滤器
from curses import wrapper, wrapper
from functools import wraps

from flask import current_app
from flask import g
from flask import session




def index_class(index):
    if index == 1:
        return "first"
    elif index ==2:
        return "second"
    elif index ==3:
        return "third"
    else:
        return ""

# 试用装饰器,封装用户登录
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # 获取用户的编号,从session
        user_id = session.get("user_id")
        # 判断用户是否存在
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 将用户对象封装到,g对象
        g.user = user
        return view_func(*args,**kwargs)
    return wrapper