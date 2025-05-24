"""
文档切片质量分析脚本
分析向量数据库中文档片段的质量问题，找出得分低的根因
"""

import json
import random
from collections import defaultdict, Counter
from vector_db import VectorDatabase
from config import Config

def analyze_chunk_quality():
    """分析文档切片质量"""
    print("🔍 文档切片质量分析")
    print("=" * 60)
    
    # 加载向量数据库
    vdb = VectorDatabase()
    if not vdb.load_from_disk():
        print("❌ 无法加载向量数据库")
        return
    
    print("✅ 向量数据库加载成功")
    stats = vdb.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n📊 文档片段长度分析")
    print("-" * 40)
    
    # 分析所有文档片段
    chunk_lengths = []
    short_chunks = []  # 长度小于50的短片段
    empty_chunks = []  # 空或几乎空的片段
    title_chunks = []  # 可能是标题的片段
    
    total_chunks = len(vdb.document_store)
    print(f"总文档片段数: {total_chunks}")
    
    for chunk_id, chunk_data in vdb.document_store.items():
        text = chunk_data.get('text', '')
        length = len(text)
        chunk_lengths.append(length)
        
        if length < 50:
            short_chunks.append((chunk_id, text))
        
        if length < 10:
            empty_chunks.append((chunk_id, text))
        
        # 检测可能的标题片段（短且包含标点）
        if length < 100 and ('《' in text or '》' in text or '的通知' in text):
            title_chunks.append((chunk_id, text))
    
    # 长度统计
    avg_length = sum(chunk_lengths) / len(chunk_lengths)
    sorted_lengths = sorted(chunk_lengths)
    median_length = sorted_lengths[len(sorted_lengths) // 2]
    
    print(f"平均长度: {avg_length:.1f} 字符")
    print(f"中位数长度: {median_length} 字符")
    print(f"最短片段: {min(chunk_lengths)} 字符")
    print(f"最长片段: {max(chunk_lengths)} 字符")
    
    # 长度分布
    length_ranges = {
        "极短(0-10)": len([l for l in chunk_lengths if 0 <= l <= 10]),
        "很短(11-50)": len([l for l in chunk_lengths if 11 <= l <= 50]),
        "短(51-200)": len([l for l in chunk_lengths if 51 <= l <= 200]),
        "中等(201-500)": len([l for l in chunk_lengths if 201 <= l <= 500]),
        "长(501+)": len([l for l in chunk_lengths if l > 500])
    }
    
    print(f"\n📈 长度分布:")
    for range_name, count in length_ranges.items():
        percentage = (count / total_chunks) * 100
        print(f"  {range_name}: {count} 个 ({percentage:.1f}%)")
    
    # 问题片段分析
    print(f"\n⚠️ 问题片段分析")
    print("-" * 40)
    print(f"短片段(<50字符): {len(short_chunks)} 个 ({len(short_chunks)/total_chunks*100:.1f}%)")
    print(f"空片段(<10字符): {len(empty_chunks)} 个 ({len(empty_chunks)/total_chunks*100:.1f}%)")
    print(f"疑似标题片段: {len(title_chunks)} 个 ({len(title_chunks)/total_chunks*100:.1f}%)")
    
    # 显示问题片段样例
    if short_chunks:
        print(f"\n🔍 短片段样例 (前10个):")
        for i, (chunk_id, text) in enumerate(short_chunks[:10]):
            print(f"  {i+1}. [{chunk_id}] (长度{len(text)}): {repr(text)}")
    
    if title_chunks:
        print(f"\n📄 疑似标题片段样例 (前10个):")
        for i, (chunk_id, text) in enumerate(title_chunks[:10]):
            print(f"  {i+1}. [{chunk_id}] (长度{len(text)}): {repr(text)}")
    
    return analyze_specific_queries(vdb)

def analyze_specific_queries(vdb):
    """分析特定查询的检索质量"""
    print(f"\n🎯 特定查询分析")
    print("=" * 60)
    
    # 测试查询
    test_queries = [
        ("流动性覆盖率LCR最低要求", ["流动性覆盖率", "LCR", "100%", "不低于"]),
        ("银行杠杆率监管要求", ["杠杆率", "4%", "不低于", "一级资本"]),
        ("银行间同业拆借利率", ["同业拆借", "利率", "银行间", "资金"])
    ]
    
    for query, expected_keywords in test_queries:
        print(f"\n查询: {query}")
        print("-" * 30)
        
        # 执行搜索
        results = vdb.search(query, top_k=5)
        
        if not results:
            print("❌ 无搜索结果")
            continue
        
        print(f"检索到 {len(results)} 个结果")
        
        # 分析每个结果
        for i, result in enumerate(results):
            text = result.get('text', '')
            score = result.get('score', 0)
            chunk_id = result.get('chunk_id', '')
            
            print(f"\n结果 {i+1}:")
            print(f"  片段ID: {chunk_id}")
            print(f"  相似度: {score:.3f}")
            print(f"  长度: {len(text)} 字符")
            print(f"  内容: {repr(text[:100])}...")
            
            # 关键词匹配分析
            found_keywords = [kw for kw in expected_keywords if kw in text]
            print(f"  期望关键词: {expected_keywords}")
            print(f"  匹配关键词: {found_keywords}")
            print(f"  匹配率: {len(found_keywords)/len(expected_keywords)*100:.1f}%")
            
            # 内容质量评估
            has_numbers = any(char.isdigit() for char in text)
            has_percentage = '%' in text
            has_punctuation = any(p in text for p in ['。', '，', '；', '：'])
            
            print(f"  包含数字: {has_numbers}")
            print(f"  包含百分比: {has_percentage}")
            print(f"  有标点符号: {has_punctuation}")
            
            # 判断内容类型
            if len(text) < 50:
                content_type = "片段过短"
            elif '通知' in text and len(text) < 100:
                content_type = "疑似标题"
            elif not has_punctuation:
                content_type = "可能是表格片段"
            else:
                content_type = "正常内容"
            
            print(f"  内容类型: {content_type}")

def analyze_config_impact():
    """分析配置参数对切片质量的影响"""
    print(f"\n⚙️ 配置参数分析")
    print("=" * 60)
    
    print(f"当前配置:")
    print(f"  CHUNK_SIZE: {Config.CHUNK_SIZE}")
    print(f"  CHUNK_OVERLAP: {Config.CHUNK_OVERLAP}")
    print(f"  TOP_K: {Config.TOP_K}")
    print(f"  SIMILARITY_THRESHOLD: {Config.SIMILARITY_THRESHOLD}")
    
    print(f"\n📋 切片配置建议:")
    if Config.CHUNK_SIZE < 800:
        print(f"  ⚠️ CHUNK_SIZE ({Config.CHUNK_SIZE}) 过小，建议增加到 1000-1200")
        print(f"     小切片容易导致信息不完整，特别是复杂的监管条文")
    
    if Config.CHUNK_OVERLAP < 100:
        print(f"  ⚠️ CHUNK_OVERLAP ({Config.CHUNK_OVERLAP}) 过小，建议增加到 150-200")
        print(f"     更大的重叠有助于保持语义连续性")
    
    if Config.TOP_K < 8:
        print(f"  ⚠️ TOP_K ({Config.TOP_K}) 过小，建议增加到 8-10")
        print(f"     增加检索数量可以提供更多上下文")

def recommend_solutions():
    """推荐解决方案"""
    print(f"\n💡 解决方案建议")
    print("=" * 60)
    
    print(f"1. 🔧 更新配置参数")
    print(f"   - 使用 config_improved.py 替代 config.py")
    print(f"   - CHUNK_SIZE: 512 → 1000")
    print(f"   - CHUNK_OVERLAP: 50 → 200")
    print(f"   - TOP_K: 5 → 10")
    
    print(f"\n2. 🔄 重建向量数据库")
    print(f"   - python main_improved.py --force-rebuild")
    print(f"   - 使用改进的切片参数重新处理文档")
    
    print(f"\n3. 📝 文档预处理优化")
    print(f"   - 移除页眉页脚和标题片段")
    print(f"   - 合并短段落，确保语义完整性")
    print(f"   - 过滤掉长度小于100字符的片段")
    
    print(f"\n4. 🎯 检索优化")
    print(f"   - 实施二阶段检索：粗检索 + 重排序")
    print(f"   - 基于关键词覆盖率进行结果过滤")
    print(f"   - 增加同义词扩展")

def main():
    """主函数"""
    print("🚀 启动文档切片质量分析")
    
    analyze_chunk_quality()
    analyze_config_impact() 
    recommend_solutions()
    
    print(f"\n✅ 分析完成！")
    print(f"\n📌 核心问题总结:")
    print(f"1. 切片大小过小 (512字符) 导致信息分割")
    print(f"2. 文档预处理不当，保留了标题和空片段")
    print(f"3. 检索参数需要优化")
    print(f"\n🎯 立即行动:")
    print(f"1. 修改主程序使用 config_improved.py")
    print(f"2. 重建向量数据库")
    print(f"3. 重新测试检索质量")

if __name__ == "__main__":
    main() 