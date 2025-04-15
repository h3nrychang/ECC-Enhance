import io
import os
from datetime import datetime

import pandas as pd

from flask import Blueprint, render_template, request, flash, redirect, send_file
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from werkzeug.utils import secure_filename
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

# from blueprint import business_park
# from blueprint.business_park import BusinessParkModel
from exts import db

hotel_bp = Blueprint('hotel', __name__, url_prefix='/hotel')


# class Hotel:
#     def __init__(self, name, a, b, c, d, e, update_time):
#         self.name = name
#         self.a = a
#         self.b = b
#         self.c = c
#         self.d = d
#         self.e = e
#         self.update_time = update_time
#

class HotelModel(db.Model):
    __tablename__ = 'hotel'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_name = db.Column(db.String(500))
    actual_people_count = db.Column(db.String(500))
    other_carrier = db.Column(db.String(500))
    key_person_name = db.Column(db.String(500))
    key_person_phone = db.Column(db.String(500))
    competitor_services = db.Column(db.String(500))
    competitor_price = db.Column(db.String(500))
    competitor_expiry = db.Column(db.String(500))
    visitor_name = db.Column(db.String(500))
    remarks = db.Column(db.String(500))
    update_time = db.Column(db.String(500))
    # business_park_id = db.Column(db.Integer, ForeignKey('business_park.id'))
    # business_park = db.relationship('BusinessParkModel')
    business_park = db.Column(db.String(500))


class HotelForm(FlaskForm):
    hotel_name = StringField('企业名称', validators=[DataRequired()])
    actual_people_count = StringField('单位实际人数')
    other_carrier = StringField('异网运营商')
    key_person_name = StringField('关键人姓名')
    key_person_phone = StringField('关键人电话')
    competitor_services = StringField('友商已有业务')
    competitor_price = StringField('友商合同价格')
    competitor_expiry = StringField('友商产品到期时间')
    visitor_name = StringField('拜访人')
    remarks = StringField('备注')
    update_time = StringField('更新时间')
    id = StringField('ID')  # 如果你要传 hidden id
    submit = SubmitField('提交')


# class HotelForm(FlaskForm):
#     hotel_name = StringField('Hotel Name', validators=[DataRequired()])
#     business_park = StringField('楼园名称')
#     actual_people_count = StringField('Actual People Count')
#     other_carrier = StringField('Other Carrier')
#     key_person_name = StringField('Key Person Name')
#     key_person_phone = StringField('Key Person Phone')
#     competitor_services = StringField('Competitor Services')
#     competitor_price = StringField('Competitor Price')
#     competitor_expiry = StringField('Competitor Expiry')
#     remarks = StringField('Remarks')
#     update_time = StringField('Update Time')
#     # business_park = SelectField('园区', choices=[], validators=[DataRequired()])
#     submit = SubmitField('确定')


# @hotel_bp.route('/list')
# def index():
#     hotelList = HotelModel.query.all()
#     return render_template('hotel/list.html', hotelList=hotelList)
#
@hotel_bp.route('/list')
def index():
    # 从查询参数中获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = HotelModel.query.paginate(page=page, per_page=per_page, error_out=False)
    hotel_list = pagination.items

    return render_template(
        'hotel/list.html',
        hotelList=hotel_list,
        pagination=pagination,
        per_page=per_page
    )


@hotel_bp.route('/add', methods=['GET', 'POST'])
def add():
    hotelForm = HotelForm()
    # businessParkList = BusinessParkModel.query.all()
    # hotelForm.business_park.choices = [('', '请选择楼园')] + [(business_park.id, business_park.name) for business_park
    #                                                             in businessParkList]

    if request.method == 'GET':
        return render_template('hotel/add.html', form=hotelForm)
    else:
        if hotelForm.validate_on_submit():
            data = hotelForm.data
            hotel = HotelModel(
                hotel_name=data['hotel_name'],
                actual_people_count=data['actual_people_count'],
                other_carrier=data['other_carrier'],
                key_person_name=data['key_person_name'],
                key_person_phone=data['key_person_phone'],
                competitor_services=data['competitor_services'],
                competitor_price=data['competitor_price'],
                competitor_expiry=data['competitor_expiry'],
                visitor_name=data['visitor_name'],
                remarks=data['remarks'],
                update_time=data['update_time'],
                # business_park_id=data['business_park']
                business_park=data['business_park']
            )
            db.session.add(hotel)
            db.session.commit()
            return index()
        else:
            # 验证失败就重新渲染表单并显示错误
            return '表单验证没通过'


@hotel_bp.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('hotel/upload.html')

    file = request.files.get('file')
    if not file:
        flash('请上传文件')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    filepath = os.path.join('upload', filename)
    file.save(filepath)

    # 读取 Excel 文件（pandas 自动支持 .xlsx/.xls）
    try:
        df = pd.read_excel(filepath, dtype=str)  # 强制为字符串，防止数值被转成 float
    except Exception as e:
        return render_template('error/400.html', error='无法读取Excel文件，请确认格式')

    expected_fields = [
        "hotel_name", "visitor_name", "actual_people_count", "other_carrier", "key_person_name", "key_person_phone",
        "competitor_services", "competitor_price", "competitor_expiry", "remarks", "update_time"

    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return render_template('error/400.html', error='Excel表头不符合预期')

    # 遍历每一行数据
    for _, row in df.iterrows():
        row_data = row.to_dict()
        hotel_name = row_data.get("hotel_name")

        if not hotel_name or pd.isna(hotel_name):
            continue

        # 格式化 update_time
        update_time = row_data.get("update_time")
        if pd.isna(update_time) or not str(update_time).strip():
            # 自动生成 yyyymmdd 格式
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')

        hotel = HotelModel.query.filter_by(hotel_name=hotel_name).first()

        if hotel:
            # 更新：仅非空字段更新
            for field, value in row_data.items():
                if field != 'hotel_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(hotel, field, value)
        else:
            # 新增公司
            filtered_data = {
                k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
            }
            hotel = HotelModel(**filtered_data)
            db.session.add(hotel)

    db.session.commit()
    flash('导入完成')
    return redirect(request.url)


@hotel_bp.route('/update', methods=['GET', 'POST'])
def update():
    hotelForm = HotelForm()
    if request.method == 'GET':
        hotel_id = request.args.get('id', type=int)
        hotel = HotelModel.query.get(hotel_id)
        hotelForm.id.data = hotel.id
        hotelForm.hotel_name.data = hotel.hotel_name
        hotelForm.actual_people_count.data = hotel.actual_people_count
        hotelForm.other_carrier.data = hotel.other_carrier
        hotelForm.key_person_name.data = hotel.key_person_name
        hotelForm.key_person_phone.data = hotel.key_person_phone
        hotelForm.competitor_services.data = hotel.competitor_services
        hotelForm.competitor_price.data = hotel.competitor_price
        hotelForm.competitor_expiry.data = hotel.competitor_expiry
        hotelForm.visitor_name.data = hotel.visitor_name
        hotelForm.remarks.data = hotel.remarks
        return render_template('hotel/update.html', form=hotelForm)
    else:
        if hotelForm.validate_on_submit():
            data = hotelForm.data
            # businessParkModel = BusinessParkModel(name=data['name'], hotel_name=data['hotel_name'])
            hotel = HotelModel.query.get(data['id'])
            hotel.hotel_name = data['hotel_name']
            hotel.actual_people_count = data['actual_people_count']
            hotel.other_carrier = data['other_carrier']
            hotel.key_person_name = data['key_person_name']
            hotel.key_person_phone = data['key_person_phone']
            hotel.competitor_services = data['competitor_services']
            hotel.competitor_price = data['competitor_price']
            hotel.competitor_expiry = data['competitor_expiry']
            hotel.visitor_name = data['visitor_name']
            hotel.remarks = data['remarks']

            db.session.add(hotel)
            db.session.commit()
            return index()


@hotel_bp.route('/export', methods=['GET'])
def export_file():
    # 1. 查询数据库中的数据
    companies = HotelModel.query.all()

    # 如果表中没有数据，可以考虑给出提示或返回一个空 Excel
    if not companies:
        flash('没有数据可导出')
        return redirect(request.referrer or '/')

    # 2. 将数据转换为 pandas 的 DataFrame
    #    这里假设你的 HotelModel 包含的字段跟导入时一致，你也可以根据实际情况调整
    data = []
    for hotel in companies:
        data.append({
            "hotel_name": hotel.hotel_name,
            "business_park": hotel.business_park,
            "visitor_name": hotel.visitor_name,
            "actual_people_count": hotel.actual_people_count,
            "other_carrier": hotel.other_carrier,
            "key_person_name": hotel.key_person_name,
            "key_person_phone": hotel.key_person_phone,
            "competitor_services": hotel.competitor_services,
            "competitor_price": hotel.competitor_price,
            "competitor_expiry": hotel.competitor_expiry,
            "remarks": hotel.remarks,
            "update_time": hotel.update_time
        })

    df = pd.DataFrame(data)

    # 3. 写入到 Excel 并使用内存对象保存文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HotelData')
    output.seek(0)

    # 4. 以附件形式返回给浏览器
    # Flask 2.x 之后可以使用 download_name 参数
    return send_file(
        output,
        as_attachment=True,
        download_name=f"hotel_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
