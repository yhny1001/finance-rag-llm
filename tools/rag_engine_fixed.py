#!/usr/bin/env python
"""
修复版本的 RAG 引擎 - 解决 transformers 库 NoneType 错误
包含多种解决方案的 RAG 核心实现
"""

import os
import sys
import torch
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM

class FixedRAGEngine:
    """修复版本的 RAG 引擎"""
    
    def __init__(self, config):
        """初始化RAG引擎"""
        self.config = config
        self.llm = None
        self.tokenizer = None
        self.embedding_model = None
        self.index = None
        self.query_engine = None
        
        # 应用修复补丁
        self._apply_transformers_fix()
        
        # 设置环境变量
        self._set_environment_variables()
    
    def _apply_transformers_fix(self):
        """应用 transformers 库修复补丁"""
        print("🔧 应用 transformers 库修复补丁...")
        
        try:
            import transformers.modeling_utils as modeling_utils
            
            # 修复 ALL_PARALLEL_STYLES
            if hasattr(modeling_utils, 'ALL_PARALLEL_STYLES'):
                if modeling_utils.ALL_PARALLEL_STYLES is None:
                    print("⚠️  发现 ALL_PARALLEL_STYLES 为 None，正在修复...")
                    modeling_utils.ALL_PARALLEL_STYLES = [
                        "model_parallel",
                        "pipeline_parallel", 
                        "tensor_parallel",
                        "data_parallel"
                    ]
                    print("✅ ALL_PARALLEL_STYLES 修复完成")
                else:
                    print("✅ ALL_PARALLEL_STYLES 正常")
            else:
                print("⚠️  添加 ALL_PARALLEL_STYLES 属性...")
                modeling_utils.ALL_PARALLEL_STYLES = [
                    "model_parallel",
                    "pipeline_parallel", 
                    "tensor_parallel", 
                    "data_parallel"
                ]
                print("✅ ALL_PARALLEL_STYLES 添加完成")
                
        except Exception as e:
            print(f"⚠️  运行时补丁应用失败: {e}")
            print("将继续尝试其他解决方案...")
    
    def _set_environment_variables(self):
        """设置环境变量"""
        print("🔧 设置环境变量...")
        
        # 设置 transformers 相关环境变量
        os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        
        print("✅ 环境变量设置完成")
    
    def load_llm_with_retry(self):
        """使用重试机制加载LLM模型"""
        print(f"🤖 加载LLM模型: {self.config.LLM_MODEL_PATH}")
        
        # 加载策略列表（从最安全到最高性能）
        load_strategies = [
            {
                "name": "最安全模式",
                "params": {
                    "torch_dtype": torch.float32,
                    "device_map": "cpu",
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True
                }
            },
            {
                "name": "CPU模式",
                "params": {
                    "torch_dtype": torch.float16,
                    "device_map": "cpu", 
                    "trust_remote_code": True
                }
            },
            {
                "name": "单GPU模式",
                "params": {
                    "torch_dtype": torch.float16,
                    "device_map": "cuda:0",
                    "trust_remote_code": True
                }
            },
            {
                "name": "自动设备映射",
                "params": {
                    "torch_dtype": torch.float16,
                    "device_map": "auto",
                    "trust_remote_code": True
                }
            }
        ]
        
        # 首先加载 tokenizer
        try:
            print("📝 加载 tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.LLM_MODEL_PATH,
                trust_remote_code=True
            )
            print("✅ tokenizer 加载成功")
        except Exception as e:
            print(f"❌ tokenizer 加载失败: {e}")
            return False
        
        # 尝试不同策略加载模型
        for strategy in load_strategies:
            try:
                print(f"🔄 尝试策略: {strategy['name']}")
                print(f"参数: {strategy['params']}")
                
                # 清理GPU缓存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
                
                # 加载模型
                self.llm = AutoModelForCausalLM.from_pretrained(
                    self.config.LLM_MODEL_PATH,
                    **strategy['params']
                )
                
                print(f"✅ 使用 {strategy['name']} 加载模型成功！")
                return True
                
            except Exception as e:
                print(f"❌ 策略 {strategy['name']} 失败: {e}")
                
                # 如果是我们要修复的特定错误，显示详细信息
                if "NoneType" in str(e) and "iterable" in str(e):
                    print("🎯 这是我们要修复的 NoneType 错误！")
                    print("正在尝试下一个策略...")
                
                # 清理失败的模型
                if hasattr(self, 'llm') and self.llm is not None:
                    del self.llm
                    self.llm = None
                
                continue
        
        print("❌ 所有加载策略都失败了")
        return False
    
    def load_embedding_model(self):
        """加载嵌入模型"""
        print(f"📊 加载嵌入模型: {self.config.EMBEDDING_MODEL_PATH}")
        
        try:
            self.embedding_model = HuggingFaceEmbedding(
                model_name=self.config.EMBEDDING_MODEL_PATH,
                trust_remote_code=True
            )
            print("✅ 嵌入模型加载成功")
            return True
        except Exception as e:
            print(f"❌ 嵌入模型加载失败: {e}")
            return False
    
    def initialize(self):
        """初始化 RAG 引擎"""
        print("🚀 初始化 RAG 引擎...")
        
        # 1. 加载嵌入模型
        if not self.load_embedding_model():
            return False
        
        # 2. 加载LLM模型
        if not self.load_llm_with_retry():
            return False
        
        # 3. 设置全局配置
        Settings.embed_model = self.embedding_model
        
        print("✅ RAG 引擎初始化成功")
        return True
    
    def create_documents(self, texts: List[str]) -> List[Document]:
        """创建文档对象"""
        print(f"📄 创建 {len(texts)} 个文档...")
        documents = [Document(text=text) for text in texts]
        print("✅ 文档创建完成")
        return documents
    
    def build_index(self, documents: List[Document]):
        """构建向量索引"""
        print("🔍 构建向量索引...")
        
        try:
            self.index = VectorStoreIndex.from_documents(documents)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=self.config.TOP_K,
                response_mode="compact"
            )
            print("✅ 向量索引构建完成")
            return True
        except Exception as e:
            print(f"❌ 索引构建失败: {e}")
            return False
    
    def generate_answer(self, query: str, retrieved_texts: List[str]) -> str:
        """使用LLM生成答案"""
        try:
            # 构建提示词
            context = "\n\n".join(retrieved_texts)
            prompt = f"""基于以下文档内容回答问题：

文档内容：
{context}

问题：{query}

请根据文档内容准确回答问题："""
            
            # 使用tokenizer编码
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # 移动到正确的设备
            if torch.cuda.is_available() and next(self.llm.parameters()).is_cuda:
                inputs = inputs.cuda()
            
            # 生成答案
            with torch.no_grad():
                outputs = self.llm.generate(
                    inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码答案
            answer = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return answer.strip()
            
        except Exception as e:
            print(f"❌ 答案生成失败: {e}")
            return f"生成答案时出错: {str(e)}"
    
    def query(self, question: str) -> Dict[str, Any]:
        """查询接口"""
        try:
            print(f"🔍 查询: {question}")
            
            # 使用查询引擎检索
            response = self.query_engine.query(question)
            
            # 提取检索到的文本
            retrieved_texts = []
            if hasattr(response, 'source_nodes'):
                retrieved_texts = [node.text for node in response.source_nodes]
            
            # 使用LLM生成最终答案
            if self.llm and self.tokenizer:
                answer = self.generate_answer(question, retrieved_texts)
            else:
                answer = str(response)
            
            return {
                "question": question,
                "answer": answer,
                "retrieved_texts": retrieved_texts,
                "confidence": 0.8  # 简单的置信度
            }
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return {
                "question": question,
                "answer": f"查询失败: {str(e)}",
                "retrieved_texts": [],
                "confidence": 0.0
            }
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        
        if self.llm:
            del self.llm
            self.llm = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        
        if self.embedding_model:
            del self.embedding_model
            self.embedding_model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        gc.collect()
        print("✅ 资源清理完成")

# 测试函数
def test_fixed_rag_engine():
    """测试修复版本的RAG引擎"""
    print("="*60)
    print("🧪 测试修复版本的 RAG 引擎")
    print("="*60)
    
    try:
        from config import Config
        
        # 创建RAG引擎
        rag_engine = FixedRAGEngine(Config)
        
        # 初始化
        if not rag_engine.initialize():
            print("❌ RAG引擎初始化失败")
            return False
        
        # 测试文档
        test_documents = [
            "银行资本充足率监管要求：核心一级资本充足率不得低于5%，一级资本充足率不得低于6%，资本充足率不得低于8%。",
            "个人理财产品销售需要进行风险评估，确保产品风险等级与客户风险承受能力相匹配。",
            "城商行内审部门负责人任职后需在5个工作日内向监管部门备案。"
        ]
        
        # 创建文档并构建索引
        documents = rag_engine.create_documents(test_documents)
        if not rag_engine.build_index(documents):
            print("❌ 索引构建失败")
            return False
        
        # 测试查询
        test_questions = [
            "银行资本充足率的最低要求是多少？",
            "城商行内审部门负责人任职后多久需要备案？"
        ]
        
        for question in test_questions:
            result = rag_engine.query(question)
            print(f"\n问题: {result['question']}")
            print(f"答案: {result['answer']}")
            print(f"置信度: {result['confidence']}")
        
        # 清理资源
        rag_engine.cleanup()
        
        print("\n🎉 测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_rag_engine() 