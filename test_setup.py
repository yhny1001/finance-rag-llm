#!/usr/bin/env python
"""
项目设置测试脚本
用于验证项目环境和依赖是否正确配置
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """测试Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python版本满足要求 (3.8+)")
        return True
    else:
        print("❌ Python版本不满足要求，需要3.8或以上版本")
        return False

def test_file_structure():
    """测试项目文件结构"""
    print("\n检查项目文件结构...")
    
    required_files = [
        'config.py',
        'rag_engine.py', 
        'vector_db.py',
        'requirements.txt',
        'test_imports.py'
    ]
    
    optional_files = [
        'main.py',
        'README.md',
        '需求文档.md'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    for file in optional_files:
        if Path(file).exists():
            print(f"✅ {file} (可选)")
        else:
            print(f"⚠️  {file} (可选，缺失)")
    
    return len(missing_files) == 0

def test_directories():
    """测试必要目录"""
    print("\n检查项目目录...")
    
    required_dirs = [
        '赛题制度文档',
        '数据集A'
    ]
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/")
        else:
            print(f"⚠️  {directory}/ (运行时需要)")
    
    return True  # 目录可以在运行时创建

def test_core_imports():
    """测试核心模块导入"""
    print("\n检查核心模块导入...")
    
    # 必需的核心模块
    core_modules = [
        ('json', '标准库'),
        ('pathlib', '标准库'),
        ('os', '标准库'),
        ('sys', '标准库'),
        ('torch', 'PyTorch - 深度学习框架'),
        ('numpy', 'NumPy - 数值计算')
    ]
    
    failed_imports = []
    for module, description in core_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"❌ {module} ({description}) - 需要安装")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_ml_dependencies():
    """测试机器学习相关依赖"""
    print("\n检查机器学习依赖...")
    
    ml_modules = [
        ('transformers', 'Transformers - HuggingFace模型库'),
        ('sentence_transformers', 'Sentence Transformers - 句子嵌入'),
        ('faiss', 'FAISS - 向量检索'),
        ('pandas', 'Pandas - 数据处理'),
        ('tqdm', 'TQDM - 进度条')
    ]
    
    optional_modules = [
        ('jieba', 'Jieba - 中文分词'),
        ('chardet', 'Chardet - 编码检测')
    ]
    
    failed_critical = []
    
    for module, description in ml_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"❌ {module} ({description}) - 需要安装")
            failed_critical.append(module)
    
    print("\n检查可选依赖...")
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"⚠️  {module} ({description}) - 建议安装")
    
    return len(failed_critical) == 0

def test_config_import():
    """测试配置文件导入"""
    print("\n检查配置模块...")
    
    try:
        from config import Config
        print("✅ config.Config 导入成功")
        
        # 检查关键配置项
        config_items = [
            'LLM_MODEL_PATH',
            'EMBEDDING_MODEL_PATH', 
            'DOCUMENTS_DIR',
            'VECTOR_DB_DIR',
            'CHUNK_SIZE',
            'TOP_K'
        ]
        
        missing_configs = []
        for item in config_items:
            if hasattr(Config, item):
                value = getattr(Config, item)
                print(f"✅ {item}: {value}")
            else:
                print(f"❌ {item}: 配置项缺失")
                missing_configs.append(item)
                
        return len(missing_configs) == 0
        
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False

def test_rag_engine_import():
    """测试RAG引擎导入"""
    print("\n检查RAG引擎模块...")
    
    try:
        from rag_engine import RAGEngine, DocumentProcessor, SimpleDocument, SimpleLLM, SimpleEmbedding
        print("✅ RAG引擎核心类导入成功")
        print("  ✅ RAGEngine - 主引擎类")
        print("  ✅ DocumentProcessor - 文档处理器")
        print("  ✅ SimpleDocument - 文档类")
        print("  ✅ SimpleLLM - 简化LLM类")
        print("  ✅ SimpleEmbedding - 简化嵌入类")
        return True
        
    except Exception as e:
        print(f"❌ RAG引擎模块导入失败: {e}")
        return False

def test_vector_db_import():
    """测试向量数据库导入"""
    print("\n检查向量数据库模块...")
    
    try:
        from vector_db import VectorDatabase
        print("✅ VectorDatabase 类导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 向量数据库模块导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("金融监管制度智能问答系统 - 简化架构测试")
    print("="*60)
    
    tests = [
        ("Python版本", test_python_version),
        ("文件结构", test_file_structure), 
        ("目录检查", test_directories),
        ("核心模块导入", test_core_imports),
        ("机器学习依赖", test_ml_dependencies),
        ("配置模块", test_config_import),
        ("RAG引擎模块", test_rag_engine_import),
        ("向量数据库模块", test_vector_db_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 打印测试结果总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}")
            passed += 1
        else:
            print(f"❌ {test_name}")
            failed += 1
    
    print(f"\n通过: {passed}, 失败: {failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！项目设置正确。")
        print("\n下一步:")
        print("1. 运行 'python test_imports.py' 进行详细导入测试")
        print("2. 确保文档目录 '赛题制度文档/' 包含金融监管文档")  
        print("3. 确保测试数据 '数据集A/testA.json' 存在")
        print("4. 运行主程序开始使用系统")
        
    elif passed >= 5:  # 至少核心功能正常
        print("\n✅ 核心功能正常，部分依赖可能需要安装。")
        print("\n建议执行:")
        print("pip install faiss-cpu jieba pandas chardet sentence-transformers")
        
    else:
        print("\n⚠️  存在重要配置问题，请检查失败的测试项目。")
        
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 