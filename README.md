# 金融监管制度智能问答系统

基于大模型的金融监管制度智能问答系统，使用RAG（检索增强生成）技术，能够根据金融监管文档回答相关问题。

## 🆕 新增特性 - 向量数据库持久化

- 🗄️ **FAISS向量数据库**：高效的向量存储和检索
- 💾 **持久化存储**：向量数据一次计算，持久保存
- ⚡ **快速启动**：避免重复向量化，大幅提升启动速度
- 🔄 **增量更新**：支持智能增量更新和全量重建
- 🛠️ **数据库管理**：专用管理工具，方便维护

## 项目特性

- 🤖 基于千问2.5-7B大模型
- 🔍 使用RAG技术实现精准检索
- 📚 支持多种文档格式（TXT、PDF、DOCX、MD）
- 🎯 支持选择题和问答题两种题型
- ⚡ 支持批量处理和交互式问答
- 💾 自动保存结果和中间处理状态
- 🔧 智能显存管理和缓存清理
- 🗄️ **FAISS向量数据库持久化**

## 系统架构

```
金融监管制度智能问答系统
├── 配置模块 (config.py)
├── 向量数据库 (vector_db.py) ⭐ 新增
│   ├── FAISS索引管理
│   ├── 向量持久化存储
│   ├── 文档切片管理
│   └── 增量更新机制
├── RAG引擎 (rag_engine.py)
│   ├── 文档处理器
│   ├── 向量索引构建
│   ├── 相似度检索
│   └── 答案生成
├── 主程序 (main.py)
├── 向量数据库管理工具 (vector_db_manager.py) ⭐ 新增
├── 依赖管理 (requirements.txt)
└── 文档目录
    ├── 赛题制度文档/
    ├── 数据集A/testA.json
    └── vector_db/ ⭐ 向量数据库存储目录
        ├── faiss_index.bin
        ├── vector_metadata.json
        └── document_store.json
```

## 环境要求

- Python 3.8+
- CUDA 支持的 GPU（推荐24GB显存）
- ModelScope服务器环境

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 模型路径配置

系统默认使用以下预设路径：

- 大模型：`/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct`
- 嵌入模型：`/mnt/workspace/.cache/modelscope/models/Jerry0/m3e-base`

### 数据路径配置

- 文档目录：`赛题制度文档/`
- 测试数据：`数据集A/testA.json`
- 输出目录：`output/`
- 索引目录：`index/`
- **向量数据库目录：`vector_db/`** ⭐ 新增

### 向量数据库配置

可在 `config.py` 中修改向量数据库相关配置：

```python
# 向量数据库配置
VECTOR_DB_DIR = "vector_db"
FAISS_INDEX_FILE = "faiss_index.bin"
VECTOR_METADATA_FILE = "vector_metadata.json"
DOCUMENT_STORE_FILE = "document_store.json"

# 向量数据库参数
VECTOR_DIMENSION = 768  # m3e-base向量维度
FAISS_INDEX_TYPE = "IndexFlatIP"  # FAISS索引类型
VECTOR_NORMALIZE = True  # 是否标准化向量
BATCH_ENCODE_SIZE = 32  # 批量编码大小
```

## 使用方法

### 1. 批量测试模式（推荐）

运行完整的批量测试：

```bash
python main.py
```

自定义参数运行：

```bash
# 强制重建向量数据库
python main.py --force-rebuild

# 设置批处理大小
python main.py --batch-size 5

# 指定处理范围
python main.py --start-idx 0 --end-idx 50

# 查看向量数据库信息
python main.py --vector-info

# 重建向量数据库
python main.py --rebuild-vector
```

### 2. 交互式问答模式

```bash
python main.py --interactive
```

在交互模式下：
- 输入问题进行实时问答
- 输入 `info` 查看向量数据库信息
- 输入 `quit` 退出

### 3. 向量数据库管理 ⭐ 新增

使用专用管理工具：

```bash
# 查看向量数据库状态
python vector_db_manager.py --status

# 构建向量数据库
python vector_db_manager.py --build

# 强制重建向量数据库
python vector_db_manager.py --force-rebuild

# 搜索文档
python vector_db_manager.py --search "银行资本充足率" --top-k 3

# 测试搜索功能
python vector_db_manager.py --test-search

# 清空向量数据库
python vector_db_manager.py --clear
```

## 向量数据库优势

### 性能提升
- **首次启动**：需要构建向量数据库（耗时较长）
- **后续启动**：直接加载预计算向量（秒级启动）
- **内存效率**：优化的FAISS索引，高效检索

### 存储结构
```
vector_db/
├── faiss_index.bin          # FAISS向量索引文件
├── vector_metadata.json     # 向量数据库元数据
└── document_store.json      # 文档内容和元数据存储
```

### 智能更新
- **自动检测**：检测文档变更，智能决定是否需要重建
- **增量更新**：支持新增文档的增量处理
- **版本管理**：记录构建时间和文档版本信息

## 输入数据格式

测试数据应为JSON格式，支持以下两种题型：

### 选择题格式
```json
{
  "id": 12,
  "category": "选择题",
  "question": "城商行内审部门负责人任职后需在多少日内备案？",
  "content": "A. 3个工作日\nB. 5个工作日\nC. 10个工作日\nD. 30个工作日"
}
```

### 问答题格式
```json
{
  "id": 13,
  "category": "问答题",
  "question": "简述商业银行资本充足率的最低监管要求指标及各自数值。",
  "content": null
}
```

## 输出结果

系统会生成以下输出文件：

1. **JSON结果文件**：包含完整的问答结果和元数据
2. **CSV结果文件**：便于查看和分析的表格格式
3. **批次中间结果**：每个批次的中间结果，防止数据丢失

### 结果格式示例

```json
{
  "id": 12,
  "category": "选择题",
  "question": "城商行内审部门负责人任职后需在多少日内备案？",
  "content": "A. 3个工作日\nB. 5个工作日\nC. 10个工作日\nD. 30个工作日",
  "answer": "C",
  "context_used": "相关文档内容...",
  "num_sources": 3,
  "timestamp": "2024-01-01 12:00:00"
}
```

## 性能优化

### 向量数据库优化
- **FAISS索引类型**：
  - `IndexFlatIP`：内积索引，精度高（默认）
  - `IndexFlatL2`：L2距离索引
  - `IndexIVFFlat`：IVF索引，适合大规模数据

### 显存管理
- 自动检测GPU可用性
- 定期清理CUDA缓存
- 支持显存使用比例配置

### 批处理优化
- 支持自定义批处理大小
- 自动保存中间结果
- 支持断点续传

### 索引优化
- **向量持久化**：避免重复计算
- 增量索引更新
- 智能索引重建

## 参数配置

### RAG参数
- `CHUNK_SIZE`: 文档切片大小（默认512）
- `CHUNK_OVERLAP`: 切片重叠大小（默认50）
- `TOP_K`: 检索返回数量（默认5）
- `SIMILARITY_THRESHOLD`: 相似度阈值（默认0.7）

### 向量数据库参数
- `VECTOR_DIMENSION`: 向量维度（默认768）
- `FAISS_INDEX_TYPE`: FAISS索引类型
- `VECTOR_NORMALIZE`: 是否标准化向量
- `BATCH_ENCODE_SIZE`: 批量编码大小

### 生成参数
- `MAX_TOKENS`: 最大生成长度（默认2048）
- `TEMPERATURE`: 生成温度（默认0.1）
- `TOP_P`: 核采样参数（默认0.8）

### 系统参数
- `BATCH_SIZE`: 批处理大小（默认10）
- `MAX_RETRIES`: 最大重试次数（默认3）
- `GPU_MEMORY_FRACTION`: GPU显存使用比例（默认0.8）

## 错误处理

系统具备完善的错误处理机制：

1. **路径验证**：启动时检查所有必要路径
2. **异常捕获**：捕获并记录处理过程中的异常
3. **资源清理**：自动清理GPU缓存和系统资源
4. **断点续传**：支持从中断点继续处理
5. **向量数据库恢复**：自动检测和恢复损坏的向量数据库

## 日志输出

系统提供详细的日志输出，包括：

- 系统初始化状态
- 模型加载进度
- 向量数据库构建进度
- 文档处理详情
- 问题处理过程
- 错误信息和堆栈
- 性能统计信息

## 故障排除

### 常见问题

1. **模型路径不存在**
   - 检查 `config.py` 中的模型路径配置
   - 确认模型已正确下载到指定位置

2. **显存不足**
   - 减小 `BATCH_SIZE` 参数
   - 调整 `GPU_MEMORY_FRACTION` 参数
   - 减小 `CHUNK_SIZE` 参数

3. **文档加载失败**
   - 检查文档目录路径
   - 确认文档格式支持
   - 检查文档编码格式

4. **向量数据库损坏** ⭐ 新增
   - 使用 `python vector_db_manager.py --status` 检查状态
   - 使用 `--force-rebuild` 重建数据库
   - 检查磁盘空间是否充足

5. **索引构建失败**
   - 使用 `--force-rebuild` 重新构建
   - 检查磁盘空间是否充足
   - 确认写入权限

### 性能调优建议

1. **提高处理速度**
   - 使用向量数据库持久化（首次构建后显著提速）
   - 增大批处理大小（在显存允许的情况下）
   - 选择合适的FAISS索引类型

2. **提高答案质量**
   - 增大文档切片大小
   - 提高相似度阈值
   - 增加检索返回数量

3. **节约显存和存储**
   - 减小批处理大小
   - 启用定期缓存清理
   - 调整模型精度配置
   - 使用压缩的FAISS索引类型

## 开发者指南

### 扩展新的文档格式

在 `rag_engine.py` 的 `DocumentProcessor` 类中添加新的文件格式支持：

```python
def _read_file(self, file_path: Path) -> str:
    if file_path.suffix.lower() == '.your_format':
        # 添加您的文档读取逻辑
        return content
```

### 自定义向量数据库索引

在 `config.py` 中修改FAISS索引配置：

```python
FAISS_INDEX_TYPE = "IndexIVFFlat"  # 更改索引类型
VECTOR_DIMENSION = 768  # 匹配嵌入模型维度
```

### 自定义提示词模板

在 `config.py` 中修改提示词模板：

```python
CUSTOM_PROMPT_TEMPLATE = """您的自定义提示词模板"""
```

### 添加新的评估指标

在 `main.py` 的 `print_statistics` 方法中添加新的统计指标。

## 快速启动指南

### 第一次使用
```bash
# 1. 验证环境
python test_setup.py

# 2. 安装依赖
pip install -r requirements.txt

# 3. 构建向量数据库（一次性操作）
python vector_db_manager.py --build

# 4. 运行测试
python main.py --batch-size 5 --end-idx 10
```

### 日常使用
```bash
# 直接运行（秒级启动）
python main.py

# 或交互式问答
python main.py --interactive
```

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请联系开发团队。 