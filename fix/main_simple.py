#!/usr/bin/env python
"""
金融监管制度智能问答系统 - 简化版本
使用简化的RAG引擎，避免transformers并行处理问题
"""

import json
import traceback
from pathlib import Path
from typing import List, Dict
from simple_rag_engine import SimpleRAGEngine
from config import Config

class SimpleFinancialQA:
    """简化版金融问答系统"""
    
    def __init__(self):
        self.rag_engine = None
        self.initialized = False
    
    def initialize(self):
        """初始化系统"""
        print("="*60)
        print("🚀 初始化简化版金融问答系统")
        print("="*60)
        
        try:
            # 创建简化引擎
            self.rag_engine = SimpleRAGEngine(Config)
            
            # 初始化引擎
            if not self.rag_engine.initialize():
                print("❌ RAG引擎初始化失败")
                return False
            
            # 加载测试文档
            test_documents = [
                "银行资本充足率监管要求：核心一级资本充足率不得低于5%，一级资本充足率不得低于6%，资本充足率不得低于8%。系统重要性银行还需额外计提资本缓冲。",
                "个人理财产品销售必须进行风险评估，确保产品风险等级与客户风险承受能力相匹配。销售人员应具备相应资格。",
                "城商行内审部门负责人任职后需在5个工作日内向监管部门备案。内审部门应独立设置。",
                "金融机构开展新业务需要事先向监管部门报告或审批。系统重要性业务变更需提前30个工作日报告。",
                "反洗钱工作要求：建立健全内控制度，客户身份识别核实，保存资料和记录至少5年。",
                "商业银行风险管理要求建立全面风险管理体系，设立首席风险官，实施风险限额管理。",
                "保险公司偿付能力监管：核心偿付能力充足率不低于50%，综合偿付能力充足率不低于100%。",
                "证券公司净资本监管：净资本不得低于规定标准，净资本与各项风险资本准备之比不得低于100%。"
            ]
            
            # 构建索引
            documents = self.rag_engine.create_documents(test_documents)
            if not self.rag_engine.build_index(documents):
                print("❌ 索引构建失败")
                return False
            
            self.initialized = True
            print("✅ 系统初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            traceback.print_exc()
            return False
    
    def process_questions(self, questions: List[str]):
        """处理问题列表"""
        if not self.initialized:
            print("❌ 系统未初始化")
            return []
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n📝 处理问题 {i}/{len(questions)}")
            result = self.rag_engine.query(question)
            results.append(result)
            print(f"✅ 完成: {result['answer'][:100]}...")
        
        return results
    
    def run_demo(self):
        """运行演示"""
        print("\n" + "="*60)
        print("🧪 运行演示测试")
        print("="*60)
        
        demo_questions = [
            "银行资本充足率的最低监管要求是什么？",
            "城商行内审部门负责人任职后多长时间内需要备案？",
            "个人理财产品销售需要满足哪些要求？",
            "反洗钱工作有哪些基本要求？",
            "保险公司的偿付能力监管标准是什么？"
        ]
        
        results = self.process_questions(demo_questions)
        
        # 显示结果
        print("\n" + "="*60)
        print("📊 演示结果")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 问题: {result['question']}")
            print(f"   答案: {result['answer']}")
            print(f"   置信度: {result['confidence']}")
        
        return results
    
    def load_and_process_testfile(self, test_file: str):
        """加载并处理测试文件"""
        print(f"\n📝 处理测试文件: {test_file}")
        
        try:
            if not Path(test_file).exists():
                print(f"❌ 测试文件不存在: {test_file}")
                return []
            
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            print(f"✅ 加载了 {len(test_data)} 个测试题目")
            
            results = []
            for item in test_data[:10]:  # 只处理前10个，避免过长
                question = item.get('question', '')
                if question:
                    result = self.rag_engine.query(question)
                    result.update({
                        'id': item.get('id'),
                        'category': item.get('category'),
                        'original_content': item.get('content')
                    })
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ 处理测试文件失败: {e}")
            return []
    
    def save_results(self, results: List[Dict], output_file: str):
        """保存结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.rag_engine:
            self.rag_engine.cleanup()

def main():
    """主函数"""
    print("🏦 金融监管制度智能问答系统 - 简化版本")
    print("="*60)
    
    # 创建系统
    qa_system = SimpleFinancialQA()
    
    try:
        # 初始化
        if not qa_system.initialize():
            print("❌ 系统初始化失败，退出")
            return
        
        # 运行演示
        demo_results = qa_system.run_demo()
        
        # 尝试处理测试文件
        test_file = "数据集A/testA.json"
        if Path(test_file).exists():
            print(f"\n📁 发现测试文件，处理前10个题目...")
            test_results = qa_system.load_and_process_testfile(test_file)
            
            if test_results:
                # 保存测试结果
                qa_system.save_results(test_results, "simple_test_results.json")
                
                print(f"\n📊 测试文件处理完成，共处理 {len(test_results)} 个题目")
                print("前3个结果预览:")
                for i, result in enumerate(test_results[:3], 1):
                    print(f"\n{i}. ID: {result.get('id')} | 类型: {result.get('category')}")
                    print(f"   问题: {result['question']}")
                    print(f"   答案: {result['answer'][:150]}...")
        else:
            print(f"\n⚠️  未找到测试文件: {test_file}")
        
        print("\n🎉 程序执行完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        traceback.print_exc()
    finally:
        qa_system.cleanup()

if __name__ == "__main__":
    main() 