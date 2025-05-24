"""
修复文档切片算法BUG并重建向量数据库
解决切片重复、片段过短等问题
"""

import os
import shutil
from pathlib import Path
from vector_db import VectorDatabase
from rag_engine import RAGEngine
from config_improved import ImprovedConfig

def analyze_current_chunking_bug():
    """分析当前切片算法的问题"""
    print("🔍 分析当前切片算法问题")
    print("=" * 50)
    
    # 模拟当前切片算法
    test_text = "目的发生额分析填列。净利润，是指融资性担保机构实现的净利润；如为净亏损，前加\"-\"号填列。这是一个测试文本，用来验证切片算法。"
    
    print(f"测试文本: {test_text}")
    print(f"文本长度: {len(test_text)} 字符")
    
    # 当前有问题的切片逻辑
    chunk_size = 512
    chunk_overlap = 50
    
    print(f"\n当前配置: CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={chunk_overlap}")
    
    # 模拟有问题的切片算法
    chunks = []
    start = 0
    
    while start < len(test_text):
        end = start + chunk_size
        
        # 这里可能是问题所在 - 错误的边界处理
        if end < len(test_text):
            for sep in ['\n\n', '\n', '。', '！', '？', ';', '.']:
                sep_pos = test_text.rfind(sep, start, end)
                if sep_pos > start:
                    end = sep_pos + len(sep)
                    break
        
        chunk = test_text[start:end].strip()
        if chunk:
            chunks.append((start, end, chunk))
        
        # 这里可能有BUG
        start = max(start + 1, end - chunk_overlap)  # 问题：start + 1 导致重复切片
    
    print(f"\n有问题的切片结果 ({len(chunks)} 个片段):")
    for i, (start, end, chunk) in enumerate(chunks[:5]):
        print(f"  {i+1}. [{start}:{end}] (长度{len(chunk)}): {repr(chunk)}")

def backup_current_database():
    """备份当前向量数据库"""
    print("\n💾 备份当前向量数据库")
    print("-" * 30)
    
    if os.path.exists("vector_db"):
        backup_dir = "vector_db_backup"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree("vector_db", backup_dir)
        print(f"✅ 已备份到 {backup_dir}")
    else:
        print("⚠️ 向量数据库目录不存在，无需备份")

def clear_problematic_database():
    """清理有问题的向量数据库"""
    print("\n🗑️ 清理有问题的向量数据库")
    print("-" * 30)
    
    if os.path.exists("vector_db"):
        # 只保留演示文件，删除真实数据库文件
        for file in os.listdir("vector_db"):
            if not file.startswith("demo_"):
                file_path = os.path.join("vector_db", file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"删除文件: {file}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"删除目录: {file}")
                except Exception as e:
                    print(f"删除 {file} 时出错: {e}")
        print("✅ 清理完成")
    else:
        print("⚠️ 向量数据库目录不存在")

def test_improved_chunking():
    """测试改进的切片算法"""
    print("\n🔧 测试改进的切片算法")
    print("-" * 30)
    
    test_text = "目的发生额分析填列。净利润，是指融资性担保机构实现的净利润；如为净亏损，前加\"-\"号填列。这是一个测试文本，用来验证切片算法。银行应当建立完善的风险管理体系，包括风险识别、风险评估、风险控制等环节。商业银行的资本充足率不得低于8%，一级资本充足率不得低于6%。"
    
    print(f"测试文本长度: {len(test_text)} 字符")
    
    # 改进的切片算法
    chunk_size = ImprovedConfig.CHUNK_SIZE  # 1000
    chunk_overlap = ImprovedConfig.CHUNK_OVERLAP  # 200
    
    print(f"改进配置: CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={chunk_overlap}")
    
    chunks = []
    start = 0
    
    while start < len(test_text):
        end = min(start + chunk_size, len(test_text))
        
        # 如果不是最后一个片段，尝试在句号等位置切分
        if end < len(test_text):
            for sep in ['。', '！', '？', '\n\n', '\n', ';', '.']:
                sep_pos = test_text.rfind(sep, start + chunk_size // 2, end)  # 在后半部分寻找分隔符
                if sep_pos > start:
                    end = sep_pos + len(sep)
                    break
        
        chunk = test_text[start:end].strip()
        if chunk and len(chunk) >= 20:  # 过滤掉过短的片段
            chunks.append((start, end, chunk))
        
        # 修正：正确的步长计算
        if end >= len(test_text):
            break
        start = end - chunk_overlap  # 正确的重叠计算
        
        # 防止无限循环
        if start <= 0:
            start = end // 2
    
    print(f"\n改进的切片结果 ({len(chunks)} 个片段):")
    for i, (start, end, chunk) in enumerate(chunks):
        print(f"  {i+1}. [{start}:{end}] (长度{len(chunk)}): {repr(chunk[:100])}...")

def rebuild_with_improved_config():
    """使用改进配置重建向量数据库"""
    print("\n🚀 使用改进配置重建向量数据库")
    print("=" * 50)
    
    # 临时修改配置导入
    import sys
    sys.modules['config'] = __import__('config_improved')
    
    try:
        # 使用改进配置创建RAG引擎
        from config_improved import ImprovedConfig as Config
        
        print("配置参数:")
        print(f"  CHUNK_SIZE: {Config.CHUNK_SIZE}")
        print(f"  CHUNK_OVERLAP: {Config.CHUNK_OVERLAP}")
        print(f"  TOP_K: {Config.TOP_K}")
        print(f"  SIMILARITY_THRESHOLD: {Config.SIMILARITY_THRESHOLD}")
        
        # 创建RAG引擎并重建索引
        rag_engine = RAGEngine()
        print("\n开始重建向量索引...")
        rag_engine.build_index(force_rebuild=True)
        
        # 验证重建结果
        stats = rag_engine.get_vector_db_stats()
        print(f"\n✅ 重建完成！向量数据库统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 重建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_fix():
    """验证修复效果"""
    print("\n✅ 验证修复效果")
    print("=" * 50)
    
    try:
        # 创建新的向量数据库实例进行验证
        vdb = VectorDatabase()
        if not vdb.load_from_disk():
            print("❌ 无法加载重建后的向量数据库")
            return False
        
        stats = vdb.get_statistics()
        total_chunks = len(vdb.document_store)
        
        print(f"重建后统计:")
        print(f"  总片段数: {total_chunks}")
        
        # 分析新的片段质量
        chunk_lengths = []
        short_chunks = 0
        empty_chunks = 0
        
        for chunk_data in vdb.document_store.values():
            length = len(chunk_data.get('text', ''))
            chunk_lengths.append(length)
            if length < 50:
                short_chunks += 1
            if length < 10:
                empty_chunks += 1
        
        avg_length = sum(chunk_lengths) / len(chunk_lengths)
        
        print(f"  平均长度: {avg_length:.1f} 字符")
        print(f"  短片段率: {short_chunks/total_chunks*100:.1f}% (目标<5%)")
        print(f"  空片段率: {empty_chunks/total_chunks*100:.1f}% (目标<1%)")
        
        # 质量评估
        if short_chunks/total_chunks < 0.05 and empty_chunks/total_chunks < 0.01:
            print("✅ 切片质量显著改善!")
            return True
        else:
            print("⚠️ 切片质量仍需进一步优化")
            return False
    
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🛠️ 文档切片BUG修复工具")
    print("=" * 60)
    
    # 1. 分析当前问题
    analyze_current_chunking_bug()
    
    # 2. 备份当前数据库
    backup_current_database()
    
    # 3. 测试改进算法
    test_improved_chunking()
    
    # 4. 清理有问题的数据库
    clear_problematic_database()
    
    # 5. 重建向量数据库
    if rebuild_with_improved_config():
        # 6. 验证修复效果
        if verify_fix():
            print("\n🎉 修复成功！")
            print("\n📋 后续步骤:")
            print("1. 运行 python test_retrieval_quality.py 测试检索质量")
            print("2. 运行 python main_improved.py 进行完整测试")
            print("3. 检查系统分数是否有显著提升")
        else:
            print("\n⚠️ 修复不完全，可能需要进一步调整参数")
    else:
        print("\n❌ 修复失败，请检查错误信息")

if __name__ == "__main__":
    main() 