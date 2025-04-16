import os

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect
from sqlalchemy import Column, Integer
from werkzeug.utils import secure_filename
from wtforms.fields.simple import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

from exts import db

chain_band_bp = Blueprint('chain_band', __name__, url_prefix='/chain_band')


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


class ChainBandForm(FlaskForm):
    # id = Column(Integer, primary_key=True)
    id = HiddenField()
    band = StringField('连锁品牌名称', render_kw={'placeholder': '请输入连锁品牌名称'}, validators=[DataRequired()])
    store = StringField('连锁店铺名称', render_kw={'placeholder': '请输入连锁店铺名称'})
    submit = SubmitField('确定')


@chain_band_bp.route('/list')
def index():
    chanBandList = ChainBandModel.query.all()
    return render_template('chain_band/list.html', chanBandList=chanBandList)


@chain_band_bp.route('/add', methods=['GET', 'POST'])
def add():
    chainBandForm = ChainBandForm()
    if request.method == 'GET':
        # print(chanBandForm.name.label)
        return render_template('chain_band/add.html', form=chainBandForm)
    else:
        if chainBandForm.validate_on_submit():
            data = chainBandForm.data
            chanBand = ChainBandModel(name=data['name'], company_name=data['company_name'])
            db.session.add(chanBand)
            db.session.commit()
            return index()

@chain_band_bp.route('/update', methods=['GET', 'POST'])
def update():
    chanBandForm = ChainBandForm()
    if request.method == 'GET':
        id = request.args.get('id', type=int)
        chanBand = ChainBandModel.query.get(id)
        chanBandForm.id.data = chanBand.id
        chanBandForm.band.data = chanBand.band
        chanBandForm.store.data = chanBand.store
        return render_template('chain_band/update.html', form=chanBandForm)
    else:
        if chanBandForm.validate_on_submit():
            data = chanBandForm.data
            # chanBandModel = ChainBandModel(name=data['name'], company_name=data['company_name'])
            chanBand = ChainBandModel.query.get(data['id'])
            chanBand.band = data['band']
            chanBand.store = data['store']
            db.session.add(chanBand)
            db.session.commit()
            return index()


@chain_band_bp.route('/delete/<int:id>')
def delete(id):
    chanBand = ChainBandModel.query.get(id)
    db.session.delete(chanBand)
    db.session.commit()
    return index()
    # return render_template('chain_band/list.html')

@chain_band_bp.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('chain_band/upload.html')

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
        "band", "area", "store", "remark"
    ]

    if list(df.columns[:len(expected_fields)]) != expected_fields:
        return render_template('error/400.html', error='Excel表头不符合预期')

    # 遍历每一行数据
    for _, row in df.iterrows():
        row_data = row.to_dict()
        name = row_data.get("band")

        if not name or pd.isna(name):
            continue

        # 新增连锁品牌
        filtered_data = {
            k: v for k, v in row_data.items() if pd.notna(v) and str(v).strip() != ''
        }
        chain_band = ChainBandModel(**filtered_data)
        db.session.add(chain_band)

    db.session.commit()
    flash('导入完成')
    return index()


