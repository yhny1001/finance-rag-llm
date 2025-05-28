# 🚀 金融监管制度RAG问答系统 - 简化使用指南

## 🎯 已修复问题
✅ **Word文档(.docx)乱码问题已完全修复**  
✅ 现在可以正确提取中文文本内容  
✅ 添加了数据库管理工具  

## ⚡ 快速启动

### 方法1: 一键启动(推荐)
```bash
python start.py
```
自动检查依赖、清理数据库、启动系统

### 方法2: 手动启动
```bash
# 1. 清除旧的向量数据库(修复乱码)
python clear_vector_db.py clear

# 2. 运行主程序
python main.py
```

## 🛠️ 数据库管理

```bash
# 清除向量数据库，强制重新构建
python clear_vector_db.py clear

# 清除所有缓存和数据库
python clear_vector_db.py all

# 查看当前状态
python clear_vector_db.py status
```

## 📋 系统要求

- **依赖**: `pip install python-docx PyPDF2`
- **文档**: 将Word文档放在`赛题制度文档/`目录
- **测试数据**: `数据集A/testA.json`

## 🔍 验证修复

运行测试验证DOCX文档是否正确处理：
```bash
python test_docx_fix.py
```

## ⚠️ 问题排查

**如果仍然看到乱码:**
1. 运行 `python clear_vector_db.py clear`
2. 确认已安装 `python-docx`
3. 重新运行 `python main.py`

**如果模型加载失败:**
```bash
pip install transformers==4.44.0
```

---

🎉 **现在系统已完全修复，可以正确处理Word文档了！** 