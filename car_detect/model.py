#!/usr/bin/python3
# -*- coding: utf-8 -*-
from car_detect import db


# 定义数据库模型
class CarInfo(db.Model):
    # 表名
    __tablename__ = 'car_info'
    # 字段
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer)
    brand_name = db.Column(db.String(128))
    series_id = db.Column(db.Integer)
    series_name = db.Column(db.String(128))
    type_id = db.Column(db.Integer)
    type_name = db.Column(db.String(128))
    index = db.Column(db.String(256), index=True)

    def __repr__(self):
        return self.index
