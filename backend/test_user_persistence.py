#!/usr/bin/env python3
"""
测试用户注册的持久化
"""
import requests
import time
import json


def test_user_persistence():
    base_url = "http://localhost:5000"

    # 生成唯一用户名
    timestamp = int(time.time())
    username = f"test_user_{timestamp}"

    print("🧪 测试用户注册持久化...")

    # 1. 注册用户
    print(f"1. 注册用户: {username}")
    reg_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "test123"
    }

    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=reg_data,
            timeout=5
        )

        if response.status_code == 201:
            token = response.json().get('access_token')
            print("✅ 注册请求成功")
        else:
            print(f"❌ 注册失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

    # 2. 立即登录验证
    print("2. 立即登录验证")
    try:
        login_data = {
            "username": username,
            "password": "test123"
        }

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            timeout=5
        )

        if response.status_code == 200:
            print("✅ 登录成功 - 用户已持久化")
        else:
            print("❌ 登录失败 - 用户可能未保存到数据库")
            return False
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return False

    # 3. 重启应用后测试持久化（需要手动测试）
    print("\n💡 要测试完整持久化，需要：")
    print("   - 重启Flask应用")
    print("   - 再次尝试登录")
    print("   - 如果还能登录，说明数据真正持久化")

    return True


if __name__ == "__main__":
    test_user_persistence()