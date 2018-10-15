import random
import re
from flask import current_app
from flask import make_response
from flask import request, jsonify

from info import constants, db
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha


# 注册用户
# 请求路径: /passport/register
# 请求方式: POST
# 请求参数: mobile, sms_code,password
# 返回值: errno, errmsg
@passport_blue.route('/register', methods=['POST'])
def register():
    # 获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")
    # 校验参数是否为空
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 手机号格式校验
    if not re.match("1[35789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")
    # 根据手机号,去redis中去除短信验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码异常")
    # 判断短信验证码时候否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")
    # 删除redis的短信验证码
    try:
        redis_store.delete("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="删除短信验证码异常")

    # 判断传入的短信验证码和redis中取出的是否一致

    if redis_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码填写有误")

    # 创建用户对象,设置属性
    user = User()
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile

    # 保存用户到数据库mysql
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="注册失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 获取短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_blue.route('/sms_code', methods=["POST"])
def sms_code():
    # 获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # 校验参数是否为空
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验手机号格式是否正确
    if not re.match("1[35789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")
    # 通过验证码编号取出,redis中的图片验证码A
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码异常")
    # 判断验证码A是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")
    try:
        # 未过期,就删除redis中的图片验证码
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码操作异常")
    # 判断验证码A和传入进来的验证码B是否相等
    if image_code.lower() != redis_image_code.lower():
        return jsonify(errno=RET.DATAERR, errnsg="图片验证码填写错误")
    # 生成验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 发送短信验证码,调用ccp
    ccp = CCP()
    try:
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="云通讯发送异常")

    if result == -1:
        return jsonify(errno=RET.DATAERR, errmsg="短信发送失败")

    # 储存短信验证码到redis中
    try:
        redis_store.set("sms_code:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存验证码失败")
    # 返回发送状态
    return jsonify(errno=RET.OK, errmsg="发送成功")


# 获取返回一张图片
# 请求路径: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id, pre_id
# 返回值: 图片验证码
@passport_blue.route('/image_code')
def image_code():
    # 获取参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 校验参数
    if not cur_id:
        return jsonify(errno=RET.PARAMERR, errmsg="图片验证码编号未存在")

    # 生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    try:
        # 保存图片验证码到redis
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        # 判断是否有上个图片验证码编号，有则删除
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码异常")
    # 返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
