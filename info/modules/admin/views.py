import time
from datetime import datetime, timedelta

from flask import g, jsonify
from flask import render_template, request, redirect, current_app, session

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import admin_blue
# 功能描述: 增加&编辑分类
# 请求路径: /admin/add_category
# 请求方式: POST
# 请求参数: id,name
# 返回值:errno,errmsg
@admin_blue.route('/add_category', methods=['POST'])
def add_category():
    #1.获取参数
    c_id = request.json.get("id")
    c_name = request.json.get("name")

    #2.校验参数,为空校验
    if not c_name:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    #3.根据编号,判断是否增加,还是编辑
    if c_id: # 编辑

        #3.1 通过编号查询,分类对象
        try:
            category = Category.query.get(c_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="分类获取失败")

        #3.2判断分类对象是否存在
        if not category: return jsonify(errno=RET.NODATA,errmsg="分类不存在")

        #3.3设置新的分类名字
        category.name = c_name

    else:
        #3.4创建分类对象,设置属性
        category = Category()
        category.name = c_name

        #3.4添加到数据库
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR,errmsg="分类创建失败")

    #4.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")
# 功能描述: 展示所有分类
# 请求路径: /admin/news_category
# 请求方式: GET
# 请求参数: GET,无
# 返回值:GET,渲染news_type.html页面, data数据
@admin_blue.route('/news_category')
def news_category():
    #1.查询所有分类
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取分类失败")

    #2.携带分类数据渲染页面
    return render_template("admin/news_type.html",categories=categories)

# 功能描述: 新闻编辑详情
# 请求路径: /admin/news_edit_detail
# 请求方式: GET, POST
# 请求参数: GET, news_id, POST(news_id,title,digest,content,index_image,category_id)
# 返回值:GET,渲染news_edit_detail.html页面,data字典数据, POST(errno,errmsg)
@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """
       - 1.判断请求方式,如果GET,渲染页面
       - 1.1 获取参数,新闻编号
       - 1.2 校验参数
       - 1.3 根据新闻编号获取新闻对象,并判断是否存在
       - 1.4 携带新闻数据,渲染页面
       - 2.如果是POST请求,获取参数
       - 3.校验参数,为空校验
         4. 判断新闻对象是否存在
       - 5.上传图片
       - 6.判断图片是否上传成功
       - 7.设置属性到新闻对象
       - 8.返回响应

       :return:
       """
    # - 1.判断请求方式,如果GET,渲染页面
    if request.method == "GET":
        # - 1.1 获取参数,新闻编号
        news_id = request.args.get("news_id")

        # - 1.2 校验参数
        if not news_id: return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        # - 1.3 根据新闻编号获取新闻对象,并判断是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

        if not news: return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

        # 1.3.1 查询所有的分类信息
        try:
            categories = Category.query.all()
            categories.pop(0)  # 弹出最新
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取分类失败")

        # - 1.4 携带新闻数据,渲染页面
        return render_template("admin/news_edit_detail.html", news=news.to_dict(), categories=categories)

    # - 2.如果是POST请求,获取参数
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    # - 3.校验参数,为空校验
    if not all([news_id, title, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # - 4. 根据编号,查询新闻对象, 判断新闻对象是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    if not news: return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # - 5.上传图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")

    # - 6.判断图片是否上传成功
    if not image_name: return jsonify(errno=RET.DATAERR, errmsg="上传失败")

    # - 7.设置属性到新闻对象
    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id

    # - 8.返回响应
    return jsonify(errno=RET.OK, errmsg="编辑成功")

#功能描述: 新闻编辑列表
# 请求路径: /admin/news_edit
# 请求方式: GET
# 请求参数: GET, p, keywords
# 返回值:GET,渲染news_edit.html页面,data字典数据
@admin_blue.route('/news_edit')
def news_edit():
    """
       - 1.获取参数
       - 2.参数类型转换
       - 3.分页查询
       - 4.获取分页对象属性,总页数,当前页,当前页对象列表
       - 5.对象列表转成,字典列表
       - 6.拼接数据,渲染页面
       :return:
       """
    # - 1.获取参数
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords")

    # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # - 3.分页查询,所有新闻都能编辑
    try:

        # 判断是否填写了搜索关键字
        filters = []
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")

    # - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # - 5.对象列表转成,字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # - 6.拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template("admin/news_edit.html", data=data)
# 获取/设置新闻审核详情
# 请求路径: /admin/news_review_detail
# 请求方式: GET,POST
# 请求参数: GET, news_id, POST,news_id, action
# 返回值:GET,渲染news_review_detail.html页面,data字典数据
@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
    # 如果是GET请求
    if request.method == 'GET':
        # 获取参数(新闻编号)
        news_id = request.args.get("news_id")
        # 校验参数
        if not news_id:
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
        # 根据新闻编号获取新闻对象,并判断是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
        # 携带数据,渲染页面
        return render_template("admin/news_review_detail.html", news=news.to_dict())
    # 如果是POST请求
    if request.method == "POST":
        # 获取参数
        news_id = request.json.get("news_id")
        action = request.json.get("action")
        # 校验参数
        if not all([news_id, action]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
        # 操作类型校验
        if not action in ["accept","reject"]:
            return jsonify(errno=RET.DBERR, errmsg="操作类型有误")
        # 通过编号获取新闻对象
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
        # 判断新闻对象是否存在
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
        # 根据操作类型,改变新闻状态
        if action=="accept":
            news.status=0
        else:
            reason=request.json.get("reason","")
            news.reason=reason
            news.status=-1
        # 返回响应
        return jsonify(errno=RET.OK, errmsg="操作成功")

# 获取/设置新闻审核
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: GET, p,keywords
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/news_review')
def news_review():
    # 获取参数
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords")
    # 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 分页查询,为通过和待审核的
    try:
        # 判断是否填写了搜索关键字
        filters = [News.status != 0]
        if keywords:
            filters.append(News.title.contains(keywords))
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 对象列表转换成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())
    # 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }

    return render_template("admin/news_review.html", data=data)


# 用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
def user_list():
    # 获取参数
    page = request.args.get("p", "1")
    # 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 分页查询
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")
    # 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 将对象列表转换成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())
    # 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "user_list": user_list
    }
    return render_template("admin/user_list.html", data=data)


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

    # 查询月活人数,time.localtime()查询日历对象
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
        day_startime_date = datetime.strptime(day_startime_str, "%Y-%m-%d")
        # 获取此刻时间
        day_endtime_date = datetime.now()
        # 根据时间,查询用户
        day_count = User.query.filter(User.last_login >= day_startime_date, User.last_login <= day_endtime_date,
                                      User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 查询时间段内,活跃人数
    active_date = []  # 记录活跃日期
    active_count = []  # 记录活跃人数
    for i in range(0, 31):
        # 当天时间A
        begin_date = day_startime_date - timedelta(days=i)
        # 当天开始时间的后一天B
        end_date = day_startime_date - timedelta(days=i - 1)
        # 添加当天开始时间字符串到活跃日期中
        active_date.append(begin_date.strftime("%Y-%m-%d"))
        # 查询时间A到B这一天的注册人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                                  User.last_login <= end_date).count()
        # 添加当天注册人数到获取数量中
        active_count.append(everyday_active_count)
    # 为了方便查看进行反转
    active_date.reverse()
    active_count.reverse()
    # 携带数据,渲染页面
    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
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
