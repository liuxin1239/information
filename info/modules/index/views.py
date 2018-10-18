from flask import g
from flask import session, jsonify
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blue
from flask import render_template, current_app, request


# 首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blue.route('/newslist')
def new_list():
    # 获取参数
    cid = request.args.get("cid")
    page = request.args.get("page")
    per_page = request.args.get("per_page")
    # 参数类型转换
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10
    # 分页查询
    try:
        filters =[]
        if cid != "1":
            filters.append(News.category_id==cid)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="分页获取失败")
    # 获取分页对象属性,总页数,当前页,当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 将当前页列表转化为对象
    newsList = []
    for item in items:
        newsList.append(item.to_dict())

    # 响应
    return jsonify(errno=RET.OK, errmsg="获取成功",totalPage=totalPage,currentPage=currentPage,newsList=newsList)


# 首页右上角用户展示
# 请求路径: /
# 请求方式: GET
# 请求参数: 无
# 返回值: index.html页面, data数据
@index_blue.route('/')
@user_login_data
def show_index():
    # # 获取用户的编号,从session
    # user_id = session.get("user_id")
    # # 判断用户是否存在
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻异常")

    # 将新闻对象转成字典
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())

    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="分类获取失败")
    # 将分类对象转成字典
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 将用户信息转成字典
    dict_data = {
        # 如果user存在,返回左边,否则返回右边
        "user_info": g.user.to_dict() if g.user else "",
        "click_news_list": click_news_list,
        "category_list": category_list
    }

    return render_template("news/index.html", data=dict_data)


# 页面logo /favicon.ico
@index_blue.route('/favicon.ico')
def web_log():
    return current_app.send_static_file("news/favicon.ico")
