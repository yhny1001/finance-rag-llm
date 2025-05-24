"""
金融监管制度智能问答系统主程序
"""

import os
import json
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from tqdm import tqdm

from config import Config
from rag_engine import RAGEngine


class FinancialQASystem:
    """金融监管制度智能问答系统主类"""
    
    def __init__(self):
        self.config = Config
        self.rag_engine = None
        self.results = []
        
    def initialize(self):
        """初始化系统"""
        print("初始化金融监管制度智能问答系统...")
        
        # 验证路径
        if not self.config.validate_paths():
            print("路径验证失败，请检查配置")
            return False
            
        # 创建必要目录
        self.config.create_dirs()
        
        # 初始化RAG引擎
        print("初始化RAG引擎...")
        self.rag_engine = RAGEngine()
        
        print("系统初始化完成")
        return True
    
    def build_knowledge_base(self, force_rebuild: bool = False):
        """构建知识库"""
        print("构建知识库...")
        
        if self.rag_engine is None:
            print("请先初始化系统")
            return False
            
        try:
            self.rag_engine.build_index(force_rebuild=force_rebuild)
            print("知识库构建完成")
            return True
        except Exception as e:
            print(f"知识库构建失败: {e}")
            return False
    
    def load_test_data(self) -> List[Dict[str, Any]]:
        """加载测试数据 - 支持JSONL格式"""
        print(f"加载测试数据: {self.config.TEST_DATA_PATH}")
        
        test_path = Path(self.config.TEST_DATA_PATH)
        if not test_path.exists():
            print(f"测试数据文件不存在: {self.config.TEST_DATA_PATH}")
            return []
            
        try:
            # 首先尝试标准JSON格式
            with open(test_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        questions = data
                    else:
                        questions = [data]
                    print(f"✅ 使用标准JSON格式成功加载 {len(questions)} 个问题")
                    return questions
                except json.JSONDecodeError:
                    print("标准JSON格式解析失败，尝试JSONL格式...")
                    
            # 尝试JSONL格式（每行一个JSON对象）
            questions = []
            with open(test_path, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # 跳过空行
                        continue
                        
                    try:
                        question_data = json.loads(line)
                        questions.append(question_data)
                    except json.JSONDecodeError as e:
                        print(f"警告：解析第{line_no}行时出错: {e}")
                        print(f"问题行内容: {line[:100]}...")
                        continue
                        
            if questions:
                print(f"✅ 使用JSONL格式成功加载 {len(questions)} 个问题")
                
                # 显示统计信息
                choice_count = sum(1 for q in questions if q.get('category') == '选择题')
                qa_count = sum(1 for q in questions if q.get('category') == '问答题')
                print(f"   选择题: {choice_count} 道")
                print(f"   问答题: {qa_count} 道")
                
                return questions
            else:
                print("❌ JSONL格式解析也失败了")
                return []
                
        except Exception as e:
            print(f"加载测试数据失败: {e}")
            return []
    
    def process_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个问题"""
        question_id = question_data.get('id', 'unknown')
        category = question_data.get('category', '问答题')
        question = question_data.get('question', '')
        content = question_data.get('content', '')
        
        print(f"\n处理问题 ID: {question_id}")
        print(f"类别: {category}")
        print(f"问题: {question}")
        
        # 构建完整问题（对于选择题，包含选项）
        if category == "选择题" and content:
            full_question = f"{question}\n{content}"
        else:
            full_question = question
            
        # 调用RAG引擎回答问题
        try:
            result = self.rag_engine.answer_question(full_question, category)
            
            # 整理结果
            processed_result = {
                "id": question_id,
                "category": category,
                "question": question,
                "content": content,
                "answer": result.get("answer", ""),
                "context_used": result.get("context_used", ""),
                "num_sources": result.get("num_sources", 0),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 如果有错误，记录错误信息
            if "error" in result:
                processed_result["error"] = result["error"]
                
            return processed_result
            
        except Exception as e:
            print(f"处理问题时发生错误: {e}")
            return {
                "id": question_id,
                "category": category,
                "question": question,
                "content": content,
                "answer": f"处理失败: {e}",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def process_batch(self, questions: List[Dict[str, Any]], start_idx: int = 0, end_idx: int = None) -> List[Dict[str, Any]]:
        """批量处理问题"""
        if end_idx is None:
            end_idx = len(questions)
            
        print(f"开始批量处理问题 {start_idx} 到 {end_idx}")
        
        batch_results = []
        for i in tqdm(range(start_idx, min(end_idx, len(questions))), desc="处理问题"):
            question_data = questions[i]
            result = self.process_question(question_data)
            batch_results.append(result)
            
            # 定期清理GPU缓存
            if (i + 1) % 5 == 0:
                self.rag_engine.cleanup()
                
        return batch_results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = None):
        """保存结果"""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.config.OUTPUT_DIR}/results_{timestamp}.json"
            
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            print(f"结果已保存到: {output_file}")
            
            # 同时保存为CSV格式以便查看
            csv_file = output_path.with_suffix('.csv')
            df = pd.DataFrame(results)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"结果CSV文件已保存到: {csv_file}")
            
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def run_test(self, force_rebuild: bool = False, batch_size: int = None, start_idx: int = 0, end_idx: int = None):
        """运行完整测试"""
        print("开始运行金融监管制度智能问答测试")
        
        # 初始化系统
        if not self.initialize():
            return False
            
        # 构建知识库
        if not self.build_knowledge_base(force_rebuild=force_rebuild):
            return False
            
        # 加载测试数据
        questions = self.load_test_data()
        if not questions:
            print("没有可用的测试数据")
            return False
            
        # 设置批处理大小
        if batch_size is None:
            batch_size = self.config.BATCH_SIZE
            
        # 设置处理范围
        if end_idx is None or end_idx > len(questions):
            end_idx = len(questions)
            
        print(f"将处理 {end_idx - start_idx} 个问题 (索引 {start_idx} 到 {end_idx - 1})")
        
        # 分批处理
        all_results = []
        for batch_start in range(start_idx, end_idx, batch_size):
            batch_end = min(batch_start + batch_size, end_idx)
            
            print(f"\n处理批次 {batch_start}-{batch_end-1}")
            batch_results = self.process_batch(questions, batch_start, batch_end)
            all_results.extend(batch_results)
            
            # 保存中间结果
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            intermediate_file = f"{self.config.OUTPUT_DIR}/batch_results_{batch_start}_{batch_end-1}_{timestamp}.json"
            self.save_results(batch_results, intermediate_file)
            
            print(f"批次 {batch_start}-{batch_end-1} 处理完成")
            
        # 保存最终结果
        self.save_results(all_results)
        
        # 打印统计信息
        self.print_statistics(all_results)
        
        print("测试完成！")
        return True
    
    def print_statistics(self, results: List[Dict[str, Any]]):
        """打印统计信息"""
        print("\n" + "="*50)
        print("测试统计信息")
        print("="*50)
        
        total_questions = len(results)
        choice_questions = sum(1 for r in results if r.get('category') == '选择题')
        qa_questions = sum(1 for r in results if r.get('category') == '问答题')
        error_count = sum(1 for r in results if 'error' in r)
        
        print(f"总问题数: {total_questions}")
        print(f"选择题数: {choice_questions}")
        print(f"问答题数: {qa_questions}")
        print(f"处理失败数: {error_count}")
        print(f"成功率: {((total_questions - error_count) / total_questions * 100):.2f}%")
        
        # 统计平均检索源数量
        avg_sources = sum(r.get('num_sources', 0) for r in results if 'error' not in r) / max(1, total_questions - error_count)
        print(f"平均检索源数量: {avg_sources:.2f}")
        
        # 显示向量数据库统计
        if self.rag_engine:
            vector_stats = self.rag_engine.get_vector_db_stats()
            print(f"\n向量数据库统计:")
            for key, value in vector_stats.items():
                print(f"  {key}: {value}")
    
    def show_vector_db_info(self):
        """显示向量数据库信息"""
        if not self.rag_engine:
            print("RAG引擎未初始化")
            return
            
        stats = self.rag_engine.get_vector_db_stats()
        print("\n" + "="*50)
        print("向量数据库详细信息")
        print("="*50)
        
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    def rebuild_vector_database(self):
        """重建向量数据库"""
        print("开始重建向量数据库...")
        
        if not self.initialize():
            return False
            
        try:
            self.rag_engine.rebuild_vector_db()
            print("向量数据库重建完成")
            self.show_vector_db_info()
            return True
        except Exception as e:
            print(f"重建向量数据库失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="金融监管制度智能问答系统")
    parser.add_argument("--force-rebuild", action="store_true", help="强制重建索引")
    parser.add_argument("--batch-size", type=int, default=10, help="批处理大小")
    parser.add_argument("--start-idx", type=int, default=0, help="开始索引")
    parser.add_argument("--end-idx", type=int, help="结束索引")
    parser.add_argument("--interactive", action="store_true", help="交互式问答模式")
    parser.add_argument("--vector-info", action="store_true", help="显示向量数据库信息")
    parser.add_argument("--rebuild-vector", action="store_true", help="重建向量数据库")
    
    args = parser.parse_args()
    
    # 创建系统实例
    qa_system = FinancialQASystem()
    
    if args.vector_info:
        # 显示向量数据库信息
        qa_system.initialize()
        qa_system.show_vector_db_info()
        return
        
    if args.rebuild_vector:
        # 重建向量数据库
        qa_system.rebuild_vector_database()
        return
    
    if args.interactive:
        # 交互式模式
        print("进入交互式问答模式")
        if not qa_system.initialize():
            return
            
        if not qa_system.build_knowledge_base(force_rebuild=args.force_rebuild):
            return
            
        print("系统准备就绪，输入 'quit' 退出，'info' 查看向量数据库信息")
        
        while True:
            user_input = input("\n请输入问题: ").strip()
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'info':
                qa_system.show_vector_db_info()
                continue
                
            if not user_input:
                continue
                
            result = qa_system.rag_engine.answer_question(user_input, "问答题")
            print(f"\n答案: {result.get('answer', '无法生成答案')}")
            
    else:
        # 批量测试模式
        qa_system.run_test(
            force_rebuild=args.force_rebuild,
            batch_size=args.batch_size,
            start_idx=args.start_idx,
            end_idx=args.end_idx
        )


if __name__ == "__main__":
    main() 