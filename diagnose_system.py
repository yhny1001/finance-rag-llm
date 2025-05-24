"""
系统性能诊断工具
深入分析RAG系统的各个环节，找出分数低的根本原因
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import re

# 添加当前目录到路径
sys.path.append(".")

try:
    from main import FinancialQASystem
    from config import Config
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class SystemDiagnostics:
    """系统诊断器"""
    
    def __init__(self):
        try:
            self.qa_system = FinancialQASystem()
            self.config = Config
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.qa_system = None
            self.config = None
    
    def run_full_diagnosis(self):
        """运行完整诊断"""
        print("🔍 开始系统诊断...")
        print("=" * 80)
        
        # 1. 检查基础环境
        self.check_environment()
        
        # 2. 检查数据质量
        self.check_data_quality()
        
        # 3. 检查向量数据库
        self.check_vector_database()
        
        # 4. 检查检索质量
        self.check_retrieval_quality()
        
        # 5. 分析实际答案
        self.analyze_real_answers()
        
        # 6. 给出建议
        self.provide_recommendations()
    
    def check_environment(self):
        """检查环境配置"""
        print("\n🔧 环境检查")
        print("-" * 40)
        
        if not self.config:
            print("❌ 配置加载失败")
            return
        
        # 检查文件存在性
        docs_path = Path(self.config.DOCUMENTS_DIR)
        test_path = Path(self.config.TEST_DATA_PATH)
        
        print(f"文档目录: {docs_path.exists()} - {docs_path}")
        print(f"测试数据: {test_path.exists()} - {test_path}")
        
        if docs_path.exists():
            docx_files = list(docs_path.glob("*.docx"))
            print(f"Word文档数量: {len(docx_files)}")
            
            # 检查文档大小
            if docx_files:
                total_size = sum(f.stat().st_size for f in docx_files)
                print(f"文档总大小: {total_size / 1024 / 1024:.2f} MB")
                
                print("文档列表:")
                for doc in docx_files[:5]:  # 显示前5个
                    size_mb = doc.stat().st_size / 1024 / 1024
                    print(f"  - {doc.name} ({size_mb:.2f} MB)")
                
                if len(docx_files) > 5:
                    print(f"  ... 还有 {len(docx_files) - 5} 个文档")
        
        # 检查向量数据库
        vector_path = Path(self.config.VECTOR_DB_DIR)
        print(f"向量数据库目录: {vector_path.exists()} - {vector_path}")
        
        if vector_path.exists():
            vector_files = list(vector_path.glob("*"))
            print(f"向量数据库文件数: {len(vector_files)}")
    
    def check_data_quality(self):
        """检查数据质量"""
        print("\n📊 数据质量检查")
        print("-" * 40)
        
        if not self.qa_system:
            print("❌ QA系统未初始化")
            return
        
        # 加载测试数据
        questions = self.qa_system.load_test_data()
        if not questions:
            print("❌ 无法加载测试数据")
            return
        
        print(f"✅ 成功加载 {len(questions)} 个问题")
        
        # 分析问题类型
        choice_count = sum(1 for q in questions if q.get('category') == '选择题')
        qa_count = sum(1 for q in questions if q.get('category') == '问答题')
        
        print(f"选择题: {choice_count} 道 ({choice_count/len(questions)*100:.1f}%)")
        print(f"问答题: {qa_count} 道 ({qa_count/len(questions)*100:.1f}%)")
        
        # 分析问题长度
        question_lengths = [len(q.get('question', '')) for q in questions]
        avg_length = sum(question_lengths) / len(question_lengths)
        print(f"平均问题长度: {avg_length:.1f} 字符")
        
        # 分析选择题内容
        print("\n选择题样例分析:")
        choice_questions = [q for q in questions if q.get('category') == '选择题']
        
        if choice_questions:
            sample = choice_questions[0]
            print(f"问题: {sample.get('question', '')[:100]}...")
            content = sample.get('content', '')
            if content:
                print(f"选项: {content[:200]}...")
                
                # 分析选项格式
                options = re.findall(r'[ABCD][、.]', content)
                print(f"检测到选项: {options}")
            else:
                print("⚠️ 该选择题没有选项内容")
        
        # 分析问答题内容
        print("\n问答题样例分析:")
        qa_questions = [q for q in questions if q.get('category') == '问答题']
        
        if qa_questions:
            sample = qa_questions[0]
            print(f"问题: {sample.get('question', '')[:150]}...")
    
    def check_vector_database(self):
        """检查向量数据库质量"""
        print("\n🗃️ 向量数据库检查")
        print("-" * 40)
        
        if not self.qa_system:
            print("❌ QA系统未初始化")
            return
        
        try:
            # 初始化系统
            if not self.qa_system.initialize():
                print("❌ 系统初始化失败")
                return
            
            # 获取向量数据库统计
            if self.qa_system.rag_engine:
                stats = self.qa_system.rag_engine.get_vector_db_stats()
                
                print("向量数据库统计:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                
                # 检查文档块数量是否合理
                doc_count = stats.get('文档数量', 0)
                chunk_count = stats.get('文档块数量', 0)
                
                if chunk_count == 0:
                    print("❌ 向量数据库为空！")
                elif chunk_count < 50:
                    print("⚠️ 文档块数量过少，可能影响检索质量")
                elif chunk_count > 10000:
                    print("⚠️ 文档块数量过多，可能影响检索效率")
                else:
                    print("✅ 文档块数量合理")
                
                if doc_count > 0 and chunk_count > 0:
                    avg_chunks = chunk_count / doc_count
                    print(f"平均每文档切片数: {avg_chunks:.1f}")
                    
                    if avg_chunks < 5:
                        print("⚠️ 平均切片数过少，文档可能太小或切片太大")
                    elif avg_chunks > 100:
                        print("⚠️ 平均切片数过多，切片可能太小")
                
        except Exception as e:
            print(f"❌ 向量数据库检查失败: {e}")
    
    def check_retrieval_quality(self):
        """检查检索质量"""
        print("\n🔍 检索质量检查")
        print("-" * 40)
        
        # 测试几个典型问题的检索效果
        test_queries = [
            "商业银行的资本充足率要求是什么？",
            "流动性覆盖率的最低标准是多少？",
            "银行的核心一级资本充足率不低于多少？",
            "什么是杠杆率？"
        ]
        
        if not self.qa_system or not self.qa_system.rag_engine:
            print("❌ RAG引擎未初始化")
            return
        
        try:
            for i, query in enumerate(test_queries[:2], 1):  # 只测试前2个
                print(f"\n测试查询 {i}: {query}")
                
                # 执行检索
                results = self.qa_system.rag_engine.search_documents(query)
                
                if results:
                    print(f"✅ 检索到 {len(results)} 个结果")
                    
                    # 分析第一个结果
                    top_result = results[0]
                    content = top_result.get('content', '')
                    score = top_result.get('score', 0)
                    
                    print(f"最佳匹配得分: {score:.3f}")
                    print(f"内容预览: {content[:200]}...")
                    
                    # 检查是否包含相关关键词
                    query_keywords = ["资本充足率", "流动性", "核心一级", "杠杆率"]
                    found_keywords = [kw for kw in query_keywords if kw in content]
                    
                    if found_keywords:
                        print(f"包含关键词: {found_keywords}")
                    else:
                        print("⚠️ 检索内容可能不相关")
                        
                    # 检查相似度分布
                    scores = [r.get('score', 0) for r in results]
                    min_score = min(scores)
                    max_score = max(scores)
                    
                    print(f"相似度范围: {min_score:.3f} - {max_score:.3f}")
                    
                    if max_score < 0.3:
                        print("⚠️ 最高相似度过低，检索质量可能有问题")
                else:
                    print("❌ 没有检索到任何结果")
                    
        except Exception as e:
            print(f"❌ 检索测试失败: {e}")
    
    def analyze_real_answers(self):
        """分析实际生成的答案文件"""
        print("\n📋 实际答案分析")
        print("-" * 40)
        
        result_files = list(Path(".").glob("result*.json"))
        
        if not result_files:
            print("❌ 没有找到result.json文件")
            return
        
        # 分析最新的result文件
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        print(f"分析文件: {latest_file}")
        
        try:
            results = []
            with open(latest_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        results.append(json.loads(line))
            
            print(f"✅ 加载了 {len(results)} 个结果")
            
            # 分析答案分布
            choice_answers = []
            qa_lengths = []
            error_count = 0
            
            for result in results:
                if 'error' in result:
                    error_count += 1
                    continue
                    
                answer = result.get('answer', '')
                
                if isinstance(answer, list):
                    # 选择题
                    if answer:
                        choice_answers.append(answer[0])
                    else:
                        choice_answers.append('EMPTY')
                elif isinstance(answer, str):
                    # 问答题
                    qa_lengths.append(len(answer))
            
            print(f"处理失败数: {error_count}")
            print(f"成功率: {((len(results) - error_count) / len(results) * 100):.2f}%")
            
            # 分析选择题答案分布
            if choice_answers:
                print(f"\n选择题答案分布 (共{len(choice_answers)}题):")
                choice_dist = Counter(choice_answers)
                
                for choice, count in sorted(choice_dist.items()):
                    percentage = count / len(choice_answers) * 100
                    print(f"  {choice}: {count} 次 ({percentage:.1f}%)")
                
                # 检查是否过度集中
                max_choice = max(choice_dist.values())
                if max_choice / len(choice_answers) > 0.8:
                    print("🔴 答案过度集中在某个选项，可能有严重问题")
                elif max_choice / len(choice_answers) > 0.6:
                    print("🟡 答案分布不均匀，需要检查")
                else:
                    print("✅ 选择题答案分布相对正常")
            
            # 分析问答题长度分布
            if qa_lengths:
                avg_length = sum(qa_lengths) / len(qa_lengths)
                min_length = min(qa_lengths)
                max_length = max(qa_lengths)
                
                print(f"\n问答题长度统计 (共{len(qa_lengths)}题):")
                print(f"  平均长度: {avg_length:.1f} 字符")
                print(f"  最短: {min_length} 字符")
                print(f"  最长: {max_length} 字符")
                
                # 检查异常
                short_count = sum(1 for length in qa_lengths if length < 50)
                long_count = sum(1 for length in qa_lengths if length > 500)
                
                if short_count > 0:
                    print(f"⚠️ {short_count} 个答案过短 (<50字符)")
                    
                if long_count > 0:
                    print(f"⚠️ {long_count} 个答案过长 (>500字符)")
                
                if avg_length < 100:
                    print("🔴 问答题平均长度过短，可能信息不足")
                else:
                    print("✅ 问答题长度相对正常")
            
            # 显示几个样例答案
            print(f"\n答案样例:")
            for i, result in enumerate(results[:3], 1):
                qid = result.get('id', f'unknown_{i}')
                answer = result.get('answer', '')
                
                print(f"问题 {qid}:")
                if isinstance(answer, list):
                    print(f"  选择题答案: {answer}")
                else:
                    preview = answer[:100] + "..." if len(answer) > 100 else answer
                    print(f"  问答题答案: {preview}")
                
        except Exception as e:
            print(f"❌ 分析result文件失败: {e}")
    
    def provide_recommendations(self):
        """提供改进建议"""
        print("\n💡 改进建议")
        print("=" * 40)
        
        print("基于诊断结果，建议按以下优先级解决问题:")
        
        print("\n🔴 高优先级 - 立即执行:")
        print("1. 清理并重建向量数据库")
        print("   python clear_vector_db.py clear")
        print("   python main.py --force-rebuild")
        
        print("\n2. 运行检索质量测试")
        print("   python test_retrieval_quality.py")
        
        print("\n3. 使用改进配置重新运行")
        print("   python main_improved.py")
        
        print("\n🟡 中优先级:")
        print("4. 检查文档内容提取质量")
        print("5. 优化提示词设计")
        print("6. 调整模型参数")
        
        print("\n🟢 低优先级:")
        print("7. 实施多轮检索策略")
        print("8. 添加领域特定后处理")


def main():
    """主函数"""
    diagnostics = SystemDiagnostics()
    diagnostics.run_full_diagnosis()


if __name__ == "__main__":
    main() 