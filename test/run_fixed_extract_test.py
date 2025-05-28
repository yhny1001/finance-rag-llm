"""
运行测试，验证修复后的选择题答案提取功能
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# 导入测试类和修复函数
from test_extract_fix import TestExtractChoiceAnswer
from fix.extract_choice_wrapper import apply_fix, restore_original

def run_test_before_fix():
    """运行修复前的测试"""
    print("\n" + "=" * 50)
    print("运行修复前的测试")
    print("=" * 50)
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestExtractChoiceAnswer)
    test_result = unittest.TextTestRunner().run(test_suite)
    
    return test_result.wasSuccessful()

def run_test_after_fix():
    """应用修复并运行测试"""
    print("\n" + "=" * 50)
    print("应用修复并运行测试")
    print("=" * 50)
    
    # 应用修复
    original_function = apply_fix()
    
    try:
        # 运行测试
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestExtractChoiceAnswer)
        test_result = unittest.TextTestRunner().run(test_suite)
        success = test_result.wasSuccessful()
    finally:
        # 恢复原始函数
        restore_original(original_function)
    
    return success

def test_problematic_case():
    """直接测试用户提供的问题案例"""
    from main import FinancialQASystem
    from fix.fix_extract_choice_answer import extract_choice_answer_fixed
    
    qa_system = FinancialQASystem()
    
    # 用户提供的问题案例
    answer_text = """选项A: [分析选项A是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这表明境外投资者不需要经过中国人民银行单独批准即可通过托管银行办理开户手续，因此选项A不正确。

选项B: [分析选项B是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这明确指出不需要中国人民银行单独批准，可以直接通过托管银行办理，因此选项B是正确的。

选项C: [分析选项C是否正确的依据]
参考资料中没有提到QFII资质持有者这一特定条件，因此选项C不正确。

选项D: [分析选项D是否正确的依据]
参考资料中也没有提及需要获得财政部备案的要求，因此选项D不正确。

综上所述，正确答案是：B"""
    
    print("\n" + "=" * 50)
    print("直接测试用户提供的问题案例")
    print("=" * 50)
    
    # 使用原始函数
    print("原始函数结果:")
    original_result = qa_system.extract_choice_answer(answer_text)
    print(f"提取的答案: {original_result}")
    
    # 使用修复后的函数
    print("\n修复后函数结果:")
    fixed_result = extract_choice_answer_fixed(answer_text)
    print(f"提取的答案: {fixed_result}")
    
    # 验证结果
    is_correct = fixed_result == ["B"]
    print(f"\n修复结果验证: {'✓ 正确' if is_correct else '✗ 错误'}")
    
    return is_correct

if __name__ == "__main__":
    # 运行修复前的测试
    original_success = run_test_before_fix()
    
    # 应用修复并运行测试
    fixed_success = run_test_after_fix()
    
    # 测试问题案例
    case_success = test_problematic_case()
    
    # 打印总结
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    print(f"修复前测试: {'通过' if original_success else '失败'}")
    print(f"修复后测试: {'通过' if fixed_success else '失败'}")
    print(f"问题案例测试: {'通过' if case_success else '失败'}")
    
    if fixed_success and case_success:
        print("\n✅ 修复成功！可以应用到生产环境。")
        print("   运行以下命令应用修复:")
        print("   python -m fix.extract_choice_wrapper")
    else:
        print("\n❌ 修复不完全，需要进一步改进。") 