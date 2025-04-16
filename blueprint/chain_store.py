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

chain_store_bp = Blueprint('chain_store', __name__, url_prefix='/chain_store')


# class ChainStore:
#     def __init__(self, name, a, b, c, d, e, update_time):
#         self.name = name
#         self.a = a
#         self.b = b
#         self.c = c
#         self.d = d
#         self.e = e
#         self.update_time = update_time
#

class ChainBandModel(db.Model):
    '''
    连锁品牌模型
    '''
    __tablename__ = 'chain_band'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    band = db.Column(db.String(500))
    area = db.Column(db.String(500))
    store = db.Column(db.String(500))
    remark = db.Column(db.String(500))

class ChainStoreModel(db.Model):
    __tablename__ = 'chain_store'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chain_store_name = db.Column(db.String(500))
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
    chain_band = db.Column(db.String(500))


class ChainStoreForm(FlaskForm):
    chain_store_name = StringField('企业名称', validators=[DataRequired()])
    actual_people_count = StringField('单位实际人数')
    other_carrier = StringField('异网运营商')
    key_person_name = StringField('关键人姓名')
    key_person_phone = StringField('关键人电话')
    competitor_services = StringField('友商已有业务')
    competitor_price = StringField('友商合同价格')
    competitor_expiry = StringField('友商产品到期时间')
    visitor_name = StringField('拜访人')
    remarks = StringField('备注')
    id = StringField('ID')  # 如果你要传 hidden id
    submit = SubmitField('提交')


# class ChainStoreForm(FlaskForm):
#     chain_store_name = StringField('ChainStore Name', validators=[DataRequired()])
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


# @chain_store_bp.route('/list')
# def index():
#     chain_storeList = ChainStoreModel.query.all()
#     return render_template('chain_store/list.html', chain_storeList=chain_storeList)
#
@chain_store_bp.route('/list')
def index():
    # 从查询参数中获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = ChainStoreModel.query.paginate(page=page, per_page=per_page, error_out=False)
    chain_store_list = pagination.items

    return render_template(
        'chain_store/list.html',
        chain_storeList=chain_store_list,
        pagination=pagination,
        per_page=per_page
    )


@chain_store_bp.route('/add', methods=['GET', 'POST'])
def add():
    chain_storeForm = ChainStoreForm()
    # businessParkList = BusinessParkModel.query.all()
    # chain_storeForm.business_park.choices = [('', '请选择楼园')] + [(business_park.id, business_park.name) for business_park
    #                                                             in businessParkList]

    if request.method == 'GET':
        return render_template('chain_store/add.html', form=chain_storeForm)
    else:
        if chain_storeForm.validate_on_submit():
            data = chain_storeForm.data
            chain_store = ChainStoreModel(
                chain_store_name=data['chain_store_name'],
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
                chain_band=data['chain_band']
            )
            db.session.add(chain_store)
            db.session.commit()
            return index()
        else:
            # 验证失败就重新渲染表单并显示错误
            return '表单验证没通过'


@chain_store_bp.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('chain_store/upload.html')

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
        "chain_store_name", "chain_band", "visitor_name", "actual_people_count", "other_carrier", "key_person_name",
        "key_person_phone", "competitor_services", "competitor_price", "competitor_expiry", "remarks", "update_time"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return render_template('error/400.html', error='Excel表头不符合预期')

    # 遍历每一行数据
    for _, row in df.iterrows():
        row_data = row.to_dict()
        chain_store_name = row_data.get("chain_store_name")

        if not chain_store_name or pd.isna(chain_store_name):
            continue

        # 格式化 update_time
        update_time = row_data.get("update_time")
        if pd.isna(update_time) or not str(update_time).strip():
            # 自动生成 yyyymmdd 格式
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')

        chain_store = ChainStoreModel.query.filter_by(chain_store_name=chain_store_name).first()

        if chain_store:
            # 更新：仅非空字段更新
            for field, value in row_data.items():
                if field != 'chain_store_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(chain_store, field, value)
        else:
            # 新增公司
            filtered_data = {
                k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
            }
            chain_store = ChainStoreModel(**filtered_data)
            db.session.add(chain_store)

    db.session.commit()
    flash('导入完成')
    return redirect(request.url)


@chain_store_bp.route('/update', methods=['GET', 'POST'])
def update():
    chain_storeForm = ChainStoreForm()
    if request.method == 'GET':
        chain_store_id = request.args.get('id', type=int)
        chain_store = ChainStoreModel.query.get(chain_store_id)
        chain_storeForm.id.data = chain_store.id
        chain_storeForm.chain_store_name.data = chain_store.chain_store_name
        chain_storeForm.actual_people_count.data = chain_store.actual_people_count
        chain_storeForm.other_carrier.data = chain_store.other_carrier
        chain_storeForm.key_person_name.data = chain_store.key_person_name
        chain_storeForm.key_person_phone.data = chain_store.key_person_phone
        chain_storeForm.competitor_services.data = chain_store.competitor_services
        chain_storeForm.competitor_price.data = chain_store.competitor_price
        chain_storeForm.competitor_expiry.data = chain_store.competitor_expiry
        chain_storeForm.visitor_name.data = chain_store.visitor_name
        chain_storeForm.visitor_name.data = chain_store.visitor_name
        chain_storeForm.remarks.data = chain_store.remarks
        return render_template('chain_store/update.html', form=chain_storeForm)
    else:
        if chain_storeForm.validate_on_submit():
            data = chain_storeForm.data
            # businessParkModel = BusinessParkModel(name=data['name'], chain_store_name=data['chain_store_name'])
            chain_store = ChainStoreModel.query.get(data['id'])
            chain_store.chain_store_name = data['chain_store_name']
            chain_store.actual_people_count = data['actual_people_count']
            chain_store.other_carrier = data['other_carrier']
            chain_store.key_person_name = data['key_person_name']
            chain_store.key_person_phone = data['key_person_phone']
            chain_store.competitor_services = data['competitor_services']
            chain_store.competitor_price = data['competitor_price']
            chain_store.competitor_expiry = data['competitor_expiry']
            chain_store.visitor_name = data['visitor_name']
            chain_store.remarks = data['remarks']

            db.session.add(chain_store)
            db.session.commit()
            return index()


@chain_store_bp.route('/export_old', methods=['GET'])
def export_file_old():
    # 1. 查询数据库中的数据
    companies = ChainStoreModel.query.all()

    # 如果表中没有数据，可以考虑给出提示或返回一个空 Excel
    if not companies:
        flash('没有数据可导出')
        return redirect(request.referrer or '/')

    # 2. 将数据转换为 pandas 的 DataFrame
    #    这里假设你的 ChainStoreModel 包含的字段跟导入时一致，你也可以根据实际情况调整
    data = []
    for chain_store in companies:
        data.append({
            "chain_store_name": chain_store.chain_store_name,
            "business_park": chain_store.business_park,
            "visitor_name": chain_store.visitor_name,
            "actual_people_count": chain_store.actual_people_count,
            "other_carrier": chain_store.other_carrier,
            "key_person_name": chain_store.key_person_name,
            "key_person_phone": chain_store.key_person_phone,
            "competitor_services": chain_store.competitor_services,
            "competitor_price": chain_store.competitor_price,
            "competitor_expiry": chain_store.competitor_expiry,
            "remarks": chain_store.remarks,
            "update_time": chain_store.update_time
        })

    df = pd.DataFrame(data)

    # 3. 写入到 Excel 并使用内存对象保存文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ChainStoreData')
    output.seek(0)

    # 4. 以附件形式返回给浏览器
    # Flask 2.x 之后可以使用 download_name 参数
    return send_file(
        output,
        as_attachment=True,
        download_name=f"chain_store_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@chain_store_bp.route('/export', methods=['GET'])
def export_file():
    # 1. 获取所有“品牌-商店”记录
    bs_list = ChainBandModel.query.all()

    # 如果没有数据，可以酌情返回提示
    if not bs_list:
        return "没有设置连锁企业"

    # 2. 逐行查找企业详细信息，并将信息拼在一起
    output_data = []
    for bs in bs_list:
        # pc 是 ParkCompanyModel 的一行（id, business_park, company_name）
        store_detail = ChainStoreModel.query.filter_by(chain_store_name=bs.store).first()

        # 把楼园+企业拼到一个字典
        row_dict = {
            'band': bs.band,
            'store': bs.store
        }
        if store_detail:
            # 如果查到对应的企业信息，就把详细字段加上
            row_dict['actual_people_count'] = store_detail.actual_people_count
            row_dict['other_carrier'] = store_detail.other_carrier
            row_dict['key_person_name'] = store_detail.key_person_name
            row_dict['key_person_phone'] = store_detail.key_person_phone
            row_dict['competitor_services'] = store_detail.competitor_services
            row_dict['competitor_price'] = store_detail.competitor_price
            row_dict['competitor_expiry'] = store_detail.competitor_expiry
            row_dict['visitor_name'] = store_detail.visitor_name
            row_dict['remarks'] = store_detail.remarks
            row_dict['update_time'] = store_detail.update_time
        else:
            # 如果公司详细信息里没有匹配到，就留空或自定义提示
            row_dict['actual_people_count'] = ''
            row_dict['other_carrier'] = ''
            row_dict['key_person_name'] = ''
            row_dict['key_person_phone'] = ''
            row_dict['competitor_services'] = ''
            row_dict['competitor_price'] = ''
            row_dict['competitor_expiry'] = ''
            row_dict['visitor_name'] = ''
            row_dict['remarks'] = ''
            row_dict['update_time'] = ''

        output_data.append(row_dict)

    # 3. 用 pandas 生成 DataFrame
    df = pd.DataFrame(output_data)

    df.rename(columns={
        "band": "连锁品牌名称",
        "store": "连锁商铺名称",
        "actual_people_count": "单位实际人数",
        "other_carrier": "异网运营商",
        "key_person_name": "关键人姓名",
        "key_person_phone": "关键人电话",
        "competitor_services": "友商已有业务",
        "competitor_price": "友商合同价格",
        "competitor_expiry": "友商产品到期时间",
        "visitor_name": "拜访人",
        "remarks": "备注",
        "update_time": "更新时间"
    }, inplace=True)

    # 4. 写入到 Excel 并使用内存对象保存文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='连锁品牌商铺导出')
    output.seek(0)

    # 5. 以附件形式返回给浏览器
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        as_attachment=True,
        download_name=f"连锁品牌商铺导出_{now_str}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@chain_store_bp.route('/delete/<int:id>')
def delete(id):
    chain_store = ChainStoreModel.query.get(id)
    db.session.delete(chain_store)
    db.session.commit()
    return index()