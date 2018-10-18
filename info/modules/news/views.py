from flask import current_app, jsonify, render_template, abort
from flask import session

from info.models import News, User
from info.utils.response_code import RET
from . import news_blue


# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户data字典数据
@news_blue.route('/<int:news_id>')
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



    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(e)

    click_news_list=[]
    for click_news in news_list:
        click_news_list.append(click_news)

    # 获取用户的编号,从session
    user_id = session.get("user_id")
    # 判断用户是否存在
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # # 携带数据渲染页面
    data = {
        "news": news.to_dict(),
        "user_info": user.to_dict() if user else "",
        "click_news_list":click_news_list

    }



    return render_template("news/detail.html",data=data)
