"""
优化版配置文件 - 针对低分问题的改进
"""

from pathlib import Path

class Config:
    """优化版系统配置"""
    
    # 基础路径配置
    BASE_DIR = Path(".")
    DOCUMENTS_DIR = "赛题制度文档"
    TEST_DATA_PATH = "数据集A/testA.json"
    OUTPUT_DIR = "outputs"
    
    # 模型配置
    LLM_MODEL_PATH = "Qwen/Qwen2.5-7B-Instruct"
    EMBEDDING_MODEL_PATH = "moka-ai/m3e-base"
    
    # 🎯 优化：减小切片大小，提高检索精度
    CHUNK_SIZE = 600  # 从1000减少到600，更精确的文档片段
    CHUNK_OVERLAP = 100  # 增加重叠，避免重要信息被切断
    
    # 🎯 优化：增加检索数量，提供更多上下文
    TOP_K = 8  # 从5增加到8，检索更多相关文档
    TOP_K_RETRIEVAL = 8
    
    # 🎯 优化：调整相似度阈值
    SIMILARITY_THRESHOLD = 0.3  # 降低阈值，包含更多可能相关的内容
    
    # 批处理配置
    BATCH_SIZE = 5  # 减小批次，更好的内存管理
    
    # 🎯 优化：增加生成长度
    MAX_TOKENS = 2048  # 增加最大token数，允许更详细的回答
    
    # 🎯 改进的提示词模板
    QA_PROMPT_TEMPLATE = """你是一个专业的金融监管制度专家，请基于以下相关文档内容，准确回答问题。

相关文档内容：
{context}

问题：{question}

回答要求：
1. 基于文档内容提供准确、详细的答案
2. 如果文档中有具体的数字、比例、条款，必须准确引用
3. 答案要完整、逻辑清晰
4. 如果文档内容不足以回答问题，请明确说明

答案："""

    CHOICE_PROMPT_TEMPLATE = """你是一个专业的金融监管制度专家，请基于以下相关文档内容，分析选择题并给出正确答案。

相关文档内容：
{context}

问题：{question}

选项：
{options}

分析要求：
1. 仔细分析每个选项与文档内容的符合程度
2. 基于文档内容选择最准确的答案
3. 先分析，再明确给出答案选项(A/B/C/D)

分析过程：
[请逐一分析各选项]

正确答案："""

    # 向量数据库配置
    VECTOR_DB_DIR = "vector_db"
    FAISS_INDEX_FILE = "faiss_index.bin"
    METADATA_FILE = "metadata.json"
    
    # 🎯 优化：模型推理参数
    GENERATION_CONFIG = {
        "temperature": 0.1,  # 降低随机性，提高一致性
        "top_p": 0.8,
        "top_k": 40,
        "do_sample": True,
        "repetition_penalty": 1.1
    }
    
    # 🎯 优化：重排序配置
    USE_RERANK = True  # 启用重排序
    RERANK_TOP_K = 15  # 初次检索更多，然后重排序
    
    @classmethod
    def validate_paths(cls) -> bool:
        """验证必要路径是否存在"""
        doc_path = Path(cls.DOCUMENTS_DIR)
        test_path = Path(cls.TEST_DATA_PATH)
        
        if not doc_path.exists():
            print(f"❌ 文档目录不存在: {cls.DOCUMENTS_DIR}")
            return False
            
        if not test_path.exists():
            print(f"❌ 测试数据不存在: {cls.TEST_DATA_PATH}")
            return False
            
        # 检查文档目录中是否有.docx文件
        docx_files = list(doc_path.glob("*.docx"))
        if not docx_files:
            print(f"⚠️ 文档目录中没有.docx文件")
            
        print(f"✅ 找到 {len(docx_files)} 个.docx文件")
        return True
    
    @classmethod
    def create_dirs(cls):
        """创建必要的目录"""
        Path(cls.OUTPUT_DIR).mkdir(exist_ok=True)
        Path(cls.VECTOR_DB_DIR).mkdir(exist_ok=True)
        print("📁 目录结构检查完成") 