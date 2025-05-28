"""
金融监管制度智能问答系统配置文件
"""

import os
from pathlib import Path

class Config:
    """系统配置类"""
    
    # 模型配置
    LLM_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct"
    EMBEDDING_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Jerry0/m3e-base"
    
    # 数据路径配置
    DOCUMENTS_DIR = "赛题制度文档"
    TEST_DATA_PATH = "数据集A/testA.json"
    OUTPUT_DIR = "output"
    INDEX_DIR = "index"
    
    # 向量数据库配置
    VECTOR_DB_DIR = "vector_db"
    FAISS_INDEX_FILE = "faiss_index.bin"
    VECTOR_METADATA_FILE = "vector_metadata.json"
    DOCUMENT_STORE_FILE = "document_store.json"
    
    # RAG参数配置
    CHUNK_SIZE = 512  # 文档切片大小
    CHUNK_OVERLAP = 50  # 切片重叠大小
    TOP_K = 5  # 检索返回的文档数量
    SIMILARITY_THRESHOLD = 0.7  # 相似度阈值
    
    # 向量数据库参数
    VECTOR_DIMENSION = 768  # m3e-base向量维度
    FAISS_INDEX_TYPE = "IndexFlatIP"  # FAISS索引类型 (内积)
    VECTOR_NORMALIZE = True  # 是否标准化向量
    BATCH_ENCODE_SIZE = 32  # 批量编码大小
    
    # 模型生成参数
    MAX_TOKENS = 2048  # 最大生成长度
    TEMPERATURE = 0.1  # 生成温度
    DO_SAMPLE = True
    TOP_P = 0.8
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个专业的金融监管制度问答助手。请根据提供的文档内容回答问题，确保答案准确、合规。
对于选择题，请分析各个选项，给出正确答案。
对于问答题，请提供详细、准确的回答。
请基于文档内容回答，不要编造信息。"""

    # 选择题提示词模板
    CHOICE_PROMPT_TEMPLATE = """基于以下文档内容，回答选择题：

文档内容：
{context}

问题：{question}
选项：
{options}

请分析各个选项，选择正确答案。只需要输出正确选项（如：A、B、C或D），不需要解释。

答案："""

    # 问答题提示词模板
    QA_PROMPT_TEMPLATE = """基于以下文档内容，回答问题：

文档内容：
{context}

问题：{question}

请提供详细、准确的回答："""

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 批处理配置
    BATCH_SIZE = 10  # 批处理大小
    MAX_RETRIES = 3  # 最大重试次数
    
    # GPU配置
    USE_GPU = True
    GPU_MEMORY_FRACTION = 0.8  # GPU显存使用比例
    
    @classmethod
    def create_dirs(cls):
        """创建必要的目录"""
        dirs = [cls.OUTPUT_DIR, cls.INDEX_DIR, cls.VECTOR_DB_DIR]
        for dir_path in dirs:
            Path(dir_path).mkdir(exist_ok=True)
            print(f"创建目录: {dir_path}")
    
    @classmethod
    def validate_paths(cls):
        """验证路径是否存在"""
        paths_to_check = [
            cls.LLM_MODEL_PATH,
            cls.EMBEDDING_MODEL_PATH,
            cls.DOCUMENTS_DIR,
            cls.TEST_DATA_PATH
        ]
        
        for path in paths_to_check:
            if not Path(path).exists():
                print(f"警告: 路径不存在 - {path}")
                return False
        return True 