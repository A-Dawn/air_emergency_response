# /www/wwwroot/air_emergency_response/routes/incident.py
from flask import Blueprint, current_app, request, jsonify
from models.incident import Incident
from functools import wraps

from models.user import User
from utils.jwt_utils import decode_jwt_token
from models import db

incident = Blueprint('incident', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少Token!'}), 401
        user_id = decode_jwt_token(token, current_app.config['JWT_SECRET_KEY'])
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401
        current_user = User.query.filter_by(user_id=user_id).first()
        if not current_user:
            return jsonify({'message': '用户不存在!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@incident.route('/incidents', methods=['POST'])
@token_required
def create_incident(current_user):
    data = request.get_json()
    new_incident = Incident(
        incident_info=data['incident_info'],
        process_status=data['process_status'],
        response_log=data['response_log'],
        incident_level=data['incident_level'],
        assigned_resources=data.get('assigned_resources', '')
    )
    db.session.add(new_incident)
    db.session.commit()
    return jsonify({'message': '事件记录创建成功!'}), 201

@incident.route('/incidents/<int:incident_id>', methods=['GET'])
@token_required
def get_incident(current_user, incident_id):
    incident = Incident.query.filter_by(incident_id=incident_id).first()
    if not incident:
        return jsonify({'message': '事件记录不存在!'}), 404
    return jsonify({
        'incident_id': incident.incident_id,
        'incident_info': incident.incident_info,
        'process_status': incident.process_status,
        'response_log': incident.response_log,
        'incident_level': incident.incident_level,
        'assigned_resources': incident.assigned_resources,
        'update_time': incident.update_time.strftime('%Y-%m-%d %H:%M:%S')
    }), 200