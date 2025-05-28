"""
测试DOCX文档处理修复
验证Word文档是否能正确提取文本内容
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(".")

from rag_engine import DocumentProcessor

def test_docx_processing():
    """测试DOCX文档处理"""
    print("=" * 60)
    print("测试DOCX文档处理修复")
    print("=" * 60)
    
    # 创建文档处理器
    processor = DocumentProcessor()
    
    # 查找docx文件
    doc_dir = Path("赛题制度文档")
    if not doc_dir.exists():
        print("❌ 文档目录不存在")
        return False
    
    docx_files = list(doc_dir.glob("*.docx"))[:3]  # 测试前3个文件
    
    if not docx_files:
        print("❌ 未找到docx文件")
        return False
    
    print(f"找到 {len(list(doc_dir.glob('*.docx')))} 个docx文件，测试前3个...")
    
    success_count = 0
    for i, docx_file in enumerate(docx_files, 1):
        print(f"\n--- 测试文件 {i}: {docx_file.name} ---")
        
        try:
            # 测试单个文件读取
            content = processor._read_docx(docx_file)
            
            if content and len(content) > 100:  # 确保提取到了有意义的内容
                print(f"✅ 成功提取 {len(content)} 字符")
                print("内容预览:")
                print("-" * 40)
                preview = content[:300] + "..." if len(content) > 300 else content
                print(preview)
                print("-" * 40)
                success_count += 1
            else:
                print(f"⚠️ 提取内容过少或为空: {len(content) if content else 0} 字符")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
    
    print(f"\n测试结果: {success_count}/{len(docx_files)} 个文件成功处理")
    
    if success_count > 0:
        print("✅ DOCX处理修复成功！")
        return True
    else:
        print("❌ DOCX处理修复失败")
        return False

def test_full_document_loading():
    """测试完整的文档加载流程"""
    print("\n" + "=" * 60)
    print("测试完整文档加载流程")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # 加载所有文档
    documents = processor.load_documents("赛题制度文档")
    
    if documents:
        print(f"✅ 成功加载 {len(documents)} 个文档")
        
        # 显示前3个文档的统计信息
        for i, doc in enumerate(documents[:3]):
            print(f"文档 {i+1}:")
            print(f"  文件名: {doc.metadata.get('filename', 'unknown')}")
            print(f"  文本长度: {len(doc.text)} 字符")
            print(f"  内容预览: {doc.text[:100]}...")
            print()
        
        return True
    else:
        print("❌ 未能加载任何文档")
        return False

if __name__ == "__main__":
    # 测试DOCX处理
    docx_success = test_docx_processing()
    
    # 测试完整流程
    full_success = test_full_document_loading()
    
    print("\n" + "=" * 60)
    if docx_success and full_success:
        print("🎉 所有测试通过！DOCX文档处理修复成功！")
        print("现在可以正确处理Word文档并提取文本内容了。")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 60) 