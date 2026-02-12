"""
测试豆包 API 配置和连接
用于诊断评分失败的根本原因
"""
import sys
import os
import socket
import requests
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def test_network_connectivity():
    """测试网络连接"""
    print("\n" + "="*60)
    print("1. 测试网络连接")
    print("="*60)

    host = "aigc.sankuai.com"
    port = 443

    try:
        print(f"尝试连接 {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ 成功连接到 {host}:{port}")
            return True
        else:
            print(f"❌ 无法连接到 {host}:{port}，错误码: {result}")
            return False
    except socket.gaierror as e:
        print(f"❌ DNS 解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_api_configuration():
    """测试 API 配置"""
    print("\n" + "="*60)
    print("2. 测试 API 配置")
    print("="*60)

    print(f"DOUBAO_API_URL: {config.DOUBAO_API_URL}")

    if config.DOUBAO_BEARER_TOKEN:
        token_preview = config.DOUBAO_BEARER_TOKEN[:20] + "..." if len(config.DOUBAO_BEARER_TOKEN) > 20 else config.DOUBAO_BEARER_TOKEN
        print(f"DOUBAO_BEARER_TOKEN: {token_preview} (长度: {len(config.DOUBAO_BEARER_TOKEN)})")
    else:
        print("❌ DOUBAO_BEARER_TOKEN 未配置")
        return False

    if not config.DOUBAO_API_URL:
        print("❌ DOUBAO_API_URL 未配置")
        return False

    print("✅ API 配置已设置")
    return True


def test_api_call():
    """测试 API 调用"""
    print("\n" + "="*60)
    print("3. 测试 API 调用")
    print("="*60)

    headers = {
        "Authorization": f"Bearer {config.DOUBAO_BEARER_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 简单的测试 payload
    payload = {
        "model": "Doubao-pro-128k",
        "messages": [
            {
                "role": "user",
                "content": "请用一句话介绍强化学习。"
            }
        ],
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 100
    }

    try:
        print(f"发送请求到: {config.DOUBAO_API_URL}")
        print(f"请求内容: {payload['messages'][0]['content']}")

        import json
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        response = requests.post(
            config.DOUBAO_API_URL,
            headers=headers,
            data=json_data,
            timeout=30
        )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")

            # 尝试提取内容
            try:
                content = result['choices'][0]['message']['content']
                print(f"\n✅ API 调用成功！")
                print(f"生成的内容: {content}")
                return True
            except (KeyError, IndexError) as e:
                print(f"❌ 响应格式不正确: {e}")
                print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return False
        else:
            print(f"❌ API 调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ 请求超时: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")
        return False


def test_doubao_service():
    """测试 DoubaoService 类"""
    print("\n" + "="*60)
    print("4. 测试 DoubaoService 类")
    print("="*60)

    try:
        from services.doubao_service import doubao_service

        print("尝试调用 doubao_service.generate_json()...")

        test_prompt = """请对以下论文进行评分（1-10分）并返回 JSON 格式：

标题: Deep Reinforcement Learning for Combinatorial Optimization
摘要: This paper presents a novel approach using deep reinforcement learning to solve combinatorial optimization problems.

返回格式：
{
    "score": 8.5,
    "reason": "该论文结合了深度强化学习和组合优化，具有创新性",
    "title_zh": "深度强化学习用于组合优化",
    "abstract_zh": "本文提出了一种使用深度强化学习解决组合优化问题的新方法。",
    "tags": ["强化学习", "组合优化"]
}
"""

        result = doubao_service.generate_json(test_prompt, temperature=0.3)

        print(f"\n✅ DoubaoService 调用成功！")
        print(f"返回结果: {result}")
        return True

    except Exception as e:
        print(f"❌ DoubaoService 调用失败: {e}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("豆包 API 诊断测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = {
        "网络连接": test_network_connectivity(),
        "API配置": test_api_configuration(),
        "API调用": test_api_call(),
        "DoubaoService": test_doubao_service()
    }

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过！豆包 API 配置正确。")
    else:
        print("\n⚠️  部分测试失败，请根据上述错误信息排查问题。")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
