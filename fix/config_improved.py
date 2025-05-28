"""
改进版配置文件
针对系统分数低的问题，优化各项参数设置
"""

import os
from pathlib import Path

class ImprovedConfig:
    """改进版配置类"""
    
    # 基础路径配置
    BASE_DIR = Path(__file__).parent
    DOCUMENTS_DIR = BASE_DIR / "documents"
    VECTOR_DB_DIR = BASE_DIR / "vector_db"
    TEST_DATA_PATH = BASE_DIR / "金融监管制度问答-测试集.jsonl"
    
    # 文档处理配置 - 关键优化点
    CHUNK_SIZE = 1000              # 增大切片大小，减少信息分割
    CHUNK_OVERLAP = 200            # 增大重叠，确保连续性
    
    # 向量检索配置 - 核心改进
    TOP_K = 10                     # 增加检索数量，获取更多上下文
    SIMILARITY_THRESHOLD = 0.25    # 降低阈值，包含更多相关内容
    
    # Embedding模型配置
    EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    EMBEDDING_BATCH_SIZE = 8       # 减小批次大小，提高稳定性
    
    # LLM模型配置
    LLM_MODEL_PATH = r"D:\model\Qwen2.5-7B-Instruct"
    LLM_DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    
    # 生成参数配置 - 重要优化
    MAX_TOKENS = 2048              # 增加最大token数，允许更详细回答
    TEMPERATURE = 0.1              # 降低随机性，提高准确性
    TOP_P = 0.8                    # 适度的多样性
    REPETITION_PENALTY = 1.1       # 避免重复
    
    # 批处理配置
    BATCH_SIZE = 3                 # 减小批次，提高成功率
    MAX_WORKERS = 2                # 减少并发，提高稳定性
    
    # 提示词模板 - 大幅改进
    CHOICE_QUESTION_PROMPT = """你是一名专业的金融监管法规专家，请根据提供的参考资料，准确回答选择题。

参考资料：
{context}

问题：{question}
选项：{options}

请仔细分析参考资料，结合金融监管知识，选择最准确的答案。

分析步骤：
1. 理解问题的核心要求
2. 在参考资料中查找相关信息
3. 对比各选项与参考资料的匹配程度
4. 选择最符合监管要求的答案

请直接输出选择的选项字母（A、B、C或D），不需要其他解释。

答案："""

    QA_QUESTION_PROMPT = """你是一名专业的金融监管法规专家，请根据提供的参考资料，详细回答问题。

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

    # 错误处理配置
    MAX_RETRIES = 3                # 最大重试次数
    RETRY_DELAY = 2                # 重试间隔（秒）
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "improved_system.log"
    
    # 缓存配置
    ENABLE_CACHE = True
    CACHE_DIR = BASE_DIR / "cache"
    
    # 新增：质量控制配置
    MIN_ANSWER_LENGTH = 50         # 最小答案长度
    MAX_ANSWER_LENGTH = 1000       # 最大答案长度
    REQUIRE_KEYWORDS = True        # 是否要求答案包含关键词
    
    # 新增：选择题答案提取配置
    CHOICE_EXTRACTION_PATTERNS = [
        r'答案[是为：:]\s*([A-D])',
        r'选择\s*([A-D])',
        r'正确答案[是为：:]\s*([A-D])',
        r'答案为\s*([A-D])',
        r'选项\s*([A-D])',
        r'([A-D])\s*是正确的',
        r'([A-D])\s*正确',
        r'应该选择\s*([A-D])',
        r'选择题答案[：:]\s*([A-D])',
        r'^\s*([A-D])\s*$',          # 单独的字母
        r'[^A-Za-z]([A-D])[^A-Za-z]', # 被非字母包围的字母
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
    def get_improved_generation_config(cls):
        """获取改进的生成配置"""
        return {
            "max_new_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P,
            "repetition_penalty": cls.REPETITION_PENALTY,
            "do_sample": True,
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
        if not cls.DOCUMENTS_DIR.exists():
            issues.append(f"文档目录不存在: {cls.DOCUMENTS_DIR}")
        
        if not cls.TEST_DATA_PATH.exists():
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

# 使用示例
Config = ImprovedConfig 