import os
from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect
from sqlalchemy import Column, Integer
from werkzeug.utils import secure_filename
from wtforms.fields.simple import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

from exts import db

business_park_bp = Blueprint('business_park', __name__, url_prefix='/park')


class BusinessParkModel(db.Model):
    '''
    园区模型
    '''
    __tablename__ = 'business_park'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500))
    area = db.Column(db.String(500))
    company_name = db.Column(db.String(500))
    remark = db.Column(db.String(500))


class BusinessParkForm(FlaskForm):
    # id = Column(Integer, primary_key=True)
    id = HiddenField()
    name = StringField('园区名称', render_kw={'placeholder': '请输入园区名称'}, validators=[DataRequired()])
    company_name = StringField('公司名称', render_kw={'placeholder': '请输入公司名称'})
    submit = SubmitField('确定')


@business_park_bp.route('/list')
def index():
    businessParkList = BusinessParkModel.query.all()
    return render_template('business_park/list.html', businessParkList=businessParkList)


@business_park_bp.route('/add', methods=['GET', 'POST'])
def add():
    businessParkForm = BusinessParkForm()
    if request.method == 'GET':
        # print(businessParkForm.name.label)
        return render_template('business_park/add.html', form=businessParkForm)
    else:
        if businessParkForm.validate_on_submit():
            data = businessParkForm.data
            businessPark = BusinessParkModel(name=data['name'], company_name=data['company_name'])
            db.session.add(businessPark)
            db.session.commit()
            return index()

@business_park_bp.route('/update', methods=['GET', 'POST'])
def update():
    businessParkForm = BusinessParkForm()
    if request.method == 'GET':
        id = request.args.get('id', type=int)
        businessPark = BusinessParkModel.query.get(id)
        businessParkForm.id.data = businessPark.id
        businessParkForm.name.data = businessPark.name
        businessParkForm.company_name.data = businessPark.company_name
        return render_template('business_park/update.html', form=businessParkForm)
    else:
        if businessParkForm.validate_on_submit():
            data = businessParkForm.data
            # businessParkModel = BusinessParkModel(name=data['name'], company_name=data['company_name'])
            businessPark = BusinessParkModel.query.get(data['id'])
            businessPark.name = data['name']
            businessPark.company_name = data['company_name']
            db.session.add(businessPark)
            db.session.commit()
            return index()


@business_park_bp.route('/delete/<int:id>')
def delete(id):
    businessPark = BusinessParkModel.query.get(id)
    db.session.delete(businessPark)
    db.session.commit()
    return index()
    # return render_template('business_park/list.html')

@business_park_bp.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('business_park/upload.html')

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
        "name", "area", "company_name", "remark"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return render_template('error/400.html', error='Excel表头不符合预期')

    # 遍历每一行数据
    for _, row in df.iterrows():
        row_data = row.to_dict()
        name = row_data.get("name")

        if not name or pd.isna(name):
            continue

        # 新增公司
        filtered_data = {
            k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
        }
        business_park = BusinessParkModel(**filtered_data)
        db.session.add(business_park)

    db.session.commit()
    flash('导入完成')
    return index()

