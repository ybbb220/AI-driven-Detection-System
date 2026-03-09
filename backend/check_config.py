# check_config_fixed.py
# !/usr/bin/env python3
"""
修复编码问题的配置检查脚本
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("🔍 当前环境配置检查")
print("=" * 50)


def read_file_safely(filepath):
    """安全读取文件，尝试多种编码"""
    encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ 使用 {encoding} 编码成功读取文件")
            return content
        except UnicodeDecodeError:
            continue

    # 如果所有编码都失败，使用错误忽略模式
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print("⚠️  使用错误忽略模式读取文件（可能丢失部分字符）")
        return content
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")
        return None


# 检查.env文件
env_file = '.env'
if os.path.exists(env_file):
    print(f"📁 .env文件存在: {os.path.abspath(env_file)}")

    content = read_file_safely(env_file)
    if content:
        # 隐藏敏感信息显示
        sensitive_keys = ['PASSWORD', 'SECRET', 'KEY']
        lines = content.split('\n')
        safe_lines = []

        for line in lines:
            safe_line = line
            for key in sensitive_keys:
                if key in line.upper() and '=' in line:
                    # 隐藏密码值
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        value = parts[1].strip()
                        if value and not value.startswith('#'):
                            safe_line = f"{parts[0]}=***隐藏***"
            safe_lines.append(safe_line)

        safe_content = '\n'.join(safe_lines)
        print("环境变量内容:")
        print(safe_content)
else:
    print("❌ .env文件不存在")

print("\n📊 当前环境变量值:")
vars_to_check = [
    'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD',
    'MYSQL_DB', 'MYSQL_PORT', 'FLASK_ENV', 'DEBUG'
]

for var in vars_to_check:
    value = os.getenv(var, '未设置')
    # 隐藏密码显示
    if 'PASSWORD' in var and value != '未设置':
        value = '***' + value[-3:] if len(value) > 3 else '***'
    elif 'SECRET' in var and value != '未设置':
        value = '***' + value[-6:] if len(value) > 6 else '***'
    print(f"  {var}: {value}")

# 检查SQLite数据库文件
print("\n🔎 检查SQLite数据库文件:")
sqlite_files = [
    'dev_ai_detector.db',
    'instance/app.db',
    'app.db',
    'ai_detector.db'
]

for file in sqlite_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"✅ 找到SQLite文件: {file} ({size} bytes)")
    else:
        print(f"❌ 未找到: {file}")

print("\n" + "=" * 50)
print("检查完成!")