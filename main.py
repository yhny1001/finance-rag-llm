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
from resume_processor import ResumeProcessor  # 导入断点续传处理器


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
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = None, generate_competition_format: bool = False):
        """保存结果"""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.config.OUTPUT_DIR}/results_{timestamp}.json"
            
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            # 保存完整结果（用于调试和分析）
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            print(f"完整结果已保存到: {output_file}")
            
            # 只有在指定时才生成比赛要求的result.json文件
            if generate_competition_format:
                self.save_competition_format(results)
            
            # 同时保存为CSV格式以便查看
            csv_file = output_path.with_suffix('.csv')
            df = pd.DataFrame(results)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"结果CSV文件已保存到: {csv_file}")
            
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def save_competition_format(self, results: List[Dict[str, Any]]):
        """保存符合比赛要求的result.json文件"""
        print("\n🎯 生成比赛提交格式文件...")
        
        result_file = "result.json"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                for result in results:
                    # 提取基本信息
                    question_id = result.get('id')
                    category = result.get('category', '问答题')
                    answer = result.get('answer', '')
                    
                    # 处理答案格式
                    if category == '选择题':
                        # 从答案中提取选项（A、B、C、D等）
                        processed_answer = self.extract_choice_answer(answer)
                    else:
                        # 问答题直接使用文本答案
                        processed_answer = answer.strip()
                    
                    # 构建比赛格式的JSON对象
                    competition_result = {
                        "id": question_id,
                        "answer": processed_answer
                    }
                    
                    # 写入文件（JSONL格式，每行一个JSON对象）
                    json.dump(competition_result, f, ensure_ascii=False)
                    f.write('\n')
            
            print(f"✅ 比赛提交文件已生成: {result_file}")
            
            # 验证文件格式
            self.validate_result_file(result_file)
            
        except Exception as e:
            print(f"❌ 生成比赛格式文件失败: {e}")
    
    def extract_choice_answer(self, answer_text: str) -> List[str]:
        """从回答中提取选择题答案 - 改进版"""
        import re
        
        # 🎯 改进的选择题答案模式，优先级从高到低
        patterns = [
            # 1. 明确的答案声明
            r'正确答案[是为：:]\s*([A-D])',
            r'答案[是为：:]\s*([A-D])',
            r'选择\s*([A-D])',
            r'应该选择?\s*([A-D])',
            r'答案应该[是为]?\s*([A-D])',
            
            # 2. 分析结论
            r'因此[,，]?\s*答案[是为]?\s*([A-D])',
            r'所以[,，]?\s*答案[是为]?\s*([A-D])',
            r'综上所述[,，]?\s*答案[是为]?\s*([A-D])',
            r'综合分析[,，]?\s*答案[是为]?\s*([A-D])',
            
            # 3. 选项分析
            r'选项\s*([A-D])\s*[是为]?正确',
            r'([A-D])\s*选项[是为]?正确',
            r'([A-D])\s*是正确的',
            r'([A-D])\s*正确',
            
            # 4. 格式化答案
            r'[选答]\s*([A-D])',
            r'答案[:：]\s*([A-D])',
            r'^([A-D])[.、，]',  # 以选项开头
            
            # 5. 在句子中的选项
            r'\b([A-D])\b.*?正确',
            r'选择.*?([A-D])',
        ]
        
        # 先尝试在完整文本中查找
        answer_text_clean = answer_text.strip()
        answer_text_upper = answer_text_clean.upper()
        
        # 按优先级尝试匹配
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, answer_text_upper)
            if matches:
                choice = matches[0].strip()
                if choice in ['A', 'B', 'C', 'D']:
                    print(f"✅ 提取选择题答案: {choice} (模式{i+1})")
                    return [choice]
        
        # 🎯 改进：检查最后一句话中的选项
        sentences = re.split(r'[。！？.!?]', answer_text_clean)
        for sentence in reversed(sentences):  # 从最后一句开始
            if sentence.strip():
                sentence_upper = sentence.upper()
                for pattern in patterns[:8]:  # 使用前8个高优先级模式
                    matches = re.findall(pattern, sentence_upper)
                    if matches:
                        choice = matches[0].strip()
                        if choice in ['A', 'B', 'C', 'D']:
                            print(f"✅ 从句子中提取选择题答案: {choice}")
                            return [choice]
        
        # 🎯 改进：查找单独出现的选项
        isolated_choices = re.findall(r'\b([A-D])\b', answer_text_upper)
        if isolated_choices:
            # 统计每个选项出现的次数
            choice_counts = {}
            for choice in isolated_choices:
                choice_counts[choice] = choice_counts.get(choice, 0) + 1
            
            # 选择出现次数最多的，如果平局则选择最后出现的
            if choice_counts:
                max_count = max(choice_counts.values())
                frequent_choices = [c for c, count in choice_counts.items() if count == max_count]
                
                # 在频繁选项中选择最后出现的
                for choice in reversed(isolated_choices):
                    if choice in frequent_choices:
                        print(f"✅ 基于频率提取选择题答案: {choice}")
                        return [choice]
        
        # 🎯 最后尝试：基于关键词推测
        answer_lower = answer_text.lower()
        if any(word in answer_lower for word in ['第一', '首先', '最初']):
            print("⚠️ 基于关键词推测答案: A")
            return ["A"]
        elif any(word in answer_lower for word in ['第二', '其次', '另外']):
            print("⚠️ 基于关键词推测答案: B")
            return ["B"]
        elif any(word in answer_lower for word in ['第三', '再者', '此外']):
            print("⚠️ 基于关键词推测答案: C")
            return ["C"]
        elif any(word in answer_lower for word in ['第四', '最后', '最终']):
            print("⚠️ 基于关键词推测答案: D")
            return ["D"]
        
        # 如果都没有找到，返回默认答案
        print(f"⚠️ 无法从答案中提取选项，使用默认答案A")
        print(f"原文: {answer_text[:200]}...")
        return ["A"]  # 默认选择A
    
    def validate_result_file(self, result_file: str):
        """验证结果文件格式"""
        print("🔍 验证结果文件格式...")
        
        try:
            choice_count = 0
            qa_count = 0
            
            with open(result_file, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # 检查必需字段
                        if 'id' not in data or 'answer' not in data:
                            print(f"❌ 第{line_no}行缺少必需字段: {line}")
                            continue
                        
                        # 统计答案类型
                        answer = data['answer']
                        if isinstance(answer, list):
                            choice_count += 1
                        else:
                            qa_count += 1
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ 第{line_no}行JSON格式错误: {e}")
            
            print(f"✅ 文件格式验证通过")
            print(f"   选择题: {choice_count} 道")
            print(f"   问答题: {qa_count} 道")
            print(f"   总计: {choice_count + qa_count} 道")
            
            # 显示前几行示例
            print("\n📝 文件内容示例:")
            with open(result_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 3:  # 只显示前3行
                        break
                    print(f"   {line.strip()}")
                        
        except Exception as e:
            print(f"❌ 验证文件时出错: {e}")
    
    def run_test(self, force_rebuild: bool = False, batch_size: int = None, start_idx: int = 0, end_idx: int = None, no_resume: bool = False):
        """运行完整测试"""
        print("开始运行金融监管制度智能问答测试")
        
        # 初始化断点续传处理器
        resume_processor = ResumeProcessor()
        
        # 清理旧的中间文件
        self.cleanup_intermediate_files()
        
        # 生成本次运行的唯一标识
        run_timestamp = time.strftime("%Y%m%d_%H%M%S")
        print(f"🏷️ 本次运行标识: {run_timestamp}")
        
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
        
        # 检查是否有上次的断点
        checkpoint_start_idx = None
        checkpoint_batch_size = None
        checkpoint_results = None
        
        if not no_resume and resume_processor.has_checkpoint():
            # 询问用户是否继续上次的处理
            print("\n🔄 检测到上次处理的断点")
            choice = input("是否继续上次的处理? (y/n，默认y): ").strip().lower()
            
            if choice != 'n':
                checkpoint_start_idx, checkpoint_batch_size, checkpoint_results = resume_processor.load_checkpoint()
                
                if checkpoint_start_idx is not None:
                    start_idx = checkpoint_start_idx
                    print(f"🔄 将从索引 {start_idx} 继续处理")
                    
                    if checkpoint_batch_size is not None:
                        batch_size = checkpoint_batch_size
                        print(f"🔄 使用上次的批处理大小: {batch_size}")
                    
                    if checkpoint_results:
                        print(f"🔄 已加载上次的处理结果: {len(checkpoint_results)} 个问题")
                        all_results = checkpoint_results
                    else:
                        all_results = []
                else:
                    all_results = []
            else:
                # 用户选择从头开始，清除检查点
                resume_processor.clear_checkpoint()
                all_results = []
        else:
            # 强制从头开始，或者没有检查点
            if no_resume and resume_processor.has_checkpoint():
                print("🧹 根据参数设置，忽略断点，从头开始处理")
                resume_processor.clear_checkpoint()
            all_results = []
        
        # 设置处理范围
        if end_idx is None or end_idx > len(questions):
            end_idx = len(questions)
            
        print(f"将处理 {end_idx - start_idx} 个问题 (索引 {start_idx} 到 {end_idx - 1})")
        
        # 分批处理
        try:
            for batch_start in range(start_idx, end_idx, batch_size):
                batch_end = min(batch_start + batch_size, end_idx)
                
                print(f"\n处理批次 {batch_start}-{batch_end-1}")
                batch_results = self.process_batch(questions, batch_start, batch_end)
                all_results.extend(batch_results)
                
                # 保存中间结果（不生成比赛格式文件）
                intermediate_file = f"{self.config.OUTPUT_DIR}/batch_results_{batch_start}_{batch_end-1}_{run_timestamp}.json"
                self.save_results(batch_results, intermediate_file, generate_competition_format=False)
                
                # 保存断点续传检查点
                resume_processor.save_checkpoint(batch_end, end_idx, batch_size, all_results)
                
                print(f"批次 {batch_start}-{batch_end-1} 处理完成")
                
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断处理")
            print(f"💾 已处理结果将保存在断点续传检查点中")
            resume_processor.save_checkpoint(batch_start, end_idx, batch_size, all_results)
            return False
        except Exception as e:
            print(f"\n❌ 处理过程中出错: {e}")
            print(f"💾 已处理结果将保存在断点续传检查点中")
            resume_processor.save_checkpoint(batch_start, end_idx, batch_size, all_results)
            return False
        
        # 保存最终结果（生成比赛格式文件）
        print(f"\n🏁 所有批次处理完成，生成最终结果...")
        final_result_file = f"{self.config.OUTPUT_DIR}/final_results_{run_timestamp}.json"
        competition_result_file = f"result_{run_timestamp}.json"
        
        # 保存完整结果
        self.save_results(all_results, final_result_file, generate_competition_format=False)
        
        # 生成比赛格式文件
        self.save_competition_format_with_filename(all_results, competition_result_file)
        
        # 同时生成默认名称的result.json（覆盖旧版本）
        self.save_competition_format_with_filename(all_results, "result.json")
        
        # 打印统计信息
        self.print_statistics(all_results)
        
        print(f"\n🎯 比赛文件已生成:")
        print(f"   - {competition_result_file} (带时间戳)")
        print(f"   - result.json (默认文件)")
        print("测试完成！")
        
        # 清除检查点（成功完成后）
        resume_processor.clear_checkpoint()
        
        return True
    
    def cleanup_intermediate_files(self):
        """清理旧的中间文件"""
        print("🧹 清理旧的中间文件...")
        
        output_dir = Path(self.config.OUTPUT_DIR)
        if not output_dir.exists():
            return
            
        # 清理批次结果文件
        batch_files = list(output_dir.glob("batch_results_*.json"))
        for file in batch_files:
            try:
                file.unlink()
                print(f"   ✅ 删除: {file.name}")
            except Exception as e:
                print(f"   ❌ 删除失败 {file.name}: {e}")
        
        if batch_files:
            print(f"清理了 {len(batch_files)} 个中间文件")
        else:
            print("没有需要清理的中间文件")

    def save_competition_format_with_filename(self, results: List[Dict[str, Any]], filename: str):
        """保存比赛格式文件到指定文件名"""
        print(f"\n🎯 生成比赛提交格式文件: {filename}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for result in results:
                    # 提取基本信息
                    question_id = result.get('id')
                    category = result.get('category', '问答题')
                    answer = result.get('answer', '')
                    
                    # 处理答案格式
                    if category == '选择题':
                        # 从答案中提取选项（A、B、C、D等）
                        processed_answer = self.extract_choice_answer(answer)
                    else:
                        # 问答题直接使用文本答案
                        processed_answer = answer.strip()
                    
                    # 构建比赛格式的JSON对象
                    competition_result = {
                        "id": question_id,
                        "answer": processed_answer
                    }
                    
                    # 写入文件（JSONL格式，每行一个JSON对象）
                    json.dump(competition_result, f, ensure_ascii=False)
                    f.write('\n')
            
            print(f"✅ 比赛提交文件已生成: {filename}")
            
            # 验证文件格式
            self.validate_result_file(filename)
            
        except Exception as e:
            print(f"❌ 生成比赛格式文件失败: {e}")
    
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
    # 断点续传相关参数
    parser.add_argument("--no-resume", action="store_true", help="不使用断点续传，从头开始处理")
    parser.add_argument("--checkpoint-info", action="store_true", help="显示当前检查点信息")
    parser.add_argument("--checkpoint-clear", action="store_true", help="清除当前检查点")
    
    args = parser.parse_args()
    
    # 创建系统实例
    qa_system = FinancialQASystem()
    
    # 处理断点续传相关命令
    if args.checkpoint_info or args.checkpoint_clear:
        from resume_processor import ResumeProcessor
        resume = ResumeProcessor()
        
        if args.checkpoint_info:
            # 显示检查点信息
            if resume.has_checkpoint():
                with open(resume.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                print("\n" + "="*50)
                print("📊 检查点信息")
                print("="*50)
                
                print(f"🕒 保存时间: {checkpoint_data.get('time_str', '未知')}")
                print(f"📈 进度: {checkpoint_data.get('current_idx', 0)}/{checkpoint_data.get('total', 0)} "
                      f"({checkpoint_data.get('completed_percentage', 0)}%)")
                print(f"📦 批处理大小: {checkpoint_data.get('batch_size', 0)}")
            else:
                print("📝 没有检查点信息")
        
        if args.checkpoint_clear:
            # 清除检查点
            if resume.has_checkpoint():
                if resume.clear_checkpoint():
                    print("✅ 检查点已清除")
            else:
                print("📝 没有检查点需要清除")
        
        # 如果只是查看或清除检查点，不执行其他操作
        if not any([args.vector_info, args.rebuild_vector, args.interactive]):
            return
    
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
            end_idx=args.end_idx,
            no_resume=args.no_resume
        )


if __name__ == "__main__":
    main() 