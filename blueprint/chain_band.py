from flask import Blueprint, render_template, request
from sqlalchemy import Column, Integer
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
    name = db.Column(db.String(500))
    area = db.Column(db.String(500))
    company_name = db.Column(db.String(500))
    remark = db.Column(db.String(500))


class ChainBandForm(FlaskForm):
    # id = Column(Integer, primary_key=True)
    id = HiddenField()
    name = StringField('连锁品牌名称', render_kw={'placeholder': '请输入连锁品牌名称'}, validators=[DataRequired()])
    company_name = StringField('连锁店铺名称', render_kw={'placeholder': '请输入连锁店铺名称'})
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
        chanBandForm.name.data = chanBand.name
        chanBandForm.company_name.data = chanBand.company_name
        return render_template('chain_band/update.html', form=chanBandForm)
    else:
        if chanBandForm.validate_on_submit():
            data = chanBandForm.data
            # chanBandModel = ChainBandModel(name=data['name'], company_name=data['company_name'])
            chanBand = ChainBandModel.query.get(data['id'])
            chanBand.name = data['name']
            chanBand.company_name = data['company_name']
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


