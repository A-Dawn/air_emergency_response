from flask import Flask
from models import db
from routes import auth, emergency_plan, incident, security_check, user
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth)
app.register_blueprint(emergency_plan)
app.register_blueprint(incident)
app.register_blueprint(security_check)
app.register_blueprint(user)

@app.route('/')
def index():
    return jsonify({'message': '欢迎使用应急响应平台!'})

if __name__ == '__main__':
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
    app.run(debug=True)