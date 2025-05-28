"""
修复配置应用脚本
使用正确的服务器路径，保留所有必要的配置项
"""

import shutil
import os

def backup_old_config():
    """备份旧配置文件"""
    print("💾 备份旧配置文件")
    if os.path.exists("config.py"):
        shutil.copy2("config.py", "config_backup.py")
        print("✅ 已备份 config.py -> config_backup.py")
    else:
        print("⚠️ config.py 不存在")

def apply_fixed_config():
    """应用修复后的配置"""
    print("\n🔄 应用修复后的配置")
    
    if not os.path.exists("config_improved_fixed.py"):
        print("❌ config_improved_fixed.py 不存在")
        return False
    
    # 读取修复后配置的内容
    with open("config_improved_fixed.py", "r", encoding="utf-8") as f:
        fixed_content = f.read()
    
    # 写入config.py
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("✅ 已将修复后配置应用到 config.py")
    return True

def verify_config_fix():
    """验证配置修复"""
    print("\n✅ 验证配置修复")
    
    try:
        # 重新导入配置（清除模块缓存）
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import Config
        
        print(f"修复后的配置参数:")
        print(f"  LLM_MODEL_PATH: {Config.LLM_MODEL_PATH}")
        print(f"  EMBEDDING_MODEL_PATH: {Config.EMBEDDING_MODEL_PATH}")
        print(f"  CHUNK_SIZE: {Config.CHUNK_SIZE}")
        print(f"  TOP_K: {Config.TOP_K}")
        print(f"  SIMILARITY_THRESHOLD: {Config.SIMILARITY_THRESHOLD}")
        print(f"  FAISS_INDEX_FILE: {Config.FAISS_INDEX_FILE}")
        
        # 检查关键修复
        if "/mnt/workspace" in Config.LLM_MODEL_PATH:
            print("✅ 模型路径修复成功！使用服务器路径")
        else:
            print(f"❌ 模型路径修复失败: {Config.LLM_MODEL_PATH}")
            return False
            
        if hasattr(Config, 'FAISS_INDEX_FILE'):
            print("✅ FAISS_INDEX_FILE配置存在")
        else:
            print("❌ 缺少FAISS_INDEX_FILE配置")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def clear_and_prepare():
    """清理旧数据，准备重建"""
    print("\n🗑️ 清理旧数据")
    
    # 删除向量数据库
    if os.path.exists("vector_db"):
        try:
            shutil.rmtree("vector_db")
            print("✅ 删除旧向量数据库")
        except Exception as e:
            print(f"⚠️ 删除向量数据库失败: {e}")
    
    # 创建必要目录
    os.makedirs("vector_db", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    print("✅ 创建必要目录")

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能")
    
    try:
        from config import Config
        
        # 测试路径验证
        print("测试路径验证...")
        validation_issues = Config.validate_config()
        if validation_issues:
            print("⚠️ 发现配置问题:")
            for issue in validation_issues:
                print(f"  - {issue}")
        else:
            print("✅ 配置验证通过")
        
        # 测试配置方法
        print("测试配置方法...")
        gen_config = Config.get_improved_generation_config()
        retrieval_config = Config.get_retrieval_config()
        chunk_config = Config.get_chunking_config()
        
        print(f"  生成配置: {len(gen_config)} 项")
        print(f"  检索配置: {len(retrieval_config)} 项")
        print(f"  切片配置: {len(chunk_config)} 项")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🔧 修复配置并准备重建系统")
    print("=" * 60)
    
    # 1. 备份旧配置
    backup_old_config()
    
    # 2. 应用修复后的配置
    if not apply_fixed_config():
        print("❌ 配置应用失败")
        return
    
    # 3. 验证配置修复
    if not verify_config_fix():
        print("❌ 配置验证失败")
        return
    
    # 4. 清理并准备
    clear_and_prepare()
    
    # 5. 测试基本功能
    if test_basic_functionality():
        print("\n🎉 配置修复成功！")
        print("\n📋 下一步操作:")
        print("1. python -c \"from rag_engine import RAGEngine; rag = RAGEngine(); rag.build_index(force_rebuild=True)\"")
        print("2. python test_retrieval_quality.py")
        print("3. python main_improved.py")
        print("\n💡 如果还有问题，请运行 python diagnose_system.py")
    else:
        print("\n❌ 基本功能测试失败，请检查依赖和环境")

if __name__ == "__main__":
    main() 