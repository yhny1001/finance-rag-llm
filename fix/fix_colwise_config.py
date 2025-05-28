#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复Qwen3模型配置中的colwise tensor parallel问题
"""

import json
import shutil
from pathlib import Path
from config import Config

def fix_model_config():
    """修复模型配置文件"""
    print("🔧 修复模型配置中的colwise问题...")
    
    try:
        model_path = Path(Config.LLM_MODEL_PATH)
        config_file = model_path / "config.json"
        
        if not config_file.exists():
            print(f"❌ 配置文件不存在: {config_file}")
            return False
        
        print(f"📁 配置文件: {config_file}")
        
        # 备份
        backup_file = config_file.with_suffix('.json.backup')
        if not backup_file.exists():
            shutil.copy2(config_file, backup_file)
            print(f"📦 已备份到: {backup_file}")
        
        # 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📋 当前配置:")
        for key in ['tensor_parallel_style', 'tensor_parallel_size', 'quantization_config']:
            if key in config:
                print(f"  {key}: {config[key]}")
        
        # 修复问题配置
        changes_made = False
        
        # 1. 移除或修复tensor_parallel_style
        if 'tensor_parallel_style' in config:
            if config['tensor_parallel_style'] == 'colwise':
                print("🔧 移除colwise tensor_parallel_style...")
                del config['tensor_parallel_style']
                changes_made = True
            elif config['tensor_parallel_style'] not in ['fsdp', 'deepspeed', 'megatron', 'torchpaxus']:
                print(f"🔧 修复不支持的tensor_parallel_style: {config['tensor_parallel_style']}")
                config['tensor_parallel_style'] = 'fsdp'
                changes_made = True
        
        # 2. 检查其他并行相关配置
        parallel_keys = [
            'tensor_parallel_size', 
            'pipeline_model_parallel_size',
            'data_parallel_size'
        ]
        
        for key in parallel_keys:
            if key in config and config[key] != 1:
                print(f"🔧 重置{key}为1...")
                config[key] = 1
                changes_made = True
        
        # 3. 添加安全的并行配置
        safe_parallel_config = {
            'use_cache': True,
            'torch_dtype': 'float16'
        }
        
        for key, value in safe_parallel_config.items():
            if key not in config:
                config[key] = value
                changes_made = True
        
        # 保存修复后的配置
        if changes_made:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ 配置文件已修复")
            
            # 显示修复后的配置
            print("\n📋 修复后配置:")
            for key in ['tensor_parallel_style', 'tensor_parallel_size', 'torch_dtype']:
                if key in config:
                    print(f"  {key}: {config[key]}")
            
            return True
        else:
            print("✅ 配置文件无需修复")
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixed_config():
    """测试修复后的配置"""
    print("\n🧪 测试修复后的配置...")
    
    try:
        from transformers import AutoConfig
        
        model_path = Config.LLM_MODEL_PATH
        config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        
        print("✅ 配置加载成功")
        
        # 检查关键配置
        parallel_attrs = [
            'tensor_parallel_style',
            'tensor_parallel_size', 
            'pipeline_model_parallel_size'
        ]
        
        for attr in parallel_attrs:
            if hasattr(config, attr):
                value = getattr(config, attr)
                print(f"  {attr}: {value}")
                
                if attr == 'tensor_parallel_style' and value == 'colwise':
                    print("⚠️ colwise问题仍然存在")
                    return False
        
        print("✅ 配置检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def restore_config():
    """恢复配置文件"""
    print("\n🔄 配置恢复说明...")
    
    try:
        model_path = Path(Config.LLM_MODEL_PATH)
        backup_file = model_path / "config.json.backup"
        config_file = model_path / "config.json"
        
        if backup_file.exists():
            print(f"💡 如需恢复原始配置，请运行：")
            print(f"   cp {backup_file} {config_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 恢复说明失败: {e}")
        return False

def main():
    """主修复流程"""
    print("🔧 修复Qwen3 colwise配置问题")
    print("=" * 50)
    
    steps = [
        ("修复模型配置", fix_model_config),
        ("测试修复配置", test_fixed_config)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if step_func():
            print(f"✅ {step_name}成功")
            success_count += 1
        else:
            print(f"❌ {step_name}失败")
            break
    
    if success_count == len(steps):
        print("\n🎉 colwise配置修复完成！")
        restore_config()
        return True
    else:
        print("\n❌ colwise配置修复失败")
        restore_config()
        return False

if __name__ == "__main__":
    main() 