"""
测试 Gemini API 调用
运行: python test_gemini_api.py
"""
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.llm_service import llm_service

def test_simple_text():
    """测试简单文本生成"""
    print("=" * 50)
    print("测试 1: 简单文本生成")
    print("=" * 50)

    try:
        prompt = "请用一句话介绍什么是机器学习。"
        print(f"Prompt: {prompt}")
        print("正在调用 API...")

        result = llm_service.generate_text(prompt, temperature=0.7)
        print(f"✅ 成功！响应:\n{result}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_generation():
    """测试 JSON 生成"""
    print("\n" + "=" * 50)
    print("测试 2: JSON 生成")
    print("=" * 50)

    try:
        prompt = """请返回一个 JSON 对象，包含以下字段：
- title: 一个简短的标题
- summary: 一句话总结

只返回 JSON，不要其他内容。"""
        print(f"Prompt: {prompt}")
        print("正在调用 API...")

        result = llm_service.generate_json(prompt, temperature=0.3)
        print(f"✅ 成功！响应:\n{result}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试 Gemini API 调用...\n")

    test1 = test_simple_text()
    test2 = test_json_generation()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"简单文本生成: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"JSON 生成: {'✅ 通过' if test2 else '❌ 失败'}")

    if test1 and test2:
        print("\n🎉 所有测试通过！Gemini API 调用正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
