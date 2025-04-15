from flask import Flask, request, render_template
from sqlalchemy import text

from blueprint.chain_store import chain_store_bp
from blueprint.hotel import hotel_bp
# from blueprint import business_park
from exts import db
from blueprint.questionaire import questionaire_bp
from blueprint.analysis import analysis_bp
from blueprint.business_park import business_park_bp
from blueprint.company import company_bp
from blueprint.chain_band import chain_band_bp

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:toor@localhost:3306/ecc_enhance_db?charset=utf8'
app.config.from_object('config')
app.config['SECRET_KEY'] = '1234567890'


db.init_app(app)

# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text('SELECT 1;'))
#         print(rs.fetchone())

app.register_blueprint(questionaire_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(business_park_bp)
app.register_blueprint(company_bp)
app.register_blueprint(hotel_bp)
app.register_blueprint(chain_band_bp)
app.register_blueprint(chain_store_bp)


with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    '''
    URL带参数
    :return:
    '''
    city = request.args.get('city')
    if city == "my":
        return f'Welcome to Mianyang'
    return render_template('index.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
