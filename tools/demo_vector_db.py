#!/usr/bin/env python
"""
向量数据库功能演示脚本
展示FAISS向量数据库的持久化存储和检索功能
"""

import os
import json
import numpy as np
from pathlib import Path
import time

def demo_vector_database():
    """演示向量数据库功能"""
    print("="*60)
    print("向量数据库持久化功能演示")
    print("="*60)
    
    try:
        import faiss
        print("✅ FAISS库导入成功")
    except ImportError:
        print("❌ FAISS库未安装，请运行: pip install faiss-cpu")
        return
    
    from config import Config
    print(f"✅ 配置加载成功，向量数据库目录: {Config.VECTOR_DB_DIR}")
    
    # 创建向量数据库目录
    vector_db_path = Path(Config.VECTOR_DB_DIR)
    vector_db_path.mkdir(exist_ok=True)
    print(f"✅ 向量数据库目录已创建: {vector_db_path}")
    
    # 演示基本的FAISS功能
    print("\n" + "-"*40)
    print("演示基本FAISS向量索引功能")
    print("-"*40)
    
    # 创建示例向量数据
    dimension = 128  # 简化的向量维度
    num_vectors = 1000
    
    print(f"创建 {num_vectors} 个 {dimension} 维向量...")
    vectors = np.random.random((num_vectors, dimension)).astype(np.float32)
    
    # 标准化向量
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms
    print("✅ 向量标准化完成")
    
    # 创建FAISS索引
    print("创建FAISS索引...")
    index = faiss.IndexFlatIP(dimension)  # 内积索引
    index.add(vectors)
    print(f"✅ FAISS索引创建完成，包含 {index.ntotal} 个向量")
    
    # 测试搜索
    print("\n测试向量搜索...")
    query_vector = np.random.random((1, dimension)).astype(np.float32)
    query_vector = query_vector / np.linalg.norm(query_vector)
    
    start_time = time.time()
    scores, indices = index.search(query_vector, 5)  # 返回前5个最相似的向量
    search_time = time.time() - start_time
    
    print(f"✅ 搜索完成，耗时: {search_time:.4f}秒")
    print("搜索结果:")
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        print(f"  {i+1}. 索引: {idx}, 相似度分数: {score:.4f}")
    
    # 演示持久化存储
    print("\n" + "-"*40)
    print("演示向量数据库持久化存储")
    print("-"*40)
    
    # 保存索引到磁盘
    index_file = vector_db_path / "demo_faiss_index.bin"
    metadata_file = vector_db_path / "demo_metadata.json"
    
    print(f"保存FAISS索引到: {index_file}")
    faiss.write_index(index, str(index_file))
    
    # 保存元数据
    metadata = {
        "total_vectors": int(index.ntotal),
        "vector_dimension": dimension,
        "index_type": "IndexFlatIP",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "演示用向量数据库"
    }
    
    print(f"保存元数据到: {metadata_file}")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print("✅ 向量数据库持久化存储完成")
    
    # 演示加载持久化数据
    print("\n" + "-"*40)
    print("演示从磁盘加载向量数据库")
    print("-"*40)
    
    # 清空内存中的索引
    del index
    print("✅ 内存中的索引已清空")
    
    # 从磁盘重新加载
    print(f"从磁盘加载索引: {index_file}")
    loaded_index = faiss.read_index(str(index_file))
    
    # 加载元数据
    print(f"加载元数据: {metadata_file}")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        loaded_metadata = json.load(f)
    
    print("✅ 向量数据库加载完成")
    print("加载的元数据:")
    for key, value in loaded_metadata.items():
        print(f"  {key}: {value}")
    
    # 验证加载的索引功能正常
    print("\n验证加载的索引...")
    start_time = time.time()
    scores2, indices2 = loaded_index.search(query_vector, 5)
    search_time2 = time.time() - start_time
    
    print(f"✅ 搜索完成，耗时: {search_time2:.4f}秒")
    
    # 验证结果一致性
    if np.array_equal(scores, scores2) and np.array_equal(indices, indices2):
        print("✅ 加载的索引与原始索引结果完全一致")
    else:
        print("❌ 结果不一致")
    
    print("\n" + "="*60)
    print("向量数据库持久化演示完成")
    print("="*60)
    
    # 显示文件信息
    print("\n生成的文件:")
    for file_path in [index_file, metadata_file]:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  {file_path}: {size:,} 字节")
    
    print(f"\n💡 优势说明:")
    print(f"   - 首次构建：计算 {num_vectors} 个向量并保存")
    print(f"   - 后续加载：直接从磁盘读取，秒级启动")
    print(f"   - 搜索性能：{num_vectors} 个向量搜索耗时 {search_time:.4f}秒")
    print(f"   - 存储空间：索引文件约 {index_file.stat().st_size/1024:.1f} KB")
    
    return True

def demo_vector_database_integration():
    """演示向量数据库与文档检索的集成"""
    print("\n" + "="*60)
    print("文档检索集成演示")
    print("="*60)
    
    # 模拟文档数据
    documents = [
        "银行应当建立完善的风险管理体系，包括风险识别、风险评估、风险控制等环节。",
        "商业银行的资本充足率不得低于8%，一级资本充足率不得低于6%。",
        "银行业金融机构应当建立内部控制制度，确保业务操作的合规性。",
        "金融机构应当建立健全反洗钱制度，履行反洗钱义务。",
        "银行应当对信贷资产进行分类管理，及时识别和处置不良资产。"
    ]
    
    print(f"模拟文档数据：{len(documents)} 个文档片段")
    
    # 这里会在实际系统中使用嵌入模型生成向量
    # 为演示目的，我们使用随机向量
    dimension = 768  # m3e-base模型的向量维度
    
    print("生成文档向量（实际系统中会使用m3e-base模型）...")
    doc_vectors = np.random.random((len(documents), dimension)).astype(np.float32)
    # 标准化
    norms = np.linalg.norm(doc_vectors, axis=1, keepdims=True)
    doc_vectors = doc_vectors / norms
    
    # 创建文档索引
    import faiss
    doc_index = faiss.IndexFlatIP(dimension)
    doc_index.add(doc_vectors)
    
    print(f"✅ 文档向量索引创建完成，包含 {len(documents)} 个文档")
    
    # 模拟查询
    queries = [
        "银行风险管理制度",
        "资本充足率要求",
        "反洗钱规定"
    ]
    
    print("\n文档检索演示:")
    for query in queries:
        print(f"\n查询: {query}")
        
        # 生成查询向量（实际系统中会使用嵌入模型）
        query_vector = np.random.random((1, dimension)).astype(np.float32)
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # 搜索相关文档
        scores, indices = doc_index.search(query_vector, 3)
        
        print("检索结果:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(documents):
                print(f"  {i+1}. [分数: {score:.4f}] {documents[idx]}")
    
    print("\n✅ 文档检索演示完成")

if __name__ == "__main__":
    try:
        success = demo_vector_database()
        if success:
            demo_vector_database_integration()
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc() 