from flask import current_app, jsonify, render_template, abort
from info.models import News
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
    # 携带数据渲染页面
    data = {
        "news": news.to_dict()
    }

    return render_template("news/detail.html",data=data)
