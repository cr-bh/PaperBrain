"""
高级豆包 API 测试脚本
尝试不同的配置来找到问题根源
"""
import sys
import os
import requests
import ssl
import urllib3
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def test_with_ssl_verification_disabled():
    """测试：禁用 SSL 验证"""
    print("\n" + "="*60)
    print("测试1: 禁用 SSL 验证")
    print("="*60)

    headers = {
        "Authorization": f"Bearer {config.DOUBAO_BEARER_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "model": "Doubao-pro-128k",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 50
    }

    try:
        import json
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        # 禁用 SSL 警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.post(
            config.DOUBAO_API_URL,
            headers=headers,
            data=json_data,
            timeout=30,
            verify=False  # 禁用 SSL 验证
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            print("✅ 禁用 SSL 验证后调用成功！")
            return True
        else:
            print(f"❌ 调用失败，状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 仍然失败: {e}")
        return False


def test_with_different_headers():
    """测试：尝试不同的请求头"""
    print("\n" + "="*60)
    print("测试2: 尝试不同的请求头格式")
    print("="*60)

    # 尝试不同的 Header 组合
    header_variants = [
        {
            "Authorization": f"Bearer {config.DOUBAO_BEARER_TOKEN}",
            "Content-Type": "application/json"
        },
        {
            "Authorization": f"Bearer {config.DOUBAO_BEARER_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json"
        },
        {
            "Authorization": config.DOUBAO_BEARER_TOKEN,  # 不加 Bearer 前缀
            "Content-Type": "application/json"
        },
        {
            "token": config.DOUBAO_BEARER_TOKEN,  # 使用 token 字段
            "Content-Type": "application/json"
        }
    ]

    payload = {
        "model": "Doubao-pro-128k",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 50
    }

    import json
    json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    for i, headers in enumerate(header_variants, 1):
        print(f"\n尝试 Header 变体 {i}: {list(headers.keys())}")
        try:
            response = requests.post(
                config.DOUBAO_API_URL,
                headers=headers,
                data=json_data,
                timeout=30,
                verify=False
            )
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 成功！使用这个 Header 格式")
                return True, headers
        except Exception as e:
            print(f"  ❌ 失败: {str(e)[:100]}")

    return False, None


def test_with_session():
    """测试：使用 Session 对象"""
    print("\n" + "="*60)
    print("测试3: 使用 requests.Session")
    print("="*60)

    session = requests.Session()
    session.verify = False

    # 设置 SSL 适配器
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context

    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            context = create_urllib3_context()
            context.set_ciphers('DEFAULT@SECLEVEL=1')
            kwargs['ssl_context'] = context
            return super().init_poolmanager(*args, **kwargs)

    session.mount('https://', SSLAdapter())

    headers = {
        "Authorization": f"Bearer {config.DOUBAO_BEARER_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "model": "Doubao-pro-128k",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 50
    }

    try:
        import json
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = session.post(
            config.DOUBAO_API_URL,
            headers=headers,
            data=json_data,
            timeout=30
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            print("✅ 使用 Session 调用成功！")
            return True
        else:
            print(f"❌ 调用失败，状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        print(traceback.format_exc()[:1000])
        return False


def test_curl_command():
    """生成 curl 命令供手动测试"""
    print("\n" + "="*60)
    print("测试4: 生成 curl 命令")
    print("="*60)

    import json
    payload = {
        "model": "Doubao-pro-128k",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 50
    }

    curl_cmd = f"""curl -X POST '{config.DOUBAO_API_URL}' \\
  -H 'Authorization: Bearer {config.DOUBAO_BEARER_TOKEN}' \\
  -H 'Content-Type: application/json; charset=utf-8' \\
  -d '{json.dumps(payload, ensure_ascii=False)}'
"""

    print("请在终端中手动执行以下命令测试：")
    print(curl_cmd)
    print("\n如果 curl 命令成功，说明是 Python requests 库的配置问题")


def check_environment():
    """检查环境信息"""
    print("\n" + "="*60)
    print("环境信息")
    print("="*60)

    import platform
    print(f"Python 版本: {platform.python_version()}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"requests 版本: {requests.__version__}")
    print(f"urllib3 版本: {urllib3.__version__}")

    import ssl
    print(f"OpenSSL 版本: {ssl.OPENSSL_VERSION}")
    print(f"支持的 TLS 版本: {ssl.HAS_TLSv1_3}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("豆包 API 高级诊断测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    check_environment()

    results = {}

    # 测试1: 禁用 SSL 验证
    results['禁用SSL验证'] = test_with_ssl_verification_disabled()

    # 测试2: 不同的 Header
    success, headers = test_with_different_headers()
    results['不同Header'] = success

    # 测试3: 使用 Session
    results['使用Session'] = test_with_session()

    # 测试4: 生成 curl 命令
    test_curl_command()

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    if any(results.values()):
        print("\n✅ 找到了可行的解决方案！")
    else:
        print("\n⚠️  所有测试都失败了，可能需要检查：")
        print("  1. Bearer Token 是否正确")
        print("  2. API URL 是否正确")
        print("  3. 是否需要额外的认证参数")
        print("  4. 联系豆包 API 技术支持")


if __name__ == "__main__":
    main()
