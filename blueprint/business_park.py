from flask import Blueprint, render_template, request
from sqlalchemy import Column, Integer
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


