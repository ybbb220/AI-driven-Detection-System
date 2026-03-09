import os
import urllib.parse
from datetime import timedelta


class Config:
    """基础配置类"""

    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # 服务器配置
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.getenv('PORT', 5000))

    # AI服务配置
    AI_API_KEY = os.getenv('AI_API_KEY')
    AI_API_URL = os.getenv('AI_API_URL')

    # 数据库配置 - 修改为常规属性
    SQLALCHEMY_DATABASE_URI = None  # 先设置为None，在初始化时设置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

    def __init__(self):
        """初始化配置，构建数据库URI"""
        self.SQLALCHEMY_DATABASE_URI = self._build_database_uri()

    def _build_database_uri(self):
        """构建数据库URI"""
        # 确保环境变量已加载
        from dotenv import load_dotenv
        load_dotenv()

        # 获取环境变量
        mysql_user = os.getenv('MYSQL_USER', 'root')
        mysql_password = os.getenv('MYSQL_PASSWORD', '')
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_db = os.getenv('MYSQL_DB', 'ai_detector')

        # 验证密码
        if not mysql_password:
            raise ValueError("MySQL密码未设置！请检查.env文件中的MYSQL_PASSWORD")

        # URL编码密码（处理特殊字符）
        encoded_password = urllib.parse.quote_plus(mysql_password)

        # 构建URI
        uri = f'mysql+mysqlconnector://{mysql_user}:{encoded_password}@{mysql_host}:{mysql_port}/{mysql_db}'

        # 添加连接参数
        params = "charset=utf8mb4&autocommit=true"
        full_uri = f'{uri}?{params}'

        print(f"🔧 构建的数据库URI: mysql+mysqlconnector://{mysql_user}:***@{mysql_host}:{mysql_port}/{mysql_db}")

        return full_uri


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True

    def _build_database_uri(self):
        """测试环境使用SQLite内存数据库"""
        return 'sqlite:///:memory:'

    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-required'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'production-jwt-secret-key-required'


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """根据环境变量获取配置实例"""
    env = os.environ.get('FLASK_ENV') or 'development'
    config_class = config.get(env, config['default'])
    return config_class()  # 返回配置类的实例