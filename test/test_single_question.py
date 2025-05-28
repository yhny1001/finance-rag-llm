"""
测试单个选择题的处理
"""

from main import FinancialQASystem

def test_single_choice_question():
    """测试单个选择题的处理"""
    print("=" * 50)
    print("测试单个选择题的处理")
    print("=" * 50)
    
    # 创建系统实例
    qa_system = FinancialQASystem()
    
    # 初始化系统 - 跳过知识库构建
    qa_system.initialize()
    
    # 测试用例 - 使用batch_results_40_49文件中的问题ID 542
    test_case = {
        "id": 542,
        "category": "选择题",
        "question": "普惠金融事业部筹备工作领导小组的组长通常由谁担任？",
        "content": "   A. 分行行长  \n   B. 董事会主席  \n   C. 总行高级管理人员  \n   D. 审计部门负责人  "
    }
    
    # 处理问题
    result = qa_system.process_question(test_case)
    
    # 打印结果
    print("\n📋 处理结果:")
    print(f"问题ID: {test_case['id']}")
    print(f"问题类型: {test_case['category']}")
    print(f"问题: {test_case['question']}")
    print(f"最终答案: {result.get('answer', '')}")
    print(f"原始输出长度: {len(result.get('raw_llm_output', ''))}")
    print("\n原始输出预览:")
    raw_output = result.get("raw_llm_output", "")
    print(raw_output[:500] + "..." if len(raw_output) > 500 else raw_output)
    
    return True

if __name__ == "__main__":
    test_single_choice_question() 