#!/usr/bin/env python
"""
紧急修复方案：强制重装 transformers 库
适用于 ModelScope 服务器环境
"""

import subprocess
import sys
import os

def emergency_fix():
    """紧急修复 transformers 库"""
    print("🚨 执行紧急修复方案...")
    print("="*60)
    
    commands = [
        "卸载当前 transformers",
        "清理缓存", 
        "安装稳定版本",
        "验证安装"
    ]
    
    try:
        # 1. 卸载当前版本
        print("步骤1: 卸载当前 transformers 版本...")
        result1 = subprocess.run([
            sys.executable, "-m", "pip", "uninstall", "transformers", "-y"
        ], capture_output=True, text=True)
        print(f"卸载结果: {result1.returncode}")
        
        # 2. 清理pip缓存
        print("步骤2: 清理pip缓存...")
        result2 = subprocess.run([
            sys.executable, "-m", "pip", "cache", "purge"
        ], capture_output=True, text=True)
        print(f"清理结果: {result2.returncode}")
        
        # 3. 安装稳定版本
        print("步骤3: 安装 transformers==4.44.0...")
        result3 = subprocess.run([
            sys.executable, "-m", "pip", "install", "transformers==4.44.0", "--no-cache-dir"
        ], capture_output=True, text=True)
        print(f"安装结果: {result3.returncode}")
        if result3.returncode != 0:
            print(f"安装错误: {result3.stderr}")
            
            # 尝试其他版本
            print("尝试安装 transformers==4.43.0...")
            result3b = subprocess.run([
                sys.executable, "-m", "pip", "install", "transformers==4.43.0", "--no-cache-dir"
            ], capture_output=True, text=True)
            print(f"备用安装结果: {result3b.returncode}")
        
        # 4. 验证安装
        print("步骤4: 验证安装...")
        try:
            import transformers
            print(f"✅ transformers 版本: {transformers.__version__}")
            return True
        except ImportError as e:
            print(f"❌ 验证失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 紧急修复失败: {e}")
        return False

def test_basic_loading():
    """测试基本加载功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        from transformers import AutoTokenizer
        print("✅ AutoTokenizer 导入成功")
        
        from transformers import AutoModelForCausalLM
        print("✅ AutoModelForCausalLM 导入成功")
        
        # 测试基本属性
        import transformers.modeling_utils as modeling_utils
        if hasattr(modeling_utils, 'ALL_PARALLEL_STYLES'):
            print(f"✅ ALL_PARALLEL_STYLES: {modeling_utils.ALL_PARALLEL_STYLES}")
        else:
            print("⚠️  ALL_PARALLEL_STYLES 不存在，但这在新版本中是正常的")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本测试失败: {e}")
        return False

def main():
    print("🚨 紧急修复 Transformers 库")
    print("="*60)
    
    # 执行紧急修复
    if emergency_fix():
        print("\n✅ 紧急修复完成")
        
        # 测试基本功能
        if test_basic_loading():
            print("\n🎉 修复成功！现在可以尝试运行你的代码了")
            print("\n📋 建议执行:")
            print("python main_fixed.py")
        else:
            print("\n❌ 基本测试失败，可能需要更多步骤")
    else:
        print("\n❌ 紧急修复失败")
        print("\n🔧 手动操作指南:")
        print("1. 在终端执行:")
        print("   pip uninstall transformers -y")
        print("   pip install transformers==4.44.0 --no-cache-dir")
        print("2. 重启 Python 会话")
        print("3. 运行: python main_fixed.py")

if __name__ == "__main__":
    main() 