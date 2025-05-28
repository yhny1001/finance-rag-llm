#!/usr/bin/env python
"""
向量数据库管理工具
提供向量数据库的创建、查询、维护等功能
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from config import Config
from vector_db import VectorDatabase
from rag_engine import DocumentProcessor, SimpleEmbedding


class VectorDBManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.config = Config
        self.vector_db = None
        self.doc_processor = DocumentProcessor()
        
    def init_embedding_model(self):
        """初始化嵌入模型"""
        print("初始化嵌入模型...")
        try:
            # 使用简化的嵌入模型
            embed_model = SimpleEmbedding(self.config.EMBEDDING_MODEL_PATH)
            
            self.vector_db = VectorDatabase(embedding_model=embed_model)
            print("嵌入模型初始化完成")
            return True
            
        except Exception as e:
            print(f"初始化嵌入模型失败: {e}")
            return False
    
    def show_status(self):
        """显示向量数据库状态"""
        print("\n" + "="*60)
        print("向量数据库状态")
        print("="*60)
        
        if not self.vector_db:
            print("向量数据库未初始化")
            return
            
        # 检查文件存在性
        vector_db_path = Path(self.config.VECTOR_DB_DIR)
        faiss_index_path = vector_db_path / self.config.FAISS_INDEX_FILE
        metadata_path = vector_db_path / self.config.VECTOR_METADATA_FILE
        document_store_path = vector_db_path / self.config.DOCUMENT_STORE_FILE
        
        print(f"向量数据库目录: {vector_db_path}")
        print(f"FAISS索引文件: {faiss_index_path} ({'存在' if faiss_index_path.exists() else '不存在'})")
        print(f"元数据文件: {metadata_path} ({'存在' if metadata_path.exists() else '不存在'})")
        print(f"文档存储文件: {document_store_path} ({'存在' if document_store_path.exists() else '不存在'})")
        
        # 尝试加载并显示统计信息
        if self.vector_db.can_load_existing():
            if self.vector_db.load_from_disk():
                stats = self.vector_db.get_statistics()
                print(f"\n向量数据库统计信息:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            else:
                print("\n无法加载向量数据库")
        else:
            print("\n向量数据库文件不完整")
    
    def build_database(self, force_rebuild: bool = False):
        """构建向量数据库"""
        print("构建向量数据库...")
        
        if not self.init_embedding_model():
            return False
        
        # 检查是否需要重建
        if not force_rebuild and self.vector_db.can_load_existing():
            print("发现已存在的向量数据库")
            choice = input("是否重建? (y/N): ").strip().lower()
            if choice != 'y':
                print("取消重建")
                return True
        
        # 加载文档
        print(f"从目录加载文档: {self.config.DOCUMENTS_DIR}")
        documents = self.doc_processor.load_documents(self.config.DOCUMENTS_DIR)
        
        if not documents:
            print("未找到可用的文档文件")
            return False
        
        # 转换格式
        vector_db_docs = []
        for doc in documents:
            vector_db_docs.append({
                'text': doc.text,
                'metadata': doc.metadata
            })
        
        # 构建向量数据库
        success = self.vector_db.build_from_documents(vector_db_docs, force_rebuild=True)
        
        if success:
            print("向量数据库构建成功!")
            self.show_status()
        else:
            print("向量数据库构建失败")
            
        return success
    
    def search_documents(self, query: str, top_k: int = None):
        """搜索文档"""
        if not self.vector_db:
            if not self.init_embedding_model():
                return
        
        if not self.vector_db.is_loaded:
            if not self.vector_db.load_from_disk():
                print("无法加载向量数据库，请先构建数据库")
                return
        
        if top_k is None:
            top_k = self.config.TOP_K
            
        print(f"\n搜索查询: {query}")
        print(f"返回数量: {top_k}")
        print("-" * 50)
        
        try:
            results = self.vector_db.search(query, top_k=top_k)
            
            for i, result in enumerate(results, 1):
                print(f"\n结果 {i}:")
                print(f"相似度分数: {result['score']:.4f}")
                print(f"文档片段ID: {result['chunk_id']}")
                print(f"内容: {result['text'][:200]}...")
                if result.get('metadata'):
                    print(f"文档来源: {result['metadata']}")
                    
        except Exception as e:
            print(f"搜索失败: {e}")
    
    def clear_database(self):
        """清空向量数据库"""
        print("清空向量数据库...")
        
        if not self.vector_db:
            self.vector_db = VectorDatabase()
        
        choice = input("确认清空向量数据库? 这将删除所有向量数据 (y/N): ").strip().lower()
        if choice == 'y':
            self.vector_db.clear_database()
            print("向量数据库已清空")
        else:
            print("取消清空操作")
    
    def test_search(self):
        """测试搜索功能"""
        if not self.vector_db:
            if not self.init_embedding_model():
                return
        
        if not self.vector_db.is_loaded:
            if not self.vector_db.load_from_disk():
                print("无法加载向量数据库，请先构建数据库")
                return
        
        print("\n进入测试搜索模式")
        print("输入 'quit' 退出")
        
        while True:
            query = input("\n请输入搜索查询: ").strip()
            if query.lower() == 'quit':
                break
                
            if not query:
                continue
                
            try:
                top_k = int(input("返回结果数量 (默认5): ") or "5")
            except ValueError:
                top_k = 5
                
            self.search_documents(query, top_k)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="向量数据库管理工具")
    parser.add_argument("--status", action="store_true", help="显示向量数据库状态")
    parser.add_argument("--build", action="store_true", help="构建向量数据库")
    parser.add_argument("--force-rebuild", action="store_true", help="强制重建向量数据库")
    parser.add_argument("--clear", action="store_true", help="清空向量数据库")
    parser.add_argument("--search", type=str, help="搜索文档")
    parser.add_argument("--top-k", type=int, default=5, help="搜索返回数量")
    parser.add_argument("--test-search", action="store_true", help="测试搜索功能")
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = VectorDBManager()
    
    if args.status:
        manager.show_status()
        
    elif args.build or args.force_rebuild:
        manager.build_database(force_rebuild=args.force_rebuild)
        
    elif args.clear:
        manager.clear_database()
        
    elif args.search:
        manager.search_documents(args.search, args.top_k)
        
    elif args.test_search:
        manager.test_search()
        
    else:
        # 默认显示状态
        print("向量数据库管理工具")
        print("使用 --help 查看所有选项")
        manager.show_status()


if __name__ == "__main__":
    main() 