# 封装Flask的全局变量，包括app，数据库等
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_redis import FlaskRedis
import os

class Application(Flask):
    def __init__(self, import_name, template_folder=None, root_path=None):
        # Application init didn't pass in root_path param
        super(Application, self).__init__(import_name, template_folder=template_folder, root_path=root_path,
                                          static_folder=None)
        self.config.from_pyfile('config/local_setting.py')
        if "ops_config" in os.environ:
            self.config.from_pyfile('config/%s_setting.py' % os.environ['ops_config'])
        db.init_app(self)
        redis_client.init_app(self)

db = SQLAlchemy()
redis_client = FlaskRedis()
app = Application(__name__, template_folder=os.getcwd() + '/web/templates/', root_path=os.getcwd())

manager = Manager(app)
"""
函数模板
"""
from common.libs.UrlManager import UrlManager

app.add_template_global(UrlManager.buildUrl, 'buildUrl')
app.add_template_global(UrlManager.buildStaticUrl, 'buildStaticUrl')
