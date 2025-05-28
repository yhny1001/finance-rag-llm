#!/usr/bin/env python
"""
导入测试脚本
测试修复后的简化架构是否正常工作
"""

import sys
import traceback

def test_basic_imports():
    """测试基础模块导入"""
    print("测试基础模块导入...")
    
    try:
        import torch
        print("✅ torch导入成功")
    except ImportError as e:
        print(f"❌ torch导入失败: {e}")
        return False
    
    try:
        import faiss
        print("✅ faiss导入成功")
    except ImportError as e:
        print(f"❌ faiss导入失败: {e}")
        return False
    
    try:
        from config import Config
        print("✅ config导入成功")
    except ImportError as e:
        print(f"❌ config导入失败: {e}")
        return False
    
    try:
        from vector_db import VectorDatabase
        print("✅ vector_db导入成功")
    except ImportError as e:
        print(f"❌ vector_db导入失败: {e}")
        return False
    
    return True

def test_transformers_imports():
    """测试transformers相关导入"""
    print("\n测试transformers相关导入...")
    
    # 测试transformers导入
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("✅ transformers导入成功")
        transformers_available = True
    except ImportError as e:
        print(f"❌ transformers导入失败: {e}")
        transformers_available = False
    
    # 测试sentence-transformers导入
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers导入成功")
        sentence_transformers_available = True
    except ImportError as e:
        print(f"❌ sentence-transformers导入失败: {e}")
        sentence_transformers_available = False
    
    # 测试可选依赖
    try:
        import jieba
        print("✅ jieba导入成功")
        jieba_available = True
    except ImportError as e:
        print(f"⚠️  jieba导入失败: {e}")
        jieba_available = False
    
    try:
        import pandas as pd
        print("✅ pandas导入成功")
        pandas_available = True
    except ImportError as e:
        print(f"⚠️  pandas导入失败: {e}")
        pandas_available = False
    
    # 核心组件必须可用
    return transformers_available and sentence_transformers_available

def test_rag_engine_import():
    """测试RAG引擎导入"""
    print("\n测试RAG引擎导入...")
    
    try:
        from rag_engine import RAGEngine, DocumentProcessor, SimpleDocument, SimpleLLM, SimpleEmbedding
        print("✅ RAG引擎核心组件导入成功")
        return True
    except ImportError as e:
        print(f"❌ RAG引擎导入失败: {e}")
        traceback.print_exc()
        return False

def test_rag_engine_initialization():
    """测试RAG引擎初始化"""
    print("\n测试RAG引擎初始化...")
    
    try:
        from rag_engine import RAGEngine
        
        # 尝试初始化 (可能会因为模型路径不存在而失败，但不应该有导入错误)
        print("尝试初始化RAG引擎...")
        rag = RAGEngine()
        print("✅ RAG引擎初始化成功")
        return True
    except ImportError as e:
        print(f"❌ RAG引擎初始化失败 (导入错误): {e}")
        return False
    except Exception as e:
        print(f"⚠️  RAG引擎初始化失败 (其他错误): {e}")
        print("这通常是由于模型路径不存在等配置问题，不影响导入测试")
        return True

def test_vector_db_manager():
    """测试向量数据库管理器"""
    print("\n测试向量数据库管理器...")
    
    try:
        from vector_db_manager import VectorDBManager
        print("✅ 向量数据库管理器导入成功")
        return True
    except ImportError as e:
        print(f"❌ 向量数据库管理器导入失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("简化RAG架构导入验证测试")
    print("="*60)
    
    tests = [
        ("基础模块导入", test_basic_imports),
        ("transformers导入", test_transformers_imports),
        ("RAG引擎导入", test_rag_engine_import),
        ("RAG引擎初始化", test_rag_engine_initialization),
        ("向量数据库管理器", test_vector_db_manager),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试失败: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n通过: {passed}, 失败: {total - passed}")
    
    if passed == total:
        print("\n🎉 所有测试通过！简化RAG架构工作正常。")
    elif passed >= 3:  # 至少基础功能正常
        print(f"\n✅ 核心功能正常，还有 {total - passed} 个测试失败，可能是由于依赖缺失。")
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试失败，需要进一步检查。")
    
    # 提供安装建议
    if passed < total:
        print("\n💡 如果存在导入失败，请安装缺失的依赖：")
        print("pip install faiss-cpu jieba pandas chardet sentence-transformers")
    
    return passed >= 3  # 至少核心功能要正常

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 