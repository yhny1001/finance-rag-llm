import sys
import os
import unittest

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from main import FinancialQASystem

class TestExtractChoiceAnswer(unittest.TestCase):
    def setUp(self):
        self.qa_system = FinancialQASystem()
    
    def test_extract_single_choice(self):
        """测试单选题答案提取"""
        # 测试案例1: 明确给出答案是B
        answer_text = """选项A: [分析选项A是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这表明境外投资者不需要经过中国人民银行单独批准即可通过托管银行办理开户手续，因此选项A不正确。

选项B: [分析选项B是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这明确指出不需要中国人民银行单独批准，可以直接通过托管银行办理，因此选项B是正确的。

选项C: [分析选项C是否正确的依据]
参考资料中没有提到QFII资质持有者这一特定条件，因此选项C不正确。

选项D: [分析选项D是否正确的依据]
参考资料中也没有提及需要获得财政部备案的要求，因此选项D不正确。

综上所述，正确答案是：B"""
        
        result = self.qa_system.extract_choice_answer(answer_text)
        self.assertEqual(result, ["B"], "明确给出'正确答案是：B'时应提取为B")

    def test_extract_multiple_choice(self):
        """测试多选题答案提取"""
        # 测试案例2: 明确给出答案是A和C
        answer_text = """选项A: [分析选项A是否正确的依据]
根据参考资料，选项A是正确的。

选项B: [分析选项B是否正确的依据]
根据参考资料，选项B不正确。

选项C: [分析选项C是否正确的依据]
根据参考资料，选项C是正确的。

选项D: [分析选项D是否正确的依据]
根据参考资料，选项D不正确。

综上所述，正确答案是：A和C"""
        
        result = self.qa_system.extract_choice_answer(answer_text)
        self.assertEqual(sorted(result), ["A", "C"], "明确给出'正确答案是：A和C'时应提取为A和C")

    def test_pattern_selection(self):
        """测试当文本提到所有选项但只有一个正确时的情况"""
        answer_text = """这个问题涉及到境外投资者在银行间债券市场开立债券账户的规定。我们需要分析各个选项：

A. 必须提交书面申请并经审核：这个选项是错误的。
B. 无需批准，可直接通过托管银行办理：根据相关规定，这个选项是正确的。
C. 仅限QFII资质持有者：这个选项没有依据。
D. 需获得财政部备案：没有相关要求。

根据参考资料，境外投资者无需中国人民银行单独批准即可开立债券账户，因此B是正确选项。"""
        
        result = self.qa_system.extract_choice_answer(answer_text)
        self.assertEqual(result, ["B"], "应该能从模糊分析中提取出正确选项B")

    def test_problematic_case(self):
        """测试用户提供的问题案例"""
        answer_text = """选项A: [分析选项A是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这表明境外投资者不需要经过中国人民银行单独批准即可通过托管银行办理开户手续，因此选项A不正确。

选项B: [分析选项B是否正确的依据]
根据参考资料中的第四条，"已在银行间债券市场登记托管结算机构开立债券账户的投资者，在柜台业务开办机构开立债券账户，不需要经中国人民银行同意。" 这明确指出不需要中国人民银行单独批准，可以直接通过托管银行办理，因此选项B是正确的。

选项C: [分析选项C是否正确的依据]
参考资料中没有提到QFII资质持有者这一特定条件，因此选项C不正确。

选项D: [分析选项D是否正确的依据]
参考资料中也没有提及需要获得财政部备案的要求，因此选项D不正确。

综上所述，正确答案是：B"""
        
        result = self.qa_system.extract_choice_answer(answer_text)
        self.assertEqual(result, ["B"], "应正确提取出单选答案B，而不是全部选项")

if __name__ == '__main__':
    unittest.main() 