#!/usr/bin/env python
"""
简化版 RAG 引擎 - 避免 transformers 并行处理问题
专为 ModelScope 环境设计的最小化实现
"""

import os
import torch
import gc
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class SimpleRAGEngine:
    """简化版 RAG 引擎"""
    
    def __init__(self, config):
        """初始化"""
        self.config = config
        self.llm = None
        self.tokenizer = None
        self.embedding_model = None
        self.index = None
        self.query_engine = None
        
    def load_embedding_model(self):
        """加载嵌入模型 - 优先方案"""
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
    
    def load_llm_simple(self):
        """简单加载LLM - 避免复杂并行处理"""
        print(f"🤖 简单加载LLM: {self.config.LLM_MODEL_PATH}")
        
        try:
            # 设置简单的环境变量
            os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
            # 加载 tokenizer
            print("📝 加载 tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.LLM_MODEL_PATH,
                trust_remote_code=True,
                use_fast=False  # 避免fast tokenizer的问题
            )
            print("✅ tokenizer 加载成功")
            
            # 简单加载模型 - CPU模式避免GPU问题
            print("🔄 加载模型 (CPU模式)...")
            self.llm = AutoModelForCausalLM.from_pretrained(
                self.config.LLM_MODEL_PATH,
                torch_dtype=torch.float32,  # 使用float32避免精度问题
                device_map="cpu",           # 强制使用CPU
                trust_remote_code=True,
                low_cpu_mem_usage=True      # 低内存模式
            )
            print("✅ LLM模型加载成功 (CPU模式)")
            return True
            
        except Exception as e:
            print(f"❌ LLM加载失败: {e}")
            # 如果还是失败，尝试最基本的加载
            try:
                print("🔄 尝试最基本的加载方式...")
                self.llm = AutoModelForCausalLM.from_pretrained(
                    self.config.LLM_MODEL_PATH,
                    trust_remote_code=True
                )
                print("✅ 基本模式加载成功")
                return True
            except Exception as e2:
                print(f"❌ 基本模式也失败: {e2}")
                return False
    
    def initialize(self):
        """初始化引擎"""
        print("🚀 初始化简化版 RAG 引擎...")
        
        # 1. 加载嵌入模型
        if not self.load_embedding_model():
            print("❌ 嵌入模型加载失败，但继续尝试...")
        
        # 2. 加载LLM (可选)
        llm_loaded = self.load_llm_simple()
        if not llm_loaded:
            print("⚠️  LLM加载失败，将使用纯检索模式")
        
        # 3. 设置全局配置
        if self.embedding_model:
            Settings.embed_model = self.embedding_model
        
        print("✅ RAG 引擎初始化完成")
        return True
    
    def create_documents(self, texts: List[str]) -> List[Document]:
        """创建文档"""
        print(f"📄 创建 {len(texts)} 个文档...")
        documents = [Document(text=text) for text in texts]
        print("✅ 文档创建完成")
        return documents
    
    def build_index(self, documents: List[Document]):
        """构建索引"""
        print("🔍 构建向量索引...")
        
        try:
            self.index = VectorStoreIndex.from_documents(documents)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=getattr(self.config, 'TOP_K', 3),
                response_mode="compact"
            )
            print("✅ 向量索引构建完成")
            return True
        except Exception as e:
            print(f"❌ 索引构建失败: {e}")
            return False
    
    def generate_simple_answer(self, query: str, retrieved_texts: List[str]) -> str:
        """简单生成答案"""
        if not self.llm or not self.tokenizer:
            # 如果没有LLM，返回检索到的文本摘要
            if retrieved_texts:
                return f"根据相关文档，{query}的相关信息如下：\n" + "\n".join(retrieved_texts[:2])
            else:
                return "未找到相关信息"
        
        try:
            # 构建简单提示词
            context = "\n".join(retrieved_texts[:2])  # 只取前2个结果避免过长
            prompt = f"问题：{query}\n参考内容：{context}\n回答："
            
            # 简单生成
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.llm.generate(
                    inputs,
                    max_new_tokens=256,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            answer = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return answer.strip() if answer.strip() else "无法生成答案"
            
        except Exception as e:
            print(f"⚠️  生成失败，返回检索结果: {e}")
            if retrieved_texts:
                return f"根据文档内容：{retrieved_texts[0][:200]}..."
            else:
                return "处理出错"
    
    def query(self, question: str) -> Dict[str, Any]:
        """查询接口"""
        try:
            print(f"🔍 查询: {question}")
            
            if not self.query_engine:
                return {
                    "question": question,
                    "answer": "系统未正确初始化",
                    "retrieved_texts": [],
                    "confidence": 0.0
                }
            
            # 检索
            response = self.query_engine.query(question)
            
            # 提取检索文本
            retrieved_texts = []
            if hasattr(response, 'source_nodes'):
                retrieved_texts = [node.text for node in response.source_nodes]
            
            # 生成答案
            answer = self.generate_simple_answer(question, retrieved_texts)
            
            return {
                "question": question,
                "answer": answer,
                "retrieved_texts": retrieved_texts,
                "confidence": 0.8
            }
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return {
                "question": question,
                "answer": f"查询错误: {str(e)}",
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
def test_simple_engine():
    """测试简化引擎"""
    print("="*60)
    print("🧪 测试简化版 RAG 引擎")
    print("="*60)
    
    try:
        # 模拟配置
        class SimpleConfig:
            LLM_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct"
            EMBEDDING_MODEL_PATH = "/mnt/workspace/.cache/modelscope/models/Jerry0/m3e-base"
            TOP_K = 3
        
        # 创建引擎
        engine = SimpleRAGEngine(SimpleConfig)
        
        # 初始化
        if not engine.initialize():
            print("❌ 初始化失败")
            return False
        
        # 测试文档
        test_docs = [
            "银行资本充足率要求：核心一级资本充足率5%，一级资本充足率6%，资本充足率8%。",
            "城商行内审部门负责人需在5个工作日内备案。",
            "个人理财产品需要风险评估和匹配。"
        ]
        
        # 构建索引
        documents = engine.create_documents(test_docs)
        if not engine.build_index(documents):
            print("❌ 索引构建失败")
            return False
        
        # 测试查询
        result = engine.query("银行资本充足率要求是多少？")
        print(f"\n✅ 测试结果:")
        print(f"问题: {result['question']}")
        print(f"答案: {result['answer']}")
        
        # 清理
        engine.cleanup()
        
        print("\n🎉 测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_engine() 