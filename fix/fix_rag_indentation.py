"""
修复rag_engine.py文件中的缩进问题
"""

def fix_indentation():
    """修复rag_engine.py中的缩进问题"""
    print("开始修复rag_engine.py中的缩进问题...")
    
    # 读取文件内容
    with open('rag_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复缩进问题
    content = content.replace('        def retrieve_documents', '    def retrieve_documents')
    
    # 写回文件
    with open('rag_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("缩进问题修复成功!")

if __name__ == "__main__":
    fix_indentation() 