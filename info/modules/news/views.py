from flask import current_app, jsonify, render_template, abort
from flask import g
from flask import request
from flask import session

from info import db
from info.models import News, User, Comment
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blue


# 新闻评论后端
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数:news_id,comment,parent_id
# 返回值: errno,errmsg,评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登陆")
    # 获取参数
    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 校验参数是否为空
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 根据新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
    # 判断新闻是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content

    if parent_id:
        comment.parent_id = parent_id
    # 保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="评论失败")
    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())

 
# 收藏功能接口
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数:news_id,action, g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 判断用户是否存在
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")
    # 获取参数
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")
    # 校验参数是个否为空
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 判断操作类型
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")
    # 根据新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    # 根据操作类型,收藏或者取消收藏
    try:
        if action == "collect":
            # 判断是否收藏过该新闻
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")


# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户data字典数据
@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 根据传入的新闻编号,获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
    # 判断新闻是否存在
    if not news:
        abort(404)
    # 查询热门新闻数据
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(e)
    # 将新闻列表转成,字典列表
    click_news_list = []
    for click_news in news_list:
        click_news_list.append(click_news)

    # 查询当前用户是否收藏该新闻
    is_collected = False
    if g.user and news in g.user.collection_news:
        is_collected = True
    # 查询所有的评论
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    # 将评论对象列表转成,字典列表
    comments_list = []
    for comment in comments:
        comments_list.append(comment.to_dict())
        
    # # 获取用户的编号,从session
    # user_id = session.get("user_id")
    # # 判断用户是否存在
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # # 携带数据渲染页面
    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else "",
        "click_news_list": click_news_list,
        "is_collected": is_collected,
        "comments_list":comments_list
    }

    return render_template("news/detail.html", data=data)