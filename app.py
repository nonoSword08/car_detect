from urllib import request as ur

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from aip import AipImageClassify

app = Flask(__name__)

# haoservice查询key
HAOSERVICE_KEY = '88005ebd24174690b3004a07b9e80aae'
# 百度查询key
APP_ID = '16440708'
API_KEY = 'sPf4YNUaOjrVS8dMqHTYjN95'
SECRET_KEY = '1B48tlGDWnZZpk61cirTiRkOyTKTgpdm'

# 数据库配置
app.config['SECRET_KEY'] = '654321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@120.78.81.19:3306/car_detect'
# 每次请求结束后会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)  # 创建数据库实例对象


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

# 数据库初始化操作
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
                car_info = CarInfo(
                    brand_id=car_brand_id, brand_name=car_brand_name,
                    series_id=car_series_id, series_name=car_series_name,
                    type_id=car_type_id, type_name=car_type_name,
                    index=(car_brand_name + car_type_name)
                )
                car_info_list.append(car_info)
    print(car_info_list)
    db.session.add_all(car_info_list)
    # 提交修改
    db.session.commit()
    return '初始化成功'

# 首页（搜索）
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        img = request.files.get('img')
        print(img)
        if not img:  # 没有上传图片则取url
            img_url = request.form.get('img_url')
            try:
                img = ur.urlopen(img_url)
            except ValueError:
                return render_template('index.html', msg="请上传文件或URL地址")
        # 上传到百度接口
        client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
        options = {'top_num': 1, 'baike_num': 5}
        car_info = client.carDetect(img.read(), options)
        car_type_name = car_info['result'][0]['name']
        print(car_type_name)
        try:
            cars_info = CarInfo.query.filter(CarInfo.index.ilike('%' + car_type_name + '%'))
        except Exception:
            cars_info = None
        print(cars_info)
        return render_template('index.html', cars_info=cars_info)


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
            'http://apis.haoservice.com/lifeservice/car?id=' + str(
                car_id) + '&key=' + HAOSERVICE_KEY + '&paybyvas=false')
        details = eval(response.read().decode('utf-8'))['result']
    except Exception:
        return render_template('detail.html', msg='非常抱歉，暂无此车型信息')
    index = request.args.get('index')
    price = request.args.get('price')
    return render_template('detail.html', details=details, index=index, price=price)


if __name__ == '__main__':
    app.run()
