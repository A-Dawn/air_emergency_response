# routes/user.py
from flask import Blueprint, request, jsonify, current_app, render_template_string, url_for
from models import db, User
from utils.jwt_utils import generate_jwt_token, decode_jwt_token, token_required, role_required # 导入之前编写的文件
from utils.sm_utils import encrypt_sm3, generate_salt # 导入加密函数
from utils.email import send_email  # 导入邮件发送函数
from forms import RegistrationForm, CreateUserForm,ResetPasswordRequestForm, ResetPasswordForm, UpdateUserForm # 导入表单
from itsdangerous import URLSafeTimedSerializer as Serializer # 用于生成用户token
from itsdangerous import BadSignature, SignatureExpired # 用于处理异常情况

user = Blueprint('user', __name__)

"""
tags:
  - 用户管理
"""
# 用户注册路由
@user.route('/register', methods=['POST'])
def register():
    """
    openapi:
      summary: 用户注册
      description: 用户注册接口，创建新用户。
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: 用户名
                email:
                  type: string
                  format: email
                  description: 邮箱
                password:
                  type: string
                  description: 密码
                confirm_password:
                  type: string
                  description: 确认密码
              required:
                - username
                - email
                - password
                - confirm_password
      responses:
        '201':
          description: 注册成功
        '400':
          description: 表单验证失败
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # 生成盐值
        salt = generate_salt()
        # 使用 SM3 算法对密码进行哈希 (加盐)
        hashed_password = encrypt_sm3(form.password.data, salt)

        new_user = User(username=form.username.data, email=form.email.data, hashed_password=hashed_password,
        salt=salt, role_level=3)  # 默认⻆⾊级别为 3
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '注册成功!'}), 201
    return jsonify({'message': '表单验证失败!', 'errors': form.errors}), 400

"""
tags:
  - 用户管理
"""
# 创建用户 (仅管理员)
@user.route('/users', methods=['POST'])
@token_required
@role_required([-1]) # 只有管理员才能访问
def create_user(current_user):
    """
    openapi:
      summary: 创建用户 (管理员)
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: 用户创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        example: "用户创建成功!"
        '400':
          description: 表单验证失败
        '401':
          description: 未授权
        '403':
            description: "权限不足"
    """
    form = CreateUserForm()
    if form.validate_on_submit():
        #  生成盐值
        salt = generate_salt()
        # 使用 SM3 算法对密码进行哈希 (加盐)
        hashed_password = encrypt_sm3(form.password.data, salt)
        new_user = User(username=form.username.data, email=form.email.data,
        hashed_password=hashed_password, salt=salt, role_level=form.role_level.data)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '用户创建成功!'}), 201
    return jsonify({'message': '表单验证失败!', 'errors': form.errors}), 400

"""
tags:
  - 用户管理
"""
# 获取所有用户 (仅管理员)
@user.route('/users', methods=['GET'])
@token_required
@role_required([-1]) #  只有管理员才能访问
def get_all_users(current_user):
    """
    openapi:
      summary: 获取所有用户 (管理员)
      security:
        - bearerAuth: []
      responses:
        '200':
          description: 成功返回所有用户信息
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
        '401':
          description: 未授权
        '403':
            description: "权限不足"

    """
    users = User.query.all()
    users_list = []
    for user in users:
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role_level': user.role_level,
            'is_active': user.is_active
        }
        users_list.append(user_data)
    return jsonify(users_list), 200

"""
tags:
  - 用户管理
"""
# 获取单个用户信息
@user.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """
    openapi:
      summary: 获取单个用户信息
      security:
        - bearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          description: 用户ID
          schema:
            type: integer
      responses:
        '200':
          description: 成功返回用户信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: 未授权
        '403':
            description: "权限不足"
        '404':
          description: 用户不存在
    """
    # 管理员可以查看所有用户， 普通用户只能查看自己的信息
    if current_user.role_level != -1 and current_user.user_id != user_id:
        return jsonify({'message': '权限不足!'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在!'}), 404

    user_data = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role_level': user.role_level,
        'is_active': user.is_active
    }
    return jsonify(user_data), 200

"""
tags:
  - 用户管理
"""
# 更新用户信息
@user.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    openapi:
      summary: 更新用户信息
      security:
        - bearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          description: 用户 ID
          schema:
            type: integer
      requestBody:
            description: 更新的用户信息
            content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/User'
      responses:
        '200':
            description: "更新成功"
        '400':
            description: "数据不合法"
        '401':
          description: 未授权
        '403':
          description: 无权限操作
        '404':
          description: 用户不存在!
    """
    form = UpdateUserForm() # 获取表单信息
    # 只有管理员 可以修改 他人信息 或用户自己 才能修改
    if current_user.role_level != -1 and current_user.user_id != user_id:
        return jsonify({'message': '无权限操作!'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在!'}), 404
    #表单验证
    if form.validate_on_submit():
        # 更新数据
      user.username = form.username.data
      user.email = form.email.data
      user.role_level = form.role_level.data
      db.session.commit()
      return jsonify({'message':'更新成功'}),200
   #表单验证失败
    return jsonify({'message':"表单验证失败",'error': form.errors}),400

"""
tags:
  - 用户管理
"""
# 删除用户 (管理员，逻辑删除)
@user.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required([-1]) # 只有管理员才能访问
def delete_user(current_user, user_id):
    """
    openapi:
      summary: 删除用户 (管理员)
      security:
        - bearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          description: 用户ID
          schema:
            type: integer
      responses:
        '200':
          description: 删除成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 删除成功
        '401':
          description: 未授权
        '403':
          description: 无权限操作
        '404':
          description: 用户不存在
    """
    # 管理员才能删除
    if current_user.role_level != -1:
        return jsonify({'message': '无权限操作!'}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在!'}), 404
    # 逻辑删除
    user.is_active = False
    db.session.commit()
    return jsonify({'message': '删除成功'}), 200
"""
tags:
  - 用户管理
"""
# 发送密码重置邮件
@user.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    """
    openapi:
      summary: 发送密码重置邮件
      description: 发送密码重置邮件到指定邮箱。
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                  description: 用户邮箱
              required:
                - email
      responses:
        '200':
          description: 密码重置邮件已发送，请查收!
        '400':
            description: "邮箱不正确"
    """
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # 生成密码重置令牌
            s = Serializer(current_app.config['SECRET_KEY'])
            token = s.dumps({'user_id': user.user_id}).decode('utf-8')

            # 构建密码重置链接
            reset_url = url_for('user.reset_password', token=token, _external=True)

            # 发送邮件(可以自定义邮件内容)
            html = render_template_string('''
                <p>尊敬的 {{ user.username }},</p>
                <p>您请求重置密码， 请点击以下链接重置您的密码：</p>
                <p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
                <p>如果不是您本人操作， 请忽略此邮件。</p>
                <p>民航通用应急响应平台</p>''', user=user, reset_url=reset_url)
                # 发送密码重置链接
            send_email(user.email, '密码重置', html)
            return jsonify({'message': '密码重置邮件已发送， 请查收!'}), 200
    return jsonify({'message': '邮箱不正确!', 'error': form.errors}), 400
"""
tags:
  - 用户管理
"""
# 密码重置
@user.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    """
      openapi:
        summary: 重置用户密码
        description: 通过密码重置链接重置用户密码
        parameters:
          - in: path
            name: token
            schema:
              type: string
            required: true
            description: 密码重置token
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  password:
                    type: string
                    description: 新密码
                  confirm_password:
                    type: string
                    description: 确认新密码
        responses:
          '200':
            description: 密码已成功重置!
            content:
              application/json:
                schema:
                  type: object
                  properties:
                      message:
                        type: string
                        example: "密码已成功重置!"
          '400':
            description: 密码重置失败
            content:
              application/json:
                schema:
                  type: object
                  properties:
                      message:
                        type: string
                        example: "密码重置失败"

    """
    form = ResetPasswordForm() # 获取表单类
    s = Serializer(current_app.config['SECRET_KEY']) # 用于校验token
    # 判断form表单是否提交 并且数据是否符合要求
    if form.validate_on_submit():
        try:
            # 尝试解密
            data = s.loads(token.encode('utf-8'))
        except SignatureExpired:
          return jsonify({'message': 'Token已过期'}), 400
        except BadSignature:
          return jsonify({'message': '无效Token'}), 400
        # 获取user
        user = User.query.get(data['user_id'])
        if user is None:
            return jsonify({'message': '无效token'}),400
        # 生成盐值
        salt = generate_salt()
        # 使用 SM3 算法对密码进行哈希 (加盐)
        hashed_password = encrypt_sm3(form.password.data, salt)
        # 更新密码和盐值字段
        user.hashed_password = hashed_password
        user.salt = salt
        db.session.commit()
        return jsonify({'message': '密码已成功重置!'}), 200
    return jsonify({'message': '密码重置失败', 'error': form.errors}), 400