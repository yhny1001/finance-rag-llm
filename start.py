"""
一键启动脚本
自动检查依赖、清理旧数据库(可选)、启动RAG系统
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 添加各个模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), "tools"))
sys.path.append(os.path.join(os.path.dirname(__file__), "fix"))
sys.path.append(os.path.join(os.path.dirname(__file__), "test"))

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

def start_system(resume=False, batch_size=None, start_idx=None, end_idx=None):
    """启动RAG系统"""
    print("\n🚀 启动RAG系统...")
    
    try:
        # 构建命令行参数
        cmd = [sys.executable, 'main.py']
        
        # 添加断点续跑参数
        if resume:
            cmd.append('--resume')
            
        # 添加批处理参数
        if batch_size is not None:
            cmd.extend(['--batch-size', str(batch_size)])
            
        # 添加开始和结束索引
        if start_idx is not None:
            cmd.extend(['--start-idx', str(start_idx)])
            
        if end_idx is not None:
            cmd.extend(['--end-idx', str(end_idx)])
            
        # 运行主程序
        print(f"执行命令: {' '.join(cmd)}")
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
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="金融监管制度RAG问答系统 - 一键启动")
    parser.add_argument("--resume", action="store_true", help="断点续跑，不清除中间结果文件")
    parser.add_argument("--batch-size", type=int, help="批处理大小")
    parser.add_argument("--start-idx", type=int, help="开始索引")
    parser.add_argument("--end-idx", type=int, help="结束索引")
    parser.add_argument("--skip-deps-check", action="store_true", help="跳过依赖检查")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 金融监管制度RAG问答系统 - 一键启动")
    print("=" * 60)
    
    # 检查是否存在中间文件，并在命令行参数未指定resume的情况下询问用户
    if not args.resume:
        output_dir = Path("outputs")
        if output_dir.exists():
            batch_files = list(output_dir.glob("batch_results_*.json"))
            if batch_files:
                print(f"\n发现 {len(batch_files)} 个已有的批次结果文件:")
                for i, file in enumerate(sorted(batch_files)[:5]):  # 只显示前5个
                    print(f"   - {file.name}")
                if len(batch_files) > 5:
                    print(f"   - ... 等共 {len(batch_files)} 个文件")
                
                # 提示用户选择操作
                choice = input("\n请选择操作: \n1. 删除这些文件并重新开始 \n2. 保留文件并从断点续跑 \n请输入选择(1/2): ").strip()
                if choice == '2':
                    args.resume = True
                    print("已选择断点续跑模式")
                else:
                    print("已选择删除文件并重新开始")
    
    # 检查是否为断点续跑模式
    if args.resume:
        print("📌 断点续跑模式：将保留所有中间结果文件")
    
    # 检查依赖
    if not args.skip_deps_check:
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
    else:
        print("⏩ 已跳过依赖检查")
    
    # 检查项目结构
    if not check_project_structure():
        print("\n❌ 项目结构不完整，请检查缺失的文件和目录")
        return
    
    # 如果不是断点续跑模式，询问是否清理旧数据库
    if not args.resume:
        print("\n🔄 数据库管理选项:")
        print("1. 保留现有向量数据库(如果存在)")
        print("2. 清除向量数据库，重新构建(推荐，修复乱码问题)")
        
        choice = input("请选择 (1/2，默认为2): ").strip()
        
        if choice != '1':
            clear_old_database()
    else:
        print("\n🔄 断点续跑模式：保留现有向量数据库和中间文件")
    
    # 启动系统
    print("\n" + "=" * 60)
    print("🎉 准备工作完成，启动系统...")
    print("=" * 60)
    
    success = start_system(
        resume=args.resume,
        batch_size=args.batch_size,
        start_idx=args.start_idx,
        end_idx=args.end_idx
    )
    
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