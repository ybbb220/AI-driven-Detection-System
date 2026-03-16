from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import get_config
from utils.database import db, init_db
from routes.auth import auth_bp
from routes.analysis import analysis_bp
import os
from dotenv import load_dotenv
from routes.ai_detector import AITextDetector

# 加载环境变量
load_dotenv()

print("正在加载AI文本检测模型...")
ai_text_detector = AITextDetector(model_path="./roberta_ai_text_classifier")
print("模型加载完成。")


def create_app():
    app = Flask(__name__)

    # 【核心修改】将全局的检测器实例挂载到当前的 app 实例上
    app.ai_text_detector = ai_text_detector

    # 根据环境加载配置
    config = get_config()
    app.config.from_object(config)

    # 初始化扩展
    CORS(app)
    jwt = JWTManager(app)
    init_db(app)

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'debug': app.config['DEBUG']
        })

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '接口不存在'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        if app.config['DEBUG']:
            return jsonify({'error': str(error)}), 500
        return jsonify({'error': '服务器内部错误'}), 500

    return app


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 直接从app.py启动
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']

    print(f"启动AI检测器应用在 {host}:{port}")
    print(f"环境: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"调试模式: {debug}")

    app.run(host=host, port=port, debug=debug)