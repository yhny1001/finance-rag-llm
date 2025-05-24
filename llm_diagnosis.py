#!/usr/bin/env python
"""
LLM模型加载诊断脚本
帮助排查Qwen2.5-7B-Instruct模型加载问题
"""

import os
import torch
from pathlib import Path
from config import Config

def check_model_path():
    """检查模型路径"""
    print("🔍 检查模型路径...")
    model_path = Config.LLM_MODEL_PATH
    print(f"LLM模型路径: {model_path}")
    
    if not Path(model_path).exists():
        print(f"❌ 模型路径不存在: {model_path}")
        return False
    
    print("✅ 模型路径存在")
    
    # 检查关键文件
    key_files = ['config.json', 'tokenizer.json', 'tokenizer_config.json']
    for file in key_files:
        file_path = Path(model_path) / file
        if file_path.exists():
            print(f"✅ {file} 存在")
        else:
            print(f"⚠️  {file} 不存在")
    
    return True

def check_transformers_version():
    """检查transformers版本"""
    print("\n🔍 检查transformers版本...")
    try:
        import transformers
        print(f"transformers版本: {transformers.__version__}")
        
        # 推荐版本
        import packaging.version as pv
        current_version = pv.parse(transformers.__version__)
        min_version = pv.parse("4.20.0")
        
        if current_version >= min_version:
            print("✅ transformers版本符合要求")
        else:
            print(f"⚠️  transformers版本较低，推荐升级到4.20.0+")
        
        return True
    except ImportError:
        print("❌ transformers未安装")
        return False

def test_simple_tokenizer_load():
    """测试简单的tokenizer加载"""
    print("\n🔍 测试tokenizer加载...")
    try:
        from transformers import AutoTokenizer
        
        model_path = Config.LLM_MODEL_PATH
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ tokenizer加载成功")
        
        # 测试编码
        test_text = "你好"
        tokens = tokenizer.encode(test_text)
        print(f"✅ tokenizer编码测试成功: {test_text} -> {tokens}")
        
        return True
    except Exception as e:
        print(f"❌ tokenizer加载失败: {e}")
        return False

def test_model_config():
    """测试模型配置加载"""
    print("\n🔍 测试模型配置加载...")
    try:
        from transformers import AutoConfig
        
        model_path = Config.LLM_MODEL_PATH
        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ 模型配置加载成功")
        print(f"模型类型: {config.model_type}")
        print(f"模型架构: {config.architectures}")
        
        return True
    except Exception as e:
        print(f"❌ 模型配置加载失败: {e}")
        return False

def check_gpu_memory():
    """检查GPU内存"""
    print("\n🔍 检查GPU状态...")
    
    if not torch.cuda.is_available():
        print("⚠️  CUDA不可用，将使用CPU")
        return False
    
    print(f"✅ CUDA可用，版本: {torch.version.cuda}")
    
    for i in range(torch.cuda.device_count()):
        gpu_name = torch.cuda.get_device_name(i)
        memory_total = torch.cuda.get_device_properties(i).total_memory / 1024**3
        memory_allocated = torch.cuda.memory_allocated(i) / 1024**3
        memory_free = memory_total - memory_allocated
        
        print(f"GPU {i}: {gpu_name}")
        print(f"  总内存: {memory_total:.2f} GB")
        print(f"  已用内存: {memory_allocated:.2f} GB")
        print(f"  可用内存: {memory_free:.2f} GB")
        
        # 检查是否有足够内存加载7B模型
        if memory_free < 14:  # 7B模型大约需要14GB
            print(f"  ⚠️  可用内存不足，7B模型需要约14GB")
        else:
            print(f"  ✅ 内存充足")
    
    return True

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("1. 如果模型路径不存在，请检查模型是否正确下载")
    print("2. 如果内存不足，可以尝试:")
    print("   - 使用更小的模型（如Qwen2.5-3B）")
    print("   - 启用8bit或4bit量化")
    print("   - 调整device_map参数")
    print("3. 如果transformers版本问题，请升级:")
    print("   pip install -U transformers")
    print("4. 暂时的替代方案:")
    print("   - 系统可以仅使用向量检索功能")
    print("   - 使用更小的本地模型")
    print("   - 集成在线API服务")

def main():
    """主诊断函数"""
    print("="*60)
    print("🔧 LLM模型加载诊断工具")
    print("="*60)
    
    checks = [
        ("模型路径检查", check_model_path),
        ("transformers版本检查", check_transformers_version),
        ("tokenizer加载测试", test_simple_tokenizer_load),
        ("模型配置测试", test_model_config),
        ("GPU内存检查", check_gpu_memory),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}失败: {e}")
            results.append((check_name, False))
    
    # 总结
    print("\n" + "="*60)
    print("🔍 诊断结果总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n通过: {passed}/{total}")
    
    # 提供建议
    suggest_solutions()
    
    # 系统状态评估
    print("\n" + "="*60)
    print("📊 系统状态评估")
    print("="*60)
    
    if passed >= 4:
        print("🟢 系统状态良好，LLM问题可能是暂时的配置问题")
    elif passed >= 2:
        print("🟡 系统部分功能正常，向量检索可以使用")
    else:
        print("🔴 系统存在较多问题，需要检查环境配置")
    
    print("\n✨ 好消息：即使LLM加载失败，向量检索功能仍然可以正常工作！")

if __name__ == "__main__":
    main() 