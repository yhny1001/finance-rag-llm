"""
选择题答案提取功能的专门测试脚本
主要针对不定项选择题的答案提取
"""

import sys
import json
from pathlib import Path
from typing import List

# 添加当前目录到路径
sys.path.append(".")

# 导入答案提取函数
from main import FinancialQASystem

def test_extract_choice():
    """测试选择题答案提取"""
    
    qa_system = FinancialQASystem()
    
    test_cases = [
        # 单选测试用例
        ("答案是A", ["A"], "基本单选"),
        ("正确答案为B", ["B"], "基本单选"),
        ("应该选择C", ["C"], "基本单选"),
        
        # 多选测试用例 - 标准格式
        ("答案是A,B", ["A", "B"], "标准多选"),
        ("正确答案为A、B、C", ["A", "B", "C"], "标准多选"),
        ("应该选择A，C", ["A", "C"], "标准多选"),
        
        # 多选测试用例 - 特殊格式
        ("选项A和D是正确的", ["A", "D"], "连接词和"),
        ("A,B,C都是正确选项", ["A", "B", "C"], "都是模式"),
        ("A、C、D正确", ["A", "C", "D"], "标准多选"),
        ("答案为：A,B", ["A", "B"], "冒号多选"),
        
        # 额外边界情况测试
        ("选项B与C是正确答案", ["B", "C"], "连接词与"),
        ("既有A也有B是对的", ["A", "B"], "也有模式"),
        ("本题答案包括A以及C", ["A", "C"], "包括以及"),
    ]
    
    total = len(test_cases)
    passed = 0
    
    print(f"开始测试 {total} 个选择题答案提取用例")
    print("="*50)
    
    for i, (input_text, expected, test_type) in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{total} [{test_type}]:")
        print(f"  输入: {input_text}")
        print(f"  期望: {expected}")
        
        result = qa_system.extract_choice_answer(input_text)
        
        # 对于多选题，排序后再比较
        if len(expected) > 1:
            expected = sorted(expected)
            result = sorted(result)
            
        print(f"  结果: {result}")
        
        if result == expected:
            status = "✅ 通过"
            passed += 1
        else:
            status = "❌ 失败"
            
        print(f"  {status}")
    
    print("\n" + "="*50)
    print(f"测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total

def test_raw_llm_output_saving():
    """测试大模型原始输出保存功能"""
    
    print("\n" + "="*50)
    print("测试大模型原始输出保存功能")
    print("="*50)
    
    # 创建测试数据
    test_results = [
        {
            "id": 999,
            "category": "选择题",
            "question": "商业银行普通员工的基本薪酬通常占总薪酬的最高比例是多少？",
            "content": "   A. 25%  \n   B. 35%  \n   C. 45%  \n   D. 55%  ",
            "answer": "B",
            "raw_llm_output": "根据参考资料，商业银行的基本薪酬一般不高于其薪酬总额的35%。\n\n选项A: 25% - 过低，参考资料指出基本薪酬一般不高于35%，暗示其通常接近35%。\n选项B: 35% - 正确，与参考资料中提到的最高比例一致。\n选项C: 45% - 过高，超过了参考资料规定的最高比例35%。\n选项D: 55% - 过高，远超参考资料规定的最高比例35%。\n\n答案：B"
        },
        {
            "id": 998,
            "category": "问答题", 
            "question": "如果开户单位与中国人民银行账务余额核对不一致，应当采取什么标准化处理流程？",
            "content": None,
            "answer": "当开户单位与中国人民银行账务余额核对不一致时，应遵循以下标准化处理流程：首先，开户单位应逐笔勾对发生额，及时查清原因，由主管确认对账结果，并予以说明。中国人民银行事后监督部门应于开户单位完成账务核对的当日确认对账结果。若对账务核对结果有疑问，营业部门应及时与开户单位联系，查清原因，并予以说明；事后监督部门应追踪监督。",
            "raw_llm_output": "当开户单位与中国人民银行账务余额核对不一致时，应遵循以下标准化处理流程：首先，开户单位应逐笔勾对发生额，及时查清原因，由主管确认对账结果，并予以说明。中国人民银行事后监督部门应于开户单位完成账务核对的当日确认对账结果。若对账务核对结果有疑问，营业部门应及时与开户单位联系，查清原因，并予以说明；事后监督部门应追踪监督。"
        }
    ]
    
    # 创建系统实例
    from main import FinancialQASystem
    qa_system = FinancialQASystem()
    
    # 测试保存功能
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    test_output_file = f"test_raw_llm_outputs_{timestamp}.json"
    
    # 调用保存函数
    qa_system.save_raw_llm_outputs(test_results, test_output_file)
    
    # 验证文件是否生成
    output_path = Path(test_output_file)
    if not output_path.exists():
        print("❌ 测试失败: 输出文件未生成")
        return False
    
    print("\n✅ 测试通过: 原始输出文件已生成")
    print(f"  文件保存位置: {test_output_file}")
    
    return True

if __name__ == "__main__":
    print("🧪 选择题答案提取测试")
    
    # 测试答案提取功能
    extract_test_result = test_extract_choice()
    
    # 测试原始输出保存功能
    raw_output_test_result = test_raw_llm_output_saving()
    
    # 总结测试结果
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    print(f"答案提取功能: {'✅ 通过' if extract_test_result else '❌ 失败'}")
    print(f"原始输出保存: {'✅ 通过' if raw_output_test_result else '❌ 失败'}")
    
    if extract_test_result and raw_output_test_result:
        print("\n🎉 所有测试通过！系统功能正常。")
    else:
        print("\n⚠️ 部分测试未通过，请检查问题。") 