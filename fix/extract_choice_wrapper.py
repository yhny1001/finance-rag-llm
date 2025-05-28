"""
包装原始的extract_choice_answer函数，使用修复后的实现
"""

import sys
import os
from typing import List

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# 导入原始函数和修复后的函数
from main import FinancialQASystem
from fix.fix_extract_choice_answer import extract_choice_answer_fixed

def apply_fix():
    """应用修复：用修复后的函数替换原函数"""
    print("应用选择题答案提取函数修复...")
    
    # 保存原始函数的引用
    original_function = FinancialQASystem.extract_choice_answer
    
    # 创建一个包装器，使用修复后的实现
    def extract_choice_answer_wrapper(self, answer_text: str) -> List[str]:
        return extract_choice_answer_fixed(answer_text)
    
    # 替换函数
    FinancialQASystem.extract_choice_answer = extract_choice_answer_wrapper
    
    print("修复已应用，所有选择题答案提取将使用修复后的逻辑")
    
    return original_function  # 返回原始函数，以便于需要时恢复

def restore_original(original_function):
    """恢复原始函数"""
    FinancialQASystem.extract_choice_answer = original_function
    print("已恢复原始选择题答案提取函数")

if __name__ == "__main__":
    # 直接运行此脚本时，应用修复
    original = apply_fix()
    print("已将答案提取逻辑更新为修复版本")
    print("如需恢复原始版本，请在代码中调用 restore_original(original)") 