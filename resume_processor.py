"""
断点续传功能模块
用于保存和恢复批处理进度，防止程序中断后需要重新开始
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class ResumeProcessor:
    """断点续传处理类"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """初始化断点续传处理器"""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "processing_status.json"
        self.checkpoint_results = self.checkpoint_dir / "checkpoint_results.json"
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        
        print(f"📋 断点续传功能已初始化，会话ID: {self.session_id}")
    
    def save_checkpoint(self, current_idx: int, total: int, 
                        batch_size: int, all_results: List[Dict[str, Any]]) -> bool:
        """保存当前处理进度"""
        try:
            # 保存进度信息
            checkpoint_data = {
                "session_id": self.session_id,
                "current_idx": current_idx,
                "total": total,
                "batch_size": batch_size,
                "timestamp": time.time(),
                "time_str": time.strftime("%Y-%m-%d %H:%M:%S"),
                "completed_percentage": round((current_idx / total) * 100, 2) if total > 0 else 0
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            # 保存已处理的结果
            with open(self.checkpoint_results, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False)
            
            print(f"✅ 断点续传检查点已保存: 已处理 {current_idx}/{total} 个问题 ({checkpoint_data['completed_percentage']}%)")
            return True
            
        except Exception as e:
            print(f"❌ 保存断点续传检查点失败: {e}")
            return False
    
    def load_checkpoint(self) -> Tuple[Optional[int], Optional[int], Optional[List[Dict[str, Any]]]]:
        """加载上次处理进度"""
        if not self.checkpoint_file.exists() or not self.checkpoint_results.exists():
            print("📝 未找到断点续传检查点，将从头开始处理")
            return None, None, None
        
        try:
            # 加载进度信息
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # 加载已处理结果
            with open(self.checkpoint_results, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            current_idx = checkpoint_data.get("current_idx", 0)
            batch_size = checkpoint_data.get("batch_size", 10)
            timestamp = checkpoint_data.get("time_str", "未知时间")
            
            print(f"🔄 找到断点续传检查点: {timestamp}")
            print(f"📊 上次进度: {current_idx} 个问题，批次大小: {batch_size}")
            
            return current_idx, batch_size, results
            
        except Exception as e:
            print(f"❌ 加载断点续传检查点失败: {e}")
            return None, None, None
    
    def clear_checkpoint(self) -> bool:
        """清除检查点文件"""
        try:
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
            
            if self.checkpoint_results.exists():
                self.checkpoint_results.unlink()
                
            print("🧹 断点续传检查点已清除")
            return True
            
        except Exception as e:
            print(f"❌ 清除断点续传检查点失败: {e}")
            return False
    
    def has_checkpoint(self) -> bool:
        """检查是否存在检查点"""
        return self.checkpoint_file.exists() and self.checkpoint_results.exists()


# 测试代码
if __name__ == "__main__":
    # 测试断点续传功能
    resume = ResumeProcessor()
    
    # 检查是否有上次的检查点
    if resume.has_checkpoint():
        print("发现上次的检查点，可以继续处理")
        last_idx, batch_size, results = resume.load_checkpoint()
        print(f"上次处理到索引: {last_idx}, 已有结果数: {len(results) if results else 0}")
    else:
        print("没有检查点，将从头开始")
    
    # 模拟保存检查点
    dummy_results = [{"id": i, "answer": f"测试答案 {i}"} for i in range(5)]
    resume.save_checkpoint(5, 100, 10, dummy_results)
    
    # 清除检查点(可选)
    # resume.clear_checkpoint() 