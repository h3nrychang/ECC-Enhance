from flask import Blueprint, render_template
from sqlalchemy.dialects.postgresql import JSON
from exts import db


# 创建问卷蓝图
questionaire_bp = Blueprint('questionaire', __name__, url_prefix='/q')

# class Questionaire:
#     def __init__(self, code, question):
#         self.code = code
#         self.question = question


class QuestionaireModel(db.Model):
    '''
    问卷列表模型
    '''
    __tablename__ = 'q_list'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area = db.Column(db.String(10))
    code = db.Column(db.String(10))
    questions = db.Column(JSON)


@questionaire_bp.route('/')
def index():
    return render_template('questionnaire/code.html')


@questionaire_bp.route("/<int:code>")
def find_questionaire(code):
    '''
    根据问卷的 code 搜索对应的问卷模板，返回该模板中的问题
    :param code: 问卷的 code
    :return: 问卷模板及其问题
    '''
    # 查询数据库，根据传入的 code 查找对应的问卷
    questionaire = QuestionaireModel.query.filter_by(code=code).first()

    # 如果找不到问卷，返回一个错误页面或信息
    if not questionaire:
        return "未找到，<analysis href='/questionnaire'>返回</analysis>", 404


    # 获取存储在 JSON 字段中的问题
    questions = questionaire.questions
    # print(f'typeof question: {type(questions)}')

    # for question in questions["questions"]:
    #     print(question)

    # 返回渲染页面，并将问卷和问题传递到模板
    return render_template('questionnaire/fill.html', q=questionaire, questions=questions)




