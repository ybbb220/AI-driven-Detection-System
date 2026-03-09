from flask import Blueprint, request, jsonify, current_app  # 【修改】导入 current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.analysis import AnalysisRecord
from models.user import User
from utils.database import db
import time
import re
from datetime import datetime

# 【核心修改】移除下面这行导致循环导入的代码：
# from app import ai_text_detector

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required(optional=True)
def analyze_text():
    try:
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({'error': '文本内容是必填项'}), 400

        text = data['text'].strip()
        if len(text) < 10:
            return jsonify({'error': '文本内容太短，至少需要10个字符'}), 400

        if len(text) > 10000:
            return jsonify({'error': '文本内容过长，最多支持10000个字符'}), 400

        # 【关键修改】：如果有 Token，返回 ID；没有（匿名），返回 None
        identity = get_jwt_identity()
        # 如果令牌中存放的是用户名而不是数字 id，需要查库转换
        if identity is None:
            user_id = None
        else:
            try:
                user_id = int(identity)
            except ValueError:
                # 假设是 username
                user_obj = User.query.filter_by(username=identity).first()
                user_id = user_obj.id if user_obj else None
        start_time = time.time()

        result = current_app.ai_text_detector.detect(text)
        analysis_time = time.time() - start_time

        # 保存分析记录到数据库
        # DEBUG: 输出 user_id 和 identity
        current_app.logger.debug(f"analyze_text user_id resolved to {user_id} (identity was {identity})")
        analysis = AnalysisRecord(
            user_id=user_id,
            original_text=text,
            ai_probability=result['ai_probability'],
            human_probability=result['human_probability'],
            sentence_analysis=result['sentence_analysis'],
            analysis_time=analysis_time
        )

        db.session.add(analysis)
        db.session.commit()

        return jsonify({
            'message': '分析完成',
            'analysis_id': analysis.id,
            'result': result,
            'analysis_time': round(analysis_time, 3)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '分析失败: ' + str(e)}), 500


@analysis_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    try:
        identity = get_jwt_identity()
        # resolve to numeric id if necessary
        if identity is None:
            return jsonify({'analyses': [], 'total': 0, 'pages': 0, 'current_page': 1}), 200
        try:
            user_id = int(identity)
        except ValueError:
            user_obj = User.query.filter_by(username=identity).first()
            user_id = user_obj.id if user_obj else None
        current_app.logger.debug(f"get_analysis_history for user_id {user_id} (identity {identity})")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 获取用户的分析历史
        analyses = AnalysisRecord.query.filter_by(user_id=user_id) \
            .order_by(AnalysisRecord.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page
        }), 200

    except Exception as e:
        return jsonify({'error': '获取分析历史失败: ' + str(e)}), 500


@analysis_bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required(optional=True)  # 允许无 Token 访问
def get_analysis_detail(analysis_id):
    try:
        current_user_id = get_jwt_identity()

        # 先不带 user_id 查出记录
        analysis = AnalysisRecord.query.filter_by(id=analysis_id).first()

        if not analysis:
            return jsonify({'error': '分析记录不存在'}), 404

        # 【核心权限校验】
        # 如果这条记录有主人 (user_id 不为空)，且当前访问者不是主人，则拒绝访问
        if analysis.user_id is not None and str(analysis.user_id) != str(current_user_id):
            return jsonify({'error': '无权查看此分析记录'}), 403

        # 如果记录是匿名的 (user_id 为空)，或者当前访问者就是主人，则允许放行
        return jsonify({
            'result': analysis.to_dict()  # 兼容前端的 result 字段
        }), 200

    except Exception as e:
        return jsonify({'error': '获取分析详情失败: ' + str(e)}), 500


@analysis_bp.route('/history/<username>', methods=['GET'])
@jwt_required()
def get_user_history(username):
    try:
        current_user_id = get_jwt_identity()

        # 查找目标用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 权限检查：只能查看自己的历史
        if user.id != current_user_id:
            return jsonify({'error': '无权查看他人历史记录'}), 403

        # 获取该用户的所有分析记录，按时间倒序
        analyses = AnalysisRecord.query.filter_by(user_id=user.id) \
            .order_by(AnalysisRecord.created_at.desc()) \
            .all()

        # 返回前端期望的格式：数组，每个元素有 text 和 result
        return jsonify([{
            'text': analysis.original_text,
            'result': analysis.ai_probability > 0.5  # 假设 result 为布尔值：AI概率>0.5则为True
        } for analysis in analyses]), 200

    except Exception as e:
        return jsonify({'error': '获取历史记录失败: ' + str(e)}), 500