#!/usr/bin/env python
"""
全面修复rag_engine.py文件中的缩进错误和语法问题
"""

import re
import sys
import os
from pathlib import Path

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

def fix_retrieve_documents(content):
    """修复retrieve_documents方法的缩进问题"""
    # 匹配整个方法定义和实现
    retrieve_pattern = r'''        def retrieve_documents\(self, query: str, top_k: int = 3\) -> str:
        """检索相关文档.*?Returns:.*?str: 合并的相关文档文本.*?"""
        try:
                # 使用基础向量检索
                results = self\.vector_db\.search\(query, top_k=top_k\)
            
            if not results:
                return ""
            
            # 合并文档文本
            context = "\\n\\n"\.join\(\[doc\["text"\] for doc in results\]\)
            return context
            
        except Exception as e:
            self\.logger\.error\(f"检索文档失败: \{e\}"\)
            return ""'''
    
    correct_method = '''    def retrieve_documents(self, query: str, top_k: int = 3) -> str:
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
    
    # 使用re.DOTALL让.匹配换行符
    pattern = re.compile(retrieve_pattern, re.DOTALL)
    if pattern.search(content):
        print("修复retrieve_documents方法...")
        return pattern.sub(correct_method, content)
    
    # 如果正则匹配失败，尝试更简单的替换
    if '        def retrieve_documents' in content:
        print("使用简单替换修复retrieve_documents方法...")
        content = content.replace('        def retrieve_documents', '    def retrieve_documents')
        content = content.replace('                # 使用基础向量检索', '            # 使用基础向量检索')
        content = content.replace('                results = self.vector_db.search(query, top_k=top_k)', '            results = self.vector_db.search(query, top_k=top_k)')
        content = content.replace('            if not results:', '            if not results:')
        content = content.replace('                return ""', '            return ""')
        content = content.replace('            # 合并文档文本', '            # 合并文档文本')
        content = content.replace('            context = "\\n\\n".join([doc["text"] for doc in results])', '            context = "\\n\\n".join([doc["text"] for doc in results])')
        content = content.replace('            return context', '            return context')
    
    return content

def fix_search_documents(content):
    """修复search_documents方法的缩进问题"""
    search_pattern = r'''    def search_documents\(self, query: str, top_k: int = 3\) -> List\[Dict\[str, Any\]\]:
        """搜索文档.*?Returns:.*?List\[Dict\[str, Any\]\]: 搜索结果列表.*?"""
        try:
                results = self\.vector_db\.search\(query, top_k=top_k\)
            return results
            
        except Exception as e:
            self\.logger\.error\(f"搜索文档失败: \{e\}"\)
            return \[\]'''
    
    correct_method = '''    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
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
    
    pattern = re.compile(search_pattern, re.DOTALL)
    if pattern.search(content):
        print("修复search_documents方法...")
        return pattern.sub(correct_method, content)
    
    # 如果正则匹配失败，尝试更简单的替换
    if '                results = self.vector_db.search(query, top_k=top_k)' in content:
        print("使用简单替换修复search_documents方法...")
        content = content.replace('                results = self.vector_db.search(query, top_k=top_k)', '            results = self.vector_db.search(query, top_k=top_k)')
        content = content.replace('            return results', '            return results')
    
    return content

def fix_indentation_errors(file_path):
    """修复rag_engine.py文件中的缩进错误"""
    print(f"开始全面修复 {file_path} 文件中的缩进错误...")
    
    # 创建备份
    backup_path = make_backup(file_path)
    
    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复retrieve_documents方法
        content = fix_retrieve_documents(content)
        
        # 修复search_documents方法
        content = fix_search_documents(content)
        
        # 检查是否有其他缩进问题
        if '    def _split_document(' in content and '    def retrieve_documents(' not in content:
            print("检测到_split_document方法后面的方法可能缩进不正确，进行修复...")
            content = content.replace('    def _split_document(', '    def _split_document(')
        
        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"{file_path} 文件修复完成！")
        print(f"如果修复后仍有问题，可以从备份恢复: {backup_path}")
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        print(f"建议从备份恢复: {backup_path}")
        return False
    
    return True

if __name__ == "__main__":
    file_path = "rag_engine.py"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    if fix_indentation_errors(file_path):
        print("修复成功完成")
    else:
        print("修复过程中出现错误，请查看上面的错误信息")
        sys.exit(1) 