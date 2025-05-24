#!/usr/bin/env python
"""
在 ModelScope 服务器环境中修复 transformers 库 NoneType 错误
针对 'argument of type 'NoneType' is not iterable' 错误的完整解决方案
"""

import os
import sys
import subprocess

def check_environment():
    """检查当前环境"""
    print("🔍 检查当前环境...")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        import transformers
        print(f"Transformers 版本: {transformers.__version__}")
        print(f"Transformers 路径: {transformers.__file__}")
        return True
    except ImportError:
        print("❌ 未安装 transformers")
        return False

def solution_1_upgrade_transformers():
    """解决方案1：升级transformers版本"""
    print("\n🔧 解决方案1: 升级 transformers...")
    
    try:
        # 升级到最新版本
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "transformers"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ transformers 升级成功")
            return True
        else:
            print(f"❌ 升级失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 升级过程出错: {e}")
        return False

def solution_2_install_specific_version():
    """解决方案2：安装特定稳定版本"""
    print("\n🔧 解决方案2: 安装稳定版本...")
    
    stable_versions = ["4.44.0", "4.43.0", "4.42.0"]
    
    for version in stable_versions:
        try:
            print(f"尝试安装 transformers=={version}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", f"transformers=={version}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ transformers {version} 安装成功")
                return True
            else:
                print(f"❌ 版本 {version} 安装失败")
                continue
        except Exception as e:
            print(f"❌ 安装版本 {version} 出错: {e}")
            continue
    
    return False

def solution_3_runtime_patch():
    """解决方案3：运行时补丁"""
    print("\n🔧 解决方案3: 运行时补丁...")
    
    try:
        import transformers.modeling_utils as modeling_utils
        
        # 检查 ALL_PARALLEL_STYLES
        if hasattr(modeling_utils, 'ALL_PARALLEL_STYLES'):
            if modeling_utils.ALL_PARALLEL_STYLES is None:
                print("⚠️  发现 ALL_PARALLEL_STYLES 为 None，正在修复...")
                modeling_utils.ALL_PARALLEL_STYLES = [
                    "model_parallel",
                    "pipeline_parallel", 
                    "tensor_parallel",
                    "data_parallel"
                ]
                print("✅ 运行时补丁应用成功")
                return True
            else:
                print("✅ ALL_PARALLEL_STYLES 已正常")
                return True
        else:
            print("⚠️  未找到 ALL_PARALLEL_STYLES 属性，添加...")
            modeling_utils.ALL_PARALLEL_STYLES = [
                "model_parallel",
                "pipeline_parallel", 
                "tensor_parallel", 
                "data_parallel"
            ]
            print("✅ 运行时补丁应用成功")
            return True
            
    except Exception as e:
        print(f"❌ 运行时补丁失败: {e}")
        return False

def solution_4_environment_fix():
    """解决方案4：环境变量修复"""
    print("\n🔧 解决方案4: 设置环境变量...")
    
    try:
        # 设置环境变量
        os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        
        print("✅ 环境变量设置完成")
        return True
    except Exception as e:
        print(f"❌ 环境变量设置失败: {e}")
        return False

def test_model_loading():
    """测试模型加载"""
    print("\n🧪 测试模型加载...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        model_path = "/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct"
        
        print("步骤1: 加载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        print("✅ tokenizer 加载成功")
        
        print("步骤2: 加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("✅ 模型加载成功！")
        print("🎉 问题已解决！")
        
        # 清理内存
        del model
        del tokenizer
        torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载仍然失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数 - 尝试多种解决方案"""
    print("="*60)
    print("🐛 修复 ModelScope 环境 transformers 库问题")
    print("="*60)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败")
        return
    
    # 尝试解决方案4：环境变量 (最快)
    if solution_4_environment_fix():
        if test_model_loading():
            print("\n🎉 通过环境变量修复成功！")
            return
    
    # 尝试解决方案3：运行时补丁
    if solution_3_runtime_patch():
        if test_model_loading():
            print("\n🎉 通过运行时补丁修复成功！")
            return
    
    # 尝试解决方案1：升级版本
    print("\n环境变量和运行时补丁都未成功，尝试升级版本...")
    if solution_1_upgrade_transformers():
        if test_model_loading():
            print("\n🎉 通过升级版本修复成功！")
            return
    
    # 尝试解决方案2：安装稳定版本
    print("\n升级失败，尝试安装稳定版本...")
    if solution_2_install_specific_version():
        if test_model_loading():
            print("\n🎉 通过安装稳定版本修复成功！")
            return
    
    # 所有方案都失败
    print("\n" + "="*60)
    print("❌ 所有自动修复方案都失败了")
    print("="*60)
    print("手动解决方案:")
    print("1. 重启 Python 内核")
    print("2. 运行: pip uninstall transformers && pip install transformers==4.44.0")
    print("3. 联系技术支持")

if __name__ == "__main__":
    main() 