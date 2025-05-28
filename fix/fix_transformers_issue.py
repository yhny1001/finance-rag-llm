#!/usr/bin/env python
"""
修复 transformers 库 NoneType 错误
解决方案：临时修补 transformers 库中的 bug
"""

import os
import sys
import importlib.util
from pathlib import Path

def fix_transformers_bug():
    """修复 transformers 库中的 ALL_PARALLEL_STYLES 问题"""
    print("🔧 正在修复 transformers 库 bug...")
    
    try:
        # 导入 transformers
        import transformers
        from transformers.modeling_utils import ALL_PARALLEL_STYLES
        
        # 检查是否存在问题
        if ALL_PARALLEL_STYLES is None:
            print("⚠️  发现 ALL_PARALLEL_STYLES 为 None，正在修复...")
            
            # 设置正确的并行样式
            import transformers.modeling_utils as modeling_utils
            modeling_utils.ALL_PARALLEL_STYLES = [
                "model_parallel",
                "pipeline_parallel", 
                "tensor_parallel",
                "data_parallel"
            ]
            
            print("✅ 修复完成")
            return True
        else:
            print("✅ ALL_PARALLEL_STYLES 正常，无需修复")
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def alternative_fix():
    """替代方案：直接修补 modeling_utils.py 文件"""
    print("\n🔧 尝试替代修复方案...")
    
    try:
        import transformers
        
        # 获取 transformers 安装路径
        transformers_path = Path(transformers.__file__).parent
        modeling_utils_path = transformers_path / "modeling_utils.py"
        
        print(f"📁 transformers 路径: {modeling_utils_path}")
        
        if modeling_utils_path.exists():
            # 读取文件内容
            with open(modeling_utils_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否需要修复
            if 'ALL_PARALLEL_STYLES = None' in content or 'ALL_PARALLEL_STYLES=None' in content:
                print("⚠️  发现问题代码，正在修复...")
                
                # 替换问题代码
                content = content.replace(
                    'ALL_PARALLEL_STYLES = None',
                    'ALL_PARALLEL_STYLES = ["model_parallel", "pipeline_parallel", "tensor_parallel", "data_parallel"]'
                )
                content = content.replace(
                    'ALL_PARALLEL_STYLES=None',
                    'ALL_PARALLEL_STYLES=["model_parallel", "pipeline_parallel", "tensor_parallel", "data_parallel"]'
                )
                
                # 备份原文件
                backup_path = modeling_utils_path.with_suffix('.py.backup')
                modeling_utils_path.rename(backup_path)
                print(f"📦 已备份原文件到: {backup_path}")
                
                # 写入修复后的内容
                with open(modeling_utils_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ 文件修复完成")
                return True
            else:
                print("✅ 文件中未发现问题代码")
                return True
                
    except Exception as e:
        print(f"❌ 替代修复失败: {e}")
        return False

def test_model_loading():
    """测试模型加载是否正常"""
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
        
        # 清理内存
        del model
        del tokenizer
        torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("🐛 修复 transformers 库 NoneType 错误")
    print("="*60)
    
    # 方案1：运行时修复
    if fix_transformers_bug():
        print("✅ 运行时修复成功，测试模型加载...")
        if test_model_loading():
            print("🎉 问题已解决！")
            return
    
    # 方案2：文件修复
    print("\n方案1失败，尝试方案2...")
    if alternative_fix():
        print("✅ 文件修复成功，请重新导入 transformers 后测试")
        return
    
    # 方案3：版本解决方案
    print("\n" + "="*60)
    print("🔍 推荐解决方案")
    print("="*60)
    print("1. 升级 transformers 版本:")
    print("   pip install --upgrade transformers")
    print()
    print("2. 或者降级到稳定版本:")
    print("   pip install transformers==4.44.0")
    print()
    print("3. 设置环境变量:")
    print("   export TRANSFORMERS_VERBOSITY=error")
    print()
    print("4. 手动修复 (运行此脚本):")
    print("   python fix_transformers_issue.py")

if __name__ == "__main__":
    main() 