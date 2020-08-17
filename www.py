# HTTP 模块相关初始化
"""
static interceptor
"""
from web.interceptors.AuthInterceptor import *

from application import app
from web.controllers.index import route_index
from web.controllers.compute.MockTransaction import route_mockTransaction
from web.controllers.static import route_static
from web.controllers.user.User import route_user

app.register_blueprint(route_mockTransaction, url_prefix='/mock')
app.register_blueprint(route_index,url_prefix='/')
app.register_blueprint(route_static,url_prefix='/static')
app.register_blueprint(route_user, url_prefix='/user')