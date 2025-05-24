"""
诊断切片修复问题的脚本
检查为什么修复后还是15598个文档片段
"""

import os
import sys
from vector_db import VectorDatabase
from config import Config
from config_improved import ImprovedConfig

def check_config_usage():
    """检查当前实际使用的配置"""
    print("🔍 检查配置文件使用情况")
    print("=" * 50)
    
    print("当前config.py配置:")
    print(f"  CHUNK_SIZE: {Config.CHUNK_SIZE}")
    print(f"  CHUNK_OVERLAP: {Config.CHUNK_OVERLAP}")
    print(f"  TOP_K: {Config.TOP_K}")
    
    print("\nconfig_improved.py配置:")
    print(f"  CHUNK_SIZE: {ImprovedConfig.CHUNK_SIZE}")
    print(f"  CHUNK_OVERLAP: {ImprovedConfig.CHUNK_OVERLAP}")
    print(f"  TOP_K: {ImprovedConfig.TOP_K}")
    
    # 检查哪个配置被实际导入
    print(f"\n当前Python模块中的config:")
    if 'config' in sys.modules:
        config_module = sys.modules['config']
        print(f"  模块路径: {config_module.__file__}")
        print(f"  CHUNK_SIZE: {getattr(config_module, 'Config', {}).CHUNK_SIZE if hasattr(config_module, 'Config') else '未找到'}")

def check_vector_db_files():
    """检查向量数据库文件"""
    print("\n📁 检查向量数据库文件")
    print("=" * 50)
    
    if os.path.exists("vector_db"):
        files = os.listdir("vector_db")
        print(f"vector_db目录中的文件: {files}")
        
        for file in files:
            if not file.startswith("demo_"):
                file_path = os.path.join("vector_db", file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    import datetime
                    mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  {file}: {size} bytes, 修改时间: {mtime_str}")
    else:
        print("❌ vector_db目录不存在")

def analyze_chunk_distribution():
    """分析当前切片分布"""
    print("\n📊 分析当前切片分布")
    print("=" * 50)
    
    try:
        vdb = VectorDatabase()
        if not vdb.load_from_disk():
            print("❌ 无法加载向量数据库")
            return
        
        total_chunks = len(vdb.document_store)
        print(f"总片段数: {total_chunks}")
        
        # 分析长度分布
        lengths = []
        for chunk_data in vdb.document_store.values():
            text = chunk_data.get('text', '')
            lengths.append(len(text))
        
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            max_len = max(lengths)
            min_len = min(lengths)
            
            print(f"平均长度: {avg_len:.1f} 字符")
            print(f"最大长度: {max_len} 字符")
            print(f"最小长度: {min_len} 字符")
            
            # 长度分布统计
            ranges = {
                "0-10": len([l for l in lengths if 0 <= l <= 10]),
                "11-50": len([l for l in lengths if 11 <= l <= 50]),
                "51-200": len([l for l in lengths if 51 <= l <= 200]),
                "201-500": len([l for l in lengths if 201 <= l <= 500]),
                "501-1000": len([l for l in lengths if 501 <= l <= 1000]),
                "1000+": len([l for l in lengths if l > 1000])
            }
            
            print("\n长度分布:")
            for range_name, count in ranges.items():
                percentage = (count / total_chunks) * 100
                print(f"  {range_name}: {count} 个 ({percentage:.1f}%)")
            
            # 检查是否有超过1000字符的片段（说明使用了新配置）
            long_chunks = ranges["1000+"]
            if long_chunks > 0:
                print(f"\n✅ 发现 {long_chunks} 个超过1000字符的片段，说明使用了新配置")
            else:
                print(f"\n⚠️ 没有发现超过1000字符的片段，可能还在使用旧配置")
                
            # 检查最大长度是否接近新的CHUNK_SIZE
            if max_len > 800:
                print(f"✅ 最大片段长度 {max_len} 接近新配置的CHUNK_SIZE (1000)")
            else:
                print(f"⚠️ 最大片段长度 {max_len} 仍然接近旧配置的CHUNK_SIZE (512)")
                
    except Exception as e:
        print(f"❌ 分析失败: {e}")

def check_duplicate_chunks():
    """检查是否还有重复切片"""
    print("\n🔍 检查重复切片问题")
    print("=" * 50)
    
    try:
        vdb = VectorDatabase()
        if not vdb.load_from_disk():
            print("❌ 无法加载向量数据库")
            return
        
        # 检查是否有高度相似的片段
        texts = []
        for chunk_data in vdb.document_store.values():
            text = chunk_data.get('text', '').strip()
            if text:
                texts.append(text)
        
        # 寻找相似的文本片段
        similar_pairs = 0
        sample_similar = []
        
        for i in range(min(100, len(texts))):  # 只检查前100个，避免太慢
            text1 = texts[i]
            for j in range(i+1, min(i+20, len(texts))):  # 检查后续20个
                text2 = texts[j]
                
                # 计算相似度（简单的字符相似度）
                if len(text1) > 10 and len(text2) > 10:
                    common_length = 0
                    min_len = min(len(text1), len(text2))
                    
                    for k in range(min_len):
                        if text1[k] == text2[k]:
                            common_length += 1
                        else:
                            break
                    
                    similarity = common_length / min_len
                    if similarity > 0.8:  # 80%相似
                        similar_pairs += 1
                        if len(sample_similar) < 5:
                            sample_similar.append((text1[:100], text2[:100], similarity))
        
        print(f"发现 {similar_pairs} 对高度相似的片段")
        
        if sample_similar:
            print("\n相似片段样例:")
            for i, (t1, t2, sim) in enumerate(sample_similar):
                print(f"  {i+1}. 相似度: {sim:.2f}")
                print(f"     片段1: {repr(t1)}...")
                print(f"     片段2: {repr(t2)}...")
        
        if similar_pairs > total_chunks * 0.1:  # 如果超过10%是相似的
            print("⚠️ 检测到大量相似片段，可能仍然存在重复切片问题")
        else:
            print("✅ 重复切片问题基本解决")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def test_new_chunking_algorithm():
    """测试新的切片算法实际效果"""
    print("\n🧪 测试新切片算法")
    print("=" * 50)
    
    test_text = "银行应当建立完善的风险管理体系，包括风险识别、风险评估、风险控制等环节。商业银行的资本充足率不得低于8%，一级资本充足率不得低于6%，核心一级资本充足率不得低于5%。银行应当按照监管要求，定期报告资本充足率情况，确保资本水平满足监管标准。同时，银行还应当建立资本规划机制，合理安排资本补充计划。" * 5  # 重复5次，确保超过1000字符
    
    print(f"测试文本长度: {len(test_text)} 字符")
    
    # 使用当前配置进行切片
    from vector_db import VectorDatabase
    
    # 创建临时VectorDatabase实例来测试切片
    vdb = VectorDatabase()
    chunks = vdb._split_document(test_text)
    
    print(f"\n切片结果:")
    print(f"  总片段数: {len(chunks)}")
    
    for i, chunk in enumerate(chunks[:3]):  # 只显示前3个
        print(f"  片段{i+1} (长度{len(chunk)}): {repr(chunk[:100])}...")
    
    # 分析片段长度
    chunk_lengths = [len(chunk) for chunk in chunks]
    if chunk_lengths:
        avg_len = sum(chunk_lengths) / len(chunk_lengths)
        max_len = max(chunk_lengths)
        print(f"\n  平均片段长度: {avg_len:.1f}")
        print(f"  最大片段长度: {max_len}")
        
        if max_len > 800:
            print("✅ 切片长度符合新配置预期")
        else:
            print("⚠️ 切片长度仍然偏小，可能使用了旧配置")

def main():
    """主函数"""
    print("🔧 诊断切片修复问题")
    print("=" * 60)
    
    check_config_usage()
    check_vector_db_files()
    analyze_chunk_distribution()
    check_duplicate_chunks()
    test_new_chunking_algorithm()
    
    print("\n📋 诊断总结:")
    print("1. 如果最大片段长度仍然是512，说明还在使用旧配置")
    print("2. 如果发现大量相似片段，说明重复切片问题未解决")
    print("3. 如果文件修改时间很早，说明向量数据库没有重建")
    print("4. 如果15598这个数字没变，说明重建过程可能失败了")

if __name__ == "__main__":
    main() 