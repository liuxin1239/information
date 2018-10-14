import logging
from flask import session
from info import create_app

# 传入标记，加载对用的配置环境信息
app = create_app("develop")



if __name__ == '__main__':
    app.run()
