"""
快速重建脚本
一键清理并重建整个RAG系统，解决分数低的问题
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
import time

def print_step(step_num, description):
    """打印步骤信息"""
    print(f"\n{'='*10} 步骤 {step_num}: {description} {'='*10}")

def run_command(command, description="", check=True):
    """运行命令并处理错误"""
    print(f"🔧 执行: {description if description else command}")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"✅ 输出: {result.stdout.strip()}")
        if result.stderr and not check:
            print(f"⚠️ 警告: {result.stderr.strip()}")
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def clear_vector_database():
    """清理向量数据库"""
    print_step(1, "清理向量数据库")
    
    vector_db_paths = [
        "vector_db",
        "cache",
        "__pycache__",
    ]
    
    for path in vector_db_paths:
        path_obj = Path(path)
        if path_obj.exists():
            try:
                if path_obj.is_file():
                    path_obj.unlink()
                    print(f"✅ 删除文件: {path}")
                else:
                    shutil.rmtree(path)
                    print(f"✅ 删除目录: {path}")
            except Exception as e:
                print(f"⚠️ 删除 {path} 失败: {e}")
        else:
            print(f"ℹ️ 路径不存在: {path}")
    
    # 清理中间文件
    temp_files = list(Path(".").glob("*.log")) + list(Path(".").glob("*.tmp"))
    for temp_file in temp_files:
        try:
            temp_file.unlink()
            print(f"✅ 删除临时文件: {temp_file}")
        except Exception as e:
            print(f"⚠️ 删除 {temp_file} 失败: {e}")

def check_environment():
    """检查环境"""
    print_step(2, "检查环境")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = [
        "main.py",
        "config.py", 
        "rag_engine.py",
        "金融监管制度问答-测试集.jsonl"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ 找到文件: {file}")
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    # 检查documents目录
    docs_dir = Path("documents")
    if not docs_dir.exists():
        print(f"❌ 文档目录不存在: {docs_dir}")
        return False
    
    docx_files = list(docs_dir.glob("*.docx"))
    print(f"✅ 找到Word文档: {len(docx_files)} 个")
    
    if len(docx_files) == 0:
        print("❌ 没有找到Word文档")
        return False
    
    return True

def run_diagnostics():
    """运行诊断"""
    print_step(3, "运行系统诊断")
    
    print("📊 运行系统诊断脚本...")
    success = run_command([sys.executable, "diagnose_system.py"], "系统诊断", check=False)
    
    if not success:
        print("⚠️ 诊断脚本运行有问题，但继续执行重建")
    
    return True

def rebuild_system():
    """重建系统"""
    print_step(4, "重建RAG系统")
    
    print("🚀 使用改进配置重建系统...")
    
    # 首先尝试改进版
    success = run_command([sys.executable, "main_improved.py", "--force-rebuild"], 
                         "改进版系统重建", check=False)
    
    if not success:
        print("⚠️ 改进版重建失败，尝试原版重建...")
        success = run_command([sys.executable, "main.py", "--force-rebuild"], 
                             "原版系统重建", check=False)
    
    return success

def test_retrieval():
    """测试检索质量"""
    print_step(5, "测试检索质量")
    
    print("🔍 运行检索质量测试...")
    success = run_command([sys.executable, "test_retrieval_quality.py"], 
                         "检索质量测试", check=False)
    
    if not success:
        print("⚠️ 检索测试失败，但继续执行")
    
    return True

def run_final_test():
    """运行最终测试"""
    print_step(6, "运行最终测试")
    
    print("📝 运行完整测试...")
    
    # 优先使用改进版
    success = run_command([sys.executable, "main_improved.py"], 
                         "改进版完整测试", check=False)
    
    if not success:
        print("⚠️ 改进版测试失败，尝试原版测试...")
        success = run_command([sys.executable, "main.py"], 
                             "原版完整测试", check=False)
    
    return success

def check_results():
    """检查结果"""
    print_step(7, "检查结果")
    
    result_files = list(Path(".").glob("result*.json"))
    
    if not result_files:
        print("❌ 没有找到result文件")
        return False
    
    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
    print(f"✅ 找到结果文件: {latest_file}")
    
    # 简单分析结果
    try:
        import json
        results = []
        with open(latest_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        
        total = len(results)
        errors = sum(1 for r in results if 'error' in r)
        success_rate = ((total - errors) / total * 100) if total > 0 else 0
        
        print(f"📊 结果统计:")
        print(f"  总问题数: {total}")
        print(f"  成功处理: {total - errors}")
        print(f"  处理失败: {errors}")
        print(f"  成功率: {success_rate:.2f}%")
        
        if success_rate > 95:
            print("✅ 重建成功，系统运行良好")
        elif success_rate > 80:
            print("🟡 重建基本成功，仍有优化空间")
        else:
            print("🔴 重建效果不佳，需要进一步诊断")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ 分析结果失败: {e}")
        return False

def main():
    """主函数"""
    print("🛠️ 金融监管RAG系统快速重建工具")
    print("=" * 60)
    print("本工具将:")
    print("1. 清理向量数据库和缓存")
    print("2. 检查环境配置")
    print("3. 运行系统诊断")
    print("4. 重建RAG系统")
    print("5. 测试检索质量")
    print("6. 运行完整测试")
    print("7. 检查结果")
    print("=" * 60)
    
    # 确认执行
    try:
        confirm = input("\n是否开始重建? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 用户取消操作")
            return
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        return
    
    start_time = time.time()
    
    # 执行重建步骤
    steps = [
        (clear_vector_database, "清理向量数据库"),
        (check_environment, "检查环境"),
        (run_diagnostics, "运行诊断"),
        (rebuild_system, "重建系统"),
        (test_retrieval, "测试检索"),
        (run_final_test, "运行测试"),
        (check_results, "检查结果"),
    ]
    
    failed_steps = []
    
    for i, (step_func, step_name) in enumerate(steps, 1):
        try:
            success = step_func()
            if not success:
                failed_steps.append(step_name)
                if step_name in ["检查环境", "重建系统"]:  # 关键步骤失败则停止
                    print(f"❌ 关键步骤 '{step_name}' 失败，停止执行")
                    break
        except Exception as e:
            print(f"❌ 步骤 '{step_name}' 异常: {e}")
            failed_steps.append(step_name)
    
    # 总结
    total_time = time.time() - start_time
    print(f"\n" + "="*60)
    print("🎯 重建完成总结")
    print("="*60)
    print(f"总耗时: {total_time:.1f} 秒")
    
    if not failed_steps:
        print("✅ 所有步骤执行成功")
        print("\n📋 下一步建议:")
        print("1. 查看 result.json 了解答案质量")
        print("2. 如果分数仍然不理想，运行:")
        print("   python compare_results.py baseline.json result.json")
        print("3. 继续调整参数或联系技术支持")
    else:
        print(f"⚠️ 以下步骤执行失败: {failed_steps}")
        print("\n🔧 故障排除建议:")
        print("1. 检查Python环境和依赖包")
        print("2. 确保所有必要文件存在")
        print("3. 检查磁盘空间和权限")
        print("4. 运行单独的诊断脚本:")
        print("   python diagnose_system.py")
    
    print(f"\n📧 如需技术支持，请提供:")
    print("1. 重建日志输出")
    print("2. diagnose_system.py 的输出")
    print("3. 系统环境信息")

if __name__ == "__main__":
    main() 