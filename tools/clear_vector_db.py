"""
清除向量数据库切片
删除已构建的向量索引，强制重新构建
"""

import os
import shutil
from pathlib import Path

def clear_vector_database():
    """清除向量数据库文件"""
    print("=" * 60)
    print("清除向量数据库切片")
    print("=" * 60)
    
    # 向量数据库相关文件和目录
    vector_files = [
        "vector_db/",           # 向量数据库目录
        "faiss_index.bin",      # FAISS索引文件
        "vector_metadata.json", # 向量元数据
        "document_store.json",  # 文档存储
    ]
    
    removed_count = 0
    
    for item in vector_files:
        path = Path(item)
        
        try:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"✅ 已删除目录: {item}")
                else:
                    path.unlink()
                    print(f"✅ 已删除文件: {item}")
                removed_count += 1
            else:
                print(f"⚠️ 不存在: {item}")
        except Exception as e:
            print(f"❌ 删除失败 {item}: {e}")
    
    print(f"\n总共删除了 {removed_count} 个项目")
    
    if removed_count > 0:
        print("✅ 向量数据库清除完成！下次运行程序时将重新构建索引。")
    else:
        print("⚠️ 没有找到需要清除的向量数据库文件")
    
    print("=" * 60)

def clear_all_cache():
    """清除所有缓存文件"""
    print("\n" + "=" * 60)
    print("清除所有缓存文件")
    print("=" * 60)
    
    cache_patterns = [
        "__pycache__/",
        "*.pyc",
        "*.pyo", 
        "*.log",
        ".cache/",
        "tmp/",
        "temp/"
    ]
    
    removed_count = 0
    
    # 清除Python缓存
    for root, dirs, files in os.walk("."):
        # 删除__pycache__目录
        if "__pycache__" in dirs:
            cache_dir = Path(root) / "__pycache__"
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ 已删除: {cache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {cache_dir}: {e}")
        
        # 删除.pyc文件
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = Path(root) / file
                try:
                    file_path.unlink()
                    print(f"✅ 已删除: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_path}: {e}")
    
    print(f"\n总共清除了 {removed_count} 个缓存文件")
    print("=" * 60)

def show_current_status():
    """显示当前状态"""
    print("\n" + "=" * 60)
    print("当前状态检查")
    print("=" * 60)
    
    # 检查向量数据库状态
    vector_db_dir = Path("vector_db")
    if vector_db_dir.exists():
        files_in_db = list(vector_db_dir.glob("*"))
        print(f"📁 向量数据库目录存在，包含 {len(files_in_db)} 个文件")
        for file in files_in_db[:5]:  # 显示前5个文件
            print(f"   - {file.name}")
        if len(files_in_db) > 5:
            print(f"   ... 还有 {len(files_in_db) - 5} 个文件")
    else:
        print("📁 向量数据库目录不存在")
    
    # 检查文档目录
    doc_dir = Path("赛题制度文档")
    if doc_dir.exists():
        docx_files = list(doc_dir.glob("*.docx"))
        print(f"📄 文档目录存在，包含 {len(docx_files)} 个docx文件")
    else:
        print("📄 文档目录不存在")
    
    # 检查主要文件
    main_files = ["rag_engine.py", "main.py", "config.py", "vector_db.py"]
    for file_name in main_files:
        if Path(file_name).exists():
            print(f"✅ {file_name} 存在")
        else:
            print(f"❌ {file_name} 不存在")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_vector_database()
        elif command == "all":
            clear_vector_database()
            clear_all_cache()
        elif command == "cache":
            clear_all_cache()
        elif command == "status":
            show_current_status()
        else:
            print("使用方法:")
            print("python clear_vector_db.py clear  - 只清除向量数据库")
            print("python clear_vector_db.py all    - 清除向量数据库和缓存")
            print("python clear_vector_db.py cache  - 只清除缓存文件")
            print("python clear_vector_db.py status - 显示当前状态")
    else:
        # 默认只清除向量数据库
        clear_vector_database()
        show_current_status() 