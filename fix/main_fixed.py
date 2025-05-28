#!/usr/bin/env python
"""
金融监管制度智能问答系统 - 修复版本
解决 transformers 库 NoneType 错误的主程序
"""

import json
import os
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any
from rag_engine_fixed import FixedRAGEngine
from config import Config

class FinancialQASystem:
    """金融问答系统 - 修复版本"""
    
    def __init__(self):
        """初始化系统"""
        self.rag_engine = None
        self.documents_loaded = False
        
    def load_documents(self, doc_dir: str) -> List[str]:
        """加载文档内容"""
        print(f"📚 加载文档目录: {doc_dir}")
        
        documents = []
        doc_path = Path(doc_dir)
        
        if not doc_path.exists():
            print(f"❌ 文档目录不存在: {doc_dir}")
            return documents
        
        # 支持的文件格式
        supported_formats = ['.txt', '.md', '.json']
        
        for file_path in doc_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in supported_formats:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            documents.append(content)
                            print(f"✅ 已加载: {file_path.name}")
                except Exception as e:
                    print(f"⚠️  跳过文件 {file_path.name}: {e}")
        
        print(f"📊 总共加载了 {len(documents)} 个文档")
        return documents
    
    def initialize_system(self):
        """初始化系统"""
        print("="*60)
        print("🚀 初始化金融监管制度智能问答系统")
        print("="*60)
        
        try:
            # 1. 创建RAG引擎
            print("步骤1: 创建RAG引擎...")
            self.rag_engine = FixedRAGEngine(Config)
            
            # 2. 初始化RAG引擎
            print("步骤2: 初始化RAG引擎...")
            if not self.rag_engine.initialize():
                print("❌ RAG引擎初始化失败")
                return False
            
            # 3. 加载文档
            print("步骤3: 加载文档...")
            documents_text = self.load_documents(Config.DOCUMENTS_DIR)
            
            if not documents_text:
                print("⚠️  未找到文档，使用默认测试文档")
                documents_text = [
                    "银行资本充足率监管要求：核心一级资本充足率不得低于5%，一级资本充足率不得低于6%，资本充足率不得低于8%。系统重要性银行在此基础上还需要额外计提资本缓冲。",
                    "个人理财产品销售需要进行风险评估，确保产品风险等级与客户风险承受能力相匹配。销售人员应当具备相应的专业知识和销售资格。",
                    "城商行内审部门负责人任职后需在5个工作日内向监管部门备案。内审部门应当独立设置，直接向董事会或其授权的审计委员会报告。",
                    "金融机构开展新业务需要事先向监管部门报告或审批。涉及系统重要性的业务变更需要提前30个工作日报告。",
                    "反洗钱工作要求金融机构建立健全反洗钱内控制度，对客户身份进行识别和核实，保存客户身份资料和交易记录至少5年。"
                ]
            
            # 4. 构建向量索引
            print("步骤4: 构建向量索引...")
            documents = self.rag_engine.create_documents(documents_text)
            if not self.rag_engine.build_index(documents):
                print("❌ 向量索引构建失败")
                return False
            
            self.documents_loaded = True
            print("✅ 系统初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            traceback.print_exc()
            return False
    
    def load_test_data(self, test_file: str) -> List[Dict]:
        """加载测试数据"""
        print(f"📝 加载测试数据: {test_file}")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ 加载了 {len(data)} 个测试题目")
            return data
        except Exception as e:
            print(f"❌ 加载测试数据失败: {e}")
            return []
    
    def process_question(self, question_data: Dict) -> Dict:
        """处理单个问题"""
        question_id = question_data.get('id', 'unknown')
        category = question_data.get('category', '未知')
        question = question_data.get('question', '')
        content = question_data.get('content', '')
        
        print(f"\n🔍 处理题目 {question_id} ({category})")
        print(f"问题: {question}")
        
        try:
            # 使用RAG引擎查询
            result = self.rag_engine.query(question)
            
            # 根据题目类型处理答案
            if category == "选择题" and content:
                # 选择题需要从选项中选择
                processed_answer = self.process_multiple_choice(
                    question, content, result['answer'], result['retrieved_texts']
                )
            else:
                # 问答题直接使用生成的答案
                processed_answer = result['answer']
            
            return {
                "id": question_id,
                "category": category,
                "question": question,
                "content": content,
                "answer": processed_answer,
                "retrieved_texts": result['retrieved_texts'],
                "confidence": result['confidence']
            }
            
        except Exception as e:
            print(f"❌ 处理题目 {question_id} 失败: {e}")
            return {
                "id": question_id,
                "category": category,
                "question": question,
                "content": content,
                "answer": f"处理失败: {str(e)}",
                "retrieved_texts": [],
                "confidence": 0.0
            }
    
    def process_multiple_choice(self, question: str, content: str, 
                              generated_answer: str, retrieved_texts: List[str]) -> str:
        """处理选择题"""
        # 简单的选择题处理逻辑
        options = content.split('\n')
        
        # 在生成的答案中查找选项
        for option in options:
            if option.strip():
                option_letter = option.split('.')[0].strip()
                option_text = option.split('.', 1)[1].strip() if '.' in option else option
                
                # 检查答案中是否包含该选项的关键信息
                if any(keyword in generated_answer for keyword in option_text.split()[:3]):
                    return f"{option_letter}. {option_text}"
        
        # 如果无法匹配，返回第一个选项（保守策略）
        first_option = options[0].strip() if options else "A"
        return f"{first_option} (基于文档内容推测)"
    
    def run_batch_test(self, test_file: str, output_file: str = None, batch_size: int = 5):
        """批量测试"""
        print("="*60)
        print("🧪 开始批量测试")
        print("="*60)
        
        if not self.documents_loaded:
            print("❌ 系统未正确初始化")
            return
        
        # 加载测试数据
        test_data = self.load_test_data(test_file)
        if not test_data:
            return
        
        results = []
        total_questions = len(test_data)
        
        # 分批处理
        for i in range(0, total_questions, batch_size):
            batch = test_data[i:i+batch_size]
            print(f"\n📦 处理批次 {i//batch_size + 1}/{(total_questions-1)//batch_size + 1}")
            
            for question_data in batch:
                result = self.process_question(question_data)
                results.append(result)
                
                # 显示处理结果
                print(f"✅ 题目 {result['id']}: {result['answer'][:100]}...")
            
            # 批次间清理GPU内存
            if hasattr(self.rag_engine, 'llm') and self.rag_engine.llm:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            print(f"📊 批次完成，已处理 {min(i+batch_size, total_questions)}/{total_questions} 个题目")
        
        # 保存结果
        if output_file:
            self.save_results(results, output_file)
        
        # 统计结果
        self.print_statistics(results)
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """保存结果"""
        print(f"\n💾 保存结果到: {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("✅ 结果保存成功")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
    
    def print_statistics(self, results: List[Dict]):
        """打印统计信息"""
        print("\n" + "="*60)
        print("📊 测试统计")
        print("="*60)
        
        total = len(results)
        choice_questions = len([r for r in results if r['category'] == '选择题'])
        qa_questions = len([r for r in results if r['category'] == '问答题'])
        
        avg_confidence = sum(r['confidence'] for r in results) / total if total > 0 else 0
        
        print(f"总题目数: {total}")
        print(f"选择题: {choice_questions}")
        print(f"问答题: {qa_questions}")
        print(f"平均置信度: {avg_confidence:.2f}")
        
        # 示例结果
        print("\n📝 示例结果:")
        for i, result in enumerate(results[:3]):
            print(f"\n{i+1}. 题目ID: {result['id']}")
            print(f"   类型: {result['category']}")
            print(f"   问题: {result['question']}")
            print(f"   答案: {result['answer']}")
            print(f"   置信度: {result['confidence']}")
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理系统资源...")
        if self.rag_engine:
            self.rag_engine.cleanup()
        print("✅ 资源清理完成")

def main():
    """主函数"""
    print("="*60)
    print("🏦 金融监管制度智能问答系统 - 修复版本")
    print("="*60)
    
    # 创建系统实例
    qa_system = FinancialQASystem()
    
    try:
        # 1. 初始化系统
        if not qa_system.initialize_system():
            print("❌ 系统初始化失败，退出程序")
            return
        
        # 2. 运行批量测试
        test_file = "数据集A/testA.json"
        output_file = "results_fixed.json"
        
        if Path(test_file).exists():
            qa_system.run_batch_test(test_file, output_file, batch_size=3)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")
            print("进行简单测试...")
            
            # 简单测试
            test_questions = [
                "银行资本充足率的最低监管要求是多少？",
                "城商行内审部门负责人任职后需要多久备案？",
                "个人理财产品销售需要满足哪些要求？"
            ]
            
            for question in test_questions:
                result = qa_system.rag_engine.query(question)
                print(f"\n问题: {question}")
                print(f"答案: {result['answer']}")
                print(f"置信度: {result['confidence']}")
        
        print("\n🎉 程序执行完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        traceback.print_exc()
    finally:
        # 清理资源
        qa_system.cleanup()

if __name__ == "__main__":
    main() 