from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 加载数据库配置文件内容
app.config.from_object('config')  # 模块下的setting文件名，不用加py后缀
# app.config.from_envvar('FLASKR_SETTINGS')  # 环境变量，指向配置文件setting的路径

# 创建数据库实例对象
db = SQLAlchemy(app)



