# 请注意！SwaggerUI目前无法使用！原因不明！（可能是装饰器的问题）
# 查询API接口请自行分析代码或者等待总结（总结文档可能过时，如果可以的话还是自行阅读代码比较好）
import os
from flask import Flask, jsonify
from flask_wtf import CSRFProtect
from flask_mail import Mail
from models import db
from routes import auth, emergency_plan, incident, security_check, user, event_type, summary, message
from config import Config
from version import version
# from flasgger import Swagger

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)
mail = Mail(app)
# Swagger(app)

# 注册蓝图
app.register_blueprint(auth)
app.register_blueprint(emergency_plan)
app.register_blueprint(incident)
app.register_blueprint(security_check)
app.register_blueprint(user)
app.register_blueprint(event_type)
app.register_blueprint(summary)
app.register_blueprint(message)


# OpenAPI 全局信息
"""
openapi: 3.0.0
info:
  title: 民航应急响应平台 API
  version: 1.0.0
  description: |
    民航应急响应平台 API 文档。
    此文档描述了平台的所有 API 接口。

    ## 核心概念

    *   **用户 (User):**  系统中的用户，具有不同的角色和权限。
    *   **事件 (Incident):**  需要应急响应的事件。
    *   **应急预案 (Emergency Plan):**  针对不同事件类型的应急响应预案。
    *   **安全检查 (Security Check):**  定期进行的安全检查记录。
    *   **事件总结 (Summary):** 事件处理后的总结报告。
    *   **消息 (Message):** 系统内用户之间的消息通知。
    * **事件类型 (EventType):**  事件的分类.

    ## 角色与权限

    *   **-1:  管理员 (Admin):** 拥有最高权限，可以管理所有资源。
    *   **0: 领导小组 (Leadership Team):**  负责重大事件的决策和指挥。
    *   **1: 指挥中心 (Command Center):**  负责事件的协调和处理。
    *   **2: 部门领导 (Department Head):**  负责本部门事件的审批。
    *   **3: 安全管理员/普通用户 (Security Admin/Normal User):**  可以提交事件、创建事件总结等。

    ## 登录认证 
    所有的API请求均需要登录认证,请在获取到token后填入`Authorization`中.

    ## 数据安全
    部分敏感数据采用了SM4加密存储，涉及字段已在文档中注明。
    *   **Incident.incident_info**: 事件详细信息, 采用SM4加密存储.
    *   **Summary.content**:   事件总结内容,  采用SM4加密存储.

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT  # 指示使用 JWT

security:
  - bearerAuth: []
"""

@app.route('/')
def index():
    """
    openapi:
      summary: 获取欢迎信息
      description: 返回平台的欢迎消息。
      responses:
        '200':
          description: 成功返回欢迎消息
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: 欢迎消息
                    example: 欢迎使用应急响应平台!
    """
    return jsonify({'欢迎使用应急响应平台!' '当前版本': version.VERSION})

if __name__ == '__main__':
    # 生产环境必须关闭Debug模式！
    app.run(host='0.0.0.0', port=5000, debug=True)