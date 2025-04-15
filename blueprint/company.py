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


company_bp = Blueprint('company', __name__, url_prefix='/company')

# class Company:
#     def __init__(self, name, a, b, c, d, e, update_time):
#         self.name = name
#         self.a = a
#         self.b = b
#         self.c = c
#         self.d = d
#         self.e = e
#         self.update_time = update_time
#

class CompanyModel(db.Model):
    __tablename__ = 'company'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(500))
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

class CompanyForm(FlaskForm):
    company_name = StringField('企业名称', validators=[DataRequired()])
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

# class CompanyForm(FlaskForm):
#     company_name = StringField('Company Name', validators=[DataRequired()])
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


# @company_bp.route('/list')
# def index():
#     companyList = CompanyModel.query.all()
#     return render_template('company/list.html', companyList=companyList)
#
@company_bp.route('/list')
def index():
    # 从查询参数中获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = CompanyModel.query.paginate(page=page, per_page=per_page, error_out=False)
    company_list = pagination.items

    return render_template(
        'company/list.html',
        companyList=company_list,
        pagination=pagination,
        per_page=per_page
    )


@company_bp.route('/add', methods=['GET', 'POST'])
def add():
    companyForm = CompanyForm()
    # businessParkList = BusinessParkModel.query.all()
    # companyForm.business_park.choices = [('', '请选择楼园')] + [(business_park.id, business_park.name) for business_park
    #                                                             in businessParkList]

    if request.method == 'GET':
        return render_template('company/add.html', form=companyForm)
    else:
        if companyForm.validate_on_submit():
            data = companyForm.data
            company = CompanyModel(
                company_name=data['company_name'],
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
            db.session.add(company)
            db.session.commit()
            return index()
        else:
            # 验证失败就重新渲染表单并显示错误
            return '表单验证没通过'


@company_bp.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('company/upload.html')

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
        "company_name", "business_park", "visitor_name", "actual_people_count",
        "other_carrier", "key_person_name", "key_person_phone",
        "competitor_services", "competitor_price", "competitor_expiry",
        "remarks", "update_time"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return render_template('error/400.html', error='Excel表头不符合预期')

    # 遍历每一行数据
    for _, row in df.iterrows():
        row_data = row.to_dict()
        company_name = row_data.get("company_name")

        if not company_name or pd.isna(company_name):
            continue

        # 格式化 update_time
        update_time = row_data.get("update_time")
        if pd.isna(update_time) or not str(update_time).strip():
            # 自动生成 yyyymmdd 格式
            row_data["update_time"] = datetime.now().strftime('%Y%m%d')

        company = CompanyModel.query.filter_by(company_name=company_name).first()

        if company:
            # 更新：仅非空字段更新
            for field, value in row_data.items():
                if field != 'company_name' and pd.notna(value) and str(value).strip() != '':
                    setattr(company, field, value)
        else:
            # 新增公司
            filtered_data = {
                k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
            }
            company = CompanyModel(**filtered_data)
            db.session.add(company)

    db.session.commit()
    flash('导入完成')
    return redirect(request.url)

@company_bp.route('/update', methods=['GET', 'POST'])
def update():
    companyForm = CompanyForm()
    if request.method == 'GET':
        company_id = request.args.get('id', type=int)
        company = CompanyModel.query.get(company_id)
        companyForm.id.data = company.id
        companyForm.company_name.data = company.company_name
        companyForm.actual_people_count.data = company.actual_people_count
        companyForm.other_carrier.data = company.other_carrier
        companyForm.key_person_name.data = company.key_person_name
        companyForm.key_person_phone.data = company.key_person_phone
        companyForm.competitor_services.data = company.competitor_services
        companyForm.competitor_price.data = company.competitor_price
        companyForm.competitor_expiry.data = company.competitor_expiry
        companyForm.visitor_name.data = company.visitor_name
        companyForm.remarks.data = company.remarks
        return render_template('company/update.html', form=companyForm)
    else:
        if companyForm.validate_on_submit():
            data = companyForm.data
            # businessParkModel = BusinessParkModel(name=data['name'], company_name=data['company_name'])
            company = CompanyModel.query.get(data['id'])
            company.company_name = data['company_name']
            company.actual_people_count = data['actual_people_count']
            company.other_carrier = data['other_carrier']
            company.key_person_name = data['key_person_name']
            company.key_person_phone = data['key_person_phone']
            company.competitor_services = data['competitor_services']
            company.competitor_price = data['competitor_price']
            company.competitor_expiry = data['competitor_expiry']
            company.visitor_name = data['visitor_name']
            company.remarks = data['remarks']

            db.session.add(company)
            db.session.commit()
            return index()


@company_bp.route('/export', methods=['GET'])
def export_file():
    # 1. 查询数据库中的数据
    companies = CompanyModel.query.all()

    # 如果表中没有数据，可以考虑给出提示或返回一个空 Excel
    if not companies:
        flash('没有数据可导出')
        return redirect(request.referrer or '/')

    # 2. 将数据转换为 pandas 的 DataFrame
    #    这里假设你的 CompanyModel 包含的字段跟导入时一致，你也可以根据实际情况调整
    data = []
    for company in companies:
        data.append({
            "company_name": company.company_name,
            "business_park": company.business_park,
            "visitor_name": company.visitor_name,
            "actual_people_count": company.actual_people_count,
            "other_carrier": company.other_carrier,
            "key_person_name": company.key_person_name,
            "key_person_phone": company.key_person_phone,
            "competitor_services": company.competitor_services,
            "competitor_price": company.competitor_price,
            "competitor_expiry": company.competitor_expiry,
            "remarks": company.remarks,
            "update_time": company.update_time
        })

    df = pd.DataFrame(data)

    # 3. 写入到 Excel 并使用内存对象保存文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CompanyData')
    output.seek(0)

    # 4. 以附件形式返回给浏览器
    # Flask 2.x 之后可以使用 download_name 参数
    return send_file(
        output,
        as_attachment=True,
        download_name=f"company_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
