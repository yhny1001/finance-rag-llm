def retrieve_documents(self, query: str, top_k: int = 3) -> str:
    """检索相关文档
    
    Args:
        query: 查询文本
        top_k: 返回的文档数量
        
    Returns:
        str: 合并的相关文档文本
    """
    try:
        # 使用基础向量检索
        results = self.vector_db.search(query, top_k=top_k)
        
        if not results:
            return ""
        
        # 合并文档文本
        context = "\n\n".join([doc["text"] for doc in results])
        return context
        
    except Exception as e:
        self.logger.error(f"检索文档失败: {e}")
        return ""

def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """搜索文档
    
    Args:
        query: 查询文本
        top_k: 返回的文档数量
        
    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    try:
        results = self.vector_db.search(query, top_k=top_k)
        return results
        
    except Exception as e:
        self.logger.error(f"搜索文档失败: {e}")
        return [] 