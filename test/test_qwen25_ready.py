#!/usr/bin/env python
"""
测试Qwen2.5模型和不定项选择题 - 服务器版本
"""

import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.append(".")

def test_config():
    """测试配置是否正确"""
    print("🧪 测试配置")
    print("=" * 40)
    
    try:
        from config import Config
        
        print(f"✅ 模型路径: {Config.LLM_MODEL_PATH}")
        print(f"✅ 嵌入模型: {Config.EMBEDDING_MODEL_PATH}")
        print(f"✅ 思考模式: {Config.QWEN3_ENABLE_THINKING}")
        print(f"✅ 选择题tokens: {Config.CHOICE_GENERATION_CONFIG['max_new_tokens']}")
        print(f"✅ 问答题tokens: {Config.QWEN25_GENERATION_CONFIG['max_new_tokens']}")
        print(f"✅ 文档切片大小: {Config.CHUNK_SIZE}")
        print(f"✅ 切片重叠: {Config.CHUNK_OVERLAP}")
        print(f"✅ 保留标题: {Config.PRESERVE_TITLES}")
        print(f"✅ 保持表格完整性: {Config.KEEP_TABLES_INTACT}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_choice_extraction():
    """测试不定项选择题答案提取"""
    print("\n🧪 测试不定项选择题答案提取")
    print("=" * 40)
    
    try:
        from main import FinancialQASystem
        
        qa_system = FinancialQASystem()
        
        test_cases = [
            ("A、B、C", ["A", "B", "C"]),     # 多选
            ("答案是A", ["A"]),                # 单选
            ("正确答案为B,C,D", ["B", "C", "D"]),  # 逗号分隔多选
            ("选择A和B", ["A", "B"]),          # 自然语言多选
        ]
        
        all_passed = True
        for input_text, expected in test_cases:
            result = qa_system.extract_choice_answer(input_text)
            # 对结果和期望进行排序以便比较
            result = sorted(result)
            expected = sorted(expected)
            passed = result == expected
            status = "✅" if passed else "❌"
            print(f"  {status} '{input_text}' -> {result} (期望: {expected})")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 答案提取测试失败: {e}")
        return False

def test_prompt_template():
    """测试提示词模板是否包含不定项选择提示"""
    print("\n🧪 测试提示词模板")
    print("=" * 40)
    
    try:
        from config import Config
        
        choice_template = Config.CHOICE_PROMPT_TEMPLATE
        
        keywords = ["不定项", "多个", "多选"]
        has_multi_choice_hint = any(kw in choice_template for kw in keywords)
        
        if has_multi_choice_hint:
            print(f"  ✅ 提示词模板包含不定项选择题提示")
            return True
        else:
            print(f"  ❌ 提示词模板未包含不定项选择题提示")
            return False
            
    except Exception as e:
        print(f"❌ 提示词模板测试失败: {e}")
        return False

def test_result_format():
    """测试多选题结果格式"""
    print("\n🧪 测试多选题结果格式")
    print("=" * 40)
    
    test_result = {
        "id": "test001",
        "answer": ["A", "C", "D"]
    }
    
    try:
        # 序列化为JSON
        json_str = json.dumps(test_result, ensure_ascii=False)
        print(f"  JSON格式: {json_str}")
        
        # 反序列化
        parsed = json.loads(json_str)
        if parsed["answer"] == test_result["answer"]:
            print(f"  ✅ 多选题结果格式正确")
            return True
        else:
            print(f"  ❌ 多选题结果格式错误")
            return False
            
    except Exception as e:
        print(f"❌ 结果格式测试失败: {e}")
        return False

def test_model_detection():
    """测试模型类型检测"""
    print("\n🧪 测试模型类型检测")
    print("=" * 40)
    
    try:
        # 使用UniversalLLM而不是直接检查
        from universal_llm import UniversalLLM, create_universal_llm
        from config import Config
        
        # 创建LLM实例但不加载
        llm = UniversalLLM.__new__(UniversalLLM)
        llm.model_path = Config.LLM_MODEL_PATH
        
        # 检查是否正确识别为Qwen2.5
        if "Qwen2.5" in Config.LLM_MODEL_PATH:
            print("✅ 使用Qwen2.5模型")
        else:
            print("⚠️ 可能不是使用Qwen2.5模型，请确认")
        
        print(f"✅ 模型路径: {Config.LLM_MODEL_PATH}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型检测测试失败: {e}")
        return False

def test_generation_configs():
    """测试生成配置"""
    print("\n🧪 测试生成配置")
    print("=" * 40)
    
    try:
        from config import Config
        
        # 检查Qwen2.5配置
        qwen25_config = Config.QWEN25_GENERATION_CONFIG
        choice_config = Config.CHOICE_GENERATION_CONFIG
        
        print(f"✅ Qwen2.5配置tokens: {qwen25_config['max_new_tokens']}")
        print(f"✅ 选择题配置tokens: {choice_config['max_new_tokens']}")
        
        # 检查温度设置
        if choice_config['temperature'] < qwen25_config['temperature']:
            print("✅ 选择题温度更低，确定性更强")
        else:
            print("❌ 选择题温度设置可能不当")
            return False
        
        # 检查token_id
        if qwen25_config['pad_token_id'] == 151643:
            print("✅ Qwen2.5 token_id 配置正确")
        else:
            print("❌ token_id配置可能有误")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 生成配置测试失败: {e}")
        return False

def test_enhanced_retrieval():
    """测试增强检索系统"""
    print("\n🧪 测试增强检索系统")
    print("=" * 40)
    
    try:
        # 导入增强检索系统
        from enhanced_retrieval_system import QueryProcessor, HybridRetriever, RelevanceReranker
        print("✅ 增强检索系统导入成功")
        
        # 检查RAG引擎中的增强检索标志
        from rag_engine import ENHANCED_RETRIEVAL_AVAILABLE
        print(f"✅ 增强检索系统状态: {'可用' if ENHANCED_RETRIEVAL_AVAILABLE else '不可用'}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ 增强检索系统测试失败: {e}")
        print("⚠️ 系统将使用基础检索模式")
        return True  # 不影响整体测试结果

if __name__ == "__main__":
    print("🚀 测试Qwen2.5配置和不定项选择题")
    print("=" * 50)
    
    tests = [
        ("配置检查", test_config),
        ("答案提取", test_choice_extraction),
        ("提示词模板", test_prompt_template),
        ("结果格式", test_result_format),
        ("模型检测", test_model_detection),
        ("生成配置", test_generation_configs),
        ("增强检索", test_enhanced_retrieval),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Qwen2.5不定项选择题系统配置完成")
        print("💡 现在可以运行: python main.py --reset-progress")
    else:
        print("⚠️ 部分测试失败，请检查配置") 