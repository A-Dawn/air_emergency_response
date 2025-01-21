from flask import Blueprint, request, jsonify
from models.emergency_plan import EmergencyPlan
from functools import wraps
from ... import db

emergency_plan = Blueprint('emergency_plan', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少Token!'}), 401
        user_id = decode_jwt_token(token, app.config['JWT_SECRET_KEY'])
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401
        current_user = User.query.filter_by(user_id=user_id).first()
        if not current_user:
            return jsonify({'message': '用户不存在!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@emergency_plan.route('/emergency-plans', methods=['POST'])
@token_required
def create_emergency_plan(current_user):
    data = request.get_json()
    new_plan = EmergencyPlan(plan_details=data['plan_details'], version=data['version'], status=data['status'])
    db.session.add(new_plan)
    db.session.commit()
    return jsonify({'message': '应急预案创建成功!'}), 201

@emergency_plan.route('/emergency-plans/<int:plan_id>', methods=['GET'])
@token_required
def get_emergency_plan(current_user, plan_id):
    plan = EmergencyPlan.query.filter_by(plan_id=plan_id).first()
    if not plan:
        return jsonify({'message': '应急预案不存在!'}), 404
    return jsonify({
        'plan_id': plan.plan_id,
        'plan_details': plan.plan_details,
        'version': plan.version,
        'status': plan.status
    }), 200