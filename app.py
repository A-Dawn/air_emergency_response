import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from flask import Flask, jsonify
from models import db
from routes import auth, emergency_plan, incident, security_check, user
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # 从环境变量加载配置
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
   # with app.app_context():
   #     db.drop_all()
   #     db.create_all()  # 初始化数据库表（仅首次部署时运行）
   # # 生产环境必须关闭Debug模式！
    app.run(host='0.0.0.0', port=5000, debug=True)
