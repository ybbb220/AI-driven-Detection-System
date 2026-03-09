from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from utils.database import db
from utils.auth import validate_username_format, validate_email_format, validate_password_strength

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': '用户名、邮箱和密码是必填项'}), 400

        # 验证用户名格式
        is_valid_username, username_msg = validate_username_format(data['username'])
        if not is_valid_username:
            return jsonify({'error': f'用户名格式错误: {username_msg}'}), 400

        # 验证邮箱格式
        if not validate_email_format(data['email']):
            return jsonify({'error': '邮箱格式不正确'}), 400

        # 验证密码强度
        is_valid_password, password_msg = validate_password_strength(data['password'])
        if not is_valid_password:
            return jsonify({'error': f'密码强度不足: {password_msg}'}), 400

        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已被注册'}), 400

        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # 生成访问令牌
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': '注册成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败: ' + str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码是必填项'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': '用户名或密码错误'}), 401

        # 生成访问令牌
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': '登录失败: ' + str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': '获取用户信息失败: ' + str(e)}), 500