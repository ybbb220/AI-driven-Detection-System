# test_mysql_connection.py
# !/usr/bin/env python3
"""
测试MySQL连接
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def test_mysql_connection():
    print("🔌 测试MySQL连接...")
    print("=" * 50)

    # 获取配置
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'mysql'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }

    # 隐藏密码显示
    display_config = config.copy()
    display_config['password'] = '***' + (config['password'][-3:] if config['password'] else '')

    print("连接配置:")
    for key, value in display_config.items():
        print(f"  {key}: {value}")

    try:
        # 测试连接
        connection = pymysql.connect(**config)
        print("✅ MySQL连接成功!")

        # 检查数据库是否存在
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            print(f"📊 可用数据库: {databases}")

            target_db = os.getenv('MYSQL_DB', 'ai_detector')
            if target_db in databases:
                print(f"✅ 目标数据库 '{target_db}' 存在")
            else:
                print(f"❌ 目标数据库 '{target_db}' 不存在")
                print("💡 需要创建数据库")

        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]

        print(f"❌ MySQL连接失败: {error_msg}")

        # 常见错误处理建议
        if error_code == 1045:
            print("\n💡 解决方案: 密码错误或未设置")
            print("1. 检查 .env 文件中的 MYSQL_PASSWORD")
            print("2. 确保密码正确")
            print("3. 如果忘记密码，需要重置MySQL root密码")
        elif error_code == 2003:
            print("\n💡 解决方案: MySQL服务未运行")
            print("1. 启动MySQL服务")
            print("2. 检查防火墙设置")
        elif error_code == 1049:
            print("\n💡 解决方案: 数据库不存在")
            print("1. 创建数据库: CREATE DATABASE ai_detector;")
        else:
            print(f"💡 错误代码: {error_code}")

        return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False


def create_database_if_needed():
    """如果需要，创建数据库"""
    print("\n🗃️  检查并创建数据库...")

    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }

    target_db = os.getenv('MYSQL_DB', 'ai_detector')

    try:
        connection = pymysql.connect(**config)

        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]

            if target_db not in databases:
                print(f"📋 创建数据库: {target_db}")
                cursor.execute(f"CREATE DATABASE {target_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
                print(f"✅ 数据库 '{target_db}' 创建成功")
            else:
                print(f"✅ 数据库 '{target_db}' 已存在")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 MySQL连接测试工具")
    print("=" * 50)

    # 测试连接
    if test_mysql_connection():
        # 确保数据库存在
        create_database_if_needed()

        print("\n🎉 MySQL配置正确！现在可以启动应用了。")
    else:
        print("\n❌ 需要先解决MySQL连接问题")

    print("=" * 50)