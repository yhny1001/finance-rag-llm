#!/usr/bin/env python
"""
精确调试LLM加载问题
捕获详细的错误堆栈信息
"""

import traceback
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import Config

def test_exact_same_code_as_rag():
    """使用与rag_engine.py完全相同的代码进行测试"""
    print("🔍 使用与RAG引擎完全相同的代码测试...")
    
    model_path = Config.LLM_MODEL_PATH
    model = None
    tokenizer = None
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"模型路径: {model_path}")
    print(f"设备: {device}")
    
    try:
        print(f"加载LLM模型: {model_path}")
        
        # 步骤1：加载tokenizer
        print("步骤1: 加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ tokenizer加载成功")
        
        # 步骤2：加载模型
        print("步骤2: 加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("✅ LLM模型加载成功")
        
        return True, model, tokenizer
        
    except Exception as e:
        print(f"❌ LLM模型加载失败: {e}")
        print("\n🔍 详细错误信息:")
        traceback.print_exc()
        return False, None, None

def test_step_by_step():
    """逐步测试，找出具体在哪一步失败"""
    print("\n🔧 逐步测试...")
    
    model_path = Config.LLM_MODEL_PATH
    
    # 测试1：基础导入
    try:
        print("测试1: 导入transformers...")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        traceback.print_exc()
        return
    
    # 测试2：检查路径
    try:
        print("测试2: 检查模型路径...")
        from pathlib import Path
        if Path(model_path).exists():
            print("✅ 路径存在")
        else:
            print("❌ 路径不存在")
            return
    except Exception as e:
        print(f"❌ 路径检查失败: {e}")
        traceback.print_exc()
        return
    
    # 测试3：加载tokenizer（不传递额外参数）
    try:
        print("测试3: 加载tokenizer（基础参数）...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ 基础tokenizer加载成功")
    except Exception as e:
        print(f"❌ 基础tokenizer加载失败: {e}")
        traceback.print_exc()
        
    # 测试4：加载tokenizer（添加trust_remote_code）
    try:
        print("测试4: 加载tokenizer（trust_remote_code=True）...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ 完整tokenizer加载成功")
    except Exception as e:
        print(f"❌ 完整tokenizer加载失败: {e}")
        traceback.print_exc()
        return
    
    # 测试5：加载模型配置
    try:
        print("测试5: 加载模型配置...")
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ 模型配置加载成功")
        print(f"配置信息: {config}")
    except Exception as e:
        print(f"❌ 模型配置加载失败: {e}")
        traceback.print_exc()
        return
    
    # 测试6：加载模型（最小参数）
    try:
        print("测试6: 加载模型（最小参数）...")
        model = AutoModelForCausalLM.from_pretrained(model_path)
        print("✅ 最小参数模型加载成功")
    except Exception as e:
        print(f"❌ 最小参数模型加载失败: {e}")
        traceback.print_exc()
    
    # 测试7：加载模型（逐步添加参数）
    try:
        print("测试7: 加载模型（trust_remote_code=True）...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ trust_remote_code模型加载成功")
    except Exception as e:
        print(f"❌ trust_remote_code模型加载失败: {e}")
        traceback.print_exc()
    
    # 测试8：加载模型（添加torch_dtype）
    try:
        print("测试8: 加载模型（torch_dtype=torch.float16）...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        print("✅ float16模型加载成功")
    except Exception as e:
        print(f"❌ float16模型加载失败: {e}")
        traceback.print_exc()
    
    # 测试9：加载模型（完整参数）
    try:
        print("测试9: 加载模型（完整参数）...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("✅ 完整参数模型加载成功")
    except Exception as e:
        print(f"❌ 完整参数模型加载失败: {e}")
        print("\n🔍 这里可能就是问题所在！")
        traceback.print_exc()

def test_with_different_parameters():
    """测试不同的参数组合"""
    print("\n🧪 测试不同参数组合...")
    
    model_path = Config.LLM_MODEL_PATH
    
    parameter_sets = [
        {
            "name": "默认参数",
            "params": {}
        },
        {
            "name": "只添加trust_remote_code",
            "params": {"trust_remote_code": True}
        },
        {
            "name": "添加torch_dtype",
            "params": {
                "torch_dtype": torch.float16,
                "trust_remote_code": True
            }
        },
        {
            "name": "使用CPU设备映射",
            "params": {
                "torch_dtype": torch.float16,
                "device_map": "cpu",
                "trust_remote_code": True
            }
        },
        {
            "name": "使用cuda设备映射",
            "params": {
                "torch_dtype": torch.float16,
                "device_map": "cuda:0",
                "trust_remote_code": True
            }
        },
        {
            "name": "原始auto设备映射",
            "params": {
                "torch_dtype": torch.float16,
                "device_map": "auto",
                "trust_remote_code": True
            }
        }
    ]
    
    for param_set in parameter_sets:
        print(f"\n测试: {param_set['name']}")
        print(f"参数: {param_set['params']}")
        
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                **param_set['params']
            )
            print(f"✅ {param_set['name']} - 成功")
            del model  # 释放内存
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"❌ {param_set['name']} - 失败: {e}")
            if "NoneType" in str(e):
                print("🎯 发现NoneType错误！")
                traceback.print_exc()

def main():
    """主函数"""
    print("="*60)
    print("🐛 LLM加载问题精确调试")
    print("="*60)
    
    # 测试1：使用完全相同的代码
    success, model, tokenizer = test_exact_same_code_as_rag()
    if success:
        print("🎉 问题解决！使用相同代码可以正常加载")
        return
    
    # 测试2：逐步测试
    test_step_by_step()
    
    # 测试3：不同参数组合
    test_with_different_parameters()
    
    print("\n" + "="*60)
    print("🔍 调试总结")
    print("="*60)
    print("请查看上面的详细错误信息，找出导致 'NoneType' 错误的具体参数")

if __name__ == "__main__":
    main() 