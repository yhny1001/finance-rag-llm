"""
测试比赛结果格式输出
验证result.json文件格式是否符合要求
"""

import json
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(".")

from main import FinancialQASystem

def test_choice_answer_extraction():
    """测试选择题答案提取功能 - 包含不定项选择题"""
    print("=" * 60)
    print("测试选择题答案提取功能 - 含不定项选择题")
    print("=" * 60)
    
    qa_system = FinancialQASystem()
    
    # 测试用例
    test_cases = [
        # 单选测试用例
        ("答案是A", ["A"]),
        ("正确答案为B", ["B"]),
        ("应该选择C", ["C"]),
        ("选D", ["D"]),
        ("根据分析，答案是B。", ["B"]),
        ("A选项是正确的", ["A"]),
        ("选择题答案：C", ["C"]),
        ("D. 这是正确答案", ["D"]),
        ("我认为答案应该是A，因为...", ["A"]),
        
        # 多选测试用例 - 标准格式
        ("答案是A,B", ["A", "B"]),
        ("正确答案为A、B、C", ["A", "B", "C"]),
        ("应该选择A，C", ["A", "C"]),
        
        # 多选测试用例 - 特殊格式
        ("选项A和D是正确的", ["A", "D"]),  # 添加连接词"和"的情况
        ("A,B,C都是正确选项", ["A", "B", "C"]),  # 添加"都是"的情况
        ("A、C、D正确", ["A", "C", "D"]),
        ("答案为：A,B", ["A", "B"]),
        
        # 额外边界情况测试
        ("选项B与C是正确答案", ["B", "C"]),  # 测试连接词"与"
        ("既有A也有B是对的", ["A", "B"]),  # 测试其他表述方式
        ("本题答案包括A以及C", ["A", "C"]),  # 测试连接词"以及"
        
        # 边界情况
        ("没有明确选项的答案", ["A"]),  # 默认情况
    ]
    
    success_count = 0
    for i, (answer_text, expected) in enumerate(test_cases, 1):
        result = qa_system.extract_choice_answer(answer_text)
        
        # 对于多选题，排序后再比较
        if len(expected) > 1:
            expected = sorted(expected)
            result = sorted(result)
            
        print(f"测试 {i}:")
        print(f"  输入: {answer_text}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        
        if result == expected:
            print("  ✅ 通过")
            success_count += 1
        else:
            print("  ❌ 失败")
        print()
    
    print(f"测试结果: {success_count}/{len(test_cases)} 通过")
    return success_count == len(test_cases)

def test_competition_format_generation():
    """测试比赛格式文件生成"""
    print("\n" + "=" * 60)
    print("测试比赛格式文件生成")
    print("=" * 60)
    
    qa_system = FinancialQASystem()
    
    # 模拟测试结果
    test_results = [
        {
            "id": 1,
            "category": "选择题",
            "question": "银行的核心资本包括哪些？",
            "answer": "根据题目分析，正确答案是A。核心资本主要包括普通股和留存收益。",
            "timestamp": "2024-01-01 10:00:00"
        },
        {
            "id": 2,
            "category": "问答题", 
            "question": "什么是资本充足率？",
            "answer": "资本充足率是衡量银行资本充足程度的重要指标，等于银行资本与风险加权资产的比率。",
            "timestamp": "2024-01-01 10:01:00"
        },
        {
            "id": 3,
            "category": "选择题",
            "question": "巴塞尔协议的主要目的是什么？",
            "answer": "选择B。巴塞尔协议主要目的是加强银行监管。",
            "timestamp": "2024-01-01 10:02:00"
        }
    ]
    
    try:
        # 生成比赛格式文件
        qa_system.save_competition_format(test_results)
        
        # 验证生成的文件
        result_file = "result.json"
        if Path(result_file).exists():
            print("\n📁 验证生成的文件:")
            
            with open(result_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"文件行数: {len(lines)}")
            
            for i, line in enumerate(lines):
                try:
                    data = json.loads(line.strip())
                    print(f"第{i+1}行: {data}")
                    
                    # 验证格式
                    if 'id' not in data or 'answer' not in data:
                        print(f"❌ 格式错误：缺少必需字段")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析错误: {e}")
                    return False
            
            print("✅ 格式验证通过")
            return True
        else:
            print("❌ 文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def validate_existing_result_file():
    """验证现有的result.json文件"""
    result_file = "result.json"
    
    if not Path(result_file).exists():
        print(f"❌ 文件不存在: {result_file}")
        return False
    
    print("\n" + "=" * 60)
    print(f"验证现有文件: {result_file}")
    print("=" * 60)
    
    try:
        choice_count = 0
        qa_count = 0
        total_lines = 0
        error_count = 0
        
        with open(result_file, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                total_lines += 1
                
                try:
                    data = json.loads(line)
                    
                    # 检查必需字段
                    if 'id' not in data or 'answer' not in data:
                        print(f"❌ 第{line_no}行缺少必需字段")
                        error_count += 1
                        continue
                    
                    # 统计答案类型
                    answer = data['answer']
                    if isinstance(answer, list):
                        choice_count += 1
                        if line_no <= 3:  # 显示前3个选择题示例
                            print(f"选择题示例: {data}")
                    else:
                        qa_count += 1
                        if qa_count <= 3:  # 显示前3个问答题示例
                            print(f"问答题示例: {data}")
                
                except json.JSONDecodeError as e:
                    print(f"❌ 第{line_no}行JSON格式错误: {e}")
                    error_count += 1
        
        print(f"\n📊 文件统计:")
        print(f"总行数: {total_lines}")
        print(f"选择题: {choice_count}")
        print(f"问答题: {qa_count}")
        print(f"错误行数: {error_count}")
        print(f"格式正确率: {((total_lines - error_count) / total_lines * 100):.2f}%" if total_lines > 0 else "0%")
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

if __name__ == "__main__":
    print("🧪 比赛结果格式测试")
    
    # 测试选择题答案提取
    extraction_ok = test_choice_answer_extraction()
    
    # 测试格式生成
    generation_ok = test_competition_format_generation()
    
    # 验证现有文件（如果存在）
    validation_ok = validate_existing_result_file()
    
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print(f"选择题答案提取: {'✅ 通过' if extraction_ok else '❌ 失败'}")
    print(f"格式文件生成: {'✅ 通过' if generation_ok else '❌ 失败'}")
    print(f"现有文件验证: {'✅ 通过' if validation_ok else '⚠️ 无文件或有错误'}")
    
    if extraction_ok and generation_ok:
        print("\n🎉 所有核心测试通过！现在系统可以正确生成比赛格式的result.json文件了。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。") 