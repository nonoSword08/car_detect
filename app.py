from urllib import request as ur

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from aip import AipImageClassify

app = Flask(__name__)

# haoservice查询key
HAOSERVICE_KEY = 'f26a68790f634569867a295c02cc37dd'
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
@app.route('/index', methods=['GET', 'POST'])
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
    response = ur.urlopen(
        'http://apis.haoservice.com/lifeservice/car/GetModel/?id=' +
        car_type_id + '&key=' + HAOSERVICE_KEY + '&paybyvas=false'
    )
    type_result = eval(response.read().decode('utf-8'))['result']['List']
    return render_template('typedetail.html', type_result=type_result, index=index)

# 配置详情页
@app.route('/detail/<string:car_id>')
def detail(car_id):
    response = ur.urlopen(
        'http://apis.haoservice.com/lifeservice/car?id=' + str(
            car_id) + '&key=' + HAOSERVICE_KEY + '&paybyvas=false')
    details = eval(response.read().decode('utf-8'))['result']
    print(details)
    index = request.args.get('index')
    price = request.args.get('price')
    # details = eval(
    #     "{'基本参数': {'img': 'https://car2.autoimg.cn/cardfs/product/g2/M08/EB/AB/t_autohomecar__wKgHFlsX2JOATHguAApj2TqFUug251.jpg', 'manufacturers': '广汽本田', 'level': '中型车', 'engine': '1.5T 177马力 L4', 'gearbox': 'CVT无级变速', 'longHighWith': '4893*1862*1449', 'bodyStructure': '4门5座三厢车', 'maximumSpeed': '190', 'officialAcceleration': '-', 'measuredAcceleration': '-', 'measuredBrake': '-', 'measuredFuelConsumption': '-', 'averageConsumptionOfCertification': '-', 'ministryOfIntegratedFuelConsumption': '6.4', 'measuredGroundClearance': '', 'vehicleQuality': '三年或10万公里'}, '车身': {'length': '4893', 'width': '1862', 'height': '1449', 'wheelbase': '2830', 'frontTrack': '1600', 'rearWheel': '1610', 'minnumGroundClearance': '-', 'kerbMass': '1475', 'bodyStructure': '三厢车', 'numberOfDoors': '4', 'numberOfSeats': '5', 'mailVolume': '56', 'compartmentVolume': '-'}, '发动机': {'model': '-', 'displacement': '1498', 'intakeForm': '涡轮增压', 'cylinderExhaustForm': 'L', 'cylinders': '4', 'valvePerCylinder': '4', 'compressionRatio': '10.3', 'gasDistrbutionMechanism': 'DOHC', 'cylinderBy': '-', 'trip': '-', 'maxHorsepower': '177', 'maxPower': '130', 'maxPowerSpeed': '6000', 'maxTorque': '230', 'maxTorqueSpeed': '1500-3000', 'specialTechnology': '-', 'fuelForm': '汽油', 'fuel': '92号', 'fuleWay': '直喷', 'cylinderHeadMeterial': '铝合金', 'cylinderMaterial': '铝合金', 'environmentalProtection': '国V'}, '变速箱': {'abbreviation': 'CVT无级变速', 'grarNum': '无级变速', 'type': '无级变速箱(CVT)'}, '底盘转向': {'drivingMethod': '前置前驱', 'fourWheelDriveForm': '', 'centralDifferentialStructure': '', 'frontSuspensionType': '麦弗逊式独立悬架', 'SuspensionType': '多连杆独立悬架', 'powerType': '电动助力', 'bodyStructure': '承载式'}, '车轮制动': {'frontBrakeType': '通风盘式', 'brakeType': '盘式', 'parkingBrakeType': '电子驻车', 'frontTyreSpecifications': '225/50 R17', 'typreSpecifications': '225/50 R17', 'spareTrieSpecifications': '非全尺寸'}, '安全装备': {'lordDeputyDirversSeatAirbag': '主●&nbsp;/&nbsp;副●', 'frontAndRearSideAirbags': '前●&nbsp;/&nbsp;后-', 'beforeAndAffterTheHeadAirbag': '-', 'kneeAirbag': '-', 'pressureMonitoringDevice': '●', 'zeroPressureContinuedTravel': '-', 'sagetyBeltPrompt': '●', 'childSeatInterface': '●', 'engineElectronicAntitheft': '●', 'controlLock': '●', 'RmeoteKey': '-', 'keylessStartSystem': '●', 'keylessEntrySystem': '-'}, '操控配置': {'ABS': '●', 'brakingForceDistribution': '●', 'braleAssist': '●', 'tractionControl': '●', 'stabilityControl': '●', 'upslopeAuxiliary': '●', 'automaticParking': '●', 'steepSlopeSlowlyDescending': '-', 'variableSuspension': '-', 'frontAxleLimitedSlip': '-', 'centralDifferential': '-', 'axleLimitedSlip': '-', 'differentialLocking': '-', 'DifferetialMechanism': '-'}, '外部配置': {'electricSkylight': '●', 'panoramicSunroof': '-', 'appearancePackage': '-', 'aluminumAlloyWheels': '●', 'electricSuctionDoor': '-', 'slideDoor': '-', 'electricTrunk': '-'}, '内部配置': {'leatherSteeringWheel': '', 'steeringWheelAdjustment': '上下+前后调节', 'steeringWheelOfElectricControl': '-', 'multifunctionSteeringWheel': '●', 'steeringWheelShift': '-', 'steeringWheelHeating': '-', 'cruiseControl': '-', 'parkingRadar': '-', 'reverseVideoPhotography': '-', 'drivingComputerDispaly': '●', 'HUD': '-'}, '座椅配置': {'genuineLeather': '', 'movementStyle': '-', 'heightAdjustment': '●', 'lumbarSupport': '-', 'shoulderSupport': '-', 'driverSeatElectricAdjustment': '-', 'SecondRowOfBackrestAngleAdjustment': '-', 'secondSeatMove': '-', 'RearSeatElectricAdjustment': '-', 'electricSeatMemory': '-', 'Heating': '-', 'ventilation': '-', 'massage': '-', 'backDowmMode': '整体放倒', 'ThirdRowSeat': '-', 'handrail': '前●&nbsp;/&nbsp;后●', 'rearGlassFrame': '●'}, '多媒体配置': {'GPS': '-', 'orientationOfInteraction': '', 'consoleScreen': '●', 'hardDrive': '', 'bluetoothPhone': '●', 'TV': '-', 'rearLcdScreen': '-', 'externalSoundSource': 'USB', 'cd': '-', 'multimediaSystem': '', 'speakerBrand': '-', 'loundspeakersNum': '4-5喇叭'}, '灯光配置': {'gangGasHeadlight': 'LED', 'LED': '卤素', 'daytimeWalkLamp': '●', 'automaticHeadlights': '-', 'steeringSuxiliaryLamp': '-', 'steeringHeadlamp': '-', 'frontFogLamp': '●', 'headlightAdjusting': '●', 'headlightCleaning': '-', 'atmosphereLamp': '-'}, '玻璃后视镜': {'electricWindow': '前●&nbsp;/&nbsp;后●', 'preventClampsHand': '●', 'ultravioletRays': '●', 'mirrorElectricAdiustment': '●', 'rearviewMirrorHeating': '●', 'antiGtlare': '-', 'fold': '●', 'memory': '-', 'yangCurtain': '-', 'ceZheCurtain': '-', 'privacyglass': '-', 'cosmeticMirror': '●', 'rearWiper': '-', 'sensingWipers': '-'}, '空调冰箱': {'controlMethod': '自动●', 'rearAirConditioning': '', 'rearSeatVents': '●', 'temperatureCXontrol': '●', 'airConditioning': '●', 'regrigerator': '-'}, '高科技配置': {'automaticParking': '-', 'engineStartStop': '-', 'auxiliary': '-', 'laneDepartureWarning': '-', 'activesafety': '-', 'activeSteering': '-', 'nightVisionSystem': '-', 'lcdScreen': '-', 'adaptiveCruiseControl': '-', 'panoramicCamera': '-'}}")
    return render_template('detail.html', details=details, index=index, price=price)


if __name__ == '__main__':
    app.run()
