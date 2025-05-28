"""
检索质量测试脚本
专门测试RAG系统的检索效果，帮助诊断检索质量问题
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加当前目录到路径
sys.path.append(".")

try:
    from main import FinancialQASystem
    from config import Config
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class RetrievalQualityTester:
    """检索质量测试器"""
    
    def __init__(self):
        try:
            self.qa_system = FinancialQASystem()
            print("正在初始化系统...")
            if not self.qa_system.initialize():
                print("❌ 系统初始化失败")
                self.qa_system = None
            else:
                print("✅ 系统初始化成功")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.qa_system = None
    
    def test_key_financial_queries(self):
        """测试关键金融问题的检索效果"""
        print("\n🔍 测试关键金融问题检索效果")
        print("=" * 60)
        
        # 关键金融问题测试用例
        test_cases = [
            {
                "query": "商业银行核心一级资本充足率要求",
                "expected_keywords": ["核心一级资本充足率", "6%", "不低于", "商业银行"],
                "category": "资本充足率"
            },
            {
                "query": "流动性覆盖率LCR最低要求",
                "expected_keywords": ["流动性覆盖率", "LCR", "100%", "不低于"],
                "category": "流动性管理"
            },
            {
                "query": "银行杠杆率监管要求",
                "expected_keywords": ["杠杆率", "4%", "不低于", "一级资本"],
                "category": "杠杆率管理"
            },
            {
                "query": "贷款五级分类标准",
                "expected_keywords": ["五级分类", "正常", "关注", "次级", "可疑", "损失"],
                "category": "贷款分类"
            },
            {
                "query": "银行间同业拆借利率",
                "expected_keywords": ["同业拆借", "利率", "银行间", "资金"],
                "category": "货币市场"
            }
        ]
        
        if not self.qa_system or not self.qa_system.rag_engine:
            print("❌ RAG引擎未初始化")
            return
        
        total_score = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 测试 {i}/{total_tests}: {test_case['category']} ---")
            print(f"查询: {test_case['query']}")
            
            try:
                # 执行检索
                results = self.qa_system.rag_engine.search_documents(test_case['query'])
                
                if not results:
                    print("❌ 没有检索到任何结果")
                    continue
                
                print(f"✅ 检索到 {len(results)} 个结果")
                
                # 分析最佳结果
                best_result = results[0]
                best_score = best_result.get('score', 0)
                best_content = best_result.get('content', '')
                
                print(f"最佳匹配得分: {best_score:.3f}")
                print(f"内容长度: {len(best_content)} 字符")
                
                # 检查期望关键词
                found_keywords = []
                for keyword in test_case['expected_keywords']:
                    if keyword in best_content:
                        found_keywords.append(keyword)
                
                keyword_score = len(found_keywords) / len(test_case['expected_keywords'])
                
                print(f"期望关键词: {test_case['expected_keywords']}")
                print(f"找到关键词: {found_keywords}")
                print(f"关键词覆盖率: {keyword_score:.2%}")
                
                # 计算综合得分
                similarity_score = min(best_score / 0.5, 1.0)  # 0.5为理想相似度
                combined_score = (similarity_score * 0.4 + keyword_score * 0.6)
                
                print(f"综合得分: {combined_score:.3f}")
                
                if combined_score > 0.7:
                    print("✅ 检索质量良好")
                elif combined_score > 0.4:
                    print("🟡 检索质量中等")
                else:
                    print("🔴 检索质量较差")
                
                total_score += combined_score
                
                # 显示内容预览
                print(f"内容预览: {best_content[:200]}...")
                
                # 显示所有结果的得分分布
                scores = [r.get('score', 0) for r in results]
                print(f"得分分布: 最高={max(scores):.3f}, 最低={min(scores):.3f}, 平均={sum(scores)/len(scores):.3f}")
                
            except Exception as e:
                print(f"❌ 检索测试失败: {e}")
        
        # 计算总体得分
        avg_score = total_score / total_tests
        print(f"\n📊 总体检索质量评估")
        print("=" * 30)
        print(f"平均得分: {avg_score:.3f}")
        
        if avg_score > 0.7:
            print("✅ 检索质量整体良好")
        elif avg_score > 0.5:
            print("🟡 检索质量中等，需要优化")
        elif avg_score > 0.3:
            print("🔴 检索质量较差，需要重点改进")
        else:
            print("💀 检索质量极差，系统可能存在严重问题")
    
    def test_specific_question_types(self):
        """测试特定类型问题的检索效果"""
        print("\n🎯 测试特定问题类型")
        print("=" * 60)
        
        # 选择题类型测试
        choice_queries = [
            "银行核心一级资本充足率不低于多少",
            "流动性覆盖率应达到多少",
            "银行杠杆率不得低于"
        ]
        
        # 问答题类型测试
        qa_queries = [
            "什么是银行资本充足率，包括哪些指标",
            "流动性风险管理的主要措施有哪些",
            "银行信贷风险的识别和控制方法"
        ]
        
        print("\n📋 选择题类型检索测试:")
        self._test_query_batch(choice_queries, "选择题")
        
        print("\n📝 问答题类型检索测试:")
        self._test_query_batch(qa_queries, "问答题")
    
    def _test_query_batch(self, queries: List[str], query_type: str):
        """批量测试查询"""
        if not self.qa_system or not self.qa_system.rag_engine:
            print("❌ RAG引擎未初始化")
            return
        
        for i, query in enumerate(queries, 1):
            print(f"\n{query_type} {i}: {query}")
            try:
                results = self.qa_system.rag_engine.search_documents(query)
                if results:
                    best_score = results[0].get('score', 0)
                    print(f"  检索结果: {len(results)} 个，最佳得分: {best_score:.3f}")
                    
                    # 分析内容质量
                    content = results[0].get('content', '')
                    has_numbers = any(char.isdigit() for char in content)
                    has_percentage = '%' in content
                    
                    print(f"  内容包含数字: {has_numbers}, 包含百分比: {has_percentage}")
                else:
                    print("  ❌ 没有检索结果")
            except Exception as e:
                print(f"  ❌ 检索失败: {e}")
    
    def analyze_vector_db_coverage(self):
        """分析向量数据库覆盖情况"""
        print("\n📚 向量数据库覆盖分析")
        print("=" * 60)
        
        if not self.qa_system or not self.qa_system.rag_engine:
            print("❌ RAG引擎未初始化")
            return
        
        try:
            # 获取向量数据库统计
            stats = self.qa_system.rag_engine.get_vector_db_stats()
            
            print("数据库基础信息:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # 测试不同主题的覆盖情况
            topics = [
                "资本充足率",
                "流动性管理", 
                "风险管理",
                "贷款管理",
                "票据业务",
                "反洗钱",
                "信息披露",
                "内部控制"
            ]
            
            print(f"\n主题覆盖测试:")
            covered_topics = 0
            
            for topic in topics:
                results = self.qa_system.rag_engine.search_documents(topic)
                if results and results[0].get('score', 0) > 0.3:
                    covered_topics += 1
                    print(f"  ✅ {topic}: 有相关内容 (得分: {results[0].get('score', 0):.3f})")
                else:
                    print(f"  ❌ {topic}: 缺乏相关内容")
            
            coverage_rate = covered_topics / len(topics)
            print(f"\n主题覆盖率: {coverage_rate:.2%}")
            
            if coverage_rate > 0.8:
                print("✅ 主题覆盖率良好")
            elif coverage_rate > 0.6:
                print("🟡 主题覆盖率中等")
            else:
                print("🔴 主题覆盖率不足，可能文档不完整")
                
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    def test_edge_cases(self):
        """测试边缘情况"""
        print("\n🧪 边缘情况测试")
        print("=" * 60)
        
        edge_cases = [
            ("空查询", ""),
            ("短查询", "银行"),
            ("长查询", "请详细说明商业银行在实施巴塞尔协议III框架下的资本充足率管理要求时，需要考虑的核心一级资本、一级资本和总资本的具体计算方法、最低要求标准以及缓冲资本的相关规定"),
            ("数字查询", "6% 8% 10.5%"),
            ("英文查询", "LCR NSFR CAR"),
            ("特殊字符", "资本充足率≥8%"),
        ]
        
        if not self.qa_system or not self.qa_system.rag_engine:
            print("❌ RAG引擎未初始化")
            return
        
        for case_name, query in edge_cases:
            print(f"\n{case_name}: '{query}'")
            try:
                results = self.qa_system.rag_engine.search_documents(query)
                if results:
                    print(f"  结果数: {len(results)}, 最佳得分: {results[0].get('score', 0):.3f}")
                else:
                    print("  无结果")
            except Exception as e:
                print(f"  错误: {e}")
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 开始检索质量综合测试")
        print("=" * 80)
        
        # 运行各项测试
        self.test_key_financial_queries()
        self.test_specific_question_types()
        self.analyze_vector_db_coverage()
        self.test_edge_cases()
        
        print("\n💡 测试完成建议")
        print("=" * 40)
        print("1. 如果检索得分普遍低于0.3，考虑重建向量数据库")
        print("2. 如果关键词覆盖率低，检查文档内容提取质量")
        print("3. 如果主题覆盖率低，确认文档是否完整")
        print("4. 如果边缘情况处理不当，优化查询预处理")


def main():
    """主函数"""
    tester = RetrievalQualityTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main() 