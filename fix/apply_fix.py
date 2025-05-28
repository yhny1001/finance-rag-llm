#!/usr/bin/env python
"""
直接修复rag_engine.py文件中的问题
"""

import re
import os
from pathlib import Path

# 正确的retrieve_documents函数实现
FIXED_RETRIEVE_DOCUMENTS = '''    def retrieve_documents(self, query: str, top_k: int = 3) -> str:
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
            context = "\\n\\n".join([doc["text"] for doc in results])
            return context
            
        except Exception as e:
            self.logger.error(f"检索文档失败: {e}")
            return ""'''

# 正确的search_documents函数实现
FIXED_SEARCH_DOCUMENTS = '''    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
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
            return []'''

def make_backup(file_path):
    """创建备份文件"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    original_path = Path(file_path)
    backup_path = backup_dir / f"{original_path.stem}_backup{original_path.suffix}"
    
    with open(file_path, "r", encoding="utf-8") as src:
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    
    print(f"备份文件已创建: {backup_path}")
    return backup_path

def apply_fix():
    """应用修复"""
    file_path = "rag_engine.py"
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return False
    
    # 创建备份
    backup_path = make_backup(file_path)
    
    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 使用正则表达式找到有问题的方法并替换
        retrieve_pattern = r'(\s+)def retrieve_documents\(self, query: str, top_k: int = 3\) -> str:.*?return ""'
        content = re.sub(retrieve_pattern, FIXED_RETRIEVE_DOCUMENTS, content, flags=re.DOTALL)
        
        search_pattern = r'(\s+)def search_documents\(self, query: str, top_k: int = 3\) -> List\[Dict\[str, Any\]\]:.*?return \[\]'
        content = re.sub(search_pattern, FIXED_SEARCH_DOCUMENTS, content, flags=re.DOTALL)
        
        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"{file_path} 文件修复完成！")
        print(f"如果修复后仍有问题，可以从备份恢复: {backup_path}")
        return True
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        print(f"建议从备份恢复: {backup_path}")
        return False

if __name__ == "__main__":
    if apply_fix():
        print("修复成功完成")
    else:
        print("修复过程中出现错误") 