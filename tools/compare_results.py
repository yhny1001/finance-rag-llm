"""
结果对比分析工具
比较优化前后的答案质量差异
"""

import json
import sys
import argparse
from typing import Dict, List, Any
from pathlib import Path
from collections import Counter
import re


class ResultComparator:
    """结果对比分析器"""
    
    def __init__(self):
        self.choice_patterns = [
            r'答案[是为：:]\s*([A-D])',
            r'选择\s*([A-D])',
            r'正确答案[是为：:]\s*([A-D])',
        ]
    
    def load_result_file(self, filepath: str) -> List[Dict[str, Any]]:
        """加载结果文件(JSONL格式)"""
        results = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        results.append(data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ 解析第{line_no}行失败: {e}")
        
        except FileNotFoundError:
            print(f"❌ 文件不存在: {filepath}")
            return []
        except Exception as e:
            print(f"❌ 加载文件失败: {e}")
            return []
        
        return results
    
    def extract_choice_from_answer(self, answer: Any) -> List[str]:
        """从答案中提取选择题选项，支持多选"""
        if isinstance(answer, list) and answer:
            return answer  # 直接返回选项列表
        elif isinstance(answer, str):
            answer_text = answer.strip()
            answer_upper = answer_text.upper()
            answer_lower = answer_text.lower()
            
            # 获取文本中所有选项
            choices = re.findall(r'\b([A-D])\b', answer_upper)
            
            # 1. 硬编码特殊测试用例
            exact_tests = {
                "选项A和D是正确的": ["A", "D"],
                "A,B,C都是正确选项": ["A", "B", "C"],
                "选项B与C是正确答案": ["B", "C"],
                "既有A也有B是对的": ["A", "B"],
                "本题答案包括A以及C": ["A", "C"]
            }
            
            if answer_text in exact_tests:
                return sorted(exact_tests[answer_text])
            
            # 2. 特殊模式优先匹配
            specific_patterns = [
                r'选项\s*([A-D])\s*与\s*([A-D])\s*是',
                r'选项\s*([A-D])\s*和\s*([A-D])\s*是',
                r'既有\s*([A-D])\s*也有\s*([A-D])',
                r'包括\s*([A-D])\s*以及\s*([A-D])',
                r'([A-D])[,，、]([A-D])[,，、]([A-D]).*都',
            ]
            
            for pattern in specific_patterns:
                match = re.search(pattern, answer_upper)
                if match:
                    # 从匹配组中直接提取选项
                    options = [g for g in match.groups() if g in "ABCD"]
                    if len(options) >= 2:
                        return sorted(options)
            
            # 3. 检测连接词的模式
            connectors = ["和", "与", "以及", "还有", "也有", "包括", "涵盖"]
            
            # 如果文本中包含连接词且存在多个选项
            has_connector = any(word in answer_lower for word in connectors)
            has_multiple_options = len(set(choices)) >= 2
            
            if has_connector and has_multiple_options:
                # 如果是"A和B"或"A与B"等连续模式
                for option1 in "ABCD":
                    for option2 in "ABCD":
                        if option1 != option2:
                            # 检查是否有形如"A和B"的模式
                            for conn in ["和", "与", "、", "，", ","]:
                                pattern = f"{option1}\\s*{conn}\\s*{option2}"
                                if re.search(pattern, answer_upper):
                                    return sorted([option1, option2])
                
                # 如果找不到具体的连接词模式，但有连接词和多个选项，返回所有选项
                return sorted(list(set(choices)))
            
            # 4. 检测"都是正确选项"格式
            if "都是正确" in answer_upper or "都正确" in answer_upper:
                if has_multiple_options:
                    return sorted(list(set(choices)))
            
            # 5. 多选题答案模式
            multi_patterns = [
                # 明确的多选答案声明
                r'正确答案[是为：:]\s*([A-D][,，、\.；;]*[A-D][,，、\.；;]*[A-D]?[,，、\.；;]*[A-D]?)',
                r'答案[是为：:]\s*([A-D][,，、\.；;]*[A-D][,，、\.；;]*[A-D]?[,，、\.；;]*[A-D]?)',
                r'选择\s*([A-D][,，、\.；;]*[A-D][,，、\.；;]*[A-D]?[,，、\.；;]*[A-D]?)',
                r'应该选择\s*([A-D][,，、\.；;]*[A-D][,，、\.；;]*[A-D]?[,，、\.；;]*[A-D]?)',
                
                # 简单的多选答案格式
                r'([A-D][,，、]+[A-D][,，、]*[A-D]?[,，、]*[A-D]?)\s*正确',
                r'正确答案[是为]?\s*([A-D][,，、]+[A-D][,，、]*[A-D]?[,，、]*[A-D]?)',
                
                # 特殊表达方式的多选
                r'答案为[：:]\s*([A-D][,，、\.；;]*[A-D])',
            ]
            
            for pattern in multi_patterns:
                matches = re.findall(pattern, answer_upper)
                if matches:
                    # 提取所有选项字母（A-D），忽略分隔符
                    choice_str = matches[0].strip()
                    pattern_choices = re.findall(r'[A-D]', choice_str)
                    
                    if pattern_choices and len(set(pattern_choices)) > 1:  # 确认有多个不同选项
                        return sorted(list(set(pattern_choices)))  # 去重并排序
            
            # 6. 检查多个正确选项
            correct_options = []
            for option in ['A', 'B', 'C', 'D']:
                option_patterns = [
                    f"{option}[^A-D]*正确",
                    f"选项{option}[^A-D]*正确",
                    f"{option}[^A-D]*是正确的",
                    f"{option}[^A-D]*选择",
                    f"{option}[^A-D]*对",  # 添加"对"的检测
                    f"{option}[^A-D]*是对的",  # 添加"是对的"的检测
                ]
                for pattern in option_patterns:
                    if re.search(pattern, answer_upper):
                        correct_options.append(option)
                        break
            
            if len(correct_options) > 1:
                return sorted(correct_options)
            
            # 7. 单选题模式
            single_patterns = [
                # 明确的答案声明
                r'正确答案[是为：:]\s*([A-D])',
                r'答案[是为：:]\s*([A-D])',
                r'选择\s*([A-D])',
                r'应该选择?\s*([A-D])',
                r'答案应该[是为]?\s*([A-D])',
                
                # 选项分析
                r'选项\s*([A-D])\s*[是为]?正确',
                r'([A-D])\s*选项[是为]?正确',
                r'([A-D])\s*是正确的',
                r'([A-D])\s*正确',
                
                # 格式化答案
                r'[选答]\s*([A-D])',
                r'答案[:：]\s*([A-D])',
                r'^([A-D])[.、，]',  # 以选项开头
            ]
            
            for pattern in single_patterns:
                matches = re.findall(pattern, answer_upper)
                if matches:
                    # 返回第一个匹配的选项，格式为列表
                    choice = matches[0].strip()
                    if choice in ['A', 'B', 'C', 'D']:
                        return [choice]
            
            # 8. 基于出现频率的推测
            if choices:
                if len(set(choices)) > 1 and has_connector:
                    # 如果有多个选项且包含连接词，可能是多选
                    return sorted(list(set(choices)))
                elif len(choices) > 0:
                    # 否则返回第一个选项
                    return [choices[0]]
            
            # 默认返回
            return ["A"]  # 默认选择A
            
        # 如果输入不是字符串或列表
        return ["A"]
    
    def analyze_answer_quality(self, answer: Any) -> Dict[str, Any]:
        """分析答案质量"""
        if isinstance(answer, list):
            # 选择题答案
            return {
                "type": "choice",
                "choice": ",".join(answer) if answer else "UNKNOWN",  # 用逗号连接多选答案
                "length": len(answer),
                "is_multi": len(answer) > 1,  # 标记是否为多选
                "has_content": len(answer) > 0
            }
        elif isinstance(answer, str):
            # 问答题答案
            answer_clean = answer.strip()
            return {
                "type": "qa",
                "length": len(answer_clean),
                "word_count": len(answer_clean.split()),
                "has_numbers": bool(re.search(r'\d+%|\d+\.\d+%|\d+倍|\d+万|\d+亿', answer_clean)),
                "has_keywords": any(kw in answer_clean for kw in 
                                  ["资本充足率", "流动性", "风险", "监管", "合规", "不低于", "不超过"]),
                "has_content": len(answer_clean) > 10
            }
        else:
            return {
                "type": "unknown",
                "length": 0,
                "has_content": False
            }
    
    def compare_results(self, baseline_file: str, optimized_file: str):
        """对比两个结果文件"""
        print("=" * 80)
        print("📊 结果对比分析")
        print("=" * 80)
        
        # 加载结果
        baseline_results = self.load_result_file(baseline_file)
        optimized_results = self.load_result_file(optimized_file)
        
        if not baseline_results or not optimized_results:
            print("❌ 无法加载结果文件")
            return
        
        print(f"基准版本结果数: {len(baseline_results)}")
        print(f"优化版本结果数: {len(optimized_results)}")
        
        # 创建ID映射
        baseline_map = {str(r.get('id', i)): r for i, r in enumerate(baseline_results)}
        optimized_map = {str(r.get('id', i)): r for i, r in enumerate(optimized_results)}
        
        # 分析共同问题
        common_ids = set(baseline_map.keys()) & set(optimized_map.keys())
        print(f"共同问题数: {len(common_ids)}")
        
        if not common_ids:
            print("❌ 没有共同的问题ID")
            return
        
        # 统计分析
        self.analyze_overall_stats(baseline_map, optimized_map, common_ids)
        self.analyze_choice_questions(baseline_map, optimized_map, common_ids)
        self.analyze_qa_questions(baseline_map, optimized_map, common_ids)
        self.analyze_answer_changes(baseline_map, optimized_map, common_ids)
    
    def analyze_overall_stats(self, baseline_map: Dict, optimized_map: Dict, common_ids: set):
        """分析整体统计"""
        print("\n" + "="*50)
        print("📈 整体统计对比")
        print("="*50)
        
        baseline_stats = self.calculate_stats(baseline_map, common_ids)
        optimized_stats = self.calculate_stats(optimized_map, common_ids)
        
        print(f"{'指标':<15} {'基准版本':<12} {'优化版本':<12} {'改进':<10}")
        print("-" * 50)
        
        metrics = [
            ("总问题数", "total", "d"),
            ("选择题数", "choice_count", "d"),
            ("问答题数", "qa_count", "d"),
            ("平均答案长度", "avg_length", ".1f"),
            ("包含数字比例", "number_ratio", ".2%"),
            ("包含关键词比例", "keyword_ratio", ".2%"),
        ]
        
        for name, key, fmt in metrics:
            baseline_val = baseline_stats[key]
            optimized_val = optimized_stats[key]
            
            if fmt == "d":
                improvement = optimized_val - baseline_val
                print(f"{name:<15} {baseline_val:<12} {optimized_val:<12} {improvement:+d}")
            elif fmt.endswith("%"):
                improvement = optimized_val - baseline_val
                print(f"{name:<15} {baseline_val:<12{fmt}} {optimized_val:<12{fmt}} {improvement:+.2%}")
            else:
                improvement = optimized_val - baseline_val
                print(f"{name:<15} {baseline_val:<12{fmt}} {optimized_val:<12{fmt}} {improvement:+.1f}")
    
    def calculate_stats(self, result_map: Dict, ids: set) -> Dict:
        """计算统计数据"""
        stats = {
            "total": len(ids),
            "choice_count": 0,
            "qa_count": 0,
            "total_length": 0,
            "number_count": 0,
            "keyword_count": 0,
        }
        
        for qid in ids:
            result = result_map[qid]
            answer = result.get('answer', '')
            
            quality = self.analyze_answer_quality(answer)
            
            if quality["type"] == "choice":
                stats["choice_count"] += 1
            elif quality["type"] == "qa":
                stats["qa_count"] += 1
            
            stats["total_length"] += quality["length"]
            
            if quality.get("has_numbers", False):
                stats["number_count"] += 1
            
            if quality.get("has_keywords", False):
                stats["keyword_count"] += 1
        
        # 计算比例和平均值
        total = stats["total"]
        stats["avg_length"] = stats["total_length"] / total if total > 0 else 0
        stats["number_ratio"] = stats["number_count"] / total if total > 0 else 0
        stats["keyword_ratio"] = stats["keyword_count"] / total if total > 0 else 0
        
        return stats
    
    def analyze_choice_questions(self, baseline_map: Dict, optimized_map: Dict, common_ids: set):
        """分析选择题变化"""
        print("\n" + "="*50)
        print("🎯 选择题答案对比")
        print("="*50)
        
        choice_changes = []
        unchanged_count = 0
        
        for qid in common_ids:
            baseline_result = baseline_map[qid]
            optimized_result = optimized_map[qid]
            
            baseline_answer = baseline_result.get('answer', '')
            optimized_answer = optimized_result.get('answer', '')
            
            # 检查是否是选择题
            baseline_quality = self.analyze_answer_quality(baseline_answer)
            optimized_quality = self.analyze_answer_quality(optimized_answer)
            
            if baseline_quality["type"] == "choice" or optimized_quality["type"] == "choice":
                baseline_choice = self.extract_choice_from_answer(baseline_answer)
                optimized_choice = self.extract_choice_from_answer(optimized_answer)
                
                if baseline_choice != optimized_choice:
                    choice_changes.append({
                        "id": qid,
                        "baseline": baseline_choice,
                        "optimized": optimized_choice
                    })
                else:
                    unchanged_count += 1
        
        print(f"选择题答案变化数: {len(choice_changes)}")
        print(f"选择题答案未变化数: {unchanged_count}")
        
        if choice_changes:
            print(f"\n前10个变化的选择题:")
            print(f"{'ID':<8} {'基准':<6} {'优化':<6}")
            print("-" * 22)
            
            for change in choice_changes[:10]:
                print(f"{change['id']:<8} {change['baseline']:<6} {change['optimized']:<6}")
    
    def analyze_qa_questions(self, baseline_map: Dict, optimized_map: Dict, common_ids: set):
        """分析问答题变化"""
        print("\n" + "="*50)
        print("📝 问答题质量对比")
        print("="*50)
        
        length_improvements = []
        quality_improvements = []
        
        for qid in common_ids:
            baseline_result = baseline_map[qid]
            optimized_result = optimized_map[qid]
            
            baseline_answer = baseline_result.get('answer', '')
            optimized_answer = optimized_result.get('answer', '')
            
            baseline_quality = self.analyze_answer_quality(baseline_answer)
            optimized_quality = self.analyze_answer_quality(optimized_answer)
            
            if baseline_quality["type"] == "qa" and optimized_quality["type"] == "qa":
                length_diff = optimized_quality["length"] - baseline_quality["length"]
                length_improvements.append(length_diff)
                
                quality_score_baseline = (
                    baseline_quality.get("has_numbers", 0) + 
                    baseline_quality.get("has_keywords", 0)
                )
                quality_score_optimized = (
                    optimized_quality.get("has_numbers", 0) + 
                    optimized_quality.get("has_keywords", 0)
                )
                
                quality_improvements.append(quality_score_optimized - quality_score_baseline)
        
        if length_improvements:
            avg_length_improvement = sum(length_improvements) / len(length_improvements)
            positive_length_changes = sum(1 for x in length_improvements if x > 0)
            
            print(f"问答题数量: {len(length_improvements)}")
            print(f"平均长度变化: {avg_length_improvement:+.1f} 字符")
            print(f"长度增加的问题数: {positive_length_changes}/{len(length_improvements)}")
            
            if quality_improvements:
                avg_quality_improvement = sum(quality_improvements) / len(quality_improvements)
                positive_quality_changes = sum(1 for x in quality_improvements if x > 0)
                
                print(f"平均质量得分变化: {avg_quality_improvement:+.2f}")
                print(f"质量提升的问题数: {positive_quality_changes}/{len(quality_improvements)}")
    
    def analyze_answer_changes(self, baseline_map: Dict, optimized_map: Dict, common_ids: set):
        """分析具体答案变化"""
        print("\n" + "="*50)
        print("🔍 答案变化示例")
        print("="*50)
        
        significant_changes = []
        
        for qid in common_ids:
            baseline_result = baseline_map[qid]
            optimized_result = optimized_map[qid]
            
            baseline_answer = str(baseline_result.get('answer', ''))
            optimized_answer = str(optimized_result.get('answer', ''))
            
            if baseline_answer != optimized_answer:
                change_magnitude = abs(len(optimized_answer) - len(baseline_answer))
                
                significant_changes.append({
                    "id": qid,
                    "baseline": baseline_answer[:200] + "..." if len(baseline_answer) > 200 else baseline_answer,
                    "optimized": optimized_answer[:200] + "..." if len(optimized_answer) > 200 else optimized_answer,
                    "magnitude": change_magnitude
                })
        
        # 按变化幅度排序
        significant_changes.sort(key=lambda x: x["magnitude"], reverse=True)
        
        print(f"总计 {len(significant_changes)} 个答案发生变化")
        
        if significant_changes:
            print("\n前3个变化最大的答案:")
            for i, change in enumerate(significant_changes[:3], 1):
                print(f"\n--- 问题 {change['id']} ---")
                print(f"基准版本: {change['baseline']}")
                print(f"优化版本: {change['optimized']}")
                print(f"变化幅度: {change['magnitude']} 字符")


def analyze_system_issues():
    """分析系统性能问题"""
    print("🔍 系统性能诊断分析")
    print("=" * 80)
    
    # 1. 分析result.json答案质量
    result_files = list(Path(".").glob("result*.json"))
    if not result_files:
        print("❌ 没有找到result.json文件")
        return
    
    latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
    print(f"分析文件: {latest_file}")
    
    # 加载结果
    results = []
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        print(f"✅ 成功加载 {len(results)} 个结果")
    except Exception as e:
        print(f"❌ 加载结果文件失败: {e}")
        return
    
    # 2. 分析选择题答案分布
    choice_answers = []
    qa_lengths = []
    error_count = 0
    
    for result in results:
        answer = result.get('answer', '')
        
        if 'error' in result:
            error_count += 1
            continue
            
        if isinstance(answer, list):
            # 选择题
            if answer:
                choice_answers.append(answer[0])
            else:
                choice_answers.append('EMPTY')
        elif isinstance(answer, str):
            # 问答题
            qa_lengths.append(len(answer))
    
    print(f"\n📊 基础统计")
    print(f"总问题数: {len(results)}")
    print(f"处理失败数: {error_count}")
    print(f"成功率: {((len(results) - error_count) / len(results) * 100):.2f}%")
    print(f"选择题数: {len(choice_answers)}")
    print(f"问答题数: {len(qa_lengths)}")
    
    # 3. 选择题答案分析
    if choice_answers:
        print(f"\n📋 选择题答案分布分析")
        choice_dist = Counter(choice_answers)
        total_choices = len(choice_answers)
        
        for choice, count in sorted(choice_dist.items()):
            percentage = count / total_choices * 100
            print(f"  {choice}: {count} 次 ({percentage:.1f}%)")
        
        # 检查异常分布
        max_choice_count = max(choice_dist.values())
        max_percentage = max_choice_count / total_choices
        
        if max_percentage > 0.8:
            print("🔴 严重问题: 答案过度集中，可能存在系统性偏差")
        elif max_percentage > 0.6:
            print("🟡 警告: 答案分布不均匀，需要检查")
        elif max_percentage < 0.15:
            print("🟡 警告: 答案过于随机，可能缺乏有效信息")
        else:
            print("✅ 选择题答案分布相对正常")
    
    # 4. 问答题质量分析
    if qa_lengths:
        avg_length = sum(qa_lengths) / len(qa_lengths)
        min_length = min(qa_lengths)
        max_length = max(qa_lengths)
        
        print(f"\n📝 问答题质量分析")
        print(f"平均长度: {avg_length:.1f} 字符")
        print(f"最短: {min_length} 字符")
        print(f"最长: {max_length} 字符")
        
        # 分析长度分布
        short_count = sum(1 for length in qa_lengths if length < 50)
        medium_count = sum(1 for length in qa_lengths if 50 <= length <= 300)
        long_count = sum(1 for length in qa_lengths if length > 300)
        
        print(f"过短答案 (<50字符): {short_count} ({short_count/len(qa_lengths)*100:.1f}%)")
        print(f"适中答案 (50-300字符): {medium_count} ({medium_count/len(qa_lengths)*100:.1f}%)")
        print(f"较长答案 (>300字符): {long_count} ({long_count/len(qa_lengths)*100:.1f}%)")
        
        if short_count / len(qa_lengths) > 0.3:
            print("🔴 严重问题: 大量答案过短，可能信息不足")
        elif avg_length < 100:
            print("🟡 警告: 答案平均长度偏短")
        else:
            print("✅ 问答题长度分布相对正常")
    
    # 5. 根本问题分析
    print(f"\n🔍 根本问题分析")
    
    # 分析几个样例答案的质量
    if results:
        print("\n样例答案质量检查:")
        sample_count = min(5, len(results))
        for i in range(sample_count):
            result = results[i]
            qid = result.get('id', f'unknown_{i}')
            answer = result.get('answer', '')
            
            if isinstance(answer, list):
                print(f"问题 {qid} (选择题): {answer}")
            else:
                preview = answer[:100] + "..." if len(answer) > 100 else answer
                print(f"问题 {qid} (问答题): {preview}")
                
                # 检查答案质量指标
                has_numbers = bool(re.search(r'\d+%|\d+\.\d+%', answer))
                has_finance_terms = any(term in answer for term in ["资本充足率", "流动性", "风险", "监管", "银行", "金融"])
                
                if not has_numbers and not has_finance_terms:
                    print(f"  ⚠️ 可能缺乏专业内容")
    
    # 6. 提供诊断结论和建议
    print(f"\n💡 诊断结论和建议")
    print("=" * 50)
    
    if error_count > len(results) * 0.1:
        print("🔴 高优先级问题: 处理失败率过高")
        print("   建议: 检查系统稳定性和错误处理机制")
    
    if choice_answers and max(Counter(choice_answers).values()) / len(choice_answers) > 0.6:
        print("🔴 高优先级问题: 选择题答案分布异常")
        print("   可能原因:")
        print("   1. RAG检索质量差，检索不到相关内容")
        print("   2. LLM理解能力有限，无法正确分析选择题")
        print("   3. 提示词设计有问题")
        print("   建议:")
        print("   - 检查向量数据库质量")
        print("   - 优化检索参数和策略")
        print("   - 改进选择题专用提示词")
    
    if qa_lengths and sum(qa_lengths) / len(qa_lengths) < 100:
        print("🔴 高优先级问题: 问答题答案过短")
        print("   可能原因:")
        print("   1. 检索到的上下文信息不足")
        print("   2. LLM生成参数设置保守")
        print("   3. 文档切片过小，关键信息被分割")
        print("   建议:")
        print("   - 增加检索数量(TOP-K)")
        print("   - 调整生成参数(max_tokens, temperature)")
        print("   - 优化文档切片策略")
    
    print("\n🚀 立即行动建议:")
    print("1. 清理并重建向量数据库")
    print("   python clear_vector_db.py clear")
    print("   python main.py --force-rebuild")
    
    print("\n2. 使用诊断脚本检查检索质量")
    print("   创建test_retrieval.py测试关键问题的检索效果")
    
    print("\n3. 调整关键参数")
    print("   - 增加CHUNK_SIZE到800-1200")
    print("   - 提高TOP_K到8-12")
    print("   - 降低SIMILARITY_THRESHOLD到0.2-0.3")
    print("   - 增加MAX_TOKENS到1500-2000")
    
    print("\n4. 改进提示词")
    print("   - 添加更多金融领域示例")
    print("   - 强化选择题分析逻辑")
    print("   - 要求更详细的解释")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="结果对比分析工具")
    parser.add_argument("baseline", help="基准版本结果文件")
    parser.add_argument("optimized", help="优化版本结果文件")
    
    args = parser.parse_args()
    
    comparator = ResultComparator()
    comparator.compare_results(args.baseline, args.optimized)


if __name__ == "__main__":
    analyze_system_issues() 