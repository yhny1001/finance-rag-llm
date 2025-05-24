"""
向量数据库管理模块
基于FAISS实现高效的向量存储、检索和持久化
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from tqdm import tqdm

import faiss
import torch
from sentence_transformers import SentenceTransformer

from config import Config


class VectorDatabase:
    """向量数据库管理类"""
    
    def __init__(self, embedding_model=None):
        self.config = Config
        self.embedding_model = embedding_model
        self.index = None
        self.document_store = {}  # 存储文档内容和元数据
        self.vector_metadata = {}  # 存储向量元数据
        self.is_loaded = False
        
        # 向量数据库文件路径
        self.vector_db_path = Path(self.config.VECTOR_DB_DIR)
        self.faiss_index_path = self.vector_db_path / self.config.FAISS_INDEX_FILE
        self.metadata_path = self.vector_db_path / self.config.VECTOR_METADATA_FILE
        self.document_store_path = self.vector_db_path / self.config.DOCUMENT_STORE_FILE
        
        # 确保目录存在
        self.vector_db_path.mkdir(exist_ok=True)
        
        print("向量数据库初始化完成")
    
    def _get_document_hash(self, content: str) -> str:
        """计算文档内容的哈希值，用于检测文档变更"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _create_faiss_index(self) -> faiss.Index:
        """创建FAISS索引"""
        dimension = self.config.VECTOR_DIMENSION
        
        if self.config.FAISS_INDEX_TYPE == "IndexFlatIP":
            # 内积索引（适合已标准化的向量）
            index = faiss.IndexFlatIP(dimension)
        elif self.config.FAISS_INDEX_TYPE == "IndexFlatL2":
            # L2距离索引
            index = faiss.IndexFlatL2(dimension)
        elif self.config.FAISS_INDEX_TYPE == "IndexIVFFlat":
            # IVF索引（适合大规模数据）
            quantizer = faiss.IndexFlatIP(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, 100)  # 100个聚类
        else:
            # 默认使用内积索引
            index = faiss.IndexFlatIP(dimension)
            
        print(f"创建FAISS索引: {self.config.FAISS_INDEX_TYPE}, 维度: {dimension}")
        return index
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """标准化向量"""
        if self.config.VECTOR_NORMALIZE:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            # 避免除零
            norms = np.where(norms == 0, 1, norms)
            return vectors / norms
        return vectors
    
    def encode_texts(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """将文本编码为向量"""
        if self.embedding_model is None:
            raise ValueError("嵌入模型未初始化")
        
        print(f"开始编码 {len(texts)} 个文本片段...")
        
        # 分批编码以节省内存
        batch_size = self.config.BATCH_ENCODE_SIZE
        all_vectors = []
        
        for i in tqdm(range(0, len(texts), batch_size), 
                     desc="编码文本", disable=not show_progress):
            batch_texts = texts[i:i + batch_size]
            
            # 使用嵌入模型编码
            if hasattr(self.embedding_model, 'encode'):
                # sentence-transformers风格
                batch_vectors = self.embedding_model.encode(
                    batch_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
            else:
                # HuggingFace风格
                batch_vectors = []
                for text in batch_texts:
                    vector = self.embedding_model.get_text_embedding(text)
                    batch_vectors.append(vector)
                batch_vectors = np.array(batch_vectors)
            
            all_vectors.append(batch_vectors)
            
            # 定期清理GPU缓存
            if torch.cuda.is_available() and (i + batch_size) % 128 == 0:
                torch.cuda.empty_cache()
        
        vectors = np.vstack(all_vectors)
        print(f"编码完成，向量形状: {vectors.shape}")
        
        return self._normalize_vectors(vectors)
    
    def build_from_documents(self, documents: List[Dict[str, Any]], 
                           force_rebuild: bool = False) -> bool:
        """从文档列表构建向量数据库"""
        print("开始构建向量数据库...")
        
        # 检查是否可以增量更新
        if not force_rebuild and self.can_load_existing():
            if self._should_incremental_update(documents):
                return self._incremental_update(documents)
        
        # 全量重建
        print("执行全量重建...")
        
        # 准备文档切片
        text_chunks = []
        chunk_metadata = []
        
        for doc_idx, doc in enumerate(tqdm(documents, desc="处理文档")):
            content = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            # 文档切片
            chunks = self._split_document(content)
            
            for chunk_idx, chunk in enumerate(chunks):
                if chunk.strip():  # 跳过空片段
                    chunk_id = f"doc_{doc_idx}_chunk_{chunk_idx}"
                    
                    text_chunks.append(chunk)
                    chunk_metadata.append({
                        'chunk_id': chunk_id,
                        'doc_index': doc_idx,
                        'chunk_index': chunk_idx,
                        'text': chunk,
                        'doc_metadata': metadata,
                        'content_hash': self._get_document_hash(chunk)
                    })
        
        print(f"总共生成 {len(text_chunks)} 个文档片段")
        
        # 编码向量
        vectors = self.encode_texts(text_chunks)
        
        # 创建FAISS索引
        self.index = self._create_faiss_index()
        
        # 添加向量到索引
        print("添加向量到FAISS索引...")
        self.index.add(vectors.astype(np.float32))
        
        # 更新存储
        self.document_store = {
            meta['chunk_id']: meta for meta in chunk_metadata
        }
        
        self.vector_metadata = {
            'total_vectors': len(vectors),
            'vector_dimension': vectors.shape[1],
            'index_type': self.config.FAISS_INDEX_TYPE,
            'created_at': str(pd.Timestamp.now()),
            'document_count': len(documents)
        }
        
        # 持久化保存
        self.save_to_disk()
        
        self.is_loaded = True
        print("向量数据库构建完成!")
        return True
    
    def _split_document(self, content: str) -> List[str]:
        """文档切片"""
        chunk_size = self.config.CHUNK_SIZE
        chunk_overlap = self.config.CHUNK_OVERLAP
        
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # 尝试在句号、换行符等位置切分
            if end < len(content):
                for sep in ['\n\n', '\n', '。', '！', '？', ';', '.']:
                    sep_pos = content.rfind(sep, start, end)
                    if sep_pos > start:
                        end = sep_pos + len(sep)
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - chunk_overlap)
        
        return chunks
    
    def can_load_existing(self) -> bool:
        """检查是否可以加载已有的向量数据库"""
        return (self.faiss_index_path.exists() and 
                self.metadata_path.exists() and 
                self.document_store_path.exists())
    
    def load_from_disk(self) -> bool:
        """从磁盘加载向量数据库"""
        if not self.can_load_existing():
            print("未找到已有的向量数据库文件")
            return False
        
        try:
            print("从磁盘加载向量数据库...")
            
            # 加载FAISS索引
            self.index = faiss.read_index(str(self.faiss_index_path))
            
            # 加载元数据
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.vector_metadata = json.load(f)
            
            # 加载文档存储
            with open(self.document_store_path, 'r', encoding='utf-8') as f:
                self.document_store = json.load(f)
            
            self.is_loaded = True
            print(f"向量数据库加载完成，包含 {self.vector_metadata.get('total_vectors', 0)} 个向量")
            return True
            
        except Exception as e:
            print(f"加载向量数据库失败: {e}")
            return False
    
    def save_to_disk(self) -> bool:
        """保存向量数据库到磁盘"""
        try:
            print("保存向量数据库到磁盘...")
            
            # 保存FAISS索引
            faiss.write_index(self.index, str(self.faiss_index_path))
            
            # 保存元数据
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.vector_metadata, f, ensure_ascii=False, indent=2)
            
            # 保存文档存储
            with open(self.document_store_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_store, f, ensure_ascii=False, indent=2)
            
            print("向量数据库保存完成")
            return True
            
        except Exception as e:
            print(f"保存向量数据库失败: {e}")
            return False
    
    def search(self, query_text: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self.is_loaded or self.index is None:
            raise ValueError("向量数据库未加载")
        
        if top_k is None:
            top_k = self.config.TOP_K
        
        # 编码查询文本
        query_vector = self.encode_texts([query_text], show_progress=False)
        
        # 执行搜索
        scores, indices = self.index.search(query_vector.astype(np.float32), top_k)
        
        # 整理结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # 有效索引
                chunk_id = list(self.document_store.keys())[idx]
                chunk_data = self.document_store[chunk_id]
                
                results.append({
                    'chunk_id': chunk_id,
                    'text': chunk_data['text'],
                    'score': float(score),
                    'metadata': chunk_data.get('doc_metadata', {}),
                    'chunk_index': chunk_data.get('chunk_index', 0)
                })
        
        return results
    
    def _should_incremental_update(self, documents: List[Dict[str, Any]]) -> bool:
        """判断是否应该进行增量更新"""
        # 简单实现：检查文档数量变化
        current_doc_count = self.vector_metadata.get('document_count', 0)
        return len(documents) <= current_doc_count * 1.1  # 允许10%的增长
    
    def _incremental_update(self, documents: List[Dict[str, Any]]) -> bool:
        """增量更新（简化实现）"""
        print("执行增量更新...")
        # 在实际应用中，这里会实现更复杂的增量更新逻辑
        # 目前简化为全量重建
        return self.build_from_documents(documents, force_rebuild=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取向量数据库统计信息"""
        if not self.is_loaded:
            return {"status": "未加载"}
        
        return {
            "status": "已加载",
            "total_vectors": self.vector_metadata.get('total_vectors', 0),
            "vector_dimension": self.vector_metadata.get('vector_dimension', 0),
            "document_count": self.vector_metadata.get('document_count', 0),
            "index_type": self.vector_metadata.get('index_type', 'unknown'),
            "created_at": self.vector_metadata.get('created_at', 'unknown'),
            "storage_path": str(self.vector_db_path)
        }
    
    def clear_database(self):
        """清空向量数据库"""
        print("清空向量数据库...")
        
        # 删除文件
        for file_path in [self.faiss_index_path, self.metadata_path, self.document_store_path]:
            if file_path.exists():
                file_path.unlink()
        
        # 重置内存状态
        self.index = None
        self.document_store = {}
        self.vector_metadata = {}
        self.is_loaded = False
        
        print("向量数据库已清空")


# 为了兼容性，添加pandas导入
try:
    import pandas as pd
except ImportError:
    print("警告: pandas未安装，将使用简化的时间戳")
    class pd:
        @staticmethod
        class Timestamp:
            @staticmethod
            def now():
                import datetime
                return datetime.datetime.now().isoformat() 