#!/usr/bin/env python
"""
直接用字符串替换方式修复rag_engine.py文件
"""

import os
from pathlib import Path

def make_backup(file_path):
    """创建备份文件"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    original_path = Path(file_path)
    backup_path = backup_dir / f"{original_path.stem}_direct_fix{original_path.suffix}"
    
    with open(file_path, "r", encoding="utf-8") as src:
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    
    print(f"备份文件已创建: {backup_path}")
    return backup_path

def direct_fix():
    """直接修复rag_engine.py文件"""
    file_path = "rag_engine.py"
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return False
    
    # 创建备份
    backup_path = make_backup(file_path)
    
    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 找到有问题的行并修复
        fixed_lines = []
        skip_mode = False
        
        for line in lines:
            # 开始跳过有问题的retrieve_documents方法
            if line.strip() == 'def retrieve_documents(self, query: str, top_k: int = 3) -> str:':
                skip_mode = True
                fixed_lines.append('    def retrieve_documents(self, query: str, top_k: int = 3) -> str:\n')
                fixed_lines.append('        """检索相关文档\n')
                fixed_lines.append('        \n')
                fixed_lines.append('        Args:\n')
                fixed_lines.append('            query: 查询文本\n')
                fixed_lines.append('            top_k: 返回的文档数量\n')
                fixed_lines.append('            \n')
                fixed_lines.append('        Returns:\n')
                fixed_lines.append('            str: 合并的相关文档文本\n')
                fixed_lines.append('        """\n')
                fixed_lines.append('        try:\n')
                fixed_lines.append('            # 使用基础向量检索\n')
                fixed_lines.append('            results = self.vector_db.search(query, top_k=top_k)\n')
                fixed_lines.append('            \n')
                fixed_lines.append('            if not results:\n')
                fixed_lines.append('                return ""\n')
                fixed_lines.append('            \n')
                fixed_lines.append('            # 合并文档文本\n')
                fixed_lines.append('            context = "\\n\\n".join([doc["text"] for doc in results])\n')
                fixed_lines.append('            return context\n')
                fixed_lines.append('            \n')
                fixed_lines.append('        except Exception as e:\n')
                fixed_lines.append('            self.logger.error(f"检索文档失败: {e}")\n')
                fixed_lines.append('            return ""\n')
            # 开始跳过有问题的search_documents方法
            elif line.strip() == 'def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:':
                skip_mode = True
                fixed_lines.append('    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:\n')
                fixed_lines.append('        """搜索文档\n')
                fixed_lines.append('        \n')
                fixed_lines.append('        Args:\n')
                fixed_lines.append('            query: 查询文本\n')
                fixed_lines.append('            top_k: 返回的文档数量\n')
                fixed_lines.append('            \n')
                fixed_lines.append('        Returns:\n')
                fixed_lines.append('            List[Dict[str, Any]]: 搜索结果列表\n')
                fixed_lines.append('        """\n')
                fixed_lines.append('        try:\n')
                fixed_lines.append('            results = self.vector_db.search(query, top_k=top_k)\n')
                fixed_lines.append('            return results\n')
                fixed_lines.append('            \n')
                fixed_lines.append('        except Exception as e:\n')
                fixed_lines.append('            self.logger.error(f"搜索文档失败: {e}")\n')
                fixed_lines.append('            return []\n')
            # 结束跳过模式
            elif skip_mode and line.strip() == 'def generate_answer(self, question: str, context: str, question_type: str) -> str:':
                skip_mode = False
                fixed_lines.append(line)
            elif skip_mode and line.strip() == 'def cleanup(self):':
                skip_mode = False
                fixed_lines.append(line)
            # 不在跳过模式下，正常添加行
            elif not skip_mode:
                fixed_lines.append(line)
        
        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        
        print(f"{file_path} 文件修复完成！")
        print(f"如果修复后仍有问题，可以从备份恢复: {backup_path}")
        return True
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        print(f"建议从备份恢复: {backup_path}")
        return False

if __name__ == "__main__":
    if direct_fix():
        print("修复成功完成")
    else:
        print("修复过程中出现错误") 