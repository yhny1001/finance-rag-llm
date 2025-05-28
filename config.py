"""
修复后的改进版配置文件
保留所有必要配置项，修正模型路径，优化参数设置
"""

import os
from pathlib import Path

class Config:
    """改进版配置类"""
    
    # 基础路径配置
    BASE_DIR = Path(__file__).parent
    
    # 模型配置 - 修正为服务器路径
    LLM_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct"
    EMBEDDING_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Jerry0/m3e-base"
    
    # 数据路径配置
    DOCUMENTS_DIR = "赛题制度文档"
    TEST_DATA_PATH = "数据集A/testA.json"
    OUTPUT_DIR = "output"
    INDEX_DIR = "index"
    
    # 向量数据库配置 - 保留所有必要文件配置
    VECTOR_DB_DIR = "vector_db"
    FAISS_INDEX_FILE = "faiss_index.bin"
    VECTOR_METADATA_FILE = "vector_metadata.json"
    DOCUMENT_STORE_FILE = "document_store.json"
    
    # RAG参数配置 - 优化后的参数
    CHUNK_SIZE = 1000              # 增大切片大小，减少信息分割
    CHUNK_OVERLAP = 200            # 增大重叠，确保连续性
    TOP_K = 10                     # 增加检索数量，获取更多上下文
    SIMILARITY_THRESHOLD = 0.25    # 降低阈值，包含更多相关内容
    
    # 向量数据库参数
    VECTOR_DIMENSION = 768  # m3e-base向量维度
    FAISS_INDEX_TYPE = "IndexFlatIP"  # FAISS索引类型 (内积)
    VECTOR_NORMALIZE = True  # 是否标准化向量
    BATCH_ENCODE_SIZE = 8   # 减小批次大小，提高稳定性
    
    # 模型生成参数 - 优化设置
    MAX_TOKENS = 2048              # 增加最大token数
    TEMPERATURE = 0.1              # 降低随机性，提高准确性
    DO_SAMPLE = True
    TOP_P = 0.8                    # 适度的多样性
    REPETITION_PENALTY = 1.1       # 避免重复
    
    # 系统提示词 - 保持原有
    SYSTEM_PROMPT = """你是一个专业的金融监管制度问答助手。请根据提供的文档内容回答问题，确保答案准确、合规。
对于选择题，请分析各个选项，给出正确答案。
对于问答题，请提供详细、准确的回答。
请基于文档内容回答，不要编造信息。"""

    # 选择题提示词模板 - 改进版，支持不定项选择
    CHOICE_PROMPT_TEMPLATE = """你是一名专业的金融监管法规专家，请根据提供的参考资料，准确回答选择题。

参考资料：
{context}

问题：{question}
选项：
{options}

注意：这是不定项选择题，可能有一个或多个正确答案。请仔细分析每个选项。

分析步骤：
1. 理解问题的核心要求
2. 在参考资料中查找相关信息
3. 对比各选项与参考资料的匹配程度
4. 判断每个选项的正确性

请务必先详细分析每个选项，说明你的推理过程，引用相关的参考资料内容，然后给出最终答案。

对于每个选项，请按以下格式分析：
选项A: [分析选项A是否正确的依据]
选项B: [分析选项B是否正确的依据]
选项C: [分析选项C是否正确的依据]
选项D: [分析选项D是否正确的依据]

最后，基于以上分析，给出答案。
如果是单选题，请直接输出一个选项字母（如A）
如果是多选题，请输出所有正确选项字母，用逗号分隔（如A,C,D）

答案："""

    # 问答题提示词模板 - 改进版
    QA_PROMPT_TEMPLATE = """你是一名专业的金融监管法规专家，请根据提供的参考资料，详细回答问题。

参考资料：
{context}

问题：{question}

请基于参考资料，提供准确、详细的回答。回答要求：
1. 信息准确，基于参考资料
2. 结构清晰，逻辑分明
3. 包含具体的数字、比例、标准等关键信息
4. 涵盖相关的监管要求和操作要点
5. 字数在200-500字之间

答案："""

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 批处理配置 - 优化后的设置
    BATCH_SIZE = 3                 # 减小批次，提高成功率
    MAX_RETRIES = 3                # 最大重试次数
    MAX_WORKERS = 2                # 减少并发，提高稳定性
    
    # GPU配置
    USE_GPU = True
    GPU_MEMORY_FRACTION = 0.8  # GPU显存使用比例
    
    # 新增：质量控制配置
    MIN_ANSWER_LENGTH = 50         # 最小答案长度
    MAX_ANSWER_LENGTH = 1000       # 最大答案长度
    REQUIRE_KEYWORDS = True        # 是否要求答案包含关键词
    
    # 新增：选择题答案提取配置，支持多选
    CHOICE_EXTRACTION_PATTERNS = [
        r'答案[是为：:]\s*([A-D,]+)',
        r'选择\s*([A-D,]+)',
        r'正确答案[是为：:]\s*([A-D,]+)',
        r'答案为\s*([A-D,]+)',
        r'选项\s*([A-D,]+)',
        r'([A-D,]+)\s*是正确的',
        r'([A-D,]+)\s*正确',
        r'应该选择\s*([A-D,]+)',
        r'选择题答案[：:]\s*([A-D,]+)',
        r'^\s*([A-D,]+)\s*$',          # 单独的字母或字母组合
        r'[^A-Za-z]([A-D,]+)[^A-Za-z]', # 被非字母包围的字母组合
    ]
    
    # 新增：文档预处理配置
    REMOVE_HEADERS = True          # 移除页眉页脚
    NORMALIZE_WHITESPACE = True    # 标准化空白字符
    MERGE_SHORT_LINES = True       # 合并短行
    MIN_SENTENCE_LENGTH = 10       # 最小句子长度
    
    # 新增：检索优化配置
    USE_RERANKING = False          # 暂不使用重排序（减少复杂度）
    DIVERSITY_THRESHOLD = 0.8      # 结果多样性阈值
    CONTENT_FILTER_MIN_LENGTH = 20 # 内容过滤最小长度
    
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
    
    @classmethod
    def get_improved_generation_config(cls):
        """获取改进的生成配置"""
        return {
            "max_new_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P,
            "repetition_penalty": cls.REPETITION_PENALTY,
            "do_sample": cls.DO_SAMPLE,
            "pad_token_id": 151643,  # Qwen2的pad_token_id
            "eos_token_id": 151645,  # Qwen2的eos_token_id
        }
    
    @classmethod
    def get_retrieval_config(cls):
        """获取检索配置"""
        return {
            "top_k": cls.TOP_K,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD,
            "diversity_threshold": cls.DIVERSITY_THRESHOLD,
            "min_content_length": cls.CONTENT_FILTER_MIN_LENGTH,
        }
    
    @classmethod
    def get_chunking_config(cls):
        """获取文档切片配置"""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "remove_headers": cls.REMOVE_HEADERS,
            "normalize_whitespace": cls.NORMALIZE_WHITESPACE,
            "merge_short_lines": cls.MERGE_SHORT_LINES,
            "min_sentence_length": cls.MIN_SENTENCE_LENGTH,
        }
    
    @classmethod
    def validate_config(cls):
        """验证配置有效性"""
        issues = []
        
        # 检查必要的路径
        if not Path(cls.DOCUMENTS_DIR).exists():
            issues.append(f"文档目录不存在: {cls.DOCUMENTS_DIR}")
        
        if not Path(cls.TEST_DATA_PATH).exists():
            issues.append(f"测试数据文件不存在: {cls.TEST_DATA_PATH}")
        
        # 检查参数合理性
        if cls.CHUNK_SIZE <= 100:
            issues.append("CHUNK_SIZE过小，可能导致信息分割")
        
        if cls.TOP_K < 5:
            issues.append("TOP_K过小，可能信息不足")
        
        if cls.SIMILARITY_THRESHOLD > 0.7:
            issues.append("SIMILARITY_THRESHOLD过高，可能过滤掉相关内容")
        
        if cls.MAX_TOKENS < 500:
            issues.append("MAX_TOKENS过小，可能导致回答不完整")
        
        return issues 