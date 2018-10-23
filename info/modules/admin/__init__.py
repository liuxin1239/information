from flask import Blueprint
from flask import redirect
from flask import request
from flask import session

admin_blue=Blueprint("admin",__name__,url_prefix="/admin")

from . import views
# 对后台登陆做拦截
@admin_blue.before_request
def visit_admin():
    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            print(request.url)
            print("==========")
            return redirect("/")