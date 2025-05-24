"""
合并批次结果工具
用于将多个批次的结果文件合并成最终的result.json文件
"""

import json
import sys
from pathlib import Path
import re
from typing import List, Dict, Any

def find_batch_files(output_dir: str = "outputs") -> List[Path]:
    """查找所有批次结果文件"""
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"❌ 输出目录不存在: {output_dir}")
        return []
    
    # 查找batch_results_*.json文件
    batch_files = list(output_path.glob("batch_results_*.json"))
    
    # 按批次开始索引排序
    def extract_start_idx(filename):
        match = re.search(r'batch_results_(\d+)_', filename.name)
        return int(match.group(1)) if match else 0
    
    batch_files.sort(key=extract_start_idx)
    return batch_files

def load_batch_results(batch_files: List[Path]) -> List[Dict[str, Any]]:
    """加载所有批次的结果"""
    all_results = []
    
    for batch_file in batch_files:
        print(f"加载批次文件: {batch_file.name}")
        
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                
            if isinstance(batch_data, list):
                all_results.extend(batch_data)
                print(f"  ✅ 加载了 {len(batch_data)} 条结果")
            else:
                print(f"  ⚠️ 文件格式不正确，跳过")
                
        except Exception as e:
            print(f"  ❌ 加载失败: {e}")
    
    return all_results

def extract_choice_answer(answer_text: str) -> List[str]:
    """从回答中提取选择题答案"""
    import re
    
    # 常见的选择题答案模式
    patterns = [
        r'答案[是为]?\s*([A-D])',
        r'选择\s*([A-D])',
        r'选项\s*([A-D])',
        r'正确答案[是为]?\s*([A-D])',
        r'应该选择?\s*([A-D])',
        r'答案应该[是为]?\s*([A-D])',
        r'[选答]([A-D])',
        r'\b([A-D])\b.*?正确',
        r'^\s*([A-D])\s*[.、，]',  # 以选项开头
    ]
    
    answer_text = answer_text.upper()  # 转为大写便于匹配
    
    for pattern in patterns:
        matches = re.findall(pattern, answer_text)
        if matches:
            # 返回第一个匹配的选项，格式为列表
            return [matches[0]]
    
    # 如果没有匹配到明确的选项，尝试查找单独的A、B、C、D
    single_choices = re.findall(r'\b([A-D])\b', answer_text)
    if single_choices:
        return [single_choices[0]]
    
    # 如果都没有找到，返回默认答案
    print(f"⚠️ 无法从答案中提取选项: {answer_text[:100]}...")
    return ["A"]  # 默认选择A

def generate_competition_format(results: List[Dict[str, Any]], output_file: str = "result.json"):
    """生成比赛格式的result.json文件"""
    print(f"\n🎯 生成比赛提交格式文件: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                # 提取基本信息
                question_id = result.get('id')
                category = result.get('category', '问答题')
                answer = result.get('answer', '')
                
                # 处理答案格式
                if category == '选择题':
                    # 从答案中提取选项（A、B、C、D等）
                    processed_answer = extract_choice_answer(answer)
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
        
        print(f"✅ 比赛提交文件已生成: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 生成比赛格式文件失败: {e}")
        return False

def validate_result_file(result_file: str):
    """验证结果文件格式"""
    print(f"\n🔍 验证结果文件格式: {result_file}")
    
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
                    else:
                        qa_count += 1
                
                except json.JSONDecodeError as e:
                    print(f"❌ 第{line_no}行JSON格式错误: {e}")
                    error_count += 1
        
        print(f"✅ 文件格式验证通过")
        print(f"   总行数: {total_lines}")
        print(f"   选择题: {choice_count}")
        print(f"   问答题: {qa_count}")
        print(f"   错误行数: {error_count}")
        print(f"   格式正确率: {((total_lines - error_count) / total_lines * 100):.2f}%" if total_lines > 0 else "0%")
        
        # 显示前几行示例
        print("\n📝 文件内容示例:")
        with open(result_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 3:  # 只显示前3行
                    break
                print(f"   {line.strip()}")
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 批次结果合并工具")
    print("=" * 60)
    
    # 查找批次文件
    batch_files = find_batch_files()
    
    if not batch_files:
        print("❌ 未找到任何批次结果文件")
        print("请确保在outputs目录中有batch_results_*.json文件")
        return
    
    print(f"找到 {len(batch_files)} 个批次文件:")
    for batch_file in batch_files:
        print(f"  - {batch_file.name}")
    
    # 加载所有结果
    all_results = load_batch_results(batch_files)
    
    if not all_results:
        print("❌ 没有加载到任何结果")
        return
    
    print(f"\n📊 合并统计:")
    print(f"总结果数: {len(all_results)}")
    
    choice_count = sum(1 for r in all_results if r.get('category') == '选择题')
    qa_count = sum(1 for r in all_results if r.get('category') == '问答题')
    print(f"选择题: {choice_count}")
    print(f"问答题: {qa_count}")
    
    # 按ID排序
    all_results.sort(key=lambda x: x.get('id', 0))
    
    # 保存完整结果
    complete_file = "complete_results.json"
    with open(complete_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {complete_file}")
    
    # 生成比赛格式文件
    success = generate_competition_format(all_results)
    
    if success:
        # 验证生成的文件
        validate_result_file("result.json")
        print(f"\n🎉 合并完成！result.json文件已生成，可直接用于比赛提交！")
    else:
        print(f"\n❌ 合并失败")

if __name__ == "__main__":
    main() 