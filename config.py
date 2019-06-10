#!/usr/bin/python3
# -*- coding: utf-8 -*-
from car_detect import app


# haoservice查询key
HAOSERVICE_KEY = '88005ebd24174690b3004a07b9e80aae'
# HAOSERVICE_KEY = 'cdc63e0018424147ade60c7292f6a2c1'
# HAOSERVICE_KEY = 'f26a68790f634569867a295c02cc37dd'

# 百度查询key
APP_ID = '16440708'
API_KEY = 'sPf4YNUaOjrVS8dMqHTYjN95'
SECRET_KEY = '1B48tlGDWnZZpk61cirTiRkOyTKTgpdm'

# 数据库配置
app.config['SECRET_KEY'] = '654321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:bb12345@127.0.0.1:3306/car_detect'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:654321@127.0.0.1:3306/car_detect'
# 每次请求结束后会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True




