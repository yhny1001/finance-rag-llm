"""
修复测试数据路径配置
将配置文件中的测试数据路径更新为实际存在的文件路径
"""

import sys
from pathlib import Path
import shutil

def fix_test_data_path():
    """修复测试数据路径"""
    print("🔧 修复测试数据路径配置...")
    
    # 实际的测试文件路径
    actual_test_file = Path("数据集A/testA.json")
    expected_test_file = Path("金融监管制度问答-测试集.jsonl")
    
    if not actual_test_file.exists():
        print(f"❌ 实际测试文件不存在: {actual_test_file}")
        return False
    
    print(f"✅ 找到实际测试文件: {actual_test_file}")
    
    # 方案1: 创建符号链接或复制文件
    try:
        if expected_test_file.exists():
            expected_test_file.unlink()
            print(f"删除旧的测试文件: {expected_test_file}")
        
        # 复制文件到预期位置
        shutil.copy2(actual_test_file, expected_test_file)
        print(f"✅ 复制测试文件到: {expected_test_file}")
        
    except Exception as e:
        print(f"⚠️ 复制文件失败: {e}")
        print("尝试更新配置文件...")
        
        # 方案2: 更新配置文件
        config_files = [
            "config.py",
            "config_improved.py", 
            "config_optimized.py"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    update_config_file(config_file, actual_test_file)
                    print(f"✅ 更新配置文件: {config_file}")
                except Exception as e:
                    print(f"⚠️ 更新 {config_file} 失败: {e}")
    
    # 验证文件是否可读
    try:
        import json
        with open(actual_test_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line:
                data = json.loads(first_line)
                print(f"✅ 测试文件格式验证成功，包含ID: {data.get('id')}")
                return True
    except Exception as e:
        print(f"❌ 测试文件格式验证失败: {e}")
        return False
    
    return True

def update_config_file(config_file: str, actual_test_file: Path):
    """更新配置文件中的测试数据路径"""
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新测试数据路径
    old_path = '"金融监管制度问答-测试集.jsonl"'
    new_path = f'"{actual_test_file}"'
    
    if old_path in content:
        content = content.replace(old_path, new_path)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  更新路径: {old_path} -> {new_path}")
    else:
        print(f"  配置文件中未找到需要更新的路径")

def main():
    """主函数"""
    print("🛠️ 测试数据路径修复工具")
    print("=" * 50)
    
    if fix_test_data_path():
        print("\n✅ 测试数据路径修复完成")
        print("\n📋 现在可以运行:")
        print("1. python diagnose_system.py")
        print("2. python main_improved.py --force-rebuild")
        print("3. python quick_rebuild.py")
    else:
        print("\n❌ 测试数据路径修复失败")
        print("请手动检查测试文件是否存在")

if __name__ == "__main__":
    main() 