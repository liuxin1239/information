import time
from datetime import datetime

from flask import g, jsonify
from flask import render_template, request, redirect, current_app, session
from info.models import User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import admin_blue


# 用户统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route('/user_count')
def user_count():
    # 查询总人数,不包含管理员
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月活人数
    calender = time.localtime()
    try:
        # 获取本月的1号:零点钟
        month_startime_str = "%d-%d-01" % (calender.tm_year, calender.tm_mon)
        month_startime_data = datetime.strptime(month_startime_str, "%Y-%m-%d")
        # 获取此刻时间
        month_endtime_data = datetime.now()
        # 根据时间,查询用户
        month_count = User.query.filter(User.last_login >= month_startime_data, User.last_login <= month_endtime_data,
                                        User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日活人数
    try:
        # 获取本日的1号:零点钟
        day_startime_str = "%d-%d-%d" % (calender.tm_year, calender.tm_mon, calender.tm_mday)
        day_startime_data = datetime.strptime(day_startime_str, "%Y-%m-%d")
        # 获取此刻时间
        day_endtime_data = datetime.now()
        # 根据时间,查询用户
        day_count = User.query.filter(User.last_login >= day_startime_data, User.last_login <= day_endtime_data,
                                      User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 查询时间段内,活跃人数
    # 携带数据,渲染页面
    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count
    }
    return render_template("admin/user_count.html", data=data)


# 后台主页内容
# 请求路径: /admin/index
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    # if not session.get("is_admin"):
    #     return redirect("/")
    admin = g.user.to_dict() if g.user else ""
    return render_template("admin/index.html", admin=admin)


# 获取/登陆,管理员登陆
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg/ 成功字符串
@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    # 判断请求方式是否为GET
    if request.method == "GET":
        # 判断管理员有没有登陆过,如有重定向到首页
        if session.get("is_admin"):
            return redirect("/admin/index")
        return render_template("admin/login.html")
    # 判断请求方式是否为POST
    if request.method == "POST":
        # 获取参数
        username = request.form.get("username")
        password = request.form.get("password")
        # 根据用户查询管理员对象
        try:
            admin = User.query.filter(User.mobile == username, User.is_admin == True).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/login.html", errmsg="管理员登录失败")
        # 判断管理员对象是否存在
        if not admin:
            return render_template("admin/login.html", errmsg="管理员不存在")
        # 校验管理员密码是否正确
        if not admin.check_passowrd(password):
            return render_template("admin/login.html", errmsg="密码错误")
        # 记录管理员登录信息到session
        session["user_id"] = admin.id
        session["nick_name"] = admin.nick_name
        session["mobile"] = admin.mobile
        session["is_admin"] = True
        # 重定向到首页
        return redirect("admin/index")
