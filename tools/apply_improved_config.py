"""
应用改进配置的脚本
用config_improved.py覆盖config.py，让所有代码自动使用新配置
"""

import shutil
import os

def backup_old_config():
    """备份旧配置文件"""
    print("💾 备份旧配置文件")
    if os.path.exists("config.py"):
        shutil.copy2("config.py", "config_old.py")
        print("✅ 已备份 config.py -> config_old.py")
    else:
        print("⚠️ config.py 不存在")

def apply_improved_config():
    """应用改进的配置"""
    print("\n🔄 应用改进配置")
    
    if not os.path.exists("config_improved.py"):
        print("❌ config_improved.py 不存在")
        return False
    
    # 读取改进配置的内容
    with open("config_improved.py", "r", encoding="utf-8") as f:
        improved_content = f.read()
    
    # 替换类名，让它与原来的导入兼容
    # 将 ImprovedConfig 替换为 Config
    new_content = improved_content.replace("class ImprovedConfig:", "class Config:")
    new_content = new_content.replace("Config = ImprovedConfig", "")
    
    # 写入config.py
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ 已将改进配置应用到 config.py")
    return True

def verify_config_change():
    """验证配置是否成功更改"""
    print("\n✅ 验证配置更改")
    
    try:
        # 重新导入配置（清除模块缓存）
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import Config
        
        print(f"新的配置参数:")
        print(f"  CHUNK_SIZE: {Config.CHUNK_SIZE}")
        print(f"  CHUNK_OVERLAP: {Config.CHUNK_OVERLAP}")
        print(f"  TOP_K: {Config.TOP_K}")
        print(f"  SIMILARITY_THRESHOLD: {Config.SIMILARITY_THRESHOLD}")
        
        if Config.CHUNK_SIZE == 1000:
            print("✅ 配置更改成功！CHUNK_SIZE已更新为1000")
            return True
        else:
            print(f"❌ 配置更改失败，CHUNK_SIZE仍然是{Config.CHUNK_SIZE}")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def clear_vector_db():
    """清理旧的向量数据库，强制重建"""
    print("\n🗑️ 清理旧向量数据库")
    
    if os.path.exists("vector_db"):
        try:
            # 删除所有非演示文件
            for file in os.listdir("vector_db"):
                if not file.startswith("demo_"):
                    file_path = os.path.join("vector_db", file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"删除文件: {file}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"删除目录: {file}")
            print("✅ 向量数据库清理完成")
        except Exception as e:
            print(f"⚠️ 清理过程中出错: {e}")
    else:
        print("⚠️ vector_db目录不存在")

def rebuild_vector_database():
    """重建向量数据库"""
    print("\n🚀 重建向量数据库")
    
    try:
        # 重新导入模块，确保使用新配置
        import sys
        modules_to_reload = ['config', 'vector_db', 'rag_engine']
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]
        
        from rag_engine import RAGEngine
        
        print("创建RAG引擎...")
        rag = RAGEngine()
        
        print("开始重建索引...")
        rag.build_index(force_rebuild=True)
        
        # 验证重建结果
        stats = rag.get_vector_db_stats()
        print(f"\n✅ 重建完成！")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 重建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_improvement():
    """验证改进效果"""
    print("\n📊 验证改进效果")
    
    try:
        from vector_db import VectorDatabase
        
        vdb = VectorDatabase()
        if not vdb.load_from_disk():
            print("❌ 无法加载重建后的向量数据库")
            return False
        
        total_chunks = len(vdb.document_store)
        
        # 分析新的切片质量
        lengths = []
        for chunk_data in vdb.document_store.values():
            text = chunk_data.get('text', '')
            lengths.append(len(text))
        
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            max_len = max(lengths)
            min_len = min(lengths)
            
            long_chunks = len([l for l in lengths if l > 800])
            short_chunks = len([l for l in lengths if l < 50])
            
            print(f"重建后统计:")
            print(f"  总片段数: {total_chunks}")
            print(f"  平均长度: {avg_len:.1f} 字符")
            print(f"  最大长度: {max_len} 字符")
            print(f"  最小长度: {min_len} 字符")
            print(f"  长片段(>800字符): {long_chunks} 个 ({long_chunks/total_chunks*100:.1f}%)")
            print(f"  短片段(<50字符): {short_chunks} 个 ({short_chunks/total_chunks*100:.1f}%)")
            
            # 成功标准
            if max_len > 800 and avg_len > 500 and short_chunks/total_chunks < 0.1:
                print("✅ 切片质量显著改善！")
                return True
            else:
                print("⚠️ 切片质量有改善但仍需优化")
                return False
    
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 应用改进配置并重建向量数据库")
    print("=" * 60)
    
    # 1. 备份旧配置
    backup_old_config()
    
    # 2. 应用改进配置
    if not apply_improved_config():
        print("❌ 配置应用失败")
        return
    
    # 3. 验证配置更改
    if not verify_config_change():
        print("❌ 配置验证失败")
        return
    
    # 4. 清理旧向量数据库
    clear_vector_db()
    
    # 5. 重建向量数据库
    if rebuild_vector_database():
        # 6. 验证改进效果
        if verify_improvement():
            print("\n🎉 配置应用和数据库重建成功！")
            print("\n📋 现在可以运行:")
            print("1. python test_retrieval_quality.py")
            print("2. python main_improved.py")
            print("3. 检查系统分数提升情况")
        else:
            print("\n⚠️ 重建完成但效果有待验证")
    else:
        print("\n❌ 数据库重建失败")

if __name__ == "__main__":
    main() 