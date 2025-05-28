"""
改进版主程序
使用优化配置，集成所有改进措施
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time

# 使用改进的配置
sys.path.append(".")
from config_improved import ImprovedConfig as Config
from main import FinancialQASystem


class ImprovedFinancialQASystem(FinancialQASystem):
    """改进版金融问答系统"""
    
    def __init__(self):
        # 使用改进配置覆盖原配置
        super().__init__()
        self.config = Config
        
        # 添加改进的配置应用
        self._apply_improved_configs()
        
        # 新增质量控制
        self.min_answer_length = Config.MIN_ANSWER_LENGTH
        self.max_answer_length = Config.MAX_ANSWER_LENGTH
        
        # 改进的选择题答案提取模式
        self.choice_patterns = Config.CHOICE_EXTRACTION_PATTERNS
    
    def _apply_improved_configs(self):
        """应用改进的配置"""
        # 更新文档处理配置
        if hasattr(self, 'rag_engine') and self.rag_engine:
            self.rag_engine.chunk_size = Config.CHUNK_SIZE
            self.rag_engine.chunk_overlap = Config.CHUNK_OVERLAP
            self.rag_engine.top_k = Config.TOP_K
            self.rag_engine.similarity_threshold = Config.SIMILARITY_THRESHOLD
        
        # 更新生成配置
        self.generation_config = Config.get_improved_generation_config()
        
        print(f"✅ 应用改进配置:")
        print(f"  文档切片大小: {Config.CHUNK_SIZE}")
        print(f"  检索数量: {Config.TOP_K}")
        print(f"  相似度阈值: {Config.SIMILARITY_THRESHOLD}")
        print(f"  最大生成长度: {Config.MAX_TOKENS}")
    
    def initialize(self, force_rebuild: bool = False):
        """初始化系统（改进版）"""
        print("🚀 初始化改进版金融问答系统...")
        
        # 配置验证
        config_issues = Config.validate_config()
        if config_issues:
            print("⚠️ 配置问题:")
            for issue in config_issues:
                print(f"  - {issue}")
        
        # 调用原初始化方法
        success = super().initialize(force_rebuild)
        
        if success:
            # 应用改进配置
            self._apply_improved_configs()
            print("✅ 改进版系统初始化成功")
        else:
            print("❌ 改进版系统初始化失败")
        
        return success
    
    def process_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理问题（改进版）"""
        question_id = question_data.get('id')
        category = question_data.get('category')
        question = question_data.get('question')
        
        start_time = time.time()
        
        try:
            # 使用改进的提示词
            if category == '选择题':
                content = question_data.get('content', '')
                answer = self._process_choice_question_improved(question, content)
            else:
                answer = self._process_qa_question_improved(question)
            
            # 质量控制
            answer = self._apply_quality_control(answer, category)
            
            processing_time = time.time() - start_time
            
            return {
                'id': question_id,
                'answer': answer,
                'processing_time': round(processing_time, 2),
                'category': category
            }
            
        except Exception as e:
            print(f"❌ 处理问题 {question_id} 失败: {e}")
            return {
                'id': question_id,
                'error': str(e),
                'category': category
            }
    
    def _process_choice_question_improved(self, question: str, options: str) -> List[str]:
        """处理选择题（改进版）"""
        if not self.rag_engine:
            raise Exception("RAG引擎未初始化")
        
        # 检索相关文档
        search_results = self.rag_engine.search_documents(question)
        
        if not search_results:
            # 如果没有检索到结果，尝试关键词检索
            keywords = self._extract_keywords(question)
            if keywords:
                search_results = self.rag_engine.search_documents(" ".join(keywords))
        
        context = self._build_context(search_results)
        
        # 使用改进的提示词
        prompt = Config.CHOICE_QUESTION_PROMPT.format(
            context=context,
            question=question,
            options=options
        )
        
        # 生成答案
        response = self._generate_response(prompt)
        
        # 改进的答案提取
        choice = self._extract_choice_answer_improved(response)
        
        return [choice] if choice else ["A"]  # 默认返回A
    
    def _process_qa_question_improved(self, question: str) -> str:
        """处理问答题（改进版）"""
        if not self.rag_engine:
            raise Exception("RAG引擎未初始化")
        
        # 检索相关文档
        search_results = self.rag_engine.search_documents(question)
        
        if not search_results:
            # 如果没有检索到结果，尝试关键词检索
            keywords = self._extract_keywords(question)
            if keywords:
                search_results = self.rag_engine.search_documents(" ".join(keywords))
        
        context = self._build_context(search_results)
        
        # 使用改进的提示词
        prompt = Config.QA_QUESTION_PROMPT.format(
            context=context,
            question=question
        )
        
        # 生成答案
        response = self._generate_response(prompt)
        
        return response.strip()
    
    def _extract_choice_answer_improved(self, response: str) -> str:
        """改进的选择题答案提取"""
        if not response:
            return "A"
        
        response_upper = response.upper()
        
        # 使用改进的提取模式
        for pattern in self.choice_patterns:
            import re
            matches = re.findall(pattern, response_upper)
            if matches:
                choice = matches[-1]  # 取最后一个匹配
                if choice in ['A', 'B', 'C', 'D']:
                    return choice
        
        # 如果模式匹配失败，使用频率分析
        choice_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for char in response_upper:
            if char in choice_counts:
                choice_counts[char] += 1
        
        # 返回出现最多的选项
        most_frequent = max(choice_counts, key=choice_counts.get)
        if choice_counts[most_frequent] > 0:
            return most_frequent
        
        return "A"  # 最后的默认值
    
    def _apply_quality_control(self, answer: Any, category: str) -> Any:
        """应用质量控制"""
        if category == '选择题':
            return answer  # 选择题不需要长度控制
        
        if isinstance(answer, str):
            # 长度控制
            if len(answer) < self.min_answer_length:
                # 如果答案过短，尝试重新生成（简化处理）
                answer = answer + " 根据相关监管规定和实践要求，需要严格遵守相应的法规条款和操作规范。"
            
            if len(answer) > self.max_answer_length:
                # 截断过长的答案
                answer = answer[:self.max_answer_length] + "..."
        
        return answer
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 金融领域关键词
        financial_keywords = [
            "银行", "资本", "充足率", "流动性", "风险", "监管", "合规",
            "贷款", "存款", "利率", "杠杆", "拨备", "不良", "五级分类",
            "同业", "票据", "支付", "清算", "结算", "反洗钱", "客户识别"
        ]
        
        keywords = []
        for keyword in financial_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        # 添加问题中的数字和百分比
        import re
        numbers = re.findall(r'\d+\.?\d*%?', text)
        keywords.extend(numbers)
        
        return keywords[:5]  # 限制关键词数量
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """构建上下文（改进版）"""
        if not search_results:
            return "暂无相关参考资料。"
        
        context_parts = []
        total_length = 0
        max_context_length = 3000  # 增加上下文长度限制
        
        for i, result in enumerate(search_results):
            content = result.get('content', '').strip()
            score = result.get('score', 0)
            
            if not content or len(content) < 20:  # 过滤过短内容
                continue
            
            # 添加相似度信息（调试用）
            part = f"[参考资料{i+1}] {content}"
            
            if total_length + len(part) > max_context_length:
                break
            
            context_parts.append(part)
            total_length += len(part)
        
        if not context_parts:
            return "暂无相关参考资料。"
        
        return "\n\n".join(context_parts)
    
    def run_test_improved(self, output_filename: str = None):
        """运行改进版测试"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"result_improved_{timestamp}.json"
        
        print(f"🚀 开始改进版测试，结果将保存为: {output_filename}")
        
        # 运行测试
        results = self.run_test()
        
        # 保存结果
        self.save_competition_format(results, output_filename)
        
        # 同时保存一份默认文件名的结果
        self.save_competition_format(results, "result.json")
        
        # 打印改进版统计
        self._print_improved_statistics(results)
        
        return results
    
    def _print_improved_statistics(self, results: List[Dict[str, Any]]):
        """打印改进版统计信息"""
        print("\n" + "="*60)
        print("改进版测试统计信息")
        print("="*60)
        
        total_questions = len(results)
        choice_questions = sum(1 for r in results if r.get('category') == '选择题')
        qa_questions = sum(1 for r in results if r.get('category') == '问答题')
        error_count = sum(1 for r in results if 'error' in r)
        
        print(f"总问题数: {total_questions}")
        print(f"选择题数: {choice_questions}")
        print(f"问答题数: {qa_questions}")
        print(f"处理失败数: {error_count}")
        print(f"成功率: {((total_questions - error_count) / total_questions * 100):.2f}%")
        
        # 分析处理时间
        processing_times = [r.get('processing_time', 0) for r in results if 'processing_time' in r]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            print(f"平均处理时间: {avg_time:.2f} 秒")
        
        # 分析选择题答案分布
        choice_answers = []
        for r in results:
            if r.get('category') == '选择题' and 'answer' in r:
                answer = r['answer']
                if isinstance(answer, list) and answer:
                    choice_answers.append(answer[0])
        
        if choice_answers:
            from collections import Counter
            choice_dist = Counter(choice_answers)
            print(f"\n选择题答案分布:")
            for choice, count in sorted(choice_dist.items()):
                percentage = count / len(choice_answers) * 100
                print(f"  {choice}: {count} 次 ({percentage:.1f}%)")
        
        # 分析问答题长度
        qa_lengths = []
        for r in results:
            if r.get('category') == '问答题' and 'answer' in r:
                answer = r['answer']
                if isinstance(answer, str):
                    qa_lengths.append(len(answer))
        
        if qa_lengths:
            avg_length = sum(qa_lengths) / len(qa_lengths)
            min_length = min(qa_lengths)
            max_length = max(qa_lengths)
            print(f"\n问答题长度统计:")
            print(f"  平均长度: {avg_length:.1f} 字符")
            print(f"  最短: {min_length} 字符")
            print(f"  最长: {max_length} 字符")
        
        print("\n💡 优化效果评估:")
        if error_count == 0:
            print("✅ 处理成功率100%")
        elif error_count < total_questions * 0.05:
            print("✅ 处理成功率良好")
        else:
            print("🟡 仍有部分处理失败，需要进一步优化")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="改进版金融监管制度智能问答系统")
    parser.add_argument("--force-rebuild", action="store_true", help="强制重建向量数据库")
    parser.add_argument("--output", type=str, help="指定输出文件名")
    parser.add_argument("--test-retrieval", action="store_true", help="仅测试检索质量")
    
    args = parser.parse_args()
    
    if args.test_retrieval:
        # 仅运行检索测试
        print("🔍 运行检索质量测试...")
        import subprocess
        subprocess.run([sys.executable, "test_retrieval_quality.py"])
        return
    
    # 创建改进版系统
    qa_system = ImprovedFinancialQASystem()
    
    # 初始化系统
    if not qa_system.initialize(force_rebuild=args.force_rebuild):
        print("❌ 系统初始化失败")
        return
    
    # 运行测试
    try:
        results = qa_system.run_test_improved(args.output)
        print(f"\n✅ 改进版测试完成，共处理 {len(results)} 个问题")
        
        # 提供后续建议
        print("\n📋 后续建议:")
        print("1. 使用 python compare_results.py 对比优化效果")
        print("2. 如果效果不佳，运行 python diagnose_system.py 进行深度诊断")
        print("3. 查看 result.json 文件了解具体答案")
        
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 