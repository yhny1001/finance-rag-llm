#!/usr/bin/env python
"""
修复rag_engine.py文件中的缩进错误
"""

import re

def fix_indentation_errors():
    """修复rag_engine.py文件中的缩进错误"""
    print("开始修复rag_engine.py文件中的缩进错误...")
    
    # 读取文件内容
    with open("rag_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 修复retrieve_documents方法的缩进问题
    pattern1 = r'def retrieve_documents\(self, query: str, top_k: int = 3\) -> str:'
    if re.search(pattern1, content):
        # 检查是否有缩进问题
        if '        def retrieve_documents' in content:
            print("发现retrieve_documents缩进错误，进行修复...")
            content = content.replace('        def retrieve_documents', '    def retrieve_documents')
    
    # 修复search_documents方法内部的缩进问题
    pattern2 = r'try:\s+results = self\.vector_db\.search\(query, top_k=top_k\)\s+return results'
    if re.search(pattern2, content):
        print("发现search_documents内部缩进错误，进行修复...")
        content = content.replace('                results = self.vector_db.search(query, top_k=top_k)\n            return results', 
                                  '            results = self.vector_db.search(query, top_k=top_k)\n            return results')
    
    # 修复retrieve_documents方法内部的缩进问题
    pattern3 = r'try:\s+# 使用基础向量检索\s+results = self\.vector_db\.search\(query, top_k=top_k\)\s+'
    if re.search(pattern3, content):
        print("发现retrieve_documents内部缩进错误，进行修复...")
        content = content.replace('                # 使用基础向量检索\n                results = self.vector_db.search(query, top_k=top_k)', 
                                 '            # 使用基础向量检索\n            results = self.vector_db.search(query, top_k=top_k)')
    
    # 修复retrieve_documents方法内部if条件缩进问题
    if 'if not results:\n                return ""' in content:
        print("修复if条件缩进...")
        content = content.replace('if not results:\n                return ""',
                                 'if not results:\n            return ""')
    
    # 修复context变量缩进问题
    if 'context = "\n\n".join([doc["text"] for doc in results])\n            return context' in content:
        print("修复context变量缩进...")
        content = content.replace('context = "\n\n".join([doc["text"] for doc in results])\n            return context',
                                 'context = "\n\n".join([doc["text"] for doc in results])\n            return context')
    
    # 写回文件
    with open("rag_engine.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("rag_engine.py文件修复完成！")

if __name__ == "__main__":
    fix_indentation_errors() 