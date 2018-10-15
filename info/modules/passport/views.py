from flask import request, jsonify

from info import constants
from info import redis_store
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha

# 获取返回一张图片
# 请求路径: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id, pre_id
# 返回值: 图片验证码
@passport_blue.route('/image_code')
def image_code():
    # 获取参数
    cur_id=request.args.get("cur_id")
    pre_id=request.args.get("pre_id")
    # 校验参数
    if not cur_id:
        return jsonify(errno=RET.PARAMERR, errmsg="图片验证码编号未存在")

    # 生成图片验证码
    name,text,image_data =captcha.generate_captcha()
    # 保存图片验证码到redis
    redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    # 判断是否有上个图片验证码编号，有则删除
    if pre_id:
        redis_store.delete("image_code:%s"%pre_id)
    return image_data

