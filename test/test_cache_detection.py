"""
测试脚本：检测系统中可能存在的缓存问题或伪造答案
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

# 添加当前目录到路径
sys.path.append(".")

# 导入系统组件
from main import FinancialQASystem
from rag_engine import RAGEngine

class CacheDetector:
    """检测缓存或伪造答案的工具类"""
    
    def __init__(self):
        self.qa_system = FinancialQASystem()
        self.qa_system.initialize()
    
    def test_repeated_questions(self):
        """使用相同问题多次查询，检测是否有缓存机制"""
        print("="*60)
        print("测试1: 重复问题检测")
        print("="*60)
        
        # 构建测试用例 - 使用相同问题多次查询
        test_questions = [
            {
                "id": f"dup_test_{i}",
                "category": "选择题",
                "question": "普惠金融事业部筹备工作领导小组的组长通常由谁担任？",
                "content": "   A. 分行行长  \n   B. 董事会主席  \n   C. 总行高级管理人员  \n   D. 审计部门负责人  "
            } for i in range(3)  # 相同问题重复3次
        ]
        
        # 执行测试
        print("执行测试：重复提问相同问题3次，记录时间和答案...")
        results = []
        start_times = []
        end_times = []
        
        for i, question in enumerate(test_questions):
            print(f"\n处理问题 #{i+1} (ID: {question['id']})...")
            start_time = time.time()
            start_times.append(start_time)
            result = self.qa_system.process_question(question)
            end_time = time.time()
            end_times.append(end_time)
            results.append(result)
            
            print(f"  耗时: {end_time - start_time:.2f}秒")
            print(f"  答案长度: {len(result.get('raw_llm_output', ''))}")
        
        # 分析结果
        print("\n分析结果:")
        self._analyze_repeated_results(results, start_times, end_times)
        
        return results
    
    def test_similar_questions(self):
        """使用相似但不完全相同的问题查询，检测是否有缓存机制"""
        print("\n" + "="*60)
        print("测试2: 相似问题检测")
        print("="*60)
        
        # 构建测试用例 - 使用相似但不完全相同的问题
        test_questions = [
            {
                "id": "sim_test_1",
                "category": "选择题",
                "question": "普惠金融事业部筹备工作领导小组的组长通常由谁担任？",
                "content": "   A. 分行行长  \n   B. 董事会主席  \n   C. 总行高级管理人员  \n   D. 审计部门负责人  "
            },
            {
                "id": "sim_test_2",
                "category": "选择题",
                "question": "普惠金融事业部筹备工作领导小组的组长一般由谁来担任？",  # 略微改变措辞
                "content": "   A. 分行行长  \n   B. 董事会主席  \n   C. 总行高级管理人员  \n   D. 审计部门负责人  "
            },
            {
                "id": "sim_test_3", 
                "category": "选择题",
                "question": "在普惠金融事业部的筹备工作中，领导小组组长通常由谁担任？",  # 更大改动
                "content": "   A. 分行行长  \n   B. 董事会主席  \n   C. 总行高级管理人员  \n   D. 审计部门负责人  "
            }
        ]
        
        # 执行测试
        print("执行测试：提问3个相似问题，记录时间和答案...")
        results = []
        start_times = []
        end_times = []
        
        for i, question in enumerate(test_questions):
            print(f"\n处理问题 #{i+1} (ID: {question['id']})...")
            start_time = time.time()
            start_times.append(start_time)
            result = self.qa_system.process_question(question)
            end_time = time.time()
            end_times.append(end_time)
            results.append(result)
            
            print(f"  耗时: {end_time - start_time:.2f}秒")
            print(f"  答案长度: {len(result.get('raw_llm_output', ''))}")
        
        # 分析结果
        print("\n分析结果:")
        self._analyze_similar_results(results, start_times, end_times)
        
        return results
    
    def test_direct_rag_engine(self):
        """直接测试RAG引擎，绕过上层封装"""
        print("\n" + "="*60)
        print("测试3: 直接测试RAG引擎")
        print("="*60)
        
        # 获取RAG引擎实例
        rag_engine = self.qa_system.rag_engine
        if not rag_engine:
            print("❌ RAG引擎未初始化")
            return []
        
        # 构建测试用例
        test_queries = [
            "普惠金融事业部筹备工作领导小组的组长通常由谁担任？",
            "普惠金融事业部筹备工作领导小组的组长通常由谁担任？",  # 完全相同
            "区域性保险公估机构的营运资金要求是多少？"  # 完全不同
        ]
        
        # 执行测试
        print("执行测试：直接通过RAG引擎处理3个查询...")
        results = []
        timestamps = []
        
        for i, query in enumerate(test_queries):
            print(f"\n处理查询 #{i+1}...")
            start_time = time.time()
            
            # 检索文档
            print("  检索文档...")
            contexts = rag_engine.retrieve_documents(query)
            retrieval_time = time.time()
            print(f"  检索耗时: {retrieval_time - start_time:.2f}秒")
            print(f"  检索到 {len(contexts) if contexts else 0} 个相关文档")
            
            # 生成答案
            print("  生成答案...")
            if contexts:
                combined_context = '\n\n'.join(contexts[:3])
                answer = rag_engine.generate_answer(query, combined_context, "选择题" if i < 2 else "问答题")
            else:
                answer = "未找到相关文档"
            
            end_time = time.time()
            timestamps.append((start_time, retrieval_time, end_time))
            
            print(f"  生成耗时: {end_time - retrieval_time:.2f}秒")
            print(f"  总耗时: {end_time - start_time:.2f}秒")
            print(f"  答案长度: {len(answer)}")
            
            results.append({
                "query": query,
                "answer": answer,
                "num_contexts": len(contexts) if contexts else 0
            })
        
        # 分析结果
        print("\n分析结果:")
        self._analyze_engine_results(results, timestamps)
        
        return results
    
    def _analyze_repeated_results(self, results: List[Dict[str, Any]], start_times: List[float], end_times: List[float]):
        """分析重复问题的结果"""
        if len(results) < 2:
            print("❌ 结果数量不足，无法分析")
            return
        
        # 检查时间差异
        time_diffs = [end_times[i] - start_times[i] for i in range(len(results))]
        avg_time = sum(time_diffs) / len(time_diffs)
        max_diff = max(time_diffs) - min(time_diffs)
        
        print(f"时间分析:")
        print(f"  平均耗时: {avg_time:.2f}秒")
        print(f"  最大时间差异: {max_diff:.2f}秒")
        
        if max_diff < 0.5 and avg_time < 1.0:
            print("⚠️ 警告: 所有查询耗时几乎相同且非常短，可能存在缓存机制")
        
        # 检查答案相似度
        answers = [result.get('raw_llm_output', '') for result in results]
        
        identical = all(a == answers[0] for a in answers)
        if identical:
            print("⚠️ 警告: 所有答案完全相同，几乎可以确定存在缓存或预设答案")
        else:
            # 计算文本相似度 (简单实现，使用共同单词比例)
            def simple_similarity(text1, text2):
                if not text1 or not text2:
                    return 0.0
                words1 = set(text1.split())
                words2 = set(text2.split())
                common = words1.intersection(words2)
                return len(common) / max(len(words1), len(words2))
            
            similarities = [simple_similarity(answers[i], answers[i+1]) 
                           for i in range(len(answers)-1)]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            
            print(f"文本相似度分析:")
            print(f"  答案之间的平均相似度: {avg_similarity:.2f}")
            
            if avg_similarity > 0.9:
                print("⚠️ 警告: 答案相似度非常高，可能存在缓存或模板答案")
    
    def _analyze_similar_results(self, results: List[Dict[str, Any]], start_times: List[float], end_times: List[float]):
        """分析相似问题的结果"""
        if len(results) < 2:
            print("❌ 结果数量不足，无法分析")
            return
        
        # 检查时间差异
        time_diffs = [end_times[i] - start_times[i] for i in range(len(results))]
        avg_time = sum(time_diffs) / len(time_diffs)
        
        print(f"时间分析:")
        print(f"  平均耗时: {avg_time:.2f}秒")
        for i, diff in enumerate(time_diffs):
            print(f"  问题 #{i+1} 耗时: {diff:.2f}秒")
        
        # 特别关注第一个问题和第二个问题的时间差异
        if len(time_diffs) >= 2:
            ratio = time_diffs[1] / time_diffs[0] if time_diffs[0] > 0 else 0
            print(f"  第二个问题相对第一个问题的时间比例: {ratio:.2f}")
            
            if ratio < 0.5:
                print("⚠️ 警告: 第二个相似问题处理时间显著短于第一个，可能存在缓存机制")
        
        # 检查答案相似度
        answers = [result.get('raw_llm_output', '') for result in results]
        
        # 简单相似度检查
        identical_pairs = [(i, j) for i in range(len(answers)) for j in range(i+1, len(answers)) 
                          if answers[i] == answers[j]]
        
        if identical_pairs:
            print("⚠️ 警告: 发现完全相同的答案对:")
            for i, j in identical_pairs:
                print(f"  问题 #{i+1} 和问题 #{j+1} 的答案完全相同")
    
    def _analyze_engine_results(self, results: List[Dict[str, Any]], timestamps: List[Tuple[float, float, float]]):
        """分析直接调用引擎的结果"""
        if len(results) < 2:
            print("❌ 结果数量不足，无法分析")
            return
        
        # 分析时间
        retrieval_times = [ts[1] - ts[0] for ts in timestamps]
        generation_times = [ts[2] - ts[1] for ts in timestamps]
        total_times = [ts[2] - ts[0] for ts in timestamps]
        
        print(f"时间分析:")
        print(f"  平均检索时间: {sum(retrieval_times)/len(retrieval_times):.2f}秒")
        print(f"  平均生成时间: {sum(generation_times)/len(generation_times):.2f}秒")
        print(f"  平均总时间: {sum(total_times)/len(total_times):.2f}秒")
        
        # 检查第一次和第二次(相同问题)的时间差异
        if len(retrieval_times) >= 2:
            retrieval_ratio = retrieval_times[1] / retrieval_times[0] if retrieval_times[0] > 0 else 0
            generation_ratio = generation_times[1] / generation_times[0] if generation_times[0] > 0 else 0
            
            print(f"  第二次检索相对第一次的时间比例: {retrieval_ratio:.2f}")
            print(f"  第二次生成相对第一次的时间比例: {generation_ratio:.2f}")
            
            if retrieval_ratio < 0.5:
                print("⚠️ 警告: 第二次检索时间显著短于第一次，可能存在检索缓存")
            
            if generation_ratio < 0.5:
                print("⚠️ 警告: 第二次生成时间显著短于第一次，可能存在生成缓存")
        
        # 分析答案
        answers = [result.get('answer', '') for result in results]
        
        # 检查重复问题的答案
        if len(answers) >= 2 and answers[0] == answers[1]:
            print("⚠️ 警告: 相同问题的两次答案完全一致，可能存在缓存")
        
        # 输出答案长度
        for i, answer in enumerate(answers):
            print(f"  查询 #{i+1} 答案长度: {len(answer)}")

def main():
    """主函数"""
    print("="*60)
    print("缓存检测工具")
    print("="*60)
    print("此工具用于检测系统中可能存在的缓存问题或伪造答案\n")
    
    detector = CacheDetector()
    
    # 运行测试
    detector.test_repeated_questions()
    detector.test_similar_questions()
    detector.test_direct_rag_engine()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main() 