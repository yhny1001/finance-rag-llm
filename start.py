"""
一键启动脚本
自动检查依赖、清理旧数据库(可选)、启动RAG系统
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """检查必要的依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'torch',
        'transformers', 
        'sentence_transformers',
        'faiss_cpu',
        'pandas',
        'numpy',
        'tqdm',
        'jieba',
        'chardet'
    ]
    
    optional_packages = [
        'python-docx',
        'PyPDF2'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} (必需)")
    
    for package in optional_packages:
        try:
            if package == 'python-docx':
                __import__('docx')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️ {package} (可选)")
    
    return missing_required, missing_optional

def install_missing_packages(missing_packages):
    """安装缺失的包"""
    if not missing_packages:
        return True
    
    print(f"\n📦 安装缺失的包: {', '.join(missing_packages)}")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
        subprocess.check_call(cmd)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        'main.py',
        'rag_engine.py', 
        'config.py',
        'vector_db.py'
    ]
    
    required_dirs = [
        '赛题制度文档',
        '数据集A'
    ]
    
    all_good = True
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} 缺失")
            all_good = False
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            if dir_name == '赛题制度文档':
                docx_count = len(list(Path(dir_name).glob('*.docx')))
                print(f"✅ {dir_name} (包含 {docx_count} 个docx文件)")
            else:
                print(f"✅ {dir_name}")
        else:
            print(f"❌ {dir_name} 缺失")
            all_good = False
    
    return all_good

def clear_old_database():
    """清理旧的向量数据库"""
    print("\n🗑️ 清理旧的向量数据库...")
    
    try:
        # 尝试导入清理脚本
        if Path("clear_vector_db.py").exists():
            from clear_vector_db import clear_vector_database
            clear_vector_database()
        else:
            # 手动清理
            items_to_remove = ["vector_db/", "faiss_index.bin", "vector_metadata.json", "document_store.json"]
            for item in items_to_remove:
                path = Path(item)
                if path.exists():
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                        print(f"✅ 已删除目录: {item}")
                    else:
                        path.unlink()
                        print(f"✅ 已删除文件: {item}")
        
        print("✅ 向量数据库清理完成")
        return True
    except Exception as e:
        print(f"⚠️ 清理过程中出现错误: {e}")
        return False

def check_checkpoint():
    """检查是否有未完成的断点续传"""
    try:
        # 尝试导入断点续传处理器
        sys.path.append('.')  # 确保可以导入当前目录的模块
        from resume_processor import ResumeProcessor
        
        resume = ResumeProcessor()
        if resume.has_checkpoint():
            print("\n" + "="*60)
            print("🔄 检测到未完成的处理进度")
            
            # 读取检查点信息
            with open(resume.checkpoint_file, 'r', encoding='utf-8') as f:
                import json
                checkpoint_data = json.load(f)
            
            print(f"🕒 保存时间: {checkpoint_data.get('time_str', '未知')}")
            print(f"📈 进度: {checkpoint_data.get('current_idx', 0)}/{checkpoint_data.get('total', 0)} "
                  f"({checkpoint_data.get('completed_percentage', 0)}%)")
            print("="*60)
            
            choice = input("\n选择操作:\n1. 继续上次的处理 (推荐)\n2. 清除断点，从头开始\n请选择 (1/2，默认1): ").strip()
            
            if choice == '2':
                print("🧹 清除断点，将从头开始处理")
                resume.clear_checkpoint()
                return "clear"
            else:
                print("🔄 将继续上次的处理")
                return "resume"
        else:
            return "none"
    except Exception as e:
        print(f"⚠️ 检查断点时出错: {e}")
        return "error"

def start_system():
    """启动RAG系统"""
    print("\n🚀 启动RAG系统...")
    
    try:
        # 检查断点状态
        checkpoint_status = check_checkpoint()
        
        # 准备命令行参数
        cmd = [sys.executable, 'main.py']
        
        # 如果选择清除断点或没有断点，添加参数
        if checkpoint_status in ["clear", "none", "error"]:
            # 不传递特殊参数，系统会从头开始
            pass
        elif checkpoint_status == "resume":
            # 不需要额外参数，系统会自动检测断点
            pass
        
        # 运行主程序
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 系统启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 金融监管制度RAG问答系统 - 一键启动")
    print("=" * 60)
    
    # 检查依赖
    missing_required, missing_optional = check_dependencies()
    
    # 安装缺失的必需依赖
    if missing_required:
        print(f"\n⚠️ 发现 {len(missing_required)} 个缺失的必需依赖")
        if input("是否立即安装？(y/n): ").lower() == 'y':
            if not install_missing_packages(missing_required):
                print("❌ 依赖安装失败，请手动安装后重试")
                return
        else:
            print("❌ 缺失必需依赖，程序无法运行")
            return
    
    # 安装缺失的可选依赖(主要是文档处理)
    if missing_optional:
        print(f"\n⚠️ 发现 {len(missing_optional)} 个缺失的文档处理依赖")
        print("这些依赖对于正确处理Word文档(.docx)是必需的")
        if input("是否安装文档处理依赖？(推荐: y/n): ").lower() == 'y':
            install_missing_packages(missing_optional)
    
    # 检查项目结构
    if not check_project_structure():
        print("\n❌ 项目结构不完整，请检查缺失的文件和目录")
        return
    
    # 询问是否清理旧数据库
    print("\n🔄 数据库管理选项:")
    print("1. 保留现有向量数据库(如果存在)")
    print("2. 清除向量数据库，重新构建(推荐，修复乱码问题)")
    
    choice = input("请选择 (1/2，默认为2): ").strip()
    
    if choice != '1':
        clear_old_database()
    
    # 启动系统
    print("\n" + "=" * 60)
    print("🎉 准备工作完成，启动系统...")
    print("=" * 60)
    
    success = start_system()
    
    if success:
        print("\n✅ 系统运行完成")
    else:
        print("\n❌ 系统运行出现问题")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 启动过程中出现未预期的错误: {e}")
        print("请检查错误信息并重试") 