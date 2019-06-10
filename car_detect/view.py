#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib import request as ur

from flask import render_template, request
from aip import AipImageClassify

from car_detect import app
from config import HAOSERVICE_KEY, APP_ID, API_KEY, SECRET_KEY
from car_detect.model import CarInfo

# 数据库初始化操作
"""
@app.route('/init')
def init():
    # 删除旧表
    db.drop_all()
    # 创建新表
    db.create_all()
    # 插入获得json数据
    import json
    with open('car.json', 'r', encoding='utf-8') as f:
        car_data = json.load(f)
    car_info_list = []
    for car_brand_info in car_data['result']:
        car_brand_name = car_brand_info['N']
        car_brand_id = car_brand_info['I']
        print('车牌：%s，车牌ID：%s' % (car_brand_name, car_brand_id))
        for car_series_info in car_brand_info['List']:
            car_series_name = car_series_info['N']
            car_series_id = car_series_info['I']
            print('\t车系：%s，车系ID：%s' % (car_series_name, car_series_id))
            for car_type_info in car_series_info['List']:
                car_type_name = car_type_info['N']
                car_type_id = car_type_info['I']
                print('\t\t车型：%s，车型ID：%s' % (car_type_name, car_type_id))
                # 处理字符串拿出索引字符串
                if car_brand_name in car_type_name:
                    index = car_type_name.replace('·', '')
                else:
                    index = car_brand_name.replace('·', '') + car_type_name.replace('·', '')
                car_info = CarInfo(
                    brand_id=car_brand_id, brand_name=car_brand_name,
                    series_id=car_series_id, series_name=car_series_name,
                    type_id=car_type_id, type_name=car_type_name,
                    index=index,
                )
                car_info_list.append(car_info)
    print(car_info_list)
    db.session.add_all(car_info_list)
    # 提交修改
    db.session.commit()
    return '初始化成功'
"""


# 首页（搜索）
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        img = request.files.get('img')
        if not img:  # 没有上传图片则取url
            img_url = request.form.get('img_url')
            try:
                img = ur.urlopen(img_url)
            except Exception:
                return render_template('index.html', msg="请上传文件或URL地址")
        # 上传到百度接口
        try:
            client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
            options = {'top_num': 1, 'baike_num': 5}
            car_info = client.carDetect(img.read(), options)
            if car_info['result'][0]['name'] == '非车类':
                return render_template('index.html', msg="未识别到车类")
            car_index_name = car_info['result'][0]['name']
            print(car_index_name)
        except Exception:
            return render_template('index.html', msg="接口繁忙，请稍后再试")
        try:
            cars_info = CarInfo.query.filter(CarInfo.index.ilike('%' + car_index_name + '%'))
        except Exception:
            cars_info = None
        if cars_info.count() != 0:
            return render_template('index.html', cars_info=cars_info)
        else:
            return render_template('index.html', msg="未识别到车类")


# 车型详情页
@app.route('/typedetail/<string:car_type_id>')
def typetail(car_type_id):
    index = request.args.get('index')
    try:
        response = ur.urlopen(
            'http://apis.haoservice.com/lifeservice/car/GetModel/?id=' +
            car_type_id + '&key=' + HAOSERVICE_KEY + '&paybyvas=false'
        )
        type_result = eval(response.read().decode('utf-8'))['result']['List']
    except Exception:
        return render_template('typedetail.html', msg="非常抱歉，暂无此车型信息")
    return render_template('typedetail.html', type_result=type_result, index=index)


# 配置详情页
@app.route('/detail/<string:car_id>')
def detail(car_id):
    try:
        response = ur.urlopen(
            'http://apis.haoservice.com/lifeservice/car?id=' +
            car_id + '&key=' + HAOSERVICE_KEY + '&paybyvas=false'
        )
        details = eval(response.read().decode('utf-8'))['result']
    except Exception:
        return render_template('detail.html', msg='非常抱歉，暂无此车型信息')
    index = request.args.get('index')
    price = request.args.get('price')
    return render_template('detail.html', details=details, index=index, price=price)
