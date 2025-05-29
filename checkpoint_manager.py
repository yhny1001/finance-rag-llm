"""
检查点管理工具
用于管理断点续传检查点，查看、恢复或清除检查点
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

from resume_processor import ResumeProcessor


def show_checkpoint_info(resume: ResumeProcessor):
    """显示检查点信息"""
    if not resume.has_checkpoint():
        print("❌ 未找到检查点")
        return False
    
    try:
        # 读取检查点信息
        with open(resume.checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        # 读取结果信息
        with open(resume.checkpoint_results, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print("\n" + "="*50)
        print("📊 检查点信息")
        print("="*50)
        
        print(f"🕒 保存时间: {checkpoint_data.get('time_str', '未知')}")
        print(f"🔖 会话ID: {checkpoint_data.get('session_id', '未知')}")
        print(f"📈 进度: {checkpoint_data.get('current_idx', 0)}/{checkpoint_data.get('total', 0)} "
              f"({checkpoint_data.get('completed_percentage', 0)}%)")
        print(f"📦 批处理大小: {checkpoint_data.get('batch_size', 0)}")
        print(f"📝 已保存结果数: {len(results)}")
        
        return True
    except Exception as e:
        print(f"❌ 读取检查点信息失败: {e}")
        return False


def backup_checkpoint(resume: ResumeProcessor, backup_name: str = None):
    """备份检查点"""
    if not resume.has_checkpoint():
        print("❌ 未找到检查点，无法备份")
        return False
    
    try:
        # 生成备份文件名
        if backup_name is None:
            from datetime import datetime
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 备份文件路径
        backup_dir = resume.checkpoint_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_status = backup_dir / f"{backup_name}_status.json"
        backup_results = backup_dir / f"{backup_name}_results.json"
        
        # 复制文件
        import shutil
        shutil.copy2(resume.checkpoint_file, backup_status)
        shutil.copy2(resume.checkpoint_results, backup_results)
        
        print(f"✅ 检查点已备份: {backup_name}")
        print(f"   状态文件: {backup_status}")
        print(f"   结果文件: {backup_results}")
        
        return True
    except Exception as e:
        print(f"❌ 备份检查点失败: {e}")
        return False


def restore_checkpoint(resume: ResumeProcessor, backup_name: str):
    """从备份恢复检查点"""
    # 备份文件路径
    backup_dir = resume.checkpoint_dir / "backups"
    backup_status = backup_dir / f"{backup_name}_status.json"
    backup_results = backup_dir / f"{backup_name}_results.json"
    
    if not backup_status.exists() or not backup_results.exists():
        print(f"❌ 未找到备份 {backup_name}")
        return False
    
    try:
        # 先备份当前检查点（如果存在）
        if resume.has_checkpoint():
            backup_checkpoint(resume, "auto_before_restore")
        
        # 复制文件
        import shutil
        shutil.copy2(backup_status, resume.checkpoint_file)
        shutil.copy2(backup_results, resume.checkpoint_results)
        
        print(f"✅ 检查点已恢复: {backup_name}")
        
        # 显示恢复后的检查点信息
        show_checkpoint_info(resume)
        
        return True
    except Exception as e:
        print(f"❌ 恢复检查点失败: {e}")
        return False


def list_backups(resume: ResumeProcessor):
    """列出所有备份"""
    backup_dir = resume.checkpoint_dir / "backups"
    
    if not backup_dir.exists():
        print("📝 没有备份目录")
        return False
    
    # 查找所有状态文件
    backup_files = list(backup_dir.glob("*_status.json"))
    
    if not backup_files:
        print("📝 没有找到备份")
        return False
    
    print("\n" + "="*50)
    print("📋 备份列表")
    print("="*50)
    
    for idx, file in enumerate(sorted(backup_files), 1):
        backup_name = file.name.replace("_status.json", "")
        
        # 读取备份信息
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            progress = f"{data.get('current_idx', 0)}/{data.get('total', 0)} ({data.get('completed_percentage', 0)}%)"
            timestamp = data.get('time_str', '未知')
            
            print(f"{idx}. {backup_name}")
            print(f"   时间: {timestamp}")
            print(f"   进度: {progress}")
            print(f"   批次大小: {data.get('batch_size', 0)}")
            print()
        except:
            print(f"{idx}. {backup_name} (无法读取详细信息)")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="检查点管理工具")
    parser.add_argument("--info", action="store_true", help="显示当前检查点信息")
    parser.add_argument("--clear", action="store_true", help="清除当前检查点")
    parser.add_argument("--backup", action="store_true", help="备份当前检查点")
    parser.add_argument("--backup-name", type=str, help="备份名称")
    parser.add_argument("--restore", type=str, help="从备份恢复检查点")
    parser.add_argument("--list-backups", action="store_true", help="列出所有备份")
    
    args = parser.parse_args()
    
    # 初始化断点续传处理器
    resume = ResumeProcessor()
    
    # 没有参数时显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        # 如果有检查点，显示其信息
        if resume.has_checkpoint():
            print("\n检测到当前有检查点:")
            show_checkpoint_info(resume)
        return
    
    # 显示检查点信息
    if args.info:
        if not show_checkpoint_info(resume):
            return
    
    # 清除检查点
    if args.clear:
        if resume.has_checkpoint():
            confirm = input("确定要清除当前检查点吗? (y/n): ").strip().lower()
            if confirm == 'y':
                if resume.clear_checkpoint():
                    print("✅ 检查点已清除")
        else:
            print("📝 没有检查点需要清除")
    
    # 备份检查点
    if args.backup:
        if backup_checkpoint(resume, args.backup_name):
            print("✅ 检查点备份成功")
    
    # 从备份恢复
    if args.restore:
        if restore_checkpoint(resume, args.restore):
            print("✅ 检查点恢复成功")
    
    # 列出所有备份
    if args.list_backups:
        list_backups(resume)


if __name__ == "__main__":
    main() 