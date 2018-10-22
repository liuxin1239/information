from flask import render_template, request,redirect,current_app,session
from info.models import User
from . import admin_blue


# 获取/登陆,管理员登陆
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg/ 成功字符串
@admin_blue.route('/login',methods=["GET","POST"])
def admin_login():
    # 判断请求方式是否为GET
    if request.method == "GET":
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
            return render_template("admin/login.html",errmsg="管理员登录失败")
        # 判断管理员对象是否存在
        if not admin:
            return render_template("admin/login.html",errmsg="管理员不存在")
        # 校验管理员密码是否正确
        if not admin.check_passowrd(password):
            return render_template("admin/login.html",errmsg="密码错误")
        # 记录管理员登录信息到session
        session["user_id"] =admin.id
        session["nick_name"]=admin.nick_name
        session["mobile"]=admin.mobile
        session["is_admin"]=True
        # 重定向到首页
        return redirect("http://www.baidu.com")