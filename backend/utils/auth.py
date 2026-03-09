from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User
import re


def admin_required(f):
    """需要管理员权限的装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # 这里可以添加管理员权限检查逻辑
            # 暂时先保留这个装饰器结构，便于后续扩展

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': '权限验证失败: ' + str(e)}), 401

    return decorated_function


def validate_password_strength(password):
    """
    验证密码强度
    """
    if len(password) < 6:
        return False, '密码长度至少6位'

    if len(password) > 50:
        return False, '密码长度不能超过50位'

    return True, '密码强度符合要求'


def validate_email_format(email):
    """
    简单的邮箱格式验证
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username_format(username):
    """
    验证用户名格式
    """
    if len(username) < 3:
        return False, '用户名长度至少3位'

    if len(username) > 20:
        return False, '用户名长度不能超过20位'

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, '用户名只能包含字母、数字和下划线'

    return True, '用户名格式正确'